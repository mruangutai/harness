# Receipt — harness-backend-dev — T-04 (FEAT-26) — run t04-eng

## BLUF
`closes` is implemented and verified: T-04's verify prints `VERIFY-OK` literally. MF-1
(uncaught `int(pr_arg)`) is fixed at the `main()` parse boundary with a test. MF-2 and
MF-3 (false docstrings) are corrected — MF-3 flagged as my addition, not the plan's. The
discriminating mutant at `gh-sync.py:586` reddened exactly as specified (`pr == 15`) and
the suite is confirmed green again after revert. All edits to the shared file pair are
additive; T-02/T-03 cases stay green (120/120 `ok`, `ALL PASSED`).

## 1. T-04 verify — literal output
Command run verbatim from the dispatch, in the worktree:
```
out=$(python3 .claude/skills/harness/bin/test-gh-sync.py 2>&1) || { printf '%s\n' "$out"; exit 1; }
... (four grep -q checks, then grep -q 'ALL PASSED') ...
echo VERIFY-OK
```
Output: `VERIFY-OK` (confirmed on a clean, non-mutated tree — see §3 for why one earlier
run of this same command overlapped a mutation window and is disregarded as evidence).

Cross-checked against `plan.yaml`'s own T-04 `verify:` — identical, byte for byte, to
the string given in the dispatch.

## 2. MF-1 — `--pr abc` no longer a traceback
Fixed in `main()`, beside the other flag checks (not in `_record_pr`, so its never-die
contract for `cmd_ship` stays intact):
```python
try:
    int(pr_arg)
except ValueError:
    die(f"--pr needs an integer, got {pr_arg!r}")
```
Manual repro after the fix:
```
$ gh-sync.py record-pr <dir> --pr abc
gh-sync: ERROR — --pr needs an integer, got 'abc'
rc=1
```
No `Traceback (most recent call last)` in stdout+stderr. New case `record-pr --pr abc
exits non-zero with no traceback` asserts exactly this (rc != 0, no traceback string,
`--pr` present in the combined output) — `ok` in every run since the fix landed.

## 3. The discriminating mutant (gh-sync.py:586, `if len(found) > 1:`)
- **Mutation applied**, read back from disk before running:
  `if False:  # MUTANT (T-04 discriminating check): drop the >1 guard` — sed -n
  confirmed the exact line was in place.
- **Suite actually ran**: 120 cases executed; run output (task `bkv20kaqo`) shows 119
  `ok` lines plus exactly one `FAIL`, ending `1 FAILED`.
- **Case 3 reddened with `pr == 15`**, verbatim from that run:
  ```
  FAIL  record-pr leaves pr null when the branch has two merged PRs
        rc=0 pr=15
  ```
- **Reverted** (`if len(found) > 1:` restored, read back and confirmed), then re-run
  clean: 120/120 `ok`, `ALL PASSED`, `exit=0` (task `by82r5szr`, log `/tmp/final_green.log`).

Caveat for the record: one intermediate verify run (`bh44wyd2y`) and one intermediate
"clean" rerun (`bkv20kaqo`) overlapped my apply/revert edits because subprocess-per-case
execution reads gh-sync.py fresh from disk on every invocation and a background run in
flight is not isolated from a concurrent edit. `bkv20kaqo`'s FAIL is the mutant signature
above and is used as evidence; `bh44wyd2y`'s VERIFY-OK is corroborated by the strictly-
clean `final_green.log` run that followed the revert with no further edits, so it is not
relied on alone. Lesson: never edit the shared file pair while a background test run
against it is in flight, even after starting a "revert" — wait for the run to fully
finish first. (Filed as an observation, not expertise.)

## 4. Post-edit counts — floor, not equality
| file | `grep -c source_issues` (LINES) | `grep -o source_issues \| wc -l` (occurrences) |
|---|---|---|
| `gh-sync.py` | 13 (baseline 12) | 15 (baseline 14) |
| `test-gh-sync.py` | 32 (baseline 25) | 33 (baseline 26) |

Both files are >= baseline on both expressions; every pre-existing occurrence is
untouched (confirmed by the full green suite, including every T-02/T-03 case named in
the dispatch).

## 5. `test-gh-sync.py:1308`-class assertion — stayed green
The case `ship leaves every other top-level key unchanged` (quantifies over every key
except `status`, so it transitively includes `pr`) is `ok` in every run after my edits.
I did not touch `_record_pr`'s body at all — only `main()`'s flag-parse boundary and the
module/`save_recorded` docstrings — so this was never at risk, and the full-suite run
confirms it directly rather than by inspection alone.

## 6. `load_recorded` stdout purity
`load_recorded` never prints to stdout on any path. Its three error branches all
`raise SystemExit(<string>)`; uncaught, Python's default handling for a string
`SystemExit` argument prints that string to **stderr** and exits 1 — verified directly:
```
$ python3 -c "raise SystemExit('boom')" 1>out 2>err; cat out; cat err
(out empty)
boom
```
So `cmd_closes` calls `load_recorded(feat_dir)` directly, with no wrapping needed to
hold stdout purity — the only production code in `cmd_closes` is the `for` loop printing
`Closes #<n>`. A second purity risk existed one level up: `main()` calls `load_config()`
unconditionally before dispatch, and `load_config` itself prints to stdout on two paths
(the "no github.board configured" note, and every `skip()` call). I dispatch `closes`
**before** the root-climb/`load_config` call in `main()` — `cmd_closes(feat_dir)` runs and
`main()` returns, so `load_config` is never invoked on this path at all. This is also
why `closes` needs no `repo`/`board` argument, matching the intent's own reasoning.

## 7. Fake gh's call log
Pre-existing. `FAKE_GH` already does
`echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"` and `run()` already sets
`env["FAKE_LOG"] = os.path.join(tmp, "calls.log")`; the `calls(tmp)` helper reads it back.
No fixture extension was needed — `closes makes no gh call at all` asserts `calls(tmp) ==
[]` against this existing log, strengthened to also assert the exact expected stdout
(`"Closes #9\n"`), which is what makes the case genuinely RED against unmodified
`gh-sync.py` (unmodified code hits `skip()` via `load_config`, which happens to also
leave the log empty and exit 0 — a vacuous pass on the log-only assertion alone).

## Files touched
- `.claude/skills/harness/bin/gh-sync.py` — `cmd_closes`, `main()` dispatch + `--pr` int
  guard, module docstring (MF-2), `save_recorded` docstring (MF-3, my addition)
- `.claude/skills/harness/bin/test-gh-sync.py` — 4 T-04 cases, 1 MF-1 case
- this receipt

## Open questions
- MF-3 (the `save_recorded` docstring fix) is my addition, not the plan's. Flagging per
  the dispatch's own instruction so it can be backed out cleanly if out of scope for T-04.
