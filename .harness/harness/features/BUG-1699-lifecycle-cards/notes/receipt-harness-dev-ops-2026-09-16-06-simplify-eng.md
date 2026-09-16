# EFFICIENCY inspection — BUG-1699-lifecycle-cards

## Conclusion

No substantive EFFICIENCY finding. The committed product diff `60b8d4d99f50edab6a63352ea43ebbc4ffc09750..212ad9ca` adds no repeated remote I/O, recurring startup work, hot-path computation, retained closure, or broad gate whose removal would preserve the settled lifecycle contract.

## Scope and cost basis

Static source/call-path inspection only; no tests, commands that exercise product behavior, or benchmarks were run. Product source inspected: `.claude/skills/harness/bin/{board_lifecycle.py,check-state.py,gh-sync.py,gh_board.py,plan-merge.py}`. Feature bookkeeping, plans, briefs, ledgers, prior receipts, and tests were excluded.

- `check-state.py:2211-2260` builds an in-memory candidate set before the board query. The diff's documented historical cost basis is a 918-item, 10-process whole-board read costing 11.25 s of a 14.3 s run; the added local feature reads are a deliberate bounded trade that avoids that recurring remote cost, not waste.
- `board_lifecycle.py:1086-1094` takes one audit snapshot and applies against it. The diff removes the former second identical four-call detection pass, so reconciliation does not add a recurring post-write board read.
- `gh-sync.py:1439-1460` retains the necessary closed-card guard but uses one targeted board lookup and one issue-state lookup for the card being moved; it does not restore the prior whole-board lookup. `gh-sync.py:1529` consumes one in-memory projection per status operation.
- `gh_board.py:126-150` performs only in-memory projection work. `plan-merge.py:858-921` reloads only on a task-set mutation that must derive and verify approval-resume metadata; no session-entry or recurring gate is added.

## Findings

[]
