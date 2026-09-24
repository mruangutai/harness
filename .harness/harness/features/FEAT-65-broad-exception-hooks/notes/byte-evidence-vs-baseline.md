# FEAT-65 — exact byte evidence per suite (SC-01, validate c2 — regenerated with the pin's tests)

Baseline `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` vs head `62a0299bf3b03e297abafaa7adf6738b7c7fc3de` (review pin 7596434c's tree plus the c1 ledger commit; production and test files identical to 7596434c).
Each suite's test file AS COMMITTED AT THE PIN is run once per tree (copied into the baseline tree for its run, then restored): `HARNESS_PROJECT_DIR=<tree> python3 <tree>/<suite>`, cwd `<tree>`. So the `-` lines are the pin's assertions failing against the baseline production hooks, verbatim.
`raw` digests are sha256[:16] of the untouched stream. `norm` digests are the same stream after exactly two
substitutions: the tree's own absolute path → `<ROOT>`, and any `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>`.
Under `Lines` every differing line of the NORMALISED streams is printed verbatim (unified diff, zero context);
a suite with `norm` digests equal and no lines listed is byte-identical up to those two substitutions.

## `tests/integration/test-check-domain.py`

- exit: baseline 1 → head 0
- stdout raw `1de13ec0ae233ac0` → `75be33c60abd75af`; norm `1de13ec0ae233ac0` → `75be33c60abd75af`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  a defect reading the payload passes through with exactly the hook_guard line
-      exit 0: 
-FAIL  a defect in the feature-checkout rule is no longer absorbed: it is named on stderr
-      exit 0: 
-FAIL  a defect in the claim rule is no longer classified locally: it is named on stderr
-      exit 0: check-domain: claim-worktree boundary was not enforced; passing through because the guard failed internally: FEAT-65 injected
-FAIL  a --resolve defect passes through the same guard and answers no route
-      exit 2: check-domain: BLOCKED — the manifest does not parse, so no domain can be resolved: FEAT-65 injected
+ok    a defect reading the payload passes through with exactly the hook_guard line
+ok    a defect in the feature-checkout rule is no longer absorbed: it is named on stderr
+ok    a defect in the claim rule is no longer classified locally: it is named on stderr
+ok    a --resolve defect passes through the same guard and answers no route
-19/23 T-06 check-domain cases passed.
+23/23 T-06 check-domain cases passed.
-4 FAILING
+ALL PASSED
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

- exit: baseline 1 → head 0
- stdout raw `31ce5051172a4f9a` → `51d19db1e52bb91a`; norm `31ce5051172a4f9a` → `51d19db1e52bb91a`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
-      | 0: ''
+ok    [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
-5/6 FEAT-61 T-03 adapter cases passed.
+6/6 FEAT-61 T-03 adapter cases passed.
```

## `tests/integration/test-check-domain-approval.py`

- exit: baseline 0 → head 0
- stdout raw `c7794321f8e0d333` → `c7794321f8e0d333`; norm `c7794321f8e0d333` → `c7794321f8e0d333` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-validate-digest.py`

- exit: baseline 1 → head 0
- stdout raw `608a461e7dbf20b1` → `31fa4cf294cdf93a`; norm `b908d7f1d43b8ce2` → `70d0444c0c75ea5d`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  [canonical-reader audit] duplicate hook payload did not take the typed fail-open path
-FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
-      | exit 0: 'check-digest: unreadable hook payload (FEAT-65 injected) — passing through.'
-FAIL  [feat65] an unreadable payload is the hook's own failure and takes the same template
-      | exit 0: 'check-digest: unreadable hook payload (SubagentStop hook payload: invalid JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)) — passing through.'
-FAIL  [feat65] a defect in the registry errand is no longer reported in its own sentence
-      | exit 2: "check-digest: could not release harness-qa's claim (RuntimeError('FEAT-65 injected')) — it will expire or reconcile on supervisor loss. Not blocking on our own errand.\nYour return does not satisfy the digest contract, so it cannot be accepted. Fix these and return again — every field is required; say nothing with an explicit `[]`, or `none` for a scalar that genuinely does not apply:\n  - no DIGEST"
+ok    [feat65] a defect reading the payload passes through with exactly the hook_guard line
+ok    [feat65] an unreadable payload is the hook's own failure and takes the same template
+ok    [feat65] a defect in the registry errand is no longer reported in its own sentence
-3/6 FEAT-65 guard cases passed.
+6/6 FEAT-65 guard cases passed.
-4 FAILING.
+ALL PASSED.
```

## `tests/unit/test-code-grade.py`

- exit: baseline 0 → head 0
- stdout raw `a6133575d90833b8` → `a6133575d90833b8`; norm `a6133575d90833b8` → `a6133575d90833b8` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-bash-write-guard.py`

- exit: baseline 1 → head 0
- stdout raw `d5af2a3e49ab3bdd` → `c5f5de6f51976c86`; norm `d5af2a3e49ab3bdd` → `c5f5de6f51976c86`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
-      | 0: ''
-
-5/6 FEAT-61 T-03 adapter cases passed.
-FAIL  [feat65] a defect in the claim rule is no longer classified locally: it is named on stderr
-      | 0: 'bash-write-guard: claim-worktree boundary was not enforced; passing through because the guard failed internally: FEAT-65 injected\n'
-FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
-      | 0: ''
+ok    [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
+
+6/6 FEAT-61 T-03 adapter cases passed.
+ok    [feat65] a defect in the claim rule is no longer classified locally: it is named on stderr
+ok    [feat65] a defect reading the payload passes through with exactly the hook_guard line
-2/4 FEAT-65 guard cases passed.
+4/4 FEAT-65 guard cases passed.
```

## `tests/integration/test-branch-create-gate.py`

- exit: baseline 1 → head 0
- stdout raw `3c083436dbdb606a` → `41e65ecc68e1be42`; norm `5bb3c53c58100c37` → `41e65ecc68e1be42`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-      | rc=2 stderr='branch-create-gate.py: no harness root could be resolved from <TMP>/bin — refusing to run\n'
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-FAIL  FEAT-65 config reader carries no broad catch
-      | import json, os, sys
-try:
-    g = json.load(open(os.path.join(sys.argv[1], ".harness", "harness.json"))).get("github") or {}
-except Exception:
-    g = {}
-print(str(bool(g.get("sync"))).lower(),
-      g.get("repo") or "-")
+ok    FEAT-65 config reader carries no broad catch
-
-12/14 cases passed.
+14/14 cases passed.
```

## `tests/integration/test-dispatch-guard.py`

- exit: baseline 1 → head 0
- stdout raw `b1a503786e841e0f` → `f89829d7caaf3795`; norm `f5aeee5443317aa0` → `f89829d7caaf3795`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  feat65: a claim-step defect passes through hook_guard, named
-      | exit 0, stderr=" not read tool grants for harness-pm ([Errno 2] No such file or directory: '<TMP>/.omp/agents/harness-pm.md') -- passing through.\ndispatch-guard: claim step failed (RuntimeError: FEAT-65 injected) — passing through, the dispatch is NOT blocked.\n"
+PASS  feat65: a claim-step defect passes through hook_guard, named
-84 of 85 cases passed
+85 of 85 cases passed
```

## `tests/unit/test-feature-record.py`

- exit: baseline 1 → head 0
- stdout raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)
- stderr raw `9e4d2aa75ee555ae` → `1976a1519114c4e0`; norm `00b5ca73d4c72a29` → `1976a1519114c4e0`

Lines (stderr):
```
-.................F........................................................
-======================================================================
-FAIL: test_an_unexpected_defect_stays_loud_and_nonzero (__main__.ProposeReworkTest.test_an_unexpected_defect_stays_loud_and_nonzero)
-FEAT-65 SC-09: feature-record.py is an authoritative direct command and gets no
+..........................................................................
-Traceback (most recent call last):
-  File "<ROOT>/tests/unit/test-feature-record.py", line 951, in test_an_unexpected_defect_stays_loud_and_nonzero
-    self.assertNotIn(result.returncode, (0, 2), result.stderr)
-    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-AssertionError: 2 unexpectedly found in (0, 2) : REFUSED: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feature-record-test-72_oj4hy/.harness/features/FEAT-77-record/plan.yaml does not load: FEAT-65 injected
+Ran 74 tests in 10.257s
-
-Ran 74 tests in 9.550s
-
-FAILED (failures=1)
+OK
```

## `tests/integration/test-gh-close-gate.py`

- exit: baseline 1 → head 0
- stdout raw `3de92f2e38fa8a44` → `c938ecba1dce3d30`; norm `5763fedde4596b6e` → `c938ecba1dce3d30`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-      rc=2 stderr='gh-close-gate.py: no harness root could be resolved from <TMP>/bin — refusing to run\n'
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-1 FAILED
+ALL PASSED
```

## `tests/integration/test-inflight-registry.py`

- exit: baseline 1 → head 0
- stdout raw `b64e46bfe5409ed8` → `12327690623b4491`; norm `b64e46bfe5409ed8` → `12327690623b4491`
- stderr raw `da6f5bfb48f793ec` → `da6f5bfb48f793ec`; norm `da6f5bfb48f793ec` → `da6f5bfb48f793ec` (identical)

Lines (stdout):
```
-FAIL - feat65: an unrelated defect in the ps probe escapes (returned)
+PASS - feat65: an unrelated defect in the ps probe escapes
-FAIL - feat65: an unrelated lookup defect escapes feature_root (returned)
+PASS - feat65: an unrelated lookup defect escapes feature_root
-FAIL - 2/144 checks failed
+PASS - 144/144 checks passed
```

## `tests/integration/test-inject-expertise.py`

- exit: baseline 1 → head 0
- stdout raw `0cc143a3b7c5f67c` → `49035c70c1384ff8`; norm `c3af0771fd500b05` → `49035c70c1384ff8`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL feat65: an unexpected resolver defect is loud and nonzero, not absorbed
-        rc=0 stderr='inject-expertise.py: no harness root resolved from <TMP>/bin — no Expertise injected.\n'
+PASS feat65: an unexpected resolver defect is loud and nonzero, not absorbed
-20/21 cases passed.
+21/21 cases passed.
```

## `tests/integration/test-merge-gate.py`

- exit: baseline 1 → head 0
- stdout raw `2872cacee0486552` → `be41d360798b2ffb`; norm `2872cacee0486552` → `be41d360798b2ffb`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named
-      rc=0 stdout='{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "merge-gate: could not evaluate FEAT-9001-fixture-non-era\'s Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge."}}\n' stderr=''
+ok    FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named
-1 FAILED
+ALL PASSED
```

## `tests/integration/test-plan-sign-gate.py`

- exit: baseline 1 → head 0
- stdout raw `0ea981dbb74d3ba9` → `fdf654d77d0babf5`; norm `b8533c30ca1c393a` → `fdf654d77d0babf5`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-      rc=2 stderr='plan-sign-gate.py: no harness root could be resolved from <TMP>/bin — refusing to run\n'
+ok    FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
-1 failing.
+all checks passed.
```

## `tests/unit/test-broad-catch-census.py`

- exit: baseline 1 → head 0
- stdout raw `dafab4d00b2b9163` → `3054a612fd3e3fc9`; norm `dafab4d00b2b9163` → `3054a612fd3e3fc9`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL FEAT-65: the ceiling table is exactly {harness_boundary.py: 2} {'bash-write-guard.py': 6, 'branch-create-gate.py': 4, 'check-domain.py': 24, 'check-state.py': 0, 'dispatch-guard.py': 9, 'feature-record.py': 1, 'gh-close-gate.py': 3, 'harness_boundary.py': 2, 'inflight_registry.py': 3, 'inject-expertise.py': 2, 'merge-gate.py': 5, 'plan-sign-gate.py': 2, 'validate-digest.py': 18}
-FAIL FEAT-65: one broad catch in bash-write-guard.py is a finding against ceiling 0
-FAIL FEAT-65: bash-write-guard.py carries zero broad catches 6
-FAIL FEAT-65: one broad catch in branch-create-gate.py is a finding against ceiling 0
-FAIL FEAT-65: branch-create-gate.py carries zero broad catches 4
-FAIL FEAT-65: one broad catch in check-domain.py is a finding against ceiling 0
-FAIL FEAT-65: check-domain.py carries zero broad catches 24
-FAIL FEAT-65: one broad catch in dispatch-guard.py is a finding against ceiling 0
-FAIL FEAT-65: dispatch-guard.py carries zero broad catches 9
-FAIL FEAT-65: one broad catch in feature-record.py is a finding against ceiling 0
-FAIL FEAT-65: feature-record.py carries zero broad catches 1
-FAIL FEAT-65: one broad catch in gh-close-gate.py is a finding against ceiling 0
-FAIL FEAT-65: gh-close-gate.py carries zero broad catches 3
-FAIL FEAT-65: one broad catch in inflight_registry.py is a finding against ceiling 0
-FAIL FEAT-65: inflight_registry.py carries zero broad catches 3
-FAIL FEAT-65: one broad catch in inject-expertise.py is a finding against ceiling 0
-FAIL FEAT-65: inject-expertise.py carries zero broad catches 2
-FAIL FEAT-65: one broad catch in merge-gate.py is a finding against ceiling 0
-FAIL FEAT-65: merge-gate.py carries zero broad catches 5
-FAIL FEAT-65: one broad catch in plan-sign-gate.py is a finding against ceiling 0
-FAIL FEAT-65: plan-sign-gate.py carries zero broad catches 2
-FAIL FEAT-65: one broad catch in validate-digest.py is a finding against ceiling 0
-FAIL FEAT-65: validate-digest.py carries zero broad catches 18
+PASS FEAT-65: the ceiling table is exactly {harness_boundary.py: 2}
+PASS FEAT-65: one broad catch in bash-write-guard.py is a finding against ceiling 0
+PASS FEAT-65: bash-write-guard.py carries zero broad catches
+PASS FEAT-65: one broad catch in branch-create-gate.py is a finding against ceiling 0
+PASS FEAT-65: branch-create-gate.py carries zero broad catches
+PASS FEAT-65: one broad catch in check-domain.py is a finding against ceiling 0
+PASS FEAT-65: check-domain.py carries zero broad catches
+PASS FEAT-65: one broad catch in dispatch-guard.py is a finding against ceiling 0
+PASS FEAT-65: dispatch-guard.py carries zero broad catches
+PASS FEAT-65: one broad catch in feature-record.py is a finding against ceiling 0
+PASS FEAT-65: feature-record.py carries zero broad catches
+PASS FEAT-65: one broad catch in gh-close-gate.py is a finding against ceiling 0
+PASS FEAT-65: gh-close-gate.py carries zero broad catches
+PASS FEAT-65: one broad catch in inflight_registry.py is a finding against ceiling 0
+PASS FEAT-65: inflight_registry.py carries zero broad catches
+PASS FEAT-65: one broad catch in inject-expertise.py is a finding against ceiling 0
+PASS FEAT-65: inject-expertise.py carries zero broad catches
+PASS FEAT-65: one broad catch in merge-gate.py is a finding against ceiling 0
+PASS FEAT-65: merge-gate.py carries zero broad catches
+PASS FEAT-65: one broad catch in plan-sign-gate.py is a finding against ceiling 0
+PASS FEAT-65: plan-sign-gate.py carries zero broad catches
+PASS FEAT-65: one broad catch in validate-digest.py is a finding against ceiling 0
+PASS FEAT-65: validate-digest.py carries zero broad catches
-FAIL an embedded `-c` program's broad catch counts against its carrier 0
+PASS an embedded `-c` program's broad catch counts against its carrier
-FAIL the live branch-create-gate.py config reader carries no broad catch
-FAIL FEAT-65: the five DEC-234 prologues are byte-identical ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
+PASS the live branch-create-gate.py config reader carries no broad catch
+PASS FEAT-65: the five DEC-234 prologues are byte-identical
-FAIL FEAT-65: mutating branch-create-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
-FAIL FEAT-65: mutating gh-close-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
-FAIL FEAT-65: mutating merge-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
-FAIL FEAT-65: mutating plan-sign-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
+PASS FEAT-65: mutating branch-create-gate.py's prologue alone is reported
+PASS FEAT-65: mutating gh-close-gate.py's prologue alone is reported
+PASS FEAT-65: mutating merge-gate.py's prologue alone is reported
+PASS FEAT-65: mutating plan-sign-gate.py's prologue alone is reported
-30 FAILURE(S): ['FEAT-65: the ceiling table is exactly {harness_boundary.py: 2}', 'FEAT-65: one broad catch in bash-write-guard.py is a finding against ceiling 0', 'FEAT-65: bash-write-guard.py carries zero broad catches', 'FEAT-65: one broad catch in branch-create-gate.py is a finding against ceiling 0', 'FEAT-65: branch-create-gate.py carries zero broad catches', 'FEAT-65: one broad catch in check-domain.py is a finding against ceiling 0', 'FEAT-65: check-domain.py carries zero broad catches', 'FEAT-65: one broad catch in dispatch-guard.py is a finding against ceiling 0', 'FEAT-65: dispatch-guard.py carries zero broad catches', 'FEAT-65: one broad catch in feature-record.py is a finding against ceiling 0', 'FEAT-65: feature-record.py carries zero broad catches', 'FEAT-65: one broad catch in gh-close-gate.py is a finding against ceiling 0', 'FEAT-65: gh-close-gate.py carries zero broad catches', 'FEAT-65: one broad catch in inflight_registry.py is a finding against ceiling 0', 'FEAT-65: inflight_registry.py carries zero broad catches', 'FEAT-65: one broad catch in inject-expertise.py is a finding against ceiling 0', 'FEAT-65: inject-expertise.py carries zero broad catches', 'FEAT-65: one broad catch in merge-gate.py is a finding against ceiling 0', 'FEAT-65: merge-gate.py carries zero broad catches', 'FEAT-65: one broad catch in plan-sign-gate.py is a finding against ceiling 0', 'FEAT-65: plan-sign-gate.py carries zero broad catches', 'FEAT-65: one broad catch in validate-digest.py is a finding against ceiling 0', 'FEAT-65: validate-digest.py carries zero broad catches', "an embedded `-c` program's broad catch counts against its carrier", 'the live branch-create-gate.py config reader carries no broad catch', 'FEAT-65: the five DEC-234 prologues are byte-identical', "FEAT-65: mutating branch-create-gate.py's prologue alone is reported", "FEAT-65: mutating gh-close-gate.py's prologue alone is reported", "FEAT-65: mutating merge-gate.py's prologue alone is reported", "FEAT-65: mutating plan-sign-gate.py's prologue alone is reported"]
+ALL PASS
```

## `tests/unit/test-harness-boundary.py`

- exit: baseline 1 → head 0
- stdout raw `4effe4eddaf03704` → `14d569909492d386`; norm `4effe4eddaf03704` → `14d569909492d386`
- stderr raw `51f5ae2115a88212` → `4246c8d65ab2e1f4`; norm `179f949873782ae8` → `179f949873782ae8` (identical)

Lines (stdout):
```
-FAIL hook_guard_is_called_by_exactly_the_five_guarded_hooks []
-FAIL case_run_hook_body_contract_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_hook_body'")
+PASS hook_guard_is_called_by_exactly_the_five_guarded_hooks
+PASS run_hook_body_returns_0_when_the_body_falls_off
+PASS run_hook_body_open_passes_through_a_body_defect
+PASS run_hook_body_closed_blocks_a_body_defect
+PASS run_hook_body_lets_the_bodys_SystemExit_escape
-2 FAILURE(S): ['hook_guard_is_called_by_exactly_the_five_guarded_hooks', 'case_run_hook_body_contract_did_not_crash']
+ALL PASS
```

## `tests/integration/test-check-plan-routes.py`

- exit: baseline 1 → head 0
- stdout raw `ebb4e0f40e0b6103` → `d5ca1a56461d1a4c`; norm `ebb4e0f40e0b6103` → `d5ca1a56461d1a4c`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-FAIL feat65_census_a_hook_plus_one_is_one_finding_against_ceiling_0 .claude/skills/harness/bin/check-domain.py carries 25 broad catch(es) (`except Exception` or bare `except:`) against ceiling 24 — narrow the new one to the boundary's real error class (FEAT-63 SC-04)
+PASS feat65_census_a_hook_plus_one_is_one_finding_against_ceiling_0
-1 FAILURE(S): ['feat65_census_a_hook_plus_one_is_one_finding_against_ceiling_0']
+ALL PASS
```

## Summary

| Suite | exit | stdout norm-identical | stderr norm-identical | `-` lines |
|---|---|---|---|---|
| `tests/integration/test-check-domain.py` | 1→0 | no | yes | 10 |
| `tests/integration/test-check-domain-artifact.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-claims.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-grant.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-post.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-worktree-parity.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-check-domain-worktree.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-check-domain-approval.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-validate-digest.py` | 1→0 | no | yes | 9 |
| `tests/unit/test-code-grade.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-bash-write-guard.py` | 1→0 | no | yes | 9 |
| `tests/integration/test-branch-create-gate.py` | 1→0 | no | yes | 12 |
| `tests/integration/test-dispatch-guard.py` | 1→0 | no | yes | 3 |
| `tests/unit/test-feature-record.py` | 1→0 | yes | no | 13 |
| `tests/integration/test-gh-close-gate.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-inflight-registry.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-inject-expertise.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-merge-gate.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-plan-sign-gate.py` | 1→0 | no | yes | 3 |
| `tests/unit/test-broad-catch-census.py` | 1→0 | no | yes | 31 |
| `tests/unit/test-harness-boundary.py` | 1→0 | no | yes | 3 |
| `tests/integration/test-check-plan-routes.py` | 1→0 | no | yes | 2 |
