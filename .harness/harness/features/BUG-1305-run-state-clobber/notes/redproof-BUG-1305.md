# Red proofs — BUG-1305

## T-01

Command before `run_identity.py` existed:

```text
python3 tests/unit/test-run-identity.py
```

Verbatim output (exit 1):

```text
FAIL case_seed_is_write_once FileNotFoundError(2, 'No such file or directory')
FAIL case_marker_absent_and_unreadable FileNotFoundError(2, 'No such file or directory')
FAIL case_uid_mint_and_injection FileNotFoundError(2, 'No such file or directory')
FAIL case_seed_conflict_guards FileNotFoundError(2, 'No such file or directory')
FAIL case_uid_conflicts FileNotFoundError(2, 'No such file or directory')
```

## SC-04

Command while `check_artifact_file` still had its pre-change single-candidate fail-open branch:

```text
python3 -c 'import importlib.util; p="tests/integration/test-validate-digest.py"; s=importlib.util.spec_from_file_location("vd", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); raise SystemExit(1 if m.run_bug1305_artifact_resolution_cases() else 0)'
```

Verbatim discriminating output (exit 1; unaffected passing cases omitted only outside this fenced capture):

```text
FAIL  [bug1305-artifact] existing run directory without digest is refused
      | expected exit 2, got 0
      | stderr should mention '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/vd-bug1305-00ezp0b8/.claude/worktrees/FEAT-X/runs/r1'
      | stderr should mention 'missing'
      | check-digest: harness-eng-lead's artifact runs/r1/digest.md not found from the hook's vantage — file-shape check skipped; check-state.sh INV-15 will audit it from repo root.
```

The non-compliant fixture is the resolved, existing run directory with no durable `digest.md`; the old hook passed it with exit 0.
