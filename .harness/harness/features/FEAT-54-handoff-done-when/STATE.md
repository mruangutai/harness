# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: ship — branch pushed, PR #1285 open, BLOCKED on the required `integration` check
- squad: none spawned this run; the ship path is orchestrator and main-session work
- status: review (plan.yaml `status: review`) — the station stays here until the merge lands

The ship run pushed `feat/FEAT-54-handoff-done-when` (45 ahead of `origin/main`, 0 behind, so no
force was needed) and opened **PR #1285**, recorded as `pr: 1285`. Ten of eleven CI steps pass,
including the unit suite, the integration suite, the plan-route, instruction-path and layout gates.

**The merge is blocked by this feature's own new CI step.** The `Repository-state gate` added
post-review as B-5 runs `check-state.sh` and exits on its status; on a GitHub runner that checker
reports exactly one violation — `INV-31: core.hooksPath is unset` — because `actions/checkout`
never sets it and INV-31 asks whether THIS MACHINE runs the `post-merge` hook. The step is red by
construction on every runner, `integration` is the single required context with
`enforce_admins: true`, so nothing in this repository can merge until it is fixed.

Measured in a fresh clone of the branch at `91495a60`, under CI's own conditions: hooksPath unset →
exit 1, that one violation and nothing else; hooksPath set to `.claude/skills/harness/hooks` →
exit 0 over 877 rows. The remedy is one `git config` line inside the existing step, and it
suppresses nothing — INV-31's second branch then really does assert `hooks/post-merge` exists and
is executable, and it passes.

The remedy edits `.github/workflows/tests.yml`, which hosts the required check's own gate steps.
The path resolver grants that file to `harness-dev-ops`, so a squad dispatch was available; it was
refused on the merits, not on domain. DEC-174 stops self-hosting at the enforcement layer, and this
feature's own record already settled the lane for this exact row — all seven post-review remedies,
B-5 among them, landed main-session-direct. It is returned up as F-01 with the patch text.

Not done, each for a stated reason: the merge (branch protection, no override exists); the `done`
station (false over an unmerged feature); `gh-sync.py ship` and `record-pr` (both refuse at exit 1
while the feature dir resolves inside `.claude/worktrees/`); worktree removal (never this agent's
act — DEC-193; the `post-merge` hook takes it when `main` pulls).

Everything the feature itself had to prove still holds: final independent review PASS with no
findings at `df5f7ea1`, product goal-check PASS on 15/15, unit and integration suites exit 0, and
the repository-state gate exits 0 in a correctly configured clone. `review_sha` stays `df5f7ea1`;
every commit after it touches only this feature's record and notes, no code.

Cycles used: 22 of 30 — this run added none, because F-01 was routed up, not back to a lead
(DEC-157 counts rework only). Runs stand at 51 against the informational budget of 20; this run
spawned nobody. Operator briefing: `notes/ship-review-2026-09-04-ship.md`.

## Open Questions

- Q1 (blocking, for the operator): F-01. Apply the one-line `git config core.hooksPath` fix to the
  `Repository-state gate` step in `.github/workflows/tests.yml` — main-session-direct under
  DEC-174 — or overrule that reading and have it routed to `harness-dev-ops`. Nothing merges in
  this repository until it lands. Patch text and both measurement arms are in
  `notes/ship-review-2026-09-04-ship.md` F-01.
- One residual cannot be closed without fabricating an artifact: ledger entry
  `2026-09-02-goalcheck-c1-product` has no run directory. The run is real — its evidence survives
  as `notes/research-FEAT-54-goalcheck-plan-c1.md` — so the entry is truthful and was kept.
  Deleting it would erase a recorded FAIL; writing a digest for a run whose digest was never
  created would invent one. Left as a known ledger-floor gap.
- The B-7 exclusion cites `signed: DEC-187`, the decision that established the rule and signed
  `functional`'s exclusion on the same double-count rationale. If the operator wants a DEC of its
  own for `eval`, that is a documentor dispatch.
