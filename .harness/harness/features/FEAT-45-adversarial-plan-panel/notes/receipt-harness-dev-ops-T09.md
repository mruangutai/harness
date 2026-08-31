# Receipt — harness-dev-ops — FEAT-45 T-09

**BLUF:** T-09 built. `panel_findings.py` implements the content-hash identity, its test
`test-panel-findings.py` was authored first and observed RED, then GREEN after the
implementation, and it is registered in `run-unit-tests.sh`'s `UNIT_SCRIPTS`. Plan's `verify:`
block ran verbatim from the worktree root and exited 0. Unit runner overall: 0 `^FAIL ` lines,
exit 0. No commit made.

## RED evidence (observed before `panel_findings.py` existed)

```
$ python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
Traceback (most recent call last):
  ...
  File ".../test-panel-findings.py", line 30, in pf
    spec.loader.exec_module(mod)
  ...
FileNotFoundError: [Errno 2] No such file or directory: '.../panel_findings.py'
exit=1
```

## GREEN (after implementation)

```
9/9 checks passed
PASS test-panel-findings.py
exit=0
```

## `verify:` block, byte-cross-checked against plan.yaml:995-1004, run from worktree root

Exit code: **0**. Includes the full `test-panel-findings.py` run (9/9 pass) plus the
`run-unit-tests.sh --kind unit` invocation (which also runs the unrelated existing suite,
including a pre-existing `factory: decompose` stderr line from an unrelated test that is not
part of T-09's files and asserts nothing about its own exit code) and the three id-equality/
inequality/length checks. All passed.

## Unit runner overall result (separate run, not tail-read)

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/t09-unit.out 2>&1; st=$?
$ grep -c '^FAIL ' /tmp/t09-unit.out
0
$ echo "exit=$st"
exit=0
```

0 `^FAIL ` lines, exit 0 — a genuinely green suite, not a tail-read.

## No commit

```
$ git status --porcelain
 M .claude/skills/harness/bin/run-unit-tests.sh
 M .harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml   <- pre-existing, not T-09's
?? .claude/skills/harness/bin/panel_findings.py
?? .claude/skills/harness/bin/test-panel-findings.py
$ git log --oneline -1
2d7cbac FEAT-45 T-01: record the two structural carve-outs as DEC-206 and DEC-207   <- unchanged
```

`plan.yaml`'s modified status was present in `git status` before this task started any edit and
was not touched by this run — it belongs to a status update outside T-09's file set.

## Design notes

- `finding_id`/`normalize_summary` and the CLI (`id --reader R --summary S`) match D-05 exactly:
  sha256(reader + "\n" + normalize(summary)), `PF-` + first 8 lowercase hex chars, length 11.
- CLI exits 2 with a stderr message on empty reader or whitespace-only-normalized summary.
- Module docstring states the WHY (content hash vs sequential id) as required by the intent.
- File modes match directory convention: `panel_findings.py` executable (755, matches
  `observations-merge.py`), `test-panel-findings.py` non-executable (644, matches
  `test-observations-merge.py`).
- `run-unit-tests.sh` line 30: appended the literal string `"test-panel-findings.py"` to
  `UNIT_SCRIPTS`; no other line in that file changed. `harness.json` and `INTEGRATION_SCRIPTS`
  untouched, per non-goals.

## Open questions

None.

## Mutation-RED evidence (cycle 1)

The cycle-0 RED (`FileNotFoundError`, module absent) only proved the suite imports
`panel_findings.py`. It did not show that any of the 9 checks discriminate a wrong
implementation from a correct one. This cycle proves discrimination directly: five mutants,
each a single deliberate defect, each run against the real `test-panel-findings.py` via
`PANEL_FINDINGS_BIN` — never editing the module or the test in the repo. Every mutated copy
lived at `/tmp/pf-mutants/<name>.py` only; none was ever written into the worktree.

### Mutants and results

| Mutant | Change | Expected FAIL | Actual FAIL(s) | Exit |
|---|---|---|---|---|
| M1 `no_normalize` | `normalize_summary` returns `summary` unchanged | case2 | case2, **case5b** (unexpected, reported not suppressed) | 1 |
| M2 `over_normalize` | normalize also strips all digits (`re.sub(r"[0-9]", "", ...)`) | case3 | case3 | 1 |
| M3 `reader_ignored` | digest input built from normalized summary alone, dropping reader and newline | case4 | case4 | 1 |
| M4 `wrong_shape` | digest suffix uppercased instead of the plain lowercase 8-char slice | case1 | case1 (`suffix is 8 lowercase hex characters`) | 1 |
| M5 `no_guard` | both empty-input guards deleted from `_cli_id`; always prints and returns 0 | case5a AND case5b | case5a, case5b | 1 |

All five mutants reddened at least the expected case, with a non-zero exit in every run. No
mutant ran GREEN, so no case is vacuous and `test-panel-findings.py` needed no edit this
cycle.

M1's extra fail is explained, not suppressed: `no_normalize` also breaks the CLI's
whitespace-only-summary guard, because `_cli_id` checks `not normalize_summary(summary)` —
with normalization disabled, `"   \t  "` is truthy and the guard never fires, so case5b
(which is a real, independent discriminator for that guard) reddens too. This is a second
genuine defect signature from the same mutation, not a false positive.

```
$ PANEL_FINDINGS_BIN=/tmp/pf-mutants/m1_no_normalize.py python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
FAIL  case2: normalization-only difference gives the same id
FAIL  case5b: whitespace-only summary exits 2
7/9 checks passed
exit=1

$ PANEL_FINDINGS_BIN=/tmp/pf-mutants/m2_over_normalize.py python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
FAIL  case3: one-character summary change gives a different id
8/9 checks passed
exit=1

$ PANEL_FINDINGS_BIN=/tmp/pf-mutants/m3_reader_ignored.py python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
FAIL  case4: different readers give different ids
8/9 checks passed
exit=1

$ PANEL_FINDINGS_BIN=/tmp/pf-mutants/m4_wrong_shape.py python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
FAIL  case1: suffix is 8 lowercase hex characters
8/9 checks passed
exit=1

$ PANEL_FINDINGS_BIN=/tmp/pf-mutants/m5_no_guard.py python3 .claude/skills/harness/bin/test-panel-findings.py; echo "exit=$?"
FAIL  case5a: empty reader exits 2
FAIL  case5b: whitespace-only summary exits 2
7/9 checks passed
exit=1
```

### Repo cleanliness after mutation testing

```
$ ls .claude/skills/harness/bin/panel_findings*.py
.claude/skills/harness/bin/panel_findings.py
$ ls .claude/skills/harness/bin/test-panel-findings*.py
.claude/skills/harness/bin/test-panel-findings.py
$ git status --porcelain
 M .claude/skills/harness/bin/run-unit-tests.sh
 M .harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml
?? .claude/skills/harness/bin/panel_findings.py
?? .claude/skills/harness/bin/test-panel-findings.py
?? .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/receipt-harness-dev-ops-T09.md
```

Same three T-09 paths plus the pre-existing `plan.yaml` modification as cycle 0, plus this
receipt itself (untracked, being appended to in this cycle). No stray mutant path in the
repo tree; no other new entry.

### `verify:` block re-run, real module in place (final)

Byte-cross-checked again against `plan.yaml:995-1004` before running.

```
9/9 checks passed
PASS test-panel-findings.py
verify_exit=0
```

### Unit runner overall, counted (final)

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/t09-unit-c1.out 2>&1; st=$?
$ grep -c '^FAIL ' /tmp/t09-unit-c1.out
0
$ echo "exit=$st"
exit=0
```

### No commit, unchanged

```
$ git log --oneline -1
2d7cbac FEAT-45 T-01: record the two structural carve-outs as DEC-206 and DEC-207
```

HEAD unchanged from cycle 0. No `panel_findings.py`, `test-panel-findings.py`, or
`run-unit-tests.sh` edit was made this cycle — every mutant lived and died in `/tmp`.
