# Receipt — tests-reuse (BUG-1016 T-01), harness-backend-dev

BLUF: one REUSE candidate (F1, low cost, no behavior change). Read-only; nothing run (T-01 verify `python3 tests/unit/test-omp-hooks.py` not executed). Diff inspected: `git diff 8d79d63d..89b7d960 -- tests/unit/omp-hooks.test.ts` (+281/-4). Read: angle-reuse.md, delete-first.md.

## Findings

### F1 — `rootedHooks()` restates `governedUriHooks()`
- file/line: `tests/unit/omp-hooks.test.ts:1291-1317` (new `rootedHooks`) vs existing `:1028-1052` (`governedUriHooks`, BUG-2003).
- summary: ~25 lines are the same harness: `fixture()` -> bare `Map` + `registerHarnessHooks` with a runner wrapper that blocks `check-domain.py` when `tool_input.file_path` equals one forbidden literal -> `ompContext("/repo","LeadOne","OrchestratorOne","parent-session")` -> `start` -> `domainTargets` -> `pre` -> `post`. Only three things differ: forbidden target (`FORBIDDEN` vs `${WT}/forbidden.ts`), a `featureRoot` answer passed to `fixture`, and `toolCallId` (`call-uri` vs `call-rooted`), plus the extra `lookups`, `hooks`, `ctx` returns.
- cost: two spellings of the pre/post/domainTargets/blocker plumbing must be edited in lockstep (e.g. if the `tool_call`/`tool_result` event shape or the ctx identity changes); the BUG-2003 copy is the one nobody revisits and goes stale silently. Delete-first: the new helper is a net addition where a parameter would do.
- alternative: give `governedUriHooks` an options arg `{ featureRoot?, forbidden? = FORBIDDEN }` that forwards `featureRoot` to `fixture({ featureRoot })`, and also returns `lookups`, `hooks`, `ctx`. Define `rootedHooks = (featureRoot = worktreeAnswer) => governedUriHooks({ featureRoot, forbidden: `${WT}/forbidden.ts` })` or call it directly, and delete the 25-line body. The BUG-2003 callers (`governedUriHooks()` with no args) stay unchanged. `toolCallId` can be shared as `call-uri` because no BUG-1016 assertion reads it.
- exact test-name impact: none. No test is renamed, deleted or weakened. All 16 `BUG-1016:` tests keep their names and assertions. The BUG-2003 tests (`agent:// and xd://report_issue skip the domain gate...`, `every other scheme is refused by name...`, etc.) are untouched in behavior. Only helper bodies change.
- BUG-1016 behavior change: none (test-fixture only).
- angle: reuse.

## Checked and not flagged
- `fixture()` extension (`featureRoot` option, `cwd` in `calls`): reuses the existing runner and `option` helper; the default answer keeps every other case unchanged. Reuse is correct.
- `start`, `ompContext`, `extractEditPaths` are imported/reused, not restated. `cleanExpected` assertion deliberately compares against the real `extractEditPaths` (settled shared matcher).
- Hand-built hashline strings in the BUG-1016 tests (`[forbidden.ts#1A2B]\nPUT 1:\n+x`, `:1523`, `:1526`, `:1540`) resemble `uriEdit(...)` (`:1025`) for single-target cases only. Mixed multi-section literals cannot use it. Below the cost threshold; not raised, and literal expected strings are settled.
- main-session setup inside the "untouched" test (`:1391`ff) is a one-off, not raised.

files_touched: []
