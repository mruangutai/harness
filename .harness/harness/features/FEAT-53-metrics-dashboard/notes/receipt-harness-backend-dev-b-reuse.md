## REUSE angle — FEAT-53 plan.yaml — receipt

**BLUF:** the plan mostly reuses correctly. Two genuine findings survive: T-06 leaves its
plan.yaml read unspecified, risking a bespoke YAML parse where `harness_yaml.load_plan`/
`load_file` already exists and is already hardened against the failure modes that broke three
prior hand-rolled parsers; and T-07 recomputes a count `code-grade.py --json` already returns
under a different name. Everything else checked in the dispatch — the grader invocation shape,
the verify-clause duplication risks, the trend-record denormalisation, and the fixture-project
builder — clears.

### Findings

**F1 — T-06's plan.yaml read has no named loader; the tree's only hardened one goes unmentioned**
- Location: T-06, `plan.yaml:250-302` (intent), file `.claude/skills/harness/bin/dashboard/kpi.py`
- Summary: T-06's intent says `compute()` reads `plan.yaml` for `approval.status`/`approval.date`
  but never names how. Every existing caller across the tree that needs `approval.*` out of a
  `plan.yaml` — `factory_decompose.py:351-352`, `gh-sync.py:987-989,1097-1099` — loads through
  `harness_yaml.load_plan(path)` (or `.load_file`) first, never a bare `yaml.safe_load`.
  `harness_yaml.py`'s own docstring (`harness_yaml.py:293-317`) exists precisely because a
  from-scratch parse failed on 35 of 36 real task blocks for reasons an author would not predict
  (backtick-led scalars, decorated `execution_mode` values, duplicate-key silence).
- Concrete cost: a second, from-scratch YAML read path in `kpi.py` is a second place the same
  five parsing landmines can resurface, and it is exactly the failure this file was written to
  retire once. If `harness_yaml.py`'s parsing rules tighten again (as they already have once),
  `kpi.py` does not inherit the fix and silently diverges on the next malformed `plan.yaml` it
  meets in whatever foreign project it is pointed at.
- Alternative: name `harness_yaml.load_plan(project_root / ".harness" / feat / "plan.yaml")`
  explicitly in T-06's intent (with a fallback path for `PlanSchemaError`/`YamlParseError` feeding
  the unavailability contract, since `load_plan` also validates `tasks:`, which a station-only or
  malformed plan may not carry — the intent should say to catch load-level errors and route them
  to the existing per-feature `unavailable` map rather than let `compute()` crash).
- `changes_task_set: no`
- `remedy_cost: amend` — a text change to T-06's `intent:` scalar only.

**F2 — T-07 recomputes `code-grade.py`'s own `passing` count under a new name**
- Location: T-07, `plan.yaml:315-345` (intent), file `.claude/skills/harness/bin/code-grade.py:154`
- Summary: `code-grade.py --json` already returns
  `{"records": [...], "passing": sum(r["grade"] >= r["bar"] for r in records), "ungraded": [...]}`
  (verified at `code-grade.py:152-159`, `code_grade.py:485-490` for the per-record `bar`/`grade`
  fields it is built from). T-07's intent derives `at_or_above_bar` from `records` itself rather
  than reading the subprocess's own `passing` field, which is the identical predicate over the
  identical records.
- Concrete cost: two independently-maintained spellings of "does this function's grade clear its
  bar" — `code-grade.py`'s `passing` and `kpi.py`'s `at_or_above_bar` — that must be kept in
  lockstep by hand. If the bar/pass rule in `code_grade.py` is ever refined (weighting, a new
  exemption class), `passing` picks it up and `at_or_above_bar` silently does not until someone
  remembers the second site.
- Alternative: T-07's intent should say to read `payload["passing"]` directly as
  `at_or_above_bar` (dividing by `len(payload["records"])` for the share), and reserve T-07's own
  iteration over `records` for what `code-grade.py` genuinely does not return: `bins`, `outliers`,
  and `file_mix` (confirmed distinct below).
- `changes_task_set: no`
- `remedy_cost: amend` — a text change to T-07's `intent:` scalar only.

### Cleared

- **T-06/feature.json read** — plain `json.load` over a per-feature `feature.json` is stdlib and
  trivial; no shared feature.json *reader* exists to reuse (`feature-json-merge.py` and
  `validate-feature-json.py` are write-side/schema-validation CLIs, not read helpers — checked
  both files directly). Not a duplication.
- **check-state.sh / feature-json-merge.py as the "existing reader" for T-06** — genuinely
  different from T-06's need. `check-state.sh` hardcodes governance checks over *this*
  repository's own `.harness/` tree (INV-22, INV-32, …); T-06 must resolve **everything** from an
  arbitrary `project_root` and "reads no value from this repository" (its own intent, verbatim).
  A tool built to police one fixed tree is not the reader a cross-project KPI compute needs.
  Clearing this half of item 1; only the `harness_yaml.load_plan` half survives as F1.
- **T-07's grader invocation shape** — verified against `code-grade.py:134-159`: root resolution
  is `_git_root(Path.cwd())` (`code-grade.py:15-20,144`), which matches T-07's explicit instruction
  to run the subprocess with `cwd=project_root` for exactly the reason T-07 states (the script
  would otherwise grade this repo). The `--json` shape (`{records, passing, ungraded}`) and every
  per-record key T-07 lists (`path, line, qualname, cyclomatic, cognitive, abc, grade, driver, bar,
  severity` plus `result`, `code_grade.py:485-490`) matches exactly, `cognitive_method` aside.
- **T-07's `bins`, `outliers`, `file_mix`** — none of these has a `code-grade.py` equivalent to
  duplicate. `code-grade.py` returns a flat, unbinned record list and never touches non-Python
  tracked files; `file_mix` is built from `git ls-files` at the project root, which is disjoint
  data (total tracked files by extension) from `code-grade.py`'s own `ungraded` (paths in the
  passed set that failed to parse). Confirmed by reading `_paths_report` (`code-grade.py:47-57`).
- **T-07's `outliers` using `record["grade"] in {1,2}` rather than `record["result"]`** — correct
  as written: `result`/`severity` are bar-relative (a grade-3 function can be `FAIL` against a
  grade-4 bar), while D-12's outlier definition is bar-independent by design. Using `grade`
  directly is the right field, not a missed reuse of `result`.
- **T-01/T-02/T-03/T-06/T-10/T-12 verify clauses** — each hand-rolled `python3 -c` assertion was
  checked against the nearest existing script and found to assert something that script does not:
  `check-domain.sh --resolve` (T-01) and `merge-gitignore.sh --check` (T-02) are used directly, no
  duplication. `run-unit-tests.sh --check-kinds` (T-03, T-06, T-10) only cross-checks the bash
  `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays against `harness.json`'s `test_kinds` set generally
  (`run-unit-tests.sh:38-145`) — it does not and cannot assert that two specific new literals are
  present, which is exactly and only what T-03's inline check adds. No overlap found across the
  17 tasks' verify clauses beyond what is already on the found-list (T-05's rglob issue).
- **D-18's trend-record fields vs. feature.json/plan.yaml** — checked every field. `shipped_at`,
  `grade{...}` and `attribution{...}` have no live equivalent anywhere and are trend-only by
  construction. `approved_on`, `cycles_used`, `max_total_cycles`, `runs`, `insertions`,
  `deletions`, `files_changed` duplicate values `kpi.py` can also read live from `feature.json`/
  `plan.yaml` for the *current* window — but D-10's stated rationale ("history is never
  recomputed or backfilled... would invent a past that was never measured") is the reason for the
  whole record, not just its unique fields: freezing these at ship time protects a historical
  point against a later `plan-merge.py amend` to the same feature's `plan.yaml` changing what a
  live re-read would show. That is a real snapshot rationale, not an unexamined copy — treating it
  as an unstated duplicate would be relitigating D-10 through its restatement in D-18. No finding.
- **T-06's fixture project** — grepped every `test-*.py` under `bin/` for a shared fixture-project
  or fake-`.harness`-tree builder; none exists. Every existing test (`test-gh-sync.py`,
  `test-check-state.py`, `test-factory-decompose.py`, …) hand-writes its own throwaway tmp
  directory per test case — a different pattern in kind from T-06's committed, static
  `dashboard/fixtures/project-a/`. Nothing to reuse; T-06 is not restating an existing helper.
