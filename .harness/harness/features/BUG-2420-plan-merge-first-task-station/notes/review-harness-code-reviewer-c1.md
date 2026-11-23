# PASS — byte-oracle closure; no new findings

Reviewed `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd`; c1 judgement is restricted to the delta from accepted c0 `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`, as delegated. Dispatch and feature.json agree. Initial git status was clean; full range commit census contains no `[harness:human]` commits or foreign-feature commits.

## Stage 1 — specification: PASS

Independent git diff census: **21 paths** — one unit test, seven feature notes, eleven feature run/receipt files, feature.json and plan.yaml. Production `stations.py` and the integration test are unchanged from c0. BRIEF is unchanged; plan's only delta is top-level station `building` → `review`, not a criterion, decision, task or approval amendment. Feature records document this feature's validation/rework; no scope creep found. Consulted assigned product SPEC §2 and DEC-120/174/225; signature authority and main-session-direct execution remain unchanged.

All U citations are `tests/unit/test-plan-merge-first-station.py` at the exact pin, read with git show:
- **SC-01 inspection:** U:93–117 retains exactly three rows and four checks per row. Insertion's complete expected value splices `  status: building\n` immediately after the unique T-01 id; rewrite replaces the unique T-02 `  status: ready\n`; refusal expects the complete original PLAN (U:49–58,95–101). Exit, outcome needles and APPLIED checks remain. No adjacent or production contract change.
- **SC-01 byte proof:** fixture writes encoded bytes (U:80); U:84–87 reads bytes and strictly decodes UTF-8 without newline conversion; U:110–113 compares the entire actual result to the complete expected value. Strict UTF-8 decoding is injective for these valid fixture bytes, so this text equality proves their byte equality; invalid UTF-8 fails rather than normalizing silently.
- **SC-02:** U:49–50,148–156 preserves the complete approval block, including approved status, and requires rc=0 in both the success check and approval predicate. A failed unchanged insertion cannot satisfy it. Reads no longer normalize newlines.
- **SC-03:** unchanged integration coverage inherits c0 assessment; no fresh execution claim.

## Stage 2 — quality: PASS

**Closed: c0 F1, med / substance / T-01**, not a new finding. The membership helper is deleted. Whole-file equality now rejects swapped title lines, duplicates, omissions and CRLF insertion: each changes the actual sequence relative to the fixed expected sequence. Each row executes the real cmd_set_task_station through the existing writer/lock seam (U:61–71,109), then reads the resulting file; expected values never call production or derive from actual output. A no-op fails both successful rows. No vacuous comparison or fake transform found.

Static risk assessment, not a grader execution: prior `notes/green-T-01.md:719` records production grades 4, test grades 3–5. Production is unchanged. Changed test bodies retain control-flow shape, replacing reads and reducing repeated comparison calls; removed changed_lines had comprehensions, while new plan_bytes is branchless. No below-bar or grade-2 shape identified. `code_grade: pass` is a static assessment; QA owns fresh pinned mechanical evidence.

## Principles applied

- **Delete First:** replacement removes the lossy membership helper instead of layering another oracle beside it; complete expected values remain beside the three existing rows.

## Limits and open questions

No tests, mutants, builds, lint, formatters or grader commands executed. Rework receipt red/M8/green output was inspected, not independently reproduced. QA owns fail-first, mutation and final pinned verification. No new findings, must-fix, spec violations or open questions. Only this report was written.
