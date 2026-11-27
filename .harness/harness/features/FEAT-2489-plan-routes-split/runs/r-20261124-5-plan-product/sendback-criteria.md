# Send-back criteria — apply c3 (written before dispatch, P-05)

Lead pre-check at the worktree's check-plan-routes.py: structure-audit findings print
`{relative}::{symbol}:{node.lineno}` (lines 1922, 1940, 2108, 2138, 2360-2444), so a finding sited in
moved code changes file AND line number. Line-number member is real.

Send pm's apply back if any holds:

1. SC-02 item 5 states its class by source (producer names, rewritten fields, inventory rows) rather than by
   what the diagnostic prints: any diagnostic, any mode, either stream, whose leading locator (file path and,
   where printed, line number) names a site in moved code shows the new location; otherwise identical in text,
   multiset position and order. Producer names may appear only as illustration, never as the list.
2. The line-number member is omitted, or the class admits any change outside the locator.
3. T-02's comparison substitutes old->new across the whole line, or its mapping is not derived from the
   relocated identity set (old path::symbol -> new path::symbol, exactly the moved symbols), or it is applied
   anywhere except the diagnostic's locator.
4. T-02's task text does not say what happens to a line-numbered locator in moved code: either modelled
   (line remap derived from the move) or the checker FAILs on it. A loosening (ignore/wildcard line numbers) is a send-back.
5. T-01's checkpoint guard does not assert BOTH new modules absent at the recorded commit.
6. BRIEF's disclosed-departure note not reworded to the locator class.
7. Ruled scope touched: SC numbering SC-01..SC-05, new task, AST-identity checker, PF-b25f/PF-0e91/PF-6efa
   ancestor-and-blob binding, complete-install gap, approval.status (must stay pending).
8. `plan-merge.py check` failures > 0, or a PF id lacks a reported disposition; PF-6efa/PF-5dbe not recorded
   resolved (confirmed closed at c3); PF-2411/PF-6159/PF-b14b/PF-1dd0 not left open.
