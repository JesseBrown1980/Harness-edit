# v2 — Rollout Behavior Scoring

v1 (`scripts/score_skill.py`) lints the **skill text** for rule coverage. That is necessary but not
sufficient: a rule can be present in the law and the agent still violates it. (Observed in practice:
an agent's law layer scored **8/8** rule-coverage while the agent committed several of those exact
mistakes in the same session.) Coverage of the law ≠ disciplined behavior.

**v2 (`scripts/rollout_score.py`) scores the agent's *response* to a realistic prompt** — the axis
the SkillOpt paper (arXiv 2605.23904) is actually about — and gates on whether the skill changes
behavior on the held-out scenarios.

## Harness-agnostic adapters

`--harness` selects how a `(skill, prompt)` becomes a response (the SkillOpt adapter interface):

| harness | needs | use |
|---|---|---|
| `transcript` | nothing (offline) | CI + self-test; reads a pre-recorded response map |
| `echo` | nothing | plumbing test only |
| `claude` | `ANTHROPIC_API_KEY` | the **Claude Code / acer** harness |
| `codex` | `OPENAI_API_KEY` | the **Codex / liris** harness |

Live adapters error clearly when the key is absent; no key is ever read into the report or stored.
This is what makes the harness work across both seats — Claude and Codex are first-class targets.

## Run

```bash
# offline self-test: a "good" trajectory should pass, a "bad" one should fail
python scripts/rollout_score.py --scenarios examples/asolaria-rollout.json \
  --harness transcript --transcript examples/transcripts/good.json   # -> ok=1 8/8
python scripts/rollout_score.py --scenarios examples/asolaria-rollout.json \
  --harness transcript --transcript examples/transcripts/bad.json    # -> ok=0 0/8

# offline delta self-test: good with-skill trajectory vs bad no-skill baseline
python scripts/rollout_score.py --scenarios examples/asolaria-rollout.json \
  --harness transcript --transcript examples/transcripts/good-with-bad-baseline.json \
  --baseline                                                    # -> ok=1 8/8, baseline=0, delta=8

# live rollout with the Claude (acer) harness, skill vs no-skill delta
ANTHROPIC_API_KEY=... python scripts/rollout_score.py \
  --scenarios examples/asolaria-rollout.json --harness claude \
  --skill ../path/to/SKILL.md --baseline
```

`--baseline` runs each scenario with the skill **and** with no skill, and reports `skill_delta`
(the SkillOpt forward pass: does the skill actually help?). The gate: an edit is accepted only if it
raises the rollout pass-rate without regressing a passing scenario.

## Scenario format

Each scenario adds a realistic `prompt` and a `rubric` to the v1 fields:

```json
{
  "id": "...",
  "failure": "...",
  "prompt": "the situation that triggers the mistake",
  "rubric": {
    "apply_any": ["markers a correct response shows"],
    "fail_any":  ["markers of committing the mistake"]
  }
}
```

A response **passes** iff it shows ≥1 `apply_any` marker and **0** `fail_any` markers.

## Honest boundaries

- The rubric is **keyword-based** — the right *axis* (behavior), but a coarse *judge*. A v3 should
  use an LLM-as-judge with the same scenario set; the adapter + gate plumbing here is unchanged.
- `transcript` mode is fully offline and deterministic (good for CI). The `claude`/`codex` adapters
  do real rollouts but need keys + network, so they are not run in CI by default.
- This is still a **scaffold of SkillOpt**, not the full optimizer loop (no edit proposer / textual
  learning rate yet). It is the missing *behavior gate*; the edit-proposer is the next layer.
