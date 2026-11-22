# T-01 RED/GREEN evidence — Python narrow gates (C2)

Slice: gh-close-gate.py, branch-create-gate.py, plan-sign-gate.py and their integration suites.

## RED — converted and new assertions against the pre-edit gates

The three gate sources were confirmed identical to the baseline pin before this run
(`git diff --stat 1e0b014917125bc9aae1f30a2f6fd53ed239f3bc -- <the three gates>` printed nothing).
Only the test files had been edited: the APPLICABILITY_CORPUS literal, the corpus-agreement
rows, the converted FEAT-65 resolver-defect assertions, the no-root and body-failure pairs,
and (branch-create) the #2107 case. Every corpus-agreement row passed at baseline, so the corpus
labels match the working gate; every FAIL below is a contract assertion the baseline violates.
The copied bins pick up the shared `harness_boundary.py` as it stood during the concurrent
T-01 slices, so traceback line numbers in the copies vary.

### gh-close

`python3 tests/integration/test-gh-close-gate.py` (from W) — exit 1; 92 ok, 49 FAIL.

FAIL counts by group: FEAT-65=1, body failure=2, no harness root=2, resolver defect=44

Representative failures (detail truncated to 400 chars):

```
FAIL  FEAT-65: an unexpected resolver defect REFUSES a matching close at exit 2, named
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmps893neg0/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git status'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmps893neg0/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'gh pr close 5'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmps893neg0/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git branch -d x'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmps893neg0/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  no harness root: a matching close is refused at exit 2, named
      rc=2 stderr='gh-close-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfpyw8a3u/bin — refusing to run\n'
FAIL  no harness root: an unrelated command exits 0 untouched
      rc=2 stdout='' stderr='gh-close-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfpyw8a3u/bin — refusing to run\n'
FAIL  body failure: a matching close is refused at exit 2, named
      rc=1 stderr='ath).get("github") or {}\n        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpf0ft1vlv/bin/artifact_accessors.py", line 490, in load_harness_json\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
FAIL  body failure: an unrelated command exits 0 untouched
      rc=1 stdout='' stderr='ath).get("github") or {}\n        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpf0ft1vlv/bin/artifact_accessors.py", line 490, in load_harness_json\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
```

Tail:

```
      rc=1 stdout='' stderr='ath).get("github") or {}\n        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpf0ft1vlv/bin/artifact_accessors.py", line 490, in load_harness_json\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'

49 FAILED
```

### branch-create

`python3 tests/integration/test-branch-create-gate.py` (from W) — exit 1; 44 ok, 36 FAIL.

FAIL counts by group: #2107=1, FEAT-65=1, body failure=2, no harness root=2, resolver defect=30

Representative failures (detail truncated to 400 chars):

```
FAIL  FEAT-65: an unexpected resolver defect REFUSES a matching branch creation at exit 2, named
      | rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfj92m1bi/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git status'
      | rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfj92m1bi/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git branch -d x'
      | rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfj92m1bi/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'gh pr close 5'
      | rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpfj92m1bi/bin/harness_boundary.py", line 1414, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  no harness root: a matching branch creation is refused at exit 2, named
      | rc=2 stderr='branch-create-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpx9fnwjr6/bin — refusing to run\n'
FAIL  no harness root: an unrelated command exits 0 untouched
      | rc=2 stdout='' stderr='branch-create-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpx9fnwjr6/bin — refusing to run\n'
FAIL  body failure: a matching branch creation is refused at exit 2, named
      | rc=1 stderr='g_path).get("github") or {})\n    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpneuv1tp0/bin/artifact_accessors.py", line 490, in load_harness_json\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
FAIL  body failure: an unrelated command exits 0 untouched
      | rc=1 stdout='' stderr='g_path).get("github") or {})\n    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpneuv1tp0/bin/artifact_accessors.py", line 490, in load_harness_json\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
FAIL  #2107: a flow branch over a landed feature.json with github.parent "²" is DENIED by name, never exit 1
      | rc=0 stdout='{"systemMessage": "[work-tracking] Branch maps to flow FEAT-90-fixture-flow."}\n' stderr=''
```

Tail:

```
ok    FEAT-65 config reader carries no broad catch

44/80 cases passed.
```

### plan-sign

`python3 tests/integration/test-plan-sign-gate.py` (from W) — exit 1; 125 ok, 67 FAIL.

FAIL counts by group: FEAT-65=4, body failure=2, no harness root=2, resolver defect=59

Representative failures (detail truncated to 400 chars):

```
FAIL  FEAT-65: under a resolver defect the unrelated `git status` passes untouched
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  FEAT-65: an unexpected resolver defect REFUSES an agent's sign-approval at exit 2, named
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  FEAT-65: an unexpected resolver defect REFUSES an agent's raise-cycles at exit 2, named
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  FEAT-65: an unexpected resolver defect REFUSES an agent's set-rework at exit 2, named
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git status'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'gh pr close 5'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  resolver defect: an unrelated command passes untouched: 'git branch -d x'
      rc=1 stdout='' stderr=' harness_boundary.resolve_root(_bootstrap_bin)\n           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpklau_m52/bin/harness_boundary.py", line 1431, in resolve_root\n    raise RuntimeError(\'FEAT-65 injected\')\nRuntimeError: FEAT-65 injected\n'
FAIL  no harness root: an agent's sign-approval is refused at exit 2, named
      rc=2 stderr='plan-sign-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpmye0srt5/bin — refusing to run\n'
FAIL  no harness root: an unrelated command exits 0 untouched
      rc=2 stdout='' stderr='plan-sign-gate.py: no harness root could be resolved from /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpmye0srt5/bin — refusing to run\n'
FAIL  body failure: an agent's raise-cycles is refused at exit 2, named
      rc=1 stderr='cessors.read_hook_payload(\n        sys.stdin.read(), "plan-sign-gate hook payload")\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv4tqsjzt/bin/artifact_accessors.py", line 490, in read_hook_payload\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
FAIL  body failure: an unrelated command exits 0 untouched
      rc=1 stdout='' stderr='cessors.read_hook_payload(\n        sys.stdin.read(), "plan-sign-gate hook payload")\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv4tqsjzt/bin/artifact_accessors.py", line 490, in read_hook_payload\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'
```

Tail:

```
      rc=1 stdout='' stderr='cessors.read_hook_payload(\n        sys.stdin.read(), "plan-sign-gate hook payload")\n  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv4tqsjzt/bin/artifact_accessors.py", line 490, in read_hook_payload\n    raise RuntimeError(\'FEAT-2274 body injected\')\nRuntimeError: FEAT-2274 body injected\n'

67 failing.
```

## GREEN — after the gate changes

Implementation: each gate reads the payload command with the standard library
(`_payload_command`), runs its own matcher (`denies` / `_branch_name`; plan-sign also exempts
an absent or empty agent_type) before `_resolve_root()` and any library load, and exits 0 when
the command does not apply. When it does apply, the gate installs `sys.excepthook =
_refuse_on_crash` (traceback, then the named refusal, then exit 2) and turns "no root" into the
same refusal. The DEC-234 `_resolve_root` text is unchanged. branch-create also refuses by name
when every corpus entry matching the flow carries a feature.json read error (#2107).

All three commands run from W, each exiting 0:

```
python3 tests/integration/test-gh-close-gate.py      -> 141 ok, 0 FAIL, "ALL PASSED"
python3 tests/integration/test-branch-create-gate.py -> "80/80 cases passed."
python3 tests/integration/test-plan-sign-gate.py     -> 192 ok, 0 FAIL, "all checks passed."
```

Collateral checks run from W:

```
python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit
  -> "0 unresolved reader site(s) across 100 Python file(s)" (three exempt in_memory_validation
     rows added for <gate>::_payload_command::json_string#1)
python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test
  -> PASS canonical_reader_live_classification_consistent, PASS canonical_reader_live_audit_is_zero
     (two other cases FAIL in this sparse worktree; they name board_lifecycle.py, check_state/board.py
     and absent plan.yaml files, none of them touched here)
python3 tests/unit/test-broad-catch-census.py -> ALL PASS (zero broad catches per gate; the five
     DEC-234 prologues are byte-identical)
python3 tests/integration/test-feature-corpus.py BranchCreateGate -> 3 tests OK
```
