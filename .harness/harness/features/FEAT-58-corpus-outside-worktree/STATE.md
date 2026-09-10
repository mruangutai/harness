# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: SECOND BATCHED FIX APPLIED, cycle 0, 2026-09-10. The operator's cycle-5 answers (`notes/answers-operator-c5.md`) landed whole and the panel affirmed the Q6 strike removed only what it was meant to. On disk: BRIEF.md at 10 REQ / SC-01..SC-14 (SC-15 struck, surviving only as its own strike record at `BRIEF.md:106-116`), plan.yaml at 11 tasks (N-01..N-10, N-12 — N-11 retired into N-10) and 15 decisions, `status: plan`, both approvals `pending`. Handoff: notes/handoff-plan.md
- squad: none — awaiting the operator's third batched signature review
- status: awaiting_user
- gate: the final panel (`planpanelfinal-validator`) returned FAIL, `severity_max: high`. Both readers RAN, neither skipped, and BOTH returned PASS on their own charters — the FAIL is three NEW highs (PL-01, PL-02, PL-03) plus one med (PL-04) ranked to land with them. Two of the three share one root cause: nothing in the plan ever runs the shipped `check-state.sh` against the REAL repository, so every assertion runs against a fixture whose dirs and records agree by construction. DEC-207 forbids a pre-signature fix dispatch and no agent may risk-accept a high.
- verified at my own tier, not taken on the panel's word: `ls -d .harness/harness/features/*/ | wc -l` = 89 against `feature.json` = 79, so the expected-set/reached-set key mismatch is real; and `branch-create-gate.sh`'s `deny()` at `:63-66` prints its payload then `exit 0`, exactly as the allow path at `:91-92` does, so an ALLOW assertion on exit status cannot distinguish allow from deny.
- budget: cycles_used 6 of 10. runs 40 of a 20-run informational budget — INV-22 notes a long feature and never stops one.

## Open Questions

- PL-01 (high) — N-06 PART 1 keys the expected set differently from the reached set, so the audit exits 2 with "reached 89 of 79" at the owner root and in every fresh clone. Ten record-less directories carry non-ignored tracked notes. Remedy named: key both the same way, or restrict both to `feature.json`-carrying dirs.
- PL-02 (high) — D-12's preflight gates on `--verify` exit 8, so `check-state.sh`, which its own header at `:24` calls the canonical pre-commit gate for the whole repository, refuses in every dirty feature worktree, and exit 8's stated remedy is the commit it is refusing ahead of. **The remedy amends SC-09's last sentence in BRIEF.md, which is approval-gated — the operator makes that edit, not pm and not a fix cycle.**
- PL-03 (high) — N-10 PART 7 clause (c) asserts the ALLOW path by `exit 0`, which cannot distinguish allow from deny. Remedy named: assert the printed output is NOT a `permissionDecision: deny` payload, and carry N-07 PART 4(b)'s never-assert-exit-status warning across.
- PL-04 (med, ranked to land WITH the highs) — no assertion anywhere runs the shipped `check-state.sh` against the real owner root or inside a dirty worktree. This is the common root of PL-01 and PL-02; point fixes without it leave the class free to recur.
- The nine prior findings VL-01..VL-09 now carry forward `resolved` with `resolved_by`, correcting GC5-01; `panel.prior_cycle` retains the 13-row disposition from the cycle before. One known blemish, deliberately not sent back: VL-07's `resolved_by` pointer has the right line range and the wrong path prefix — the amended DoD note is at `.harness/notes/`, not the feature's `notes/`. The next writer of `panel` corrects it.
- Filed as their own tickets, untouched here: #1595, #1596, #1597, #1598, #1630, #1631, #1635, #1636, #1637, #1638.
