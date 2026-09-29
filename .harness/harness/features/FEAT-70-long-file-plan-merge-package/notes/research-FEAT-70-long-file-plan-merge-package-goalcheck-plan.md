# FEAT-70 plan goal-check

## Conclusion

**does this plan deliver the operator's stated intent? PASS.** The two declared perspectives are fully carried by SC-01 through SC-03 and T-01 through T-02. The plan specifies the complete settled refactor, the one intended behavior correction, and immutable evidence that distinguishes behavior preservation from the crash fix. This is a planning-coverage judgment only: implementation, test results, receipt contents, and the immutable pin do not yet exist as proven outcomes. Approval is correctly still pending.

## Perspective grades

- **PASS — operator** — SC-02 and SC-03 are carried by T-01 and T-02: the unchanged hyphenated CLI, public behavior and byte identity, clean baseline/pin comparison, root-only normalization, committed receipts, and the atomic two-entry block-scalar repair all have explicit implementation and evidence work.
- **PASS — code maintainer** — SC-01 is carried by T-01 and T-02: the exact entry/package split, ownership, public `signed_task_hash`, package-aware tests and canonical identities, all-function grade-4 bar, twelve named repairs, moved-body identity, and new-glue grading are specified and pinned.

## Binding-intent trace

| Binding item | Plan carrier | Result |
|---|---|---|
| Baseline and immutable identity | `baseline.sha`; T-01 intent; T-02 dependency and intent | Uses full baseline `9e531b34fc04f752cedf51586dc13c460580901a`; T-01 lands first, then T-02 names that commit as the immutable pin and forbids amending it. |
| Thin unchanged entry and exact package | SC-01; T-01 intent and verify | Keeps `.claude/skills/harness/bin/plan-merge.py`, one CLI and one unchanged `VERBS` dispatch table, four registrars and `main`; creates `__init__.py` plus exactly the ten settled modules. The verify asserts the exact eleven-file set. |
| Exact ownership and public identity | D-01; T-01 intent | Assigns every verb family and shared primitive to the settled owner, puts the complete reset/resume family in `stations.py`, has `approval.py` call it for revoke, and keeps `signed_task_hash` callable from the entry. |
| Grade bar, counts, and identity proof | SC-01; T-01 intent/verify; T-02 intent | Grades every function across entry and package at 4 or better; names all four grade-2 and eight grade-3 functions; compares moved functions to the baseline pre-image; preserves grade identity for unchanged bodies; and separately grades genuinely new glue. |
| Exact decompositions | D-02; T-01 intent | Specifies `_task_status_line` as `_task_search`, `_status_in_task`, and coordinator with task-range, indentation, scan, tuple, ordering, duplicate-first, and refusal invariants. Specifies `_verify_spliced` as `_reload_spliced`, `_verify_schema_preserved`, `_expected_union_ids`, `_verify_union_ids`, and coordinator with signature, order, schema, mapping, refusal, replacement, and return invariants. |
| Source-level crash fix and red-first proof | SC-03; T-01 first paragraph and `_render_field` work; T-02 receipt work | Requires the regression to fail before production edits, fixes `_render_field` physical-line shape in `text.py` rather than special-casing the digest, and proves both amendments, reload identity, valid ledger, atomic refusal behavior, exit zero, and no traceback at the pin. |
| 107-case baseline/pin proof | SC-02; T-02 intent | Runs each checkout's own applicable suite, requires the same 107 pre-existing case identities, all executed, zero exit, and no `FAIL`; separately runs the new SC-03 case. It correctly does not run frozen monolith-only source/private assertions at the pin. |
| Public CLI identity ledger | SC-02; T-02 intent | Aligns every behavioral subprocess by stable case and invocation ordinal, retaining argv, context, status, stdout, stderr, plan before/after, hashes, concurrency order, refusals, and successes; missing, added, reordered, or unalignable calls are differences. |
| Scratch-plan baseline/pin proof | SC-02; T-02 intent | Discovers every tracked feature `plan.yaml` at the pin, explicitly excludes FEAT-70, preserves discovery/document order, and compares `check`, current `set-feature-station`, each current-or-default `set-task-station`, and eligible `amend --show`. `record-amendments` is correctly excluded here and proven by SC-03. |
| Normalization and divergence policy | SC-02; T-02 intent | Replaces only raw absolute checkout-root bytes with one shared token. It forbids all other normalization, filtering, sorting, rewriting, or accepted-difference rules and leaves overall red for any remaining difference absent an operator ruling. |
| Committed receipts and chronology | T-02 files, verify, and intent | Commits the three reusable receipt scripts and four named receipt/ledger files only after the implementation pin; records full SHAs, clean detached checkouts, timestamps, commands, raw/normalized hashes, one-execution provenance, grade/regression results, and exact divergences. The verify reads the receipt from its commit, proves pin ancestry and distinct chronology, checks the required 107/identity/overall lines, and reruns the grade assertion. |
| Shared tree-copy helper | SC-02; T-01 files and intent | T-01 owns `check_state_support.py` and extracts one `copy_executable_package(entry, package_name, dst_bin)` implementation. `copy_check_state` and thin `copy_plan_merge` delegates both use it; `PLAN_MERGE_BIN` selects the entry and its sibling package; caches are excluded and executable mode retained. |
| Mutation switches | T-01 intent | Keeps `UNION_MERGE`, `PRESERVE_BASE_BYTES`, and `APPROVAL_REFUSAL` in `union.py`, their real mutation owner, while preserving each proof's discriminating behavior. |
| Canonical-reader fixtures | SC-02; T-01 intent | Re-keys exactly 15 rows only in source-derived file/id identity, preserves every other enumerated field, and updates `scanned_files` to the unchanged entry, `__init__.py`, and all ten modules. |
| Free consolidations and literal moves | T-01 intent | Consolidates `TASK_ID_RE` and `ITEM_ID_RE` into one `text.py` regex; moves comments and banners byte-for-byte; forbids gratuitous renames, stale source assertions, source padding, and private entry re-exports. |
| Direct execution and reasons | `lanes`; T-01 and T-02 routing | All three surfaces and both tasks are `main-session-direct`. Each lane/task records its DEC-174 reason: canonical enforcement source, its owning tests/classification, and inseparable immutable-pin proof collection. T-02 depends on T-01. |
| Legal, bounded anchors | T-01 and T-02 `files` | Uses path/glob anchors only, with no line-number anchor. T-01's `.claude/skills/harness/bin/plan[-_]merge*` glob owns the entry and package while keeping the machine field line-bounded; its remaining exact paths own the integration test, shared copy helper, and classification fixture. T-02 owns only the FEAT-70 notes glob. There is no cross-task file overlap. |
| Approval and rework | `approval.status`; `needs_approval`; BRIEF constraint | Both artifacts remain pending and `needs_approval: true`. The brief recommends, but does not sign, exactly 2 rework rounds and 480 wall-clock minutes. |

Both planning decisions trace through executable work: D-01 is fully instantiated in T-01's ownership and revoke-call requirements; D-02 is fully instantiated in T-01's named helper contracts and behavior invariants. No settled item is orphaned.

## Panel accounting

- `PF-b81946176b41e9a34d3a6521dcb29a3c` is resolved by T-01's single shared `copy_executable_package` implementation and two thin delegates.
- `PF-5a2f0315a74baa10be3dbd92b88e82a4` is resolved by SC-02 plus T-01/T-02: each checkout runs its own structurally applicable 107 cases, while only public subprocess behavior and the fixed scratch script enter cross-version identity.
- `PF-9d58f7b7ff37672dcc6c0310fc9b135e` is reasonably dismissed because the binding operator instruction requires exact decompositions with no unresolved implementation decision; D-02 and T-01 supply them.
- `PF-30522a8c4477a03105e2cd58d669507f` is reasonably dismissed because the binding operator instruction explicitly requires the unsigned 2-round/480-minute recommendation; pending approval is unchanged.

## Open gaps

There is no uncovered intent or unresolved planning choice. The remaining gaps are deliberately post-approval execution facts: T-01 must demonstrate the red-first case and land the implementation; T-02 must select the immutable pin, run clean detached measurements, commit the scripts and receipts, and produce `overall: PASS`. None is inferred here. The user must approve or amend the pending brief and plan before execution.

## Handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: The pending two-task plan fully specifies every operator and code-maintainer outcome without claiming unbuilt evidence.
  feasibility: clear
  surface: L
  flags: [critical-writer, behavior-fix, package-refactor, immutable-receipts]
  recommend: proceed
  tasks: 2
  decisions: 2
  needs_approval: true
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: inspection, evidence: "plan.yaml D-01, D-02, T-01.intent/T-01.verify, and T-02.intent" }
    - { id: SC-02, verdict: met, method: inspection, evidence: "plan.yaml T-01.intent and T-02.intent/T-02.verify" }
    - { id: SC-03, verdict: met, method: inspection, evidence: "plan.yaml T-01 red-first intent and T-02 separate regression receipt intent" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/research-FEAT-70-long-file-plan-merge-package-goalcheck-plan.md
```
