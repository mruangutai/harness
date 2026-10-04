# Grilling — complex function, the three heaviest rule evaluators — 2026-09-26

## Destination
`check-domain.shape_problems` (691 lines, cyc 135 / cog 356 / abc 320.6),
`validate-digest.validate` (416 lines, 134 / 286 / 274.3) and `plan-merge.apply_merge`
(244 lines, 59 / 136 / 162.9) each become a small driver over per-rule functions, and every
function the refactor leaves behind — driver and extracted rules alike — grades at bar 4 or
better on `code-grade.py` (grade 2 excepted, as the grader excepts it). Every owning suite's
output is byte-identical to the baseline except enumerated, ruled divergences; the grader's
existing ratchet is the lock, so no new check is added. Nothing else in the three files changes.

## Mission
mission: patch
reason: cause known (one body carrying every rule for its record kind), diff bounded (three
functions in three named files plus their suites), no new public interface, schema or
enforcement surface — the grade ratchet already in code_grade holds the result.
confirmed-by: operator

## Settled
- Family → complex function, chosen from `.harness/notes/smell-measurements-2026-09-25.md`
  (31 grade-1 functions; 82 below bar tolerated by the ratchet; primitive obsession is the other
  candidate and is addressed through #1928 for the digest record, not tree-wide).
- Scope → the three heaviest first, as one feature; the remaining 16 grade-1 rule evaluators
  follow as a mechanical second wave copying the pattern once it has survived review.
- Target → **(a)**: the three surviving drivers reach bar 4 too, not merely leave grade 1.
  Every extracted helper is a new function with no pre-image and is gated at bar 4 by the
  grader regardless; the driver is the part the ratchet would otherwise tolerate at grade 1.
- Mission → patch, by the three-part test; `plan` was offered for three separate review pins
  and declined.
- Proof (precedent, waves 1–4) → byte identity across every owning suite at a clean checkout
  of the implementation pin under `.claude/worktrees/`; divergences ledgered old/new/ruling;
  red-first receipts committed after the pin.
- Execution (precedent, DEC-174) → all three files are enforcement; `execution_mode:
  main-session-direct`, no dev dispatch, worktree under `.claude/worktrees/harness/`.
- Shape (precedent, wave 2 / `check-state.py`) → an ordered table of rule records the driver
  iterates; a parsed context read once and passed to each rule; rule order preserved so output
  order is byte-identical. `shape_problems` keys rules by file-kind regex (eight kinds today);
  `validate` by the common block then persona; `apply_merge` by its merge phases. pm fixes the
  record shape per file; a shared record type across the three is not required.
- Comments → load-bearing; every comment moves byte-for-byte with the rule it explains.

## Not yet specified
- Whether `validate`'s context is one object or the persona-specific tuples the branches already
  build — pm decides from the branch inventory.
- How `apply_merge`'s `MergeResult` accumulators (added, preserved, ignored, changes, reset) are
  threaded through phase functions without a mutable bag that re-creates the cognitive load.

## Out of scope
- The 12 grade-1 CLI dispatchers (`main`/`_main`/`cmd_*` in gh-sync, factory_*, board-station,
  feature-record, feature-worktree, upgrade-config, wayfind) — argparse fan-out, a different
  shape; not forced into the rule-table pattern.
- The other 16 grade-1 rule evaluators (`approval_guard`, `hook_mode`, `parse_digest`,
  `check-omp-port.check`, `md_to_html`, …) — second wave.
- Any behaviour change in the three files; any new lock, verb or schema.
- #1928 (digest wire format) — separate; this work makes `validate` cheaper to change for it.

## Facts I verified (so pm does not re-derive them)
- Grades and line counts above: `code_grade.grade_source` over bin/ at 4e4e50bd
  (`.harness/notes/smell-measurements-2026-09-25.md`).
- `code_grade._gate_file_records`: a function with no pre-image is gated; one with a pre-image is
  gated only when its grade drops. Bar 4 for production paths, 3 for test paths; grade 2 never
  blocks (`_blocks`).
- `shape_problems` (check-domain.py:1283–1973) is eight `if RE_<kind>.match(rel): … return out`
  blocks: RUN_DIGEST 1322, RUN_IDENTITY 1342, PLAN_YAML 1352, FEATURE_JSON 1413, STATE_YAML
  1545 (350 lines), HANDOFF 1896, CLAUDE_MD 1920, STATE_MD 1960.
- `validate` (validate-digest.py:1653–2069): 39 `err.append` sites; common VERDICT/DIGEST/
  artifact/schema checks then `if persona == "qa"`, `"lead"`, `"orchestrator"` branches.
- `apply_merge` (plan-merge.py:970–1213): phases at 975 (base bytes), 1019 (union), 1032,
  1050/1057 (key order), 1173 (preserve base bytes), 1192 (UNION_KEYS), 1205, 1210 (approval).
- Owning suites: tests/integration/test-check-domain*.py (8 files), test-config-shape-matrix.py,
  test-plan-merge.py, test-validate-digest.py, test-validate-digest-shadows.py.
- Duplicated bodies across bin/: 2 pairs only (one the DEC-234 locked twin); wave 1 held.
