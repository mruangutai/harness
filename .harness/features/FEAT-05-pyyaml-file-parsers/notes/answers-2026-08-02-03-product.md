# User answers — FEAT-05, after run 2026-08-02-03-product

Taken by the main session, 2026-08-03. Both artifacts are now `status: approved`; the signature
notes on BRIEF.md and PLAN.md are the authority and this file only summarises the rulings.

## Q1/Q2/Q3 — the three FALSE brief statements: SIGNED WITH AMENDMENTS

- **Q1 `cost-report.py`** — STAYS IN SCOPE. It parses no YAML, but it hand-rolls YAML manipulation
  with a regex, which is the defect class. Its REQ-01 characterisation is corrected, not its scope.
- **Q2 SC-03 count** — criterion stands, count corrected. Judge SC-03 against the census, never the
  parenthetical. 7 of 17 calls in `check-state.sh` legitimately survive, six parsing markdown.
- **Q3 SC-02 baseline** — stale. Re-baseline `check-state.sh` at build open; the BRIEF that made it
  exit 1 is now signed.

## Q7 — ROUTING WALL: main-session steps, `team-config.yaml` NOT widened

T-10 and T-11 are MAIN-SESSION steps inside the build spine, and T-12 blocks on T-10. Do not attempt
them, do not work around the domain boundary — **return, and the main session executes them.**
`dev-ops` remains granted neither `.gitignore`, nor `templates/**`, nor `harness-init/SKILL.md`.

This is the wall's third recurrence (FEAT-03 Q13, FEAT-04 T-09). The user chose the proven route
rather than widening a boundary drawn deliberately. The recurrence is a signal about the domain
model and is deliberately NOT acted on inside this feature.

## Budget — HELD at 120, overrun ACCEPTED

Not raised. 92 of 120 went to the plan phase; ~28 remains for build, validate and ship. Cost is
reported, never gated (DEC-134). Report the real number in the ship briefing; do not trim scope to
fit the number, and do not treat the ceiling as a stop.

## Q5 — discharged

The main session appended `## Approval` to both artifacts, as it must. No agent may.

## Standing context the main session added while you were planning

- **DEC-172 was CORRECTED** at `DECISIONS.md:4566-4580` — 13 files not 16, and templates may ship
  FIRST because the current parser already accepts a fenced return. You flagged the grilling artifact
  as stale on this; it has been corrected too. Affects FEAT-06, not this feature.
- **The 13 return templates are ALREADY FENCED**, done by the main session on 2026-08-02.
- **DEC-173 is new** (`DECISIONS.md`, index regenerated): `n/a` is the one spelling for "this did not
  happen", now legal on `suite`, `matrix_ok`, `severity_max`, `contract`, `surface`, `risk`. Declining
  a GATE while claiming PASS is rejected, keyed by persona — `{dev: {suite}, qa: {suite, matrix_ok}}`.
  **Your Q6 finding means this is NOT in force for you**: the hook resolves the main checkout's
  `validate-digest.py` (0 `GATE_FIELDS`) rather than this worktree's (2). Encode digests against the
  OLD contract until the branch merges, and do not read a rejection as your own error.
- Issue #5 is closed; `test-gen-decisions-index.py` no longer freezes DECISIONS.md counts.

## Not answered, because you did not ask and it is not yours to fix

B-13 (`lead` `members: []` with `steps_run > 0`) and the `stop_hook_active` pass-through are open
harness defects recorded in DEC-173. Neither blocks this feature.

## CORRECTION, 2026-08-03 — the Q6 paragraph above is DISPROVEN

This file told you DEC-173 was "NOT in force" here and to "encode digests against the OLD
contract until the branch merges." **That was wrong.** Measured by probe (receipt at
`notes/receipt-main-session-hook-resolution-probe.md`): the WORKTREE's hook copies execute and
`CLAUDE_PROJECT_DIR` is the worktree, so DEC-173 IS in force and the fenced return templates are
live. I had verified only that the two `validate-digest.py` copies differ, then asserted which one
runs — a different claim, and the wrong one.
