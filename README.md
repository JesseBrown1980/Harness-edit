# Harness-edit

SkillOpt-style edit harness for validating changes to agent skill documents.

This repo is the **harness**, not the skill. It implements the missing gate from the SkillOpt paper: a candidate skill/law edit is not accepted just because it sounds right. It must improve a held-out scenario set and avoid regressions.

Source paper: <https://arxiv.org/abs/2605.23904>

## What This Provides

- A small deterministic scorer for skill text.
- A JSON scenario format for held-out mistakes and expected rules.
- An example Asolaria scenario set seeded from real correction cases.
- Public-safe scaffolding only. No private feeds, rendered maps, vaults, keys, receipts, or local memory files are included.

## What This Is Not

- Not the full SkillOpt optimizer loop.
- Not a model-rollout evaluator yet.
- Not a replacement for fabric/canon/GitHub owning gates.

This is the buildable v1: rule-coverage scoring over held-out scenarios. A later v2 can add actual frozen-agent rollouts and scored trajectories.

## Quick Start

```bash
python scripts/score_skill.py --skill path/to/SKILL.md --scenarios examples/asolaria-heldout.json --report out/report.json
```

Exit codes:

- `0`: all scenarios pass.
- `1`: at least one scenario fails.
- `2`: invalid inputs or harness error.

## Scenario Format

Each scenario has:

- `id`: stable identifier.
- `failure`: the mistake the skill should prevent.
- `must_include_any`: at least one phrase from each inner group must appear in the skill text.
- `must_not_include`: phrases that must not appear.
- `notes`: human context for reviewers.

This is intentionally simple. The scorer is a first gate, not the whole evaluator.

## SkillOpt Mapping

- Trainable artifact: a skill/law Markdown file.
- Held-out set: `examples/*.json`.
- Textual learning-rate analogue: bounded candidate diff reviewed separately.
- Validation gate: `score_skill.py` must strictly improve or maintain all held-out cases.
- Rejected buffer: failed reports become future scenarios.
