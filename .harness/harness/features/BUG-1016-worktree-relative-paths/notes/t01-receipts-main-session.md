# T-01 receipts — main-session-direct (DEC-174) — 2026-10-04

Commit: 10f38a42. Verify `python3 tests/unit/test-omp-hooks.py`: exit 0, 123 pass / 0 fail, 5.7s. `run-unit-tests.py --kind all` exit 0.

## Red-first (new cases against the unmodified adapter, fixture extended only)

```
(fail) OMP task lifecycle adapter > BUG-1016: a relative path on every path tool is rooted in the worktree, other fields kept [0.47ms]
(fail) OMP task lifecycle adapter > BUG-1016: each list entry is judged alone; absolute, ~ and URI entries stay byte-for-byte [0.16ms]
(fail) OMP task lifecycle adapter > BUG-1016: dot, parent, glob, selector, archive and SQLite text is preserved after the root [0.15ms]
(fail) OMP task lifecycle adapter > BUG-1016: an omitted or null search path becomes the worktree root; required paths are never invented [0.19ms]
(fail) OMP task lifecycle adapter > BUG-1016: blank strings and blank list entries are kept verbatim and need no lookup [0.23ms]
(fail) OMP task lifecycle adapter > BUG-1016: edit sections and MV destinations are rooted; hashes, rows and line endings are not [0.20ms]
(fail) OMP task lifecycle adapter > BUG-1016: the resolver is asked once per call with the run's own feature, and cached for the run [0.12ms]
(fail) OMP task lifecycle adapter > BUG-1016: no worktree for the feature means no rewrite, cached or not [0.10ms]
(fail) OMP task lifecycle adapter > BUG-1016: an unusable or refused resolver answer refuses the call, and is never cached [0.22ms]
(fail) OMP task lifecycle adapter > BUG-1016: worktree prose in the assignment is never authority [0.13ms]
(fail) OMP task lifecycle adapter > BUG-1016: sibling runs resolve their own worktrees [0.10ms]
(fail) OMP task lifecycle adapter > BUG-1016: a held run is refused before any rewrite, even after a cache fill [0.10ms]
(fail) OMP task lifecycle adapter > BUG-1016: write and edit gates judge the rooted file, pre and post, revised or original input [0.20ms]
(fail) OMP task lifecycle adapter > BUG-1016: BUG-2003's URI rule holds beside a rooted sibling, MV included [0.14ms]
 109 pass
 14 fail
```

The two BUG-1016 cases that passed before the change are controls (absolute/~/URI/main/Bash untouched; silent success), not red-first.

## Mutation checks (each reverted after)

- No cache reset at run start: 1 fail. Post judges the unrooted input: 1 fail. A resolver reason without a block accepted: 1 fail. A multi-line root accepted: 1 fail. `~` rooted: 3 fail. Pre judges the unrooted input: 3 fail. A no-match root still rewrites: 12 fail.

## Smoke with the real resolver

Real `inflight_registry.py feature-root` behind the hook: for BUG-1016 (has a worktree) `read BRIEF.md:1-3`, an omitted grep path and an edit section were rooted in the worktree; `/etc/hosts` was untouched. For BUG-2003 (no worktree) nothing was rewritten.

## Deviations and findings for the panel

- OMP's `ast_edit` takes `paths: string[]`, not `path` (installed 18.6.0 `src/tools/ast-edit.ts` astEditSchema). Each array entry is rooted as a path list; nothing is invented when `paths` is absent.
- Pre-existing, not changed here: `ast_edit` mutates files but is not in the hook's mutation set (`write`, `edit`, `bash`), so it gets no authorization or domain gate.
- `extractEditPaths` now reads the shared EDIT_TARGET matcher (sections first, then MV, deduplicated), with unchanged results on every existing case.
