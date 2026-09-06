# QA Gate — BUG-440 digest verdict reconciliation (c3, final re-probe)

Pin: `442e0d24b25b92b1223eb18b7d16b3a0ff5b3280` (HEAD confirmed via `git rev-parse HEAD`; cycle-2
pin `a1a67956a5844c67ce098e9580ee6692a92f9a30`).

## BLUF

**V-02 STILL BOUND. V-03 STILL BOUND.** The cycle-3 restructure (splitting the case into
`_bug440_mixed_case`/`_bug440_blocking_case`/`_bug440_clean_case` + a `_bug440_validator()` helper,
`test-check-state.py:4618-4726`) did not unbind either mutant, and each still reddens through the
*same specific sub-check* cycle-2 identified. `check-state.sh` and `notes/redproof-BUG-440.md` are
byte-identical across the c2→c3 pins (0-line diffs) — the fix is confirmed test-only, as claimed.
V-04/V-05/V-07/V-08 and the SC-05 note-staleness finding are unchanged and carried forward by name;
V-06 stays RESOLVED. SC-06 is unchanged: exit 0, 217 lines, 0 `FAIL` lines — identical to cycle-2.
**VERDICT: PASS.**

## Pin discipline

- `git rev-parse HEAD` = `442e0d24b25b92b1223eb18b7d16b3a0ff5b3280` — matches the assigned pin.
- Working-tree `tests/integration/test-check-state.py` is byte-identical to the pinned blob
  (`git diff HEAD -- tests/integration/test-check-state.py` → 0 lines).
- `git diff a1a67956..442e0d24 --stat`: only `tests/integration/test-check-state.py | 63
  +++++++++++++++++++++++------------` (41 insertions, 22 deletions). `check-state.sh` and
  `notes/redproof-BUG-440.md` are both 0-line diffs across the same two pins — confirmed
  byte-identical, not assumed.
- `git status --porcelain` before and after probing: identical — only pre-existing
  `feature.json`/`plan.yaml` modifications and peer-written `notes/*-c1.md`/`*-c2.md`/`*-c3.md`
  files from concurrent reviewers. Nothing this dispatch is scoped to touch was altered.
- **Gotcha for the record:** the generic `read` tool resolves bare relative paths against the main
  checkout, not this worktree, for this session — a plain `read tests/integration/test-check-state.py`
  silently returned the STALE main-checkout copy (still showing the old `main()`-adjacent case
  layout at line ~4618, no `_bug440_*` helpers at all). Only an absolute
  `.claude/worktrees/.../tests/integration/test-check-state.py` path returned the correct pinned
  content. Every fact below is drawn from the absolute-path read or from `git show <pin>:<path>`.

## Mutation table (isolated `CHECK_STATE_BIN=` copy of the *whole* bin tree in a disposable
`.claude/worktrees/qa-bug440-c3-probe` worktree — never the live tree; anchor block matched exactly
once before each mutation; worktree torn down after probing)

| Mutant | Change | Expected | Actual | Per-subcheck |
|---|---|---|---|---|
| m1 (control) | `_dm.group(1) != _rv` → unreachable (`if False and ...`) | reddens | **reddens** | `mixed=False, blocking=False, clean=True` |
| m2 (V-02) | INV-37 finding `bad.append` → `warn.append` | reddens, via `_bug440_blocking_case` specifically | **confirmed**: `mixed=True` (unaffected — mixed fixture's `code==1` still holds via the unrelated `runs/G` digest-missing violation; found line demoted to a `note`-severity row, same text, still matched by the `INV-37` regex, so `len(lines)==1`/token/silent checks all still pass), `blocking=False` (its lone-run fixture, `entries=("M",)`, now sees exit 0 since a warn-only finding never sets `bad`, breaking the `code == 1` assertion) | `mixed=True, blocking=False, clean=True` |
| m3 (V-03) | reconciliation hung off the outer `if _errs:`'s implicit else so it also runs on invalid digests | reddens, via `_bug440_mixed_case` specifically, spurious `runs/X` line | **confirmed**: run X's digest text `"VERDICT: FAIL\n"` fails `validate()` but still carries a matchable `VERDICT:` line, so it now ALSO produces an INV-37 finding — 2 `VIOLATION` lines observed (`run M`, `run X`), tripping both `len(lines)==1` and `not any("runs/X" ...)`. `blocking`/`clean` (single-run, non-`X` fixtures) unaffected | `mixed=False, blocking=True, clean=True` |
| m5 (REQ-03(e)) | `if _rid in _recorded:` → unconditional, verdict resolved via `_recorded.get(_rid) or [None]` | reddens, via `_bug440_mixed_case`, spurious `runs/O` line | **confirmed**: run `O` (present in `runs`, absent from the `entries` panel passed to the fixture, i.e. unclaimed) now produces `digest verdict 'FAIL' ... differs from feature.json verdict None` — 2 `VIOLATION` lines (`run O`, `run M`) | `mixed=False, blocking=True, clean=True` |

Verbose output text for m2/m3/m5 captured; matches cycle-2's predicted binding sites exactly,
including the severity-label detail for m2 (demoted to `note`, not `VIOLATION`).

**Both V-02 and V-03 are STILL BOUND at this pin** — the restructure relocated where the fixtures
live and how they're invoked, but not which sub-check catches which regression.

## SC-06 re-measurement

`python3 tests/integration/test-check-state.py`: exit 0, 217 output lines, 0 lines beginning `FAIL`.
**Unchanged from cycle-2's 217/exit-0/0-FAIL measurement** — the restructure redistributed the case's
internals across three helper calls but the case itself still emits exactly one `ok/FAIL - BUG-440 ...`
print line, so the total line count did not move.

## Per-SC re-resolution

Unchanged since check-state.sh is byte-identical: **SC-02, SC-03, SC-04, SC-07** carry forward by
name at cycle-2's evidence (isolated all-agree fixture exit 0/no INV-37; five SC-03 legs each
independently pinned including by m3/m5 above; before/after sha256 unchanged=True; tail-anchor
regex/`_dtext` reuse/zero literal verdict tokens in the new region, all in check-state.sh, untouched).
**SC-01**: satisfied with the standing V-04 order-blindness gap (unremediated, not in must_fix,
untouched region — carried by name, not re-derived). **SC-05**: satisfied on substance (RED still
reproduces), with the standing low-severity note-staleness finding carried by name — no new
staleness introduced by this cycle's restructure since the note describes cycle-1/2 output shape,
which the c3 diff didn't touch. **SC-06**: satisfied, re-measured this cycle (above), identical.

## Test matrix

`change_type: bugfix` (plan.yaml, T-01, unchanged). `test_matrix.bugfix`: `unit if
touches_runtime_code` — false for the c2→c3 delta alone (test-file-only), but the *feature's* whole
diff includes T-01's original check-state.sh change, so `unit` was already obligated and satisfied at
cycle 1/2 by that task's own verify — no re-derivation owed this cycle. `integration if
fix_confined_to_tests_and_contract_docs` — same reasoning as cycle-2: evaluated against the whole
feature diff (which is not test-confined at T-01), so this leg stays inert; `integration` is
independently required regardless because `tests/integration/test-check-state.py` matches
`test_kinds.integration.detect` (`tests/integration/**`) AND is directly globbed by
`run-unit-tests.sh --kind integration`'s own `SCRIPTS=(tests/integration/test-*.py)` (confirmed by
reading the script, not inferred from the glob alone). `match_bug_class` stays inert (repository
Expertise G-08 — no taxonomy entry resolves for any diff yet). **matrix_ok: true.** The restructure
did not change how many changed units are gate-bound: the same one script (`check-state.sh`, 0-diff)
and the same one test file are both already inside the required-kind buckets; nothing new escaped.

## Carried-forward findings (not re-litigated)

V-04 (med, OPEN, SC-01 order-blindness), V-05/V-07/V-08 (low/info, OPEN, check-state.sh-anchored),
V-06 (RESOLVED c2), SC-05 note-staleness (low, OPEN). None plausibly moved by a test-file-only diff.
