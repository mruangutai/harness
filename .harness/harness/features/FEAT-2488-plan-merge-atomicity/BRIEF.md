# BRIEF — FEAT-2488 plan_merge two-file amendment atomicity

## Problem

DEC-229 promises that a signed-field amendment lands in `plan.yaml` and its `amendment` judgement lands in `feature.json` all-or-nothing, but `plan_merge`'s `write_plan_and_ledger` only compensates in-process. A process killed between the two renames leaves an amended plan with no judgement, so check-state reports an unledgered edit nobody explained. An exception after the ledger rename restores only the plan, so the ledger records an amendment the plan does not carry — the direction the plan-first ordering was built to prevent. A failed restore tells the operator to recover from git. The ledger is the operator's whole basis for trusting builder amendments, and today it can silently disagree with the signed text. Source: issue #2488 (omp audit finding 14). The audit's "largest simplification" framing is not the goal: this feature is a correctness fix and is about LOC-neutral, possibly net-positive.

## Done when — by perspective

**operator** — When an amendment to signed task text is interrupted — killed, out of disk, or refused by a ledger it cannot lock — the next write leaves the plan and the ledger agreeing: both carry the amendment or neither does. A state the tools cannot reconcile is refused loudly, never overwritten. `amend`'s output and every other locked write I run behave as before.

**code maintainer** — I find the one cross-file write mechanism in the shared locked core, with its lock order and its durability stated truthfully, and no plan_merge module carrying its own rename or restore code.

**reader (qa / reviewer)** — I can grade the all-or-nothing claim against tests that construct each torn state on disk, and the old ledger-failure tests still stand in migrated form, so coverage did not shrink to make the change pass.

## Success criteria

- SC-01 (operator): With each torn state constructed on disk beside its intent journal — amended plan with the old ledger, old plan with the new ledger, and both landed with the journal still present — the next plan-merge invocation on that plan (re-running the same record-amendments or amend) or the next feature.json write leaves both files carrying the amendment exactly once and no journal; a further invocation changes neither file. A journal with a member matching neither its recorded before- nor after-state refuses at exit 5 naming the journal and changes no file. A ledger write that fails after the journal is published is reported as journaled for completion by the next write, never as "nothing was written"; a feedback failure after both files are written does not turn the write into a failure. QA demonstrates each torn state persisting, the divergent journal not refusing, and both failure reports differing, at 2491336e43310cb3e95ae3110d098726ed4dc454 before the fix.
  verify: automated evidence: integration
- SC-02 (code maintainer): At git show <review_sha>, no file under .claude/skills/harness/bin/plan_merge/ contains mkstemp or os.replace; guards.py defines neither _replace_bytes nor _restore_plan; the plan-plus-ledger write is one call to a harness_merge primitive that takes both locks, writes and removes the journal, and recovers it; no plan_merge module opens, writes or deletes the journal itself.
  verify: inspection
- SC-03 (code maintainer): The journal reaches disk before any member is replaced: at git show <review_sha>:.claude/skills/harness/bin/harness_merge.py, the reviewer cites locked_pair_update fsyncing the journal file's descriptor, renaming it into place and fsyncing its directory before the first member replacement, and unlinking the journal only after the last; ordinary locked_update writes perform no fsync.
  verify: inspection
- SC-04 (operator): `amend`'s stdout is unchanged: exact-line assertions for a ledgered signed-field amend (AMENDED with judgement=amendment, APPLIED plan, APPLIED feature.json) and an unledgered amend (AMENDED, APPLIED plan), with no APPROVAL-RESET line, pass at 2491336e43310cb3e95ae3110d098726ed4dc454 and at the review pin. This is a regression lock: QA records the base run as the baseline instead of a failing first run.
  verify: automated evidence: integration
- SC-05 (reader): At git show <review_sha>:tests/integration/test-plan-merge.py, each of the three base ledger-failure cases (case_1985_amend_restores_the_plan_when_the_ledger_fails, case_b1716_record_amendments_is_all_or_nothing, case_b1716_record_amendments_restores_the_plan_on_a_ledger_io_error) has a successor, under its own or a new name, that forces the same failure and asserts a nonzero exit naming it, both files byte-identical and no journal left. Across the successors there are at least the 8 check() calls the three cases carried at 2491336e43310cb3e95ae3110d098726ed4dc454.
  verify: inspection
- SC-06 (code maintainer): At git show <review_sha>, feature_json_write.py's module docstring no longer claims that harness_merge.locked_update performs an fsync. harness_merge.py documents the journal protocol and the lock order — plan.yaml.lock before feature.json.lock, never reversed. amend.py carries no APPROVAL_RESET_LINE import and no reset bookkeeping. plan-merge.py's exit-code contract names the refused-journal case under exit 5.
  verify: inspection
- SC-07 (operator): With no journal present, every other harness_merge write behaves as before: test-harness-merge.py, test-feature-json-merge.py, test-observations-merge.py, test-expertise-merge.py, test-inflight-registry.py, test-check-state-feat59.py and test-plan-merge.py's pre-existing cases (other than the three SC-05 migrates) pass at the review pin without edits to their assertions.
  verify: automated evidence: integration

## Verification gaps

- No SC rests on a null or excluded kind: unit and integration are active. functional and eval are excluded under DEC-187; component and ui are unresolved but this feature has no browser or component surface.
- Not proven by any test: durability across an OS crash or power loss, and the fsync ordering itself — SC-03 grades the ordering by reading the code (the grilling allowed a cited code anchor); no test cuts power. A live SIGKILL between the renames is not exercised either; per the grilling ruling, SC-01 constructs each torn state on disk instead, and no production code carries an injection hook. Readers that bypass the lock (snapshot isolation) are a non-goal and untested.
- No SC requires user-run UAT.

## Constraints

- DEC-229 SUPPLIES the acceptance text ("all-or-nothing across both files (BUG-1716)") and BLOCKS any change to compare-and-splice on `was`, field-only re-rendering, approval-byte preservation, the judgement shape and `signed_task_hashes`.
- DEC-199 SUPPLIES the home — `harness_merge`, with `fcntl.flock` on an `O_CREAT|O_RDWR` sibling lock file, never `O_EXCL`. It BLOCKS any consumer-local lock or rename primitive, and its plan.yaml row ("spliced as text, never re-rendered") BLOCKS a YAML round-trip.
- DEC-174 BLOCKS team execution: `validate-digest.py` and `dispatch-guard.py` import `harness_merge`, and `check_state/ctx.py` loads `plan-merge.py`. Every task is main-session-direct: red tests first, tests run explicitly, a human reads the diff.
- DEC-171 SUPPLIES `safe_load` reading and grants no licence to re-render on write.
- Plan-first ordering is kept: `write_plan_and_ledger`'s docstring records that ledger-first was tried and reversed. Recovery lives in the core, never in a consumer, and re-runs are idempotent.
- Lock order: `plan.yaml.lock`, then `feature.json.lock`, documented in `harness_merge.py`. No path acquires them reversed.
- No production injection hooks: tests construct torn states on disk.
- Left alone: `stations._task_search` and `text._item_range_within` are not consolidated (their termination semantics differ). The `PRESERVE_BASE_BYTES` and `UNION_MERGE` branches stay. `check-plan-routes.py` and `test-check-plan-routes.py` are not edited. INV-40 and the rest of check-state are not edited. No DEC is amended.
- No LOC-reduction target. The journal, its recovery and its tests are new code, so expect roughly LOC-neutral to net-positive.
- The product is the assigned Harness feature worktree. AGENTS.md maps specification and decisions to `.harness/harness/docs/SPEC.md` and `DECISIONS.md`. `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` do not exist; the module contracts in `harness_merge.py`, `feature_json_write.py` and `plan-merge.py` supply the architecture guidance.

## Out of scope

- **A YAML round-trip rewrite of plan_merge.** DEC-199 and DEC-229 mandate byte-preserving splicing, and the amend CAS hashes field bytes.
- **Any LOC-reduction target or "broader plan_merge simplification".** Only 5 lines are proven dead; the audit's larger removal estimate is not established.
- **Transactionality for `sign-approval`'s preliminary rework, hash and BRIEF writes.** The code accepts them explicitly, and DEC-229 scopes all-or-nothing to the amendment pair. Moving the BRIEF write's rename onto the core primitive is not transactionality.
- **Snapshot isolation for readers that bypass the lock.** DEC-199's model is cooperative locking, and each rename stays atomic.
- **The check-plan-routes.py split.** Deferred to E2 (issue #2489) with its own grill.
- **Retiring the legacy PLAN.md parser.** It belongs to DEC-182's migration window.

## Approval

status: pending
approved-by:
date:
