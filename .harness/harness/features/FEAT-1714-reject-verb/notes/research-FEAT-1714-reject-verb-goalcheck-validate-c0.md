# FEAT-1714 goal-check — validation cycle 0

Reviewed exactly `origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1` (46 caller-enumerated paths). I read the BRIEF, decisions and tasks in `plan.yaml`, `feature.json`, `STATE.md`, both handoffs, the signed answer, and every receipt present under the feature before grading. Automated evidence comes from the pinned-cycle QA gate at `notes/review-harness-qa-c0.md`; I did not rerun tests.

## Verdict

**FAIL.** The feature does not deliver its first-run rejection outcome. The documented first-cycle path requires plan/GitHub state that a legitimate first sync does not have, and the confirmed GitHub command reports success and can record `rejected` after required provenance mutations fail. The blocking QA gate also fails its required unit matrix.

## Perspective grades

| Perspective | Grade | Evidence |
|---|---|---|
| orchestrator | fail | The new pre-lead instruction reads `plan.yaml.source_issues` and invokes `gh-sync.py reject` (`.claude/skills/harness/SKILL.md:45-59`), but a legitimate first sync loads `parent: None` (`gh-sync.py:519-556`) and reject refuses without a recorded parent (`gh-sync.py:1829-1833`). The same first cycle has not yet produced the plan mission's approval artifacts (`SKILL.md:35-46`), while station recording requires an existing `plan.yaml` (`gh-sync.py:655-668`). |
| operator | fail | Required comment, label, backlog, and milestone failures are only printed; execution continues and the numeric path records `rejected` anyway (`gh-sync.py:1874-1892`). Even close failure returns normally (`:1868-1872`), and CLI dispatch does not convert that return into a failing exit (`:2406-2410`). The operator therefore cannot rely on the local terminal record and GitHub parent jointly preserving provenance. |
| code maintainer | pass | `factory_config.TERMINAL_STATIONS = ("abandoned", "rejected")` is the single declaration (`factory_config.py:51`). Pinned inspection found no `TERMINAL_MARKER` reference and found the shared set consumed by plan/domain/route/state gates, gh-sync, board/lifecycle projection, handoff, and worktree cleanup. |

## Success-criterion outcomes

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | Current QA identifies direct reject-shape coverage in `tests/integration/test-validate-digest.py:1404-1443` and ledger-vocabulary coverage in `tests/unit/test-feature-record.py:221-234,575-576`; the integration matrix passed. The separate unit-matrix code-grade failure remains panel-blocking but does not contradict this behavior result. |
| SC-02 | not_met | automated + inspection | QA records no rejection-flow test preserving `source_issues` and the drafted BRIEF (`notes/review-harness-qa-c0.md:75-83,111`). More fundamentally, the instructed pre-lead flow cannot obtain the required recorded GitHub parent on a legitimate first sync and cannot reliably write the station without an existing plan; see GC-01. State-shape and worktree tests cover only fragments. |
| SC-03 | not_met | automated + inspection | QA says the happy-path test checks the final station value but not that station recording follows every required mutation (`review-harness-qa-c0.md:84-86,113`). Inspection shows failures in comment, label, backlog, milestone, and station recording do not fail the command or prevent terminalization; see GC-02. |
| SC-04 | met | automated | QA cites the valid case and independent INV-44 mutations in `tests/integration/test-check-state-feat59.py:454-517`; the integration matrix passed. |
| SC-05 | met | inspection | Pinned vocabulary inspection found the single tuple at `factory_config.py:51`, no remaining singular marker, and shared-set consumption across every named consumer. QA independently cites the consumer tests at `review-harness-qa-c0.md:89-90`. |

Overall SC status: **partial — 3 met, 2 not met**.

## Findings

### GC-01 — first-run rejection requires state that does not exist at first sync

- severity: high
- kind: substance
- reader: harness-pm
- owner: T-02, T-05
- scenario: A new `plan` or `patch` intake reaches the sole orchestrator run and discovers that its source ticket is obsolete before dispatching a lead. The new instruction requires reading this issue's `plan.yaml.source_issues`, then calling `gh-sync.py reject`. On a legitimate first sync, `load_recorded` explicitly returns an all-empty GitHub record with `parent: None`; `_reject_plan` then exits with `reject needs a recorded parent`. If `plan.yaml` has not yet been produced by the plan mission, neither the source lookup nor the terminal station write can work. The orchestrator must dispatch planning or rely on an undocumented manual bootstrap, violating the defining pre-lead outcome and SC-02.
- evidence: `.claude/skills/harness/SKILL.md:35-59`; `.claude/skills/harness/bin/gh-sync.py:519-556,655-668,1829-1833`; `.harness/harness/features/FEAT-1714-reject-verb/plan.yaml:246-264`.

### GC-02 — reject can return success and terminalize after required mutations fail

- severity: high
- kind: substance
- reader: harness-pm
- owner: T-02, T-05
- scenario: On a numeric rejection, the parent closes but posting the superseding-link comment, adding the label, returning the card to backlog, or closing the milestone fails. Each failure is printed and execution continues; `_record_station(..., "rejected")` still runs, and its own `False` result is ignored. The command exits 0, leaving a terminal local record without the GitHub provenance/state SC-03 promises. On the `none` path, even a failed parent close returns 0, so the orchestrator's instruction to write the station “only after it succeeds” cannot distinguish failure and can terminalize an open parent.
- evidence: `.claude/skills/harness/bin/gh-sync.py:610-670,1621-1640,1851-1894,2406-2410`; the changed happy-path-only assertions at `tests/integration/test-gh-sync-abandon.py:617-688`; T-02's successful-path contract at `plan.yaml:190-193`.

### QA-01 — required unit matrix fails

- severity: high
- kind: substance
- reader: harness-qa
- owner: T-01
- scenario: The configured unit gate exits 1 because the new `validate-digest.py:_reject_judgement_errors` function misses the code-grade allowlist/floor expected by `tests/unit/test-code-grade.py`. Any ship gate running the configured unit command rejects this revision.
- evidence: `notes/review-harness-qa-c0.md:17-36,107-110`.

## Dismissed candidates

- **INV-43 ownership** — dismissed: the signed answer assigns INV-43 to BUG-1723; FEAT-1714 correctly owns INV-44.
- **`TERMINAL_MARKER` deletion** — dismissed: intentional clean cutover. Pinned search found no surviving reference and consumers import `TERMINAL_STATIONS`.
- **Eng-lead preload overage** — dismissed as introduced here: the pin is 5509/5500, but main was already 5499; this diff adds pressure but does not originate the pre-existing breach.
- **Universal preload budget** — dismissed: 1895/1900 is within the configured limit.
- **Backlog before comment in `cmd_reject`** — dismissed: the stated hard ordering invariant is close-before-reseat; the implementation preserves that even though the dry-run list renders comment first.

```yaml
VERDICT: FAIL
DIGEST:
  headline: First-run reject is not executable from legitimate first-sync state, partial GitHub failures can still terminalize, and QA's unit matrix fails.
  feasibility: risky
  surface: M
  flags: [workflow-integrity, external-api, provenance, qa-blocking]
  recommend: halt
  tasks: 5
  decisions: 2
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:79-80" }
    - { id: SC-02, verdict: not_met, method: automated+inspection, evidence: "notes/review-harness-qa-c0.md:81-83,111; GC-01 above" }
    - { id: SC-03, verdict: not_met, method: automated+inspection, evidence: "notes/review-harness-qa-c0.md:84-86,113; GC-02 above" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:87-88" }
    - { id: SC-05, verdict: met, method: inspection, evidence: ".claude/skills/harness/bin/factory_config.py:51 and pinned consumer inspection" }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-validate-c0.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-validate-c0.md
```
