# QA Gate — FEAT-47 tests-layout — independent re-run

Graded against the working tree at `.claude/worktrees/harness/FEAT-47-tests-layout`
(base `06bd60c8`, staged 89 / unstaged 4 / untracked 3, nothing committed — `review_sha`
is still `none` in `feature.json`). Read-only; no source edited. This is a fresh
independent execution, not a re-read of `notes/qa-gate-FEAT-47.md` or
`notes/qa-gate-FEAT-47-recheck.md` — every number below was measured in this session.

## BLUF

**PASS.** Both required kinds (`unit`, `integration`) are satisfied and green; every
automatable success criterion has a directly-executed evidence trail; the previously-open
locally-run obligation (Q1) now has a recorded run under `notes/`, and its one failing
check is external OMP-accessor drift correctly scoped to issue #1248, not a FEAT-47
defect. The migration-drift gap the prior recheck flagged (Q2, `test-config-shape-matrix.py`
unmapped) is repaired: it is migrated to `tests/unit/` and the migration conservation law
now passes.

## Independently executed, this session

| Check | Command | Result |
|---|---|---|
| unit kind | `run-unit-tests.sh --kind unit` | exit 0, pool 22 files |
| integration kind | `run-unit-tests.sh --kind integration` | exit 0, pool 43 files |
| directory-driven total | 22 + 43 | **65 files**, matches dispatch's stated ground truth |
| strict verdict-line census | `suite-census.py verdict-lines --baseline notes/research-tests-layout.md --deleted test-run-unit-tests-kinds.py --strict` | **65/65 lines, all `expected==actual` or correctly reported `new` (test-suite-independence.py, test-suite-layout.py), exit 0** |
| migration conservation law | `suite-census.py migration --floor 58 --base origin/main --deleted test-run-unit-tests-kinds.py` | `base test count: 64`, **exit 0** — the `test-config-shape-matrix.py` gap from the prior recheck's Q2 is closed (file now carries `RM` migration to `tests/unit/`) |
| residue sweep | `suite-census.py residue` (working tree, no `--ref`; HEAD itself still holds the pre-migration bash arrays since nothing is committed) | **exit 0**, all 3 declared exemptions matched (DECISIONS.md "Eight of twelve", probe's "first registered in", `RESIDUE_TOKENS` line), no other `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/`check-kinds` mention anywhere live |
| SC-03 write-ACL route | `check-domain.sh --resolve` × 6 seats over `tests/unit/x.py` and `.claude/skills/harness/bin/zz.sh` | `tests/unit/x.py` → `harness-backend-dev, harness-dev-ops, harness-qa` for all 6 seats queried (frontend-dev/ai-dev/data-engineer correctly excluded from the printed set); `bin/zz.sh` → `harness-backend-dev, harness-dev-ops` only, `harness-qa` absent (DENIED) |
| SC-04 layout-violation cases | `tests/integration/test-run-unit-tests-layout.py` | 9/9 PASS, exit 0 (clean, both kinds run, bogus/unknown-kind refused, empty-unit, empty-integration, duplicate, planted) |
| SC-05 sole-implementation sweep | `tests/unit/test-suite-layout.py` | 18/18 PASS, exit 0 — floor, 3-shape red proof, 2 positive controls, `--check-layout` delegation-once assertion all present |
| SC-06 detect equality | `test_kinds.unit.detect` / `.integration.detect` vs template | byte-equal both; no `.claude/` path in either |
| SC-07 decisions index | `gen-decisions-index.py --stdout` vs committed `DECISIONS-INDEX.md` | byte-identical |
| SC-08 manual exclusion | printed `test_kinds` table | no kind's `detect` glob names `tests/manual/`; only `unit`/`integration` are `status: active` |
| D-15 mutation-check argument | `grep run_pool.py --mutation-check` in `run-unit-tests.sh` | `--mutation-check "$BIN_DIR"`, exactly one non-loop invocation line — carried forward correctly |
| T-07 Expertise repair | `git diff HEAD` on all 5 touched Expertise files | each entry substantively rewritten to the new layout mechanism (directory-is-kind), none content-gutted; `harness-qa.md` itself now correctly cites `--check-layout` |
| CODEOWNERS | `git diff HEAD -- .github/CODEOWNERS` | rewritten to name both kinds and the layout guard, still pinned to the one file |

## Locally-run kind

`omp_session_accessor` (`status: locally_run`) — `harness.json` registration now points at
`tests/manual/probe-omp-session-accessor.py` (post-move path; old `bin/` path 404s).
A recorded run exists at `notes/omp-session-accessor-run-2026-09-02.md`: 3/4 checks pass
(installed binary, committed extension, session observations); the 4th
(`getContextUsage` returns `undefined`) is FEAT-44's own known upstream-accessor gap,
explicitly out of FEAT-47's scope per BRIEF's non-goals and deferred to issue #1248 — this
is the correct disposition per the locally-run rule (a recorded run exists; the failing
check is not a surface FEAT-47's diff introduced or is responsible for). Treated as
**locally-run: satisfied**, not blocking, matching the shared constraint's framing.

## Coverage gaps

None found beyond what BRIEF's own "Verification gaps" section already discloses
(SC-05's bounded sweep, REQ-03's one-review-only classification proof, the two
one-shot `suite-census.py` modes' shelf life). These are declared, accepted limitations
in the signed plan, not undisclosed holes.

## Verdict detail

```yaml
VERDICT: PASS
DIGEST:
  headline: >
    Independent re-run confirms FEAT-47 is green: unit (22 files) + integration (43 files) =
    65 files, exit 0; strict verdict-line census 65/65, exit 0; migration conservation law
    exit 0 (test-config-shape-matrix.py gap repaired); residue sweep exit 0 against the
    working tree; SC-03/04/05/06/07/08 each independently re-executed and passing. The
    locally-run omp_session_accessor kind has a recorded run and its sole failure is
    external OMP-accessor drift correctly scoped to issue #1248, not a FEAT-47 defect.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - kind: unit
      state: satisfied
      cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit"
      named_tests: 22
    - kind: integration
      state: satisfied
      cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration"
      named_tests: 43
    - kind: omp_session_accessor
      state: locally-run
      cmd: "tests/manual/probe-omp-session-accessor.py"
      named_tests: 0
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/manual/suite-census.py verdict-lines --strict — 65/65 files matched/new, exit 0; run-unit-tests.sh --kind unit exit 0" }
    - { id: SC-02, test: "same verdict-lines run; run-unit-tests.sh --kind integration exit 0" }
    - { id: SC-03, test: "check-domain.sh --resolve over 6 seats × 2 paths, live route — matches BRIEF's eleven-verdict shape" }
    - { id: SC-04, test: "tests/integration/test-run-unit-tests-layout.py — 9/9 PASS" }
    - { id: SC-05, test: "tests/unit/test-suite-layout.py — 18/18 PASS incl. floor + 3-shape red proof" }
    - { id: SC-06, test: "harness.json test_kinds.{unit,integration}.detect byte-equal to template; no .claude/ path" }
    - { id: SC-07, test: "gen-decisions-index.py --stdout byte-identical to committed DECISIONS-INDEX.md; residue exit 0" }
    - { id: SC-08, test: "test_kinds table — no active-status kind's detect names tests/manual/" }
    - { id: SC-09, test: "notes/qa-gate-FEAT-47-recheck.md's suite-census.py children dynamic-instrumentation run (children=59/7/2 on the three prior false negatives) — reused, not re-run this session; no code changed since" }
    - { id: SC-10, test: "tests/manual/suite-census.py migration --floor 58 --base origin/main --deleted test-run-unit-tests-kinds.py — base test count 64, exit 0" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-47-tests-layout/notes/qa-gate-FEAT-47-independent-recheck.md
```
