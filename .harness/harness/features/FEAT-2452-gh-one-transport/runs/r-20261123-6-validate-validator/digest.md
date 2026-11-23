# Validate — FEAT-2452 — rework c1 — r-20261123-6-validate-validator

**FAIL** at review_sha `e282689dd01a1a45eb22f08be67b1e2a9b437fb1` (base `b788e9da`). H1, G1, F1 and A1 are closed. H2 is closed only partly. `blockers()` now validates the container but not the `state` field that frontier decides on. A stateless blocker `[{}]` or `[{"state":"unknown"}]` therefore still admits an open, unassigned ticket as eligible, and `[{"state":1}]` raises an untyped AttributeError. Suites are green with DEC-255 receipts (unit 67, integration 95), and T-01..T-05 verify blocks exit 0. Under `gates.review: advisory_unless_high`, the one high finding is what blocks.

## Readers
| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c2.md`; receipts `qa/manifest-{unit,integration}.json`; reproduced the G1, H2 and A1 reds independently |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c2.md`; measured H1/G1 closed; code-grade pass |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c2.md`; same T-04 defect rated med; no ReDoS, leak or 403 bypass |
| ui | harness-ui-reviewer | PASS | scoped out after a measured census: 0 UI paths in 169 (fix delta 41) |
| goalcheck | harness-pm | PASS | `notes/research-…-goalcheck-validate-c2.md`; both perspectives pass; SC-05 is met on the literal text, with a narrowed reading |

## c0 findings — disposition
- **H1 closed.** code-reviewer measured C1–C3, and QA's receipts are green.
- **G1 closed on the literal text.** QA reproduced the red at 15a240bc in its own managed pin, with exit 1, 6 FAILED, and station `building`. pm and QA both note that the red covers a failed label create, not a per-item close failure. The literal status and the narrowed reading are recorded separately (OQ-GC2-1).
- **F1 closed.** One low form inaccuracy remains (M2).
- **A1 closed** for the authority. The path segment is still loose (advisory B1).
- **H2 partial.** This is M1. pm graded SC-03 met, but its evidence cites only the null, `{}` and number cases. It does not test the blocker `state` field, so the code-reviewer's measurement governs.

## Ranked must-fix (in fix order)
1. **M1 · high · substance · T-04 (SC-03; residual of c0 H2), from code-reviewer and security.** I confirmed this at source: `wayfind.py` frontier `(b.get("state") or "").lower() == "open"`. A blocker with no state or an unknown state counts as closed, and an integer state crashes untyped. **Severity reconciled to high, not security's med.** The c0 H2 ruling rated the same realism class high (a malformed successful GitHub payload: `null` → `[]`), and c0's must_fix asked to "reject unusable payloads before eligibility". The fix validated the container but not the field the decision rests on. `parent_of` does validate the field it uses (`number`), and that asymmetry is the defect. Security's med reflects likelihood, which c0 had already weighed. **Remedy, bounded to close the class in one round:**
   - Each blocker's `state` must be a string whose lowercase is `open` or `closed`; anything else raises via `unusable()`.
   - The same applies to the other decision-bearing field I found by opening frontier myself: `full.get("assignees")` must be a list. Today a missing `assignees` reads as unclaimed, so a claimed ticket would be listed.
   - Add fail-first regressions. Keep the valid empty list and the confirmed-404 absence green.
2. **M2 · low · form · T-05 (SC-06), from code-reviewer.** `github-mirror.md:106` says every ticket closes and reseats after a label-create failure. A ticket whose close also fails is reported and neither reseated nor labelled, and later work continues. Reword. This is independent of M1.

## Advisory (not gating), ranked
- **B1 · med · substance · T-01, from code-reviewer.** `_ISSUE_URL` accepts `https://github.com/o?x/r/issues/42` because the path segments are `[^/\s]+`. This shape is unrealistic as `gh issue create` stdout. If the fix round is touching T-01, tighten the owner/repo segments to forbid `?` and `#`; otherwise backlog it.
- **B2 · low · substance · T-02, from security.** Abandon reports the label-create denial only through closed tickets. If every close fails, the 403 is never printed. The fix is to print the gap once.
- **B3 · low · substance · T-01, from security.** The authority accepts `a..b`, `a.-b` and port 65536. No request is made to that host. Backlog.
- **B4 · info · coverage · T-02, from QA.** `test-gh-sync-abandon-sources.py` never asserts the labels seam event. It was vacuous already at base, and the integration `test-gh-sync-abandon.py:70` catches a dropped label create.

## Assessed and dismissed
- A2, OQ-QA-2, OQ-QA-3 and the standing disclosures (including the SC-04 (e) cut under C5) were ruled before this run. No reader brought new evidence against them.
- The code-reviewer's `spec_violations` for factory_gh (SC-05) and github-mirror (SC-06) are carried as B1 and M2 at the reviewer's own severities (med and low). Neither is high.

## Adequacy
- QA's green rests on the runner receipts and a non-zero discovery count. QA reproduced every fix-c1 red independently rather than trusting the builder's receipts.
- Two lenses found the M1 defect independently, and security confirmed it by isolated execution at base, c0 and c1. **It predates this feature.** It is in scope because c0's H2 remedy named the class.
- No reader found a regression introduced by the fix delta. The new findings are pre-existing residuals or doc precision.

## Open questions (non-blocking)
- **OQ-GC2-1 (pm and QA).** SC-05 #13 is met on the literal text through the label-create red. The three per-item close-failure #13 assertions have never been red. Does the operator accept the literal discharge, or want a dev-side mutant that breaks `_apply_abandon_plan` after the first failed close? I recommend accepting it. The c0 ruling named H1's abandon regression as sufficient.
- **OQ-GC2-2 (pm).** The ship record must carry the C5 cut of SC-04 (e).

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2452 FAIL at e282689d. H1, G1, F1 and A1 are closed and suites are
    green with receipts (unit 67, integration 95). H2 is only partly closed: a blocker
    without a valid state still admits an open ticket to the frontier (T-04, high).
    One low doc fix rides along.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 67/67 and integration 95/95 green with DEC-255 receipts at e282689d.
      All T-01..T-05 verify blocks exit 0. QA independently reproduced the G1, H2
      and A1 reds.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-04 still admits tickets with unverified blockers. H1 and G1 are closed
      and code-grade passes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new disclosure, 403 bypass or ReDoS. The same T-04 stateless-blocker
      defect is rated med, plus two low advisories.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: 0 UI paths across the 41-path fix delta and the 169-path
      full diff.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Both perspectives pass. SC-05 is met on its literal text, with a narrowed
      #13 reading recorded as a non-gating advisory.'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  must_fix:
  - 'M1 (T-04, high, substance; SC-03; residual of c0 H2): wayfind frontier treats
    a blocker with no state or an unknown state as closed via (b.get(''state'') or
    '''').lower() == ''open'', and an integer state raises an untyped AttributeError.
    Fix: require each blocker''s state to be a string whose lowercase is open or closed,
    else raise unusable(); also require frontier''s issue `assignees` to be a list,
    since a missing value currently reads as unclaimed. Add fail-first regressions,
    and keep the valid empty-list and confirmed-404 cases green.'
  - 'M2 (T-05, low, form; SC-06): github-mirror.md:106 says every abandon ticket closes
    and reseats after a label-create failure. Reword it: a ticket whose close also
    fails is reported and neither reseated nor labelled, and later work continues.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  open_questions:
  - id: OQ-GC2-1
    question: 'SC-05 #13 is met on its literal text through the abandon label-create
      red at 15a240bc, which pm and QA both reproduced. The three per-item close-failure
      #13 assertions have never been red. Does the operator accept the literal discharge,
      or want a dev-side mutant that breaks _apply_abandon_plan after the first failed
      close? The validator lead recommends accepting it, because c0 named H1''s abandon
      regression as sufficient.'
    blocking: false
  - id: OQ-GC2-2
    question: The ship record must carry the C5 cut of SC-04 (e). This standing requirement
      can only be checked at ship.
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'QA''s green rests on DEC-255 receipts with non-zero discovery (unit 67, integration
    95). QA reproduced the fix-c1 reds independently in managed pins rather than crediting
    the builder''s receipts: G1 exit 1 with 6 FAILED at 15a240bc; H2 28 FAIL with
    wayfind@64102016; A1 4/324 with factory_gh@64102016.'
  - 'Severity reconciliation for M1: code-reviewer rated it high and security med.
    The lead kept high. c0 rated the same realism class, a malformed successful GitHub
    payload, high under H2, and c0''s must_fix asked for unusable payloads to be rejected
    before eligibility. The fix validated the container but not the state field frontier
    decides on, while parent_of does validate its decision field. The lead confirmed
    the frontier line at source.'
  - 'M1 predates this feature: security confirmed it by isolated execution at base,
    c0 and c1. No reader found a regression introduced by the fix delta 64102016..e282689d.'
  - The remedy for M1 is deliberately widened to the frontier's `assignees` read.
    The lead found that fail-open by opening frontier, and closing the whole class
    in one round avoids a third pass of malformed-field findings.
  - pm graded SC-03 met, but its evidence cites only the null, {} and number cases.
    It does not cover the blocker state field, so the code-reviewer's measured counterexample
    governs SC-03.
  - 'Advisories, not gating: B1 (T-01, med) _ISSUE_URL owner/repo segments accept
    ''?'' (https://github.com/o?x/r/issues/42); B2 (T-02, low) abandon never prints
    the label-create 403 when every close fails; B3 (T-01, low) the authority accepts
    a..b, a.-b and port 65536; B4 (T-02, info) the unit seam in test-gh-sync-abandon-sources.py
    never asserts the labels event, a gap already present at base that the integration
    test at :70 covers.'
  - A2, OQ-QA-2, OQ-QA-3 and the standing disclosures, including the C4 zero-enforcement-diff
    receipt, were ruled before this run. No reader brought new evidence against them.
    pm re-confirmed that the base..pin diff names no enforcement file.
  - Fixes are main-session-direct under DEC-174. M1 and M2 are independent. This FAIL
    consumes rework round c2 of 2.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: t01 reds; A1 red 02-red-factory-gh.txt 4/324, reproduced by QA; unit
      receipt green at e282689d
  - id: SC-02
    verdict: met
    method: automated
    evidence: t02-red-green/01-red-confinement-open.txt; test-gh-sync-open.py:863
      green at pin
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: 'H2 container cases closed (case_8b/10b/11b; red 28 FAIL reproduced
      by QA). M1: wayfind frontier admits a ticket whose blocker payload is [{}] or
      [{"state":"unknown"}], and [{"state":1}] raises an untyped AttributeError (code-reviewer
      measured; security confirmed)'
  - id: SC-04
    verdict: met-with-cut
    method: automated
    evidence: 'H1 closed: mirror_labels keeps SKIP/0 for open and recover; abandon
      continues unlabelled with exit 0; reject halts with exit 1 (06-verify-T-02.txt;
      QA receipts). (e) cut under C5'
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'abandon_label_create_failure_case is red at 15a240bc and QA reproduced
      it (exit 1, 6 FAILED); green at pin. The narrowed #13 reading is OQ-GC2-1, non-gating'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: F1 rows present and matching the code (pm, code-reviewer). One low form
      inaccuracy at github-mirror.md:106 (M2)
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'notes/enforcement-backlog.json unchanged at pin: #2468 OPEN, names
      both executors'
  - id: DEC-138
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3132 unchanged in the fix delta; c0 grading carries forward
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No regression for a blocker without a valid state, or for a missing or non-list
    assignees, in wayfind frontier (M1)
  - 'The three per-item close-failure #13 assertions have never been red; the #13
    failing-first rests on the label-create case (OQ-GC2-1)'
  - The unit seam test-gh-sync-abandon-sources.py never asserts the labels event;
    this gap was present at base, and the integration test covers it (B4)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-04: wayfind frontier treats a blocker with no state or an unknown
      state as closed; an integer state raises an untyped AttributeError'
    why: 'SC-03, residual of c0 H2: an open, unassigned ticket with an unverified
      blocker becomes eligible. security-reviewer raised the same defect at med; the
      lead reconciled it to high, consistent with c0''s H2 rating'
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'T-04: an object-shaped blocker without a recognized state can make a
      ticket eligible'
    why: Deduplicated into the code-reviewer's high M1 finding; the lead kept high
      (see adequacy_notes)
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: _ISSUE_URL owner/repo segments accept ''?'' and ''#'', e.g. https://github.com/o?x/r/issues/42'
    why: 'Advisory B1: unrealistic as gh issue create stdout; tighten it if T-01 is
      touched, otherwise backlog'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-05: github-mirror.md:106 says every abandon ticket closes and reseats
      after a label-create failure'
    why: 'M2: a ticket whose close fails is neither reseated nor labelled; SC-06 requires
      partial writes to be stated accurately'
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-02: abandon never reports the label-create 403 when every close fails'
    why: 'Advisory B2: the gap is reported only through closed tickets; print it once'
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-01: the authority matcher accepts malformed DNS labels and port 65536'
    why: 'Advisory B3: no request is made to that host; backlog'
  - kind: form
    scope: none
    severity: info
    reader: qa
    summary: 'T-02: the unit seam test-gh-sync-abandon-sources.py never asserts the
      labels event'
    why: 'Advisory B4: the gap was present at base; integration test-gh-sync-abandon.py:70
      catches a dropped label create'
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'T-02: G1 discharges #13 through a label-create red, not a per-item close-failure
      red'
    why: SC-05 is met on its literal text; the narrowed reading is routed up as OQ-GC2-1
      rather than gated
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
```
