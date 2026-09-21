# FEAT-62 validation goal-check — cycle 0

## BLUF

**FAIL.** The pinned implementation discharges the reader perspective, but not the operator or code-maintainer perspectives. SC-04, SC-07, and SC-09 are partial, and the operator promise of default-output byte identity is contradicted by the feature's own measured D-1/D-3 divergences. Review basis: exact diff `16ee44f0..1380727cc6a866627595a267b9b681fc3f7026bc`; tests were not re-run, as dispatched, so automated grades use the checked-in red-first cases and `notes/build-divergences.md` receipts.

## Success-criterion grades

- **SC-01 — PASS.** `notes/build-divergences.md:26-50` records baseline exit/stdout/stderr digests for all eight pre-existing suites, then identical receipts after T-01 and again after T-02/T-03 (`:6-17`). The ninth table suite's 22 cases were red against the baseline checker and green on the build (`:44-47`).
- **SC-02 — PASS.** `tests/integration/test-check-state-table.py:90-228` covers non-executing ordered `--list`, retired INV-9/INV-10 resolution, full no-argument execution, `--only`, `--feature`, selector intersection, clean/dirty/untracked/rename `--changed`, and repo-row narrowing. Its red-first provenance is explicit at `:4-13` and in `notes/build-divergences.md:44-50`.
- **SC-03 — PASS.** `tests/integration/test-check-plan-routes.py:2570-2605` mutates module-scope loop, conditional, try, read, and shared-source reparse shapes and requires their own findings; the shipped-tree control is empty. The live receipt is `0 consolidation finding(s)` (`notes/build-divergences.md:16-17`).
- **SC-04 — PARTIAL.** Dirty/untracked/rename selection is covered by `test-check-state-table.py:157-213`, and file/git/gh absence mutants exist at `test-check-plan-routes.py:2612-2647`. However, the lock reduces git/GitHub reads to the binary name and treats any `git:` or `gh:` declaration as covering every operation/resource (`check-plan-routes.py:1960-1967,2006-2016`); the gh mutant uses `gh auth status`, not the required undeclared board resource. Finding GC-02.
- **SC-05 — PASS.** `test-check-plan-routes.py:2650-2681` independently mutates a missing DEC, a struck DEC-90, the index's live DEC-162 row, and an unreadable index; the shipped tree is part of the clean consolidation control.
- **SC-06 — PASS.** Workflow and hook mutants are red-first at `test-check-plan-routes.py:2684-2707`; the receipt reports zero live findings (`build-divergences.md:16-17`). The base-to-pin path diff changes no workflow, hook, or command-entry file, and `.github/workflows/tests.yml:276-311` invokes the full checker without `--changed`.
- **SC-07 — PARTIAL.** Feedback, path-derived checkout, both-stream forwarding, clean silence, refusal/no-write behavior, durable output and receipts are exercised at `test-harness-boundary.py:375-429`, `test-plan-merge.py:178-202`, and `test-feature-json-merge.py:456-477`, with baseline-red/build-green receipt at `build-divergences.md:8-15`. Source places relays after `locked_update` (`plan-merge.py:2482-2487`; `feature_json_write.py:210-211`), but no red-first test observes lock release: the fixture checker never attempts the writer lock. Finding GC-03.
- **SC-08 — PASS.** Pinned `.harness/README.md:90-94` distinguishes automatic mid-edit `--changed` feedback from full pre-commit/CI execution. `AGENTS.md` is byte-unchanged base-to-pin and retains “Run the canonical Harness state checker before committing” at `:46-47`. The changed-path diff contains no `SKILL.md`, preload-set, workflow, hook, or command-entry change.
- **SC-09 — PARTIAL.** The ordered table and runner context are present (`check-state.py:455-814,4401-4547,4721-4846`); pinned inspection found 40 rows, 40 unique names, 40 unique run targets, no missing target, and no unregistered `inv_*` function. The checker remains one module. The terminal receipt reports `318 graded, 0 below bar` against base `16ee44f0` (`build-divergences.md:16-17`), and the eight suites preserve report bytes. The handler-scoped base-to-pin comparison does not meet the untouched-handler clause: the base has 47 broad handlers, the pin has 48; only 34 of the original 47 handler ASTs are unchanged, 13 bodies structurally differ, and `_dirty_paths` adds a new broad handler at pinned `check-state.py:4610-4614`. Finding GC-04.

## Perspective conclusions

- **operator — FAIL:** SC-01, SC-02, and SC-06 pass and SC-07 is partial, but the broader promise in `BRIEF.md:9` is not discharged: `build-divergences.md:49-60` records default-output reordering for INV-17, INV-22/8, INV-32, INV-3, and the FEAT-59 family plus context-finding relocation, beyond the named INV-3/15/26 exceptions.
- **code maintainer — FAIL:** SC-03 passes, but SC-04 and SC-09 are partial because resource-specific read declarations are not enforced and the promised untouched 47-handler baseline changed (`check-plan-routes.py:1960-2016`; pinned `check-state.py:4610-4614`).
- **reader — PASS:** SC-05 and SC-08 pass, and the bounded ledger names the accepted observable differences and unchanged suite receipts (`build-divergences.md:26-60`) without adding instruction/preload surfaces.

## Findings

### GC-01

- severity: high
- kind: substance
- reader: goalcheck
- owning task: T-01
- exact location: `BRIEF.md:9`; `notes/build-divergences.md:49-60`
- failure scenario: An operator runs the no-argument checker on the same multi-feature tree at base and pin. Rows within INV-17, INV-22/8, INV-32, INV-3, and the FEAT-59 family reorder, so stdout is not byte-identical even though the approved operator promise allows only the named INV-3/15/26 loop changes.
- action: Rework the ordering to the approved bound, or obtain an operator-approved brief amendment that explicitly admits D-1/D-3 before claiming the perspective is discharged.

### GC-02

- severity: high
- kind: substance
- reader: goalcheck
- owning task: T-02
- exact location: `.claude/skills/harness/bin/check-plan-routes.py:1960-1967,2006-2016`; `tests/integration/test-check-plan-routes.py:2612-2630`
- failure scenario: A row declaring only `gh:auth` is changed to query the project board. `_argv_binary` observes only `gh`, and `_row_reads_findings` accepts any `gh:` declaration, so consolidation remains green while the row's declared resource is false. The same blind spot exists between git operations.
- action: Match the declared git operation/GitHub resource, and add the required red-first board-resource mismatch case rather than another no-gh-declaration case.

### GC-03

- severity: medium
- kind: substance
- reader: goalcheck
- owning task: T-03
- exact location: `tests/integration/test-plan-merge.py:178-202`; `tests/integration/test-feature-json-merge.py:456-477`; `.claude/skills/harness/bin/plan-merge.py:2482-2487`; `.claude/skills/harness/bin/feature_json_write.py:210-211`
- failure scenario: A refactor moves feedback into the locked transform. Both current tests still pass because their fake checker never acquires the sibling lock, while a real feedback checker or nested writer can block behind the still-held writer lock.
- action: Add a red-first fixture checker that attempts the same lock and proves it is free before emitting its row.

### GC-04

- severity: high
- kind: substance
- reader: goalcheck
- owning task: T-01
- exact location: base `16ee44f0:.claude/skills/harness/bin/check-state.py` broad-handler set; pin `1380727cc6a866627595a267b9b681fc3f7026bc:.claude/skills/harness/bin/check-state.py`, representative changed bodies at `:561-562,618-622,697-703,1833-1837,2318-2322,2545-2549,3161-3164,4345-4349` and new site `:4610-4614`
- failure scenario: A wave-3 maintainer starts from the approved claim that all 47 handlers were untouched, but 13 bodies already differ and the pin has 48 sites. The extraction and exception-policy changes can no longer be reviewed as separate waves, so a regression cannot be attributed to one bounded change set.
- action: Restore the original handler clauses and bodies modulo indentation, including extraction-compatible control flow, or seek an approved criterion change that enumerates and justifies every handler-body divergence and the new broad catch.

## Parked operator items

`OMP-PORT` numbering and the duplicate `INV-37` label remain the two parked record anomalies at `notes/build-divergences.md:74-81`. They are not findings against this feature and require no FEAT-62 resolution.

## Final goal verdict

**FAIL — operator and code-maintainer perspectives are not discharged; reader is discharged.**
