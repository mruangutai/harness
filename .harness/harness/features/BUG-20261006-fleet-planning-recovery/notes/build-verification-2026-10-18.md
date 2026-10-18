# Direct build verification — T-01 and T-02

## Scope and status

Implemented the authorized tooling/schema/regression cutover and governing guidance. T-01 and T-02 are done. T-03 through T-05 have not been activated: no actual Kaya capture, historical repair, installation, live recovery, product work, merge or deployment occurred. No local commit or review pin has been created. The required full matrix has not run; its approved sequence requires one authentic pinned review SHA after T-02.

The canonical checker invoked by the T-02 station write still reports two existing feature blockers: the original `2026-10-06-2-simplify-eng` return has neither an accepted durable record nor typed refusal evidence, and this feature's existing nonempty mirror lacks `github.repo` provenance. The operator approval expressly preserves historical records; neither has been silently repaired or exempted. Historical missing cycle evidence remains a note, not an invented cycle or a FAIL-count floor.

## Exercised evidence

- The approved five-command T-01 verification chain passed first in 52.84 seconds, then after the risk/altitude fixes in 52.97 seconds, below the 60-second ceiling. The latter run includes 100 feature-record unit tests and 9 digest-reader unit tests. Complete latter output: session artifact 228.
- `test-merge-gate.py`, `test-post-merge-sweep.py` and `test-board-lifecycle.py` passed together in 19.87 seconds after refactoring. Complete output: session artifact 231.
- Governing decision anchors passed: 30 checked, zero failures. Canonical index regeneration followed by `--stdout | diff -` had an empty diff.
- Four independent read-only simplify angles completed. Reuse, simplification and efficiency reported no findings. Altitude identified inconsistent working-directory versus feature-relative digest resolution. A new permanent regression failed before the fix; all 17 close-run tests passed afterward. Close-run now resolves the operand once at its composed boundary.
- `test-check-state-feat59.py` and `test-check-state-table.py` passed together in 18.13 seconds after all binding discriminators were migrated to the shared predicate.
- The real current build run closed through `close-run` using its feature-relative JSON receipt, BLOCKED verdict and explicit zero send-backs. Its new hash-bound attribution was recorded without modifying any historical run.
- Real isolated close-run CLI smoke, from a conflicting working directory: feature-relative accepted return closed with exit 0; a valid target could not inherit a shadow file's contract rejection and left ledger bytes unchanged with exit 2; a malformed target closed BLOCKED with exit 0 and refusal proof for its own bytes.
- Manual probe close helper smoke used real isolated run-end subprocesses: FAIL/0 preserved a residual of 4; PASS/1 preserved that residual and produced total 5; missing count and contradictory verdict both left the run PENDING and total 4. No live host session or registry claim was started. The initial smoke fixture was rejected because it was outside a legal features directory; correcting that fixture layout produced the four results above.
- There are 19 new named unit-test methods against baseline `63cac11a3216aa8d34792665a05fcb185f7cf73b`, plus integration scenarios. This is a source comparison, not a claim that the full matrix ran.

## Pre-pin complexity assessment

Assessed the actual working-tree Python sources against the baseline using `code_grade`'s existing gating/classification functions, retaining the tracked logical `.claude/skills/harness/` paths. Only the head-source reader was directed to current files; no grading rules or production sources were modified for the assessment. This is explicitly NOT a commit-pinned grading run. An earlier assessment using physical `.agents/` paths had no baseline preimages and is invalid; it is not review evidence.

No gated grade-1 function or production grade-3 function remains. The raw classifier still requires the following 34 grade-2 reasons; it has not been described as an unconditional pass. These are deliberate cohesive boundaries, not permission to waive correctness, weaken assertions or refactor unrelated legacy functions.

### gh-sync.py

1. `load_config`: preserves ordered owner-onboarding skips, authoritative bound resolution, provenance refusal and host availability checks in the command's one preflight; optional owner config reading is separate.
2. `_replacement_create`: pending-before-dispatch, confirmed-save-before-next-create and known-undispatched versus uncertain failure handling form one interruption protocol.
3. `_adopt_replacement_receipt`: generation, plan, exact pending role, positive issue number, namespace uniqueness and authorization must be checked before the same durable adoption transition.
4. `_resume_replacement`: validates durable operands, original authorization and pending reconciliation together; separating them would obscure which generation can resume.
5. `cmd_recover_mirror`: owns operator operands, start-versus-resume dispatch and the command's one refusal funnel; resume and completion transitions are separate named units.

### feature_schema.py

6. `recovery_command_for`: is the single policy for the frozen era set, started work and terminal/full recovery selection; splitting those conditions would encourage competing recovery rules.
7. `verify_evidence_ref`: file identity, immutable hash and exact subject/effect verification are one trust boundary.
8. `run_evidence_problems`: cross-checks each run's accepted/refused attribution and authorization in one local evidence audit, without deriving counts from verdicts.
9. `mirror_provenance_problem`: distinguishes repository conflict, unproven active numbers and incomplete replacement generations in one shared refusal policy.

### feature-record.py

10. `cmd_record_history.mutate`: the locked mutation must preserve existing history while distinguishing cycle and refusal evidence and refusing conflicting replay.
11. `_run_end_digest`: authentic verdict/count, existing immutable proof and replay identity are checked together before recording attribution.
12. `cmd_run_end.mutate`: attribution delta, preserved residual, verdict/end time and measured-token preservation belong to one atomic ledger transition.
13. `_stage`: validator exit classification and the refused-return inversion must remain visible together; a subprocess failure is not automatically contract-rejection evidence.
14. `_close_refused_run.mutate`: compares the observed rejection's bytes, checks any historical attribution authorization and persists BLOCKED completion in the same locked update before subsequent close stages.

### Shared consumers

15. `check_state/feature_record.py:inv_7`: attributed counts, legacy residual, missing-history notes and unchanged budget ceiling are one accounting invariant.
16. `check_state/run_state.py:_refusal_completion`: the original closed BLOCKED run and its exact hash-bound refusal proof jointly establish refused completion, never accepted-return status.
17. `check_state/board.py:_inv37_feature`: authoritative binding, local proof and the remedy diagnostic are evaluated for one feature before exposing actionable numbers.
18. `merge-gate.py:_enforce_receipt`: keeps the legal unbound sync-off case and the bound provenance/evidence refusal policy within one identified merge owner.
19. `board_lifecycle.py:_status_findings`: validates the receipt before projecting numbers and compares that projection with the feature's station; invalid bindings cannot become actionable mappings.

### Unit and fixture code

20. `CloseRunTest.test_validator_crash_or_noncontract_failure_cannot_become_refusal_evidence`: one table exercises three distinct subprocess failure classes against the same unchanged-ledger/station invariant.
21. `HistoricalRecoveryTest.test_refusal_preserves_malformed_bytes_and_authorization_is_hash_bound`: original malformed bytes, metadata preservation and tampered-authorization refusal are consecutive states of the same historical repair case.
22. `gh_sync_support.py:write_feature_json`: central fixture normalization preserves explicit overrides while supplying known provenance to pre-existing receipt fixtures.
23. `gh_sync_support.py:run`: one fake-only launch boundary guards both GH command routes and their environment overrides so fixture calls cannot escape to the network.

### Integration scenarios

24. `_check_parent_adoption`: verifies that evidenced parent adoption clears only its pending role, preserves the same generation/archive and creates only the remaining task.
25. `_invalid_replacement_operand`: generates distinct invalid authority, plan and path operands in one table helper; it performs no assertions and keeps mutation setup out of the refusal driver.
26. `fleet_unproven_command_cases`: all nine public command entry points must preserve both local files and the remote mutation log for the same unproven receipt.
27. `replacement_cases`: full and terminal modes have different required object sets and receipts; each verifies verbatim archival and completed replay without duplication.
28. `replacement_parent_uncertainty_case`: lost parent response, durable exact intent and no-discovery restart are successive states of one interruption scenario before explicit adoption.
29. `replacement_milestone_uncertainty_case`: a malformed successful-create response must retain uncertainty and prohibit both title lookup and another create on restart.
30. `replacement_undispatched_case`: proves that a known pre-dispatch failure clears only its intent, then resumes normally under the original generation without a second archive.
31. `replacement_confirmed_save_failure_cases`: OSError and controlled SystemExit after a confirmed remote create must both preserve named durable uncertainty and prohibit restart creation.
32. `_replacement_role_adoption_case`: runs the same lifecycle for milestone and task namespaces, independently checking role receipt, archive, generation completion and idempotent resume.
33. `case_historical_refusal_completion`: contrasts the original evidenced BLOCKED return with a later accepted return and verifies the original malformed bytes remain untouched.
34. `case_inv37_binding`: exercises valid and invalid authoritative factory targets alongside the legal unbound sync-off case against the same invariant.

## Remaining boundary

No full-matrix, pinned-review, live recovery or UAT pass is claimed. Existing feature-state blockers require separate authorized handling; source work, focused checks and isolated smoke results do not waive them.

## Subsequent authorized own-feature recovery

The operator separately selected **Authorize own-feature recovery**. The exact immutable
authorization is `notes/operator-own-feature-recovery-2026-10-18.json`; Kaya, installation,
merge and deployment remain excluded.

- GitHub reads verified that existing milestone 103 and parent 2154 belong to
  `mruangutai/harness` and name this feature.
- `record-refusal` attached typed provenance to the original closed BLOCKED run. Direct
  comparison confirmed that its raw bytes, verdict, timestamps and attribution, and the
  aggregate count, remain unchanged. The checker now recognizes refused completion.
- The first mirror preflight stopped before dispatch because it rejected the existing
  ledgered T-01 amendments. A valid-fixture regression failed for the intended reason,
  then passed after the preflight was aligned with DEC-229/INV-40. Unrelated amendments,
  unledgered text and missing original task signatures still refuse. The initial minimal
  test fixture was corrected after the normal plan reader rejected its missing required
  fields; that fixture error is not the intended red evidence.
- The next live recovery durably archived the original mapping once, then its milestone
  POST returned HTTP 422. It stopped without a confirmed number, discovery or retry.
  Recovery `ca38c84b-a1cf-44da-828b-9b4c1cc461b4` remains in-progress with pending role
  `milestone`. No new parent or milestone is confirmed.
- A [published first-hand GitHub probe](https://github.com/wso2/labs-agentic-engineer/issues/313)
  reports duplicate-title milestone rejection with HTTP 422. Our live output did not
  retain its field-specific JSON error, so that specific cause remains [INFERENCE].
  The same-repository integration fixture now models that collision and went red then green. New
  replacement attempts use a title containing their durable generation ID; ordinary
  opens retain their original title. The existing pending generation was NOT retried or
  cleared after the fix. It needs a separately authorized exact receipt.
- The final approved five-command chain passed after both fixes in **58.11 seconds**
  (session artifact 264), within the 60-second ceiling. The intermediate amendment-aware
  chain passed in 54.44 seconds (artifact 258).
- A final uncommitted, logical-path pre-pin risk assessment found zero high blockers and
  **35** grade-2 reason requirements: the original 34 above plus the following named reason.

35. `gh-sync.py:_replacement_plan`: approval status, complete original task signatures,
    canonical ledgered amendment recognition and the exact current plan hash are one
    recovery trust boundary. Original hashes remain immutable; task-set changes and
    unledgered text are not accepted. The separately verified authorization still binds
    the entire current plan file for this generation.

Runtime comparison confirmed that the archived previous mapping exactly equals the
captured original mapping, and that both the signed plan bytes and historical digest bytes
remain unchanged. A local review commit and the pinned full matrix remain blocked by the
pending milestone outcome. No pinned review or full-matrix pass is claimed.

### Exact-receipt resolution

The operator then selected **Adopt milestone #103**. The distinct authorization is
`notes/operator-milestone-103-adoption-2026-10-18.json`, binding the existing milestone,
the same generation and the unchanged plan hash. The real recovery command adopted 103,
created and durably recorded new parent **2160**, projected that parent to Building and
completed in 11.35 seconds (session artifact 268). No milestone create was retried.

Observed postconditions: the same recovery ID is complete, no pending intent remains,
the active mapping is proven `mruangutai/harness`, the receipt is `recovered-terminal`,
and the historical task issue map was not recreated. The archived original mapping,
signed plan bytes and original malformed digest bytes still match the captured originals.
This resolves the own-feature lifecycle blockers only; it does not activate T-03–T-05.
