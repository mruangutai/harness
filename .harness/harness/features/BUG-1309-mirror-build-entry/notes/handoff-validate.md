# Handoff — BUG-1309-mirror-build-entry, validate → ship — written at 3f69a522, seq-4

## Next

**Nothing is dispatchable. The next act is the OPERATOR's, not an agent's.** SC-10
(`BRIEF.md:157-159`) is `verify: uat` and is the only thing between this feature and a ship
decision. The main session presents `notes/uat-BUG-1309-mirror-build-entry.md` — Steps 1–2 setup,
then **Step 3** (`:152-157`) — and the operator judges the refusal message against the PASS
condition quoted at `:175-177`. Only when they return PASS does a ship-phase successor write the
rewritten CEO briefing and dispose of `notes/ship-review-2026-09-08-resume.md`'s B-1..B-13 plus
Q9–Q13 in STATE.md. **Do not re-dispatch a validator: the copy delta is fully graded.**

## Trust

- The copy at `merge-gate.py:192` names the feature and carries a runnable recovery command, with
  the operator's two rejected jargon phrases gone — rendered by invoking the REAL gate, not read
  off source — `notes/research-BUG-1309-c19-goalcheck-copy.md` §1 — verified-at 4857818b
- Integration suite 36 ok / 0 FAIL / rc=0, matching the c18 baseline — `notes/qa-c19-copy.md` —
  verified-at 4857818b
- The re-anchored assertion genuinely binds the sentence: neutralising it reddens
  `T-05 recovery-required denies` — `notes/qa-c19-copy.md` (qa's scratch worktree) and the
  orchestrator's own probe recorded in `STATE.md` — verified-at 4857818b
- All 26 byte-frozen T-05 case names still resolve individually; `code_grade` 4 against a floor of
  ≥4, zero margin — `runs/c19copy-validator/digest.md` — verified-at 4857818b
- UAT Steps 3/3b already match the rendered string character for character; no edit was owed and
  none was made — `notes/research-BUG-1309-c19-goalcheck-copy.md` §2 — verified-at 4857818b
- No BRIEF amendment and no re-signature are owed; no criterion text moved — R-7 §3 confirmed by pm
  — `notes/research-BUG-1309-c19-goalcheck-copy.md` §3 — verified-at 4857818b
- Test-first ORDER for 4857818b — **UNVERIFIED.** Source and both test hunks are in one commit with
  no intermediate red; the main session's pre-edit red observation is credible but the tree does not
  corroborate it — `notes/qa-c19-copy.md`, STATE.md Q12 — UNVERIFIED

## Dead ends

- Do not spend a cycle on the `{feat}` non-discrimination — behaviour is correct at the pin and the
  remedy needs the D-11 carved-out test file — STATE.md Q9, `runs/c19copy-validator/digest.md` V-C
  — verified-at 4857818b
- Do not "fix" `merge-gate.py:188`'s surviving jargon in this feature — ruling R-7 §1/§3 scopes it
  out explicitly — `notes/rulings-2026-09-08-c19-copy.md` §1 — verified-at 4857818b
- Do not re-pin `review_sha` to 3f69a522 — that commit carries feature-dir artifacts only, and
  moving the pin would claim the panel reviewed a tree it never saw — `feature.json` — verified-at
  3f69a522
- Do not treat INV-29's worktree violations as this feature's — every one names another feature —
  `check-state.sh` output recorded in STATE.md — verified-at 3f69a522

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/STATE.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/rulings-2026-09-08-c19-copy.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`

## Done when

Scope: the operator executes UAT Step 3 and returns PASS or FAIL on the refusal message
Authority: brief-sc:SC-10
