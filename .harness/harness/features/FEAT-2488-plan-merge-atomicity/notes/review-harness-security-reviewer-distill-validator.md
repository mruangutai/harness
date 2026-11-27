# Security distillation — FEAT-2488

**Two craft rules retained; no mandatory live-execution rule.** This was distillation only: no diff reviewed, governed route executed, or suite run.

| Candidate | Disposition |
|---|---|
| 1. Journal trust boundary | **Applied as P-14.** Compare discovery, producer and write-authorization name sets, including implicitly created ancestors. The review sequence (`review-harness-security-reviewer-c1.md` through `-c5.md`) showed why neither authorized replay destinations nor leaf-name checks alone settle the boundary. |
| 2. Terminal routing | **Applied as O-08.** State what decides class membership and impact, then route to the ruling tier. The final ruling (`answers-2026-11-24-validate-c4-ship.md`, S1) distinguished a closed discovery invariant from an availability-only perimeter gap with one-command recovery and parity with an already-ruled route. |
| 3. Execute the governed route before rating high | **Rejected.** The earlier replay-authority finding and terminal availability finding had different impact and evidentiary support. Lack of live execution is not a severity ceiling: separate measured effects and source-traced reachability per existing O-04, and state uncertainty where the trace does not establish a link. |

Craft section counts before → after: Patterns 15 → 15; Gotchas 15 → 15; Outcomes 10 → 10; Open 0 → 0. No repository-tier operations.

Batch `bef98f3be11cb6d00be01810a9922e9013cc9907f2c36d786f7e6ac617753e5f`; [tool receipt](expertise-receipt-54c73b4a590c7f9d0f81cb487aa28a7e02229ff65957224990897643fbccf725.json). Open questions: none.
