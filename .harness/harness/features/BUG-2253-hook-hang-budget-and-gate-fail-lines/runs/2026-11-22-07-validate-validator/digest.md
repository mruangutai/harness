# BUG-2253 reduced-scope validation — PASS

**Both operator-amended SCs met; all five readers PASS; no must-fix.** Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..7e590f735af90220baec7013c7ce8eafc2163bce`. QA executed the literal T-01 conjunction once in a clean, converged managed exact-pin checkout: **3 integration cases + 7 unit tests, exit 0, approximately 1 second**, under the 60-second bound. The pin was removed (`notes/review-harness-qa-c8.md`). Later requirement/record commits are not source under review.

## Assessment

- **SC-01 automated:** retained buried-file, echoed-header/same-name-PASS and fallback integration cases exercise the genuine QA refusal path; seven units exercise production parsers/reporting. Exact-base `notes/receipts/red-c4.txt/.stdout` exposes diagnostic loss; `discriminate-c4.txt` and `unit-red-b228c3a2.stderr` expose no-hide failures. QA/code/security/PM independently establish gate and unit equivalence to previous PASS and unchanged retained gate cases. These receipts remain subject-bound. Exact-base missing-helper unit errors are not semantic reds.
- **SC-02 inspection:** QA/code/security/PM confirm `HOOK_HANG_BUDGET_S = 30`, the FIFO/dangling-symlink/10,000-deep-JSON/load-headroom rationale, six named-budget calls (`tests/integration/test-validate-digest.py:3033,3066,3286,3288,3316,3318`), no `timeout=3`, unchanged unrelated timeouts and intact real safety cases. Removed regression machinery leaves no dead helpers/imports. The deletion is authorized by the operator ruling and ledgered T-01.intent amendment, not missing required coverage. Previous 17-case execution is historical; current selected execution is three cases.
- **Adequacy:** matrix floor is satisfied by relevant unit coverage plus the SC's integration carrier, not relabeled tests. QA's two limits remain explicit: no current full-kind suite claim, and six unit cases lack individually demonstrated semantic-red mutants. Neither violates the amended SC-level fail-first requirement, which has genuine retained evidence. SC-02 has no behavioral-regression assurance by operator choice. Only QA executed verification; other readers inspected source/receipts. Fresh raw logs are ephemeral; QA's durable note records command, pin, counts, exit and summaries. Main's grading is supplied evidence: exit 0, 21 PASSING, not panel-rerun.
- **Goal/UI:** PM passes both declared perspectives and amendment authority. UI measured 101 changed paths (3 Python, 98 records), zero visual surfaces: scoped-out PASS, not visual approval. No UAT criteria apply. Missing PRODUCT guidance was confirmed, not invented.

## Deduplicated advisories — no fix ordering or blocking action

1. **substance/low, T-01 SC-01, code + security:** runner-shaped echoed FAIL/mutation text may over-list names. Operator-accepted attribution ambiguity; real failures remain listed and nonzero runs refuse. Both readers agree on Low; no re-rating.
2. **substance/info, outside T-01, code + security:** runner-launch/timeout fail-open is unchanged and explicitly excluded. Retained for operator visibility, not a BUG-2253 remediation request. #2283 separately owns concurrent-suite oversubscription; no concurrency remedy or loaded-host performance claim is included here.

All findings retained and deduplicated; no severity disagreement or dismissed new defect. All five readers terminal, zero send-backs, no source edits. Reader artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c8.md` and `notes/research-BUG-2253-hook-hang-budget-and-gate-fail-lines-goalcheck-validate-c8.md`. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'BUG-2253 at 7e590f735af90220baec7013c7ce8eafc2163bce meets both amended
    SCs: 3 integration cases and 7 unit tests pass; SC-02 inspection passes; no must-fix.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Exact-pin signed verify exits 0: 3 integration cases, 7 unit tests,
      approximately 1 second; matrix true and retained SC-01 fail-first evidence.'
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Amended criteria satisfied; six budget calls and real safety cases preserved,
      no dead helpers or unrelated timeout changes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Refusal boundary unchanged; production/unit equivalence confirmed; accepted
      Low and excluded Info advisories retained.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 101 changed paths, three Python and 98 records, with no visual
      UI surface; correctly scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both amended perspectives met; operator amendment authority and retained
      receipt subject binding confirmed.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - SC-02 is inspection-only by explicit operator ruling; removed behavioral regressions
    are not required coverage. Six named-budget calls, rationale, unchanged unrelated
    timeouts and cleanup were independently inspected.
  - QA alone executed the literal targeted verify once at a clean, converged managed
    exact pin, subsequently removed. Other readers used source inspection and receipts;
    supplied main-session grading was exit 0, 21 PASSING, not rerun.
  - No full-kind or whole-repository suite compatibility, loaded-host latency guarantee,
    or current SC-02 behavioral assurance is claimed. Current integration count is
    three, not the historical seventeen.
  - Exact-base missing-helper unit errors are not behavioral reds. SC-01 has genuine
    retained integration fail-first evidence and a semantic unit red for the no-hide
    behavior; no requirement demands seven independently mutated unit cases.
  - Fresh raw execution logs are ephemeral; QA's durable c8 artifact records the exact
    command, pin, counts, exit and output summaries. Historical fail-first receipts
    remain durable.
  - Duplicate code/security advisories were merged without changing severity or kind.
    Both readers agree on Low attribution ambiguity and Info excluded fail-open; neither
    warrants a BUG-2253 fix.
  - '#2283 separately owns concurrent pooled-suite oversubscription. No concurrency
    remedy is included. No UAT criteria or visual acceptance apply.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'notes/review-harness-qa-c8.md: exact-pin T-01 conjunction passes 3
      integration cases and 7 unit tests, exit 0. notes/receipts/red-c4.txt/.stdout,
      discriminate-c4.txt and unit-red-b228c3a2.stderr supply semantic fail-first
      evidence; gate/unit and retained cases unchanged from prior PASS.'
  - id: SC-02
    verdict: met
    method: inspection
    evidence: 'notes/review-harness-code-reviewer-c8.md and QA/security/PM c8 notes:
      tests/integration/test-validate-digest.py:1025-1030 defines rationale and HOOK_HANG_BUDGET_S=30;
      six uses at 3033,3066,3286,3288,3316,3318; no timeout=3, unrelated timeout changes,
      dead helpers or damaged real safety cases.'
  needs_approval: false
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - Standing full unit/integration kind suites were not run; the assignment authorized
    only the literal targeted verify. No whole-kind compatibility claim follows.
  - Six of seven unit tests lack individually demonstrated semantic-red mutants; SC-01-level
    fail-first is satisfied by retained genuine integration failures and the no-hide
    unit failure.
  findings:
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer; code-reviewer
    summary: 'T-01 SC-01 accepted advisory: echoed runner-shaped output can over-list
      filenames.'
    why: 'validate-digest.py:2494-2536: already-executing test code can echo a matching
      header plus FAIL victim.py or mutation-note-shaped text, misleading refusal
      attribution without gaining acceptance or privilege. Genuine failures remain
      listed. Operator explicitly accepts this tradeoff; no fix requested.'
  - kind: substance
    scope: none
    severity: info
    reader: security-reviewer; code-reviewer
    summary: 'Outside T-01: unchanged runner-launch/timeout fail-open remains.'
    why: 'validate-digest.py:2431-2483: missing runner, launch failure or timeout
      leaves a QA claim unverified after warning. This is base-existing, explicitly
      excluded policy; retained for operator visibility, not a BUG-2253 blocker.'
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/runs/2026-11-22-07-validate-validator/digest.md
```
