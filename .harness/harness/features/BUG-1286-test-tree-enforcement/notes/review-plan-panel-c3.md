# Team digest — plan-panel — BUG-1286-test-tree-enforcement — cycle 3

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan-panel PASSES the drafted BUG-1286 plan — both readers ran, must_fix empty, severity_max med, nothing high/critical/unrated, so no panel finding needs operator risk-acceptance; one low spec ambiguity in T-03's --against output contract is the only actionable item."
  team: plan-panel
  steps_run: 2
  cycles_used: 0
  members:
    - { step: should-not-exist, persona: fable-advisor, verdict: PASS, headline: "Ran and returned 5 findings: everything in this plan earns its existence; the per-invocation git ls-files tax is a two-subprocess delta inside a gate run-unit-tests.sh:33 already runs, and an audit-only or CI-only instrument fails issue #1286 by construction", files_touched: [] }
    - { step: scope, persona: harness-code-reviewer, verdict: PASS, headline: "Ran and returned 4 findings: no orphan REQs, valid topological depends_on, no verify shown ungradable at its own task's completion, SC-07/SC-09/SC-15 anchors all live at the pinned tip", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c3.md"] }
  severity_max: med
  findings:
    - { reader: scope, severity: low, summary: "T-03's --against output contract doesn't state whether the row/TOTAL block still prints under comparison mode", why: "A spec-compliant diff-only reading makes T-04's own verify: fail on a correct note, forcing a rework cycle" }
    - { reader: scope, severity: med, summary: "D-05's accepted archival landmine", why: "Archiving FEAT-44's evidence file reddens every run-unit-tests.sh invocation repo-wide until a backend-dev/dev-ops edit, though the archiver need not hold that grant" }
    - { reader: should-not-exist, severity: low, summary: "The D-05 coupling should be accepted at low severity; the reddening is a loud self-describing one-line finding fixable by a one-tuple-entry edit, and the alternatives are rewriting a landed feature's shipped record or letting exceptions go silently stale, which breaches AC-07", why: "A rare deliberate act (archiving landed evidence) requires routing a trivial suite_layout.py edit to backend-dev or dev-ops before any test can run again" }
    - { reader: scope, severity: info, summary: "SC-06's exact-equality assertion is acceptable, not brittle in the way asked", why: "The pinned string is introduced by T-01 itself, so a later wording change is owned by the same task — normal coupling, not cross-feature brittleness" }
    - { reader: should-not-exist, severity: info, summary: "SC-06's exact-equality grader should stand; whole-list equality is the only form that proves the valid unit, integration and manual files and the copied bin module each contributed nothing, and the pinned string is also asserted at the runner boundary in T-02", why: "Brittleness cost is one deliberate re-pin when the message is intentionally changed, which must already coordinate with T-02's MISCONFIGURED assertions" }
    - { reader: scope, severity: info, summary: "harness.json detect residual: disclosure is sufficient and does not gate", why: "None gating — disclosed, measured by T-03's unfiltered selection, empty at the tip; raised as a non-blocking open question for operator awareness" }
    - { reader: should-not-exist, severity: low, summary: "The unit.detect residual should not gate the signature but should not end at disclosure either; the only in-scope fix edits harness.json, which AC-11 and SC-14 forbid, so gating deadlocks the feature against itself", why: "Disclosure alone leaves a standing hole no instrument watches after review, since T-03's audit runs at review_sha rather than every invocation; the right consequence is a follow-up ticket" }
    - { reader: should-not-exist, severity: info, summary: "The repository-wide clause and every task carrying it should be built; issue #1286 explicitly mandates pre-dispatch refusal, so the T-03 audit alone or a pre-commit/CI check cannot discharge the ticket", why: "Striking the clause for a cheaper instrument would fail the ticket's own requirement text and AC-03" }
    - { reader: should-not-exist, severity: info, summary: "T-03's --against mode should be kept despite issue #1286 not requesting it; SC-12/AC-09 require the note's fenced row set proven identical to a re-run, and --against mechanizes exactly that comparison", why: "Striking it demotes SC-12 to a human diff of a fenced block — the manual step that rots and un-grades the criterion" }
  dismissed: []
  adequacy_notes:
    - "SC-06's unrebound two-finding baseline was not re-measured by the panel — scope traced the rebound one-element result by hand, but no reader re-ran the c3 prototype; if that count is wrong the rebinding rationale moves, not the assertion."
    - "SC-02 (test-first red proof) is ungradable at plan phase by construction; no panel finding bears on whether qa's later base-commit audit happens."
    - "This is not a shallow pass: should-not-exist verified run-unit-tests.sh:33 already calls violations(), scope opened SC-07/SC-09/SC-15's anchors and confirmed grep -c of T-05's asserted phrase is 0 — both readers ran probes that could have come back red."
    - "No security or UI lens ran; the team file defines exactly two steps and this change has no auth, secret, input or visual surface."
  must_fix: []
  files_touched:
    - ".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c3.md"
    - ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-07-validator/state.yaml"
    - ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-07-validator/digest.md"
    - ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-08-validator/state.yaml"
    - ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-08-validator/digest.md"
  branch: none
  open_questions:
    - { id: Q1, question: "Should the operator sign off by name on the disclosed unit.detect residual (extension-agnostic detect vs D-01's extension-restricted vocabulary), or file a follow-up ticket to reconcile them after ship? Both readers raised it; fixing it in-scope would require editing harness.json, which SC-14 freezes.", blocking: false }
    - { id: Q2, question: "Is D-05's archival blast radius acceptable as a standing operational landmine, or should archival tooling warn before archiving a DOCUMENTED_EXCEPTIONS path? Raised at med by scope and low by should-not-exist; both severities stand unreconciled by design.", blocking: false }
    - { id: Q3, question: "Should pm tighten T-03's intent with one clause stating the fenced row block and TOTAL line print unconditionally and that MISSING/EXTRA plus exit code are additive under --against? Without it a spec-compliant implementation can fail T-04's own verify:.", blocking: false }
    - { id: Q4, question: "Harness defect for the owner: the scope step's job exited non-zero while returning a well-formed VERDICT: PASS with a verified artifact — the reader emitted its digest fence twice, the second adding code_grade, apparently after the digest validator rejected the first. The return was accepted here only after verifying the artifact on disk.", blocking: false }
    - { id: Q5, question: "Harness defect for the owner: this panel occupies TWO run directories. The digest first written to runs/2026-09-04-07-validator/digest.md carried the panel's content in prose form without the §10.4 contract block; check-domain refuses any replacing write to an existing run digest, so the corrected contract-shaped digest had to open runs/2026-09-04-08-validator. No second dispatch occurred — 07 and 08 record the same single panel run, and 08 is canonical.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-08-validator/digest.md
```

**BLUF: the panel PASSES. Both readers ran, neither returned a `must_fix`, and no finding is high,
critical or unrated — so nothing on this panel must reach the operator as an unaccepted risk.
`severity_max: med`, carried by the D-05 archival coupling, which both readers found and both call a
disclosed, deliberate trade rather than a construction defect. The one actionable item is a `low`
spec ambiguity in T-03's `--against` output contract that can make T-04's own `verify:` fail on a
correct note.**

Graded against tip `1977ebd68d34cc0308968b03ad2d24399c0b5335` plus the uncommitted feature-directory
planning artifacts. No `review_sha` exists at this seam and none was asked for (DEC-207 / BUG-1080).

**Run-directory note.** This is one panel run recorded across two directories:
`runs/2026-09-04-07-validator/` holds the seeded `state.yaml` and a first digest written before the
contract block was added; the run digest is write-once, so the corrected canonical record is here in
`runs/2026-09-04-08-validator/`. No reader was dispatched twice.

## Readers

| step | persona | status | verdict | artifact |
|---|---|---|---|---|
| `should-not-exist` | `fable-advisor` | **ran** | PASS, 5 findings, none gating | none — no write grant; transcribed above |
| `scope` | `harness-code-reviewer` | **ran** | PASS, 4 findings, `must_fix: []` | `notes/review-harness-code-reviewer-planpanel-c3.md` |

Neither reader was skipped. `fable-advisor` resolved on this host and returned a well-formed
single-key `findings` block; no `on_fail` loop was entered and `cycles: 0` for both steps.

## Cross-referencing, not collapsing

Rows 2/3, 4/5 and 6/7 of `findings:` are one defect each — D-05's archival coupling, SC-06's
equality grader, and the `unit.detect` residual — found independently by both readers. Each side
keeps its own severity: reconciliation is forbidden here, and the med/low split on D-05 is itself
information for the operator. The two `--against` findings (rows 1 and 9) are **not** duplicates:
row 1 is a spec ambiguity in the mode's output contract, row 9 is a judgement that the mode should
exist at all. They interact — see ordering.

**Assessed and dismissed: none.** No reader claim was dropped; every finding carries a concrete
consequence, and neither reader padded.

## Ordering, if the operator elects to act

1. **Row 1 before anything else touching T-03.** Its remedy is one clause added to T-03's `intent:`
   — the row block and `TOTAL` line print unconditionally, `MISSING`/`EXTRA` and the exit code are
   additive under `--against`. A pm edit, not a plan restructure.
2. **That remedy must not be read as licence to strike `--against`** (row 9): removing the mode
   would break T-04's `verify:` outright and un-grade SC-12. The two resolve in the same direction
   only in this order.
3. **D-05 and the `unit.detect` residual are operator-visibility items, not work.** Both are already
   recorded in `plan.yaml` `decisions:` and `BRIEF.md ## Verification gaps`; the panel's contribution
   is that both readers independently judged them acceptable, and that `should-not-exist` recommends
   a follow-up ticket for the `detect` divergence rather than silence after ship.

## The gate

`must_fix: []` and `severity_max: med` → **PASS**. Nothing is high, critical or unrated, so no panel
finding requires the operator to accept a risk neither the lead nor pm may accept. Both approvals
remain `pending`; the panel wrote no `plan.yaml` and assigned no PF- ids.
