# FEAT-2225 — code/architecture plan review, c1

**FAIL — the new distill merge executor must retain the existing mirror-provenance gate. The whole plan mission is proportionate; I oppose a mission downgrade.** Pending BRIEF/plan reviewed at the supplied assignment HEAD, not a production diff. No source edits or verification commands.

## Stage 1 — scope and compliance

- **high · substance · scope none · reader code-reviewer — T-04 omits existing receipt enforcement from merge-distill.** `plan.yaml:210-211` enumerates the new executor's checks but preserves mirror-receipt behavior only for ordinary merges. With valid replay/head/base evidence but absent, wrong-repository or recovery-required build-entry evidence, this new executor can invoke gh without the existing refusal. Current enforcement is `_enforce_receipt`/`_handle_owners` (`.claude/skills/harness/bin/merge-gate.py:248-301`); a Python subprocess's internal gh invocation does not generate another host Bash tool event. DEC-220 (`.harness/harness/docs/DECISIONS.md:7182-7198`) explicitly requires the same provenance/receipt predicate for every feature, including historical ones. **Amend T-04/D-03:** call the existing owner/binding/receipt decision on the exact candidate before merging, propagate denial as nonzero, and add a valid-distill/missing-or-invalid-mirror regression. This is a planned enforcement omission, not an observed implementation defect.
- All six SCs have task coverage; no orphan SC, nonexistent SC trace, unneeded task, overlapping file ownership or non-topological dependency found by text inspection. T-01 core, T-02 product truth, T-03 application guidance/grants and T-04 enforcement each serve live requirements. #2229 and the background queue remain excluded.
- SC-06 inspection **design** is present at `plan.yaml:136` and `:212`: pinned changed passages and byte-unchanged kept decisions are required separately from index generation. This is not completed pinned-content inspection before implementation exists.

## Stage 2 — architecture and verification design

- Depth/locality are appropriate: identity remains in the trusted extension closure; expertise-merge owns reconstruction, caps and receipts; merge-gate owns enforcement. The thin host adapter is justified by caller authority unavailable to the CLI, not a speculative second merge engine. D-03 correctly keeps the shared owner-root lock alive through synchronous merge, not just preflight.
- DEC-174 routes are explicit: T-03 covers ungranted authored skills/personas; T-04 covers host/schema/validators/guards and their tests. Existing Write/grants remain; governed shell/file-tool bypasses are closed, including dev-ops, and Main's currently skipped merge route is named (`harness-hooks.ts:1146-1150`).
- Terminal T-04 requires cumulative unit/integration floors and touched legacy gate suites after all tasks land (`plan.yaml:212`), so earlier results are not treated as final after successor changes. T-03's MANUAL dependency and SC-06 inspection prevent claiming an index-only or unbuilt-tool green. Removal of scribe recipes is paired with positive tool/contract assertions.
- Product `.harness/harness.json:28-33,93-95,135-207` supports cross_module → active unit/integration and docs → no floor; typecheck remains unresolved, honestly disclosed. The separately configured `handoff_comprehension` local probe (`:159-164`) should also be scheduled before ship for this changed handoff contract; no credentials/probe execution is claimed here.
- PM's 4-task/42-anchor/no-OVERLAP and 42 resolver successes are reported planning evidence, not rerun or independently claimed. File lists are textually disjoint; grants are not a substitute for DEC-174 authorization.

## Open questions

- **Q1 (nonblocking):** How does original-member re-judgment retire an earlier refused replay batch while preserving immutable historical receipts? T-01 (`plan.yaml:116,118`) replays original PR receipts and rejects changed-main replace/drop; merely appending a new runtime receipt leaves the older failing batch first. Recommendation: specify caller-authorized supersession/active replay selection inside the existing PR receipts and test refuse → original-member re-judge → successful replay, without adding digest state or a separate ledger. This is an unresolved recovery-interface question, not an additional classified finding.

## Principles applied

- **Delete First:** keep the existing ops/lock core and remove scribe guidance rather than introduce a second writer or queue.
- **Migrate Callers, Then Delete Legacy APIs:** the planned guidance/persona cutover replaces governed shell application while preserving the low-level CLI required for Main's mechanical replay.
