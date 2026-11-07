# FEAT-71 · validate-validator · product goal-check c0

**PASS: both declared perspectives are delivered; SC-01–SC-05 are met. No unmet product criterion or finding.**

Review: `4a05030d401593003209f525fd06e00802eccd36..3e6add2af05f5b801afec1ef69440fe54e1529a4` (pin). Source/spec assertions below use `git show pin:path`, `git diff base pin`, or the committed tree, never HEAD/working-tree source. `P` = assigned PRODUCT; `F` = `P/.harness/harness/features/FEAT-71-corpus-independence`; evidence paths below are under `F/notes/` unless specified. T-01 alone traces all five SCs; no decisions are added.

## Perspective coverage

| Declared perspective | Grade | Discharging criteria and result |
|---|---|---|
| operator | pass | SC-01, SC-05; exact committed five-folder corpus, authorized record pruning, and existing standalone merge evidence rather than linked-worktree green. |
| code maintainer | pass | SC-02, SC-03, SC-04; synthetic/non-vacuous fixtures replace historical dependencies, accessor reproduction survives, and deleted-folder documentation/probe consumers are repaired. |

## sc_status

| ID | Verdict / method | Evidence and independent assessment |
|---|---|---|
| SC-01 | met / inspection | `git ls-tree -d pin:.harness/harness/features` returns exactly FEAT-71-corpus-independence, BUG-2161-abandon-source-tickets, BUG-2141-dec174-main-orchestrator, FEAT-2037-product-document-guidance, BUG-20261006-fleet-planning-recovery. The four pre-existing survivors have no diff. Fifth-survivor authority: pinned `answers-2026-11-07-02-product.md` and `feature.json judgements`. |
| SC-02 | met / automated | Pinned `tests/unit/test-feature-schema-build-entry.py` uniformly probes missing-agent/receipt/recovery behavior, pairing absence of per-id tables with concrete rule outcomes; `tests/unit/test-plan-depends-on.py` requires 3/3 synthetic plans plus exactly one planted dangling-plan failure. `red-first-S1a.md` records named baseline failures (33 runs-agent, 75 build-entry exemptions); `red-first-S1b.md` records synthetic-prefix handoff refusals failing before removal and 146 baseline-config paths. Final pin receipt `merge-3e6add2af05f5b801afec1ef69440fe54e1529a4.log:1075-1105,1863-1879,3534-3570` shows the relevant unit and handoff suites green. Both project/template configs contain no baseline key; template needed no edit because baseline already lacked it. |
| SC-03 | met / automated | Pinned `tests/integration/test-corpus-real-owner.py:136-155` asserts synthetic exact names/record-less discovery and rejects an empty walk; its fixture linked-caller leg is mandatory. `test-corpus-non-regression.py#ConversionManifest` really converts fixtures and executes both consistency/live checks, with active-feature, moved-head and layout mutants; no absent-manifest skip remains. Existing-flow tests use a present/removed synthetic directory. `red-first-S2.md` R1/R2 names exemption/default-plan/deleted-folder/floor failures; G and Grade fix record green corpus-free audit/self-tests. Final pin log `2293-2311,3822-3838,4531` confirms existing-flow, seven conversion cases, eight owner cases and ordinary route tests green. Historical manifest tests previously skipped: that is recorded as missing exercise, not falsely called a failing assertion. |
| SC-04 | met / inspection | Pinned deletion diff removes both retired probes and config kinds; `suite_layout.py` registry is empty. `tests/manual/probe-session-accessors.ts` and baseline FEAT-44 extension have identical Git blob `e8df5c44b0ef8e3172e5c3055d6b0b6a2b26291d`. `tests/manual/probe-omp-session-accessor.py` docstring retains reproduction, measured main/subagent result and version-floor limitation; `PROBE` points beside it. DEC-204 loses only the obsolete merge-gate sentence. FEAT-23 source pointer is dropped, operative angles retained, and both skill examples use placeholders. `red-first-s4.md` documents the layout/kind failures and post-deletion green. No fresh credentialled accessor result is claimed. |
| SC-05 | met / inspection | Committed deletion list removes 41 old logs and 107 old project notes; pinned record-deletion receipt binds authorized edited/untracked deletions to paths, sizes and hashes (those local bytes cannot be proved by Git). Scoped diff shows no kaya, survivor, BUILD, docs/, README or expertise edits. SPEC changes only the example path; DECISIONS changes are bounded pointer/probe/removal-truth updates below. DECISIONS-INDEX is regenerated, with its consistency test green in the standalone receipt and no final index-diff output. |

## Independence, not just green

Existing post-pin builder receipt `merge-3e6add2af05f5b801afec1ef69440fe54e1529a4.log` names `/private/tmp/feat71-standalone.DUn29lHx` and exact pin at lines 1–2, scans five features at 79/100, reports zero failed decision anchors at 80, zero route violations at 99, and completes 141 files at 8136. Independently inspected that retained clone's Git identity: top-level is the named `/private/tmp` path, git-dir is `.git`, HEAD is exactly the review pin, and its pinned tree has the same five names. Thus the evidence is not a linked caller borrowing the old owner corpus. The ledgered hook/main-ref setup models the post-merge clone; it does not restore historical folders.

The final log is external execution evidence, not committed source (it cannot exist inside the commit it measures). All script headers report exit 0. Its four literal FAIL lines are the explicitly announced factory-claim mutation proof (`1051-1060`), not ignored suite failures; the unresolved-root ERROR is also a negative-control case. The optional *real-host* linked-caller announcement (`3831-3832`) does not skip synthetic non-vacuity. Canonical-reader special-mode green comes from S2's retained self-test receipt, not an invented claim that argvless full-suite execution runs that mode. Earlier failed merge receipts and S2's code-grade failure/fix remain recorded. No tests, builds, linters or formatters were run by this persona; QA retains final matrix ownership.

## Scope judgments

- Removing five historical grandfather mechanisms necessarily makes their rules uniform, including kaya identities; there is no kaya tree edit or survivor replacement allowlist. No concrete current kaya violation is established by this diff.
- The 28 classification plan pointers, including survivor BUG-20261006's, are intentionally removed. Pinned `_classification_task_files` reads only explicit row plans; `_ownership_finding` still checks opted-in ownership and `_route_finding` still enforces DEC-174. Synthetic omitted-source/unreadable-plan refusals and no-corpus audit distinguish decoupling from disabling the reader audit.
- Removing the test-only `--conversion-manifest` path accompanies replacement of the retired historical manifest with always-executed fixture conversion; no surviving source/test/product-guidance caller uses it.
- DEC-159/215 baseline text, DEC-220 era text, DEC-213 registry status and DEC-250 standing-probe evidence are direct truth updates forced by approved removals, not unrelated changes to handoff grammar, recovery authority, layout policy or runtime lineage. DEC-204 lifecycle semantics remain intact. These are not scope findings.

Findings (kind/task/severity): none. Open questions: none. No replan, source/fixture/config edits, or commits.
