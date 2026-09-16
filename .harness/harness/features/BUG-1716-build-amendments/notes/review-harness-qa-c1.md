# QA c1 — pinned matrix gate

## Verdict

PASS — both required matrix kinds passed at `f602c7eee7761ce4325accba7a04678794c7ed69`; no coverage gap or QA finding remains.

## Scope and matrix

Phase 1, before implementation review, required automated coverage for closed lead-digest amendments (SC-01), byte-preserving all-or-nothing transcription and signed hashes/INV-40 (SC-02/SC-03), and exact overrule/refusal behavior (SC-04). The complete feature diff (`c97f8eb7..f602c7e`) has `api` T-02/T-03, `cross_module` T-04, runtime-code `bugfix` T-05, and docs T-01/T-06..T-09. The matrix therefore requires unit (API, cross-module, and runtime bugfix) and integration (cross-module); no other active or locally-run kind detects these paths.

| Kind | State | Exact command | Result |
|---|---|---|---|
| unit | satisfied | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; 40 files, including `test-code-grade.py` and BUG-1716 feature-record coverage |
| integration | satisfied | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0; 72 files, including BUG-1716 digest, plan-merge, state, and schema coverage |

`matrix_ok: true`. No task invokes an external-service or locally-run detect surface.

The Harness return validator's independent re-verification is known-broken here (issue #1756): it invokes this Python runner under Bash and exits 2 with `import: command not found`. That validator refusal is distinct from, and does not contradict, the two directly invoked Python matrix results above.

## Success-criterion evidence and fail-first

| SC | Current test coverage | Fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:603-651` accepts legal engineering-lead amendments and rejects all malformed/SC/decision cases. | `notes/receipt-main-session-T-02-fail-first.md:6-24` records the new acceptance and validation cases red at `cb26ae9e`. |
| SC-02 | `tests/integration/test-plan-merge.py:3711-3840,3909-3928` binds exact splices, named-field preservation, ledger order, refusal byte identity, and cross-file rollback. | `notes/receipt-main-session-T-04-fail-first.md:10-37` records record-amendments, refusals, and approval semantics red at `1fbf8471`. |
| SC-03 | `tests/integration/test-plan-merge.py:3647-3695` binds canonical signing; `tests/integration/test-check-state-feat59.py:440-496` binds INV-40 detection, scope, and amendment coverage. | `notes/receipt-main-session-T-04-fail-first.md:6-9` and `notes/receipt-main-session-T-05-fail-first.md:7-18`. |
| SC-04 | `tests/unit/test-feature-record.py:245-288` binds amendment-kind acceptance, exact selection, ambiguity/no-match/repeat refusals, and byte identity. | `notes/receipt-main-session-T-03-fail-first.md:6-13` records these cases red at `07424285`. |

Phase-1 expectations are all bound by changed tests; coverage gaps: none. SC-05 through SC-07 are inspection criteria.

## Prior findings

The prior validator digest identifies V-01 through V-08. The integration matrix passed the V-01 locked-ledger rollback case at `tests/integration/test-plan-merge.py:3909-3928`. The unit matrix passed `tests/unit/test-code-grade.py`, whose self-grade bar covers the repaired production and test records; this closes the grade findings V-02 through V-08, specifically V-08's prior `validate-digest.py` grade failure. No new matrix finding arose.

The temporary pinned QA worktree used for these two commands was removed. `git worktree list` contains no `qa-BUG1716-pin` worktree; no QA pin worktree created by this run remains.
