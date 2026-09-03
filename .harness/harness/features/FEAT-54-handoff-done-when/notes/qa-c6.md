# QA gate c6 — FEAT-54 handoff Done when — re-grade at pin dd55b357

## BLUF

**PASS.** At `review_sha = dd55b3570c6a20f5ca1da016d6959752bd0ffc74`, the literal SC-04 command
now exits **0** with **478** output lines, **0** lines naming `Done when`, and **0** lines matching
`refus|fail|INV-29` (case-insensitive) — the standing `BUG-1157-approval-overrule` worktree is
confirmed gone (`test -d .claude/worktrees/harness/BUG-1157-approval-overrule` → GONE) and the
INV-29 refusal that failed c5 does not recur. F-04 is closed. F-11 is closed: all three FEAT-54
handoff notes at the pinned bytes cite forward-looking authorities (`plan-task:T-01.verify`,
`brief-sc:SC-04`, `finding:...#F-04`), none an already-satisfied BRIEF approval. The configured
unit/integration matrix is non-vacuous and green (25 and 44 files respectively, 0 `^FAIL ` lines
in either run). All ten automated SC criteria are graded PASS with unchanged evidence pointers
(bytes at the pin are identical to what c5 inspected; only `feature.json`'s `review_sha` field
differs between the pin and the worktree tip — confirmed via `git diff --stat` between the two
commits).

## SC-04 measurement (own, not handed)

Ran literally from `/Users/molchairuangutai/GitHub/harness` (repository root):

```
env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/check-state.sh
```

- **Exit code: 0**
- **Total output lines: 478**
- **`Done when` (case-sensitive) line count: 0**
- **`refus|fail|INV-29` (case-insensitive) line count: 0**
- **Severity distribution:** all 478 lines carry the `note` tag (`grep -oE '^\s*(note|warn|warning|violation|error)\b'` → `478 note`, `0` of every other token).

These numbers match the handed claim exactly, but are my own independent measurement, not a
restatement — I ran the command myself and computed each count from `/tmp/qa_c6_sc04_output.txt`.

**Non-vacuity check (the interesting half of this task).** Exit 0 over an empty discovery set would
be indistinguishable from exit 0 over a clean set, so before crediting the PASS I confirmed the run
was a real board read: `grep -oE '(FEAT|BUG)-[0-9]+-[a-z0-9-]+' | sort -u | wc -l` on the captured
output returns **49 distinct feature/bug IDs cited** (e.g. `FEAT-45-adversarial-plan-panel`,
`BUG-1081-code-grade-enforcement`, `FEAT-51-claude-code-lifecycle-safety`), against **67 feature
directories present on disk** (`find .harness/harness/features -maxdepth 1 -mindepth 1 -type d | wc
-l`). 478 substantive notes spanning 49 named features is not an empty-discovery pass — **the
number I used to rule out vacuity is 49 distinct feature/bug IDs enumerated in the output**, cross-
checked against 67 on-disk feature directories (the gap is expected: not every note names its
subject feature by ID, e.g. INV-23 STATE.md-budget lines repeat the same handful of features
multiple times while INV-32 approval-pending notes span many others).

**F-04 verdict: PASS.** The command is clean end-to-end; the unrelated INV-29 worktree that caused
c5's FAIL is confirmed removed.

## F-11 verdict: PASS

Read the pinned `## Done when` block of all three FEAT-54 handoff notes via `git show dd55b357:<path>`:

- `notes/handoff-plan.md`: `Authority: plan-task:T-01.verify`
- `notes/handoff-build.md`: `Authority: brief-sc:SC-04`
- `notes/handoff-validate.md`: `Authority: brief-sc:SC-04` and `Authority: finding:...review-harness-code-reviewer-c5.md#F-04`

None cites an already-satisfied BRIEF approval as authority for a future action — each names a
plan task, a brief SC, or an open review finding, all of which are the actual forward-looking work
items the Scope line describes. The defect that produced F-11 (citing a satisfied approval as
authority for something not yet done) is absent at this pin.

## Matrix re-run at the pin (worktree checkout, bytes identical to pin per diff-stat)

Change types from `plan.yaml`: T-01/02/03/04/06/07/12 = `logic`; T-05 = `config` (touches config
shape → fires `integration` per DEC-212); T-08/10/11 = `docs`; T-09 = `scaffolding`. Required kinds:
**unit** (logic) and **integration** (config-shape + shared two-gate seam). `gates.qa_gate:
blocking` confirmed in `.harness/harness.json`.

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0;
  `pool: 8 workers, 25 files`; `grep -c '^FAIL '` = **0**.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` —
  exit 0; `pool: 8 workers, 44 files`; `grep -c '^FAIL '` = **0**.
- `python3 tests/unit/test-handoff-done-when.py` — all named assertions `PASS` (last 5 shown:
  resolve-false, symlink-escape ×2, special-file ×2).
- `python3 tests/unit/test-probe-handoff-comprehension.py` — `Ran 7 tests ... OK`.
- `python3 tests/integration/test-check-domain.py` — named `ok` outcomes through the handoff
  boundary/cap cases.
- `python3 tests/integration/test-check-state.py` — named `ok` outcomes including
  `FEAT-54 state caller-mode mutation (real=0, mutant=1)` — the SC-15 production-caller mutant
  (flips the sole `resolve=False` call to `resolve=True`) is discriminating at this pin.
- `python3 tests/integration/test-run-unit-tests-kinds.py` — 5/5 named registration/isolation
  checks `PASS`.

No assertion, import, collection, syntax, load, or discovery failure. `unit: satisfied`,
`integration: satisfied`. **matrix_ok: true.**

## Per-SC verdicts (automated), evidence unchanged from c5 (spot-checked at pin bytes)

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | PASS | `tests/integration/test-check-domain.py:4033-4042` |
| SC-02 | PASS | `tests/integration/test-check-domain.py:4043-4064` |
| SC-03 | PASS | `tests/integration/test-check-domain.py:4067-4085` |
| SC-04 | PASS | own measurement above: exit 0, 478 lines, 0 `Done when`, 0 refus/fail/INV-29 |
| SC-05 | PASS | `tests/integration/test-check-domain.py:4235-4244` |
| SC-06 | PASS | `tests/integration/test-check-domain.py:4138-4190,4216-4232` |
| SC-09 | PASS | `tests/integration/test-run-unit-tests-kinds.py:21-98` |
| SC-12 | PASS | `tests/unit/test-handoff-done-when.py:127-132` |
| SC-13 | PASS | `tests/integration/test-check-domain.py:4086-4091` |
| SC-14 | PASS | `tests/integration/test-check-domain.py:4235-4247; tests/integration/test-check-state.py:2282-2296` |
| SC-15 | PASS | `tests/integration/test-check-state.py:2162-2171,2234-2239,2299-2348` — mutant proof re-observed `real=0, mutant=1` at this run |
| SC-10 | not_run | UAT, out of scope for this gate per dispatch |

SC-07, SC-08, SC-11 are review-time (not `verify: automated`) and are not this gate's evidence —
c5 recorded them PASS by inspection against unchanged pinned bytes; no new byte differs at this pin,
so nothing here contradicts that.

## Findings status carried into this run

CLOSED with evidence in c5, not re-opened (no new evidence surfaced here): F-01, F-02, F-03, F-05,
F-06, F-07, F-08, F-09, F-10, SEC-F-10. Advisory carry-forward, non-gating: SEC-F-08 (med) — raw
repository/model/provider terminal controls remain printable; backlog item owned by harness-dev-ops.

**F-11 and F-04, the two items this run existed to re-grade, are both CLOSED** per the measurements
above.

## Scope limits

Author-nothing audit: no tests, fixtures, or source were written or modified. No formatter, linter,
or project-wide build ran. SC-10 operator UAT and the PM product goal-check were explicitly out of
scope for this dispatch and were not run (SC-10 reported `not_run`).

```yaml
VERDICT: PASS
DIGEST:
  headline: "SC-04 exits 0 (478 lines, 0 Done-when, 0 refus/fail/INV-29) at dd55b357 — BUG-1157 worktree confirmed gone; F-04 and F-11 both close; matrix non-vacuous and green (25 unit / 44 integration files, 0 FAIL)."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 25 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 44 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-domain.py:4033-4042" }
    - { id: SC-02, test: "tests/integration/test-check-domain.py:4043-4064" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py:4067-4085" }
    - { id: SC-04, test: "own literal-command measurement: exit 0, 478 lines, 0 'Done when', 0 refus|fail|INV-29" }
    - { id: SC-05, test: "tests/integration/test-check-domain.py:4235-4244" }
    - { id: SC-06, test: "tests/integration/test-check-domain.py:4138-4190,4216-4232" }
    - { id: SC-09, test: "tests/integration/test-run-unit-tests-kinds.py:21-98" }
    - { id: SC-12, test: "tests/unit/test-handoff-done-when.py:127-132" }
    - { id: SC-13, test: "tests/integration/test-check-domain.py:4086-4091" }
    - { id: SC-14, test: "tests/integration/test-check-domain.py:4235-4247; tests/integration/test-check-state.py:2282-2296" }
    - { id: SC-15, test: "tests/integration/test-check-state.py:2162-2171,2234-2239,2299-2348" }
    - { id: SC-10, test: "not_run (uat, out of scope this dispatch)" }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-c6.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/qa-c6.md
```
