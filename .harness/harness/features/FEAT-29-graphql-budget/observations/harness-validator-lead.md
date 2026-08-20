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
  unresolved operator question. RULED by the operator 2026-08-19 (plan.yaml approval amendment):
  integration satisfied for T-03, unit is the signed evidence.

- 2026-08-19: `STATE.md` is stale against `feature.json` — repo-tier G-01 firing in the real. First
  seen at run 07 and STILL true at run 09: `STATE.md:20` pins `review_sha: 3fbfd0a` and `:35` says
  "5 cycles of 10; 8 runs of 20", while `feature.json` says `review_sha: c472a02`, `cycles_used: 6`,
  nine runs. The run-05 BLOCKED-vs-PASS contradiction I logged at run 07 HAS since been corrected in
  `feature.json` (run 01 is the BLOCKED one). So the pointer file rots once per run while the
  machine file gets fixed — the human-facing artifact is the one that drifts.

- 2026-08-19: the eight new wrap-site checks at `test-gh-cost-log.py:317-379` all call
  `_counting_fake()` with its default `rc=0` (`:289`). So no wrap-site check drives a FAILING
  invocation. `run_gh` RAISES `GhError` on non-zero rc (`factory_gh.py:163-168`) rather than
  exiting, so a failing-rc fixture there is achievable and merely absent; `gh-sync.py`'s `gh()`
  calls `skip()` = `sys.exit(0)` (`:79-82`, `:118-120`), so at THAT site it is forced under
  in-process fixtures. Two different situations that the eng lead's digest merged into one word,
  "forced".

- 2026-08-19 (run 09): I nearly failed a criterion on a premise nobody had checked. The eng lead
  escalated that SC-05's OFF-side failing clause "is asserted nowhere" and that it is "unpinnable by
  mutation". Both are false, and a `grep -n 'HARNESS_GH_COST_LOG'` over the test file settled it in
  one call: `test-gh-cost-log.py:251-259` drives `record(["issue","create"], 200, 210, 1)` — a
  FAILING rc with the variable genuinely unset — and asserts no file and no line. I had already
  drafted a mutant to prove the lead wrong about pinnability, and my mutant was ALSO wrong: it
  perturbed `measured()`'s disabled branch to call `record()` on failure, but `record()` carries its
  OWN independent `_enabled()` guard at `gh_cost_log.py:112-113`, so the mutant is
  behaviour-preserving and writes nothing. The clause is pinned at the layer that actually writes:
  mutating `:112` to `if not _enabled() and returncode == 0: return` reddens `:255-258`.
  The lesson is not about this feature. It is that BOTH the escalation's premise and my own
  counter-premise were reasoned from control flow rather than measured, and both were wrong in the
  same direction — toward there being a gap. An escalation that arrives with a defect already named
  makes the named defect feel like the question, and the cheap discriminating grep felt redundant
  because two tiers had already reasoned about it. Grep the assertion set before grading a criterion
  unevidenced, however confident the tier below is.

- 2026-08-19 (run 09): a defence-in-depth pair changes what a coverage gap MEANS. `_enabled()` is
  checked twice on independent paths (`record():112`, `measured():157`), so an untested path through
  the outer guard is not an unprotected path — the inner guard still holds and is itself pinned.
  Before calling a missing case a coverage gap, establish whether the guarantee has a second,
  tested guard behind it; if it does, the case buys a demonstration, not protection, and is rarely
  worth a cycle.
