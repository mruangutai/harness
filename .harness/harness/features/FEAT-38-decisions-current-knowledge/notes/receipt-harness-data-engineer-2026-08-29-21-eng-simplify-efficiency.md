# EFFICIENCY angle — FEAT-38 plan-surface simplify pass

Read-only. No writes to `plan.yaml` or `BRIEF.md`. No full unit suite (`--kind all`) run.

## Measured wall-clocks (verbatim)

```
$ time bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration
... (222 PASS lines, exit 0)
real    2m37.699s
user    1m28.796s
sys     0m42.764s
EXIT:0
```

```
$ time bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
check-kinds: the script arrays and test_kinds.integration.detect agree.
real    0m0.201s
user    0m0.126s
sys     0m0.144s
```

```
$ time python3 .claude/skills/harness/bin/test-check-decision-anchors.py
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_malformed_anchor_extension_reports_line_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
ok - test_live_authority_anchors_all_resolve
real    0m0.365s
user    0m0.260s
sys     0m0.101s
EXIT:0
```

```
$ time git grep -lE 'subprocess|shlex|shell=|Popen|os\.system|eval\(' -- .claude/skills/harness/bin | wc -l
72
real    0m0.043s
user    0m0.044s
sys     0m0.067s
```

```
$ time (enumerate 72 candidates, then run 72x `grep -qE '^\| <base> \| ...' <note>`)
real    0m0.063s
user    0m0.067s
sys     0m0.032s
```

```
$ time python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout > /tmp/genidx.out
real    0m0.053s
```

```
$ time python3 -c "import json; json.load(open('.harness/harness.json'))"   # 10710 bytes
real    0m0.037s
```

## Verify-block inventory, T-18..T-21 (done, amended) and T-24..T-29

| Task | Command(s) | Measured/estimated cost |
|---|---|---|
| T-18 | `python3 - <<'PY'` inline json.load of `.harness/harness.json` | ~0.04s (interpreter start dominates) |
| T-19 | `grep` x2 on run-unit-tests.sh + `bash "$R" --kind integration` + 2 greps on captured output | **157.7s** (measured) — see Finding EFF-01 |
| T-20 | `git cat-file -e` x2, `git ls-files --error-unmatch` x2 | milliseconds each, negligible |
| T-21 | `git show 48bbe7e:D \| grep -c`, `grep -q` x1, `gen-decisions-index.py --stdout >/dev/null` | ~0.05–0.1s, negligible |
| T-24 | `grep` x2 on run-unit-tests.sh + `bash "$R" --kind integration` + 2 greps on captured output | **157.7s** (measured) — see Finding EFF-01 |
| T-25 | `python3 - <<'PY'` json.load of harness.json + `bash run-unit-tests.sh --check-kinds` | ~0.04s + 0.2s = ~0.24s. Already the cheap pattern. |
| T-26 | `git ls-files --error-unmatch` x2, `test -e` x2, `test -f`, one unscoped `git grep -l` sweep | sub-second; the sweep is a single grep over the tree, not timed separately (not in scope list) but structurally one call, not repeated |
| T-27 | `git show 48bbe7e:D \| grep -c`, 2 more greps on D, loop of 6 `grep -qE` for headings | sub-second, all single-pass greps on one file |
| T-28 | `sed -n` extraction, 5 greps on the extracted block, `gen-decisions-index.py --stdout \| diff` | **~0.05s** measured for the generator; sed/grep/diff on a single small file — negligible |
| T-29 | `git grep -lE ...` (measured 0.043s, 72 files) + 72x `grep -qE` per candidate against the note | **~0.06s** measured total — negligible |

## Findings

### EFF-01 — T-24 (`plan.yaml:1748-1750`) runs the full integration kind (157.7s measured) to prove two facts a 0.57s combination proves identically

`plan.yaml:1748` (`OUT="$(bash "$R" --kind integration 2>&1)"`) drives all 29 `INTEGRATION_SCRIPTS`
end to end to extract exactly two facts from the captured output: no `^KIND-DRIFT:` line
(`plan.yaml:1749`), and `PASS test-check-decision-anchors.py` present (`plan.yaml:1750`).

Read `run-unit-tests.sh:96-140`: the KIND-DRIFT cross-check runs on *every* invocation — `--kind
integration`, `--kind all`, and `--check-kinds` — as the identical code path, before any test
dispatch. `--check-kinds` (measured 0.201s real / 0.38s wall) exits right after that check
(`run-unit-tests.sh:142-145`) and asserts nothing else. The runner's own per-script step
(`run-unit-tests.sh:148-157`) is `python3 "$BIN_DIR/$s"; echo PASS/FAIL $s` — exactly what a direct
`python3 .claude/skills/harness/bin/test-check-decision-anchors.py` (measured 0.365s, exit 0) checks
by its own exit code, with no output-string parsing needed.

**Cheaper binding alternative:** replace `bash "$R" --kind integration` with
`bash "$R" --check-kinds && python3 "$BIN_DIR/test-check-decision-anchors.py"`. Combined measured
cost ≈0.57s vs 157.7s — about 276x cheaper. **Binds exactly as tightly**: both assertions T-24
actually makes (drift-absence, anchor-script pass) come from the identical code path / identical
subprocess+exit-check the runner performs internally; nothing else in the 157.7s run is asserted —
T-24's own intent (`plan.yaml:1779-1784`) explicitly states the verify does *not* sweep for FAIL
lines from the other 28 integration scripts, because their state depends on interleaving with other
lanes. No assertion is lost.

Severity: advisory (efficiency, not correctness) — but the cost is concrete and per-invocation of
this verify, e.g. every re-verification pass and every review-gate re-run pays 157s for a check that
needs 0.57s.

### EFF-02 — T-19 (`plan.yaml:1424-1426`, amended `done` task) runs the byte-identical expensive command for the byte-identical claim, at the byte-identical final state, as T-24

T-19's verify (`plan.yaml:1419-1427`) and T-24's verify (`plan.yaml:1743-1751`) both run
`bash "$R" --kind integration` and then assert the same two facts (no `^KIND-DRIFT:`, `PASS
test-check-decision-anchors.py` present). T-19's own intent (`plan.yaml:1451`) states it is "Graded
at final state, after T-24 lands" — i.e. both verifies run against the same commit and prove the
identical fact twice. Each run costs 157.7s measured; running both costs ≈315s to establish one
fact once.

**Cheaper binding alternative:** same substitution as EFF-01 for T-19's block. Binds equally tightly
for the same reason (identical code path). This does not remove either task's verify — both tasks
still gate their own registration edit — but it removes the duplicated 157s tax paid twice for one
fact.

Severity: advisory. Not a correctness gap — the plan is explicit about why the two-sided check
exists (drift asymmetry) — but the *mechanism* used to prove it (a full integration run) is
duplicated where the cheap mechanism (`--check-kinds` + direct script invocation) is already used
correctly by T-25 (`plan.yaml:1810`).

### Checked, not flagged

- **T-25** (`plan.yaml:1810`) already uses `--check-kinds` (measured 0.38s) rather than a full kind
  run — this is the efficient pattern EFF-01/EFF-02 recommend elsewhere. No finding.
- **T-29's 72-candidate grep loop** (`plan.yaml:2019-2035`): measured end-to-end at ~0.06s for the
  enumeration plus 72 greps against a worst-case (empty) note. Negligible — does not matter at any
  scale this note will reach. Not a finding.
- **`.harness/harness.json` re-parsing across T-18/T-19/T-24/T-25`**: parsed directly by T-18, T-25,
  and internally by the KIND-DRIFT check inside every `run-unit-tests.sh` invocation (T-19, T-24,
  T-25's `--check-kinds`) — up to 5 parses of a 10,710-byte file across the whole sequence, each
  measured at ~0.037s (dominated by Python interpreter startup, not JSON size). Total ≈0.19s spread
  across independently-scheduled tasks run by different agents at different times, not one pass that
  could feed several. Not a finding.
- **`DECISIONS.md` re-reads across T-27/T-28**: each is a single grep/sed pass over one file,
  sub-millisecond-class per call. Not a finding.
- **`run-unit-tests.sh`'s own text re-read (grep for registered/deregistered strings) across
  T-18/T-19/T-24/T-25**: each is a single `grep` over a script file of a few hundred lines —
  negligible, not the cost driver; the cost driver is the *execution* the same commands trigger
  (EFF-01/EFF-02), not the text reads.
- **Full-suite runs**: none of T-18..T-29's verify blocks run `--kind all`. No boundary-step
  full-suite run exists in this scope to defend or flag.

## Summary

Two findings (EFF-01, EFF-02), both advisory, both backed by wall-clock measurement, both pointing
at the same substitution (`--check-kinds` + direct script invocation replacing a full `--kind
integration` run) which is demonstrably already in use correctly at T-25. Everything else inventoried
is sub-second and not worth PM's attention.
