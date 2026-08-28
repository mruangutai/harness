# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: runs/goalcheck-product/digest.md
- squad: none — validate COMPLETE, awaiting the operator's ship decision
- status: Review

**VALIDATE IS COMPLETE. SIX TASKS DONE, QA GREEN, PANEL PASS, GOAL-CHECK PASS.** Runs 19/20 with run
20 unspent. Cycles 1/10, and that one cycle predates this session — every segment here returned ZERO
send-backs. `review_sha` `4e652f9`. Briefing at `notes/ship-review-2026-08-27-02.md`.

**SEVEN SCs MET BY THEIR OWN DECLARED METHODS. SC-08 IS not_met AND STAYS THAT WAY.** It is the
declared post-merge deferral (D-13) and the ONLY criterion measuring conduct; everything else grades
text on disk. This build proved the deferral first-hand: the stop guard refused me repeatedly reading
"this refusal fires ONCE" — the MAIN checkout's `inflight_registry.py:274` — while the branch's
corrected text at `:339` reads "at most once per consecutive stop sequence". Every agent here read the
unedited playbook. The operator runs SC-08 from the main checkout after merge.

**THREE ITEMS NEED THE OPERATOR AND NONE BLOCK.** (1) DEC-70's narrowing reached DECISIONS.md,
DECISIONS-INDEX.md and SPEC.md but NO surface an agent preloads when classifying —
`harness-qa-gate/SKILL.md:40`, `harness-ai-dev.md:38,41`, `harness.json test_matrix` are all
unqualified, confirmed by my own grep; pm and validator-lead independently recommend a backlog row
rather than a retro-added SC. (2) T-09's signed `verify:` calls `gen-decisions-index.py --check`, a
flag that never existed; the property is gated by SC-06 instead, which exits 0. (3) SC-05's BRIEF
citations are stale (`:112`→`:126`, `:181`→`:196`), confirmed by three independent measurements;
BRIEF is approval-gated and was NOT edited.

**THE MOST DURABLE FINDING IS THAT AN ENUMERATED GATE CANNOT SEE PAST ITS OWN LIST.** SC-07 named two
once-only sites; a third lived in SPEC.md and would have shipped falsified with every criterion green.
It was caught by the docs sweep's diligence, not by any gate.

**SIMPLIFY WAS NOT RUN, AND THE REASON IS STRUCTURAL rather than the cost argument I first gave.** It
must precede the `review_sha` pin, because an apply commit after the pin invalidates the panel's
verdict. The panel has graded at `4e652f9`, so running it now costs the panel run too — two runs
against a budget holding one. Accept the omission, or re-open it with a fresh pin and a fresh panel.

**ALL SEVEN INV-26 VIOLATIONS CLEARED** on the Review station write, no card touched by hand and
`check-state.sh` untouched. No PR and no merge — both the operator's.

## Open Questions

- Q1 (was: the eval's author) — CLOSED by the strike. No eval, no author.
- Q2 (was: the grader firing one rule alongside others) — MOOT. The grader is unwound.
- Q3 (the route checker validating against the wrong config) — folded into issue #910 as scope, by
  operator ruling. Not this feature's work.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files.
- Q6 (the #866 deadlock) — half closed by FEAT-42. The dispatch end is fixed; the return end is what
  this feature corrected. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry.
  CONFIRMED by measurement 2026-08-27, and Q5-of-the-t09-run is an instance of it: the registry is one
  file at the OUTER root, `.harness/.inflight-claims.json`, shared by every worktree.
- Q8: a lead holds no `SendMessage`, so a finding made after dispatch cannot reach a member in
  flight. That is D-03's deliberate consequence, not a defect to fix here. Backlog.
- Q9: the `gates` block in `harness.json` — `qa_gate`, `review`, `uat`, `merge` — is read by NO
  script. Agents honour it as prose. Folded into issue #910 by operator ruling.
