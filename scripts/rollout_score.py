#!/usr/bin/env python3
"""Harness-edit v2 - rollout BEHAVIOR scorer (the SkillOpt gate that catches behavior, not law text).

v1 (scripts/score_skill.py) lints the SKILL TEXT for rule coverage: necessary, not sufficient. A rule
can be present in the law and the agent still violates it (observed: an agent passed 8/8 law-coverage
yet committed several of these same mistakes in one session). v2 scores the AGENT'S RESPONSE to a
realistic prompt -- with the skill vs without -- and gates on whether the skill actually changes
behavior on the held-out scenarios.

Harness-agnostic via a pluggable adapter (SkillOpt's adapter interface, arXiv 2605.23904):
  transcript : read a pre-recorded response (offline; no API key)  -> CI / self-test
  echo       : returns the prompt (plumbing only)
  claude     : Anthropic API, needs ANTHROPIC_API_KEY              -> the Claude Code / acer harness
  codex      : OpenAI API, needs OPENAI_API_KEY                    -> the Codex / liris harness
Live adapters error clearly if the key is absent; no key is read into the report or stored.

Usage:
  python scripts/rollout_score.py --scenarios examples/asolaria-scenarios.json \
    --harness transcript --transcript examples/transcripts/good.json \
    --skill examples/asolaria-claims-gate-sample.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def norm(t: str) -> str:
    return " ".join((t or "").lower().split())


# ---- adapters: (skill_text, prompt, scenario_id) -> response text (the rollout trajectory) ----
def run_adapter(harness: str, skill: str, prompt: str, sid: str, store: dict) -> str:
    if harness == "echo":
        return prompt
    if harness == "transcript":
        if sid not in store:
            raise KeyError(f"no transcript for scenario id '{sid}'")
        return store[sid]
    if harness == "claude":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("claude adapter needs ANTHROPIC_API_KEY; use --harness transcript for offline CI")
        import anthropic  # noqa: PLC0415
        client = anthropic.Anthropic(api_key=key)
        model = os.environ.get("HARNESS_CLAUDE_MODEL", "claude-opus-4-8")
        msg = client.messages.create(
            model=model, max_tokens=1024,
            system=(skill.strip() or "You are a careful agent."),
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    if harness == "codex":
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("codex adapter needs OPENAI_API_KEY; use --harness transcript for offline CI")
        from openai import OpenAI  # noqa: PLC0415
        client = OpenAI(api_key=key)
        model = os.environ.get("HARNESS_CODEX_MODEL", "gpt-5.5")
        r = client.chat.completions.create(model=model, messages=[
            {"role": "system", "content": (skill.strip() or "You are a careful agent.")},
            {"role": "user", "content": prompt},
        ])
        return r.choices[0].message.content or ""
    raise ValueError(f"unknown harness '{harness}'")


# ---- rubric: judge the RESPONSE (behavior), not the law text ----
def judge(resp: str, rubric: dict) -> dict:
    r = norm(resp)
    applied = any(norm(m) in r for m in rubric.get("apply_any", []))
    failed = [m for m in rubric.get("fail_any", []) if norm(m) in r]
    return {"pass": bool(applied and not failed), "applied": applied, "failed": failed}


def run(scenarios, skill, harness, store, baseline):
    rows = []
    for s in scenarios:
        sid, prompt, rub = s["id"], s["prompt"], s["rubric"]
        row = {"id": sid, "with_skill": judge(run_adapter(harness, skill, prompt, sid, store), rub)}
        if baseline:
            bid = sid + "::baseline" if harness == "transcript" else sid
            row["no_skill"] = judge(run_adapter(harness, "", prompt, bid, store), rub)
        rows.append(row)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--skill", default="", help="path to skill/law markdown (empty = no skill)")
    ap.add_argument("--harness", default="transcript", choices=["transcript", "echo", "claude", "codex"])
    ap.add_argument("--transcript", help="transcript JSON map for --harness transcript")
    ap.add_argument("--baseline", action="store_true", help="also run no-skill and report the skill delta")
    ap.add_argument("--report")
    a = ap.parse_args()
    try:
        scenarios = json.loads(Path(a.scenarios).read_text(encoding="utf-8"))
        skill = Path(a.skill).read_text(encoding="utf-8") if a.skill else ""
        store = (json.loads(Path(a.transcript).read_text(encoding="utf-8"))
                 if (a.harness == "transcript" and a.transcript) else {})
        rows = run(scenarios, skill, a.harness, store, a.baseline)
    except Exception as exc:  # noqa: BLE001
        print(f"ROLLOUT|ok=0|error={type(exc).__name__}|detail={exc}", file=sys.stderr)
        return 2
    passed = sum(1 for r in rows if r["with_skill"]["pass"])
    total = len(rows)
    rep = {"ok": passed == total, "passed": passed, "total": total,
           "score": passed / total if total else 0.0, "harness": a.harness, "results": rows}
    if a.baseline:
        base = sum(1 for r in rows if r.get("no_skill", {}).get("pass"))
        rep["baseline_passed"] = base
        rep["skill_delta"] = passed - base
    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    line = f"ROLLOUT|ok={1 if rep['ok'] else 0}|passed={passed}|total={total}|score={rep['score']:.3f}|harness={a.harness}"
    if a.baseline:
        line += f"|baseline={rep['baseline_passed']}|skill_delta={rep['skill_delta']}"
    print(line)
    for r in rows:
        extra = f"|no_skill={1 if r['no_skill']['pass'] else 0}" if "no_skill" in r else ""
        bad = f"|hit_fail={','.join(r['with_skill']['failed'])}" if r["with_skill"]["failed"] else ""
        print(f"ROLLOUTCASE|id={r['id']}|with_skill={1 if r['with_skill']['pass'] else 0}{extra}{bad}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
