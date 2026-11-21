# Code review — BUG-2187 / T-01

PASS: no substantive or form findings in `5bd9efd411a4b4a7a6a09dcf7517946c75c5f220..1b35414bfc865786baffe0418528deeeef141272`. Contract inspection completed before the quality conclusion. All source inspection used immutable `git show`/`git diff` subjects; no managed checkout was created. No human-tagged commits or dirty tracked files were reported.

## Contract inspection

- SC-01: `.claude/skills/harness/bin/check_state/feature_record.py:66–90` removes exactly root/task status, retains nested status, uses the existing YAML loader, and falls back to raw bytes for legacy/unloadable input. The byte fast path and both-read guard remain at `:100–114`; disk-plan, placeholder, terminal and repository guards remain at `:130–197`. Restored-content acceptance is independent of commit identity. Integration cases `tests/integration/test-check-state-records.py:475–511` exercise station-only movement, reserialization and nonstation status changes alongside existing stale/presence and restored-content cases.
- SC-02: `.claude/skills/harness/bin/feature-record.py:594–617,1137–1140` resolves default HEAD/explicit refs with `code_grade.commit_oid` before `_apply`; noncommits/unresolved/option-shaped revisions exit 2 through `_exit_refused`, before mutation. `_apply` at `:101–121` retains the shared locked/schema-checked writer. CLI regressions are at `tests/unit/test-feature-record.py:1257–1312`. Guidance names the verb; `.claude/skills/harness/references/build-phase.md:43–55,76–83` preserves seam order and frozen/external exceptions, with matching SKILL guidance at `:142–153`.
- SC-03: `.claude/skills/harness/bin/feature-record.py:667–720` uses judgement `at >= first validate started_at`; regates replace, never sum with, precisely the existing fix-run fallback. No validate means an empty fallback window. Existing distill exclusion, elapsed/token fields and cycles semantics are retained. Unit cases at `tests/unit/test-feature-record.py:1231–1254` cover direct fixes, multiple rounds, the exact boundary, earlier/non-regate entries, competing fixes and fallback.
- Accepted inventory amendment: `tests/integration/canonical-reader-classification.json:515–528` identifies `_inv33_reviewed` as `in_memory_validation`, main-session-direct. No unrelated executable changes or scope expansion found. No SC is marked `verify: inspection`.

## Quality and evidence

Fail-open/refusal inspection found no new silent success path. Considered the simplify dispositions independently; retained naive/aware handling is explicit and does not alter comparable timestamps. Mechanical grading over the exact assigned range exited 0: 31 records passed, no grade-2 or high records (`code_grade: pass`).

Build red/green receipts were inspected as historical evidence, not treated as final pinned verification: their fixed subject is a pre-commit working tree. QA owns final exact-subject evidence and the assigned command: `python3 tests/integration/test-check-state-records.py && python3 tests/unit/test-feature-record.py`. No tests, builds, linters, formatters or mutants were executed by this reviewer.

## Principles applied

- Delete First: confirmed obsolete byte-only behavior was replaced locally rather than retained behind a compatibility branch.
- Model the Domain: reviewed the explicit absent-window/fallback distinction; no duplicated state or new cross-module lifecycle mechanism is introduced.

Open questions: none. Product spec/decisions/architecture documents are absent as recorded at intake; no substitute authority was invented.
