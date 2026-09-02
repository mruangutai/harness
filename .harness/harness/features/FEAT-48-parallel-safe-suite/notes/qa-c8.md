# QA test-matrix gate — FEAT-48-parallel-safe-suite — validate c8

BLUF: **matrix_ok: true** — floor `unit + integration` fully satisfied against `e64e863e`, both
kinds bound to real, non-null `cmd`s and both exercised directly by me (not only via `--kind all`).
c7's HIGH (no self-red-proof) is **closed**. c7's MEDIUM (`__pycache__` leg) is **still open**,
confirmed by direct read of the current file. A new disclosure finding: M5 (same-size/same-mtime
content-swap blindness) is not merely undisclosed — `DECISIONS.md:6601-6602` makes an affirmative
claim that reads as covering it and is not true without qualification.

## Change type and floor

`git -C <WORKTREE> diff b86ce66a..e64e863e --stat`: 15 files, `.harness/harness.json`-relevant code
touches only `run_pool.py`, `test-run-pool.py`, `test-suite-independence.py` (rest is STATE/notes).
`plan.yaml` grep: T-04 (`run_pool.py`) is `change_type: cross_module`; T-03
(`test-suite-independence.py`) is `logic`. `.harness/harness.json:8-79` `test_matrix`:
`logic.always=[unit]`, `cross_module.always=[unit,integration]`. Union floor: **unit + integration**.

## Required-kind table (four-state)

| kind | detect/list membership | cmd | state | evidence |
|---|---|---|---|---|
| unit | `test-suite-independence.py` in `UNIT_SCRIPTS` (run-unit-tests.sh:30, grep-verified, not just glob-matched) | `run-unit-tests.sh --kind unit`, status active | **satisfied** | targeted run below, exit 0 |
| integration | `test-run-pool.py` in `INTEGRATION_SCRIPTS` (run-unit-tests.sh:31, grep-verified) | `run-unit-tests.sh --kind integration`, status active | **satisfied** | targeted run below, exit 0 |
| component/ui/eval/typecheck | `cmd: null` for all four; no `detect` glob matches `.claude/skills/harness/bin/**` | n/a | soft skip (unchanged since c7, no new surface added at e64e863e) | `harness.json:126-153` |

Not re-running `--kind all` per the non-goal (lead already did: exit 0, 63 files, 0 FAIL, 0 MUTATED).

## My own targeted runs (`env -u HARNESS_AGENT_TYPE`)

- `python3 .claude/skills/harness/bin/test-suite-independence.py` → **exit 0**. Prints all six
  `ok self-test …` lines (injection idiom, mutant beside original, pid named mutant, clean
  controls, live tree, unresolved root refuses), then `root <worktree>`, **`discovered 63`**
  (matches the lead's full-suite discovery count — not an empty-set false green), `ok no test
  mutates a path derived from the live checkout`.
- `python3 .claude/skills/harness/bin/test-run-pool.py` → **exit 0**, `0 failed`, 12 `ok` lines
  including `mutation check covers clean, direct, subprocess, and creation` and `mutation check
  catches dangling and directory symlinks`.

Neither self-test lens (P1/P2) nor the symlink proof (P3) needs re-measurement; I build on them.
**Question the dispatch put to me** — does the matrix demand anything those eight artifacts don't
cover? No: unit+integration is the full floor for this diff and both are now bound to real, green
commands with non-trivial discovery counts. Matrix is satisfied on its own terms.

## Disclosure check

- **M4 (`__pycache__` leg)** — `run_pool.py:32-34,42` skips `__pycache__` dirs and `.pyc` files.
  `test-run-pool.py:74-108` (read directly): cases cover clean/direct-edit/subprocess/created-file
  and the two new symlink legs — **no `__pycache__` leg exists**. The requirement IS documented,
  just not implemented: `plan.yaml:989-992` ("Include one file under a `__pycache__` subdirectory
  … it must NOT be reported, or the check reddens on the interpreter's own byte-code caching").
  So this is a plan-mandated test that shipped missing, not merely an undisclosed limitation —
  **still open**, unchanged from c7 (`qa-c7.md:78`).
- **M5 (content-swap blindness)** — `snapshot()` at `run_pool.py:29-54` records only
  `(st_mode, st_size, st_mtime_ns)`, no content hash; a write that preserves size and resets mtime
  (e.g. via `os.utime`) evades detection entirely. Grepped `run_pool.py`, `test-run-pool.py`,
  `BRIEF.md`, `plan.yaml`, `DECISIONS.md` for any qualifier (`hash|checksum|coincid|utime|content.
  derived`): the only hit is `DECISIONS.md:6587-6603` (DEC-211), which states "snapshots size and
  nanosecond mtime" and then asserts **"A content-derived write inside bin is still caught by the
  runtime snapshot. No broader coverage is claimed than these two mechanisms deliver."** — that is
  an affirmative claim of coverage, not a disclosed limitation, and it is not true for the
  same-size/same-mtime case. **Undisclosed, and the one place that discusses coverage overclaims
  it** — this is worse than silence for a reader relying on DEC-211 as the coverage boundary.

## c7 findings reconciliation (my lens: qa's two; status-only on the other three)

| Finding | c7 severity | Disposition at e64e863e | Evidence |
|---|---|---|---|
| No self-red-proof in `test-suite-independence.py` | HIGH (qa) | **closed** | Six self-test cases now run unconditionally in `main()` (`test-suite-independence.py:170-266`); lead's P1/P2 monkeypatch probes redden all six under three different blinding strategies, none inert. My own run reproduces all six `ok` lines. |
| `test-run-pool.py` missing `__pycache__` leg | MEDIUM (qa) | **open, restated above (M4)** | Direct read of `test-run-pool.py:74-108`: no such case. Underlying `run_pool.py` exclusion behavior is correct (not what's being flagged) — the regression-protection gap is what's still open. |
| Symlink blindness in `snapshot()` | HIGH (code-reviewer/security) | **closed** (not my measurement — lead's P3) | Pre-fix `b86ce66a` copy: dangling/directory symlinks exit 0, no MUTATED. Post-fix: both exit 1 MUTATED, clean control unaffected in both. I did not re-run this myself; taking it as given per dispatch. |
| `code_grade: fail`, blocking records | HIGH (code-reviewer) | **open, unchanged direction is worse** (not my measurement — lead) | Lead: 7 FAIL records at `8e7f56dc`, 9 at `e64e863e` — the fix added two grade-1/2 records rather than reducing the count. Outside my lens (static complexity grading is not a test-matrix kind); flagging for the panel's code-reviewer to own. |
| Same-size/same-mtime content-swap blind spot | MEDIUM (security) | **open, restated above (M5)** — and now with an overclaim finding | See disclosure check. |

## SC evidence pointers (unchanged targets, re-confirmed green)

- SC-04: `test-suite-independence.py` unit run above, `PASS test-suite-independence.py` implied by
  exit 0 (targeted run doesn't print the runner's own PASS line; `--kind unit` does per lead's
  full-suite run).
- SC-10 (mutation-check correctness): `test-run-pool.py` case `mutation check catches dangling and
  directory symlinks`, exit 0, confirms the symlink fix without re-deriving P3.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Matrix gate satisfied (unit+integration, both green with real discovery counts); one c7 MEDIUM still open (__pycache__ leg missing) and one new disclosure finding (DEC-211 overclaims content-swap coverage) — neither blocks the matrix, both are findings for the panel."
  suite: pass
  failures: 0
  matrix_ok: true
  severity_max: medium
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 1 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 1 }
    - { kind: component, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: ui, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: eval, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: typecheck, state: not_applicable, cmd: null, named_tests: 0 }
  coverage_gaps:
    - "test-run-pool.py has no __pycache__-exclusion leg (plan.yaml:989-992 mandates one); underlying run_pool.py behavior is correct but unpinned — future regression would ship silently"
  sc_evidence:
    - { id: SC-04, test: ".claude/skills/harness/bin/test-suite-independence.py (unit kind, exit 0, discovered 63)" }
    - { id: SC-10, test: ".claude/skills/harness/bin/test-run-pool.py case 'mutation check catches dangling and directory symlinks'" }
  open_questions:
    - { id: Q1, question: "DECISIONS.md:6601-6602 (DEC-211) asserts content-derived writes are 'still caught by the runtime snapshot' without qualifying the same-size/same-mtime case that defeats snapshot() entirely — should this line be corrected or should M5 be closed with a stronger snapshot (e.g. content hash)?", blocking: false }
    - { id: Q2, question: "plan.yaml:989-992 mandates a __pycache__ leg in test-run-pool.py that was never shipped (c7 MEDIUM, still open at e64e863e) — is this deferred deliberately or an oversight to fix now?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/qa-c8.md
```
