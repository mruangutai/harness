# QA c4: LABEL authoritative-binding probe at a80b9ef3b2a30b1fa73101385a15b71b873cf09b

**FAIL.** The code reviewer's remaining T-01 bypass is real and executed. `board_lifecycle.py` LABEL ignores `feature_schema.resolve_binding`. My c3 line "high defect closed, no coverage gaps" is narrowed. Only the foreign-collision case (different `factory.repo`) is closed. The common authoritative-binding contract is untested and unfixed. I did not rerun the c3 suites or mutants. Only my own evidence has examined this (O-07). c3 (`review-harness-qa-c3.md`) is unchanged.

## New probe (this run only)
Method: `git archive a80b9ef3…` into `/tmp/qa-c4-xUnt` (outside the tree). `tests/integration/test-board-lifecycle.py` there is byte-identical to the pin, checked with `cmp`. A probe script (`/tmp/qa_c4_probe.py`) extracted the file's top-level defs by AST, with no `check()` cases executed. It reused the existing fake-gh helpers `write_root`, `_write_collision_fixture`, `run` and `run_module`. No network or live gh. The probe ran with `HARNESS_AGENT_TYPE` and `HARNESS_PROJECT_DIR` unset, so neither leaked into the run.

Fixture: `_write_collision_fixture(base, "acme/widget")`. Owner repo `acme/widget`, record `factory.repo = github.repo = acme/widget`, `issues: {T-01: 17}`, issue #17 NOT_PLANNED with no labels. Both measurements come from the same fixture in each row.

|Variant|`resolve_binding(doc, root)`|`audit` LABEL finding|`reconcile --apply` logged write|
|---|---|---|---|
|A. As-is (no `fleet.yaml`)|REFUSED, `FleetError: fleet file invalid … fleet.yaml … No such file or directory`|`LABEL: issue #17 is not_planned and carries no 'abandoned' label`, rc 1|`issue edit 17 --repo acme/widget --add-label abandoned`|
|B. Fleet declares acme/widget, served config sync=true and repo=acme/widget (valid control)|OK, `('acme/widget', {board…}, {})`|same finding|same single write|
|C. Declared, served `github.sync=false`|REFUSED, `invalid product mirror: acme/widget — github.sync must be enabled and github.repo must match factory.repo`|same finding|same write|
|D. Declared, product config unavailable (no content)|REFUSED, `product config unreadable: acme/widget@main:.harness/harness.json … gh returned no content field`|same finding|same write|
|E. Declared, served `github.repo=acme/other`|REFUSED, same `invalid product mirror` text|same finding|same write|

Cause: LABEL's actionable finding and write are identical in the refused rows (A, C, D, E) and in the valid control B. In A, audit stdout showed only the LABEL finding. The fixture record has no status or plan, so STATUS never fired. Any STATUS refusal is therefore separate from LABEL and does not cancel it. `_label_record_owner` (`board_lifecycle.py:974-984`) treats string equality of `factory.repo` with the audited repo, plus mirror provenance, as ownership. It never calls `resolve_binding` (`feature_schema.py:500-526`).

Consequence: the existing positive case `("acme/widget", True)` (`test-board-lifecycle.py:1062`) uses variant A. It proves a write on an **undeclared** binding. It does not prove a valid same-repo mirror. No test asserts a LABEL no-write under a binding the resolver refuses. Variant B shows the control would still pass after a fix. Variants A, C, D and E are the missing no-write controls.

## Reconciling c3
- Retained, carried from c3 and not rerun: the foreign-collision fix (`acme/other` #17 gives no finding and no write); the M-OWNER, M-INV7, M-LIVE and X-LABEL-OWNER mutants; the five T-01 verify scripts; `--kind unit` (61 files) and `--kind integration` (87 files) green.
- Withdrawn: "no coverage gaps". There is a gap for SC-01: the LABEL consumer has no authoritative-binding refusal test. The c3 mutant X-LABEL-OWNER neutered a different layer, the repo-equality check, so it could not show this.
- Ownership: the finding belongs to T-01 and SC-01 (the bound-binding cutover of board consumers). It is not emergent scope. Fix route: dev. LABEL should use `resolve_binding` and turn refusal into a report-only residual. Add tests for variants A, C, D and E (no write) and B (one write).

## Principles applied
- Build the Lever: one reusable AST-extract probe measures resolver and reconcile on the same fixture.
- Attack the Premise (informal): I questioned the premise that the same-repo positive fixture implies a valid declared binding. It does not.

## Missing guidance
Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent (as in c3). BRIEF, the plan and the Harness DECISIONS are used as authority.

Temp copy `/tmp/qa-c4-xUnt` is outside the tree and is removed on return. No pin was created, and the assigned checkout was untouched.
