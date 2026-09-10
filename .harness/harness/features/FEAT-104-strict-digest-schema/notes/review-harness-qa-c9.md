# QA gate-only matrix audit — FEAT-104, panel-c9, corrected pin `168f875f`

GATE-ONLY. Author-nothing (DEC-174): no tests, fixtures, or source touched. All commands below are
read-only probes of the diff `origin/main..168f875f` and direct invocations of standing test files
already present at that pin.

## 1. Provenance verification — HOW I verified it

Worktree branch HEAD is `71040f1c`, two commits ahead of the pin, as the dispatch states. I did not
trust that framing; I checked it:

- `git diff 168f875f 71040f1c --stat` → 11 files, all under the feature's own `notes/`,
  `observations/`, `STATE.md`, `feature.json` — zero enforcement/test/schema files touched.
- md5 of every file this audit depends on, pin (`git show 168f875f:<path> | md5`) vs. current
  working tree (`md5 -q <path>`): `check-domain.sh`, `check-state.sh`, `validate-digest.py`,
  `run-state-schema.json`, `test-validate-digest.py`, `test-check-domain.py`, `test-check-state.py`
  — **all SAME**.

Conclusion: the current worktree's enforcement/test files are byte-identical to `168f875f`, so
running commands now exercises exactly the pinned code, and the same-pin evidence note
(`notes/qa-feat104-tip-168f875f.md`, which itself records `git rev-parse HEAD` = `168f875f` at the
moment it ran) is provenance-sound to adopt.

## 2. `matrix_ok` — ADOPTED, not freshly measured

**Stating plainly, per dispatch requirement: `matrix_ok: true` in this note is ADOPTED from the
same-pin evidence note (`notes/qa-feat104-tip-168f875f.md`), not a fresh full-suite run.** I did not
re-run the 106-file canonical suite (out of scope per the dispatch's non-goals). I did independently
spot-verify the two required/qa-added kinds by running their exact standing commands myself (§5) and
got identical pass counts, which corroborates rather than substitutes for the adoption.

## 3. Per-kind audit against `harness.json`'s `test_matrix` (read directly, `harness.json:156-238`)

Full-feature `plan.yaml` task `change_type`s: T-01/T-04/T-05/T-06/T-07/T-08 = `logic`;
T-03/T-09 = `docs`; T-10 = `scaffolding`.

- `logic` → `{"always": ["unit"]}`, **no `when` clause exists for `logic` at all** (confirmed by
  reading `harness.json:156-160` directly — unlike `bugfix`/`config`/`api`/`frontend`/`feature`,
  which all carry a `when` array). Floor: **unit only**.
- `docs` → `{"always": []}`. `scaffolding` → `{"always": []}`. Floor: **none**.
- **Required kind present**: `unit` — satisfied (§5).
- **qa-added, not a floor line**: `integration` — F1/F2/F3 and all three gates' own regression
  tests live under `tests/integration/`; satisfied (§5).
- All other kinds (`functional`, `component`, `ui`, `eval`, `typecheck`, three `locally_run`
  probes) — `not_applicable` against their own `detect` surfaces; the diff touches no `.tsx`, no
  `tests/e2e/**`, and none of the three `locally_run` probes' surfaces
  (`inflight_registry.py` session resolution, handoff contract, issue-type path).

**Advisory, independently re-derived (not merely carried forward):** T-05 touches
`run-state-schema.json` — a JSON schema file two gate scripts (`check-domain.sh`,
`check-state.sh`) read to enforce shape — and is declared `change_type: logic`. DEC-212's
`touches_config_shape` predicate text ("a key's container type, required-ness, or structural
nesting in a config a gate script reads") describes this file almost exactly; had T-05 been typed
`config`, its own matrix row (`config.when: touches_config_shape → integration`) would make
`integration` an **obligated** floor line rather than a qa-added one. **This does not change the
actual gate outcome**: `integration` was run and is satisfied either way (§5). I classify this as a
**low-severity, non-gating classification finding**, not a matrix miss — the substance (integration
coverage exists and passes) is present regardless of which column it is credited under.

## 4. Red-capability — reasoned, not measured (DEC-174 forbids mutation here)

Per O-03: everything in this section is derived by **reading the guard logic and the assertion
code**, not by flipping a mutant and watching it redden. DEC-174's author-nothing constraint applies
even to a disposable-worktree perturbation proof for this dispatch, so I could not do what the F1
witness (11/12→12/12) did. Where the prior cycle already executed that kind of proof, I say so
separately (§5).

- **F1 (`schema_version` downgrade), `check-domain.sh:1760-1779`**: `_version_decreased` is a real
  conditional — `not int or bool or version < prior_version`, gated on `_prior_is_strict` (prior
  version is an actual int `>= 2`, not a bool). The test (`test-check-domain.py:152-159`) writes a
  genuine existing-checkpoint update from `schema_version: 2` → `schema_version: 1` and asserts
  **both** `returncode == 2` **and** `"schema_version downgrade" in stderr`. A regression that
  accepted the downgrade (exit 0) or refused with unrelated wording reddens this. Not vacuous.
- **F3 (undeclared-key message), `test-validate-digest.py:3130-3146`**: asserts `len(errors) == 1`
  for three rogue keys (catches message-splitting regressions) **and** per-token presence of all
  eight tokens including the literal file name `"validate-digest.py"`. A regression narrowing the
  message to name only the symbols and drop the file token — the prior SC-08 gap exactly — reddens
  this specific check. Not vacuous.
- **`run-state-schema.json` guards, both gates**:
  - `check-domain.sh:1618-1667` (write-time) and `check-state.sh:1486-1535` (at-rest sweep) both
    load the schema fresh, build a `jsonschema.Draft202012Validator`, and **wrap the whole block in
    `try/except Exception`**. Read both `except` branches directly: both **append a denial/failure
    message and treat the write as bad** (`out.append(...); return out` in check-domain.sh;
    `bad.append(...)` in check-state.sh) — this is **fail-closed**, not fail-open, so a
    schema-file-corruption or `jsonschema`-import failure blocks rather than silently passing.
  - `test-check-domain.py:_declared_shape_case` (`tests/integration/test-check-domain.py:114-124`)
    compares the schema file's own key set (`json.load(run-state-schema.json)`) against `DECLARED`,
    an **independently hand-written literal set at the top of the test file** (line 14). This is the
    one place the dispatch specifically flagged as "easiest to assert vacuously" (a test deriving
    its expectation from the same schema file it is checking would be tautological) — confirmed
    this is **not** that: `DECLARED` is authored separately from the schema, so a schema edit that
    silently drops or adds a key reddens this case.
  - Two independent legs of the "offending key" logic are each covered by their own case in
    `test-check-domain.py:_evidence_cases` (lines 91-111): a space in an evidence key name (name-
    pattern leg) and a nested-mapping evidence value (dict-value leg) are each their own assertion,
    not folded into one aggregate check (Expertise P-06 concern satisfied).

## 5. F1 / F3 witnesses — independently confirmed by direct execution

Ran both test files myself, in the worktree, against the pin-identical tree (§1):

- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` → exit 0, **12/12**
  T-06 cases, including `ok  schema_version floor refuses a version-2 checkpoint downgrade`.
  **Confirmed the post-fix 12/12 state myself.** I did not re-derive the claimed pre-fix 11/12
  state (that would require reverting the fix, prohibited by DEC-174); that half rests on the prior
  cycle's own executed record. The assertion's structural strength (§4) I verified directly, myself.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py` → exit 0, **34/34**
  T-04 cases, **55/55** T-01, **10/10** T-08, `ALL PASSED`. Confirmed the T-04 three-key assertion
  code myself (§4) — structurally sound, not merely trusted from the evidence note's transcription.

## 6. F2 reassessment — independently traced, decline confirmed sound

Traced the actual enforcement topology myself rather than accepting the evidence note's claim:

- `grep -c '\.validate('` across `check-domain.sh` and `check-state.sh`: **zero** calls in
  `check-domain.sh` — Write/Edit-tool payloads are never passed through `validate-digest.py`'s
  digest schema at all; that gate governs `state.yaml` shape only, not digest content.
- `check-state.sh:1590` — the **at-rest sweep** — calls `_vd_mod.validate("lead", _dtext)`
  unconditionally. This is where F2's raw-persona hole lives, and it is a **historical-scan of
  existing files on disk**, not a gate on a new write.
- `validate-digest.py:1990-1993` — the **SubagentStop hook**, the actual return-time gate for every
  new return — calls `validate(agent, text, ...)` where `agent` is the real raw persona read from
  the hook's own tool input (not a hardcoded `"lead"`). Read directly at lines 1959-1998: no
  persona substitution anywhere on this path.

**Conclusion: no coverage hole for a NEW return.** Every new return is validated under its true raw
persona at the stop-hook, unaffected by F2's decline. The generic-`lead` exemption the decline
preserves is reachable **only** through `check-state.sh`'s at-rest sweep over already-written files
— exactly REQ-08/SC-12's scope ("historical run digests... remain readable... enforcement binds NEW
returns and NEW writes only"). No test in this diff passes *because of* the declined behavior (no
test exercises this path at all — confirmed by reading `test-check-state.py` in full: zero
`digest`/`validate(`/`lead` references, 3/3 cases entirely about step keys). The coverage gap the
evidence note names in §8 (nothing pins `validate("lead", …)`'s exemption behavior, so a future
narrowing would silently break `2026-09-09-02-qa-gate-validator/digest.md`) is real and I confirm
it, but it is a gap in regression protection for a **declined, evidenced, non-gating** choice — not
a live defect, and not a hole a new return can fall into today.

## Findings

| id | severity | scenario | gates? |
|---|---|---|---|
| F-QA-1 | low | T-05 (`run-state-schema.json`) is typed `change_type: logic` but its own file plausibly meets DEC-212's `touches_config_shape` predicate under the `config` row; misclassification would make `integration` an obligated floor line instead of qa-added. Concrete scenario: a future task editing `run-state-schema.json` under `change_type: logic` again would not mechanically obligate `integration`, relying on qa's judgement rather than the matrix to add it. | non-gating (integration coverage exists and passes regardless; §3) |
| F-QA-2 (= evidence note's coverage gap, independently confirmed) | med | `check-state.sh:1590`'s `validate("lead", …)` exemption for the at-rest sweep has zero test coverage able to report RED. Concrete scenario: a future edit narrowing or removing `validate-digest.py`'s `raw_persona != "lead"` guard, or changing `check-state.sh` to pass a run's real host persona, would silently break `2026-09-09-02-qa-gate-validator/digest.md` and every future lead digest shaped like it, with no standing test catching the regression. | non-gating (declined-with-evidence per operator ruling, REQ-08/SC-12 compliant as designed; this is a residual regression-protection gap on a deliberate choice, not a defect) |

`severity_max`: **med** (F-QA-2).

## VERDICT

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok=true, ADOPTED from same-pin evidence (provenance independently verified by md5 across 168f875f vs. current HEAD 71040f1c — bookkeeping-only delta); logic.always=[unit] is the whole floor, satisfied, integration is qa-added and satisfied (re-ran both myself: 12/12 T-06, 34/34+55/55+10/10 T-04/T-01/T-08); F1 and F3 witnesses independently confirmed by direct execution and by reading the discriminating assertion code; run-state-schema.json guards traced and shown fail-closed with a non-tautological DECLARED cross-check (reasoned, not mutation-proven — DEC-174 forbids mutation in this dispatch); F2 decline independently re-traced through the stop-hook (validates with the REAL raw persona for every new return) and confirmed to leave no coverage hole for new returns, only a residual non-gating regression-protection gap on the at-rest sweep's deliberate historical-compat exemption."
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 36 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 70 }
    - { kind: functional, state: not_applicable, cmd: none }
    - { kind: component, state: not_applicable, cmd: none }
    - { kind: ui, state: not_applicable, cmd: none }
    - { kind: eval, state: not_applicable, cmd: none }
    - { kind: typecheck, state: not_applicable, cmd: none }
    - { kind: omp_session_accessor, state: not_applicable, cmd: none }
    - { kind: handoff_comprehension, state: not_applicable, cmd: none }
    - { kind: issue_types_live, state: not_applicable, cmd: none }
  findings:
    - { id: F-QA-1, severity: low, gates: false, scenario: "T-05 (run-state-schema.json) typed change_type: logic though it plausibly meets DEC-212's touches_config_shape (config row); a future task like it would not be mechanically obligated to add integration by the matrix itself." }
    - { id: F-QA-2, severity: med, gates: false, scenario: "check-state.sh:1590's validate('lead', ...) at-rest exemption has zero test able to report RED; a future narrowing of the raw_persona != 'lead' guard, or a change passing the real host persona, would silently break 2026-09-09-02-qa-gate-validator/digest.md and similar lead digests with no standing test catching it. Declined-with-evidence per operator ruling; non-gating." }
  severity_max: med
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-qa-c9.md
```
