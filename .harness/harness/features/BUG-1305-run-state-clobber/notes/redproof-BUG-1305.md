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

## SC-01-identity

baseline_sha: 592e88dcf0b6dfcd75ca4c1d49451fa9003d2802

Command with `CHECK_DOMAIN_BIN` pointed at the isolated-bin copy of
`592e88dcf0b6dfcd75ca4c1d49451fa9003d2802:.claude/skills/harness/bin/check-domain.sh`:

```text
python3 -c 'import importlib.util; p="tests/integration/test-check-domain.py"; s=importlib.util.spec_from_file_location("cd", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); raise SystemExit(m.run_bug1305_identity_cases())'
```

Verbatim output (exit 3):

```text
FAIL  [bug1305-identity] modal collision Write omitting uid is refused
      |
FAIL  [bug1305-identity] modal collision Edit removing uid is refused
      |
FAIL  [bug1305-identity] different minted uid is refused
      |
ok    [bug1305-identity] run_id disagreement keeps Issue 1124 precedence
ok    [bug1305-identity] DEC-154 resumed owner with same uid remains allowed across sessions
ok    [bug1305-identity] recovering owner with absent checkpoint remains allowed
ok    [bug1305-identity] recovering owner with zero-byte checkpoint remains allowed
ok    [bug1305-identity] legacy checkpoint without uid remains allowed
ok    [bug1305-identity] legacy checkpoint accepts incoming uid

6/9 BUG-1305 identity cases passed.
```

The three new minted-identity refusals were accepted as routine upserts by the baseline. The
fail-open cases passed on both trees, while the run-id precedence case exited 2 on both because the
existing Issue 1124 branch answered first.

### Cycle 10 Edit-route completion

The cycle-10 coverage case ran against the same pinned pre-change hook and produced this additional
discriminating failure (full run exit 4; 6/10 cases passed):

```text
FAIL  [bug1305-identity] different minted uid Edit is refused
      |
```

The live hook passes that case at exit 0 while naming both `U1` and `U2`; the pinned hook treated
the Edit as a routine checkpoint update.

## SC-05

Command with `CHECK_DOMAIN_BIN` pointed at
`c369fb1f:.claude/skills/harness/bin/check-domain.sh` in an isolated bin:

```text
python3 -c 'import importlib.util; p="tests/integration/test-check-domain.py"; s=importlib.util.spec_from_file_location("cd", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); raise SystemExit(m.run_bug1305_digest_repair_cases())'
```

Verbatim output (exit 1):

```text
ok    [bug1305-digest] digest Edit append repair remains allowed
FAIL  [bug1305-digest] digest Edit insertion is refused with append-at-end route
      | check-domain: BLOCKED — .claude/worktrees/FEAT-D/.harness/harness/features/FEAT-D-thing/runs/r1/digest.md: run digest already holds a recorded digest; this Write would replace rather than extend it. Write this cycle's digest into a run directory of its own.
ok    [bug1305-digest] cross-run digest replacement remains refused
ok    [bug1305-digest] digest Write append remains allowed

3/4 BUG-1305 digest cases passed.
```

The legal Edit append and Write append already passed, and the cross-run replacement already
failed closed. The red case was the insertion refusal's missing legal repair instruction.
