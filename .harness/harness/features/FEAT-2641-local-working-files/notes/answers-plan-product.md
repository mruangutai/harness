# Operator answers — FEAT-2641 plan-product ESCALATE — 2026-11-27

Answered by the operator through the main session. Each answer is the operator's ruling.

- **OQ-02 (blocking): decline all five.** BUG-2451, FEAT-2557, BUG-2565, BUG-2566 and FEAT-2581 (shipped with no distill commit on origin/main, verified by the main session with `git log origin/main --grep`) are declined; their lessons are dropped, and no preservation step or snapshot is needed. The plan records the declines. If the new skip-distill verb (GC-01) exists by landing, use it to record them; otherwise record them however pm judges fit. Their working files are lost to checkouts when the untracking commit lands, which the operator accepts. They stay in git history.
- **LEAD-01 (blocking): re-read.** One scope re-read of the applied text of T-03, T-05, T-06, T-07 and T-09 (T-09's landing commands included), run after the OQ-02 and GC-01 answers are applied, so it also covers whatever those answers change.
- **OQ-01: keep D-07.** Ship's `notes/handoff-validate.md` refusal is replaced by the `feature.json` precondition (a validator validate or fix run recorded PASS), not deleted.
- **GC-01: automatic, overriding the documented follow-up.** `set-feature-station` runs the cleanup when it writes `rejected`, and a skip-distill verb is added that records a declined distill and runs the same cleanup. The evidence-safety concern stands: cleanup runs only after the station write has succeeded.
- **OQ-03: accept the documented repair.** `git rm -r --cached --sparse`, recorded in `checkout-upgrade.md` by T-07.
- **OQ-04: manual.** This feature's grilling and facts notes in `.harness/notes/` are not claimed as project notes; the operator cleans them up by hand.
- **OQ-05: ignore.** Not filed.
- **ORCH-01: no ruling.**
