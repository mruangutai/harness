# QA gate-only re-run — FEAT-104-strict-digest-schema — pin `6126ac07`

**Verdict: PASS. `matrix_ok: true`.** Independent re-run at the pin (via HEAD `f08aad49`, which
differs from `6126ac07` only in `feature.json`'s `review_sha` — confirmed below) reproduces the
build-phase gate result: full suite green, both active kinds green, no coverage gap that changes the
outcome. Author-nothing dispatch honored: no test, fixture, or source file touched; only this note
written.

## 0. Pin identity

```
git diff --stat 6126ac07 f08aad49
```
→ `feature.json | 2 +-` only (the `review_sha` bump). Every file in the 22-file/56-file-total diff
is byte-identical between the pin and the current checkout, so running the suite here is running it
at the pin.

## 1. Change type and required kinds

`git diff abff2a84 6126ac07` = 56 files (22 code/test/instruction files inside the reviewed set, plus
34 feature-tree records/notes). Task `change_type`s from `plan.yaml`: T-01/T-04/T-05/T-06/T-07/T-08 =
**logic**; T-03/T-09 = **docs**; T-10 = **scaffolding**. No task is `config`, `api`, `cross_module`,
`bugfix`, `frontend`, `feature`, or `ai_behavior`.

`test_matrix` (`.harness/harness.json`): `logic.always: [unit]`; `docs.always: []`;
`scaffolding.always: []`. **The mechanical floor for this diff is `unit` only** — the matrix does not
unconditionally obligate `integration` for a `logic` task. `integration` runs here as qa's own added
requirement (every new SC is written against it), which the verification-rules floor-not-ceiling
principle explicitly permits, not because the matrix compels it.

**Finding (advisory, not gating) — F1, low severity:** T-05 (`run-state-schema.json`, a new closed-key
JSON schema two gate scripts read) is declared `change_type: logic`, not `config`. DEC-212 (confirmed
live by `test-config-shape-matrix.py`, part of this run's own suite) exists precisely to bind "a key's
container type, required-ness, or structural nesting in a config a gate script reads" to the
integration floor after FEAT-41 T-01 shipped a broken state gate on exactly this kind of gap. T-05 fits
that description. Concrete failure scenario this could enable: a future cycle on this same surface
that is *not* accompanied by a qa-added integration requirement (e.g., a hurried follow-up patch
labelled `logic` with a reviewer who takes the matrix's mechanical floor at face value) would see
`unit` alone as sufficient and skip integration, when the changed surface is exactly what DEC-212 was
written to catch. **Does not affect this run's coverage** — integration ran, in full, and binds every
new criterion (see §3). Route: worth a plan-time correction to T-05's `change_type`, not an execution
defect.

## 2. Per-kind results

| kind | required? | runner (`cmd`) | command | exit | verdict |
|---|---|---|---|---|---|
| `unit` | yes (`logic.always`) | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | `0` (36 files) | **satisfied** |
| `integration` | not mechanically required by matrix for `logic`; added by qa, warranted by the diff | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | `0` (70 files) | **satisfied** — every new automated SC (§3) binds here |
| `functional` | no | excluded, DEC-187 | — | — | not applicable |
| `eval` | no | excluded, DEC-187 | — | — | not applicable |
| `component`, `ui`, `typecheck` | no | `cmd: null`, unresolved | — | — | not applicable — no `.ts`/`.tsx`/`e2e/**` file in the diff |
| `omp_session_accessor`, `handoff_comprehension`, `issue_types_live` | no | `locally_run` | — | — | not applicable — diff touches none of these kinds' `detect` surface (`tests/manual/probe-*.py`); no recorded run required |

Full suite (`run-unit-tests.sh` with no `--kind`, 106 files, 73.09s): `FULL_SUITE_EXIT=0`, `ALL
PASSED`. Judged by exit status only, per the dispatch's constraint —
`tests/unit/test-factory-claim-mutation.py`'s own `FAIL ` mutation-proof lines are present in this
run's raw output and are not miscounted as a red signal.

## 3. SC-evidence adequacy (SC-01..SC-16, `verify: automated / evidence: integration` unless noted)

Spot-checked the actual assertions in `tests/integration/test-validate-digest.py` (T-01/T-04/T-08
sections, ~L2860-3300), `tests/integration/test-check-domain.py` (T-06, L17-178), and
`tests/integration/test-check-state.py` (T-07, L14-79) — not just their printed labels.

| SC | bound by a running, could-fail test? | anchor |
|---|---|---|
| SC-01 | yes | `test-check-domain.py` `_undeclared_cases` (schema_version 2 refuses+names key) + `test-validate-digest.py` T-04 3-key case |
| SC-02 | yes | T-04's per-persona loop over `CONTRACT_SOURCES`, full documented field set built from the block, not hand-written |
| SC-03 | yes | `test-check-domain.py` `_undeclared_cases` — accept@v1 / refuse@v2, both directions, key named in stderr |
| SC-04 | yes | `test-check-domain.py` `_evidence_cases` — 3 identifier keys accepted; space-key and nested-key both separately refused |
| SC-05 | yes | T-01's `run_documented_contract_cases`/`_t01_reverse_contract_gaps` sweep over every `CONTRACT_SOURCES` persona; **discrimination demonstrated live**: L2944-2951 pops `DOCUMENTED_OPTIONAL["harness-documentor"]["stale_found"]`, asserts the failure names it, restores it in `finally` |
| SC-06 | yes | T-08 vendored-fixture case: asserts fixture bytes contain `DOCUMENTED_OPTIONAL` and do not contain `undeclared digest key`, then runs the same rogue-key payloads against vendored (exit 0) vs current (exit 2) |
| SC-07 | yes | T-04's 3-key single-message case (`rogue_alpha/beta/gamma` all named in one rejection) |
| SC-08 | yes | same case asserts substrings `PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`, `digest contract is closed` — not merely non-empty |
| SC-09 | yes | dedicated `stop_hook_active` bypass case at L3161-3167, asserts exit 0 with the 3-key payload |
| SC-10 | yes | `run_documented_contract_cases`'s adequacy_notes-omission case (L2906-2912): omitting rejects, empty list validates |
| SC-11 | yes | `test-check-domain.py` `_floor_creation_cases` + `_floor_update_case`: v1/absent/string-"2" creation all refused naming `schema_version floor`; v2 creation accepted; existing-v1 update still accepted |
| SC-12 | **not run — `verify: inspection`**, per dispatch. Not evaluated here. |
| SC-13 | **not run — `verify: uat`**, per dispatch. Not evaluated here. |
| SC-15 | yes | same `_floor_creation_cases`/`_floor_update_case` set as SC-11 — four fixtures, each asserted separately |
| SC-16 | yes | same reverse-direction sweep as SC-05, same live discrimination proof (row temporarily removed, failure names it) |

No SC in this set reads as a presence-only or could-not-fail check: every accept case above has a
paired refuse case naming the specific offending key, and the two discrimination-sensitive criteria
(SC-05/SC-16) are proven by an in-process mutation, not merely asserted.

## 4. BRIEF `## Verification gaps` audit

> "every `automated` criterion above rests on `integration`, which runs" — **HOLDS.** All 13
`verify: automated` SCs (SC-01..02, 03..11, 15, 16) declare `evidence: integration` in the BRIEF text
verbatim; `integration` ran (`INTEGRATION_EXIT=0`) and, per §3, actually binds each one.

> "the null-`cmd` kinds (`functional`, `component`, `ui`, `eval`, `typecheck`) cover surfaces this
feature does not touch, so no criterion routes around a missing runner" — **HOLDS.** The 22-file code
diff is exclusively `.py`/`.sh`/`.json`/`.md`; no `.ts`/`.tsx` and no `e2e/**`/`*.e2e.spec.ts` path
appears, so `component`/`ui`/`typecheck`'s `detect` globs never match this diff, and `functional`/`eval`
are excluded repo-wide by signed `DEC-187` for unrelated reasons. Confirmed by grepping the diff's own
file list, not by re-reading the BRIEF's own claim as ground truth.

## 5. Delta against build-phase (`qa-feat104-matrix.md`, tip `1a66d2cc`)

**No difference in outcome.** That note graded a later tip (`1a66d2cc`) than the pin, itself now
several commits behind the review pin's own history; this run independently re-executed both kinds at
the actual pinned content (§0) rather than re-reading that note. Same conclusion: `unit` + `integration`
both green, `matrix_ok` true, no coverage gap that changes the verdict — with one addition this run
makes explicit that the prior note did not: the matrix's own `logic.always` list requires `unit` only,
not `integration` (§1, F1). That note's phrasing ("Matrix floor... is MET: unit + integration both
satisfied") is not wrong about outcome but reads as if the matrix mechanically obligates both; it does
not, for a `logic` task. This is the same conclusion, with a corrected characterization of *why*
`integration` is present (qa-added, warranted by the diff — not a mechanical floor line item).

## Findings summary

- **F1 (advisory, low)** — T-05's `change_type: logic` label undercounts what the DEC-212 `config`
  predicate was written to catch; no live coverage gap in this run, worth a plan-time relabel. See §1.
- No blocking findings. No coverage gap changes the PASS verdict.

## Files touched

None besides this note.
