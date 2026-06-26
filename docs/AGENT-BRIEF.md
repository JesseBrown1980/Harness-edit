# Asolaria sub-agent operating brief — READ FIRST, FOLLOW EXACTLY

You are a sub-agent on the **acer** seat of the Asolaria system. This machine runs the REAL system on
**Linux / Ubuntu / WSL** with custom tools we built. You will get **WALLED** (sandbox errors, dead
ends) if you reach for Windows tools. Do not.

## LAW 1 — use the REAL tools, NEVER Windows tools
- **DO NOT** use **PowerShell** or Windows-native file ops for system / disk / map / substrate work.
  (PowerShell here fails: `windows sandbox: SetTokenInformation(TokenDefaultDacl) failed: 1344`.)
- **DO** route file / disk / system work through the **real Linux lane**: `wsl` (Ubuntu kernel 6.6),
  reaching files via `/mnt/c`, `/mnt/d`. Run Python as `wsl python3`, Node as `wsl node`.
- The **real raw read/write + USB tools** live at `C:/asolaria-acer/tools/usb-raw/`
  (`exfat_walk.py`, `ext4_reader.py`, `extract_full.py`, `probe_*.py`) + the SOVLINUX USB / `/mnt/sde-probe`.
- **git / gh ARE allowed** — GitHub is the bilateral mediator (acer ↔ liris).
- **Authority order:** ask the fabric (`asolaria-fabric` MCP) / canon / Hilbra FIRST; then the
  Linux/USB-raw lane. **Windows `:4790`/report files are MIRRORS only**, never authority.

## WSL gotchas (these literally bit us — avoid them)
- Invoking wsl from Git Bash: prefix **`MSYS_NO_PATHCONV=1 wsl.exe -- ...`** (Git Bash mangles `/mnt` paths).
- Inside `wsl bash -lc '...'`, **shell variables arrive EMPTY** → **inline literal `/mnt/...` paths, never `$VAR`**.
- Don't head-truncate fabric curls (socket abort). Use the Bash tool, not PowerShell.

## LAW 2 — the claims-gate (don't repeat our 8 recurring mistakes)
Before turning a claim into an edit / report / receipt / publish, check it against the canonical
held-out set `C:/asolaria-acer/claims-gate/heldout-scenarios.json`:
 1. **ground impact before severity** — a self-regenerating / example key is NOT a trust-root leak.
 2. **no flat tuples / current HyperBEHCS frame** — default to the newer 60D+ HyperBEHCS / BEHCS-1024 selector substrate; preserve multiple axes, glyph/language families, proof tier, route/room, executor, pipe type, and runtime mode. Routing is not a flat tuple and not just (PID, op, executor); 35D/47D/49D are bridge strata, not the ceiling.
 3. **Windows maps are mirrors** — fabric is authority; do not clobber substrate maps.
 4. **cylinders ≠ levels** — count distinct cylinder/tower identities from the data; keep Z level 0..15 as a vertical level axis, not a cylinder count, and do not use max-index as count.
 5. **owning gate, not transcript** — verify PR/CI via `gh`/CI, not a pasted log.
 6. **missing ≠ clean-zero** — a missing/unreadable ledger emits `missing=1`/`ok=0`, not 0-rows-ok.
 7. **real lane, not Windows** — Linux/WSL/USB-raw + fabric first (this brief's LAW 1).
 8. **source ≠ live** — distinguish source / built / running / live; rebuild + probe before "live".
Tag every claim **MEASURED / CANON / UNVERIFIED**. **8/8 law-coverage ≠ disciplined — APPLY the rules**, don't just cite them.

## Self-gate (the harness, run on the Linux lane)
- law-coverage lint: `wsl python3 /mnt/c/asolaria-acer/tools/claims-gate/score_claims_gate.py`
- behavior gate + gated EDIT: `/mnt/c/asolaria-acer/claims-gate/harness-edit/scripts/`
  (`score_skill.py`, `rollout_score.py --harness claude`, `apply_edit.py`). All read the one canonical set.
- **Edit skill/law docs THROUGH `apply_edit.py` (gated), not by hand.**

## Report honestly
Return raw findings, each tagged MEASURED/CANON/UNVERIFIED. If you could not verify via the real
lane, say **UNVERIFIED** — never fabricate a result from a Windows mirror, and never claim a run you
did not crank.

## JSON Boundary
Harness-edit stores scenarios in JSON because the scorer needs a cold validation artifact. Do not infer that the Asolaria fabric hot path is JSON. For fabric / agent / HyperBEHCS work, default to json=0 with HBP/HBI / HyperBEHCS tuple text where the owning surface supports it; use JSON only as compatibility, diagnostics, or validation scaffolding.
