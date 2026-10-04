# Receipt — plan-simplify · efficiency angle · BUG-1016 (harness-dev-ops)

BLUF: **Efficiency result: 1 low finding (kind: substance), no blocking waste.** Read-only; nothing applied.

## Measurements
- `inflight_registry.py feature-root` costs ~58 ms/spawn (5 runs, 0.288 s total, this worktree). Per governed file call that is small; the settled success cache (PF-0cdd7bb1) already covers repeat lookups. Not reopened.

## Finding E-1 — post callback's root source is unspecified; may double the lookup per mutating call
- kind: substance (efficiency cost, plan-text gap)
- file/line: plan.yaml, T-01 `intent`, paragraphs on pre/post ("the post callback must remain correct whether its input is already revised or the original input"; "obtain at most one root per call needing rewriting"). Code context: `tool_result` reads `event.input` (harness-hooks.ts:1232) and calls `postDomain` (:1353), a separate handler from `tool_call`.
- summary: The "at most one lookup per call" bound is stated for the `tool_call` side only. If `event.input` reaches post as the original relative input, post must re-derive effective paths and, with the cache merely "permitted", spawns a second resolver per write/edit (and a post-time failure mode the plan has not specified).
- cost: +~58 ms and one extra python spawn per relative write/edit when no cache is built; plus an unspecified post-time refusal path. Small per call, but wholly avoidable.
- alternative (plan text): state that post reuses the root resolved in the same call's `tool_call` (e.g. keyed by `toolCallId`, dropped at result), or that a success hit in the permitted cache is the only post source and a miss is a named refusal. Add the assertion "write/edit with original-input post performs 0 additional resolver calls" to the existing "at most one lookup per rewriting call" check.

## Considered, not flagged
- T-01 verify (`test-omp-hooks.py`, whole omp-hooks.test.ts, <60 s): the co-changed enforcement suite at its own boundary; deliberate full run, not waste.
- T-02 verify (`gen-decisions-index.py --stdout | diff`): a targeted, sub-second index-consistency check; T-02 depends on T-01 legitimately (DEC text describes landed behavior).
- Red-first runs against the unmodified adapter: one extra run of the same file, required by TDD, not waste.
- Test matrix cross-product (six tools x relative/blank/selector cases): table-driven cases against one lexical predicate cost milliseconds at runtime; any consolidation is a proportionality/form matter outside this angle.
- Cache-related test burden and the resolver-per-call tax: settled (PF-0cdd7bb1 resolved), not reopened.

```yaml
VERDICT: PASS
DIGEST:
  headline: Efficiency angle returns one low finding - post-callback root source unspecified, risking a second resolver spawn per mutating call; no other plan waste
  change_type: infra
  applied: []
  suite: n/a
  task: none
  test_kinds_written: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/receipt-harness-dev-ops-plan-simplify-eng-efficiency.md
```
