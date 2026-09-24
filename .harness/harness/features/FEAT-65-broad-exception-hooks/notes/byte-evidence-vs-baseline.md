# FEAT-65 — per-suite byte evidence vs baseline `4e8c73c0` (SC-01)

Generated per task at build time from the feature worktree against a detached baseline worktree; every non-identical line is an added case or a re-pinned case name (the divergences of operator-visible HOOK output are in `build-divergences.md`, D-01..D-14).

Baseline `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` vs head `dd1203a35c5166f3c95efb6e761106adc68d8646`.
Each suite run once per tree, `HARNESS_PROJECT_DIR=<tree> python3 <tree>/<suite>`, cwd `<tree>`.
`raw` digests are sha256[:16] of the untouched stream. `norm` digests are the same stream after exactly two
substitutions: the tree's own absolute path → `<ROOT>`, and any `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>`.
Under `Lines` every differing line of the NORMALISED streams is printed verbatim (unified diff, zero context);
a suite with `norm` digests equal and no lines listed is byte-identical up to those two substitutions.

## `tests/integration/test-check-domain.py`

- exit: baseline 0 → head 0
- stdout raw `25794188a1212337` → `75be33c60abd75af`; norm `25794188a1212337` → `75be33c60abd75af`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    a defect reading the payload passes through with exactly the hook_guard line
+ok    a defect in the feature-checkout rule is no longer absorbed: it is named on stderr
+ok    a defect in the claim rule is no longer classified locally: it is named on stderr
+ok    a --resolve defect passes through the same guard and answers no route
+ok    KeyboardInterrupt escapes the guard
+ok    a deliberate SystemExit keeps its own exit code
-17/17 T-06 check-domain cases passed.
+23/23 T-06 check-domain cases passed.
```

## `tests/integration/test-check-domain-artifact.py`

- exit: baseline 0 → head 0
- stdout raw `20462b48ed57b467` → `20462b48ed57b467`; norm `20462b48ed57b467` → `20462b48ed57b467` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-check-domain-claims.py`

- exit: baseline 0 → head 0
- stdout raw `5eeb78f4c75cb8c9` → `5eeb78f4c75cb8c9`; norm `5eeb78f4c75cb8c9` → `5eeb78f4c75cb8c9` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-check-domain-grant.py`

- exit: baseline 0 → head 0
- stdout raw `6ab214e0c7242614` → `6ab214e0c7242614`; norm `6ab214e0c7242614` → `6ab214e0c7242614` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-check-domain-post.py`

- exit: baseline 0 → head 0
- stdout raw `630a86fe7444aabb` → `630a86fe7444aabb`; norm `630a86fe7444aabb` → `630a86fe7444aabb` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-check-domain-worktree-parity.py`

- exit: baseline 0 → head 0
- stdout raw `0f05a1a008bbbf95` → `0f05a1a008bbbf95`; norm `0f05a1a008bbbf95` → `0f05a1a008bbbf95` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-check-domain-worktree.py`

- exit: baseline 0 → head 0
- stdout raw `4c5fabaf2d9e9fb6` → `51d19db1e52bb91a`; norm `4c5fabaf2d9e9fb6` → `51d19db1e52bb91a`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-ok    [feat61] an unexpected core failure is absorbed and the allowance stands
+ok    [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
```

## `tests/integration/test-check-domain-approval.py`

- exit: baseline 0 → head 0
- stdout raw `c7794321f8e0d333` → `c7794321f8e0d333`; norm `c7794321f8e0d333` → `c7794321f8e0d333` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## Summary

| Suite | exit | stdout norm-identical | stderr norm-identical | `-` lines |
|---|---|---|---|---|
| `tests/integration/test-check-domain.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-check-domain-artifact.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-claims.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-grant.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-post.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-worktree-parity.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-worktree.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-check-domain-approval.py` | 0→0 | yes | yes | 0 |

Baseline `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` vs head `e10c56ded36bde93f25c3c5748536689067453e2`.
Each suite run once per tree, `HARNESS_PROJECT_DIR=<tree> python3 <tree>/<suite>`, cwd `<tree>`.
`raw` digests are sha256[:16] of the untouched stream. `norm` digests are the same stream after exactly two
substitutions: the tree's own absolute path → `<ROOT>`, and any `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>`.
Under `Lines` every differing line of the NORMALISED streams is printed verbatim (unified diff, zero context);
a suite with `norm` digests equal and no lines listed is byte-identical up to those two substitutions.

## `tests/integration/test-validate-digest.py`

- exit: baseline 0 → head 0
- stdout raw `c1732373f3bcb9c3` → `31fa4cf294cdf93a`; norm `e23e34de16aaa006` → `70d0444c0c75ea5d`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    [feat65] a defect reading the payload passes through with exactly the hook_guard line
+ok    [feat65] an unreadable payload is the hook's own failure and takes the same template
+ok    [feat65] a defect in the registry errand is no longer reported in its own sentence
+ok    [feat65] KeyboardInterrupt escapes the guard
+ok    [feat65] a deliberate SystemExit keeps its own exit code
+ok    [feat65] the direct CLI is not wrapped: a validator defect is loud and nonzero
+
+6/6 FEAT-65 guard cases passed.
```

## `tests/unit/test-code-grade.py`

- exit: baseline 0 → head 0
- stdout raw `a6133575d90833b8` → `a6133575d90833b8`; norm `a6133575d90833b8` → `a6133575d90833b8` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## Summary

| Suite | exit | stdout norm-identical | stderr norm-identical | `-` lines |
|---|---|---|---|---|
| `tests/integration/test-validate-digest.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-code-grade.py` | 0→0 | yes | yes | 0 |

Baseline `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` vs head `ec0996cbab571664a43e95f8b70b660f41577b33`.
Each suite run once per tree, `HARNESS_PROJECT_DIR=<tree> python3 <tree>/<suite>`, cwd `<tree>`.
`raw` digests are sha256[:16] of the untouched stream. `norm` digests are the same stream after exactly two
substitutions: the tree's own absolute path → `<ROOT>`, and any `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>`.
Under `Lines` every differing line of the NORMALISED streams is printed verbatim (unified diff, zero context);
a suite with `norm` digests equal and no lines listed is byte-identical up to those two substitutions.

## `tests/integration/test-bash-write-guard.py`

- exit: baseline 0 → head 0
- stdout raw `5e5372529c62479c` → `c5f5de6f51976c86`; norm `5e5372529c62479c` → `c5f5de6f51976c86`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-ok    [feat61] an unexpected core failure is absorbed and the allowance stands
+ok    [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
+ok    [feat65] a defect in the claim rule is no longer classified locally: it is named on stderr
+ok    [feat65] a defect reading the payload passes through with exactly the hook_guard line
+ok    [feat65] KeyboardInterrupt escapes the guard
+ok    [feat65] a deliberate SystemExit keeps its own exit code
+
+4/4 FEAT-65 guard cases passed.
```

## `tests/integration/test-branch-create-gate.py`

- exit: baseline 0 → head 0
- stdout raw `92ad7f6f17236541` → `fb0ea577ff1d1e21`; norm `92ad7f6f17236541` → `fb0ea577ff1d1e21`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-8/8 cases passed.
+9/9 cases passed.
```

## `tests/integration/test-dispatch-guard.py`

- exit: baseline 0 → head 0
- stdout raw `35b3099f64159867` → `f89829d7caaf3795`; norm `35b3099f64159867` → `f89829d7caaf3795`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS  feat65: a claim-step defect passes through hook_guard, named
+PASS  feat65: the registry's own unreadable class keeps the typed claim-step sentence
+PASS  feat65: KeyboardInterrupt escapes the guard
+PASS  feat65: a deliberate SystemExit keeps its own exit code
-81 of 81 cases passed
+85 of 85 cases passed
```

## `tests/unit/test-feature-record.py`

- exit: baseline 0 → head 0
- stdout raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)
- stderr raw `b171b48b4540ea74` → `36d1b9b5cd290184`; norm `b171b48b4540ea74` → `36d1b9b5cd290184`

Lines (stderr):
```
-........................................................................
+..........................................................................
-Ran 72 tests in 17.800s
+Ran 74 tests in 20.048s
```

## `tests/integration/test-gh-close-gate.py`

- exit: baseline 0 → head 0
- stdout raw `95c878d6051f8131` → `c938ecba1dce3d30`; norm `95c878d6051f8131` → `c938ecba1dce3d30`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
```

## `tests/integration/test-inflight-registry.py`

- exit: baseline 0 → head 0
- stdout raw `5e3306082763c2e0` → `12327690623b4491`; norm `5e3306082763c2e0` → `12327690623b4491`
- stderr raw `da6f5bfb48f793ec` → `da6f5bfb48f793ec`; norm `da6f5bfb48f793ec` → `da6f5bfb48f793ec` (identical)

Lines (stdout):
```
-PASS - 139/139 checks passed
+PASS - feat65: a failing ps probe still answers None
+PASS - feat65: an unrelated defect in the ps probe escapes
+PASS - feat65: an ambiguous worktree lookup falls back to the owner root
+PASS - feat65: an unrelated lookup defect escapes feature_root
+PASS - feat65: the direct feature-root command stays loud and nonzero on a defect
+PASS - 144/144 checks passed
```

## `tests/integration/test-inject-expertise.py`

- exit: baseline 0 → head 0
- stdout raw `c660ad5c31141602` → `49035c70c1384ff8`; norm `c660ad5c31141602` → `49035c70c1384ff8`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS feat65: an unexpected resolver defect is loud and nonzero, not absorbed
-20/20 cases passed.
+21/21 cases passed.
```

## `tests/integration/test-merge-gate.py`

- exit: baseline 0 → head 0
- stdout raw `cbe2c597be35c60d` → `be41d360798b2ffb`; norm `cbe2c597be35c60d` → `be41d360798b2ffb`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named
+ok    FEAT-65: KeyboardInterrupt escapes the guard
+ok    FEAT-65: a deliberate SystemExit keeps its own exit code
```

## `tests/integration/test-plan-sign-gate.py`

- exit: baseline 0 → head 0
- stdout raw `eaadcbc41fe5846a` → `fdf654d77d0babf5`; norm `eaadcbc41fe5846a` → `fdf654d77d0babf5`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
```

## Summary

| Suite | exit | stdout norm-identical | stderr norm-identical | `-` lines |
|---|---|---|---|---|
| `tests/integration/test-bash-write-guard.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-branch-create-gate.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-dispatch-guard.py` | 0→0 | no | yes | 1 |
| `tests/unit/test-feature-record.py` | 0→0 | yes | no | 2 |
| `tests/integration/test-gh-close-gate.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-inflight-registry.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-inject-expertise.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-merge-gate.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-plan-sign-gate.py` | 0→0 | no | yes | 0 |

