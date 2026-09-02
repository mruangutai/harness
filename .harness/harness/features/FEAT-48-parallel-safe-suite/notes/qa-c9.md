# QA test-matrix gate — FEAT-48-parallel-safe-suite — validate c9, pinned `27f8105b`

BLUF: **matrix_ok: true, suite: pass.** Floor (`unit + integration`, from `bugfix`/`logic`/`cross_module`
task change_types against `harness.json`'s matrix) is fully satisfied — both kinds bound to real,
active, non-null `cmd`s, both run green by me at the pin. Every case the dispatch named for
mutation-proof (`case_cache_exclusion` both legs, `case_symlinks`, all six `test-suite-independence.py`
self-tests) **discriminates under a mutation I built and ran myself**, none never-red. c8's M4
(`__pycache__` leg missing) and M5 (DEC-211 overclaim) are both closed, confirmed by direct grep/read,
not inherited. One open finding, not a must_fix: **T-06's own `verify:` block still exits 1**, and the
wrong artifact is the verify clause, not the carrier note — detail in §6.

## 1. Phase 1 (pre-code) — expected coverage from BRIEF/plan alone

Before opening any implementation file: REQ-01 needs proof no test writes/replaces/deletes a live
shared path (isolated-copy tests for the historical sites); REQ-02 needs a static invariant that
flags injection/beside-original/PID-named idioms and refuses an unresolved root; REQ-03 needs
concurrent execution where one file's non-zero exit fails the run; REQ-04 needs per-file-attributed
output; REQ-05 needs a worker-count rule reported with wall time; REQ-06 needs the existing
`--kind`/`--check-kinds`/exit-code contract preserved; REQ-07 needs an order-independence proof;
REQ-08 needs a `DECISIONS.md` entry. All eight are traced to a task (T-01..T-06) and each showed up
with a corresponding case in Phase 2 — no Phase-1 expectation surfaced with zero test.

## 2. Change types and the matrix floor

`plan.yaml`: T-01 `bugfix`, T-02 `bugfix`, T-03 `logic`, T-04 `cross_module`, T-05 `docs`, T-06
`cross_module`. `harness.json` `test_matrix`: `bugfix.always=[unit]`, `logic.always=[unit]`,
`cross_module.always=[unit,integration]`, `docs.always=[]`. Union floor: **unit + integration**.
BRIEF's own `## Verification gaps` note that `component`/`ui`/`eval`/`typecheck` have `cmd: null`
and touch no surface this diff changes (bash/Python gate scripts under `bin/`) — confirmed: none of
their `detect` globs match `.claude/skills/harness/bin/**`.

| kind | binding | cmd | status | state |
|---|---|---|---|---|
| unit | `test-suite-independence.py` in `UNIT_SCRIPTS`, unit `detect` glob matches `bin/test-*.py` | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | active | **satisfied** |
| integration | `test-run-pool.py` in `INTEGRATION_SCRIPTS` and in `test_kinds.integration.detect` explicitly | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | active | **satisfied** |
| component/ui/eval/typecheck | no detect-glob match on this diff's surface | `cmd: null` | unresolved | soft skip (unchanged from c8) |

## 3. My own runs, `env -u HARNESS_AGENT_TYPE`, at the pin

- `--check-kinds` → exit 0, agreement line, zero PASS/FAIL lines.
- `--kind nope` → exit 2.
- `--kind unit` → **exit 0, 33 files, 8 workers, 16.18s wall**, zero FAIL/MUTATED,
  `PASS test-suite-independence.py` present (`/tmp/qa_c9_unit.log`).
- `--kind all` → **exit 0, 63 files, 8 workers, 48.34s wall**, zero FAIL/MUTATED lines (grep-counted:
  0 and 0) (`/tmp/qa_c9_all.log`). Reproduces `notes/validate-evidence-c9.md`'s 63/8/48.29s within
  measurement noise — figure **does reproduce**.

## 4. Reachability-and-discrimination audit (mutations in `/tmp`, checkout never edited)

Built `/tmp/feat48_mutants/run_pool_{a,b,c}.py` from the live `run_pool.py` and drove
`test-run-pool.py`'s own case functions (imported as a module, `POOL` monkeypatched) against each:

| case | mutation applied | result |
|---|---|---|
| `case_cache_exclusion`, **create leg** (`__pycache__/x.pyc` fresh) | A: delete the `if name == "__pycache__": continue` skip | **reddens** — `MUTATED __pycache__/x.pyc` appears |
| `case_cache_exclusion`, **loose-.pyc leg** | B: restore the old over-wide skip (any `*.pyc` anywhere) | **reddens** — expected `MUTATED loose.pyc` silently disappears |
| `case_symlinks` (dangling + directory legs) | C: delete the `os.path.islink` branch, always descend | **reddens** — both `MUTATED dangling` and `MUTATED linked-dir` disappear |

Note on the "rewritten vs newly-created `__pycache__` entry" framing in the dispatch:
`_snapshot_directory` (`run_pool.py:37-49`) prunes `__pycache__` **directories by name** before the
walk descends, in both the before- and after-snapshot passes — so a rewritten pre-existing entry and
a newly-created one take the identical code path (the directory is never walked either time) and
cannot be discriminated from each other by any input. `test-run-pool.py`'s single "create" leg is
therefore sufficient to prove the exclusion mechanism; a second "rewrite" leg would exercise nothing
the create leg doesn't already. `[INFERENCE]` confirmed structurally by reading `_snapshot_directory`
directly, not merely asserted.

`test-suite-independence.py`'s six self-tests, probed by monkeypatching `scan_file` and
`resolve_scan_root` in an imported copy of the module (`/tmp/feat48_qa_probe_independence.py`):

| self-test | mutation | result |
|---|---|---|
| 0-injection idiom | `scan_file` blinded (`lambda _: []`) | **reddens** |
| 1-mutant beside original | `scan_file` blinded | **reddens** |
| 2-pid named mutant | `scan_file` blinded | **reddens** |
| clean controls | `scan_file` made over-eager (flags every file at line 1) | **reddens** |
| live tree, independent root and discovered floor | over-eager `scan_file` **and independently** a patched `resolve_scan_root` that never refuses | **reddens both ways** |
| unresolved root refuses | `resolve_scan_root` patched to always return `HERE` | **reddens** |

**Never-red cases: none.** All six turn red under an appropriate fault, none survive both probes
unchanged, and the baseline (unmutated) run reproduces the six `ok` lines plus `discovered 63`. This
independently re-derives `notes/validate-evidence-c9.md` §4's table by my own mutation rather than
trusting it.

## 5. Disclosure re-check (my own c8 findings)

- **M4 (`__pycache__` leg)** — closed. §4 above proves both legs exist and discriminate; this is
  stronger than c8's "requirement documented but code path unexercised" finding.
- **M5 (DEC-211 overclaim)** — closed, confirmed by direct grep: `DECISIONS.md:6601-6604` now reads
  "a same-size rewrite that restores the original mtime is outside this metadata snapshot's
  coverage; content hashing is deferred rather than falsely claimed. No broader coverage is
  claimed." — matches `_record`'s `(st_mode, st_size, st_mtime_ns)` tuple exactly; no residual
  overclaim.

## 6. T-06's own `verify:` — my disposition

Reproduced independently (`/tmp/feat48_t06_verify_qa.py`, verbatim copy of the block): **exit 1**,
same single failing clause reported in `notes/validate-evidence-c9.md`: `post == ["0"]` sees
`['0', '0']`. Root cause, read directly in `notes/measurements-parallel-suite.md`: T-06's own intent
(`plan.yaml:1097-1102`) *mandates* the fenced verbatim command output (which itself prints
`post-fix broken reads 0`, line 15) **and** a separate "Summary lines, exactly" section repeating the
identical line (line 20) — two occurrences by design, not by carrier error. The verify's regex
(`re.findall` over the whole file, no fenced-block exclusion) inevitably sees both, and
`post == ["0"]` is a strict single-element-list equality where every other duplicated field in the
same block (`ctrl`, `wall`) is checked leniently (`ctrl and int(ctrl[0]) > 0`, not count-based; `runs`
even uses `set(runs) == {"0"}` for exactly this reason).

**Ruling: backlog, not must_fix for this feature.** Reasons: (1) this is a one-shot,
`main-session-direct`-task build-time verify, never re-run by CI or by `run-unit-tests.sh` — a red
here carries no live gate risk (matches this repo's own Expertise G-01: no standing regression
protection re-runs a task verify); (2) SC-02/SC-05/SC-06, the only SCs this note supports, are all
`verify: inspection` — pm and I both grade their content by direct read, not by this script's exit
code, and the content is correct (control `4968 > 0`, ten runs all `exit 0`, `post-fix broken reads
0` genuinely zero, `wall 42.40 ≤ 120`); (3) the defect is a pure regex-strictness bug that contradicts
the verify author's own established pattern two lines away (`set(runs) == {"0"}`).

**Wrong artifact: the verify clause in `plan.yaml`, not `measurements-parallel-suite.md`.** The note
complies exactly with T-06's own intent, which requires the duplication. **Minimal remedy** (not
applied, per constraint): change `post == ["0"]` to `set(post) == {"0"}`, mirroring the existing
`runs` check three lines above it in the same block — a one-token diff, zero content or intent
change.

## 7. Coverage gaps

None found against the Phase-1 list in §1. All eight REQs trace to a passing, discriminating test.

## SC evidence pointers

- SC-01: `test-check-domain.py` exit 0, live `feature_schema.py` byte/mtime identical
  (`notes/validate-evidence-c9.md` §6, re-run by me via `--kind all`, zero FAIL/MUTATED).
- SC-04: `PASS test-suite-independence.py` in `/tmp/qa_c9_unit.log`.
- SC-07: `--check-kinds` exit 0 / zero lines, `--kind nope` exit 2 (§3, mine).
- SC-08: `test-run-pool.py case_completion_order`, unexercised by mutation here (not in dispatch
  scope) but exit 0 confirmed by the passing `--kind all`/`--kind integration` runs.
- SC-10: `test-run-pool.py case_file_mutations`, `case_symlinks`, `case_cache_exclusion` — all three
  independently mutation-proven in §4.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Matrix gate satisfied (unit+integration, both green, 63/8/48.34s reproduces the pin); every dispatched mutation-proof case discriminates under a fault I built myself; c8's M4 and M5 are closed on direct evidence; the one open item — T-06's verify exits 1 on a duplicate-line regex bug — is ruled backlog, not must_fix, and points at the verify clause, not the note."
  suite: pass
  failures: 0
  matrix_ok: true
  severity_max: low
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 33 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 30 }
    - { kind: component, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: ui, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: eval, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: typecheck, state: not_applicable, cmd: null, named_tests: 0 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: ".claude/skills/harness/bin/test-check-domain.py (--kind all run, exit 0, zero FAIL/MUTATED)" }
    - { id: SC-04, test: ".claude/skills/harness/bin/test-suite-independence.py (--kind unit run, PASS line present)" }
    - { id: SC-07, test: "run-unit-tests.sh --check-kinds (exit 0) and --kind nope (exit 2), run directly by me" }
    - { id: SC-08, test: ".claude/skills/harness/bin/test-run-pool.py case_completion_order (exit 0 via full suite run)" }
    - { id: SC-10, test: ".claude/skills/harness/bin/test-run-pool.py case_file_mutations/case_symlinks/case_cache_exclusion, each independently mutation-proven in qa-c9.md §4" }
  open_questions:
    - { id: Q1, question: "T-06's verify: block (plan.yaml ~line 1068) asserts post == [\"0\"] as an exact single-element list, but its own intent mandates the summary line appear twice (once in the required fenced verbatim block, once in the required standalone summary section) — every sibling duplicated field in the same block (ctrl, wall) is checked leniently or via set() except this one. Recommend set(post) == {\"0\"} for symmetry with the adjacent set(runs) == {\"0\"} check. Not applied per validate-mission constraint.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/qa-c9.md
```
