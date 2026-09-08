# review-harness-qa-c4 — BUG-124 test-matrix gate over the pin

**matrix_ok: true.** Independent re-run at `review_sha=6c037de4` reproduces both prior
measurements (`qa-c4.md`'s segment PASS, the lead's SIMPLIFY-apply sweep): full sweep
`RUNNER_EXIT=0`, 0 `^FAIL ` lines, 5403 output lines, `pool: 8 workers, 80 files`. No
disagreement to report.

## Change type and required kinds

Diff `80ce35d1..6c037de4` on the four named files spans two plan tasks, both `status: done`:
- T-01 (`harness_boundary.py` + `tests/unit/test-harness-boundary.py`) — `change_type: logic`
  → matrix `always: [unit]`.
- T-02 (`dispatch-guard.sh` + `tests/integration/test-dispatch-guard.py`) — `change_type:
  bugfix` → matrix `always: []`, `when` predicates evaluated against this diff:
  - `unit` if `touches_runtime_code` → **fires** (dispatch-guard.sh, harness_boundary.py are
    runtime source).
  - `integration` if `fix_confined_to_tests_and_contract_docs` → does not fire (the fix edits
    real source, not only tests/docs), so the matrix does not obligate `integration` here.
  - `__bug_class__` if `match_bug_class` → unresolvable placeholder per repo Expertise G-08
    (no bug-class taxonomy entry fires for any diff yet); contributes nothing.

**Floor: `unit` (mandatory, both tasks agree).** QA adds `integration` on top of the floor
(P-04/verification-rules "add what the diff warrants, never drop below"): the diff's own
183-line `test-dispatch-guard.py` addition is the only artifact that exercises
`dispatch-guard.sh`'s new refusal behaviour end-to-end, T-02's own `verify:` block runs it, and
every one of BRIEF SC-01..SC-09 (except SC-06, `verify: inspection`) is typed
`evidence: integration`. Treating it as non-binding would gate nothing that actually proves the
fix.

No other matrix kind applies: `.harness/team-config.yaml` (config surface) is unedited by this
diff (read-only per the plan and the lanes table), so `config`'s `touches_config_shape` does not
fire; the diff touches no `frontend`/`ai_behavior` surface.

## Per-kind results

| kind | required by | command | exit | discovery | result |
|---|---|---|---|---|---|
| unit | matrix (both tasks) | `python3 tests/unit/test-harness-boundary.py` (also covered by the sweep's `--kind unit` bucket) | 0 | 56 named `PASS` cases, `ALL PASS` | **satisfied** |
| integration | qa-added (diff-warranted, not matrix-mandatory) | `python3 tests/integration/test-dispatch-guard.py` (also covered by the sweep's `--kind integration` bucket) | 0 | 69 of 69 cases passed | **satisfied** |
| full sweep (both kinds, whole repo) | cross-check | `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh` | 0 | 5403 lines, `8 workers, 80 files` | **satisfied**, matches the two prior independent measurements at this pin exactly |

Both target test files are confirmed inside the sweep's own log:
`test-harness-boundary.py (exit 0, 0.12s)` and `test-dispatch-guard.py (exit 0, 4.67s)`.

## Adequacy against BRIEF SC-01..SC-09

Read the 69 integration case names directly (not just the pass count) against T-02's intent
list (a)–(i) and the BRIEF's SC list:

| SC | evidence kind | bound test case(s) | produced? |
|---|---|---|---|
| SC-01 | integration | `case 18a: an inverted run-dir slug is refused` | yes |
| SC-02 | integration | `case 18b: stderr names a compliant form ending in -eng` | yes |
| SC-03 | integration | `case 19` (t01-eng / plan-product / dated slug not refused) + all 17 pre-existing cases (1–17) present, none edited (diff stat: `+183/-0` on this file — purely additive) | yes |
| SC-04 | integration | `case 22: t01-oddsquad`/`oddsquad-t01`/compliant-form-names-oddsquad | yes |
| SC-05 | integration | `case 21: a grant-less manifest is not refused` + skip-text assertion | yes |
| SC-06 | **inspection** | not test-run; RED PROOF recorded in `receipt-harness-backend-dev-T-02-c2.md` (md5-confirmed pre-change binary, `DISPATCH_GUARD_BIN`, 61/69 with 8 named red cases). Inspection evidence exists at the pin — QA does not re-grade an inspection SC, flagging only that it is present, not missing | present |
| SC-07 | integration | `case 18g: the refusal strands no claim for the dispatched persona` | yes |
| SC-08 | integration | `case 18h: pasting the refusal back is not itself refused` + 2 companion assertions | yes |
| SC-09 | integration | `case 21`/`case 23` paired skip-vs-derivation-failed text assertions | yes |

No coverage gap: every `verify: automated, evidence: integration` SC in the BRIEF has a
named, currently-passing case; the one `verify: inspection` SC (SC-06) has its inspection
artifact present at the pinned sha. Phase-1 expectation (before reading code): unit coverage
for the four new `harness_boundary` helpers, integration coverage for the refusal, the
fail-open paths, and the paste-back non-poison-pill case — all present; no gap between Phase 1
and Phase 2.

## Findings

None. `matrix_ok: true`, all required and qa-added kinds satisfied by a real, named, currently
green test at this pin, and independently reproduces both prior measurements at the same sha.

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok true — unit (matrix floor) and integration (qa-added) both satisfied at 6c037de4, reproducing the two prior measurements exactly (RUNNER_EXIT=0, 0 FAIL, 5403 lines, 8 workers/80 files)"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-harness-boundary.py (sweep --kind unit)", named_tests: 56 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-dispatch-guard.py (sweep --kind integration)", named_tests: 69 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-dispatch-guard.py::case 18a" }
    - { id: SC-02, test: "tests/integration/test-dispatch-guard.py::case 18b" }
    - { id: SC-03, test: "tests/integration/test-dispatch-guard.py::case 19 + cases 1-17 unedited" }
    - { id: SC-04, test: "tests/integration/test-dispatch-guard.py::case 22" }
    - { id: SC-05, test: "tests/integration/test-dispatch-guard.py::case 21" }
    - { id: SC-06, test: "notes/receipt-harness-backend-dev-T-02-c2.md (inspection, RED PROOF at md5-confirmed pre-change binary)" }
    - { id: SC-07, test: "tests/integration/test-dispatch-guard.py::case 18g" }
    - { id: SC-08, test: "tests/integration/test-dispatch-guard.py::case 18h" }
    - { id: SC-09, test: "tests/integration/test-dispatch-guard.py::case 21 + case 23" }
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-124-run-dir-squad-suffix/notes/review-harness-qa-c4.md
```
