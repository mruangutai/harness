# BUG-2420 security review — cycle 0

PASS — T-01 introduces no identified exploitable security defect. In scope: station mutation consumes plan text and changes workflow state beside signed approval.

Reviewed `d5be53927009df8e7848f860f9d0b4b03b89f9ad..c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`, never moving HEAD. Requirements: BRIEF SC-01–03, signed T-01, signoff notes; product SPEC §2.2–2.3 and DEC-120/174/225. The settled AdvisorC3Stations scope governs; no unrelated writer hardening requested.

## Changed-surface census

- `.claude/skills/harness/bin/plan_merge/stations.py`: IN — plan-text interpretation, station interpolation, approval integrity, destination/lock/write boundary.
- `tests/unit/test-plan-merge-first-station.py`: IN for regression/fixture exposure; optional module override is a local test-execution seam, not production input.
- `tests/integration/test-plan-merge.py`: IN for drafting-to-station regression and fixture exposure; no new service or runtime entry point.
- Feature `plan.yaml`: IN — sole delta is T-01 `building` → `done`; approval is unchanged.
- Feature notes `red-first-T-01.md`, `green-T-01.md`, `simplify-build-c0.md`: IN for exposure census; local paths, fixture identities and verification output, no credential-shaped material identified. Their reported runs are inputs, not independent verification.

## Boundary assessment

- **Tampering: nested prose → task station.** Exact field indentation and the tasks-range upper bound prevent the changed status lookup from rewriting a deeper `verify` scalar or a later top-level approval field (`stations.py:193–255`). SC-01's nested-prose fixture discriminates the old corruption; red/green receipts record it. Insertion targets immediately after the matched task id (`:258–267`). Existing task-search conventions remain unchanged; no claim of general YAML-parser hardening.
- **Tampering/elevation: station operation → signed approval.** The changed transform only inserts/replaces task status (`:270–286`), never invokes signing or approval reset. SC-02's successful-insertion assertion includes the complete literal approval block (`tests/unit/test-plan-merge-first-station.py:142–153`); SC-03 explicitly checks apply still does not seed status (`tests/integration/test-plan-merge.py:5142–5165`). No new signing authority.
- **Injection: CLI station → YAML.** Membership in the existing station vocabulary is checked before interpolation (`stations.py:270–274`; `plan_merge/guards.py:71–117`); no new shell, request, template or spreadsheet sink.
- **Tampering: target path/concurrency → plan bytes.** Existing resolved-destination guard and locked update remain on the mutation path (`stations.py:270–289`; `guards.py:28–47,229–234`; `harness_merge.py:141–193`). Transform executes within the same lock and same-directory atomic replacement. No new file destination, lock bypass or write mechanism.

Findings / must-fix / open questions: none. No builds, tests, linters, formatters or grading commands executed; final verification belongs to assigned QA.
