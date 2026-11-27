# Security distillation — one craft replacement

**Accepted C-SEC2; rejected C-SEC1.** No diff reviewed or suite run during distillation.

- **C-SEC1 rejected at cap.** The c0 Q2 ruling showed that the newly widened refusal trigger gave the same actor no new capability; the existing fallback remains backlog. Enumerating every result that reaches the branch would have improved the original review, but it is a concrete way to apply P-09’s base comparison and P-12’s capability-delta grading, with P-02 checking actor parity and P-07 checking changed routing. Six spawns out, that extra prompt does not displace a separate review rule.
- **C-SEC2 accepted as craft (replace Gotchas G-05).** The c0 Q1 ruling weighed observed evidence loss against disabling the supported repair commands for the same damaged state. G-15 asks what evidence cleanup must preserve, and P-11 asks what downstream enforcement loses; neither asks whether the proposed refusal leaves a working repair route. That check would change future reviews of damaged-state recovery and is stronger than G-05’s fix-cost heuristic, which can cut reachability analysis short.

Sources: `review-harness-security-reviewer-c1.md`, `answers-2026-11-25-validate-c0.md` (Q1/Q2), and the three validation lead digests. The later ruling and validation records carry the original security review forward rather than re-running it.

Applied: craft Gotchas `replace G-05` (DEC-145/219/253). Tool counts before → after: Patterns 15 → 15; Gotchas 15 → 15; Outcomes 10 → 10; Open 0 → 0. Repository tier untouched.

Batch: `48f451add109a13bdb6d40311a6c0d684d11db938fde0c46348689e090fbd6b5`  
Receipt (beside this note): `expertise-receipt-d44ec07c51ddfbafa1c8bae59041418b4710c894374297742dd7e489a8353672.json`

Open questions: none.
