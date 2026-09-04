# Team digest — plan-panel — BUG-1286-test-tree-enforcement — cycle 3

**BLUF: the panel PASSES the drafted plan. Both readers ran, neither returned a `must_fix`, and no
finding is high, critical or unrated — so nothing on this panel must reach the operator as an
unaccepted risk. `severity_max: med`, carried by the D-05 archival coupling, which both readers
found and both call a disclosed, deliberate trade rather than a construction defect. The one
actionable item is a `low` spec ambiguity in T-03's `--against` output contract that can make
T-04's own `verify:` fail on a correct note.**

Graded against tip `1977ebd68d34cc0308968b03ad2d24399c0b5335` plus the uncommitted feature-directory
planning artifacts. No `review_sha` exists at this seam and none was asked for (DEC-207 / BUG-1080).

## Readers

| step | persona | status | verdict | artifact |
|---|---|---|---|---|
| `should-not-exist` | `fable-advisor` | **ran** | 5 findings, none gating | none — no write grant; transcribed here |
| `scope` | `harness-code-reviewer` | **ran** | PASS, 4 findings, `must_fix: []` | `notes/review-harness-code-reviewer-planpanel-c3.md` |

Neither reader was skipped. `fable-advisor` resolved on this host and returned a well-formed single-key
`findings` block; no `on_fail` loop was entered and `cycles: 0` for both steps.

## Findings — every survivor, at the reader's own severity

Severity is transcribed, never reassigned. No PF- ids: pm computes identity once at transcription.

| # | reader | sev | summary (reader's own wording, wrapping collapsed) | concrete consequence |
|---|---|---|---|---|
| 1 | scope | low | T-03's `--against` output contract doesn't state whether the row/TOTAL block still prints under comparison mode | A spec-compliant "diff-only" reading of the same text makes T-04's own `verify:` fail on a correct note, forcing rework |
| 2a | scope | med | D-05's accepted archival landmine | Archiving FEAT-44's evidence file reddens every `run-unit-tests.sh` invocation repo-wide until a backend-dev/dev-ops edit, though the archiver need not hold that grant |
| 2b | should-not-exist | low | The D-05 coupling should be accepted at low severity; archiving FEAT-44's evidence file reddens every runner invocation with a loud self-describing one-line finding fixable by a one-tuple-entry edit, and the only alternatives are rewriting a landed feature's shipped record or letting exceptions go silently stale, which breaches AC-07 | A rare deliberate act (archiving landed evidence) requires routing a trivial `suite_layout.py` edit to backend-dev or dev-ops before any test can run again; the failure names its own remedy |
| 3a | scope | info | SC-06 exact-equality is acceptable, not brittle in the way asked | None — the pinned string is introduced by T-01 itself, so a later wording change is owned by the same task, not cross-feature brittleness |
| 3b | should-not-exist | info | SC-06's exact-equality grader should stand; whole-list equality is the only assertion form that proves the valid unit, integration and manual files and the copied bin module each contributed nothing, and the pinned finding string is also asserted at the runner boundary in T-02 | Brittleness cost is one deliberate re-pin whenever the message is intentionally changed, which must already coordinate with T-02's `MISCONFIGURED` assertions |
| 4a | scope | info | `harness.json` `detect` residual: disclosure is sufficient, does not gate | None gating — disclosed, measured by T-03's unfiltered selection, empty at the tip; raised as a non-blocking open question for explicit operator awareness |
| 4b | should-not-exist | low | The `unit.detect` residual should not gate the signature but should not end at disclosure either; the only in-scope fix edits `harness.json`, which AC-11 and SC-14 forbid, so gating deadlocks the feature against itself | Shipping with disclosure alone leaves a standing hole no instrument watches after review, because T-03's audit runs at `review_sha` rather than on every invocation; the right consequence is a follow-up ticket, not a block |
| 5 | should-not-exist | info | The repository-wide clause and every task carrying it should be built; the per-invocation `git ls-files` tax is a delta of two subprocesses inside a layout gate `run-unit-tests.sh:33` already runs on every invocation, and issue #1286 explicitly mandates pre-dispatch refusal | Striking the clause for a cheaper instrument (audit-only, pre-commit, CI) would fail the ticket's own requirement text and AC-03 |
| 6 | should-not-exist | info | T-03's `--against` mode should be kept despite issue #1286 not requesting it; SC-12/AC-09 require the note's fenced row set proven identical to a re-run, and `--against` is the mechanization of exactly that comparison | Striking it demotes SC-12 to a human diff of a fenced block — the kind of manual step that rots and un-grades the criterion |

**Cross-referenced, not collapsed.** Rows 2a/2b, 3a/3b and 4a/4b are one defect each, found
independently by both readers; each side keeps its own severity because reconciliation is forbidden
here and the split is itself information. Rows 1 and 6 both concern T-03's `--against` and are
**not** duplicates: 1 is a spec ambiguity in its output contract, 6 is a judgement that the mode
should exist at all. They interact — see ordering below.

**Assessed and dismissed: none.** No reader claim was dropped; every finding above carries a concrete
consequence, and neither reader padded.

## Ordering, if the operator elects to act

1. **Finding 1 before anything else touching T-03.** Its remedy is one clause added to T-03's
   `intent:` — the row block and `TOTAL` line print unconditionally, `MISSING`/`EXTRA` and the exit
   code are additive under `--against`. It is a pm edit, not a plan restructure.
2. **Finding 1's remedy must not be taken as licence to strike `--against`** (Finding 6): removing
   the mode would break T-04's `verify:` outright and un-grade SC-12. The two findings resolve in
   the same direction only if applied in this order.
3. **Findings 2a/2b and 4a/4b are operator-visibility items, not work.** Both are already recorded
   in `plan.yaml` `decisions:` / `BRIEF.md ## Verification gaps`; the panel's contribution is that
   both readers independently judged them acceptable, and that `should-not-exist` recommends a
   follow-up ticket for the `unit.detect` divergence rather than silence after ship.

## The gate

`must_fix: []` and `severity_max: med` → **PASS**. Nothing is high, critical or unrated, so no
panel finding requires the operator to accept a risk neither the lead nor pm may accept. Both
approvals remain `pending`; the panel writes no `plan.yaml`.

## Adequacy — what this panel could not tell you

- **The two-finding unrebound baseline behind SC-06's grader was not re-measured.** The c3 append
  states it was measured on a throwaway prototype; the `scope` reader traced case 1's fixture by
  hand and confirms the *rebound* one-element result, but no reader re-ran the prototype. If that
  count is wrong the rebinding rationale, not the assertion, is what moves.
- **SC-02 (test-first red proof) is ungradable at plan phase by construction** — it is graded later
  by qa's audit against the base commit. No panel finding bears on whether that will happen.
- **Falsification evidence exists, so this is not a shallow pass:** `should-not-exist` verified at
  source that `run-unit-tests.sh:33` already calls `violations()` on every invocation, which is what
  collapsed the "standing tax" objection to a two-subprocess delta; `scope` opened SC-07, SC-09 and
  SC-15's anchors and confirmed each resolves, and confirmed
  `grep -c "tracked test-shaped file outside" DECISIONS-INDEX.md` is 0 so T-05's `verify:` is
  non-vacuous. Both readers probed and both could have come back red.
- **No security or UI lens ran.** The team file defines exactly these two steps, and this change has
  no auth, secret, input or visual surface — the absence is by design, not a coverage hole.
- **Host note:** the `scope` step's job exited non-zero while returning a well-formed `VERDICT: PASS`
  and a verified artifact (the reader emitted its digest fence twice, the second adding
  `code_grade`). Recorded as an open question for the harness owner; it did not affect the return,
  which was verified against the artifact on disk before being accepted here.
