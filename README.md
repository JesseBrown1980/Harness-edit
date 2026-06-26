# Harness-edit

SkillOpt-style edit harness for validating changes to agent skill documents.

This repo is the **harness**, not the skill. It implements the missing gate from the SkillOpt paper: a candidate skill/law edit is not accepted just because it sounds right. It must improve a held-out scenario set and avoid regressions.

Source paper: <https://arxiv.org/abs/2605.23904>

## What This Provides

- A small deterministic scorer for skill text.
- A JSON scenario format for held-out mistakes and expected rules.
- One canonical Asolaria scenario set seeded from real correction cases, used by both v1 text lint and v2 rollout scoring.
- A reusable sub-agent brief (`docs/AGENT-BRIEF.md`) so delegated waves inherit the same real-tools law before they touch Asolaria substrate/map/USB work.
- Public-safe scaffolding only. No private feeds, rendered maps, vaults, keys, receipts, or local memory files are included.

## What This Is Not

- Not the full SkillOpt optimizer loop.
- Not a full model-rollout optimizer yet.
- Not a replacement for fabric/canon/GitHub owning gates.

This repo has two gates over the same scenario set: v1 rule-coverage scoring over skill text, and v2 rollout behavior scoring over agent responses.

For delegated work, inject `docs/AGENT-BRIEF.md` into every fresh helper prompt. Fresh helpers do
not reliably inherit the parent law or memory; the brief tells them to use the owning Linux/Ubuntu/WSL
/ USB-raw lane instead of treating Windows report files as authority.

## Quick Start

```bash
python scripts/score_skill.py --skill path/to/SKILL.md --scenarios examples/asolaria-scenarios.json --report out/report.json
```

Exit codes:

- `0`: all scenarios pass.
- `1`: at least one scenario fails.
- `2`: invalid inputs or harness error.

## Scenario Format

Each canonical scenario can serve both gates. For v1 text lint it has:

- `id`: stable identifier.
- `failure`: the mistake the skill should prevent.
- `must_include_any`: at least one phrase from each inner group must appear in the skill text.
- `must_not_include`: phrases that must not appear.

For v2 rollout scoring it also has:

- `prompt`: the realistic situation used for a rollout.
- `rubric.apply_any`: response markers that show the correct behavior.
- `rubric.fail_any`: response markers that show the old mistake.

This is intentionally simple. The scorer is a first gate, not the whole evaluator.

## SkillOpt Mapping

- Trainable artifact: a skill/law Markdown file.
- Held-out set: `examples/asolaria-scenarios.json`.
- Textual learning-rate analogue: bounded candidate diff reviewed separately.
- Validation gate: `score_skill.py` must strictly improve or maintain all held-out cases.
- Rejected buffer: failed reports become future scenarios.
