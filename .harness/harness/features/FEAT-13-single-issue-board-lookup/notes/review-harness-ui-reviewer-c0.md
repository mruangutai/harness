# Mode B UI review — FEAT-13-single-issue-board-lookup — c0

## Verdict: PASS (in scope on one adjacent surface; no rendered UI in this diff)

## Scope determination (measured, not inferred)

`git diff 6dfbf7c..d4951c2 --name-only | sed 's/.*\.//' | sort | uniq -c` at the worktree root:

```
   4 md
   9 py
   1 yaml
```

No `html/css/scss/tsx/jsx/vue/svelte/less` anywhere in the diff. No `DESIGN.md` exists for this
feature at all (`find .harness/features/FEAT-13-single-issue-board-lookup -iname DESIGN.md` —
empty). There is no rendered surface and no contract to audit it against. Confirmed by direct
inspection, not by trusting the dispatch's framing (P-01, P-02).

The dispatch named two adjacent surfaces explicitly and asked for a yes/no on each.

### 1. Operator-facing CLI output — IN SCOPE, judged, holds

The diff adds `factory_gh.issue_board_item_id` (new `GhError` raise sites) and two new "issue is
not open" refusals in `factory_claim.py` and `factory_land.py`. All follow the existing house
grammar (`factory_cli.body(what, value, next_step)` → `factory: {tool}: {what}: {value} —
{next_step}`, `.claude/skills/harness/bin/factory_cli.py:32-43`):

- New `GhError`s in `factory_gh.py` (malformed repository, gh graphql call failed ×2, repository
  not found, missing/non-int totalCount, truncated, unrecognised node shape) all carry the
  `(what, value, next_step)` triple and reuse existing phrasing verbatim where the condition is
  the same as an existing one (`"gh graphql call failed"`, `"cannot verify the read was not
  truncated"`) — internally consistent with the pre-diff file.
- `factory_claim.py:284-287` refuses `"issue is not open"` via `factory_cli.refuse` → exit
  `EXIT_REFUSED = 2`. `factory_land.py` raises the equivalent `GhError` for the same condition,
  caught by `factory_cli.run(..., expected=(...GhError))` which also exits `EXIT_REFUSED = 2`
  (`factory_cli.py:85-87`). Checked directly: **both paths exit 2 for the same semantic
  condition** — no cross-tool inconsistency introduced.
- One low-severity, non-gating observation: `issue_board_item_id`'s truncation message ends
  "...widen the query" but no CLI flag on `claim`/`decompose`/`land` exposes a query or limit
  parameter to act on — verified via `grep -rn -- "--limit\|--query" factory_claim.py
  factory_decompose.py factory_land.py`, no matches. This is **not a new defect**: the
  pre-existing `project_items` truncation message ("widen `--limit` or narrow with `--query`",
  `factory_gh.py:187-192`, unchanged by this diff) has the identical property — neither is
  actually operator-actionable through these three CLIs. The new message is arguably more honest
  for not naming a flag that doesn't exist. Note only, does not gate.
- Terminal rendering/line-wrap of the longer new messages (e.g. the truncation message, which
  concatenates repo, issue number, both counts and the next_step) is not verifiable from source —
  a source-level review cannot see how a real terminal wraps it. Flagging per this role's known
  limit, not as a finding.

### 2. Comments/docstrings rewritten to stay truthful — OUT OF SCOPE, explicitly declined

Doc/comment truthfulness against the code they describe is a code-review/QA concern, not an
accessibility/interaction/visual-design one. Not this role's lane; no judgment rendered.

## Files inspected

- `.claude/skills/harness/bin/factory_gh.py` (new `issue_board_item_id`, its `GhError` sites)
- `.claude/skills/harness/bin/factory_claim.py` (`--issue` lookup swap, closed-issue refusal)
- `.claude/skills/harness/bin/factory_land.py` (`_find_item_id` swap, closed-issue check)
- `.claude/skills/harness/bin/factory_decompose.py` (`_find_existing_item_id` swap)
- `.claude/skills/harness/bin/factory_cli.py` (message grammar, `run()` exit-code mapping)
- `.harness/features/FEAT-13-single-issue-board-lookup/` (confirmed no `DESIGN.md`)
