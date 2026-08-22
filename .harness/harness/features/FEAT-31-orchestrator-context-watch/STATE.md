# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch · phase **validate** · 19 of 19 tasks `done`
- run: `runs/fix3-eng` IN FLIGHT (Q-WARNVERB, the panel's single `high`)
- status: in_progress · **cycles 6/10**, runs 17/20 (runs INFORMATIONAL, INV-22)
- `review_sha`: **`fcb8984`** — RE-PIN after the fix commit lands
- `check-state.sh`: ONE violation, FEAT-26's unapproved BRIEF (another flow). None in FEAT-31.
- **BOTH GATES PASS** (approved / operator / 2026-08-21). **The operator PRE-APPROVED the ship.**

### WHERE THE THREE GATES STAND

- **qa gate (blocking): matrix PASSES** at `fcb8984` — unit, integration, `--check-kinds` all exit 0,
  zero FAIL / MISCONFIGURED / KIND-DRIFT. Its SC-09 FAIL is closed by T-19.
- **goal-check: 12 of 14 met.** SC-01..09, 11, 13, 14 met. **SC-10 not met** (`verify: uat`).
  **SC-15 partially met** — gate half met, behaviour half not.
- **panel: FAIL, `severity_max: high`, ONE finding.** `gates.review: advisory_unless_high`, so it
  gates. Everything else held under independent re-derivation.

### THE GATING FINDING — Q-WARNVERB, and it is the feature's OWN rule

`context-watch.py:536-543` never states the write LANDED. `notes/settled-Q-HOOKCTX.md:48-51` makes it
a **hard obligation**: the text must say *in its first line* that nothing was blocked, the call
succeeded, and no retry or revert is needed — **before** any mention of context size. The shipped text
leads with context size and satisfies none of the three clauses. **Exposure is total and measured: 36
of 36 crossing orchestrators made a Write/Edit/Bash call afterwards**, and the framing already caused
a real revert of a landed write. `check-domain.sh:703` carries the signed remedy. Live corroboration:
my own eight `feature.json` writes each drew a POST exit 2 wrapped "blocking error" — **all landed**.

### pm REFUSED MY SC-15 EVIDENCE, AND WAS RIGHT TO

I am a live relay: I resumed from disk and my first dispatch matched `handoff-build.md`'s `## Next`.
**But I also held a main-session prompt naming T-05 and T-09** — two sufficient causes for one
observation, against a criterion whose premise is a successor given ONLY the feature directory. pm
called it **confounded rather than imperfect**. I offered it and declined to grade it; the grader
refused it. That separation is the point.

### MY SIX ERRORS — detail is in the commit messages; the durable rules are here

1. **A run digest is not evidence until its run has RETURNED.** Broken three times; the third
   dispatched T-19 TWICE (two hosts concurrently — `mutates_repo` serializes inside ONE host only).
   DEC-159 escaped carrying the rule twice only because pm wrote "run verify BEFORE your edit" into
   T-19's intent. Later proved by watching SIMPLIFY's `blocked` digest hash stable five times, then
   change to PASS.
2. **Regenerate a generated index UNCONDITIONALLY** after any body edit — T-19 shifted 39 `@line`
   anchors. "Only if the row changed" was wrong in the silently-corrupting direction.
3. **DEC-141 is `[map,brief]`/`render-map.py`**, not index generation. Authority: `INDEX.md:1-3`.
4. **`^### DEC-` matches only the 25 amendment sub-headings**, not the 195 `## DEC-N` entries — so
   "highest is 194" was wrong; it is 197, and T-19's entry is DEC-198.
5. **I named a receipt path pm holds no grant for**; the guard denied it correctly (#216).
6. **BOTH SIDES OF AN EQUALITY OVER A MOVING CORPUS MUST BE MEASURED IN THE SAME BREATH.** I claimed
   "103 + 5 vs a glob of 107 — exact agreement". 103 + 5 = 108. The finding was real but I paired
   figures taken minutes apart while the corpus grew (this session adds sidecars). **Re-measured
   atomically: glob 109, tool 104 + 5 = 109, closes exactly.**

Errors 2 and 3 were caught by a lead reading source rather than complying with my prose; 5 by the
domain guard; 6 by the review panel.

### THE ENFORCEMENT LAYER GOVERNING THIS SESSION IS THE MAIN CHECKOUT'S

Hooks resolve via `CLAUDE_PROJECT_DIR` to the main checkout, so a branch changing the enforcement
layer is governed by the OLD layer while being built. **T-15's `agent` rule is INVERTED in-session**
(the branch validator passes with the key and fails naming `runs[9]` without it, while the session's
hook rejects it as `undeclared`). **T-17's hook cannot be observed firing from here** — first fires
after merge. Neither is a defect.

### WHAT REMAINS

fix3 (in flight) → verify + commit → **re-pin `review_sha`** → close-out (ship-refresh + distillation,
**TWO dispatches in ONE message**) → briefing + `render-brief.py`. **The UAT gate then blocks the ship
and only the operator can discharge it.**

### Premises the next cycle must not re-derive

- **NO GATE EVER WALKS THE REAL PROJECTS ROOT.** `verify-context-watch-live.py` appears **0 times** in
  `run-unit-tests.sh` — neither script list — so even its own `--self-test` never gates. **The
  Defect-2 mechanism (discovery depth against real data) is undetectable by CI.** Deepest residual.
- **The tool cannot say "I could not scan."** `main()`'s catch sets `rows = []` and prints "no
  orchestrators found" at **exit 0** — a false all-clear. `med`: the trigger needs a non-numeric
  `usage` field Claude Code does not emit today. Three filed items are this one absent capability.
- **"187 PASS lines" IS NOT A COVERAGE MEASURE** — one PASS line per script, and
  `test-context-watch.py` prints `ok`/`FAIL`, so its 78 cases contribute exactly one.
- **Q-CHECKCOUNT CLOSED benign** — `test-context-watch.py:668-669` is dead canary code, 78 − 2 = 76.
- **Q-DEC159CAP, verified three ways:** `DECISIONS.md:3986` denies handoff notes above **40** lines;
  its own `:3968` says **~60 (raised at DEC-160)**; `check-domain.sh:951` enforces **60**. The entry
  contradicts itself AND the code, and **it survived T-19 — a cycle whose subject was a false clause
  in this same entry.** No SC covers it; fixing it is scope expansion, left deliberately.
- **Q-HOOKCTX is CLOSED.** Seven rows filed (#663-#669). Propose only what is NEW.
- **`.gitignore:7` ignores `runs/**`** — zero run files tracked, so every digest path in the briefing
  is LOCAL and never reaches the default branch.
- Do NOT trust a `verify:` floor expressed as an absolute case count; verify by case NAME.
- Do NOT run `feature-worktree.py behind` from inside this worktree — use the PRIMARY checkout.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING SIGNAL: the
orchestrator asks the user, writes answers to notes/answers-<runid>.md, and re-delegates with that
path. Clear each entry when it is answered.>

- **Q-UAT, BLOCKING, THE OPERATOR'S ALONE.** SC-10 and SC-15's behaviour half. `gates.uat:
  blocking_when_uat_criteria_exist`, so it blocks the ship independently of qa and the panel.
  **SC-15's behaviour half needs a CLEAN relay** — a successor whose ONLY input is the feature
  directory, with no dispatch naming its tasks.
- **Q-SIGNATURE, BLOCKING-ADJACENT.** The plan gained a 19th task after the 18-task signature.
  `approval:` is byte-identical and SC-09 was already approved scope, so T-19 fulfils the signature
  rather than extending it — the operator confirms, not me.
- **Q-DEC159CAP, non-blocking, a FALSEHOOD IN THE AUTHORITY.** Above; one line, three anchors.
- **Q-LIVEGATE, NEW, non-blocking, deepest residual.** No gate walks the real projects root.
- **Q-HOOKTAX, NEW, non-blocking.** The matcher fires for every agent type while the script gates on
  `agent_type` internally — ~19ms per early-exit call from ~15 non-subject personas. The matcher keys
  on tool name only, so the filter cannot move into `settings.json`.
- **Q-POSTCHAIN, NEW, non-blocking.** Does Claude Code run every command in one `PostToolUse` entry
  regardless of an earlier exit code? `check-domain.sh --post` and `context-watch-hook.py` share that
  entry; if an earlier exit 2 short-circuits, SC-13 silently fails. First testable after merge.
- **Q-STRAY, non-blocking, OUTSIDE MY WORKTREE.** A stale digest claiming BLOCKED sits in the MAIN
  checkout under `runs/t09-product/digest.md`.
