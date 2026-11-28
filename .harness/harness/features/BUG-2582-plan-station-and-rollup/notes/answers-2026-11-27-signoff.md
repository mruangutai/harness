# BUG-2582 sign-off: operator answers, 2026-11-27

Source: plan run `2026-11-27-01-plan-product`. Its VERDICT was FAIL, forced by DEC-123's worst-member roll-up over two readers that returned FAIL to carry findings; all 6 findings are `resolved` in `plan.yaml`. The questions are the lead's OQ-1 (a)–(c) and OQ-2, asked in one form. The main session put a recommendation on each, and the operator chose it every time.

- **OQ-1 (a): accept.** pm's apply resolved the 4 high reader findings, and no re-read run is needed. Validation reviews the built code against every SC.
- **OQ-1 (b): keep T-05.** The plan team's `teams/plan.yaml` apply step runs `set-panel` after `record-panel`, and DEC-228 is amended. Without it, the defect-2 carve-out never fires.
- **OQ-1 (c): accept D-04.** There is no dispatch-guard change. The apply-written INV-34 stub can start a plan; a hand-written stub stays refused, as at base.
- **OQ-2: yes.** Qualify `validate-digest.py`'s header statement that "the top verdict must be the WORST member verdict" while building T-02, which edits the same file.
- **Signature: approved.**
- **Rework ruling: 2 rounds / 90 minutes**, the `propose-rework` baseline (plan mission, 5 tasks at 3 per round, floor 2; 45 minutes per round).
