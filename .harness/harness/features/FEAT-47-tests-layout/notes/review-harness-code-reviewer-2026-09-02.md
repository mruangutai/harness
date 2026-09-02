# Code Review — FEAT-47 tests-layout — pinned `06bd60c8..28e4f88a`

Diffed `base 06bd60c8e3185a166723dfc7bfec860e2bdc88f7..review_sha 28e4f88a9d41539d0a561f7600f42210c84b5d38`
(`git merge-base origin/main 28e4f88a` independently confirms `06bd60c8` — matches the dispatched
base exactly). One commit in range: `28e4f88a feat(harness): move tests to directory-based suites`,
no `[harness:human]` commits since the last pin. Working tree dirty only in
`.harness/harness/features/FEAT-47-tests-layout/{feature.json,review_sha}`, permitted review-pin
metadata — nothing else uncommitted. T-01 (REQ-01, `harness_boundary.py` / `team-config.yaml`) landed
at `06bd60c8` itself and is unchanged by this diff; verified its grant is still live at the review sha
(`tests/**` present in `HARNESS_CONTROL_PLANE` and in both seats' `team-config.yaml` entries).

## BLUF

**FAIL.** Two must-fix items, both concrete and verified independently of the feature's own claims:
(1) `code-grade.py` reports a blocking grade-3 failure the digest must carry as `code_grade: fail`
(`tests/manual/suite-census.py:143 main`); (2) REQ-07 ("No live file presents the deleted arrays or
their cross-check as current") is violated by three live, non-record files the feature's own residue
sweep cannot see because they paraphrase the deleted mechanism instead of naming it literally. Four
more grade-2 functions are reported below with required reasons (non-blocking, med). Everything else
inspected — REQ-01/02/03/04/06/08, SC-06/08/09/10, the layout predicate's four contracted violation
types, the migration/residue instruments' core logic — holds.

## Stage 1 — spec compliance

| REQ | Status | Evidence |
|---|---|---|
| REQ-01 | met | `harness_boundary.py:289` carries `"tests/**"`; `team-config.yaml:187,229` grant `harness-backend-dev`/`harness-dev-ops`; unchanged since base, still true at review sha |
| REQ-02 | met | `run-unit-tests.sh` builds `SCRIPTS` from `tests/unit/test-*.py` / `tests/integration/test-*.py` globs only; no registration list survives |
| REQ-03 | met | SC-09's `children` dynamic-instrumentation run is reused from the prior recheck, no code changed since — acceptable per BRIEF's own "point measurement" framing |
| REQ-04 | met | migration conservation law (`suite-census.py migration --floor 58`) exits 0 against the review sha per the prior independent QA recheck; not re-run here per dispatch |
| REQ-05 | met, with a scope note (see Finding F-3) | `suite_layout.py` catches all four contracted violation types; `tests/integration/test-run-unit-tests-layout.py` proves the runner surfaces each |
| REQ-06 | met | verified directly: `harness.json`'s `unit`/`integration` `.detect` are byte-equal to `templates/harness.json`'s |
| REQ-07 | **NOT met** — see Finding F-1 (must_fix) | three live files still present the deleted drift-detector/cross-check as current |
| REQ-08 | met | `omp_session_accessor` kind is `status: locally_run` (not `active`), `detect`/`cmd` both point at `tests/manual/probe-omp-session-accessor.py`; no `active` kind's glob or either runner-walked directory touches `tests/manual/` |

SC-06, SC-08 verified directly (byte-equal detect, `tests/manual` absent from every active glob).
SC-10 verified via the prior independent recheck's exit-0 record; the instrument itself has a design
gap noted as Finding F-4 (should_fix, does not change today's result). SC-07 is `verify: inspection`
— this review is that inspection, and it is where F-1 originates; the automated `residue` mode passing
does not close REQ-07 by itself.

No scope leakage found beyond Finding F-3 (see below — a deviation inside an in-scope file, not new
files or unrelated work).

## Findings

### F-1 (must_fix, high) — REQ-07: three live files still present the deleted drift-detector/cross-check as current

`tests/manual/suite-census.py residue`'s token search is `RESIDUE_TOKENS = ("UNIT_SCRIPTS",
"INTEGRATION_SCRIPTS", "check-kinds")` — a literal-string sweep. It correctly reports clean (verified
by re-running it against the review sha: `reading ref 28e4f88a...`, 3/3 matches all `covered`, exit 0).
But REQ-07's own text binds to the *mechanism*, not to those three spellings, and three live files
describe the deleted mechanism in words the sweep cannot see:

1. **`.harness/harness.json:117`**, the `_test_kinds_note` field (untouched by this diff, though
   `harness.json` is one of T-05's own declared files): *"run-unit-tests.sh's drift detector requires
   every `probe-*.py` script under bin/ to appear in exactly one `locally_run` kind's `detect`, so the
   check stays discoverable rather than remembered."* This is doubly wrong at the review sha: the
   drift detector it names was deleted by this same diff, and the probe it describes no longer lives
   under `bin/` at all (T-04 moved it to `tests/manual/`). A future editor reading this schema note
   before adding a new `probe-*.py` will believe registering it in some kind's `detect` is what keeps
   `bin/` clean — the real behavior (`suite_layout.py`'s unconditional "no probe-shaped file under
   bin/" check) has nothing to do with registration.
2. **`.claude/skills/harness/bin/layout_fixtures.py:12`** (untouched by this diff): *"Not a test file
   (the run-unit-tests.sh drift detector scans only test-\*.py)."* Same mechanism, same deletion,
   same file left uncorrected.
3. **`.harness/expertise/harness-dev-ops.md`** (project tier — the cross-repo glob T-07's own D-19
   declares as swept, `.harness/expertise/*.md` and `.harness/*/expertise/*.md`), gotcha **G-03**:
   *"See the drift-detector's nested-loop membership check in
   `.claude/skills/harness/bin/run-unit-tests.sh` for the working pattern."* This is injected into
   every `harness-dev-ops` spawn, in every repository, forever — not scoped to this one. The nested-
   loop pattern it points to was deleted by this diff; a dev-ops agent following this pointer today
   finds nothing at that location. T-07 repaired the five files under `.harness/harness/expertise/`
   (repo tier) but never touched `.harness/expertise/*.md` (project tier) at all — confirmed: no path
   under that glob appears anywhere in the diff.

All three are outside `.harness/notes/`, `.harness/harness/features/`, `.harness/logs/`, so none
qualifies as a record REQ-07 exempts. This is a real omission against an explicit, numbered
requirement with dedicated verification machinery — not a style note.

### F-2 (must_fix, high) — code_grade: fail, `tests/manual/suite-census.py:143 main`

Ran `python3 .claude/skills/harness/bin/code-grade.py --base 06bd60c8e3185a166723dfc7bfec860e2bdc88f7
--head 28e4f88a9d41539d0a561f7600f42210c84b5d38` directly (base independently confirmed via
`git merge-base origin/main 28e4f88a` = `06bd60c8`, so this is the canonical range).

```
PATH: "tests/manual/suite-census.py"
LINE: 143
QUALNAME: main
CYCLOMATIC: 1
COGNITIVE: 0 (Sonar-style approximation)
ABC: 20.2
GRADE: 3
DRIVER: abc
BAR: 4
RESULT: FAIL
SEVERITY: high
```

Grade 3 against a grade-4 production bar blocks identically to grade 1 per policy — this is not
exempt the way the grade-2 records below are. `main()` is `argparse` subparser wiring (four
`add_parser`/`add_argument` chains); its cyclomatic and cognitive complexity are both near zero, and
the ABC score is driven entirely by the sheer count of chained calls on five lines. Judgment says this
is low real risk — but the mechanical gate is what `validate-digest.py` recomputes and refuses a
disagreeing digest over, so it is reported here as required rather than argued around.
`code_grade: fail` for this review.

### F-3 (should_fix, med) — `suite_layout.py.violations()` implements two violation types T-05's own intent excludes

T-05's intent for the new module is explicit: *"for these four conditions... Nothing else."* The
shipped `violations()` (`.claude/skills/harness/bin/suite_layout.py:19-27`) adds a fifth/sixth check
— any `test-*.py`/`test_*.py`/`*_test.py`-shaped file anywhere under `tests/` that is not sitting
directly in `tests/unit` or `tests/integration` under exact `test-*.py` naming is reported as
`"test file is not selected by the runner"`. `tests/unit/test-suite-layout.py` tests this deliberately
(`add_nested_test`, `add_undiscoverable_test`, needles `"test-nested.py"` / `"test_hidden.py"`), so
it is not an accident — it is undocumented, unrequested scope inside an otherwise in-scope file.
Concretely: if a later project wants to group integration tests under a subdirectory (e.g.
`tests/integration/api/test-x.py`), or names a file in the pytest convention (`test_x.py`) anywhere
under `tests/`, this predicate refuses it with a message that matches none of SC-04's four documented
failure strings and that no REQ or SC in this BRIEF authorizes. It strengthens REQ-05's spirit (fail
loudly rather than silently not-discover) and is well tested, so it is not reported as broken — it is
reported because "no REQ asked for it" gates a spec-compliance finding even when the code is an
improvement, per this review's own protocol.

### F-4 (should_fix, med) — `suite-census.py migration()`'s destination check is an unpinned, undisclosed working-tree read

`migration()` (`tests/manual/suite-census.py:47-58`) resolves `--base` through git (`git ls-tree -r
--name-only <ref> ...`) correctly, matching the plan's explicit "resolve the ref with git, never with
a working-tree read." But the destination side —
`hits=[d/name for d in KIND_DIRS if (d/name).exists()]` — is a live filesystem read with no `--ref`
option and, unlike its sibling `residue()` (which prints `"reading ref X"` / `"reading working
tree"`), no disclosure of what it read. BRIEF's Success Criteria preamble states every criterion is
"graded at the pinned review_sha... never against the working tree," and SC-10 is `verify: inspection`
— meaning a human re-runs this exact tool later to confirm the review sha's state. In *this* review
the working tree is the review sha's own clean checkout, so the answer happens to be right — but the
tool cannot tell a caller, and cannot itself guarantee, that the tree it read was the ref being
graded. A later reviewer re-verifying this exact review sha from a worktree that has since moved
past it (a common state — worktrees are reused across cycles) gets a result computed against
whatever is currently on disk, silently mislabeled as verifying the pinned sha.

### Grade-2 functions (reasoned, non-blocking — `code_grade` contribution: `fail`, subsumed by F-2)

Per policy, grade 2 never blocks the build on its own, but each needs a written reason:

- **`suite_layout.py:6 violations`** (cyclomatic 13, cognitive 11, ABC 26.9, driver
  cyclomatic+abc) — one function implementing every check D-03 requires in "one function in one
  module," including the two extra checks from F-3. The complexity mirrors the violation surface it
  is checking, not accidental sprawl; it has exactly one call site.
- **`tests/manual/suite-census.py:32 verdict`** (cognitive 26, ABC 27.1, driver cognitive+abc) — a
  one-shot review instrument (D-18) with one call site, doing baseline parsing, per-file subprocess
  execution, verdict-line counting and drift/strict reporting in sequence. Splitting it would relocate
  complexity into new one-call-site helpers rather than reduce it.
- **`tests/manual/suite-census.py:47 migration`** (cyclomatic 12, ABC 24.7, driver cyclomatic) —
  same shape: the D-14 conservation law's five preconditions, one call site, one-shot instrument.
- **`tests/manual/suite-census.py:61 residue`** (cyclomatic 17, cognitive 28, ABC 43.8, driver
  cyclomatic+cognitive+abc) — the most complex of the four; implements all of D-16's mandated safety
  properties (expertise-exemption refusal, ref/working-tree disclosure, token sweep, per-line
  exemption coverage, positive control, stale-exemption detection) in one function with one call site.
  A worthwhile decomposition exists here more than in the other three (the expertise-refusal guard and
  the stale-exemption check are already syntactically separable), but nothing here is broken.

## Not re-litigated

`.harness/harness/features/FEAT-47-tests-layout/notes/review-harness-code-reviewer-simplify-reuse.md`
already reports, in detail, the 61-file duplicated `_anchor_*` bin-path-resolver preamble introduced
by the T-02/T-03 moves. That finding stands; this review does not restate it and it is not treated as
new here.

## Verdict detail

```yaml
VERDICT: FAIL
DIGEST:
  headline: >
    REQ-07 unmet (three live non-record files still describe the deleted drift-detector/cross-check
    as current) and code-grade reports a blocking grade-3 failure in suite-census.py's main();
    everything else inspected holds, including all four contracted layout-violation types and the
    template-identical detect globs.
  severity_max: high
  findings: 6
  must_fix:
    - "REQ-07: harness.json:117 _test_kinds_note, bin/layout_fixtures.py:12, and the project-tier
       .harness/expertise/harness-dev-ops.md G-03 all still present the deleted run-unit-tests.sh
       drift detector / KIND-DRIFT cross-check as a live mechanism; none is a record path REQ-07
       exempts (F-1)"
    - "code_grade: fail — tests/manual/suite-census.py:143 main(), GRADE 3 against BAR 4, ABC 20.2,
       driver abc (F-2)"
  spec_violations:
    - { kind: omission, path: .harness/harness.json, ref: REQ-07 }
    - { kind: omission, path: .claude/skills/harness/bin/layout_fixtures.py, ref: REQ-07 }
    - { kind: omission, path: .harness/expertise/harness-dev-ops.md, ref: REQ-07 }
    - { kind: scope_creep, path: .claude/skills/harness/bin/suite_layout.py, ref: D-03 }
  reviewed: "06bd60c8e3185a166723dfc7bfec860e2bdc88f7..28e4f88a9d41539d0a561f7600f42210c84b5d38"
  human_commits_in_scope: []
  code_grade: fail
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-47-tests-layout/notes/review-harness-code-reviewer-2026-09-02.md
```
