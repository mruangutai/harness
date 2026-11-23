# BUG-2399 code review c1

**PASS — compliance holds; all three c0 high grade failures close. Three accepted grade-2 test scenarios remain advisory.**

Reviewed `59289ad1..ec95d8fb6167cfe199c4a30d4b20860d852c48f0`, including the complete commit list and c0→c1 changes. Actual source reads used `git show` at this pin. Live feature.json agrees with the dispatch pin; its pinned historical copy still names c0. No `[harness:human]` commits; checkout dirt was confined to feature metadata/run records.

## Stage 1 — spec compliance: PASS

SC-01: repository and fresh-snippet tests exercise real ordinary staging of records and exclusion of UI/locks (`tests/integration/test-merge-gitignore.py:185`). SC-02: both historical spellings, read-only refusal, byte-idempotence and literal-path operator commit are covered (`:222`, `:238`, `:342`). SC-03: same-candidate distill refusal/commit/merge (`tests/integration/test-merge-gate.py:722`) and removal refusal with preserved evidence (`tests/integration/test-feature-worktree.py:1038`) retain existing gate predicates. The interrupted fixture now seeds canonical `running`; producer coverage is not claimed.

**SC-04 inspection:** pinned DEC-257 (`.harness/harness/docs/DECISIONS.md:8536`), unchanged DEC-238 (`:8046`), SPEC commit policy (`.harness/harness/docs/SPEC.md:252`), operator checklist (`.claude/skills/harness/references/checkout-upgrade.md:38`), distill commit/push before merge (`.claude/skills/harness/references/distillation.md:49`), and research note “Dirty-tree inventory” agree. Decision changes only append DEC-257; no retention/gate weakening or historical Harness backfill appears. The DEC-257 index ruling is shortened. GC-F2 path amendments serve SC-04/D-01; they do not redefine acceptance. The build receipt's old `in_progress` explanation is superseded by its explicit c1 correction, not treated as current fixture evidence.

## Stage 2 — quality: PASS with advisory grades

Executed control-plane `code-grade.py --base 59289ad1 --head ec95d8fb6167cfe199c4a30d4b20860d852c48f0`. Also executed the canonical merge-base range (`9eb07b4f3cd235c234a10edddbfe5542c1e85fba..ec95d8fb6167cfe199c4a30d4b20860d852c48f0`), exit 0, identical records; relevant bin/integration base trees compare equal. No tests/builds/lint/formatters ran; QA owns final matrix execution and dependency provisioning.

C0 closure: `_without_obsolete` is grade 4 (CC/cognitive/ABC 5/4/13.7); `_merge` no longer emits a gated record; checklist composition is grade 3 (2/0/20.1). Extracted predicates and operator phases preserve behavior without introducing another migrator. Static inspection established no additional concrete fail-open/silent-failure defect.

All findings below are **substance / med / owner T-01**, measured maintainability costs rather than observed runtime failures:

| Function | Location | CC / cognitive / ABC | Grade / driver |
|---|---|---|---|
| `case_remove_refuses_aborted_run_evidence` | `tests/integration/test-feature-worktree.py:1038` | 12 / 5 / 40.4 | 2 / CC+ABC |
| `case_bug2399_distill_records_commit_before_merge` | `tests/integration/test-merge-gate.py:722` | 7 / 3 / 35.6 | 2 / ABC |
| `case_bug2399_merge_replaces_broad_rules` | `tests/integration/test-merge-gitignore.py:238` | 7 / 4 / 30.2 | 2 / ABC |

Reasons remain accepted at this pin: removal keeps landed setup, refusal and byte preservation in one lifecycle scenario; distill must observe the same candidate before and after commit/push; migration applies one contract to all three shipped-rule combinations. Editing these scenarios requires retaining more observations in working memory, but splitting those cohesive scenarios further would obscure the contracts. No must-fix.

## Principles applied

- Delete First: retained the existing merger seam; inspected the helper split for reader-load reduction rather than accepting grade improvement alone.
- Migrate Callers, Then Delete Legacy APIs: checked both obsolete spellings and upgrade/distillation callers together; no compatibility API remains.

## Open questions

None.
