# Grilling — governed file tools resolve relative paths against the main checkout (#1016, #1570) — 2026-10-04

## Destination
A governed agent under OMP that uses a relative path, or no path, with a file tool reads and writes
its assigned feature worktree, not the main checkout.

## Mission
mission: plan
reason: cause known, but the fix adds a new behaviour to the OMP enforcement adapter: the hook rewrites tool input across six tool shapes, including edit's hashline headers. That is a new enforcement surface, likely with its own DEC entry; DEC-174 main-session-direct.
confirmed-by: operator

## Settled
- Which tools? → All file tools: `read`, `grep`, `glob`, `edit`, `write`, `ast_grep`, `ast_edit` (their path arguments; edit's hashline section headers and `MV` destinations).
- Absolute paths? → Left untouched, including ones that point into the main checkout or a sibling worktree. Only relative paths are rewritten. Deliberate cross-checkout reads stay possible; writes there are already refused by #895.
- How is the worktree known? → Through the existing feature-root resolver (`worktree_for_feature` / `inflight_registry.py feature-root`) applied to the agent's `HARNESS-FEATURE`. No worktree means the feature lives in the checkout itself: no rewrite. An ambiguous match refuses. Dispatch text is never authority (DEC-250).
- Omitted path? → For tools that default to the cwd (`grep`, `glob`, `ast_grep`), an omitted `path` becomes the worktree root. Each relative entry of a `;`-separated path list is rewritten.
- Bash? → Out of scope.

## Not yet specified
- Internal URIs (`agent://`, `xd://`, `local://`, …) and `~` paths are not relative filesystem paths. They must pass through unrewritten, so BUG-2003's scheme decision still sees them. pm may sharpen the exact predicate.
- Whether an agent sees that its path was rewritten (e.g. an advisory line), or the rewrite is silent.
- The main session and Claude Code host are presumably unchanged; pm to confirm as criteria.

## Out of scope
- Bash cwd: agents already `cd` or use absolute paths; rewriting shell text is much riskier.
- Absolute-path remapping between checkouts.
- Changing OMP itself (a subagent inherits the parent cwd; `src/task/executor.ts` `effectiveCwd = worktree ?? cwd`).

## Facts I verified (so pm does not re-derive them)
- OMP 18.6.0 has no read-content cache: `src/tools/read.ts` reads disk and recomputes the tag per call. A sequential probe (change via bash, then `read`) returned fresh content and a new tag. Checked 2026-10-04.
- A subagent's cwd is its parent's: `src/task/executor.ts:4059` `const effectiveCwd = worktree ?? cwd;` (`worktree` is set only for isolated tasks). Harness subagents therefore start in the main checkout.
- #1570: `read` showed `harness-init/SKILL.md` at 370 lines, which was main's version at the time (`e88182c1`, `4b5dbb23`); bash showed 279 (feature branch, `464ab8b5`).
- #1016: `read` showed `validate-digest.py` at 1068 lines; bash showed 1505. Both versions existed on 2026-08-29 on different lines of history (`0a120c65`/`66e9a9d6` vs `17106762`).
- FEAT-43 B22: a stray feature directory appeared in the main checkout from a relative-path write. Same mechanism.
- `grep`, `glob` and `ast_grep` default `path` to the cwd; `path` accepts `;`-separated lists (OMP tool schemas).
- The OMP hook can revise tool input: the bash branch already returns a revised `input` (env) from `tool_call` in `.omp/extensions/harness-hooks.ts`.
- Findings are recorded on #1016 (issuecomment-5981161666); #1570 points to it.
