# Observations — harness-pm — FEAT-07

- 2026-08-04 (goalcheck at `70b0ed3`): the dominant defect axis in this feature was NOT wrong
  behaviour — the validator was correct on every clause I ran by hand. It was a criterion that
  ENUMERATES N clauses being fixtured for fewer than N. Four instances on one feature: the validation
  panel's Q2 (SC-06, four accepted refusal shapes, one fixtured), SC-03 (two rejections named for
  dev-ops, only `n/a` fixtured — while the sibling SC-02 has BOTH halves at `:1110`/`:1113`, so the
  omission is accidental, not scoped), SC-18(a) (two properties required of the hint message, one
  asserted in the `mentions` list), SC-05 (five personas named, four fixtured — documentor has zero
  cases in `test-validate-digest.py` at any commit). The cheap detector is to count the clauses in the
  SC's own prose and count the `case()` lines, not to read the validator.
- 2026-08-04: the SC-02/SC-03 sibling asymmetry was the fastest tell of all — when two criteria are
  written as "the same X holds for persona B", diff persona A's fixture set against persona B's.
- 2026-08-04: `check-domain.sh` blocked the artifact path the dispatch named
  (`notes/goalcheck-harness-pm-c0.md`); `harness-pm`'s grant is `notes/research-FEAT-*.md`. A dispatch
  naming an artifact path is not evidence the path is in my grant.
- 2026-08-04: `./run-unit-tests.sh 2>&1 | tail -20; echo $?` reports TAIL's exit status and discards
  `test-validate-digest.py`'s output entirely (it is first in `SCRIPTS`). Redirect to a file, then
  grep — the piped form silently loses the evidence for every automated SC.
- 2026-08-04: `bash-write-guard.sh` rejects shell REDIRECTS and `rm` whose target is a shell VARIABLE,
  even into the session scratchpad. Literal absolute paths pass. Cost two blocked calls building the
  per-commit worktree loop for SC-11.
