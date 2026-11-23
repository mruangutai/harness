# BUG-2399 — goalcheck, validate c0

**PASS: SC-01..04 are met by the preserved integration evidence and pinned inspection.** The two perspectives pass. File-ownership and fixture-description deviations below are nonblocking record issues, not authority to change signed scope. This is not the subsequent QA gate verdict.

Review: `59289ad1a9034113dd203ee12544cb93fb95bc3a` → `3835fde4f16d1b34d8711fc8607b5153545bfaec` (P). All content citations below are at P, obtained with `git show P:path`; feature-relative citations resolve under `.harness/harness/features/BUG-2399-run-records-tracked/`. No tests, builds, linters or formatters were run. The three conventional product documents are absent at P; the assigned self-hosted SPEC and decision record were consulted instead.

## Perspectives and traceability

| Perspective | Verdict | Discharge |
|---|---|---|
| operator | pass | SC-01/T-01,T-02,T-03 proves normal staging; SC-02/T-01,T-02,T-03 proves migration, preservation and separate operator commit before resume. |
| code maintainer | pass | SC-03/T-01,T-03 proves both intended dirty-tree refusals; SC-04/T-02,T-03 supplies one tracking decision without changing retention or invariant semantics. |

## Success criteria

| SC | Verdict / method | Specific evidence |
|---|---|---|
| SC-01 | met / automated | `tests/integration/test-merge-gitignore.py:149-153,185-215`, cases `bug2399_repository_rules_track_run_records` and `bug2399_fresh_install_tracks_run_records`: all eight named record kinds are staged through ordinary add; screenshots, traces and a run-local lock are excluded. `notes/qa-red.json:14-17` captures their pre-fix failures; `notes/qa-green.json:7-10` captures both passing. |
| SC-02 | met / automated | Same suite: `case_bug2399_check_reports_obsolete_broad_rules` (:222), `case_bug2399_merge_replaces_broad_rules` (:238), rationale/line-ending cases (:262,:285), and `case_bug2399_operator_checklist_commands_compose` (:305). Both shipped spellings and their combination are exercised; command composition covers legacy and namespaced evidence, spaces and glob metacharacters, exact staged population, unchanged evidence, no implicit commit and a separate commit. Red/green receipts above show these cases failing/passing. Pinned `checkout-upgrade.md:38-84` requires review and commit before resume. |
| SC-03 | met / automated | `tests/integration/test-merge-gate.py:722-748`, `case_bug2399_distill_records_commit_before_merge`, uses canonical repository rules and proves refusal before committing/pushing, then one merge at the updated head. `tests/integration/test-feature-worktree.py:1038-1075`, `case_remove_refuses_aborted_run_evidence`, proves exit 4, WOULD DISCARD and byte-identical surviving records. `notes/qa-red.json:20-29` records the two distill and three removal failures; `notes/qa-green.json:13-22` records their passing counterparts. See interrupted-run qualification below. |
| SC-04 | met / inspection | `.harness/harness/docs/DECISIONS.md:8536-8568` adds DEC-257 citing DEC-238 and records D-01, rejected alternatives, exact narrow rule, locks and dirty-tree consequences. `SPEC.md:249-255,1626-1627,2313-2317`, `.gitignore:8-12`, `gitignore.snippet:1-11`, merger HEADER (:50-55), `checkout-upgrade.md:38-84` and `distillation.md:49-63` agree; distill commit/push explicitly precedes merge-distill. `notes/research-BUG-2399-run-records-tracked-draft.md:12-29` contains the consumer inventory and pre-narrowing owner-main receipt: HEAD 9eb07b4f3cd235c234a10edddbfe5542c1e85fba, command, selected 0, exit 0, including non-UI locks in its population. Only this feature's paths changed under the feature tree: no historical run backfill. |

Evidence binding: the original red receipt is byte-identical to its first commit, `311a8702`; its six production hashes match base blobs. Its SHA-256 is `37c41ab7c51d57a70e85e4398d1da735d715989cc174e436d1a09309eb98c4ab`, matching green's recorded red hash. Green names executed HEAD `9c8559bb0eb731018e56e304e91745e1596e4ad6`, not P. All three test files, both ignore inputs, merger and lifecycle scripts are byte-identical between that HEAD and P; the later distillation/validate-template documentation changes were inspected at P. This transfers the recorded behavioral evidence; it does not claim a fresh execution at P or a current QA digest.

## Decisions and unchanged semantics

| Plan row | Disposition assessment at P |
|---|---|
| D-01 | met: DEC-257, `DECISIONS.md:8538-8568`, lands ordinary tracking and rejection of force-add/missing-evidence relaxation. |
| DEC-112 / keep | pass, preserved: entry bytes equal base; idempotence and read-only check clause at :1830-1834 remains. Named migration/check/idempotence regressions carry the behavior. |
| DEC-174 / keep | pass, preserved: entry bytes equal base; direct-execution ruling at :4482-4485 remains. Plan tasks retain main-session-direct routing; build receipt reports direct execution. This inspection does not independently attest the historical host session. |
| DEC-238 / keep | pass, preserved: entire entry :8046-8080 is byte-identical to base, including station retention, pruning and pin disposal. No amend/strike row exists, so there is no amendment-landing outcome to invent. |

`check_state/feature_record.py`, `check_state/run_state.py`, `check_state/table.py`, `feature_schema.py`, merge-gate and pruning implementations have no changes in this range. Removal changes only its explanatory comment, not predicates. SPEC §8.6's whitelist is unchanged. INV-7/INV-36 and retention were not weakened.

## Five build deviations — disposition, kind and owner

1. **PYTHONUSERBASE — acceptable verification-environment adjustment (T-01/T-03).** `notes/build-T-01-T-03.md:9` reports preserving user-site dependency discovery while HOME isolates Git configuration. The scripts clear inherited GIT variables and set explicit global/system Git configuration isolation; this adjustment does not relax assertions. Red contains actual feature assertion failures, not import failures. The receipts do not independently record the exported value; do not represent them as proof of the exact invocation environment or claim the enclosing invocation was wholly verbatim.
2. **Interrupted rather than literal ABORTED state — behavioral acceptance unchanged (T-01).** Removal's GATE 2 (`feature-worktree.py:294-305`) reads Git dirt, not run status; canonical rules expose the unclosed, uncommitted records and the assertions prove their preservation. **Form finding GC-F1:** the fixture's `status: in_progress` (:1052) is not the documented seed, `status: running` (`references/team-run-state.md:34-37`), and `run-state-schema.json:15` accepts any string. Thus the build's assertion that no ABORTED status exists is not a schema prohibition, and the fixture is not evidence of actual interruption/close-run behavior. This does not defeat SC-03's dirty-record outcome.
3. **Four extra policy-document corrections — serve SC-04/D-01, no behavioral expansion (T-03).** `.claude/skills/harness/teams/validate.yaml:40`, `.omp/agents/harness-qa.md:67`, `.omp/agents/harness-validator-lead.md:85-86` and `.harness/README.md:33-34` only replace stale force-add/ephemerality prose. **Form finding GC-F2:** none is in a signed task file list; the deviation ledger explains but does not grant ownership. Record/resolve that task-boundary departure explicitly; this goalcheck neither rewrites the plan nor grants approval.
4. **Removal comment correction — same nonbehavioral ownership departure (T-02; GC-F2).** `feature-worktree.py:341-344` corrects the obsolete broad-ignore explanation; that production file is absent from T-02's file list. No gate logic changed and pruning remains untouched.
5. **Panel re-transcription — acceptable record repair.** The pinned plan adds the goalcheck reader, changes reader reasons to none and preserves both finding identities/dispositions. Task intents, file lists, verify commands, decisions and approval are unchanged. No goal or decision amendment is hidden here.

The pre-existing `case_landed_differs` failure remains reported at `notes/build-T-01-T-03.md:18-19`; its case is unchanged in the pinned diff. The preserved green receipt has no FAIL lines. The receipt does not establish the claimed flake's root cause; no rerun was performed to confirm or dismiss it. QA alone performs the required subsequent gate checks.

## Principles applied

- **Outcome-Oriented Execution:** grade final tracking and lifecycle outcomes with preserved red/green boundaries, without demanding compatibility paths for the old broad-ignore policy.
- **Experience First:** judge the upgrade by explicit operator review and separate ordinary commit, not merger convenience; distinguish record defects from demonstrated evidence loss.

## Open questions

None blocking goal delivery. GC-F1 belongs to T-01; GC-F2 belongs to T-03 (four documentation paths) and T-02 (removal comment). Both are form/record findings, not unmet SCs or authorization to enlarge signed scope. Current validation QA evidence remains the validator's separate gate.
