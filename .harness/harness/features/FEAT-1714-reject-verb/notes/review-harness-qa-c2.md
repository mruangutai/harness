# QA matrix gate — FEAT-1714 c2

Pinned review: `130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57`; range `33f45262a9346b62a0e81d3a21786ab2b761cf4e..130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57` (61 paths). All measurements below came from detached `qa-1714-c2-pin` at that SHA, not the feature worktree's moving HEAD.

## Phase 1 — requirements-derived inventory

Before source inspection: automated coverage must accept/refuse the reject digest (SC-01); preserve first-run provenance and drafted BRIEF while enforcing the zero-cycle terminal record and terminal cleanup (SC-02); prove numeric report/confirmation lifecycle, no-write report mode, parent-only mutation, failure stop, and final-station ordering (SC-03); and prove every rejected-record invariant dimension (SC-04). SC-05 is inspection-only. The plan's `api`, `feature`, and `cross_module` tasks require unit; `feature` and `cross_module` require integration. The full pinned diff has no interaction flow or AI surface, so no UI/component/eval kind fires.

## Required matrix — measured at the pin

- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; 40 discovered files; pool summary: 8 workers, 40 files, 5.36s wall.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` — exit 0; 72 discovered files; pool summary: 8 workers, 72 files, 79.11s wall.

No formatter, linter, build, or other broad validation command ran.

`validate-digest.py`'s independent re-verification is known-broken (issue #1756): it invokes the Python runner as a bare shell command and exits 2. That checker failure does not re-measure these commands; the QA verdict is the direct pinned measurements above (issue #919).

## C1 finding reconciliation — direct pinned evidence

- **QA-C1-01 — closed.** `tests/integration/test-gh-sync-abandon.py:762-770` binds the executed first-sync plan twice: parsed `status == rejected` and `source_issues == [1714]`, then exact bytes equal the pre-run baseline with only `status: plan` replaced. The test's subject is the post-command `plan.yaml`; deleting or rewriting provenance makes both assertions red. This test passed in the pinned integration matrix.
- **QA-C1-02 — closed.** The same pinned test binds remote-call sequence, not final state: the fake stamps the plan station on each remote write (`:662-692`), and numeric and first-sync cases require every remote write to observe the pre-reject station (`:689-692`, `:759-761`). Moving the station before any remote call reddens these assertions. Its independent `none` comment-failure arm requires exit 1, identifies the landed close, proves backlog and milestone were not run from stderr and call log, and requires station `building` (`:778-798`); an early or failed-path station write reddens it. The full named test passed in the pinned integration matrix.

## Automated SC evidence and fail-first

- SC-01: `tests/integration/test-validate-digest.py:1404-1443`; failed before implementation in `notes/receipt-main-session-T-01-fail-first.md:6-22`.
- SC-02: `tests/integration/test-gh-sync-abandon.py:729-772`; `tests/integration/test-check-state-feat59.py:464-521`; `tests/integration/test-worktree-terminal.py:847-864`; failed before implementation in `notes/receipt-main-session-T-03-fail-first.md:7-18`.
- SC-03: `tests/integration/test-gh-sync-abandon.py:647-727, 778-798`; failed before implementation in `notes/receipt-harness-backend-dev-T-02-fail-first.md:35-41`.
- SC-04: `tests/integration/test-check-state-feat59.py:464-521`; failed before implementation in `notes/receipt-main-session-T-03-fail-first.md:7-16`.

## Auxiliary worktree census

Before c2, `git worktree list --porcelain` had no `qa-*-pin` worktree, including no c1 `qa-1714-pin`. C2 created `qa-1714-c2-pin` only to run the matrix at the immutable SHA and removed it from outside that worktree. Final `git worktree list --porcelain` census: **0** worktrees whose path is under `.claude/worktrees/qa-*-pin`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned unit and integration matrices pass; QA-C1-01 and QA-C1-02 are directly discriminated and closed."
  suite: pass
  failures: 0
  matrix_ok: true
  reviewed_sha: 130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57
  reviewed_range: 33f45262a9346b62a0e81d3a21786ab2b761cf4e..130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40, evidence: "exit 0; pool: 8 workers, 40 files, 5.36s wall" }
    - { kind: integration, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72, evidence: "exit 0; pool: 8 workers, 72 files, 79.11s wall" }
  coverage_gaps: []
  dispositions:
    - { id: QA-C1-01, disposition: closed_at_130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57 }
    - { id: QA-C1-02, disposition: closed_at_130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57 }
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py:1404-1443" }
    - { id: SC-02, test: "tests/integration/test-gh-sync-abandon.py:729-772; tests/integration/test-check-state-feat59.py:464-521; tests/integration/test-worktree-terminal.py:847-864" }
    - { id: SC-03, test: "tests/integration/test-gh-sync-abandon.py:647-727,778-798" }
    - { id: SC-04, test: "tests/integration/test-check-state-feat59.py:464-521" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-22" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-03-fail-first.md:7-18" }
    - { sc: SC-03, evidence: "notes/receipt-harness-backend-dev-T-02-fail-first.md:35-41" }
    - { sc: SC-04, evidence: "notes/receipt-main-session-T-03-fail-first.md:7-16" }
  qa_pin_worktree_census: "0; qa-1714-c2-pin removed; no c1 qa-1714-pin existed"
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c2.md
```
