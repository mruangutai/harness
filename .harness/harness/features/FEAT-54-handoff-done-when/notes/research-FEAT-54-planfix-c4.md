# Research — FEAT-54 planfix-c4: repoint the plan to the tests/ layout

**Conclusion: the plan is repaired and executable at HEAD `48d27cca`.** Ten items changed — two
decisions and eight tasks, exactly the enumerated floor and nothing else. `check-plan-routes.py`
on the plan: **exit 0, `0 violation(s)`, 8 DEVIATION lines** (baseline 8, unchanged). Dead-token
grep over `plan.yaml` and `BRIEF.md`: **0**. `yaml.safe_load` object diff before/after:
`changed tasks: [T-01, T-02, T-03, T-04, T-06, T-07, T-09, T-12]`,
`changed decisions: [D-04, D-06]`; `schema feature approval status source_issues panel lanes`
byte-identical. **The escalation tripwire did not fire.**

The rule applied: `test-*.py` / `*.test.*` / `probe-*` may not be pinned under
`.claude/skills/harness/bin/` (`suite_layout.py:29-33`, run on every runner invocation,
`run-unit-tests.sh:31-40`). Subprocess-driving test → `tests/integration/`; in-process →
`tests/unit/`; credentialled probe → `tests/manual/`. **Placement is registration**
(`run-unit-tests.sh:24-28` globs the two directories); no runner edit registers anything.

## The ten items

| # | Item | Change | Reason |
|---|---|---|---|
|1|D-04 `choice`,`because`|probe → `tests/manual/probe-handoff-comprehension.py`; "in neither array" → under neither globbed directory, so `--kind all` cannot execute it; false `because` clause replaced|registration now buys the bar-3 test-code grading (`code_grade.py:458-472`) and must be `locally_run` not `active` because `tests/unit/test-suite-layout.py:105` forbids an active kind detecting `tests/manual`. `locally_run`, `test_matrix` absence and `exclude: .claude/worktrees/**` kept (PF-1e45eb3a, PF-9183266)|
|2|D-06 `choice`,`because`|test → `tests/unit/test-handoff-done-when.py`; restated against the glob|"spawns no subprocess" IS the unit criterion|
|3|T-01 `files`,`verify`,`intent`|→ `tests/unit/`; `run-unit-tests.sh` **removed** from `files`|see verdict below|
|4|T-02 `verify`|path only|`handoff_done_when.py` is a module, stays under `bin/`|
|5|T-03 `files`,`verify`,`intent`|→ `tests/integration/test-check-domain.py`|drives `check-domain.sh` in a subprocess; file already exists there, so "extend" is true again|
|6|T-04 `verify`|path only|same target|
|7|T-06 `files`,`verify`,`intent`|→ `tests/integration/test-check-state.py`; intent changed by a single path substitution|case (g) and the tail paragraph (PF-570b9c87 ruling) byte-identical|
|8|T-07 `verify`|path only (line 2 of the block)|same target|
|9|T-09 `files`,`verify`,`intent`|→ `tests/manual/probe-handoff-comprehension.py`, incl. the `detect`/`cmd` assertions; final conjunct `! grep probe… run-unit-tests.sh` replaced by `run-unit-tests.sh --check-layout`|the old grep was already-passing at HEAD and non-discriminating; `--check-layout` exits 2 iff the probe lands under `bin/`, so it grades this task's actual choice|
|10|T-12 `files`,`verify`,`intent`|**rewritten** → new `tests/integration/test-run-unit-tests-kinds.py`|see verdict below|

## The four verdicts asked for

- **T-01 `files`: `run-unit-tests.sh` is dead weight — removed.** Placement under `tests/unit/`
  is the whole registration, so editing the runner registers nothing; keeping it in `files:`
  would license a doer to edit a required-check script for no effect.
- **T-12: NEW FILE, not an extension of `tests/integration/test-run-unit-tests-layout.py`.**
  Both routes are legal; the new file wins because (i) landing in `tests/integration/` IS its
  registration, so it costs no runner or `test_kinds` edit; (ii) subject separation — the layout
  suite grades `suite_layout.py`'s invariants, these three cases grade one kind's registration
  and its non-execution; (iii) it cannot weaken the layout gate or `suite_layout.py` because it
  touches neither, and the constraint forbidding weakening makes "do not open that file" the
  safer route. All three assertions' substance is preserved: (a) positive registration on the
  real config, (b) discrimination proved against two mutant configs — at HEAD no runner check
  reports drift, so **this test IS the registration gate** — (c) `--kind all` over a fixture tree
  holding the probe under `tests/manual/` never executes it. `traces: [REQ-10]` unchanged.
  Its `verify` also asserts `PASS planted` from the layout suite, a behavioural non-weakening check.
- **D-06's `not added to test_kinds.integration.detect` half: the original subject is gone, a
  narrower one remains.** `integration.detect` is the single directory glob `tests/integration/**`
  (no per-file list exists to add to), it cannot match a file under `tests/unit`, and
  `tests/unit/test-suite-layout.py:101-102` pins it byte-for-byte to `templates/harness.json` —
  so editing it to name a file would redden that assertion. Stated that way in the amended `because`.
- **`lanes:` (plan.yaml:130-172) is STALE AND UNREPAIRABLE by any author.** Rows 139, 142, 148 and
  160 still name `bin/test-check-domain.py`, `bin/test-check-state.py`,
  `bin/test-handoff-done-when.py` and `bin/probe-handoff-comprehension.py`. `plan-merge.py amend`
  refuses any `--key` outside `tasks`/`decisions` (`plan-merge.py:1451-1453`), `apply` exits 7 on a
  differing shared top-level key (`:672-682`), and editor/redirect writes to a `plan.yaml` are
  denied for every author. The rows are advisory — `check-plan-routes.py` never reads `lanes:` —
  so nothing gates on them, but a reader will find four dead surfaces there. **Harness defect,
  carried up as an open question.**

## Not changed, and verified so

Every REQ; every SC but SC-09's mechanism sentence; `## Out of scope`; `## Approval` / `approval:`;
`lanes:`, `panel:` (findings and dispositions), `status:`, `source_issues:`; D-01, D-02, D-03,
D-05, D-07, D-08, D-10; T-05, T-08, T-10, T-11; every `title`, `traces`, `change_type`,
`execution_mode`, `execution_reason`, `depends_on`; T-02's `files:`. **No `execution_mode` moved** —
DEC-174 categorises a gate's own test by what it IS, and `check-domain.sh --resolve` on every new
destination returns `harness-backend-dev harness-dev-ops harness-qa`, i.e. resolvable, so
`main-session-direct` yields the same advisory DEVIATION it already yielded and no violation.

## BRIEF SC-09

Acceptance preserved verbatim in substance — rerunnable on demand, absent from the normal suites —
`verify: automated  evidence: integration` unchanged, id and position unchanged. The mechanism now
names machinery that exists and that an integration test executes: the `handoff_comprehension`
registration in `.harness/harness.json` (asserted positively, shown to discriminate against a
mutant config) and the probe's placement under `tests/manual/`, which neither runner glob covers,
proved by running the real runner with `--kind all` over a fixture tree. No gate is weakened.
