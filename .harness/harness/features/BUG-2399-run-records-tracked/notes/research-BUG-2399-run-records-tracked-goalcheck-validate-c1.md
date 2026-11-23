# BUG-2399 — goalcheck, validate c1

**PASS: both perspectives and SC-01..SC-04 are met; GC-F1/F2 are resolved by the settled advisor dispositions.** No new scope or decision amendment is required.

Reviewed base `59289ad1a9034113dd203ee12544cb93fb95bc3a` → **P = `ec95d8fb6167cfe199c4a30d4b20860d852c48f0`**, including c0 (`3835fde4`) → P. Source/document citations below mean `git show P:<path>`, not mutable main. Feature-relative paths resolve under `.harness/harness/features/BUG-2399-run-records-tracked/`. Conventional `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent at P; assigned self-hosted guidance was used. No tests, builds, linters or formatters were run by PM.

## Perspectives and traceability

| Perspective | Grade | Discharge |
|---|---|---|
| operator | met | SC-01 → T-01/T-02/T-03: ordinary staging without force-add. SC-02 → T-01/T-02/T-03: historical evidence review, preservation and separate commit before resuming. |
| code maintainer | met | SC-03 → T-01/T-03: intentional dirty-tree refusals preserve evidence. SC-04 → T-02/T-03: consistent tracking policy without weakening retention or gates. |

## Success criteria

Current automated evidence is QA's PASS DIGEST and `notes/review-harness-qa-c1.md:27-35`, backed by this run's `runs/r-20261122-4-validate-validator/qa/manifest-integration.json`: `tested_commit = P`, all 95 files complete, exit 0; the three carrying suites each return 0. These are current-run outputs bound to P, not claimed to be blobs already committed at P.

| SC | Verdict / method | Discriminating pinned evidence |
|---|---|---|
| SC-01 | met / automated | `tests/integration/test-merge-gitignore.py:149-153,185-213`: `bug2399_repository_rules_track_run_records` and `bug2399_fresh_install_tracks_run_records` ordinary-stage all eight named record kinds and exclude screenshots, traces and run-local locks. `.gitignore:12,56` and `gitignore.snippet:8-10` carry the exact narrow UI rule and lock exclusion. QA names both passing cases; pinned `notes/qa-red.json` records both pre-fix failures. |
| SC-02 | met / automated | Same suite: `bug2399_check_reports_obsolete_broad_rules` (:222), `bug2399_merge_replaces_broad_rules` (:238), rationale/line-ending cases (:262,:285), and `bug2399_operator_checklist_commands_compose` (:342; helpers :309-339). Assertions cover both obsolete spellings and their combination, read-only refusal, unrelated-byte preservation, rerun idempotence, legacy/namespaced evidence, spaces/metacharacters, exact staging, unchanged evidence and separate commit. All five named cases appear individually in the pinned red receipt and pass in current QA. `checkout-upgrade.md:38-84` pauses work, reviews evidence, uses explicit literal pathspecs without -A/-f, and requires its own commit before resuming. |
| SC-03 | met / automated | `tests/integration/test-merge-gate.py:722-747`, `case_bug2399_distill_records_commit_before_merge`: refusal while dirty, ordinary staging excluding UI, commit/push, then one merge at the updated exact head. `tests/integration/test-feature-worktree.py:1038-1075`, `case_remove_refuses_aborted_run_evidence`: canonical repository rules, running-state records, exit 4, WOULD DISCARD and byte-identical survival. QA confirms the three assertions in each suite pass at P; pinned red records two distill and three removal failures. Actual interrupted-run production remains explicitly advisor-accepted untested, not silently claimed. |
| SC-04 | met / inspection | Current code-reviewer `notes/review-harness-code-reviewer-c1.md:11` cites P's `DECISIONS.md:8536`, unchanged DEC-238 (:8046), `SPEC.md:252`, upgrade (:38) and distillation (:49). Independently inspected DEC-257 :8538-8568, SPEC :249-255/:1626-1627/:2313-2317, ignore rationale, merger HEADER :50-55, upgrade :38-84 and distillation :49-63: ordinary commit/push precedes merge-distill. `notes/research-BUG-2399-run-records-tracked-draft.md:12-29` records the consumer inventory and pre-narrowing main HEAD 9eb07b4f3cd235c234a10edddbfe5542c1e85fba, NUL-delimited inventory command, selected 0, exit 0. Feature-tree changes touch only BUG-2399, not historical Harness records. |

Evidence integrity: pinned red is byte-identical to its first commit `311a8702cac8b306d6481cbc4964f0620baad722`; SHA-256 `37c41ab7c51d57a70e85e4398d1da735d715989cc174e436d1a09309eb98c4ab` matches green's recorded red hash. All six red production hashes match base blobs. Pinned green executes `71a2ac7ffae2da79afa5b5adefc49b8a97bcc320`, **not P**: the removal test subsequently changes one fixture value to running. Current QA's P-bound receipt, not a false claim of identical test bytes, supplies that final green.

## Decision landing and preserved boundaries

Canonical Mode 2 / DEC-254 applies: `plan.yaml:58-77` has **three keep rows and zero amend/strike rows**, so no DEC-disposition sc_status rows are invented. T-03 owns DECISIONS.md (`plan.yaml:164-165`) if decision remediation were needed; none is needed. D-01 is landed by DEC-257 (`DECISIONS.md:8538-8568`): ordinary tracking, UI-only ephemerality, retained locks, migration and rejected force-add/missing-digest relaxation. Its index row (:240) is now 25 words; QA's current index-cap test passes.

Supplementary preservation inspection, not extra keep-row grades: entire DEC-112, DEC-174 and DEC-238 sections are byte-identical to base. DEC-238 :8046-8080 SHA-256 is `8a756ed94036ff96d453cd2fc090f9b2f3c4163fd31c46e927887c33dad9e19f`. Gate/invariant/pruning implementations are unchanged; feature-worktree changes only its comment (:341-344). SPEC §8.6 and INV-7/INV-36 are unchanged. The inventory names merge-gate `_require_checkout`, removal `_gate_removal`, validate-digest, gh-sync, worktree-state, worktree_terminal and factory_workspace; no bypass was added.

## Settled c0 dispositions at P

- **GC-F1 closed, T-01:** fixture `test-feature-worktree.py:1051` now uses documented `running` (`team-run-state.md:34`). Existing task already owns that test; no task-field ownership amendment was needed. The pinned build note's Fix c1 section records the advisor's accepted producer gap. Removal :294-305 reads Git dirt, not status; no interruption-producer requirement is reinvented.
- **GC-F2 closed by amendment:** P's `plan.yaml:140` assigns the removal comment to T-02; :174-181 assigns all four prose corrections to T-03. `feature.json:78-89` explicitly ledgers both amendments and the delegated advisor reason. Actual diffs only replace stale tracking instructions; BRIEF/D-01 are not weakened. This is recorded authorization repair, not a claim the original ownership was correct.
- **Other settled disposals:** PYTHONUSERBASE remains an accepted environment adjustment, not proof of a wholly verbatim historical invocation. QA-Q1 is fulfilled by current QA's recorded pinned `bun install --frozen-lockfile`; PR CI was not substituted. Current reviewer confirms all three high-grade failures closed and retains the three accepted grade-2 reasons (removal lifecycle, same distill candidate, three migration combinations); these remain advisory, not erased. The old flake's cause remains unproven. Fresh-clone prerequisites still invoke the merger; a fresh clone has only tracked checkout content, not a previous checkout's ignored historical files, so this does not bypass the existing-checkout checklist.

## Principles applied

- **Experience First:** grade migration by reviewed ordinary staging and a separate commit, not merely merger success.
- **Outcome-Oriented Execution:** distinguish preserved pre-fix red, historical green and actual current-pin QA evidence at the final migration boundary.

## Open questions

None. This goalcheck grants no ship authorization and performs no implementation or replanning.
