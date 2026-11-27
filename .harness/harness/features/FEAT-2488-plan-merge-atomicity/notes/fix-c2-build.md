# Fix round c2 build — FEAT-2488 — 2026-11-24

Builder: FixE2, ungoverned, main-session-direct under DEC-174. Contract: validate c1 digest
(`runs/r-20261124-3-validate-validator/digest.md`) MF-8 then MF-7, plus the test-only advisories, under
C4/C5/C6 (`answers-2026-11-23-signoff.md`) and the c0 fix ruling (`answers-2026-11-24-validate-c0.md`). Reds are
against HEAD `13500626`. The working tree is uncommitted: no git writes of any kind (no commit, no temporary clone,
no worktree), and no plan-merge writes. `HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` were
unset for every run. Receipts are in `notes/fix-c2-build/`.

## Files

- `.claude/skills/harness/bin/harness_merge.py`: MF-8 (`_regular_fd_bytes` new, `_journal_bytes`), docstrings of
  `_require_regular` and the module (the "opened only when it is a regular file" sentence).
- `.claude/skills/harness/bin/plan_merge/guards.py`: MF-7. `_relay_after_commit` moved here from amendments.py and
  its fallback now suppresses `(OSError, ValueError)`; new `_print_receipts`; `_locked_plan_update` relays through
  `_relay_after_commit`; `import contextlib`.
- `.claude/skills/harness/bin/plan_merge/amendments.py`: MF-7. `_relay_after_commit` removed (imported from
  guards), receipts through `_print_receipts`; the now-unused `contextlib` and `harness_boundary` imports dropped.
- `.claude/skills/harness/bin/plan_merge/amend.py`: MF-7 audit site. Receipts through `_print_receipts`.
- `tests/unit/test-harness-merge-journal.py`: MF-8 red case; the four hostile shapes.
- `tests/integration/test-plan-merge.py`: MF-7 red cases; G-b; F-2r.

C4 untouched against HEAD and against `2491336e` (`08-diff-stat-and-c4-surfaces.txt`). C5 holds: no schema field,
no outcome class (both refusals are the existing exit-5 JOURNAL UNREADABLE), no fsync, no recovery entry point.

## MF-8 (T-01, med): fstat the opened journal descriptor

**Red** (`01-red-unit-journal-at-13500626.txt`; production byte-identical to HEAD; 6/165 checks FAIL). The new
`case_fifo_swapped_after_lstat_refuses` renames a FIFO already holding a well-formed J1 record over the regular
journal at the open of the read under `plan.yaml.lock`, i.e. after every `lstat` `_require_regular` made. The seam
is `patch.object(os, "open", …)`, firing on the nth open of the journal path (1st for `recover_journals(plan)`,
which never reads in discovery; 2nd for `locked_update(feature.json)`, whose lock-free discovery reads once
first). At HEAD both routes replayed: `('ok', True)` / `('ok', None)`, both members at their after images, the FIFO
removed and its record consumed (0 bytes left).

**Green** (`02-green-unit-journal.txt`, 165/165). `_journal_bytes` opens `O_RDONLY|O_NOFOLLOW|O_NONBLOCK`, then
`_regular_fd_bytes` fstats the descriptor and reads only when `S_ISREG`; otherwise it returns None and
`_journal_bytes` raises the existing `JOURNAL UNREADABLE … is not a regular file once opened (replaced after it was
examined)`, exit 5, naming the journal. The descriptor is always closed. Asserted per route: the swap happened,
code 5 naming JOURNAL UNREADABLE and the journal, both members untouched, the FIFO still at the journal name, and
its buffered record still unread (the test's own reader gets back every byte).

### One-pass audit: every open/read/rename/unlink of a journal or member path in the journal and recovery path

"Same class" = a verdict taken on a pathname (type or identity) that the later use relies on, while the use acts
on whatever object the name then holds.

| # | Site | Operation | Race of the MF-8 class? | Action |
|---|---|---|---|---|
| 1 | `_journals_naming` | `os.listdir` of the directory | No. The listing is a hint; nothing acts on it until the entry is re-read under its primary's lock. A vanished entry is `FileNotFoundError`, so False. | none |
| 2 | `_journal_names` | the canonical-name short-circuit (`entry == name + JOURNAL_SUFFIX`) | No. It does not open anything; it only says "fail closed: this names you". | none |
| 3 | `_journal_names` → `_read_journal` → `_journal_bytes` | lock-free discovery read: `lstat`, then open, then read | **Yes**: the same lstat→open window as MF-8. A swapped FIFO's record was read (and drained) in discovery. | **fixed** by the same fstat (one function). A refusal here is the fail-closed True, so the caller then refuses at #4/#5. |
| 4 | `_recover_journal` | pre-lock `_require_regular` (`lstat`) and the name check | No use follows on this verdict: it only gates the refusal before any lock. Regular→non-regular after it is caught by #5; non-regular→regular after it refuses anyway (fail closed). | none |
| 5 | `_recover_journal` → `_read_journal` → `_journal_bytes` under `plan.yaml.lock` | `lstat`, open, read | **Yes, this is MF-8.** A symlink swapped in already failed the `O_NOFOLLOW` open (ELOOP → UNREADABLE). A directory failed only at `fdopen` (`IsADirectoryError` → UNREADABLE). A FIFO was read and replayed. A character device such as `/dev/zero` would have been read without bound. | **fixed**: fstat before the first byte; FIFO, directory, device and socket now share the one refusal. |
| 6 | `_journal_bytes` | read from the opened descriptor | No: after the fstat the descriptor is pinned, so a later rename of the name cannot change what is read. A *regular* file swapped in before the open is a different generation, read and validated (schema, pair, sha256s against both members' current bytes); acting on the generation read under the lock is the design. Only a non-cooperative actor can do that swap, and that actor could write the pair directly (security A1, not gating). | none (residual, stated) |
| 7 | `_replay_targets` → `_read_base(member)`; also `locked_update`/`locked_pair_update` bases | `os.path.exists`, then `open(path, "rb")`, read | Not this class: there is no type or identity verdict for the use to rely on. Whatever object is read is hashed and judged against the recorded before/after states. A member vanishing between `exists` and `open` raises `FileNotFoundError` before any write (loud, nothing written). Cooperative writers only rename members while holding the locks recovery holds. | none. Residual, pre-existing since FEAT-32 and outside the journal: a member that *is* a FIFO blocks this `open`, and every plain `locked_update` of that file at base blocks the same way. Fixing that changes the shared plain-write read (DEC-199), so I am reporting it as an advisory, not adding it to this round. |
| 8 | `_replay`, `_commit_published` → `replace_bytes(member)` | `mkstemp` in the directory, `os.replace` onto the member name | No: there is no check before the use. A rename replaces the entry atomically, whatever it is; a directory at the name raises `IsADirectoryError` → `JournalPending` (existing). | none |
| 9 | `_replay` | `os.unlink(journal_path)` after the replay, under both locks | Pathname-only, after a read under the primary lock. Every cooperative journal writer holds `plan.yaml.lock` for the journal's whole life, so only a non-cooperative actor can swap the entry in between; the unlink then removes that entry (never a symlink's target), and no member write follows it. POSIX has no unlink-by-descriptor, so an inode compare would only narrow the window, not close it. | none (residual; security A2's "between checking, replay and unlink") |
| 10 | `_publish_journal` | `os.replace(tmp, journal_path)` | No check-then-use: the "no journal" check (`_journals_naming` under both locks) is followed by a rename that replaces whatever is there. A directory at the name raises before any member write: nothing written, temp removed. | none |
| 11 | `_commit_published` | `os.unlink(journal_path)` of the journal this call published under both locks | As #9, with the journal this call itself published. | none |
| 12 | `_commit_published` | `os.open(directory)` for the fsync | Not a journal or member path. | none |
| 13 | `acquire` | lock-file opens | Not a journal or member path (lock files, outside this audit). | none |

Fixed in this round: #3 and #5, by the one fstat. Residuals stated, not fixed: #6, #7 (member FIFO, pre-existing),
#9 and #11.

## MF-7 (T-02, high): nothing written after the commit may turn it into a traceback

**Red** (`03-red-integration-plan-merge-mf7.txt`; `plan_merge/` byte-identical to HEAD; `harness_merge.py` then
carried only the MF-8 fix, which no 2488/k or 2488/l check reaches; 6 FAIL):

- `2488/k`: `sys.stderr` is a real closed stream (`open(os.devnull)` then `close()`), and
  `harness_boundary.changed_state_feedback` returns one row, so the real relay prints. `write_plan_and_ledger`
  raised `ValueError('I/O operation on closed file.')` after the commit, and `guards._locked_plan_update` (an
  unledgered amend's commit) raised the same. Both writes had landed.
- `2488/l/record-amendments` and `2488/l/amend`: the CLI's stdout is a pipe whose reader is closed. Each exited 1
  with a `BrokenPipeError` traceback from the AMENDED print, the amendment already landed once with no journal.

**Green** (`04-green-integration-plan-merge.txt`, 0 FAIL). Asserted: `write_plan_and_ledger` and
`_locked_plan_update` return normally on a closed stderr, with the amendment ledgered exactly once and no journal,
and the plain write landed. Receipts to a closed stdout, with stderr closed too, return normally. The broken-pipe
CLI exits 0 with no Traceback, the amendment is landed once with no journal, and stderr says the write landed.

The receipts check inside 2488/k (`_print_receipts` on a closed stdout) was added after the fix. It cannot be red
at HEAD because the helper did not exist then. Its discriminating sibling for the same `print` sites is 2488/l,
which was red first.

**The contract, as signed (T-02 item 2) and as now true:**

- On a closed or broken stderr after the commit: exit **0**. stdout is exactly the receipts (`AMENDED …` then
  `APPLIED <plan>` and, when ledgered, `APPLIED <feature.json>`). The feedback and its fallback line are lost
  silently.
- On a stdout that cannot take the receipts: exit **0**, receipts lost, and one best-effort stderr line:
  `plan-merge: the write landed, but its receipts could not be printed: <type>: <exc>`.
- On a normal stdout, stdout is byte-identical to before: the SC-04 lock `2488/g` is green.

### One-pass audit: every stdout/stderr write after a commit in amendments.py, amend.py and guards.py

| # | Site | Stream | Could it raise after the commit before this round? | Now |
|---|---|---|---|---|
| 1 | `_relay_after_commit` → `harness_boundary.relay_changed_state_feedback` (header and rows) | stderr | yes: OSError or ValueError | caught as `(OSError, ValueError)` (already true at HEAD) |
| 2 | `_relay_after_commit`, the fallback line | stderr | **yes: ValueError escaped (MF-7)** | suppresses `(OSError, ValueError)` |
| 3 | `guards._locked_plan_update` → `relay_changed_state_feedback` (an unledgered amend's commit; also every other `_locked_plan_update` verb) | stderr | **yes: unguarded** | routed through `_relay_after_commit` |
| 4 | `cmd_record_amendments`: `AMENDED …` × n, `APPLIED <plan>`, `APPLIED <feature.json>` | stdout | **yes: BrokenPipeError/ValueError traceback (measured)** | `_print_receipts` (prints, flushes, suppresses both, one best-effort stderr line) |
| 5 | `cmd_amend`: `AMENDED …`, `APPLIED <plan>`, `APPLIED <ledger>` | stdout | **yes (measured)** | `_print_receipts` |
| 6 | `_print_receipts`, its stderr line | stderr | n/a (new) | suppresses `(OSError, ValueError)` |
| 7 | `sys.exit(0)` and the interpreter's exit-time flush of stdout | stdout | after an EPIPE, a still-buffered stdout would print "Exception ignored" and exit 120 | measured: the broken-pipe runs exit 0 with no such line, because `_print_receipts` flushes inside its own try |

Writes reviewed and **not** in this class, because none of them follows a commit this invocation reports:

- `_die` and `_resolve_plan`'s refusal prints. They report a refusal, and nothing this invocation wrote has landed
  when they run. A preflight recovery can complete an *earlier* journal first; that transaction's completion is not
  reported by this verb, and the refusal that follows is this verb's own outcome. A closed stderr there loses the
  refusal text, as it does for every refusal in plan-merge.
- `_legal_stations`, `_refuse_illegal_station`, `_amend_show` (`--show` writes nothing) and the amend preflight's
  `sys.stderr.write`. All of them run before any write.

Both helpers are tuple catches of the boundary's real classes, so the FEAT-63 census (ceiling 0) is unaffected:
structure-locks is green inside the full integration kind.

## Test-only advisories

All three were green at HEAD on their first run (`03-…`). They are assertion-only, as the digest classed them:

- **G-b**: `case_2488_a_feature_json_write_completes_the_pair_first` now runs `feature_json_write.write_feature_json`
  from torn (a) `2488/e`, (b) `2488/e/b` (ledger landed, plan not) and (c) `2488/e/c` (both landed, journal
  left). Each asserts the write returns, `cycles_used == 1`, the amendment ledgered exactly once, and no journal.
- **pm F-2r**: each of those three is followed by `_settles`. A further record-amendments re-run exits 6 saying
  `recorded before` and leaves both files byte-identical (`2488/e/d`, `2488/e/b/d`, `2488/e/c/d`).
- **The four probe-only hostile shapes**, now unit cases:
  - a directory journal through `locked_update(plan)`, `locked_update(feature.json)`, `recover_journals(plan)` and
    `recover_journals(feature.json)` (`NON_REGULAR`, bounded subprocess probe);
  - a dangling symlink through `locked_update(feature.json)` (`NON_REGULAR`);
  - a missing `before_sha256` key through `locked_update(feature.json)` with the ledger absent
    (`case_missing_before_key_refuses`; not recreated);
  - a feature.json-primary journal through `locked_update(plan)` (`REVERSED_ROUTES`, which also asserts no lock is
    taken).

## Verification (working tree, after the last edit)

- `06-full-unit-kind.txt`: `run-unit-tests.py --kind unit`, 68 files, exit 0. Its `FAIL BUG-1290 5…` lines are
  `test-factory-claim-mutation.py`'s expected mutant proof; that file PASSes.
- `07-full-integration-kind.txt`: `run-unit-tests.py --kind integration`, 95 files, exit 0, including
  `test-checker-structure-locks.py` and `test-plan-merge.py`. `node_modules/.bin/tsc` was present, so no
  `bun install` was needed.
- `09-verify-T-01.txt` and `09-verify-T-02.txt`: each task's literal `verify:` from plan.yaml, exit 0.
- `10-canonical-reader-audit.txt`: `0 unresolved reader site(s) across 101 Python file(s)`, exit 0.
- `05-code-grade-paths-working-tree.txt`: `code-grade.py` in PATHS mode on the four production files (working tree;
  no commit, no clone). Every function this round changed or added passes its bar: `_regular_fd_bytes` 5/4,
  `_journal_bytes` 4/4, `_require_regular` 5/4, `_relay_after_commit` 5/4, `_print_receipts` 5/4,
  `_locked_plan_update` 5/4, `write_plan_and_ledger` 5/4, `cmd_record_amendments` 4/4, `cmd_amend` 4/4. The run
  exits 1 on a single record, `harness_merge._acquire_flock`, grade 3 against bar 4. That function's AST is
  identical at `2491336e` and in the working tree, so the gate's diff mode does not grade it: paths mode grades
  whole files. I did not reproduce diff mode, because it needs a commit. **Main grades the pin in diff mode.**
- `08-diff-stat-and-c4-surfaces.txt`: the six files above changed against HEAD, and C4 is empty against both
  HEAD and `2491336e`.

## Drafted wording for Main

### T-01 amendment, replacement for deviation (4)

> (4) Item 4, under MF-3 and validate c1 MF-8: the journal is read only from a regular file. The entry is lstat'd
> first, without following it, and a symlink (dangling or not), a FIFO or a directory at the name is UNREADABLE
> naming the journal. It is never opened, so a dangling entry no longer reads as absent and spins locked_update.
> The entry is then opened O_NOFOLLOW|O_NONBLOCK, and the opened descriptor is fstat'd before any byte is read. An
> entry swapped in after the lstat is refused there with the same UNREADABLE refusal, naming the journal. A
> symlink fails the open; a FIFO, even one already holding a record, opens without blocking and is refused unread
> and left in place; a directory or device is refused the same way.

### T-02, an optional further deviation (Main's call whether it is ledgered)

T-02 item 2 names the relay call and its OSError-only fallback in amendments.py. Item 5 says amend's stdout is
unchanged. Both still hold in substance. If Main ledgers the c2 shape:

> (7) Validate c1 MF-7 and its post-commit write audit: the relay's fallback line suppresses (OSError, ValueError),
> not OSError only. The helper is now guards._relay_after_commit, which write_plan_and_ledger and
> _locked_plan_update share, so an unledgered amend's commit has the same advisory relay. The AMENDED/APPLIED
> receipts of amend and record-amendments go through guards._print_receipts, which prints, flushes and, if stdout
> cannot take them (closed: ValueError; broken pipe: OSError), prints one best-effort stderr line saying the write
> landed. The verb still exits 0, and a normal stdout is byte-identical (SC-04 lock green). No write after a commit
> can turn a landed amendment into a traceback.

## Disclosures

- The MF-7 red ran with harness_merge.py already carrying the MF-8 fix: the order was MF-8, then MF-7, as the
  digest prescribed. No 2488/k or 2488/l check reaches `_journal_bytes`.
- `_relay_after_commit` and `_print_receipts` share one shape: try, print, suppress the fallback. I kept them as two
  small helpers, not one parameterised helper, because their streams and messages differ.
- `_locked_plan_update`'s change also reaches apply, add-tasks, delete-items, set-*, record-panel and
  sign-approval's plan write. A failed feedback print there is now a note instead of a traceback after the write
  landed; nothing else changes for those verbs. union.py itself is untouched.
- Advisory for the backlog, not built: a member path that is a FIFO blocks `_read_base` (audit row 7). This is
  pre-existing and shared with every plain `locked_update`.
