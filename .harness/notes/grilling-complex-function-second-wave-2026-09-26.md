# Grilling — complex function, second wave: approval_guard, check-omp-port.check, parse_digest — 2026-09-26

## Destination
`check-domain.approval_guard` (176 lines, cyc 44 / cog 139 / abc 105.1),
`check-omp-port.check` (116 lines, 42 / 72 / 112.6) and `validate-digest.parse_digest`
(134 lines, 30 / 73 / 75.4) each become a small driver over per-rule (or per-phase) functions,
and every function the refactor leaves behind grades at bar 4 or better on `code-grade.py`
(grade 2 excepted, as the grader excepts it). Every owning suite's output is byte-identical to
the baseline except enumerated, ruled divergences; the grader's existing ratchet is the lock,
so no new check is added. Nothing else in the three files changes.

## Mission
mission: patch
reason: cause known (one body carrying every rule for its input), diff bounded (three
functions in three named files plus their suites), no new public interface, schema or
enforcement surface — the grade ratchet already in code_grade holds the result. Same
three-part test FEAT-66 passed; FEAT-66 shipped at 00c7219e with c0 FAIL / c1 PASS.
confirmed-by: operator (picked (a): "next three evaluators", 2026-09-26)

## Settled (carried from FEAT-66's tree, `grilling-complex-function-three-drivers-2026-09-26.md`)
- Family → complex function. After FEAT-66 the tree holds 28 grade-1 functions (census at
  00c7219e, `code_grade.grade_source` over `.claude/skills/harness/bin`): 10 rule evaluators,
  9 CLI dispatchers, and 9 lighter ones. This wave takes the three heaviest evaluators.
- Target → **(a)**: the surviving drivers reach bar 4 too.
- Mission → patch; three separate pins declined again.
- Proof → byte identity across every owning suite at a clean detached checkout of the pin
  under `.claude/worktrees/harness/`; divergences ledgered old/new/ruling; red-first receipts
  committed after the pin. **SC-02 fail-first is the baseline-vs-pin comparison** (FEAT-66
  ruling, `answers-validate-validator.md`); SC-01's lock is the plan's inline grade assertion,
  never a permanent test file (FEAT-66 MF-03).
- Execution → all three files are enforcement (DEC-174): `execution_mode: main-session-direct`,
  no dev dispatch, worktree under `.claude/worktrees/harness/`. `change_type: cross_module`.
- Shape → pm fixes it per function from the branch inventory; the three differ:
  - `approval_guard` — a per-entry loop (`for glob, frag, raw in entries`) whose body forks on
    `_tool == "Write"` / `"Edit"`: one driver, a parsed context read once, one rule function
    per tool form plus the shared pre-checks (guard off, NotebookEdit, missing target, frag).
  - `check` — five sequential blocks (AGENTS.md, agent files, expected names, provider
    prefixes, extension doors) each appending to `errors`: an ordered table of check functions
    over `root`, output order preserved.
  - `parse_digest` — a line scanner, not a rule set: shape is **phases / value forms** (find
    DIGEST, base indent, then per line: flow scalar, block list, nested key), the
    `apply_merge` precedent, not the rule-table one. Its cursor (`i`, `cur`, `item_indent`)
    must not become a mutable bag that re-creates the load — the "not yet specified" item from
    FEAT-66 that pm resolved for `MergeResult` applies.
- Comments → load-bearing; every comment moves byte-for-byte with the rule it explains; new
  facts carry the feature id.
- Evidence volume is where FEAT-66 tripped (six c0 items, all evidence/plan-conformance):
  raw path lines normalised up front (D-09), ledger entries in built form, no second lock.

## Out of scope
- The 9 CLI dispatchers (argparse fan-out; different shape) and the 7 remaining evaluators
  (`md_to_html`, `process_plan_yaml`, `classify`, `check-skill-refs.scan`,
  `layout_migration.scan`, `_audit_findings`, `domain_check`) — third wave.
- `validate-digest.hook_mode` (18/24) — sits beside `parse_digest` but is a dispatcher.
- Any behaviour change in the three files; any new lock, verb or schema. #1928 stays parked.

## Facts I verified
- Positions at 00c7219e: `approval_guard` check-domain.py:536–711 (`domain_check` at 794 is
  out of scope); `check` check-omp-port.py:99–214; `parse_digest` validate-digest.py:724–857.
- Owning suites: tests/integration/test-check-domain*.py (8 files) + `check_domain_support.py`
  and `test-bash-write-guard.py` (import check-domain); `test-check-omp-port.py`;
  `test-validate-digest.py`; `tests/unit/test-code-grade.py` (the bar-4 lock — it caught a
  grade-2/3 port during the post-merge rebase, so it holds).
- Estimate given: ~1.5 days plan→ship, as FEAT-66.
