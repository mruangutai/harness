# Receipt — harness-backend-dev — FEAT-32 T-03 (c2)

**Task:** T-03 send-back — the create path must not carry the proposal's approval.

## The fix

`.claude/skills/harness/bin/plan-merge.py`, `apply_merge`'s `base_bytes is None` branch: after
the existing `safe_load` validity check, if `APPROVAL_REFUSAL` is on and the proposal's parsed
doc carries an `approval` key at all, raise `MergeRefusal(8, ...)` — nothing is written, no file
is created. The refusal message names the mapping (`base approval: <absent>`, the proposal's
loaded value) and states the signer is the main session, the same shape step 7b already prints.
A proposal with no `approval` key is unaffected: written whole, exit 0, as in cycle 1. With
`APPROVAL_REFUSAL = False` the create path reverts to writing whole regardless of an approval key
— same literal, same behavior direction as step 7b's own toggle.

Reasoning, stated in the code comment: step 3's "a base that does not exist is an empty mapping"
and step 7b's "a proposal's approval differing from the base's is refused" read together — an
empty mapping has no approval key, so any approval value the proposal carries "differs" from the
base's absence. No new rule invented.

## Test — case 11, added and RED-proofed before the fix

`test-plan-merge.py`, `case_create_path_approval()` (case 11), two directions:
- **11a** — base absent, proposal carries no approval key → exit 0, file created, T-01..T-03
  present by id.
- **11b** — base absent, proposal carries `APPROVED_APPROVAL` → exit 8, **`os.path.exists(path_b)`
  is False afterward** (the create-path analogue of case10a's byte-identity check — a refusal
  that still created the file is exactly what this catches), stdout/stderr names `approval` and
  `main session`, and no stray file other than `plan.yaml.lock` in the fixture directory
  (harness_merge's flock is deliberately never removed, per D-02 and case5's own precedent).

**TDD order, verified before touching production code.** Wrote case 11 against the untouched
(cycle-1) `plan-merge.py` first and ran it:

```
FAIL  case11b: create with an approval key exits 8
FAIL  case11b: no file was created by the refused apply
FAIL  case11b: stdout/stderr names the approval mapping
FAIL  case11b: stdout/stderr names the main session as the signer
FAIL  case11b: no stray tempfile/lockfile left behind after the refusal
```

(11a's five assertions passed unchanged, as expected — the no-approval-key direction was already
correct in cycle 1.) Then implemented the fix; case 11 (all 11 assertions, both directions) went
GREEN, and no other case's assertions moved.

## Mutation proof — `APPROVAL_REFUSAL` mutated to `False` by name, tree copy

Ran `plan-merge.py`'s own literal-flip recipe (`s.replace("APPROVAL_REFUSAL = True", "APPROVAL_REFUSAL = False", 1)`, `assert m != s`) against a `shutil.copytree`'d tree, confirmed the mutant
imported and ran (the suite produced full PASS/FAIL output, not an import crash), then re-ran the
suite with `PLAN_MERGE_BIN` pointed at the mutant. Verbatim FAIL lines:

```
FAIL  case10a: differing approval exits 8
FAIL  case10a: stdout/stderr names the approval mapping and both loaded values
FAIL  case10a: file is byte identical to before (nothing applied)
FAIL  case10a: T-15 is absent, asserted by id
FAIL  case11b: create with an approval key exits 8
FAIL  case11b: no file was created by the refused apply
FAIL  case11b: stdout/stderr names the approval mapping
FAIL  case11b: stdout/stderr names the main session as the signer
FAIL  case11b: no stray tempfile/plan.yaml left behind after the refusal
FAIL test-plan-merge.py
```

## The three literals against the same mutation harness — case-set mapping vs cycle 1

- `UNION_MERGE = False` → reddens case2, case3, case4, case5, case9, case10a — **identical set
  to cycle 1.**
- `PRESERVE_BASE_BYTES = False` → reddens case3, case9 only — **identical set to cycle 1.**
- `APPROVAL_REFUSAL = False` → reddens case10a (as in cycle 1) **plus case11b**, which is new
  because case 11 exercises the same literal on the create path. This IS a change to the mapping,
  named explicitly per the dispatch: case10a's four assertions are unchanged, and case11b's five
  assertions are the newly-caught surface.

## `verify:` — re-run unchanged, exit 0

Ran the task's `verify:` string verbatim, with the one substitution declared and accepted in
cycle 1 (`cp -R "$S" "$T/bin"` → a `python3 -c "shutil.copytree(...)"` call into the same
`mktemp -d` location; `bash-write-guard.sh` denies the literal `cp -R` because it resolves `$T`
unexpanded as an out-of-domain target). All three RED-PROOF legs correctly failed the mutated
copy, then the full suite (99 assertions now, cases 1-11) ran clean. Overall exit code: `0`.

## `--check-kinds`

```
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's explicit script list
EXIT_CODE=2
```

Unchanged from cycle 1 — pre-existing, registration is T-10's (dev-ops), nothing here to fix.

## Rules held

- Cycle 1's assertions: none removed, none weakened. Case 5's self-authored "lock file is gone"
  check remains replaced by the stray-tempfile check (D-02: flock is deliberately never removed)
  — not revisited this cycle.
- Only `plan-merge.py` and `test-plan-merge.py` touched. `harness_merge.py` untouched.
- `yaml` imported plainly, unchanged. `harness_yaml.py` divergence still routed upward, not
  resolved here (unchanged open question from cycle 1, restated below).

## Open items I did not resolve

- **`harness_yaml.py` divergence** — still not mine to resolve per the dispatch; `yaml` imported
  plainly in both files.
