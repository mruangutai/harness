# Review — harness-code-reviewer — BUG-201-depends-on-integrity — c2

## BLUF
**PASS. MF-1 is CLOSED.** The extraction at `626bb599` (delta: `harness_yaml.py` only, +37/-17)
is behaviour-preserving on every hostile input tested and introduces no fail-open path. Stage 1
verdict from c1 stands unchanged (this delta touches zero spec-facing behaviour). SC-04 re-grepped
clean at the new pin.

## (a) Is MF-1 closed?
`code-grade.py --base $(git merge-base origin/main 626bb599) --head 626bb599`, the three records
in `harness_yaml.py`:

| function | line | CYC | COG | ABC | GRADE | DRIVER | RESULT |
|---|---|---|---|---|---|---|---|
| `_validate_plan_depends_on` | 427 | 4 | 1 | 7.3 | **5** | cyclomatic+cognitive+abc | PASS |
| `_depends_on_entries` (new) | 391 | 4 | 4 | 6.8 | **4** | cognitive | PASS |
| `_dangling_edges` (new) | 411 | 4 | 6 | 6.9 | **4** | cognitive | PASS |

All three clear the grade-4 production bar; c1's blocking record (grade 3: cyc 10/cog 14/ABC 17.4,
`RESULT: FAIL`, `SEVERITY: high`) is gone. Neither new helper landed at grade 3 or below — the
complexity was **removed** (cognitive 14 → 1/4/6, no single function above 6), not moved into an
under-graded shadow. **MF-1: closed.**

## (b) Is the extraction behaviour-preserving?
Ran, not read: imported the new module (`626bb599`) and the pre-refactor module
(`git show 6896ebe7:harness_yaml.py`, written to `/tmp/bug201_c2_review/`, never touching HEAD) and
called `validate_plan_doc` live against 10 hostile fixtures on both. Script:
`/tmp/bug201_c2_review/compare.py`.

| input | old type:msg | new type:msg | same? |
|---|---|---|---|
| absent id (`T-01→T-99`) | `PlanSchemaError`: "…T-01 to T-99" | identical | ✅ |
| two dangling edges (`T-01→T-88`, `T-02→T-99`) | `PlanSchemaError`: "…T-01 to T-88, T-02 to T-99" | identical | ✅ |
| `depends_on: "T-01"` (bare string) | `PlanSchemaError`: "…must be a list…got 'T-01'" | identical | ✅ |
| `depends_on: {x: 1}` (dict) | `PlanSchemaError`: "…got {'x': 1}" | identical | ✅ |
| `depends_on: [None]` | `PlanSchemaError`: "…T-01 to None" | identical | ✅ |
| `depends_on: [["T-01"]]` | `PlanSchemaError`: "…T-01 to ['T-01']" | identical | ✅ |
| int id `1`, dep `["1"]` | OK (accepted) | identical | ✅ |
| str id `"1"`, dep `[1]` | OK (accepted) | identical | ✅ |
| `depends_on` absent | OK | identical | ✅ |
| `depends_on: []` | OK | identical | ✅ |

10/10 exception type AND message byte-identical. **No divergence — must_fix empty on this axis.**

## (c) Did the extraction open a fail-open path?
Probed via `/tmp/bug201_c2_review/failopen_probe.py` and an AST walk
(`/tmp/bug201_c2_review/failopen_probe2.py`), not inspection alone:

- **H1 laziness** — `_depends_on_entries` returns the real `list` object (`t.get("depends_on")`),
  never a generator/iterator; `isinstance(result, list)` true, no `__next__`. **Killed.**
- **H2 outer-loop early exit** — 3-task fixture, dangling edges on task 1 (first) AND task 3
  (last), valid task 2 between them: `_dangling_edges` returned **both** `('T-01','T-88')` and
  `('T-03','T-99')`. An early return/break after the first match would have dropped the second.
  **Killed.**
- **H4 inner-loop short-circuit** — one task, `depends_on: [T-77, T-78, T-01]` (two dangling
  entries in the same list): both `('T-01','T-77')` and `('T-01','T-78')` captured, not just the
  first. **Killed.**
- **H5 exception swallowing** — `ast.walk` over all three function bodies: zero `ast.Try` nodes in
  any of `_depends_on_entries`, `_dangling_edges`, `_validate_plan_depends_on` (grep substring
  match on "except" false-positived on the word "exception" in a docstring — corrected with AST).
  **Killed.**
- **H3 return-without-full-scan** — `ast.walk` shows `_dangling_edges` has exactly one `Return`
  (the final `return dangling`, line 424), no `Break`/`Continue`; `_depends_on_entries` has two
  returns, both terminal value-producing exits (empty-coerce, or the raise-guarded list), neither
  mid-loop; `_validate_plan_depends_on` has zero explicit `Return` nodes (falls through after the
  conditional raise). No code path returns before every task/entry pair is visited. **Killed.**

No fail-open path opened by this extraction.

## SC-04 — re-grepped myself, whole worktree
`_validate_plan_depends_on` (`grep -rn` from worktree root): exactly one `def`
(`harness_yaml.py:427`) and exactly one call site (`harness_yaml.py:343`, inside
`validate_plan_doc`). Every other match in the tree is prose: `BRIEF.md:89-94` (spec text),
`plan.yaml:166,432` (decision/intent text), and mentions inside this feature's own
`notes/`/`observations/` (receipts, prior review notes, goal-check research) — none executable,
none a second implementation. **SC-04 holds at the new pin.**

## Suites re-run live at the new pin
`tests/unit/test-plan-depends-on.py` → 12/12, exit 0. `tests/unit/test-harness-yaml-corpus.py` →
16/16, exit 0. Both directly exercise the changed function; the remaining 7 suites named in the
orchestrator's contract were not re-run by me (delta is confined to one file already covered by
these two, and c1 ran all 9 live at the prior pin with no other file changed since).

## Stage 2 — the three grade-2 records in this range
Same three test-code records c1 already reasoned acceptable (`test-plan-merge.py:2104`
`case_bug201_apply_refuses_dangling_depends_on`, `test-factory-claim.py:324`
`build_features_root`, `test-factory-claim.py:432` `run_main`) — confirmed unchanged: the
`6896ebe7..626bb599` diff touches only `harness_yaml.py`, so none of these three functions moved
or changed. c1's reasoning (ABC-driven test-plumbing/fixture-count, not branching complexity)
still applies verbatim. Not re-litigated as new findings; `code_grade: grade_2` reflects their
continued presence, not a regression.

## Stage 1 — unchanged
This delta is an internal, behaviour-preserving refactor of one already-approved function; it adds
no new spec-facing behaviour and removes none. c1's Stage 1 verdict (clean, every REQ/SC traced,
no scope creep, no omission) stands unmodified.

```yaml
VERDICT: PASS
DIGEST:
  headline: "MF-1 closed — _validate_plan_depends_on now grade 5, both new helpers grade 4; extraction proven behaviour-preserving on 10/10 hostile inputs, no fail-open path found"
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "6896ebe7c02df49df7b9d8c5f6e7a92a37dcd5e4..626bb59934b8801bf1abdc86379aa313e021c77b"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/notes/review-harness-code-reviewer-c2.md
```
