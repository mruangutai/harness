# QA gate — FEAT-104 panel c11, pin `984bd26b`

**BLUF: matrix_ok = true.** Unit and integration both satisfied (unit/integration suite totals
ADOPTED from run 15's same-pin report; the focused `test-check-domain.py` file and the specific
PF-C10-01-discriminating case MEASURED directly by me, GREEN). PF-C10-01 closure is confirmed:
the missing-required-step-key case exists exactly as specified, is EXECUTABLE, and passes. The
fail-open shape the panel exists to grade is CONFIRMED closed by direct schema+code reading (a
reasoned proof, not a mutation sweep). Q14 (wrong-advice message on a type-wrong *declared* key)
reproduces live today with no test guarding it — carried at **low**, present-tense, undisputed
correctness of the denial itself. Q15 stays latent/unreachable — no schema keyword exists today
that would trigger it, so nothing can redden.

## Change type & required kinds

- Full reviewed diff `origin/main..984bd26b`: 18 files, +3203/-19 (confirmed via
  `git diff --stat`, MEASURED). Per `plan.yaml`, tasks are `logic` (T-01,04,05,06,07,08 —
  `always: [unit]`), `docs` (T-03,09 — `always: []`), `scaffolding` (T-10 — `always: []`). No task
  is `cross_module` or `config`. **Plan-level floor: unit only.**
- The c11 fix delta specifically (`790023f0..984bd26b`, exactly 2 files: `check-domain.sh`
  +26/-8, `test-check-domain.py` +6/-0 — MEASURED via `git diff --numstat`) is `bugfix`:
  `touches_runtime_code` fires (→ unit required); `fix_confined_to_tests_and_contract_docs` does
  **not** fire, since the runtime script itself changed, not just tests/docs — so that leg does
  not obligate integration by the letter of the matrix.
- **I ADD integration above the plan-level floor** (DEC-174 "may add what the diff clearly
  warrants, never drop below"): the fix's own regression case lives in
  `tests/integration/test-check-domain.py`, and it is the only test exercising the discriminating
  scenario. Required kinds for this gate: **unit, integration**.

## Per-kind results

| kind | state | result | provenance |
|---|---|---|---|
| unit | satisfied | exit 0, 36 files | **ADOPTED** — run 15's same-pin report; not re-run by me |
| integration (suite) | satisfied | exit 0, 70 files | **ADOPTED** — run 15's same-pin report; matches the `790023f0`/`168f875f` baseline count, so discovery did not collapse |
| integration (focused) | satisfied | `tests/integration/test-check-domain.py`: 13/13, exit 0 | **MEASURED** — I ran `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` directly just now |

No `^FAIL ` census was needed for my own run (all 13 cases in the focused file printed `ok`,
and the file's own tally line read `13/13 ... passed` / `ALL PASSED`, exit 0). I did not run the
full suites myself this cycle, so the "reprinted FAIL lines inside a passing mutation proof"
trap (`test-factory-claim-mutation.py`) did not arise in what I measured; noting it for whoever
re-runs the adopted suite-level figures.

## PF-C10-01 closure — case-level, MEASURED independently

`_undeclared_cases()` in `tests/integration/test-check-domain.py:76-96` (read directly, current
pin) contains case `"schema_version 2 names a missing required step key"`, fixture
`_state("2").replace("    status: pending\n", "")` exactly as specified, asserting
`returncode == 2 and "missing required step key" in stderr and "status" in stderr`. I reproduced
this fixture standalone (outside the test file, via `check_domain_support.fire`/`fixture`) and
confirmed:
```
RC: 2
STDERR: check-domain: BLOCKED — …: missing required step key.
  missing key(s): 'status'. Required step fields are declared in …
```
GREEN at `984bd26b`, **MEASURED by me**, not adopted. I did not re-measure the RED-at-`790023f0`
half of the witness pair the previous cycle reported (12/13) — that half is **CLAIM, unverified
by me this cycle**, inherited from run 15.

## Fail-open re-derivation — CONFIRMED, by direct schema + code reading (reasoned, not mutated)

Read `run-state-schema.json`'s step subschema directly:
`sorted(step.keys()) == ['additionalProperties', 'properties', 'required', 'type']` — exactly the
three keywords the batch context claims sit at the step object's own level (plus `properties`,
which routes into named-field paths, not an empty path). MEASURED, not adopted.

Read `shape_problems` (`check-domain.sh:1630-1677`) directly:
- Whole-step `type` failure (`_step` not a dict) is *always* caught by the manual
  `_offending.add("<step>")` at line 1635, **outside** the `if _schema_errors:` block — reached
  unconditionally per step, independent of what jsonschema reports.
- `additionalProperties` failure is *always* caught by the manual `_offending.update(set(_step) -
  _declared)` at line 1637, likewise outside the schema-errors block.
- `required` failure is the only step-level keyword whose only path to the denial message runs
  *through* `_schema_errors`, and that branch now explicitly buckets it into `_missing_required`
  (lines 1650-1656) and `continue`s before ever reaching the `_path` fallback — so it can no
  longer fall through to an empty-key message.

Net: every step-level keyword the schema declares today is caught by a code path that names a
key. **No schema error with an empty `error.path` can currently reach `out` unlabeled.** I
independently probed both discriminating messages live (below) and confirmed they never
co-occur or cross-contaminate — each case's assertion substring is uniquely satisfied by its own
message only, so the fail-open is closed and the fix is not merely coincidentally green.

```
missing-required case stderr:  "… missing required step key.\n  missing key(s): 'status'. …"
undeclared-key case stderr:    "… undeclared step key or evidence shape.\n  offending key(s): 'rogue_step_key'. …"
```
Both MEASURED directly by me this cycle, not adopted from c10.

## SC-08 seam grading

- **Step seam** (`test-check-domain.py`, `_undeclared_cases`, now spanning what were lines
  79-89 before this cycle's +6 lines shifted them): MET, EXECUTABLE. A second head string
  (`"missing required step key."`) now lives in the same `_undeclared_cases` block alongside the
  original `"undeclared step key or evidence shape."`. I measured both cases' stderr directly
  (above) and confirmed the two messages never appear in the same response — the `required`
  branch `continue`s before falling into `_offending`, and the manual `additionalProperties`/type
  checks that feed `_offending` never fire for a pure missing-field case. **The step seam's
  discriminating clause (`"undeclared step key" in strict.stderr`) remains uniquely pinned** —
  it is not satisfiable by the new message, and the new message's own clause
  (`"missing required step key" in missing.stderr`) is likewise not satisfiable by the old one.
- **Digest seam** (`test-validate-digest.py:3130-3146`, `_t04_three_key_failures`): MET,
  EXECUTABLE — untouched by this cycle's 2-file delta (confirmed: `validate-digest.py` and its
  test are not in `790023f0..984bd26b`). Single head (`"undeclared digest key"`), no analogous
  second-head risk in this subsystem at this pin.

## Q14 / Q15 — present-tense severity, MEASURED where possible

- **Q14 — reachable today, severity `low`.** I built a standalone fixture (schema_version 2,
  declared key `cycles: not-an-int`) and fired it directly against `check-domain.sh` (bypassing
  the test file entirely, per DEC-174 — source/tests untouched). Result: `returncode == 2`,
  message head `"undeclared step key or evidence shape."`, `offending key(s): 'cycles'` — wrong
  remedy (tells the author to move a *declared* key under `evidence`) for a type failure on a
  declared field. **No test in the suite covers this scenario** — I grepped `_declared_shape_case`
  and `_evidence_cases`; neither exercises a type-wrong value on a declared key, so nothing can
  redden it today, confirming the coverage gap the batch context named. Severity is `low` on the
  merits: the write is still correctly refused (fail-closed holds), only the operator-facing
  remedy text is misleading — a UX defect, not a soundness one.
- **Q15 — present-tense unreachable, no severity to assign as a live defect.** Confirmed via the
  same schema read above: the step subschema declares no `minProperties`, `dependentRequired`, or
  any other keyword that could produce an empty `error.path` outside `type`/`additionalProperties`/
  `required` — all three of which are now covered. No test can redden this today because no
  triggering schema keyword exists. Rated as a latent design-risk note only, per the batch
  context's instruction not to treat it as a present defect.

## Prior findings — disposition (qa lens)

- **Q9** (generic-`lead` archive exemption at `validate-digest.py:1407`, no reddenable test) —
  **carried unchanged**. `validate-digest.py` is untouched in `790023f0..984bd26b` (confirmed by
  `git diff --stat`); nothing in this cycle bears on it.
- **CF-2** (severity contested: qa med / code info / c9 lead low) — **carried unchanged** at my
  prior `med` rating; its subject file is outside the 2-file c11 delta, so no new evidence changes
  my grading this cycle.
- **F1/F2/F3** — **carried as previously disposed**: F1/F3 stay CLOSED (closed by execution at
  c10, nothing in this cycle reopens them). F2's DECLINED disposition **stands** — I confirm
  `check-state.sh` is not in the `790023f0..984bd26b` delta (2 files only, neither is
  `check-state.sh`), so the topology F2 was declined against is unchanged.
- **Standing residual — "schema guards argued fail-closed, not mutation-proven"** — **partially
  strengthened, not closed**. For the specific step-schema guard in `check-domain.sh` touched
  this cycle, I directly measured three live discriminating cases (missing-required, undeclared,
  and my own Q14 declared-type probe) against the real binary — genuine execution evidence, not a
  self-report. I did **not** extend this to `validate-digest.py`'s or `check-state.sh`'s guards
  this cycle (both untouched by the c11 delta), so the residual **carries** for those two files
  unchanged.

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok=true; PF-C10-01 closure MEASURED green and the fail-open shape CONFIRMED closed by direct schema+code reading; Q14 reproduces live and is uncovered (carried low), Q15 stays unreachable"
  suite: pass
  failures: 0
  matrix_ok: true
  change_type: "mixed — plan.yaml tasks mostly `logic` (floor: unit); c11's own 2-file fix delta is `bugfix` (touches_runtime_code fires unit; fix_confined_to_tests_and_contract_docs does not fire integration by the letter, but integration is ADDED as clearly warranted since the regression case lives there)"
  required_kinds: [unit, integration]
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 36, provenance: ADOPTED, source: "run 15 same-pin report" }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 70, provenance: ADOPTED, source: "run 15 same-pin report" }
    - { kind: integration_focused, state: satisfied, cmd: "python3 tests/integration/test-check-domain.py", named_tests: 13, provenance: MEASURED, source: "run just now, env -u HARNESS_AGENT_TYPE, exit 0" }
  coverage_gaps: ["Q14: type-wrong value on a declared step key routes into the wrong remedy message; no test asserts correct behavior for this case"]
  sc_evidence:
    - { id: "SC-08 (step seam)", test: "tests/integration/test-check-domain.py:76-96 (_undeclared_cases)" }
    - { id: "SC-08 (digest seam)", test: "tests/integration/test-validate-digest.py:3130-3146 (_t04_three_key_failures)" }
    - { id: "PF-C10-01 closure", test: "tests/integration/test-check-domain.py: case 'schema_version 2 names a missing required step key'" }
  findings:
    - { id: Q14, area: code, severity: low, status: reproduced-live-uncovered, note: "type-wrong value on a declared step key (e.g. cycles) is denied correctly but the message tells the author to move it under `evidence`, which is wrong advice for a declared key; no test covers this case" }
    - { id: Q15, area: code, severity: info, status: latent-unreachable, note: "no schema keyword exists today (no minProperties/dependentRequired at step level) that would fall through the emitter's validator-name branch; cannot redden any test until one is added" }
    - { id: Q9, area: code, severity: unrated-by-me, status: carried-unchanged, note: "validate-digest.py untouched this cycle" }
    - { id: CF-2, area: contested, severity: med, status: carried-unchanged, note: "subject file outside the 2-file c11 delta" }
    - { id: F1, area: code, severity: n/a, status: closed, note: "closed by execution at c10" }
    - { id: F2, area: code, severity: n/a, status: declined-stands, note: "check-state.sh topology confirmed unchanged this cycle" }
    - { id: F3, area: code, severity: n/a, status: closed, note: "closed by execution at c10" }
    - { id: "residual: schema guards fail-closed, not mutation-proven", area: code, severity: info, status: carried-partial, note: "strengthened for check-domain.sh's step guard (3 live probes this cycle); still unproven for validate-digest.py and check-state.sh guards, both untouched this cycle" }
  severity_max: med
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-qa-c11.md"
```
