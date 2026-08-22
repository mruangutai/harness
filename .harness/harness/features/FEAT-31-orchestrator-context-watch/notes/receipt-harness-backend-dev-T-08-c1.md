# Receipt — harness-backend-dev — T-08 — c1

## What now works

`context-watch.py`'s table-mode invocation (never `--resolve-dir`, never
`--warn-for`) now prints a three-line "blind spot" footer after the rows,
on every invocation including the no-orchestrators-found path:

1. **compaction** — the count of measured ROWS (not drop-events) whose
   D-11 measured set contains an entry sized lower than the one before
   it, plus the "not visible to it" / "understates the session" framing.
2. **retention** — `log_retention_days` as read from the same config path
   the run's threshold resolution already opened (`resolve_retention_days`,
   new; top-level key, never under `budgets`), and the age in whole days
   of the oldest jsonl transcript this run actually opened (`os.path.getmtime`),
   plus the "goes stale silently" framing.
3. **window** — the largest `peak` figure among this run's measured rows
   (reused from `_build_row`'s already-correct `peak`, since D-11 notes
   peak survives the defect below), plus the "not a model window limit"
   framing.

A 4th, unprefixed line ("unmeasured rows excluded from the figures
above: N") prints only when `N > 0` — it does not start with `blind
spot`, so it never inflates the exactly-3 count the verify block asserts.

## The `_build_row` defect (T-01/T-06 code) — how line 1 avoids it

Confirmed independently by reading `_build_row` (lines ~250-269): its own
`sizes` appends a spurious `0` for a parsed line with no `message.usage`,
`current` is the **last line of the file** rather than the last member
of the measured set, and `entries` counts every parsed line, not the
measured set's cardinality. None of this matches D-11. I did **not**
touch `_build_row` — it is T-01's code, `status: done`, and amending it
is not this task's to do (escalated separately per the dispatch).

Line 1 therefore never reads `_build_row`'s `sizes`/`current`/`entries`.
It rereads the same jsonl files independently
(`_orchestrator_jsonl_paths` + `_measured_sizes_for_jsonl`) and rebuilds
the measured set itself — a parsed line counts only when it carries a
dict `message.usage`, never a zero standing in for an absent one — then
counts drops over that clean set. Line 3 reuses `row["peak"]` because
the escalation note is right that peak survives the defect (a spurious
zero cannot raise a max). **This means `_build_row`'s own `current` and
`entries` fields (as displayed in the main table) remain wrong/inflated
relative to D-11, and are inconsistent with this footer's line 1, until
the `_build_row` fix lands** — stating this plainly per the dispatch's
instruction, not papering over it.

## TDD

Iron Law honored, but the RED test lives in scratchpad, not in the repo:
`test-context-watch.py` is explicitly **not** in this task's `files:`
list (dispatch says so directly), so no case was added there — writing
one would be an out-of-domain edit to a file this task does not own.

RED: wrote a throwaway probe at
`/private/tmp/claude-501/.../scratchpad/test_t08_red.py` (not committed,
not part of `files_touched`) invoking `context-watch.py` via subprocess —
(a) the no-orchestrators-found path, asserting exactly 3 `blind spot`
lines, all carrying a digit, and retention=30; (b) a fixture with a real
compaction (150000 -> 50000) PLUS a trailing entry with no
`message.usage` at all, asserting line 1 reports exactly 1 (not
inflated by the unmeasured line reading as a spurious drop-to-zero) and
line 3 reports the true peak 150000. Ran against the pre-edit tree: **5
of 6 checks failed** (genuine RED — `blind spot` did not exist yet).
Implemented the footer. Re-ran: **0 failures** (GREEN). The probe is
throwaway and left outside the repo; `git status --porcelain` for
`test-context-watch.py` is clean (I never touched it).

**Gap, as instructed to report rather than close**: no coverage for this
footer exists in the committed `test-context-watch.py` — the pre-existing
55 cases don't exercise it, and this task correctly does not add any.
Recommend a follow-up task (owned by whoever holds that file) add cases
for: the D-11 measured-set drop count (with an unmeasured-line fixture
proving no false inflation), the retention read/default fallback, the
peak-reuse for line 3, and the exactly-3/unprefixed-4th-line shape.

## Verify — both `test` lines, verbatim stdout and exit status, separately

### Command 1
```
test "$(python3 .claude/skills/harness/bin/context-watch.py --projects-dir /nonexistent-projects-dir | grep -cE '^blind spot')" = "3"
```
stdout of the piped command (what `test` compared against `"3"`): `3`
Exit status of the `test`: `0`

### Command 2
```
test "$(python3 .claude/skills/harness/bin/context-watch.py --projects-dir /nonexistent-projects-dir | grep -E '^blind spot' | grep -cE '[0-9]')" = "3"
```
stdout of the piped command (what `test` compared against `"3"`): `3`
Exit status of the `test`: `0`

## Before/after honesty check (dispatcher's item 1)

Before this change: `grep -c "blind spot" context-watch.py` → `0`, and
both verify lines printed `0` and exited `1` (measured directly, not
assumed) — confirmed genuinely red before, genuinely green after.

## Full raw output of the table-mode invocation used by verify

```
no orchestrators found under /nonexistent-projects-dir
blind spot 1 (compaction): 0 measured rows show a later entry sized lower than the one before it -- what a compaction drops BEFORE this tool looks is invisible to it, so a peak read after one understates the session.
blind spot 2 (retention): log_retention_days=30 as read from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-31/.harness/harness.json; the oldest transcript this run read is 0 day(s) old -- nothing older than that window exists to be read, and this figure goes stale SILENTLY, never erroring, once files roll past it.
blind spot 3 (window): the largest single prompt this run reported is 0 tokens -- the prompt size the API recorded, NOT a model window limit; this tool has no window limit to compare it against.
```
Exit status: `0`

## Full pre-existing suite still green

`python3 .claude/skills/harness/bin/test-context-watch.py` → `55 of 55
cases passed`, exit `0`. Confirmed the footer does not disturb T-16's
I3 (`--warn-for` stdout EMPTY on `None`) — the footer function is only
called from the table-mode branch of `main()`, never from `--warn-for`
or `--resolve-dir`, and no existing case counts exact line totals (they
all use `.count("WARNING")` substring counts), so the added lines cannot
break them. Verified by running the full suite, not by inspection alone.

## Honesty note on the verify block's own capability

Both `test` lines are capable of failing and were seen failing pre-change
(measured `0`/exit `1` above), so neither is vacuous. The verify block
asserts "exactly 3 lines, each with a digit" — it **cannot** distinguish
a correct line-1 figure from a wrong one (e.g. an inflated compaction
count), only that a numeral is present. I consider line 1's numeric
*correctness* — not just its presence — the least-covered claim here,
exactly as flagged in the dispatch; the scratchpad probe above is the
only thing that exercises it, and it is not preserved in the repo.

## Boundaries respected

- Only `.claude/skills/harness/bin/context-watch.py` was touched.
- `test-context-watch.py`, `.claude/settings.json`, and
  `run-unit-tests.sh` were not touched.
- `_build_row`'s signature, return shape, and behavior are unchanged
  (diffed mentally against the pre-edit read above; no edit was made to
  that function at all).
- T-06's threshold/headroom/warning behavior and T-16's `warn_for_agent`
  / `--warn-for` mode (including I3's empty-stdout-on-`None` case) are
  confirmed unchanged by the full 55/55 suite run above.

## Files touched

- `.claude/skills/harness/bin/context-watch.py`
