# plan-panel c4 — validator digest — BUG-1286-test-tree-enforcement

Canonical digest for the cycle-4 `plan-panel` run. The panel itself ran ONCE, in run directory
`2026-09-04-13-validator`; this directory exists only because that run's `digest.md` was written
with `status: ran` on its member rows and without an `artifact:` scalar, the schema permits `status`
only as `skipped`, and the digest write guard refuses an in-place repair. No finding, severity,
reader disposition or assessment differs from `2026-09-04-13-validator/digest-final.md`; the two
readers were dispatched and returned exactly once.

```yaml
VERDICT: PASS
DIGEST:
  headline: Amended plan passes the fresh cycle-4 panel at severity_max med with nothing gating; the one substantive finding is that the invariant justifying the whole widening - the guard must be at least as wide as unit.detect - is stated in three places and asserted by zero tests, and only the non-harness reader saw it.
  team: plan-panel
  steps_run: 2
  cycles_used: 0
  members:
    - { step: should-not-exist, persona: fable-advisor, verdict: PASS, headline: "Ran and looked; nothing in the amended plan should be struck, and the load-bearing guard-covers-detect invariant is unasserted", files_touched: [] }
    - { step: scope, persona: harness-code-reviewer, verdict: PASS, headline: "Ran and looked; two-group vocabulary coherent at all five sites, SC-18 graders exist as described, Fix 1 unbreakable on a faithful note, zero orphan REQs", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c4.md"] }
  must_fix: []
  files_touched:
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c4.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-13-validator/state.yaml
    - .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-13-validator/digest.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-13-validator/digest-final.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-14-validator/digest.md
  branch: none
  severity_max: med
  high_critical_or_unrated_present: false
  open_questions:
    - { id: Q1, question: "harness defect, non-blocking: the scope step's return was recorded failed (exit 1) by the host while its artifact exists and is substantive; the reviewer emitted four consecutive digest blocks, three of them carrying findings as the scalar 0 where a list is contracted. The verdict was identical and unambiguous in all four, so no re-prompt was spent.", blocking: false }
    - { id: Q2, question: "harness defect, non-blocking: validate-digest rejects a member row carrying status ran, while the team skill's own reporting template shows a member row with a status key; and the file it validates is always <run_dir>/digest.md derived from the artifact path, so an artifact pointing at a sibling file in the same run directory is not the file checked. A lead that follows the template therefore writes a digest.md it cannot repair, because the digest write guard refuses replacement, and the only route left is a second run directory - which is what this directory is. One run, one panel, two directories.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
  adequacy_notes:
    - "Neither reader could grade SC-02 (test-first red proof) or SC-12/SC-13 (graded at review_sha): they are ungradable at plan phase by construction, not gaps the panel missed."
    - "scope returned an empty findings list. That cannot by itself distinguish a clean specification from a shallow pass, so the discriminator is falsification evidence, and both readers produced it independently: two different enumerations of the tracked tree (scope by git ls-files, should-not-exist by git ls-files plus a whole-history sweep, pm's goal-check by git ls-tree) that could have disagreed on 85/9/0 and did not, plus 0-hit non-vacuity checks on both of T-05's greps."
    - "No reader can tell you whether the two-group split stays true of harness.json, only that it is true of harness.json today. That is exactly the med finding, and it is the panel's blind spot made explicit rather than closed."
    - "The panel graded text. Nothing here is evidence about code, and the census counts 85/9/0 were re-measured against the working tree, not against any future review_sha."
readers:
  - { reader: should-not-exist, persona: fable-advisor, disposition: ran }
  - { reader: scope, persona: harness-code-reviewer, disposition: ran }
findings:
  - reader: should-not-exist
    persona: fable-advisor
    severity: med
    summary: The guard-at-least-as-wide-as-detect invariant that justifies the entire widening is asserted by no test and can silently decay the first time a future feature edits unit.detect
    consequence: >-
      D-01's because, BRIEF's closure bullet and T-05's DEC-213 amendment all rest on the guard
      covering everything unit.detect discovers, argued from a snapshot of harness.json. A later
      feature that widens a detect glob re-creates the counted-by-the-map, permitted-by-the-guard,
      executed-by-no-runner defect this ticket exists to close, with no failing test and no signal
      until someone re-reads DEC-213's prose.
    lead_verification: >-
      Upheld at source. tests/unit/test-suite-layout.py:102 asserts only that the repo's
      test_kinds[kind].detect equals the TEMPLATE's detect - not a pinned value, and not any relation
      to the guard's vocabulary. A widening applied to both files passes it. The reader's
      characterisation is exact.
    ranking: 1
    remedy_owner: harness-pm
    remedy_window: closes at signature
  - reader: should-not-exist
    persona: fable-advisor
    severity: low
    summary: T-03's note parser inherits a find-all-fences pattern while T-04 never caps the note at one fenced block, so a correct audit note with a second fence can fail the comparison
    consequence: >-
      T-04's verify exits non-zero on a semantically correct audit, and whoever debugs it suspects the
      instrument rather than the note's shape. One sentence closes it - T-03 says first fenced block
      only, or T-04 says the note carries exactly one fenced block.
    lead_verification: >-
      Adjudicated at source; the two readers disagreed and each is half right. suite-census.py:24 is
      re.findall over EVERY block, so should-not-exist has the mechanism right and scope's
      first-block reading is wrong. But the pattern accepts only an empty or text info string, so a
      fence tagged bash or console is invisible, and scope is right that the trigger needs a BARE or
      text-tagged second fence carrying row-shaped lines that DIFFER from the measured set - a
      duplicate or a subset produces no diff. Also right that the fault is build-time and
      self-correcting, not a shipped defect. The finding survives at the reader's own low with its
      trigger set narrowed; scope's counter-claim narrows it and does not dismiss it.
    ranking: 2
    remedy_owner: harness-pm
    remedy_window: closes at signature
  - reader: should-not-exist
    persona: fable-advisor
    severity: info
    summary: No spec-compliant reading of the amended output contract makes T-04's verify fail on a correct note; the fix-1 wording closes the cycle-3 gap
    consequence: >-
      Reported as a clearance, not a defect: the row block and TOTAL line are unconditional, on stdout
      and before any comparison output, so the grep anchor holds in comparison mode and the combined
      exit rule returns 0 exactly when rows match and no violation row exists.
    lead_verification: Corroborated independently by scope section 4, which traced the same readings and also found none that breaks.
    ranking: 3
    remedy_owner: none
    remedy_window: none
  - reader: should-not-exist
    persona: fable-advisor
    severity: info
    summary: The widening breaks no assertion authored against the narrower rule; SC-06, the 85/9/0 counts and T-04's dispositions all survive, verified independently
    consequence: >-
      Reported as a clearance: none of case 1's six fixture basenames matches the agnostic pair
      (test_rogue.py carries test_ as a prefix, not _test. as an infix), so SC-06's one-element
      exact-equality list stays satisfiable, and zero tracked paths outside tests/ match the agnostic
      pair, so no row changes disposition.
    lead_verification: Corroborated independently by scope section 3, which re-measured 85/9/0 by its own enumeration and confirmed case 1 and case 10 are kept on separate fixtures.
    ranking: 4
    remedy_owner: none
    remedy_window: none
  - reader: should-not-exist
    persona: fable-advisor
    severity: info
    summary: Keep verdict on every questioned element; the agnostic widening is grounded insurance and the two-group split is enforceable without being memorized
    consequence: >-
      Reported as a keep decision: across the repository's entire git history exactly one path was
      ever added whose basename matches the agnostic pair (omp-hooks.test.ts, a real test now inside
      tests/unit), and zero Markdown, JSONL or note files ever, so the false-positive surface the
      dispatch asked about is empirically near-empty over the repository's lifetime rather than only
      on today's tree. Striking any questioned element would un-trace a ticket AC.
    lead_verification: >-
      The only new evidence in the panel bearing on the lifetime question, and no code-reading lens
      could have produced it. Recorded so a future cycle cites this measurement rather than re-runs it.
    ranking: 5
    remedy_owner: none
    remedy_window: none
  - reader: scope
    persona: harness-code-reviewer
    severity: none
    summary: Empty findings list from a reader that genuinely looked; the amendment holds at all five split sites, SC-18's graders exist as described, and no verify clause is vacuous
    consequence: >-
      No consequence to report - recorded as a real outcome, not a finding. What makes it credible
      rather than silent: three independent re-derivations that could have disagreed - 85/9/0 by its
      own git ls-files enumeration, a grep sweep for surviving blanket extension claims, and 0-hit
      preflight checks on both of T-05's grep targets.
    lead_verification: Artifact verified present and substantive at notes/review-harness-code-reviewer-planpanel-c4.md, sections 1 through 5.
    ranking: none
    remedy_owner: none
    remedy_window: none
cross_references:
  - topic: Fix 1, T-03's amended output contract against T-04's verify - both readers asked whether a correct note can still fail and both independently found no reading that breaks it
    readers: [should-not-exist, scope]
    note: Two readers, one conclusion, not collapsed - scope carries it as section 4 with no finding raised, should-not-exist as an info finding.
  - topic: The multi-fence note-shape hazard - the panel's ONE direct disagreement; should-not-exist raises it at low on a find-all-fences reading, scope dismisses it on a first-block reading plus a self-correcting-gate argument
    readers: [should-not-exist, scope]
    note: Resolved by the lead at suite-census.py:24, not averaged. findall is correct, the info-string filter narrows the trigger, the fault is build-time. Finding stands at low.
  - topic: The census measurement TOTAL 85 OUTSIDE 9 VIOLATIONS 0 and the agnostic-pair count of zero outside tests/
    readers: [should-not-exist, scope]
    note: Three independent enumerations agree (both readers plus pm's goal-check, by two different git plumbing commands). The panel's strongest evidence, and a corroboration rather than a finding.
assessed_and_dismissed:
  - item: scope's counter-reading that a second fenced block cannot affect the comparison because baseline()'s regex takes only the first block
    reason: False at source - suite-census.py:24 is re.findall, not re.search. Dismissed as a dismissal; the finding it argued against survives.
  - item: should-not-exist's own considered-and-declined option of dropping probe-* from the repository-wide vocabulary, which would moot D-05's exception machinery
    reason: Declined by the reader itself before it became a finding, correctly - it is the operator's accepted-cost item by another door, and SC-10's positive coverage needs the live registry entry. Recorded so a later cycle does not mistake its absence for an oversight.
  - item: D-05's FEAT-44 exception, its archival coupling, and the cycle-3 findings the amendment addresses
    reason: Off the table by operator ruling at the signature gate. Both readers respected it; scope re-checked D-05's DESCRIPTION for a new inaccuracy against probe-omp-session-accessor.py lines 54-55 and found none, which was the only question still open.
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-14-validator/digest.md
```

## What the panel adds beyond the two notes

**Nothing gates.** `must_fix` is empty, `severity_max` is `med`, and no finding is `high`, `critical`
or `unrated` — so nothing here has to reach the operator as a risk they must personally accept. The
amendment survived a fresh adversarial read. Both readers ran; neither was skipped or refused by
preflight.

**The one finding worth a plan edit is invisible from inside either lens alone.** `scope` graded
whether the two-group split is stated coherently across its five sites, and it is;
`should-not-exist` asked whether the split's *premise* is durable, and it is asserted nowhere. Both
are correct. The gap lives in the union: `tests/unit/test-suite-layout.py:102` pins the repo's
`detect` to the *template's* `detect`, so a widening applied to both files passes every existing gate
while falsifying D-01's `because`, BRIEF's closure bullet and T-05's DEC-213 text at once. The
remedy the reader proposes — one assertion in `tests/unit/test-suite-layout.py`, a file T-01 already
owns and already edits — is neither of the two alternatives the engineering tier rejected in
`notes/review-harness-eng-lead-plan-c0.md`, both of which concerned `violations()` itself.

**Ranked by remedy window, not by severity.** Both actionable findings are one-sentence or
one-assertion edits to an *unsigned* plan, and both become a post-signature amendment the moment the
operator signs. That ordering is the lead tier's to supply: neither reader can see that the cheap
window is closing.

**What the panel could not tell you** is in `adequacy_notes`. The load-bearing one: the split is
verified true of `harness.json` *today* by three independent measurements, and nothing in the plan
makes it stay true.

Reader artifacts: `notes/review-harness-code-reviewer-planpanel-c4.md` (scope).
`should-not-exist` holds no write grant; its findings exist only in this digest, transcribed at its
own severities and with no PF- id assigned.
