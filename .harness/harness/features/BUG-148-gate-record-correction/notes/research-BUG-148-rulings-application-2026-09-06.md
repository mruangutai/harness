# Rulings application — BUG-148 — 2026-09-06

**All four operator rulings are applied and the package is signature-ready.** `check-plan-routes.py`
exits 0, `approval.status` is still `pending` with no `rulings:` key, `status: plan`, and the three
record files are byte-unchanged (`git status --porcelain` over them prints nothing). No correction was
implemented: this was a plan edit only.

## What changed, field by field

| Where | Route | Change |
|---|---|---|
| `plan.yaml` `decisions.D-01.because` | `amend --field because` (CAS on `b085eea1…`) | Splits the two halves: DECISIONS.md's in-place rewrite is FORCED (DEC-205 + `test_no_amendment_construct_survives_in_the_authority`); FEAT-05 STATE.md's is the **operator's ruling of 2026-09-06**, SUPPORTED by `check-domain.sh:1796-1806` (current-truth rationale on the 120-line denial; heading-vocabulary bar) and compelled by **no test** — the test opens `gdi.DECISIONS_PATH` only (`tests/integration/test-gen-decisions-index.py:836-874`). `choice` untouched (verified byte-identical to HEAD). |
| `plan.yaml` `decisions.D-05` | `apply` (union, `ADDED D-05`) | Records all three rulings with their PF ids, the date, that the `--stdout \| diff` form stays named in BOTH records with REQ-03 as written, and that approval remains unsigned. `dec: DEC-176` — the single batched signature-review pass these rulings discharge (`DECISIONS-INDEX.md:179`). |
| `plan.yaml` `tasks.T-02.intent` | `amend --field intent` (CAS on `7bd2284f…`) | Prior text preserved verbatim; adds a binding clause: read T-01's landed sentence in DEC-174 before writing, state the SAME three mechanism clauses, never a narrower one — and states plainly that no automated check discriminates the agreement. |
| `plan.yaml` `tasks.T-02.depends_on` | `amend --yaml-value` | `[]` → `[T-01]`. **Introduced dependency**: the intent now orders the doer to read T-01's landed sentence, so T-01 must have landed. Prose ordering is invisible to `teams/build.yaml`, which reads only `from_task_depends_on`. |
| `plan.yaml` `panel.findings[*].disposition` (3) | `set-panel` from the loaded mapping | The three ruled findings only. `id`/`severity`/`summary`/`consequence`/`reader` verbatim; the two informational dispositions, `readers`, `last_run`, `cycle`, `severity_max` unchanged (all asserted programmatically). |
| `BRIEF.md` `## Constraints` | Edit | New `Intake — SUPPLIES` bullet pointing at `notes/grilling-gate-record-correction-2026-09-06.md`. No new `##` heading. REQ-03, SC-03, SC-05 untouched. |

## T-02 `verify:` — left alone, deliberately

No discriminating read-only check exists. T-02's verify already greps the five phrases; a cross-file
grep of the same list against `DECISIONS.md` re-asserts exactly what T-01's own verify asserts
(`plan.yaml` T-01 `verify`, phrase loop over the DEC-174 region — confirmed present), so it buys a
second-file dependency inside the verify for zero new discrimination, and a keyword-stuffed narrower
text still passes either way. That limitation is now written into T-02's intent rather than dressed
up as a gate. `verify:` is byte-unchanged, so nothing was executed against it.

## Measured verifications

- `load_plan` parses; `approval: {'status': 'pending'}`, no `rulings:`; `status: plan`.
- `check-plan-routes.py <plan>` → **exit 0**, `OK T-01 granted to harness-documentor`,
  `OK T-02 granted to harness-orchestrator`, `0 violation(s) across 1 plan(s)`.
- Finding ids identical and in order; fixed fields verbatim for all five; disposition changed for
  exactly the three ruled ids.
- `git status --porcelain` over `DECISIONS.md`, `DECISIONS-INDEX.md`, FEAT-05 `STATE.md` → empty.
  HEAD unmoved at `63f7fc97`.
- `set-panel` re-dumped `panel:` through `yaml.safe_dump`, so its **presentation** changed (277+/116-
  in `plan.yaml`); every string VALUE was asserted equal to HEAD's.

## SC-05 confirmation (read, not edited)

`BRIEF.md` SC-05 allows "no path outside these three plus **this feature's own directory**". The
relocated grilling artifact is inside that directory, so SC-05 admits it as written. No SC text changed.

## Open questions

- **Q1 (non-blocking, main session):** the untracked source copy at `.harness/harness/notes/` still
  exists (`?? .harness/harness/notes/`). It resolves to NOBODY; no task owns deleting it.
- **Q2 (non-blocking, orchestrator):** this feature's own `STATE.md:51-53` still cites the grilling at
  its OLD path and poses Q4 as open, which ruling 4 has settled. `STATE.md` is not pm-writable.
- **Q3 (advisory):** the relocated artifact is untracked; if it is never committed, `BRIEF.md`'s new
  intake pointer names a path absent from the reviewed tree.
