# FEAT-65 — red-first receipts (QA-65-01, validate c1)

Baseline production tree `4e8c73c0` (clean detached worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat65-base`); pin `a17269db` (`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks`).
Method: each suite's test file AS COMMITTED AT THE PIN is copied into the baseline tree and run there with the suite's
`*_BIN` override pointed at the baseline `bin/` — so the identical assertions are exercised against the pre-fix hooks
(RED) and against the pin (GREEN). Every red line is verbatim. A case that is red against the baseline and green at the
pin discriminates exactly the behaviour FEAT-65 changed; a case green in both is a documented-silence lock (kept outcome).

Command per run: `HARNESS_PROJECT_DIR=<tree> [<SUITE>_BIN=<tree>/…/bin/<hook>] python3 <tree>/tests/<suite>` cwd `<tree>`.

## `tests/integration/test-check-domain.py` — SC-02, SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 4; pin red lines: 0

```
FAIL  a defect reading the payload passes through with exactly the hook_guard line
      exit 0: 
FAIL  a defect in the feature-checkout rule is no longer absorbed: it is named on stderr
      exit 0: 
FAIL  a defect in the claim rule is no longer classified locally: it is named on stderr
      exit 0: check-domain: claim-worktree boundary was not enforced; passing through because the guard failed internally: FEAT-65 injected
FAIL  a --resolve defect passes through the same guard and answers no route
      exit 2: check-domain: BLOCKED — the manifest does not parse, so no domain can be resolved: FEAT-65 injected
```

## `tests/integration/test-check-domain-worktree.py` — SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL  [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
      | 0: ''
```

## `tests/integration/test-validate-digest.py` — SC-02, SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 4; pin red lines: 0

```
FAIL  [canonical-reader audit] duplicate hook payload did not take the typed fail-open path
FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
      | exit 0: 'check-digest: unreadable hook payload (FEAT-65 injected) — passing through.'
FAIL  [feat65] an unreadable payload is the hook's own failure and takes the same template
      | exit 0: 'check-digest: unreadable hook payload (SubagentStop hook payload: invalid JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)) — passing through.'
FAIL  [feat65] a defect in the registry errand is no longer reported in its own sentence
      | exit 2: "check-digest: could not release harness-qa's claim (RuntimeError('FEAT-65 injected')) — it will expire or reconcile on supervisor loss. Not blocking on our own errand.\nYour return does not satisfy the digest contract, so it cannot be accepted. Fix these and return again — every field is required; say nothing with an explicit `[]`, or `none` for a scalar that genuinely does not apply:\n  - no DIGEST"
```

## `tests/integration/test-bash-write-guard.py` — SC-02, SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 3; pin red lines: 0

```
FAIL  [feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands
      | 0: ''
FAIL  [feat65] a defect in the claim rule is no longer classified locally: it is named on stderr
      | 0: 'bash-write-guard: claim-worktree boundary was not enforced; passing through because the guard failed internally: FEAT-65 injected\n'
FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
      | 0: ''
```

## `tests/integration/test-dispatch-guard.py` — SC-02, SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL  feat65: a claim-step defect passes through hook_guard, named
      | exit 0, stderr=" not read tool grants for harness-pm ([Errno 2] No such file or directory: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpe2zduzm9/.omp/agents/harness-pm.md') -- passing through.\ndispatch-guard: claim step failed (RuntimeError: FEAT-65 injected) — passing through, the dispatch is NOT blocked.\n"
```

## `tests/integration/test-merge-gate.py` — SC-02, SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL  FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named
      rc=0 stdout='{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "merge-gate: could not evaluate FEAT-9001-fixture-non-era\'s Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge."}}\n' stderr=''
```

## `tests/integration/test-branch-create-gate.py` — SC-03, SC-05

- baseline exit 1; pin exit 0
- red lines against baseline: 2; pin red lines: 0

```
FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
      | rc=2 stderr='branch-create-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpnd6ls7e5/bin — refusing to run\n'
FAIL  FEAT-65 config reader carries no broad catch
      | import json, os, sys
```

## `tests/integration/test-gh-close-gate.py` — SC-03, SC-05

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
      rc=2 stderr='gh-close-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv_1h9zaf/bin — refusing to run\n'
```

## `tests/integration/test-plan-sign-gate.py` — SC-03, SC-05

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL  FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue
      rc=2 stderr='plan-sign-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpjio_cigz/bin — refusing to run\n'
```

## `tests/integration/test-inject-expertise.py` — SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL feat65: an unexpected resolver defect is loud and nonzero, not absorbed
        rc=0 stderr='inject-expertise.py: no harness root resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpe7c58wim/bin — no Expertise injected.\n'
```

## `tests/unit/test-feature-record.py` — SC-09

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL: test_an_unexpected_defect_stays_loud_and_nonzero (__main__.ProposeReworkTest.test_an_unexpected_defect_stays_loud_and_nonzero)
```

## `tests/integration/test-inflight-registry.py` — SC-03, SC-10

- baseline exit 1; pin exit 0
- red lines against baseline: 3; pin red lines: 0

```
FAIL - feat65: an unrelated defect in the ps probe escapes (returned)
FAIL - feat65: an unrelated lookup defect escapes feature_root (returned)
FAIL - 2/144 checks failed
```

## `tests/unit/test-broad-catch-census.py` — SC-04, SC-05

- baseline exit 1; pin exit 0
- red lines against baseline: 30; pin red lines: 0

```
FAIL FEAT-65: the ceiling table is exactly {harness_boundary.py: 2} {'bash-write-guard.py': 6, 'branch-create-gate.py': 4, 'check-domain.py': 24, 'check-state.py': 0, 'dispatch-guard.py': 9, 'feature-record.py': 1, 'gh-close-gate.py': 3, 'harness_boundary.py': 2, 'inflight_registry.py': 3, 'inject-expertise.py': 2, 'merge-gate.py': 5, 'plan-sign-gate.py': 2, 'validate-digest.py': 18}
FAIL FEAT-65: one broad catch in bash-write-guard.py is a finding against ceiling 0
FAIL FEAT-65: bash-write-guard.py carries zero broad catches 6
FAIL FEAT-65: one broad catch in branch-create-gate.py is a finding against ceiling 0
FAIL FEAT-65: branch-create-gate.py carries zero broad catches 4
FAIL FEAT-65: one broad catch in check-domain.py is a finding against ceiling 0
FAIL FEAT-65: check-domain.py carries zero broad catches 24
FAIL FEAT-65: one broad catch in dispatch-guard.py is a finding against ceiling 0
FAIL FEAT-65: dispatch-guard.py carries zero broad catches 9
FAIL FEAT-65: one broad catch in feature-record.py is a finding against ceiling 0
FAIL FEAT-65: feature-record.py carries zero broad catches 1
FAIL FEAT-65: one broad catch in gh-close-gate.py is a finding against ceiling 0
FAIL FEAT-65: gh-close-gate.py carries zero broad catches 3
FAIL FEAT-65: one broad catch in inflight_registry.py is a finding against ceiling 0
FAIL FEAT-65: inflight_registry.py carries zero broad catches 3
FAIL FEAT-65: one broad catch in inject-expertise.py is a finding against ceiling 0
FAIL FEAT-65: inject-expertise.py carries zero broad catches 2
FAIL FEAT-65: one broad catch in merge-gate.py is a finding against ceiling 0
FAIL FEAT-65: merge-gate.py carries zero broad catches 5
FAIL FEAT-65: one broad catch in plan-sign-gate.py is a finding against ceiling 0
FAIL FEAT-65: plan-sign-gate.py carries zero broad catches 2
FAIL FEAT-65: one broad catch in validate-digest.py is a finding against ceiling 0
FAIL FEAT-65: validate-digest.py carries zero broad catches 18
FAIL an embedded `-c` program's broad catch counts against its carrier 0
FAIL the live branch-create-gate.py config reader carries no broad catch
FAIL FEAT-65: the five DEC-234 prologues are byte-identical ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
FAIL FEAT-65: mutating branch-create-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
FAIL FEAT-65: mutating gh-close-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
FAIL FEAT-65: mutating merge-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
FAIL FEAT-65: mutating plan-sign-gate.py's prologue alone is reported ['branch-create-gate.py', 'gh-close-gate.py', 'merge-gate.py', 'plan-sign-gate.py']
```

## `tests/unit/test-harness-boundary.py` — SC-03

- baseline exit 1; pin exit 0
- red lines against baseline: 2; pin red lines: 0

```
FAIL hook_guard_is_called_by_exactly_the_five_guarded_hooks []
FAIL case_run_hook_body_contract_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_hook_body'")
```

## `tests/integration/test-check-plan-routes.py` — SC-04

- baseline exit 1; pin exit 0
- red lines against baseline: 1; pin red lines: 0

```
FAIL feat65_census_a_hook_plus_one_is_one_finding_against_ceiling_0 .claude/skills/harness/bin/check-domain.py carries 25 broad catch(es) (`except Exception` or bare `except:`) against ceiling 24 — narrow the new one to the boundary's real error class (FEAT-63 SC-04)
```

## Per-SC index

| SC | suite | baseline exit | pin exit | red lines vs baseline |
|---|---|---|---|---|
| SC-02 | `tests/integration/test-check-domain.py` | 1 | 0 | 4 |
| SC-02 | `tests/integration/test-validate-digest.py` | 1 | 0 | 4 |
| SC-02 | `tests/integration/test-bash-write-guard.py` | 1 | 0 | 3 |
| SC-02 | `tests/integration/test-dispatch-guard.py` | 1 | 0 | 1 |
| SC-02 | `tests/integration/test-merge-gate.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-check-domain.py` | 1 | 0 | 4 |
| SC-03 | `tests/integration/test-check-domain-worktree.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-validate-digest.py` | 1 | 0 | 4 |
| SC-03 | `tests/integration/test-bash-write-guard.py` | 1 | 0 | 3 |
| SC-03 | `tests/integration/test-dispatch-guard.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-merge-gate.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-branch-create-gate.py` | 1 | 0 | 2 |
| SC-03 | `tests/integration/test-gh-close-gate.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-plan-sign-gate.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-inject-expertise.py` | 1 | 0 | 1 |
| SC-03 | `tests/integration/test-inflight-registry.py` | 1 | 0 | 3 |
| SC-03 | `tests/unit/test-harness-boundary.py` | 1 | 0 | 2 |
| SC-04 | `tests/unit/test-broad-catch-census.py` | 1 | 0 | 30 |
| SC-04 | `tests/integration/test-check-plan-routes.py` | 1 | 0 | 1 |
| SC-05 | `tests/integration/test-branch-create-gate.py` | 1 | 0 | 2 |
| SC-05 | `tests/integration/test-gh-close-gate.py` | 1 | 0 | 1 |
| SC-05 | `tests/integration/test-plan-sign-gate.py` | 1 | 0 | 1 |
| SC-05 | `tests/unit/test-broad-catch-census.py` | 1 | 0 | 30 |
| SC-09 | `tests/unit/test-feature-record.py` | 1 | 0 | 1 |
| SC-10 | `tests/integration/test-inflight-registry.py` | 1 | 0 | 3 |

SC-01 (byte identity) is `notes/byte-evidence-vs-baseline.md`: its red is the per-suite normalised diff, every `-` line
listed verbatim. SC-06/SC-07/SC-08 are inspection criteria and carry no red.
