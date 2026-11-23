# Sign-off by delegated authority — FEAT-2397 — 2026-11-22

## Delegation

On 2026-11-22 the operator, Mike Ruangutai, said: **"start feature C. same rules, defer to
fable-advisor."** These are the same rules as FEAT-2337. Every question and approval for this
feature, from grilling through merge, goes to the `fable-advisor` agent instead of the operator.
Each ruling is recorded in this feature's `notes/answers-*.md`. The grilling rulings
(`AdvisorC1Grill`) are in `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-cleanup-c-2026-11-22.md`.

## Presented

To `fable-advisor` (`AdvisorC2Signoff`) at plan HEAD `e0b7933f`:
- BRIEF.md and plan.yaml, both pending:
  - 6 tasks, all main-session-direct (DEC-174);
  - 12 SCs from 3 perspectives;
  - 4 D-NN and 36 decision dispositions.
- Runs r-1 (plan-product), r-2 (simplify-eng) and r-3 (simplify-apply-product), all PASS.
- The proposed rework: 2 rounds / 90 min (6 tasks, 3 per round, floor 2; 45 min per round).

## Ruling (fable-advisor, on the operator's behalf)

1. **Approved, with named conditions.** Every settled grilling item is honoured, which the advisor
   verified item by item, with anchors re-confirmed at `e0b7933f`. The plan's one scope expansion
   is accepted: eight extra decision rewrites and a DEC-188 strike of DEC-111 (PF-4fe19). The
   grilling destination "current-tense doctrine" covers it.
2. **Rework: 2 rounds / 90 minutes.**
3. **Conditions (binding):**
   1. **Early host tripwire.** As soon as T-04 is green, Main runs the repaired probe once on the
      live, credentialled host as an informal smoke test. If the observation fails, Main stops and
      returns to fable-advisor before starting T-05. The formal T-06 receipt still lands after
      T-05, at the final pin.
   2. **#9 (iii) stays first to cut.** The only allowed scope shrink is that the drift check stays
      a subprocess, with all four states intact. Any such cut comes back to fable-advisor first;
      no other Settled item may shrink.
   3. **SC-10 runner.** Main may run the probe directly in the operator's environment. The receipt
      must record a real credentialled invocation: launcher, reported version 19.1.0, command,
      output and exit code. A synthetic or inferred run does not count.
4. **Backlog, not fixed here:**
   - Re-examine #1248 and #612 at ship; they are likely mooted by T-01 and T-06.
   - The six hermetic sanitizer lines that unset `CLAUDE_PROJECT_DIR` are an optional sweep for
     whenever those files are next touched.

Signed by the main session as `Mike Ruangutai (delegated to fable-advisor)`.
