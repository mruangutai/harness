# Review — harness-code-reviewer — BUG-201-depends-on-integrity — c1

## BLUF
**FAIL.** Stage 1 (spec compliance) is clean — every REQ/SC traces to code, no scope creep, no
omission. Stage 2 surfaces one gating defect: the new production function this feature exists to
add, `_validate_plan_depends_on` (`harness_yaml.py:391`), is **grade 3**, below the grade-4
production bar (`code-grade.py`, `CYCLOMATIC: 10 / COGNITIVE: 14 / ABC: 17.4`, driver
`cyclomatic+cognitive`, `RESULT: FAIL`, `SEVERITY: high`). No fail-open behavior was found anywhere
in the new code or the three consumer sites — I constructed and ran adversarial inputs against all
of it and every one was rejected (fail-closed), never silently accepted.

## Stage 1 — spec compliance

| REQ/SC | Verdict | Evidence |
|---|---|---|
| REQ-01 (reject dangling ref) | met | `harness_yaml.py:391-425` `_validate_plan_depends_on`, called `harness_yaml.py:343` inside `validate_plan_doc` |
| REQ-02 (name both ids) | met | `harness_yaml.py:424` `f"{tid} to {entry}"` pairs joined into one message |
| REQ-03 (write route blind spot closed) | met | `plan-merge.py:470` `_schema_error` calls `harness_yaml.validate_plan_doc`, used by `_verify_spliced` (`:506-513`, `:1635-1639`) which gates `cmd_apply`/`amend`; `test-plan-merge.py` `bug201a`/`bug201b` pass live (exit 5 / exit 0, sha256 unchanged) |
| REQ-04 (correct plans unchanged) | met | live-corpus case ran clean, 68/68 files, 0 dangling, 0 regressions; the six consumer suites (`test-check-plan-routes.py`, `test-check-state.py`, `test-factory-decompose.py`, `test-gh-sync.py`, `test-harness-yaml.py`, `test-plan-merge.py`) all exit 0 at the pin (re-ran all live) |
| REQ-05 (3 swallow sites surface cause) | met | `factory_claim.py:178` `bad_plan` blocker + `:215-222` render; `gh-sync.py:1174` `_projected_for` refuses via `refuse(..., stream=sys.stderr)`; `gh-sync.py:~1288-1290` `_status_plan_doc` prints to stderr, returns `None`, no new gate (confirmed by `test-gh-sync.py` cases d–g, all passing, all live-run) |
| SC-01..SC-03, SC-05..SC-09 | met | ran every named test file live at the pin — all exit 0 (`test-plan-depends-on.py` 12/12, `test-factory-claim.py` 133/133, `test-factory-decompose.py` 162/162, `test-plan-merge.py`/`test-gh-sync.py`/`test-check-plan-routes.py` all PASS) |
| SC-04 (single implementation) | met — ran the grep myself | `_validate_plan_depends_on`: exactly one `def` (`harness_yaml.py:391`) and one call site (`:343`), both in `harness_yaml.py`; zero matches anywhere else in the tree outside plan/notes prose; `plan-merge.py`/`check-plan-routes.py` carry no second comparison of `depends_on` against task ids (only `check-plan-routes.py:350`'s unrelated byte-budget field list) |

No scope creep: `factory_claim.py`'s `bad_plan` branch fires for *any* existing-but-unparseable
plan.yaml, not only a dangling `depends_on` — wider than REQ-05's literal example but exactly what
D-05/T-06's own intent text specifies ("the plan.yaml file EXISTS but `load_plan` raised"), not an
unapproved widening.

## Stage 2 — code quality

**[must_fix, high] `harness_yaml.py:391` `_validate_plan_depends_on` is grade 3, below the
grade-4 production bar.** `code-grade.py --base $(git merge-base origin/main <sha>) --head <sha>`:
`CYCLOMATIC: 10, COGNITIVE: 14 (Sonar), ABC: 17.4, GRADE: 3, DRIVER: cyclomatic+cognitive,
RESULT: FAIL`. This is the one function this whole feature exists to add. `code_grade: fail`.
The shape/collect/raise structure inside one function (two nested loops, an inline shape-check
with its own raise, and a build-up-then-raise for the batched message) is what drives cognitive
past the grade-4 ceiling; splitting the non-list shape check or the pair-collection loop into a
named helper is a plausible fix, but that decision is the implementer's, not mine to make.

**[low, non-blocking] Three grade-2 records in the same `code-grade.py` run, none blocking:**
- `tests/integration/test-plan-merge.py:2104` `case_bug201_apply_refuses_dangling_depends_on`
  (new, `ABC: 31.7`, driver `abc`) — a linear integration-test body (build fixture, subprocess,
  hash, assert × 4); cyclomatic/cognitive are low (2/3), so the ABC number is call-count from
  test plumbing, not branching logic. Reasoned acceptable.
- `tests/unit/test-factory-claim.py:324` `build_features_root` (modified, `ABC: 39.5`, driver
  `abc`) — worsened because T-03/T-06 required adding four `task_dict(...)` calls
  (`test-factory-claim.py:370-373`) so this file's own pre-existing fixture plans (which named a
  blocker id absent from their own task list, e.g. `T-10 depends_on [T-99]` with no `T-99` task)
  stay legal under the new referential-integrity check — necessary, in-scope repair, not
  speculative padding. Reasoned acceptable.
- `tests/unit/test-factory-claim.py:432` `run_main` (`ABC: 26.7`, driver `abc`) — I diffed this
  function's body against `af859ee8` byte-for-byte (`diff` on the two ranges): **identical**. It
  only shifted 29 lines down because of insertions earlier in the file. This looks like a
  base/head function-matching artifact in `code-grade.py` (line-based pre-image lookup losing
  the match across a line-number shift) rather than a real regression introduced by this diff —
  worth a harness `open_question`, not a finding against BUG-201.

**Fail-open hunt — hypotheses probed and FALSIFIED, none survived:**
- (a) `_validate_plan_depends_on` reachability without `_validate_plan_tasks` first: only one
  call site exists (`harness_yaml.py:343`, immediately after `:342`) — unreachable any other way.
- (a) hostile shapes fed directly to `validate_plan_doc`, live: `tasks` absent/`None`/non-list,
  a non-mapping task, `depends_on` as a dict, a nested list `[["T-01"]]`, `[None]`, a
  whitespace-padded id `" T-01"`, a float `1.0` vs int id `1`, and `bool True` vs int id `1` —
  **every one raised `PlanSchemaError`**, none loaded clean.
- (b) generic (non-`depends_on`) YAML corruption on an existing file: constructed a
  `tasks: [this is: not: valid...` fixture and drove it through `_blocker_gate` live — correctly
  resolves `bad_plan` with the parser's own message, never regresses to `no_plan`'s generic text.
  (Message can span multiple lines for this class of error since PyYAML's own parser error
  embeds newlines; SC-08's specific `T-02`/`T-99` message has none, and that is the only case the
  brief requires to be checked — info only.)
- (b) cache bleed across (repo, feature) keys: covered by the shipped BUG-1290 suite (`5b`/`5g`),
  re-ran live, passing.
- (c) `refuse(stream=...)` changing an existing caller: grepped every `refuse(` call site — only
  the new `_projected_for` call passes `stream=`; all five pre-existing callers are unchanged,
  and `test-gh-sync.py`'s new `refuse()` cases (ran live) confirm stdout/exit behavior for the
  no-`stream` path is byte-identical to before.

## Verdict rationale
`must_fix` is non-empty (the grade-3 production function) and `severity_max = high` →
`VERDICT: FAIL` per the gating rule. Spec compliance is otherwise clean; the fix is scoped to one
function's internal shape and does not touch the spec.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Spec compliant end to end; _validate_plan_depends_on is grade 3, below the grade-4 production bar — gates the build"
  severity_max: high
  findings: 4
  must_fix:
    - "harness_yaml.py:391 _validate_plan_depends_on is grade 3 (cyclomatic 10 / cognitive 14 / ABC 17.4), below the grade-4 production bar — code-grade.py RESULT: FAIL, SEVERITY: high"
  spec_violations: []
  code_grade: fail
  reviewed: "af859ee8..6896ebe7c02df49df7b9d8c5f6e7a92a37dcd5e4"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "code-grade.py flagged tests/unit/test-factory-claim.py:432 run_main (ABC 26.7, grade 2) as a base/head-changed record, but its body is byte-identical to af859ee8 — only its line offset shifted from earlier insertions in the file. Is this a known function-matching gap in code-grade.py's pre-image lookup (line-based rather than qualname/body-based), and should it be tracked as a harness defect?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/notes/review-harness-code-reviewer-c1.md
```
