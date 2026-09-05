# Advisor binding ruling — BUG-1304 plan phase — F1, T-09, backstop, T-08 — 2026-09-05

Fourth and final plan-phase ruling. Relayed by the main session and transcribed verbatim by the
orchestrator (the validator lead is denied `notes/`). It SELECTS the remedies the earlier rulings
left open; where it differs from `review-harness-code-reviewer-planpanel-c2.md` or from D-10's
recorded open choice, **this ruling governs**. The operator authorised it with no overrules and
extended the cycle allowance from 8 to 10.

Verdict: **REPAIRABLE** — one repair cycle plus one verification cycle. All four questions ruled
with no unresolved alternatives.

```json
{
  "verdict": "REPAIRABLE — one repair cycle plus one verification cycle. All four questions ruled below with no unresolved alternatives. Cycle allowance EXTENDED from 8 to 10 (hard max 20 not approached).",
  "Q1_unreadable_registry_vs_REQ03": {
    "ruling": "ADOPT REMEDY (a) — partial-S allow. D-10 is RETAINED, not struck; remedy (b) is REJECTED because it repairs the contradiction by amending REQ-03's promise to fit an implementation ordering, accepting a factory-wide stop of every governed write as the price of a per-write question. Remedy (a) is sound under any superset of S (a destination inside a proven member stays inside S however many members a readable registry would add), keeps REQ-03 unamended, and keeps the fail-closed refusal for exactly the writes the readable roots cannot place — which includes SC-10's founding case verbatim.",
    "binding_semantics": "For a governed write with resolved absolute destination d: build S_p from every READABLE scanned registry (owner root plus every linked worktree), collecting the set U of unreadable registry paths. (1) d inside a member of S_p → ordinary allow path. (2) U empty → S_p is the full S; the ordinary D-01 rule applies unchanged, including empty-S unbound-allow. (3) U non-empty and d not inside any member of S_p → exit 2 on BOTH routes with the seam message naming EVERY file in U; this covers both S_p empty (SC-10's case) and S_p non-empty. An unreadable root is never read as 'no claims here'. A MISSING registry file still returns [] — absent and unreadable stay different answers.",
    "required_plan_repairs": [
      "BRIEF REQ-05, third half: add one scoping sentence — the unreadable-registry refusal binds exactly the governed writes the readable roots cannot place; a destination inside a worktree proven by a readable registry stays allowed while an unrelated scanned registry is unreadable. REQ-03 is NOT amended.",
      "BRIEF: new SC-12 (verify: automated, evidence: integration, BOTH routes): fixture with the writer's own claim in a READABLE registry proving its assigned worktree, and one UNRELATED scanned registry unreadable. Assert: a write inside the writer's own assigned worktree exits 0; a governed main-checkout write by the same agent exits 2 with stderr naming the unreadable file; the refusal half carries SC-06's full pre-change proof through bug1304_assert_pre_change_allows. SC-10 stands UNCHANGED (its only-claim-is-corrupt fixture yields empty S_p, non-empty U → refusal; paired well-formed control unchanged — no conflict with SC-12).",
      "D-10: rewrite the remedy paragraph to state (a) as SELECTED at signature; reduce remedy (b) to one line recording it rejected with the reason above; rewrite the cost paragraph to the (a) scope — the refusal binds every governed write the readable roots cannot place, never a write inside a proven member. The F2 fail-open-asymmetry paragraph stands as written.",
      "T-02 intent: replace the 'unresolved operator choice' paragraph with the selected ordering. Seam shape decided here, not left to the doer: inflight_registry.live_claims is UNCHANGED (absent → [], exists-but-unreadable → raise UnreadableRegistry per root). harness_boundary.claim_worktrees gains a third parameter, the resolved absolute destination; it builds S_p from readable roots while collecting per-root UnreadableRegistry; if destination lies inside a member of S_p it returns S_p without raising; else if U non-empty it raises UnreadableRegistry carrying EVERY unreadable path; else returns S_p. The membership test uses the same containment primitive the guards use, so the two comparisons cannot drift.",
      "T-01: rewrite unit case 7 — claim_worktrees with a destination OUTSIDE the partial S raises UnreadableRegistry carrying the offending path(s), owner-root registry included; ADD unit case 8 — with one root's registry unreadable and a readable root proving a worktree containing the destination, claim_worktrees returns S_p and raises nothing. Integration cases 9/10 on live_claims unchanged.",
      "T-03: add the SC-12 case pair (own-worktree allow under unrelated corrupt registry; main-checkout refusal naming the file, routed through bug1304_assert_pre_change_allows). Verify floor moves from -ge 9 to -ge 10 — restate it as the panel-style exact floor so the L-04 tooth keeps zero slack.",
      "T-05: same pair on the Bash route (redirect inside own worktree exit 0; main-checkout redirect exit 2 naming the file). Verify floor moves from -ge 11 to -ge 12.",
      "T-04 and T-06: one added sentence each — pass the resolved absolute destination to claim_worktrees; the existing UnreadableRegistry catch-and-exit-2 clauses stand as written.",
      "T-07 obligation 1c: append the same scoping sentence (refusal binds the writes the readable roots cannot place)."
    ]
  },
  "Q2_T09_scope": {
    "ruling": "T-09 STAYS IN SCOPE. SC-11 stands; T-07 obligation 1b's strike sentence is not written. Grounds, verified in the worktree: dispatch-guard.sh calls the mutating live_claim on every dispatch and validate-digest.py calls live_children at every parent return, so a compatibility-host claim past 1200s is deleted FROM THE FILE on the routine suspend path — a read-side-only guard is then ceremonial on that host, and B-10 reopens verbatim. Advisor rulings A and B classified this as a defect this feature must close; the closure sits entirely inside files T-02 already owns; the answer/written seam split plus case_bug1304_retention_admission protects FEAT-37's 1200s single-flight admission. Deferring to a separate issue buys nothing except an interval in which the shipped guard does not guard."
  },
  "Q3_backstop_ttl": {
    "ruling": "RATIFY the existing OMP_UNVERIFIED_TTL_SECONDS = 86400 (inflight_registry.py:36) as the binding backstop. No new constant, no different value. Grounds: the value carries its own measured justification at :30-35 (12× the 7,200s longest measured leaf run, and a claim that never ages out strands its parent's yield through validate-digest.py's held-child gate); a second binding horizon would turn D-09's 'two questions over one stored claim' into three numbers, one of them unmeasured. The accepted residue — a genuinely live compatibility-host agent older than 24h silently unbinds — stands as D-09 records it."
  },
  "Q4_T08": {
    "ruling": "STRIKE T-08 at signature and FILE IT AS ITS OWN ISSUE (dispatch-guard.sh _root_for basename-equality → worktree_for_feature prefix alignment). Grounds, verified: _root_for's equality match at dispatch-guard.sh:122 with the owner-root fallback misplaces a short-form worktree's claim INTO the owner-root registry, and D-02/T-02 scan that registry and resolve every claim by its own feature field — T-01 claim_worktrees case 2 pins exactly this — so the enforcement remedy is placement-agnostic and the strike costs the remedy nothing, by the plan's own analysis and pm's and the product lead's shared recommendation. Retaining it would widen a two-gate bug fix into a third gate script. SC-08 (short-form worktree refusal, both routes) already pins the behavior T-08's re-runs were meant to cross-check, and T-10 runs the full suite regardless. Consequential edits: remove T-08 and its dependency mentions; the defect is real, so the follow-up issue is REQUIRED, not optional — file it alongside the two already-named separate issues (F2 linked_worktrees fail-open; OC-3 validate-digest live_children horizon)."
  },
  "cycle_extension": {
    "ruling": "EXTEND the plan allowance from 8 to 10 cycles (7 used). Cycle 8: pm implements this ruling exactly — BRIEF (REQ-05 sentence, SC-12), D-10 rewrite, T-01/T-02/T-03/T-04/T-05/T-06/T-07 edits, T-08 strike. Cycle 9: one panel verification pass confirming faithful transcription — F1 was HIGH and the repair touches the BRIEF plus six tasks, so it earns one independent read. Cycle 10: reserve for signature packaging only; no new scope may be introduced in it. No further extension is authorized by this ruling."
  },
  "consistency_note": "Post-repair the plan is internally consistent: REQ-03 unamended and honored (remedy a); REQ-05's third half scoped to match; SC-10 and SC-12 coexist on disjoint fixtures; D-09/T-09/SC-11 stand as a unit; D-10 states one selected rule; T-08 gone with no dangling depends_on (nothing depends on it) and T-10's depends_on already omits it. Everything above was verified against worktree source anchors, not taken from the plan on trust; the only [unverified] item is the exact panel floor counts 9/11, which I took from the plan's record of the panel's independent count rather than recounting the not-yet-written test files."
}
```

## Orchestrator's note on the one [unverified] item

The ruling flags the panel floor counts (`-ge 9` on T-03, `-ge 11` on T-05) as taken from the
plan's record rather than recounted. pm must therefore read the CURRENT floors out of `plan.yaml`
before moving them, and move them by +1 case pair from whatever is actually there — not to the
literal 10 and 12 above if the current values differ.
