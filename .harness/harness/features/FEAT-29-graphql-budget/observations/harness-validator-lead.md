# Observations — harness-validator-lead — FEAT-29-graphql-budget

- 2026-08-19 (run 07): I dispatched two mutating qa members in parallel onto the same file
  (`factory_gh.py`). `harness-team` §3c says `mutates_repo: true` steps serialize; I broke it
  because the second dispatch felt like "just one more measurement" rather than a repo mutation.
  It IS a repo mutation. `SendMessage` is disabled this session, so a parallel dispatch is
  UNRECALLABLE — there is no correction channel once the spawn is away. The prior-run incident on
  this same feature (run 05 stranding a `MUTATION PROBE` in `factory_gh.py:151`, found and reverted
  by run 06) is the same failure mode I then reproduced from the lead tier.

- 2026-08-19: the qa gate's discovery step rests on `test_kinds.<kind>.detect`, and in this repo
  those globs are a wrong model of what actually runs. `run-unit-tests.sh:17-18` is the real
  authority: `UNIT_SCRIPTS` has 18 entries, `INTEGRATION_SCRIPTS` has 12. But
  `test_kinds.integration.detect` names only 4 of those 12 (`test-check-state.py`,
  `test-factory-integration.py`, `test-gh-sync.py`, `test-check-plan-routes.py`), while
  `test_kinds.unit.detect` is `.claude/skills/harness/bin/test-*.py`, which matches ALL 30. So the
  unit kind always resolves "present" for any bin test file and the integration kind resolves
  present for 4 of its 12. A `missing` verdict from that glob is under-determined.

- 2026-08-19: the signed artifacts for FEAT-29 disagree with the matrix about where T-03's evidence
  lives. `test_matrix.feature.always` = `[unit, integration]`, but `BRIEF.md:83-90` gives SC-05
  `verify: automated  evidence: unit` (re-signed in approval amendment 5), `plan.yaml:265-266`
  gives T-03 `verify: --kind unit`, and no file in `test_kinds.integration.detect` appears anywhere
  in `plan.yaml`. Two lead contexts (eng run 05 Q1, me) independently landed on the same
  unresolved operator question.

- 2026-08-19: `STATE.md` is stale against `feature.json` — repo-tier G-01 firing in the real. STATE
  says "run: none in flight", branch tip `29c3e9d`, "3 cycles of 10; 3 runs of 20", and "THE BRANCH
  IS RED ON `--kind integration`". `feature.json` says `review_sha: 3fbfd0a`, `cycles_used: 5`,
  seven runs through `2026-08-19-06-eng`. Also `feature.json` records run 05 as `BLOCKED` while
  `runs/2026-08-19-05-eng/digest.md` records `VERDICT: PASS`. A successor reading either alone is
  misled about whether the branch is green.

- 2026-08-19: the eight new wrap-site checks at `test-gh-cost-log.py:317-379` all call
  `_counting_fake()` with its default `rc=0` (`:289`). So no wrap-site check drives a FAILING
  invocation. `run_gh` RAISES `GhError` on non-zero rc (`factory_gh.py:163-168`) rather than
  exiting, so a failing-rc fixture there is achievable and merely absent; `gh-sync.py`'s `gh()`
  calls `skip()` = `sys.exit(0)` (`:79-82`, `:118-120`), so at THAT site it is forced under
  in-process fixtures. Two different situations that the eng lead's digest merged into one word,
  "forced".
