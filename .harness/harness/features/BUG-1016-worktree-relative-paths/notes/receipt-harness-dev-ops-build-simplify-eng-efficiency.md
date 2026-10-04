# Receipt — harness-dev-ops — BUG-1016 T-01 simplify, EFFICIENCY angle

Verdict: PASS, findings [] (read-only; no builds/tests run; `python3 tests/unit/test-omp-hooks.py` not run, per contract).

Scope read: `git diff 8d79d63d..89b7d960 -- .omp/extensions/harness-hooks.ts` (hot path: `tool_call` at ~1174, `tool_result` at ~1451, `featureRoot` ~981).

## Checked, not wasteful
- Resolver subprocess (`inflight_registry.py feature-root`): runs once per run, then served from `featureRootCache` (harness-hooks.ts:983-1005); cache is also hit when the root equals cwd. Refusals are uncached by design (settled).
- Calls with nothing to root (absolute/URI/tilde/blank, non-path tools) return before any resolver or spawn (`needsRoot`, :1017, `rootCall` :1022-1023).
- Post hook roots only write/edit (:1453), so reads/greps pay nothing there; edit input is already absolute after pre-rooting, so post's `needsRoot` is a no-op scan.
- `extractEditPaths` now one regex pass (was two) and shares `EDIT_TARGET`; net reduction.
- Cache key `JSON.stringify` of 3 short strings per call: negligible.

## Residual, below flag threshold (not a finding)
`needsRoot` (:1017) builds a throwaway rewritten input via `rootedInput(..., "/")`, then `rootCall` builds it again with the real root only when the cache/root is ready. For `edit` that is one extra regex replace over the patch text per rooted call (linear in patch size). Cost unmeasured [INFERENCE]: far below the per-call policyRunner subprocess gates it precedes. Collapsing it would restructure the predicate/placeholder design the plan settles; no change recommended. Impact on named BUG-1016 tests if changed: would risk the "rooting at a placeholder changes input exactly when real root does" agreement; not worth it.

Findings: []
