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

## SC-01

Command with `HARNESS_BOUNDARY_BIN` pointed at `harness_boundary.py` from `c369fb1f`:

```text
python3 tests/unit/test-harness-boundary.py
```

Verbatim discriminating output (exit 1):

```text
FAIL case_run_identity_pattern_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'RE_RUN_IDENTITY'")
```

## SC-10

Command with `CHECK_DOMAIN_BIN` pointed at `check-domain.sh` from `c369fb1f` in an isolated bin:

```text
python3 -c 'import importlib.util; p="tests/integration/test-check-domain.py"; s=importlib.util.spec_from_file_location("cd", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.run_bug1305_marker_cases()'
```

Verbatim discriminating output:

```text
FAIL  [bug1305] foreign first Write is refused by witness
FAIL  [bug1305] foreign Edit is refused by witness
FAIL  [bug1305] witness outranks an unparseable prior
FAIL  [bug1305] witness outranks legacy run_id ladder
FAIL  [bug1305] unreadable witness fails closed
FAIL  [bug1305] Write of existing witness is refused
FAIL  [bug1305] Edit of existing witness is refused
FAIL  [bug1305] Write creating false witness is refused
FAIL  [bug1305] run_uid is a legal checkpoint key
FAIL  [bug1305] POST mints uid and matching witness
FAIL  [bug1305] second POST is byte stable
4/15 BUG-1305 marker cases passed.
```

### Witness guard and the first-write window

The pinned hook allowed a foreign first `Write` because no prior `state.yaml` existed to compare. The durable witness closes that window: it records the directory identity independently of the checkpoint and is itself write-once on both Write/Edit and Bash mutation routes.

## SC-02

Command with `CHECK_STATE_BIN` pointed at `check-state.sh` from `c369fb1f` in an isolated bin:

```text
python3 -c 'import importlib.util; p="tests/integration/test-check-state.py"; s=importlib.util.spec_from_file_location("cs", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); raise SystemExit(0 if m.case_bug1305_run_identity_invariant() else 1)'
```

Verbatim output (exit 1):

```text
FAIL - BUG-1305 INV-36 detects clobbers and stays silent on owned/legacy runs
        bad_ok=False; clean exit=1; clean violations=["  VIOLATION  harness/features/FEAT-TEST/runs/Y/state.yaml: non-checkpoint top-level key(s) ['run_uid'] — state.yaml carries only identifiers, enums, counters, paths and sequence markers (DEC-154). Findings and assessment prose belong in that run's digest.md; a one-line note: per step entry is the ceiling."]
```

The pinned checker reported none of the three witness disagreements; it only rejected `run_uid` as an unknown checkpoint key.
