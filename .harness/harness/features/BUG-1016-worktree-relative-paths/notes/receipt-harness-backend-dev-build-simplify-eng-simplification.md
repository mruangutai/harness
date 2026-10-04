# Receipt — BUG-1016 T-01 simplification angle (read-only)

VERDICT: PASS, findings: [].

Scope: `git diff 8d79d63d..89b7d960 -- .omp/extensions/harness-hooks.ts` (tests not separately judged for this angle). No commands run beyond reading the diff.

## Deletion test results
- `EDIT_TARGET` shared matcher: deleting it re-creates two regexes (extract + rooting) that can disagree. It earns its keep.
- `rootTarget` / `rootPathList`: the single path-rooting rule, called from the edit, ast_edit and path-tool branches. It earns its keep.
- `needsRoot` (`harness-hooks.ts` ~l.395): calls `rootedInput(..., "/")` to decide before the resolver runs. Removing it would run the resolver on every call. It is a two-line pass that avoids that, and it reuses one rule instead of a parallel predicate. Not flagged.
- `featureRoot` cache: one slot, key `[runtimeAgentId, currentFeature, cwd]`, reset at `openRun` and at agent end. Minimal state. Not flagged.
- `rootCall` in `tool_result`, limited to write/edit: re-derives from the cached root and avoids a resolver call for read-only tools. Not flagged.
- `extractEditPaths` rewrite keeps the original sections-then-moves order and de-duplication.

## Considered and rejected
- Making `needsRoot` lazy (pass a root thunk into `rootedInput`): it would change error ordering, since a resolver refusal currently only occurs when something needs rooting, and it saves one cheap pass.
- Merging `PATH_TOOLS` and `ROOT_DEFAULT_TOOLS`: they differ on purpose (read/write require a path).
