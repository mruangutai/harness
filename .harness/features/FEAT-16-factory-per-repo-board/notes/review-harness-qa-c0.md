# Review — harness-qa gate-only re-run — FEAT-16

## BLUF

PASS. Re-ran both required kinds (`unit`, `integration`) directly against the pinned diff; both
exit 0 with only real named-test failures (there are none) — no load/import/collection errors. This
is a **re-run of the same commands** the authoring segment (`qa-c0.md`) already ran, over the same
pinned tree. It does not add independent assurance beyond what `qa-c0.md` already established; it
confirms the gate still holds at this pin and that nothing regressed between the two checks.

## Pin confirmation

- `git rev-parse HEAD` = `132e2cecd926583ccfa6bfcfb07682ad6fb88b48`
- `git branch --show-current` = `feat/FEAT-16-factory-per-repo-board`
- `git merge-base --is-ancestor ec195ec06419eb7a2d47ed3eebab5145c346140c HEAD` → exit 0, confirmed
  ancestor.
- `git log --oneline ec195ec..HEAD`: two commits — `12e93f9` (run ledger / `review_sha` pin) and
  `132e2ce` (FEAT-16 qa gate pass note, per the dispatch — bookkeeping only). Diff under review is
  `a7c429c..ec195ec` as instructed; I did not diff against HEAD.
- Checkout: `/Users/molchairuangutai/GitHub/harness`, on branch `feat/FEAT-16-factory-per-repo-board`.
  `git worktree list` shows exactly one entry, this checkout — no separate worktree exists for this
  feature; nowhere else to run from.

## Matrix, re-derived independently from `harness.json` and `plan.yaml`

`change_type` per task (`plan.yaml`): T-01 `api`, T-02–T-06 `logic`, T-07 `config`, T-08 `api`, T-09
`logic`, T-10 `docs`, T-11 `logic`.

`test_matrix` (`.harness/harness.json`): `logic.always = [unit]`; `api.always = [unit]`,
`api.when = [{kind: integration, if: touches_db_or_external}]`; `config.always = []`;
`docs.always = []`.

Required kinds: `unit` (forced by every `logic`/`api` task) and `integration` (the `api` tasks touch
`gh`, an external system, and T-05/T-06 declare `--kind integration` in their own `verify:`, and
`test_kinds.integration.detect` names `test-factory-integration.py` explicitly). This matches the
authoring segment's ruling — I re-derived it from the same two files rather than taking it on say-so.

## Per-kind results, this run

| kind | state | cmd | exit | evidence |
|---|---|---|---|---|
| unit | satisfied | `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | full run captured; grepped for FAIL/ERROR/Traceback outside `PASS`/`ok` lines — none found; ends `PASS test-validate-feature-json.py` |
| integration | satisfied | `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | `test-factory-integration.py`: 106/106 checks passed, ends `PASS test-factory-integration.py`. Grep for FAIL/ERROR/Traceback surfaced only the suite's own deliberate PyYAML-bootstrap-failure **simulation case** output (`case_19c_zero_feature_project_is_not_an_error` passes immediately after), not a live failure (G-02) |
| component | skipped-with-reason | `cmd: null` in `harness.json`, status `unresolved` | n/a | not qa's to close — dev-ops has not run detection; no rendered surface in this feature |
| ui | skipped-with-reason | `cmd: null`, status `unresolved` | n/a | same; no `.tsx`/`.ts` files in any task |
| eval | skipped-with-reason | `cmd: null`, status `unresolved` | n/a | same; no `ai_behavior` change_type in this feature |
| typecheck | skipped-with-reason | `cmd: null`, not in matrix | n/a | not required |

`matrix_ok: true`

## The judgement call asked for

Re-running the gate does **not** change my view of how much assurance the green suites for
SC-01/02/05 carry. A second exit-0 on the same commands over the same commit range demonstrates
reproducibility of the pinned state, not new derivation — it is the same evidence observed twice, not
independent confirmation. The distinction the authoring segment drew stands: SC-13 and SC-04 are
backed by mutation (a mutant was constructed and killed), SC-01/02/05 are backed by reading the
assertion and confirming it fires on the intended input — real, but weaker, coverage. This gate-only
pass adds confidence that the suite is stable at this pin; it does not upgrade any read-only-verified
SC to mutation-verified.

One point I'd flag for the tier above rather than treat as settled myself: `qa-c0.md`'s own SC-13
finding (P6 does not discriminate from C1 on the mutant closest to the BRIEF's literal wording) is
**not re-tested here** — the dispatch explicitly parked it and told me not to re-derive it, so I did
not run mutation this pass. Its status is unchanged: real, non-vacuous coverage for the silent-exit-0
defect, unproven for the narrower "P6-alone, C1-blind" claim.

## Domain boundary — confirmed, not assumed

Checked `team-config.yaml`: the write grant over `.claude/skills/harness/bin/**` belongs to
`harness-backend-dev` and `harness-dev-ops`, not `harness-qa`. All source changes in this diff live
under that path. I hold no write grant there, made no edits, and any coverage gap in that path would
not be mine to close — none was found this pass (see per-kind table above; both required kinds are
satisfied with real, diff-relevant tests).

## Coverage gaps

None found this pass. `unit` and `integration` are both satisfied with named, diff-relevant tests
(same set the authoring segment named: `test-factory-config.py`, `test-factory-claim.py`,
`test-factory-decompose.py`, `test-factory-land.py`, `test-no-distribution.py`,
`test-factory-integration.py`, `test-check-domain.py`'s migrated case). `component`/`ui`/`eval` remain
soft-skips (`cmd: null`), unchanged from the authoring segment — genuinely not applicable to this
feature's diff, not a finding.

## SC evidence (unchanged from `qa-c0.md`; not re-derived, cited for findability)

| SC | test |
|---|---|
| SC-01 | `test-factory-config.py` cases (3), (27), (28a-d) |
| SC-02 | `test-factory-config.py` case (8b) |
| SC-04 | `test-factory-claim.py` P1-P4, `test-factory-decompose.py` T-03, `test-factory-land.py` T-04, `test-factory-integration.py` case (H) |
| SC-05 | `test-no-distribution.py` `kaya_ai_is_paired_with_board_2` + siblings |
| SC-08 | `run-unit-tests.sh --kind unit` exit 0 (this run) |
| SC-09 | `run-unit-tests.sh --kind integration` exit 0 (this run) |
| SC-13 | `test-factory-claim.py` P6 — mutation-killed for the general defect, open question on the narrower BRIEF wording (parked, not re-run) |

## Authoring

Wrote nothing. `files_touched: []`. Ran commands only; no test, fixture, or source edits.

## `git status --porcelain`, verbatim and complete

```
?? .harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-code-reviewer-c0-ui-scope.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-code-reviewer-c0.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-ui-reviewer-c0.md
```

Those three files are other reviewers' panel artifacts, not mine — no output from my session besides
this file (which is untracked at the time I ran `git status`, prior to writing it).

## Exit codes, verbatim

```
UNIT_EXIT:0
INTEGRATION_EXIT:0
```
