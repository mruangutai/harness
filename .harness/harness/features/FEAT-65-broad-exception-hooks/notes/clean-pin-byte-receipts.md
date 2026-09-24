# FEAT-65 — clean-pin byte receipts (SC-08)

Implementation pin: `79b7c268` (resolved HEAD `79b7c2682a4ca174aa19f48259d10d3b60bb43e5`). Clean detached checkout `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat65-cleanpin-79b7c268` via `git worktree add --detach`; `git status --porcelain` at the checkout: empty.

Each suite: `HARNESS_PROJECT_DIR=<checkout> python3 <checkout>/<suite>`, cwd `<checkout>`. Digests are sha256[:16] of the raw stream; the final stdout line is quoted as the suite's own verdict.

THIS RECEIPT IS COMMITTED IN A LATER COMMIT ON THE FEATURE BRANCH AND DOES NOT CLAIM TO EXIST INSIDE THE PIN IT NAMES (FEAT-64 GC-64-04/QA-64-02 lesson).

| Task | Suite | exit | stdout sha | stderr sha | last stdout line |
|---|---|---|---|---|---|
| T-01 | `tests/integration/test-check-domain.py` | 0 | `75be33c60abd75af` | `e3b0c44298fc1c14` | `ALL PASSED` |
| T-01 | `tests/integration/test-check-domain-artifact.py` | 0 | `20462b48ed57b467` | `e3b0c44298fc1c14` | `ok    [bug151-selfcheck] wiring-seam-catches-print-fail-return-zero` |
| T-01 | `tests/integration/test-check-domain-claims.py` | 0 | `5eeb78f4c75cb8c9` | `e3b0c44298fc1c14` | `PASS  [bug1304] partial unreadable is allowed by the frozen pre-change hook` |
| T-01 | `tests/integration/test-check-domain-grant.py` | 0 | `6ab214e0c7242614` | `e3b0c44298fc1c14` | `ok    schema/the live feature_schema.py was never written (bytes and mtime unchanged)` |
| T-01 | `tests/integration/test-check-domain-post.py` | 0 | `630a86fe7444aabb` | `e3b0c44298fc1c14` | `ok    handoff worktree-only brief-sc pointer refused` |
| T-01 | `tests/integration/test-check-domain-worktree-parity.py` | 0 | `0f05a1a008bbbf95` | `e3b0c44298fc1c14` | `49/49 worktree grant-parity cases passed.` |
| T-01 | `tests/integration/test-check-domain-worktree.py` | 0 | `51d19db1e52bb91a` | `e3b0c44298fc1c14` | `12/12 b2 cwd-independence cases passed.` |
| T-01 | `tests/integration/test-check-domain-approval.py` | 0 | `c7794321f8e0d333` | `e3b0c44298fc1c14` | `28/28 T-14 cases passed.` |
| T-02 | `tests/integration/test-validate-digest.py` | 0 | `f5cb25d9df05a30e` | `e3b0c44298fc1c14` | `ALL PASSED.` |
| T-02 | `tests/unit/test-code-grade.py` | 0 | `a6133575d90833b8` | `e3b0c44298fc1c14` | `PASS test-code-grade` |
| T-03 | `tests/integration/test-bash-write-guard.py` | 0 | `c5f5de6f51976c86` | `e3b0c44298fc1c14` | `PASS  [bug1304] partial unreadable is allowed by the frozen pre-change guard` |
| T-03 | `tests/integration/test-branch-create-gate.py` | 0 | `fb0ea577ff1d1e21` | `e3b0c44298fc1c14` | `9/9 cases passed.` |
| T-03 | `tests/integration/test-dispatch-guard.py` | 0 | `f89829d7caaf3795` | `e3b0c44298fc1c14` | `85 of 85 cases passed` |
| T-03 | `tests/unit/test-feature-record.py` | 0 | `e3b0c44298fc1c14` | `8e18fe6215250a41` | `` |
| T-03 | `tests/integration/test-gh-close-gate.py` | 0 | `c938ecba1dce3d30` | `e3b0c44298fc1c14` | `ALL PASSED` |
| T-03 | `tests/integration/test-inflight-registry.py` | 0 | `12327690623b4491` | `da6f5bfb48f793ec` | `PASS - 144/144 checks passed` |
| T-03 | `tests/integration/test-inject-expertise.py` | 0 | `49035c70c1384ff8` | `e3b0c44298fc1c14` | `21/21 cases passed.` |
| T-03 | `tests/integration/test-merge-gate.py` | 0 | `be41d360798b2ffb` | `e3b0c44298fc1c14` | `ALL PASSED` |
| T-03 | `tests/integration/test-plan-sign-gate.py` | 0 | `fdf654d77d0babf5` | `e3b0c44298fc1c14` | `all checks passed.` |
| T-04 | `tests/unit/test-broad-catch-census.py` | 0 | `ca5f5c39c959da1b` | `e3b0c44298fc1c14` | `ALL PASS` |
| T-04 | `tests/unit/test-harness-boundary.py` | 0 | `14d569909492d386` | `c6a545cdac96989d` | `ALL PASS` |

## AST census at the pin

```
{
 "bash-write-guard.py": 0,
 "branch-create-gate.py": 0,
 "check-domain.py": 0,
 "dispatch-guard.py": 0,
 "feature-record.py": 0,
 "gh-close-gate.py": 0,
 "inflight_registry.py": 0,
 "inject-expertise.py": 0,
 "merge-gate.py": 0,
 "plan-sign-gate.py": 0,
 "validate-digest.py": 0,
 "harness_boundary.py": 2
}
```

Eleven hooks total: 0; harness_boundary.py: 2.

`BROAD_CATCH_CEILINGS` at the pin: `{'harness_boundary.py': 2}`.

## Five-way DEC-234 prologue identity at the pin

| Copy | sha256[:16] of `_resolve_root` source |
|---|---|
| `branch-create-gate.py` | `3e8090b621e61b7f` |
| `gh-close-gate.py` | `3e8090b621e61b7f` |
| `merge-gate.py` | `3e8090b621e61b7f` |
| `plan-sign-gate.py` | `3e8090b621e61b7f` |
| `run-unit-tests.py` | `3e8090b621e61b7f` |

Identical: True; tuple `except (ModuleNotFoundError, ValueError):` present in every copy: True.

All verify commands exit 0: True.
