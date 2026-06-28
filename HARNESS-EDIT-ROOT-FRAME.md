# Harness-edit — SkillOpt / claims-gate / watcher-correction loop

Date: 2026-06-28 · Branch: `acer/p4b-harness-loop` · **docs-first, E=0.** No runtime fire, no cutover, no corpus, no keys. For liris attack-verify before main.

## Claim
Harness-edit is **the watcher-correction loop applied to the system's own skills/laws** — not a hot-path
JSON data fabric:

> a **SkillOpt-style, validation-gated edit loop** (`score_skill` / `rollout_score` / `apply_edit`) over
> the **claims-gate** held-out scenarios — it changes a skill/law doc **only if** held-out coverage does
> not regress, else it refuses and logs to the rejected-edit buffer.

It is the meta-loop that gates self-editing; it does not route runtime PID traffic.

## How it maps to the root
- It is the **N-Nest-Prime corrective gate, raised to the docs/skill layer**: a proposed edit is the
  "child," the held-out validation is the "watcher," and the edit converges **only when**
  `reported == recomputed-truth` (coverage doesn't regress) — exactly `recurrence + correction = cognition`,
  applied to the system's own laws.
- It is **how the system self-improves its skills safely**: edits don't self-authorize; they pass the
  gate or go to the rejected buffer (consent/scaling stays non-recursive, anchored at the operator apex).
- It is the local analog of Hermes's learning-loop, but **gated** — the upgrade we keep over the external
  mirror (don't harden a negative claim into a refusal; make the gate prove it).

## Evidence tags / honest boundaries
- CANON: Harness-edit implements the SkillOpt paper's validation-gate + edit-budget + rejected-buffer =
  the CLAUDE.md / memory / claims-gate edit loop; `apply_edit.py` applies only on `VALIDATION_ACCEPTED`,
  else `REJECTED_BUFFER`.
- BOUNDARY: this is **NOT** a hot-path / JSON runtime fabric — it is a decides-only edit/validation tool.
  It governs *changes to docs/skills/laws*, not live agent traffic.
- BOUNDARY: "8/8 law-coverage ≠ disciplined" — the gate reminds; it does not by itself prove the edit is
  wise. The verifier (the other seat) still attack-verifies content, per author≠verifier.

## Hard holds (T0 only; NOT this docs pass)
No auto-application of edits to live law/skill docs without the gate + operator authority; no runtime
fire; no USB/ADC/census/private-root.
