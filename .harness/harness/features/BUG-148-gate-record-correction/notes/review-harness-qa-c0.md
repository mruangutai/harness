# QA gate audit — BUG-148-gate-record-correction — review cycle 0, pin `87e6033`

## BLUF

`matrix_ok: true`. Required-kind set for `docs` is `[]` (`test_matrix.docs.always` is empty and
no `when` predicate fires — the only conditional in the matrix, `config.touches_config_shape`,
binds `change_type: config`, not `docs`; `harness.json` itself is untouched by this diff). The
matrix is satisfied by construction: there is no floor to miss. SC-04's integration evidence is
**AUDITED, not executed** by me — I did not run `run-unit-tests.sh` or any suite this cycle. My own
judgement, below: the required-kind set of `[]` is correct, and the known red-capability gap on
one of SC-04's two named tests is a **backlog row, not a ship-blocking gate**.

## 1. Change-type verification (my own check against the pinned diff)

`git diff --stat 41c16c7..87e6033` touches exactly three product paths, all confirmed:
- `.harness/harness/docs/DECISIONS.md` — prose record, DEC-174 region only
- `.harness/harness/docs/DECISIONS-INDEX.md` — generated index, no hand content
- `.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` — prose record

None is under `tests/**`, `src/**`, or any runtime-code path. Both `plan.yaml` tasks (T-01, T-02)
declare `change_type: docs`, and this independently confirms it — the label is not being used to
dodge a required kind. `test_matrix.docs.always` in `.harness/harness.json` (line 238) is `[]`,
with no `when` block under `docs` at all (unlike `bugfix`, `config`, `api`, `frontend`, `feature`,
each of which carries a conditional `when`). Docs is the one change_type in the matrix with zero
predicates to evaluate — there is nothing to check beyond confirming the label. Confirmed.

## 2. Per-kind resolution

| kind | required by `docs` matrix? | resolution |
|---|---|---|
| unit | no (`always: []`, no `when`) | not required |
| integration | not by matrix — but by this feature's own SC-04, explicitly | **satisfied**, audited (§3) |
| functional | excluded per DEC-187 | not applicable |
| component, ui, typecheck | `cmd: null` in `test_kinds` | not applicable, no runner exists |
| eval | excluded, not `ai_behavior` | not applicable |
| omp_session_accessor, handoff_comprehension, issue_types_live | `locally_run`; diff doesn't touch any of their `detect` surfaces | not on this diff's surface, no recorded run required |

`matrix_ok: true` — no verdict here rests on a null, excluded, or unresolved runner; the one kind
this diff actually exercises (integration, via SC-04) has a recorded green run.

## 3. SC-04 evidence — AUDITED, not executed

I did not run `run-unit-tests.sh --kind integration` or any suite this cycle (operator ruling:
no re-run in this phase). I am citing, not reproducing, the qa segment's measurement:
`.harness/harness/features/BUG-148-gate-record-correction/notes/qa-BUG-148-2026-09-06.md` §3,
measured at `f60d5d27` (a commit strictly before this pin): `RUNNER_EXIT=0`, `grep -c '^FAIL '` = 0,
both `test_committed_index_matches_a_fresh_regeneration` and
`test_no_amendment_construct_survives_in_the_authority` reported `ok`. The orchestrator's
independent re-measurement at `87e6033` itself (per this dispatch) reports 14 ok / 0 FAIL, same two
named tests both `ok`, exit 0.

I verified the transfer condition myself rather than taking it on faith: `git diff --stat
f60d5d27..87e6033 -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` is **empty** — the three product
paths are byte-identical between the qa segment's measurement point and this pin, so the cited
result is not stale evidence dressed up as current; it is the same tree. This is a reasoned/audited
determination (O-03), not a fresh measurement by me.

## 4. My own judgement — is `[]` right, and does the red-capability gap gate?

**Is `[]` the right floor?** Yes. The two records edited are prose (a decisions log entry and a
feature STATE.md), and the generated index is a byte-for-byte function of the prose via
`gen-decisions-index.py`. Nothing in this diff is executable, parsed-as-config, or read by a
runtime code path that a `unit`/`integration`/`config` kind would exercise differently than the
existing integration suite already does. `docs.always: []` is the honest floor for a diff whose
only possible defect class is "the prose is inaccurate" or "the generated file doesn't match its
generator" — and the second of those *is* covered, by `test_committed_index_matches_a_fresh_regeneration`,
which the change_type floor doesn't require but the feature's own SC-04 supplies anyway. There is
no gap between "docs requires nothing" and "this diff needed nothing beyond what SC-04 already
names": the two records' accuracy is judged by DEC-176/D-05's operator-ruling mechanism (SC-06,
explicitly out of my scope), and the index's fidelity to its generator is judged by the one
integration test that was proven red-capable.

**Does the red-capability gap gate?** No — it's a backlog row, not a blocker for this ship. Reasoning:
the gap is that `test_no_amendment_construct_survives_in_the_authority` was only ever observed
green and never perturbed to prove it can catch a real amendment-construct regression, while its
sibling test *was* proven red-capable (qa segment §5, measured against the stale `41c16c7` index).
But the specific defect class BUG-148 corrects — a false gate claim surviving in the prose, and a
stale generated index — is exactly what the *proven* test (`...fresh_regeneration`) catches, and
this diff's own verify commands (T-01/T-02 in `plan.yaml`) additionally grep for the exact stale
phrase ("Every gate was green", "All four gates green") going away and the corrected phrases
landing, which is a second, independent, already-executed check on the one property this feature
changes. The unperturbed test's property — no `Amendment`-headed appended section ever
reappearing — is not a property this diff's edits threaten in a new way (both edits are in-place
rewrites per D-01, not appends), so its unproven discriminating power is a pre-existing suite gap,
not a gap this correction introduces or depends on for its own soundness. It belongs on the qa
segment's/dev's backlog to eventually perturb, same as any other never-mutated assertion — it does
not block this docs-only correction from shipping.

## Findings

None that gate. One backlog note (not new — restates qa segment's own framing, not re-opening it):
`test_no_amendment_construct_survives_in_the_authority` should be perturbation-proven in a future
cycle touching that suite; out of scope here.

## Dead ends confirmed not re-opened

`--stdout | diff` retention (D-05 ruling 2), FEAT-05 STATE.md's pre-existing shape/heading-count
violation (D-04), the DEC-174/STATE.md dated-lead-in asymmetry (REQ-01/D-05), `merge-base
origin/main HEAD` as baseline. None re-litigated above.

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok: true — docs floor is [] and correctly so; SC-04 integration evidence audited (cited, not re-run) and transfers byte-identically to the pin; the one unperturbed named test is a backlog item, not a gate-blocker."
  suite: n/a
  matrix_ok: true
  kinds:
    - { kind: unit, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: integration, state: satisfied, cmd: "run-unit-tests.sh --kind integration (cited from qa-BUG-148-2026-09-06.md §3, audited not executed)", named_tests: 2 }
    - { kind: functional, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: component, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: ui, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: typecheck, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: eval, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: omp_session_accessor, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: handoff_comprehension, state: "not applicable", cmd: none, named_tests: 0 }
    - { kind: issue_types_live, state: "not applicable", cmd: none, named_tests: 0 }
  coverage_gaps: ["test_no_amendment_construct_survives_in_the_authority never perturbation-proven (pre-existing, backlog, not gating)"]
  sc_evidence:
    - { id: SC-04, test: ".harness/harness/features/BUG-148-gate-record-correction/notes/qa-BUG-148-2026-09-06.md:44-54 (audited, measured at f60d5d27, byte-identical to pin for all three product paths)" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-148-gate-record-correction/notes/review-harness-qa-c0.md
```
