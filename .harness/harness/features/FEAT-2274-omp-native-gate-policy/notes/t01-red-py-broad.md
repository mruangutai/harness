# T-01 slice py-broad (C1 + C5) — fail-first evidence

Production source at RED: identical to baseline 1e0b014917125bc9aae1f30a2f6fd53ed239f3bc (no edit to harness_boundary.py, check-domain.py, bash-write-guard.py, dispatch-guard.py, validate-digest.py when these ran; only the five test files carried the new assertions). Run from the worktree root.

## RED (2026-11-22, before implementation)

### `python3 tests/unit/test-harness-boundary.py` — exit 1

```
FAIL feat2274_emit_unavailable_exists 
FAIL feat2274_hook_guard_open_emits_unavailable_once_and_returns_0 rc=None got=[] err=TypeError("hook_guard() got an unexpected keyword argument 'script'")
FAIL feat2274_hook_guard_open_keeps_its_stderr_diagnostic TypeError("hook_guard() got an unexpected keyword argument 'script'")
FAIL feat2274_hook_guard_closed_unchanged_exit_2_no_unavailable rc=None err=TypeError("hook_guard() got an unexpected keyword argument 'script'")
FAIL feat2274_hook_guard_normal_return_emits_nothing TypeError("hook_guard() got an unexpected keyword argument 'script'")
FAIL feat2274_hook_guard_lets_SystemExit_escape_without_unavailable ''
FAIL feat2274_run_hook_body_passes_its_path_as_the_gate ''
7 FAILURE(S): ['feat2274_emit_unavailable_exists', 'feat2274_hook_guard_open_emits_unavailable_once_and_returns_0', 'feat2274_hook_guard_open_keeps_its_stderr_diagnostic', 'feat2274_hook_guard_closed_unchanged_exit_2_no_unavailable', 'feat2274_hook_guard_normal_return_emits_nothing', 'feat2274_hook_guard_lets_SystemExit_escape_without_unavailable', 'feat2274_run_hook_body_passes_its_path_as_the_ga
```

### `python3 tests/integration/test-check-domain.py` — exit 1

```
FAIL  a defect reading the payload passes through with exactly the hook_guard line
FAIL  a defect in a governed rule is visibly unavailable, once
FAIL  an unreadable payload passes through as one unavailable line
FAIL  a tree without harness_boundary.py says unavailable once and still fails open
25/29 T-06 check-domain cases passed.
4 FAILING
```

### `python3 tests/integration/test-bash-write-guard.py` — exit 1

```
48/48 cases passed.
7/7 T-14 cases passed.
29/29 worktree-boundary cases passed.
3/3 deep-layout Bash-route cases passed.
20/20 HEAD-move and forced-removal cases passed.
6/6 FEAT-50 Bash binding cases passed.
6/6 FEAT-61 T-03 adapter cases passed.
FAIL  [feat65] a defect in the claim rule is no longer classified locally: it is named on stderr
FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
2/4 FEAT-65 guard cases passed.
FAIL  [f2274] an unreadable payload passes through as exactly one unavailable line
FAIL  [f2274] a tree without harness_boundary.py passes through as exactly one unavailable line
6/8 FEAT-2274 unavailable cases passed.
2/2 bug895 Bash-route cases passed.
8/8 bug1106 Bash-route cases passed.
89/89 FEAT-2225 expertise CLI cases passed.
```

### `python3 tests/integration/test-dispatch-guard.py` — exit 1

```
FAIL  case 27a: orchestrator -> member is not refused by dispatch-guard
FAIL  case 27c: lead -> peer lead is not refused by dispatch-guard
FAIL  case 27e: a member with spawns: [] is not refused by dispatch-guard
FAIL  f2274: an own crash passes through as exactly one unavailable line
FAIL  f2274: an unreadable payload passes through as exactly one unavailable line
FAIL  f2274: the claim step's own registry failure passes through as exactly one unavailable line
FAIL  f2274: the registry library missing passes through as exactly one unavailable line
FAIL  f2274: harness_boundary itself missing passes through as exactly one unavailable line
160 of 168 cases passed
```

### `python3 tests/integration/test-validate-digest.py --only run_feat65_guard_cases` — exit 1

```
FAIL  [feat65] a defect reading the payload passes through with exactly the hook_guard line
FAIL  [feat65] an unreadable payload is the hook's own failure and takes the same template
FAIL  [feat65] a defect in the registry errand is no longer reported in its own sentence
3/6 FEAT-65 guard cases passed.
3 FAILING.
```

### `python3 tests/integration/test-validate-digest.py --only run_feat2274_unavailable_cases` — exit 1

```
FAIL  [feat65] [f2274] a persona with no schema passes through visibly unavailable
FAIL  [feat65] [f2274] a payload with no agent identity passes through visibly unavailable
FAIL  [feat65] [f2274] stop_hook_active does not change the missing-identity outcome
FAIL  [feat65] [f2274] a missing claim registry on a passing return is visibly unavailable, once
5/9 FEAT-65 guard cases passed.
4 FAILING.
```

### Revised case 27c, re-run against the baseline bin (`git archive 1e0b014 .claude/skills/harness/bin`)

Case 27c first fired an otherwise-incomplete payload (no tree root for the shell-less validator lead, then a plan mission with no pending plan); it now declares both, so its only baseline refusal is the allowlist. Command: `DISPATCH_GUARD_BIN=<baseline bin>/dispatch-guard.py python3 tests/integration/test-dispatch-guard.py` — exit 1 (`fire` uses the baseline guard; the copied-bin f2274 cases copy the current tree, so only the unreadable-payload one reaches the baseline guard here).

```
FAIL  case 27a: orchestrator -> member is not refused by dispatch-guard
      | exit 2, stderr='dispatch-guard: BLOCKED -- harness-orchestrator may not dispatch harness-backend-dev; its spawns: list is harness-product-lead, harness-eng-lead, harness-validator-lead.\n  A persona dispatches only what its frontmatter names. A task owned by\n  another squad is an ESCALATE t
--
FAIL  case 27c: lead -> peer lead is not refused by dispatch-guard
      | exit 2, stderr='dispatch-guard: BLOCKED -- harness-eng-lead may not dispatch harness-validator-lead; its spawns: list is harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-dev-ops.\n  A persona dispatches only what its frontmatter names. A task owned by
--
FAIL  case 27e: a member with spawns: [] is not refused by dispatch-guard
      | exit 2, stderr='dispatch-guard: BLOCKED -- harness-backend-dev may not dispatch harness-product-lead; its spawns: list is empty.\n  A persona dispatches only what its frontmatter names. A task owned by\n  another squad is an ESCALATE to the orchestrator, which routes it to the\n  owning lead
--
FAIL  f2274: an unreadable payload passes through as exactly one unavailable line
      | exit 0, stdout='', stderr='dispatch-guard: unreadable hook payload (Expecting value: line 1 column 1 (char 0)) — passing through.\n'
164 of 168 cases passed
```

## GREEN (after implementation)

```
python3 tests/unit/test-harness-boundary.py                -> exit 0, ALL PASS (141 checks)
python3 tests/integration/test-check-domain.py             -> exit 0, 29/29 T-06 check-domain cases passed.
python3 tests/integration/test-bash-write-guard.py         -> exit 0, every group passed (230/230 summed across group summaries; 0 FAIL lines)
python3 tests/integration/test-dispatch-guard.py           -> exit 0, 168 of 168 cases passed
python3 tests/integration/test-validate-digest.py          -> exit 0, ALL PASSED (407/407 summed across group summaries)
```
