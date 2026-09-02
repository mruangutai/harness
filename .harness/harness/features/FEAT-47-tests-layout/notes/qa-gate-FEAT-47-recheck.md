# QA Gate Recheck — FEAT-47 tests-layout (four prior findings)

Graded against `.claude/worktrees/harness/FEAT-47-tests-layout` (base `b7956fc4`, the merged route
prerequisite; 87 staged paths: moves, edits, two new files, one deletion — unchanged from the prior
gate). Read-only; no source edited. Targeted evidence only, per dispatch: the four repairs named in
`notes/qa-gate-FEAT-47.md`.

## BLUF

All four assigned findings are **closed**, each confirmed by direct execution, not by re-reading the
diff. One structural blocker the prior gate had already flagged (`Q1`, locally-run recorded-run
obligation) is **unaffected by these repairs and remains open** — it was never one of the four items
scoped for repair, but it still gates ship. A fifth, unrelated issue surfaced while re-running T-05's
own verify block verbatim: **SC-10's migration conservation law, previously PASS, is now red** —
caused by an unrelated sibling commit (`b2e36bf3` / PR #1245, "Fix #1033") that landed on
`origin/main` after this branch point and added `test-config-shape-matrix.py` to `bin/`, which this
feature's migration never mapped (it did not exist when T-02/T-03 ran). This is exogenous drift, not
a regression from the four repairs, and matches the shelf-life class the plan already documents for
`origin/main`-bound one-shot checks (`plan.yaml:300-312`).

**VERDICT: BLOCKED** — driven by the still-open locally-run obligation (a structural BLOCKED per the
locally-run rule, not a code defect), with the migration drift reported alongside as a second,
independent item to resolve before ship. Neither blocks crediting the four repairs as closed.

## The four findings, rechecked

### 1. SC-05 sole-implementation sweep — CLOSED

`tests/unit/test-suite-layout.py` now carries the full T-05 step-2b shape: a 4-entry
`SOLE_IMPLEMENTATION_EXEMPTIONS` list, `KIND_PATTERNS`/`DISCOVERY_FRAGMENTS` scan helper, a `>=90`
tracked-`.py` discovery floor, the sweep itself (`unexpected == []`), two positive controls
(`suite_layout.py`, `tests/manual/suite-census.py`), and a three-shape red proof (slash literal,
`os.path.join`, `Path(...).glob`) each asserted to trip the sweep and NOT already be in the exemption
list. Ran directly (`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-suite-layout.py`): **19/19
PASS, exit 0**, including `sole implementation sweep`, all three `red proof shape N` cases, both
positive controls, and the floor check.

### 2. SC-09 dynamic subprocess instrumentation — CLOSED

`tests/manual/suite-census.py:children()` is no longer a static regex. It now monkeypatches
`subprocess.Popen.__init__`, `os.system`, `os.fork`, and `os.posix_spawn`, runs each test file via
`runpy.run_path` under the patch, and reports the actually-observed child argv heads. Ran directly
against the three files the prior gate named as false negatives:

- `test-board-lifecycle.py`: `children=59` (previously `children=0`)
- `test-branch-create-gate.py`: `children=7`, names the real `branch-create-gate.sh` path
- `test-factory-decompose.py`: `children=2`, names `fork`/`fork`

All three now correctly report the subprocess forking the plan itself named as the reclassification
reason.

### 3. T-05 strict verdict baseline — CLOSED

Ran the exact `verdict-lines` invocation from T-05's verify block:

```
python3 tests/manual/suite-census.py verdict-lines \
  --baseline .harness/harness/features/FEAT-47-tests-layout/notes/research-tests-layout.md \
  --deleted test-run-unit-tests-kinds.py --strict
```

**64/64 files matched (`expected == actual` on every line), exit 0.** `research-tests-layout.md` has
been re-derived against the current tree; none of the ~20 files the prior gate found drifted
(`test-check-domain.py`, `test-gh-sync.py`, `test-check-state.py`, `test-harness-boundary.py`,
`test-orchestrator-playbook.py`, `test-factory-config.py`, etc.) show a mismatch now. Full suite
cross-check: `run-unit-tests.sh --kind unit` (21 files) and `--kind integration` (43 files) both exit
0 with zero `FAIL`/`not ok` lines outside self-tests — 21 + 43 = 64, consistent with dispatch's
"prior full runner passed 64 files."

### 4. `omp_session_accessor` clean-cutover registration — CLOSED (registration only; standing obligation still open, see below)

`harness.json`'s `test_kinds.omp_session_accessor.detect` and `.cmd` now both read
`tests/manual/probe-omp-session-accessor.py` — the pre-move `.claude/skills/harness/bin/` path is
gone from the registration. Confirmed: the file exists at the new path (`-rwxr-xr-x`, executable),
the old path 404s, and no other **live** reference to the old path remains — the only surviving
occurrences of the old path string are historical/narrative (`DECISIONS.md`'s DEC-201 entry, kept in
past tense by design per `plan.yaml:1048-1055`'s per-sentence exemption; `FEAT-38`/`FEAT-44` evidence
docs, also historical readbacks; and the plan's own T-04 files list, which names both the source and
destination of the `git mv`). None of these are registration surfaces.

The specific defect the prior gate named — "the registration itself is now **broken**" — is fixed.

## Residue, not attributable to the four repairs

### Still open: locally-run obligation has no recorded run (carried from prior gate's Q1)

Per the locally-run rule: a diff that touches a `locally_run` kind's `detect` surface requires a
recorded run under the feature's `notes/`, or the kind is `BLOCKED`, never a soft skip. This diff
moved the file the glob names, so the surface is touched. Checked `notes/` for a recorded execution
of the probe: none exists (only this gate's own reports discuss the kind; no run transcript). This
was already an open question in the prior gate (`Q1`) and the registration fix alone does not
discharge it — it needs either an actual recorded run on a credentialled host, or an explicit,
recorded decision to defer it to a later feature.

### New, unrelated: SC-10 migration conservation law now red

Running T-05's verify block's `migration` line verbatim:

```
python3 tests/manual/suite-census.py migration --floor 58 \
  --base "$(git rev-parse --verify --quiet origin/main || git rev-parse --verify main)" \
  --deleted test-run-unit-tests-kinds.py
```

→ `base test count: 64`, then `test-config-shape-matrix.py: expected exactly one destination, got
[]`, **exit 1**. `git log b7956fc4..origin/main` shows `b2e36bf3` ("Fix #1033: bind config-shape
changes to the integration floor (DEC-212)", PR #1245) added
`.claude/skills/harness/bin/test-config-shape-matrix.py` — a file that did not exist at this
feature's branch point and that none of T-02/T-03's migration mapping could have covered. This is
exogenous sibling-PR drift on `origin/main`, not a regression introduced by the four repairs and not
part of this diff. The prior gate's own SC-10 evidence (`base test count: 63, exit 0`) was measured
before this sibling commit landed; it is the same "one-review shelf life" class `plan.yaml:300-312`
already documents for these `origin/main`-bound one-shot checks, this time hitting `migration`
instead of `verdict-lines`. Because T-05's verify block runs under `set -e`, this line would currently
halt the block before reaching the (now-clean) `verdict-lines` line if run as one script today.
Recommend re-running T-05's verify immediately before the actual merge, per the plan's own stated
mitigation for this class of check, rather than treating it as a defect in this recheck's four items.

## Verdict detail

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: >
    All four assigned findings (SC-05 sweep, SC-09 dynamic instrumentation, T-05 --strict baseline,
    omp_session_accessor registration) are closed and confirmed by direct execution. Overall gate
    stays BLOCKED on a pre-existing, unresolved locally-run recorded-run obligation (carried from the
    prior gate's Q1, not one of the four repairs), plus a newly observed unrelated drift: SC-10's
    migration conservation law now fails because sibling PR #1245 added an unmigrated bin/ test file
    to origin/main after this branch point.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - kind: unit
      state: satisfied
      cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit"
      named_tests: 21
    - kind: integration
      state: satisfied
      cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration"
      named_tests: 43
    - kind: omp_session_accessor
      state: locally-run
      cmd: "tests/manual/probe-omp-session-accessor.py"
      named_tests: 0
  coverage_gaps: []
  sc_evidence:
    - { id: SC-05, test: "tests/unit/test-suite-layout.py (sole-implementation sweep, floor, positive controls, 3-shape red proof) — PASS, 19/19" }
    - { id: SC-09, test: "tests/manual/suite-census.py children (dynamic Popen/os.system/fork/posix_spawn instrumentation via runpy) — verified against test-board-lifecycle.py (children=59), test-branch-create-gate.py (children=7), test-factory-decompose.py (children=2, fork) — PASS" }
    - { id: "SC-01/SC-02", test: "tests/manual/suite-census.py verdict-lines --baseline notes/research-tests-layout.md --strict — PASS, 64/64 files matched, exit 0" }
    - { id: SC-10, test: "tests/manual/suite-census.py migration --floor 58 --base origin/main --deleted test-run-unit-tests-kinds.py — FAIL, exit 1, unrelated sibling drift (test-config-shape-matrix.py added to bin/ by PR #1245 after branch point)" }
  open_questions:
    - { id: Q1, question: "harness.json's omp_session_accessor (locally_run) kind's detect/cmd registration is now correct (tests/manual/probe-omp-session-accessor.py), but no recorded run of the probe exists under this feature's notes/. The diff touched this kind's detect surface (moved the file), so per the locally-run rule this is BLOCKED, not a soft skip, until a recorded run exists or an explicit deferral decision is recorded.", blocking: true }
    - { id: Q2, question: "T-05's verify block's migration line is now red (exit 1) against live origin/main due to sibling PR #1245 landing an unmigrated bin/ test file after this branch point. Not caused by this diff. Re-run T-05's verify immediately before actual merge (per plan.yaml:300-312's own one-review-shelf-life design), rather than treating this as a defect to fix now.", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-47-tests-layout/notes/qa-gate-FEAT-47-recheck.md
```
