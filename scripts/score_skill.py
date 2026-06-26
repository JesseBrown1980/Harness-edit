#!/usr/bin/env python3
"""Deterministic v1 SkillOpt-style held-out scorer for skill/law text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def phrase_present(text: str, phrase: str) -> bool:
    return norm(phrase) in text


def score(skill_text: str, scenarios: list[dict]) -> dict:
    text = norm(skill_text)
    results = []
    passed = 0
    for scenario in scenarios:
        missing_groups = []
        for group in scenario.get("must_include_any", []):
            if not any(phrase_present(text, phrase) for phrase in group):
                missing_groups.append(group)
        forbidden_hits = [
            phrase
            for phrase in scenario.get("must_not_include", [])
            if phrase_present(text, phrase)
        ]
        ok = not missing_groups and not forbidden_hits
        passed += 1 if ok else 0
        results.append(
            {
                "id": scenario.get("id"),
                "ok": ok,
                "missing_groups": missing_groups,
                "forbidden_hits": forbidden_hits,
                "failure": scenario.get("failure", ""),
            }
        )
    return {
        "ok": passed == len(scenarios),
        "passed": passed,
        "total": len(scenarios),
        "score": passed / len(scenarios) if scenarios else 0.0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Path to skill/law markdown")
    parser.add_argument("--scenarios", required=True, help="Path to scenario JSON")
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args()

    try:
        skill_text = Path(args.skill).read_text(encoding="utf-8")
        scenarios = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
        if not isinstance(scenarios, list):
            raise ValueError("scenario file must contain a JSON list")
        report = score(skill_text, scenarios)
    except Exception as exc:
        print(f"HARNESSEDIT|ok=0|error={type(exc).__name__}|detail={exc}", file=sys.stderr)
        return 2

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        "HARNESSEDIT|ok={ok}|passed={passed}|total={total}|score={score:.3f}".format(
            ok=1 if report["ok"] else 0,
            passed=report["passed"],
            total=report["total"],
            score=report["score"],
        )
    )
    for item in report["results"]:
        print(f"HARNESSEDITCASE|id={item['id']}|ok={1 if item['ok'] else 0}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
