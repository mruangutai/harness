# FEAT-2488 fix round 4, the final round: build (FixE4, main-session-direct under DEC-174)

The ruling is notes/answers-2026-11-24-validate-c3.md, "Fix brief — round 4", items 1 and 2. The base is HEAD
8f948c52, where T-01's intent and verify were already amended for MF-12. The receipts are in notes/fix-c4-build/.
All of this work is uncommitted. I made no git writes and no plan-merge writes. Every run had PYTHONUNBUFFERED,
HARNESS_AGENT_TYPE and CLAUDE_PROJECT_DIR unset.

Files changed (4):
- `.claude/skills/harness/bin/plan_merge/guards.py`
- `.claude/skills/harness/bin/harness_merge.py`
- `tests/integration/test-plan-merge.py`
- `tests/unit/test-harness-merge-journal.py`

amend.py and amendments.py are unchanged: everything they emit already goes through `_print_receipts`,
`_relay_after_commit` and `_die`.

## 1. The stdio class (MF-11, the _silence notes, the stderr-None members)

### One emission path in guards.py

**`_emit(name, write)`** is the one stdio path.
- It fetches `sys.<name>`.
- If that stream is None, it returns `"sys.<name> is None"` and never writes. So guards.py never calls
  `print(..., file=None)`, which CPython routes to sys.stdout.
- Otherwise it runs `write(stream)` and then `stream.flush()`.
- On `_STDIO_FAULTS = (OSError, ValueError, AttributeError)` it records the fault as text, then retries the flush.
  Only if that retry also fails does it call `_silence(stream, 1|2)`.
- A fault raised by `write`'s own work leaves a stream that still flushes untouched, so the note that follows
  can still reach it.
- It returns None or the fault text. It never raises.

**`_silence(stream, expected_fd)`** reads `fileno` through getattr and suppresses the whole tuple. It calls `dup2`
only when `fileno() == expected_fd`.

These callers now go through `_emit`:
- `_print_receipts` and `_note_on_stderr` (via the `_print_lines` writer).
- `_relay_after_commit`. Its use of `harness_boundary.relay_changed_state_feedback` runs inside
  `_emit("stderr", ...)`:
  - When stderr is None, the relay is skipped, so its rows cannot misroute to stdout.
  - When stderr is broken or closed, the fault is returned and becomes a note.

  This works around harness_boundary.py entirely; harness_boundary.py is not edited.
- `_die`, plus the refusal in `_resolve_plan` and the two station refusals, which now call `_die` (see D2).

When stderr works, every message is byte-identical to before.

### Child CLI matrix (2488/n)

Test: `case_2488_every_stdio_state_after_the_commit`.
- Each verb runs through `env -u PYTHONUNBUFFERED /bin/sh -c 'exec "$@" [1>&-] [2>&-]'`, with a relay row planted.
- "closed" means the sys stream object is closed before `runpy` runs the CLI.
- "none" means the fd is closed at exec.
- Every case asserts:
  - rc 0;
  - both files carry the amendment, ledgered exactly once;
  - no journal is left;
  - a working stdout equals exactly the receipts;
  - a working stderr has the relay row and no receipt or Traceback, and has the "landed" note exactly when stdout
    failed;
  - a closed stream's fd received no bytes.

Red is `fix-c4-build/mf11-red.txt`: HEAD's guards.py blob dropped into an rsync copy of the worktree. Green is
`mf11-green.txt`, and the full integration kind. Both verbs give the same result in every row.

| stdout / stderr | red at HEAD | now |
|---|---|---|
| working / working (SC-04 byte-exact) | green | green |
| broken / working | green (MF-9) | green |
| closed / working | green | green |
| **none / working** | **RED**: rc 1, AttributeError Traceback (MF-11) | green |
| working / broken | green | green |
| working / closed | green | green |
| **working / none** | **RED**: relay rows misrouted into stdout | green |
| broken / broken | green | green |
| **none / none** | **RED**: rc 1 | green |
| **none / broken** | **RED**: rc 1 | green |
| **broken / none** | **RED**: rc 1 | green |

### In-process cases (2488/o)

Tests: `case_2488_in_process_captures_after_the_commit` and `case_2488_a_caller_owned_fd_is_never_clobbered`.

| case | red at HEAD | now |
|---|---|---|
| capture with no fileno and no flush, as stdout | **RED** (AttributeError) | green |
| the same capture, as stderr | **RED** (AttributeError) | green |
| StringIO subclass, `fileno()` raises io.UnsupportedOperation, stdout and stderr | green (regression lock) | green |
| real broken stream on caller-owned fd 4, as stdout | **RED** (fd 4 dup2'd to devnull) | green, fd 4 still the caller's pipe |
| the same stream, as stderr | green | green, fd preserved |

### Mutants

`mf11-mutants.txt`: each mutant runs in an rsync copy with only guards.py mutated. A control run of the unmutated
copy gives 0 FAILs. Every mutant is killed.

| mutant | what it changes | FAILs | cases that fail |
|---|---|---|---|
| M1 | dup2 over whatever `fileno()` names | 2 | caller-owned fd |
| M2 | no None check in `_emit` | 2 | working / none misroute, both verbs |
| M3 | the tuple without AttributeError | 3 | no-flush capture |
| M4 | `_emit` never silences | 10 | broken-pipe rows |
| M5 | relay called outside `_emit` | 2 | working / none misroute |

### Regression locks

2488/a, g, h, k, l and m are green in `mf11-green.txt` and in the full integration kind. SC-04 (2488/g)
byte-identity is green.

## 2. The journal class (MF-12, remedy (b))

### The change in harness_merge.py

- **`_JOURNAL_NAME = JOURNAL_PAIR[0] + JOURNAL_SUFFIX`.**
- **`_journals_naming`** looks up that ONE name as a path, with `os.lstat`, and returns `[]` on
  FileNotFoundError. It then asks `_journal_names(journal_path, name)` whether the journal names `path`. Any other
  `*.harness-merge.journal` is never listed, read, locked or replayed.
- **`_journal_names(journal_path, name)`**: the `entry` parameter is gone. The real journal always names its primary
  (`name == JOURNAL_PAIR[0]`). An unreadable real journal still names every file, so fail-closed is kept.
- **`_recover_journal`**: the pre-lock "named for another file" refusal is removed. Discovery now hands over only
  the one name, so that refusal can no longer be reached. The regular-file check before any lock stays.
- **The module docstring** now states that the discovery set equals the producer set.
- **check-domain's two-name denial** is untouched, as ruled.

### D1: deviation from the ruling's literal filter

The ruling's literal filter is `os.listdir` + `entry == JOURNAL_PAIR[0] + JOURNAL_SUFFIX`. I implemented a path
lookup of that same one name instead.

On a filesystem that folds case (this machine, APFS), `os.replace` onto an existing case variant keeps the variant's
spelling. I measured it: replacing onto `PLAN.YAML.j` leaves `['PLAN.YAML.j']`.

So suppose a `Plan.yaml.harness-merge.journal` appears inside the lock window, and then a crash follows the
publish. The real pending journal is then LISTED under the variant spelling:
- The literal filter skips it, so the torn pair goes silent.
- The path lookup finds it, because it is the producer's own file.

Evidence:
- `case_the_producers_name_as_the_filesystem_resolves_it` is red at HEAD.
- `fix-c4-build/mf12-mutant-listdir-filter.txt`: the literal filter, mutated in, fails exactly this check.

On a case-sensitive filesystem the variant is foreign and inert, and the two forms behave identically. The variant
is the same file the check-domain denial already case-folds.

### Journal matrix (`tests/unit/test-harness-merge-journal.py`)

Red is `fix-c4-build/mf12-red.txt` (HEAD harness_merge.py): 31 of 185 checks fail, and
`case_the_real_journal_recovers_beside_foreign_ones` raises. Green is `mf12-green.txt`: 202 of 202.

| case | red at HEAD | now |
|---|---|---|
| each of {garbage `evil.harness-merge.journal`, well-formed `BRIEF.md.harness-merge.journal`, well-formed reversed `feature.json.harness-merge.journal`} × {`locked_update(plan.yaml)`, `locked_update(feature.json)`, `locked_pair_update`}: succeeds, writes on the bases, foreign file byte-identical, takes only the route's own locks in plan→feature order | **RED** ×18 (exit 5) | green |
| `recover_journals(plan / feature.json / notes.txt)` with only foreign files: returns False, no byte changes | **RED** ×3 | green |
| real journal, torn {primary at after, secondary at after, both at after} × {`recover_journals(primary)`, `locked_update(primary)`, `locked_update(secondary)`}, beside every foreign file: converges, foreign files untouched | **RED** (raises) | green |
| an unreadable REAL journal beside every foreign file: exit 5 naming the REAL journal via all three routes and `notes.txt`; writes nothing | **RED** ×4 (HEAD named BRIEF.md's journal) | green |
| a case variant arriving in the lock window, then pending: recovery rolls it forward | **RED** | green |
| a foreign FIFO `other.harness-merge.journal` via `locked_update(notes.txt)` and `locked_update(plan)`: returns exit 0, never hangs, FIFO left in place | **RED** ×4 | green |

Changes to existing tests:
- `case_reversed_primary_refuses_before_any_lock` is removed. Its claim, that the journal refuses, is the semantics
  this ruling replaces. Its lock-order guarantee is kept in the foreign case as "takes only its own locks, in order".
- NON_REGULAR's "a FIFO under another journal name" row moved to `case_a_foreign_fifo_is_never_opened`, with the
  new expectation.

The drift-pin (T-09 13) is green in the full integration kind and in T-01's verify.

### Discovery sites checked

1. `harness_merge._journals_naming`: narrowed. This is the one discovery.
2. `harness_merge._journal_names`: now follows the one-name rule.
3. `harness_merge._recover_journal`: the unreachable name refusal is removed and the regular-file check is kept.
4. `harness_merge.recover_journals`: iterates (1). Unchanged.
5. `harness_merge.locked_update`: its under-lock re-check uses (1). Unchanged.
6. `harness_merge.locked_pair_update`: recovery and its re-check use (1). The producer path
   `primary + JOURNAL_SUFFIX`, with the primary pinned by `_pair_directory`, equals `_JOURNAL_NAME`.
7. `plan_merge/guards._recover_plan_journals`: calls `recover_journals` only.
8. `feature_json_write`: `locked_update` only, with no discovery of its own.
9. `check-domain.py` `_PAIR_JOURNALS` and `RE_PAIR_JOURNAL`: a denial, not discovery. Unchanged as ruled.
10. `plan_merge/*.py`: no journal name or suffix appears (T-02's verify asserts this).
11. Tests:
    - test-plan-merge `_PAIR_JOURNAL_SUFFIX` uses the real name only.
    - test-check-domain-approval `_JOURNAL_SIDECARS` is the drift pin.

`rg 'JOURNAL_SUFFIX|harness-merge\.journal|_journals_naming|_journal_names|recover_journals|JOURNAL_PAIR'`
across the repo, excluding `.harness/`, finds no other site.

## D2: refusals through _emit

`_die` now emits through `_emit`. A refusal can follow a published journal: amend and record-amendments report
JournalPending as exit 2 through `_die`. Before this change, a broken stderr turned that into a Traceback and rc 1,
and a None stderr moved the lines onto stdout. `_resolve_plan`'s refusal, which carries a recovery replay's exit 2,
and the two station refusals now call `_die` too, so guards.py has no other stdio call.

## Verification (all in fix-c4-build/)

- `unit.txt`: run-unit-tests.py --kind unit. 68 files, 0 FAIL, exit 0.
- `integration.txt`: --kind integration. 95 files, 0 FAIL, exit 0.
- `verify-T-01.txt` (the amended literal) and `verify-T-02.txt`: both exit 0.
- `canonical-reader-audit.txt`: 0 unresolved reader sites across 101 files, exit 0.
- `c4-diff.txt`: `git diff 2491336e` over check-plan-routes.py, test-check-plan-routes.py, check_state/,
  plan_merge/union.py and test-checker-structure-locks.py is empty.
- `grade-changed.txt`:
  - Every new or changed production function is grade 4 or 5.
  - Tests are grade ≥ 3. The grade-3 tests are `case_2488_in_process_captures_after_the_commit` (ABC 21.4) and
    `case_the_producers_name_as_the_filesystem_resolves_it` (ABC 23.3).

## Out of scope, for Main

`feature_json_write.write_feature_json` relays through `harness_boundary.relay_changed_state_feedback` directly
(`feature_json_write.py:227`). That line is unchanged from base 2491336e. plan-merge's `sign-approval` and
`revoke-approval` reach it (approval.py:535 and :581). With stderr None, their feedback rows print to stdout.

This is not the amend/record-amendments contract the ruling's matrix covers, and feature_json_write.py is outside
this round's files. The same `_emit` wrapping at that call site would close it if it is ruled in.
