#!/usr/bin/env python3
"""Gated edit applier — the SkillOpt validation gate ENFORCED BY THE PROGRAM, not by hand.

This is the piece that was missing from the harness: a way to *edit* a skill/law document where
the edit is accepted ONLY if it survives the held-out gate. You propose a bounded edit
(append / replace / delete); the program scores the held-out lint coverage BEFORE and AFTER and:

  - VALIDATION_ACCEPTED : coverage did not drop AND no previously-passing scenario regressed.
                          With --apply, the edit is written to the target.
  - REJECTED_BUFFER     : the edit regressed a scenario (or dropped coverage). The target is left
                          UNCHANGED and the rejected edit + reason is appended to the rejected buffer
                          (negative feedback, SkillOpt-style). Never hand-wave a regressing edit in.

Default is dry-run; pass --apply to actually write an accepted edit. That is the discipline: a
skill/law edit goes through THIS, not a manual editor.

Usage:
  python scripts/apply_edit.py --target SKILL.md --scenarios examples/asolaria-scenarios.json \
      --op append  --text "new rule line"            [--apply]
  python scripts/apply_edit.py --target SKILL.md --scenarios ... --op replace --find OLD --text NEW
  python scripts/apply_edit.py --target SKILL.md --scenarios ... --op delete  --find PHRASE
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from score_skill import score  # reuse the v1 held-out lint scorer


def load_scenarios(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["scenarios"] if isinstance(data, dict) and "scenarios" in data else data


def apply_op(text, op, find, repl):
    if op == "append":
        sep = "" if text.endswith("\n") else "\n"
        return text + sep + repl + "\n"
    if op == "replace":
        if find not in text:
            raise ValueError(f"replace: find text not present: {find[:50]!r}")
        return text.replace(find, repl)
    if op == "delete":
        if find not in text:
            raise ValueError(f"delete: find text not present: {find[:50]!r}")
        return text.replace(find, "")
    raise ValueError(f"unknown op: {op}")


def coverage(text, scenarios):
    r = score(text, scenarios)
    return r["passed"], r["total"], {x["id"]: x["ok"] for x in r["results"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="skill/law file to edit")
    ap.add_argument("--scenarios", required=True, help="canonical held-out set")
    ap.add_argument("--op", required=True, choices=["append", "replace", "delete"])
    ap.add_argument("--text", default="")
    ap.add_argument("--find", default="")
    ap.add_argument("--buffer", default="rejected-edits.log", help="rejected-edit buffer (negative feedback)")
    ap.add_argument("--require-improve", default="",
                    help="scenario id that MUST flip FAIL->PASS (strict-improve gate; matches SkillOpt). "
                         "Without it the gate only requires non-regression.")
    ap.add_argument("--apply", action="store_true", help="write the edit IF accepted (default: dry-run)")
    a = ap.parse_args()

    scenarios = load_scenarios(a.scenarios)
    before = Path(a.target).read_text(encoding="utf-8")
    bp, bt, bmap = coverage(before, scenarios)
    try:
        after = apply_op(before, a.op, a.find, a.text)
    except Exception as exc:  # noqa: BLE001
        print(f"EDIT|verdict=ERROR|detail={exc}", file=sys.stderr)
        return 2
    ap_pass, at, amap = coverage(after, scenarios)
    regressed = sorted(i for i in bmap if bmap[i] and not amap.get(i))
    ri = a.require_improve
    target_flipped = (ri in bmap and not bmap[ri] and bool(amap.get(ri))) if ri else None
    improved_ok = (target_flipped is True) if ri else True
    accept = at > 0 and (ap_pass >= bp) and not regressed and improved_ok  # reject empty/vacuous held-out set (total=0)
    verdict = "VALIDATION_ACCEPTED" if accept else "REJECTED_BUFFER"
    applied = bool(accept and a.apply)

    if applied:
        Path(a.target).write_text(after, encoding="utf-8")
    if not accept:
        rec = {"op": a.op, "find": a.find[:120], "text": a.text[:120],
               "before": f"{bp}/{bt}", "after": f"{ap_pass}/{at}", "regressed": regressed,
               "require_improve": ri, "target_flipped": target_flipped}
        with open(a.buffer, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    flip = "n/a" if ri == "" else ("yes" if target_flipped else "no")
    print(f"EDIT|verdict={verdict}|before={bp}/{bt}|after={ap_pass}/{at}|delta={ap_pass - bp}"
          f"|regressed={','.join(regressed) or 'none'}|require_improve={ri or 'none'}|target_flipped={flip}|applied={applied}")
    return 0 if accept else 1


if __name__ == "__main__":
    raise SystemExit(main())
