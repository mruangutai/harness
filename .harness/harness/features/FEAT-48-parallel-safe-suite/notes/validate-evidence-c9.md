# Orchestrator measurements — FEAT-48 revalidation at `review_sha 27f8105b`

**Conclusion first: every c8 must_fix is closed with a discriminating proof, and the three code
files behind them were re-measured at the pin, not inherited.** One new finding stands, and it is
not a product defect: T-06's own `verify:` block returns 1 at the pin on a uniqueness clause its
carrier note has never satisfied. Detail at the end.

All figures below were taken by me in
`/Users/…/.claude/worktrees/harness/FEAT-48-parallel-safe-suite` at HEAD `de0b0d31`, whose only
delta from `27f8105b` is `feature.json`'s own `review_sha` line
(`git diff --stat 27f8105b de0b0d31` = 1 file, 1 insertion). Every run used
`env -u HARNESS_AGENT_TYPE`. `git status --porcelain` was empty before and after every probe;
no probe wrote inside the checkout.

## 1. `code_grade` — the c8 blocking gate is clean

`python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head 27f8105b` →
**exit 0, `PASSING: 70`, zero blocking records.** The three c8 `high` records are gone at source:
`run_self_tests` is now CYC 3 / COG 0 / ABC 6.5 (`test-suite-independence.py:277`) against c8's
14 / 29 / 49.7, `snapshot` is 2 / 1 / 4.6 with the walk body extracted to `_snapshot_directory`
(5 / 7 / 8.8), and `run_pool.py main` is 5 / 4 / 17.5. Nothing sits at or below its bar.

## 2. The lstat race guard — closed, and proven reachable

`_record` (`run_pool.py:29-34`) wraps `os.lstat` in `except OSError: return`, and **both** the
directory-symlink branch and the file branch of `_snapshot_directory` now go through it, which is
the asymmetry c8 reported. Probe `/tmp/feat48_probe_pool.py` (fault injection scoped to the `os`
that `run_pool`'s own globals resolve, so `os.path.islink` and `os.walk` keep the real
implementation — a globally patched `os.lstat` silently makes `islink` return False and measures
the wrong branch):

- `snapshot()` survives an injected `FileNotFoundError` in **both** branches, and drops exactly
  the raced entry — `set(base) - set(after) == {victim}`, nothing else lost.
- **Reachability:** with `_record`'s guard replaced by an unguarded body, the *same* injection
  escapes `snapshot()` in **both** branches. The guard is live code, not decoration.
- Baseline behaviour unchanged: a directory symlink is recorded and **not descended**, a dangling
  symlink is recorded, plain files are recorded.

15/15 probe assertions pass, exit 0.

## 3. `__pycache__` versus a loose `.pyc` — now exactly what SC-10 licenses

Through the real CLI, `run_pool.py --mutation-check <watched>`:

| case | result |
|---|---|
| clean run | exit 0, no `MUTATED` |
| `__pycache__/x.pyc` **rewritten** *and* `__pycache__/new.pyc` **created** | exit 0, no `MUTATED` |
| `loose.pyc` created outside `__pycache__` | **exit 1, `MUTATED loose.pyc`** |
| watched dir missing | exit 2 |
| watched dir empty | exit 2 |

The skip is now keyed on the `__pycache__` directory name (`run_pool.py:39-40`), not on the `.pyc`
suffix, so the over-wide skip c8 flagged is gone. `test-run-pool.py:145 case_cache_exclusion`
asserts both legs — the missing `__pycache__` leg (c8 M4) is closed.

## 4. The six in-file self-tests — all six run in CI and all six DISCRIMINATE

`test-suite-independence.py` was rewritten wholesale in `993ac997`, so c8's discrimination proof
did not carry and I re-took it at the pin. Probe `/tmp/feat48_probe_discriminate.py` monkeypatches
one collaborator at a time; nothing in the checkout is edited.

| self-test | reddened by |
|---|---|
| `0-injection idiom` | blinded `scan_file` |
| `1-mutant beside original` | blinded `scan_file` |
| `2-pid named mutant` | blinded `scan_file` |
| `clean controls` | over-eager `scan_file` |
| `live tree, independent root and discovered floor` | over-eager `scan_file` |
| `unresolved root refuses` | `resolve_scan_root` patched never to refuse |

**Cases that can never turn red: none.** Baseline is green with zero failures.
`main()` calls `run_self_tests()` before the scan (`:288`) and returns 1 on any self-failure
(`:295-297`), so CI gates all six. The clean control now carries the `src.replace(...)` shape
(`_clean_fixture_failure`, `:221-235`) that c8 recorded as missing.

## 5. SC-03 — both halves, measured

T-03's `verify:` block, run verbatim (`/tmp/feat48_t03_verify.py`): **exit 0.**

- CI half: live run exit 0, `root` printed and equal to `git rev-parse --show-toplevel`,
  `discovered 63` (floor 50), zero live findings, and no self-comparison shortcut (`selfcmp []`).
- Review-time pinned half: the three `ea6f51f` blobs are scanned in a throwaway directory and
  **all ten named sites are found individually, with zero extras** — `test-check-domain.py:1482`,
  `:1489`; `test-check-state.py:2112`, `:2114`, `:2133`, `:2248`, `:2250`, `:2269`;
  `test-feature-worktree.py:584`, `:605`. `missing []  extra []`. That scan exits 1, as the
  criterion requires of a violating tree.

Vendoring those blobs as committed fixtures is recorded as `BRIEF.md` **BACKLOG-C**, not built.

## 6. Suite, contract and the remaining criteria

- `run-unit-tests.sh --kind all`: **exit 0, 63 files, 8 workers, 48.29s wall, zero `FAIL`, zero
  `MUTATED`**, tree clean before and after. (Under 120s; the ten recorded runs sit 42.64–47.82s.)
- `--kind unit`: exit 0, 33 files, 12.15s, zero `FAIL`, emits `PASS test-suite-independence.py`
  (SC-04).
- `--check-kinds`: exit 0, agreement line, **zero** `PASS`/`FAIL` lines. `--kind nope`: exit 2
  (SC-07).
- SC-01: `test-check-domain.py` exit 0 and the live `feature_schema.py` is unchanged at
  `st_mtime_ns 1788333510516825193`, size `15881`, sha256 `943ef7a7…fbb2` — identical before and
  after, so never written rather than written-and-restored. The crashing-schema case still asserts
  `returncode == 2` **and** `"CRASHED" in stderr` (`test-check-domain.py:1459-1465`), which is the
  clause SC-01's FAILS IF names.
- SC-09: `gen-decisions-index.py --stdout` is **byte-identical** to the committed
  `DECISIONS-INDEX.md` (`cmp` clean).
- DEC-211's boundary is corrected at `993ac997`: it now claims a content-derived write inside bin
  is caught **only** when it changes an entry's mode, size or observed nanosecond mtime, and states
  the same-size mtime-restoring rewrite as out of coverage with content hashing deferred. That
  matches `_record`'s `(st_mode, st_size, st_mtime_ns)` tuple exactly. The c8 overclaim (M5) is
  closed as a documentation correction, not a code change.

## 7. The one open finding — T-06's `verify:` block fails at the pin

`/tmp/feat48_t06_verify.py` is T-06's declared verify block, run verbatim: **exit 1.** Every
substantive clause passes — one `run_pool.py` invocation carrying the literal
`--mutation-check "$BIN_DIR"`, no serial `"${SCRIPTS[@]}"` loop, `--check-kinds` exit 0 with no
test lines, unknown kind exit 2, ten `run N exit 0` lines all zero, `control method: isolated bin
copy`, `control broken reads 4968` (> 0), `pool:` wall `42.40` (≤ 120), one `tree condition:` line,
and `PASS test-suite-independence.py` present.

The failing clause is `post == ["0"]` — an **exactly-one-occurrence** assertion on
`post-fix broken reads 0`. The carrier note states that line twice: once inside the fenced verbatim
block the task's own intent mandates, once as the summary line the verify parses. `findall` sees
both, so the list is `['0','0']`.

**This is a verify-block defect, not a delivery defect, and it is pre-existing rather than
introduced by the refresh.** The duplicate has been present since the note was created at
`b86ce66a`; `27f8105b` only replaced the numbers. No success criterion fails on it: SC-02, SC-05
and SC-06 are `verify: inspection` and their content is present and in range. T-06 nonetheless
carries `status: done` behind a verify that has never returned 0.

## 8. Record hygiene, for the main session

`993ac997` amended `BRIEF.md`'s SC-03 and added BACKLOG-C. The BRIEF's `## Approval` block is
byte-identical across `b86ce66a`, `e64e863e` and `993ac997` — `approved / Mike Ruangutai /
2026-09-02` — so the amendment carries no distinct re-signature act in the record. The operator
ruling authorising it exists outside the file; only the operator's hand can date the block.

## Pointers

- probes: `/tmp/feat48_probe_pool.py`, `/tmp/feat48_probe_discriminate.py`,
  `/tmp/feat48_t03_verify.py`, `/tmp/feat48_t06_verify.py`, `/tmp/feat48_sc_evidence.sh`
- suite log: `/tmp/feat48_all.log` (invariant output at its `test-suite-independence.py` block)
- carrier note: `notes/measurements-parallel-suite.md` at `27f8105b`
