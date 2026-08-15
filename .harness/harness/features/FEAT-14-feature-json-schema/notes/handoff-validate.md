# Handoff — validate — FEAT-14

Written at acceptance rather than at the seam, by the main session, from the validate runs'
digests on disk. Saying so because a handoff note that implies it was written live is a small
lie in the one artifact whose whole job is to be trusted.

## Next

- Three criteria are **operator-owed and still `not_met`**: SC-10, SC-11, SC-15. About nine
  minutes; the UAT script is written at `notes/uat-FEAT-14-sc15-readability.md`. No agent tier
  may mark them met, and none did.
- 21 backlog rows are filed as GitHub issues (#279-#292), plus evidence added to #72 and #250.
  Two are P0: #279, a required CI step whose asserted guard does not exist, and #280, an
  interrupted lead not stopping its children.
- FEAT-16 and FEAT-17 build next, on the settled format. Both signed, both idle.

## Trust

- **Both HIGH findings were closed and confirmed BY EXECUTION**, not by reading — mutation runs
  on both sides, verbatim output in `notes/receipt-harness-backend-dev-fix1-c1.md` and
  `notes/review-harness-code-reviewer-confirm.md`.
- All four gates green at merge, and re-run green on `main` after it: validator 0,
  `check-state.sh` 0, routes `0 violation(s) across 10 plan(s)`, full unit suite 0.
- CI's one required context, `integration`, passed on PR #293 before merge.
- The corpus carries **zero** `feature.yaml`. All 17 are `feature.json` and validate.

## Dead ends

- `gh issue develop` **cannot link an existing branch** to an issue — it creates one, and returns
  "API returned empty branch name" against a branch that already exists. Measured, not assumed.
  #204 was closed by hand instead. The closing-keyword string was declined by the operator, so do
  not reach for it; #277 carries the durable fix.
- Two probes proved nothing until redone and are recorded so nobody repeats them: one patched
  `json.dump` where the code calls `json.dumps`, so no crash was injected and a successful write
  was briefly read as a failure; one set `PYTHONPATH` against a script that prepends its own bin
  directory, so the shim never loaded.
- Reviewers **cannot** falsify enforcement-path findings — the write guard denies them the fixture
  creation needed to break a checker on purpose. Splitting probing to qa is what worked. Filed as
  #284; do not expect a panel to prove a guard claim end to end until it is fixed.

## Working set

- `.claude/skills/harness/bin/check-domain.sh` and `test-check-domain.py` — the schema gate and its
  four new fixtures. DEC-174 carve-out: main session only.
- `.claude/skills/harness/bin/gh-sync.py` and `test-gh-sync.py` — atomic write, and the reader
  converged on `json.load`. Its contract is unpinned (#285).
- `.harness/features/*/feature.json` — all 17, plus per-feature `notes/receipt-feature-key-drop.md`
  recording every key T-04 removed and its value.
- `notes/ship-review-2026-08-12-validate.md` — the ship review, and PR #293's body.
