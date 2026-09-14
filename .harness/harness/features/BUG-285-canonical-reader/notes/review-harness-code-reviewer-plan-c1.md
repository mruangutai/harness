# Plan scope review — BUG-285-canonical-reader — c1

## BLUF

FAIL. The refreshed plan has the right deep-module architecture and now covers the PR #1688 Python enforcement surface, but two execution details still violate SC-05/DEC-174: team tasks edit an enforcement test, and the direct hook task does not execute the check-domain tests it changes. The plan also retains three earlier findings as open even though its refreshed task text appears intended to resolve them.

## Findings

1. **HIGH — substance — scope: task — reader: code-reviewer.** T-03 and T-04 both list `tests/integration/test-check-plan-routes.py` while both tasks execute through `harness-backend-dev`. That file is the test of the DEC-174 enforcement program `check-plan-routes.py`; DEC-174 explicitly includes “the test file of each” (`.harness/harness/docs/DECISIONS.md:4408-4411`), and SC-05 requires every changed enforcement test to be main-session-direct (`BRIEF.md:23-24`). **Consequence:** the team lane can change the enforcement test independently of its main-session-owned gate, bypassing the category-based ownership and proof seam that SC-05 requires. Remove this test from T-03/T-04 and place any required classification assertions in the corresponding main-session-direct task, or make those test edits a separately sequenced direct predecessor. **Pointers:** T-03, T-04; SC-05; DEC-174.

2. **HIGH — substance — scope: task — reader: code-reviewer.** T-06 lists nine changed `test-check-domain*.py` files, but its verify block runs none of them. The generic enforcement-byte comparison cannot establish that newly edited assertions execute; T-06 itself says the new strictness assertions must fail before implementation and that “all named tests” pass. **Consequence:** a broken check-domain payload/manifest migration or a test edit that is never exercised can satisfy the written T-06 verify command and advance to T-07, where the mechanical relocation assumes the semantic cutover is sound. Add every changed check-domain test file to T-06's verify block (or name one existing aggregate runner that demonstrably executes them all). **Pointers:** T-06; SC-03, SC-05.

3. **MED — form — scope: task — reader: code-reviewer.** `panel.findings` still marks PF-3e768f2abaa9b27fff332e097207c807, PF-4825fbdef33073221eb35fbee6a29203, PF-de964b2a856a70856e7547f6ff28a879, and PF-d6bb3cab806a2e81acbf1244f2de1b28 as `open`, although the refreshed T-01/T-02/T-03/T-07 text appears to address their subjects. **Consequence:** the approval record continues to advertise unresolved high/med scope defects, so a signer cannot distinguish intentionally outstanding work from findings already discharged by the refresh. Reconcile each disposition and `resolved_by` field; leave any genuinely unresolved item open. **Pointers:** plan `panel.findings`; T-01, T-02, T-03, T-07; SC-01, SC-02, SC-04, SC-05.

## Cleared questions

- T-08 has real remaining work: the live DEC-174 enumeration names `check-domain.py`, `bash-write-guard.py`, `validate-digest.py`, `check-state.py`, `check-plan-routes.py`, and `dispatch-guard.py`, but not `branch-create-gate.py` (`DECISIONS.md:4408-4411`). Its Python filename and narrow enumeration-only edit are current after PR #1688; no stale shell/#1674 narrative remains in T-08.
- The current plan does not preserve the issue body's obsolete shell exclusion: BRIEF scope and T-01/T-05/T-06 explicitly include the Python files converted by PR #1688. `source_issues: [285, 1594]` and pending approval are preserved.
- Issue #1682 is correctly folded into SC-03/SC-07 as accessor plus observable consumer behavior rather than added to `source_issues`.
- Dependencies are topological. T-01 inventories first; T-02 creates the accessor seam; semantic dispatchable/direct cutovers precede their respective relocation tasks; T-08 follows the code work.
- Architecture is sound: `artifact_accessors.py` is a deep module whose small artifact-named interface centralizes strict parsing, typed failures, and validation; `harness_yaml.py` remains the low-level adapter; callers cross one accessor seam; and dependency-light imports preserve hook locality. The deletion test is satisfied because removing the module would redistribute parser choice and error normalization across the live callers.
- No stale planned file or named source symbol found among the task projections reviewed. T-01's live AST/classification agreement is appropriately the authority when projections drift; module-internal registries, writer transforms, schemas, migration corpus, and already-supplied validation payloads have bounded exemption classes rather than silent exclusions.

## Inspection criterion

SC-06 is specified but cannot yet be discharged in plan phase. D-04 plus distinct semantic tasks (T-03/T-05/T-06) and relocation tasks (T-04/T-07) provide the required review seams; execution must preserve separate diffs and findings.
