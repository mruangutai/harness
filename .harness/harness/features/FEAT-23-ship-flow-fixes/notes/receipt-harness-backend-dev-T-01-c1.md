# Receipt — harness-backend-dev — T-01 (FEAT-23) — resumed spawn c1

## Context

This is a contract re-prompt. The prior spawn (c0) died on an API connection error immediately
after printing "All 103 cases pass, 0 failures. Now write the receipt." Its edits are on disk and
untouched by this spawn — this run only re-verifies, gathers evidence, and writes the receipt +
digest that c0 never produced.

## Red run (pre-edit)

**I did not run the red suite myself.** I have no transcript access to the dead c0 spawn and no
artifact on disk (log file, saved output) that captures its red run. I am not reconstructing or
inferring a red-run line — c0 reported "All 103 cases pass, 0 failures" as its last output before
dying, which is consistent with edits having already landed and the suite already being green at
that point, but that is not a red-run report and I am not presenting it as one. This spawn's own
verification starts from the green state already on disk.

## Green run (this spawn, post-edit)

Invocation:
```
python3 .claude/skills/harness/bin/test-gh-sync.py
```
Final lines of output:
```
ok    abandon records feature.json status Abandoned
ok    ship leaves every other top-level key unchanged
ok    abandon leaves every other top-level key unchanged

ALL PASSED
```
`grep -c "^ok"` → 103. `grep -c "^FAIL"` → 0. Exit code 0.

## Task verify (T-01, verbatim from plan.yaml)

Invocation form used:
```
python3 -c "
import yaml
p=yaml.safe_load(open('.harness/harness/features/FEAT-23-ship-flow-fixes/plan.yaml'))
print([t for t in p['tasks'] if t['id']=='T-01'][0]['verify'])" | bash
```
Full output and final line:
```
T-01 GREEN
```
Exit code 0.

## Status-write placement relative to early exits

- `cmd_abandon` (`gh-sync.py:637-682`): early exit at `:647-648` (`if rec["milestone"] is None
  and not rec["issues"]: skip(...)`) is a **conjunction** of the milestone check and the issues
  check — not a bare milestone check. `_record_status(feat_dir, "Abandoned")` is the last
  statement of the function, at `:682`, after every close (`issue comment`, per-issue closes,
  milestone close, parent close-or-leave-open per D-01) has run.
- `cmd_ship` (`gh-sync.py:707-744`): early exit at `:717-718` (`if rec["milestone"] is None:
  skip(...)`) is a single milestone check — `skip()` calls `sys.exit(0)`, so reaching the status
  write proves no early exit fired. `_record_status(feat_dir, "Done")` is the last statement of
  the function, at `:744`, after the parent comment, parent close-or-leave-open (D-01), and the
  milestone close.
- Confirmed: neither status write is gated on a milestone test as a standalone condition —
  `cmd_abandon`'s early-exit guard is a conjunction (milestone AND issues), and `cmd_ship`'s single
  milestone guard is the ordinary "nothing to close" skip, not a re-gate placed in front of the
  status write itself. Both writes sit strictly after all GitHub-side closes complete.

## Atomic-write helper

`_atomic_write(path, text)` at `gh-sync.py:418-442`. Creates a tempfile via `tempfile.mkstemp` in
the **same directory** as `path`, writes `text`, flushes, `os.fsync`s, then `os.replace`s onto
`path`; on any exception it unlinks the tempfile and re-raises.

Call sites — **two, not three**:
1. `_record_status` (`gh-sync.py:465`) — the status-only write used by `cmd_ship`/`cmd_abandon`.
2. `save_recorded` (`gh-sync.py:500`) — the pre-existing `github:` key read-modify-write, now
   routed through the shared helper instead of its own inline atomic-write logic.

I could not find a third call site (`grep -n "_atomic_write(" gh-sync.py` returns exactly these
two lines plus the definition). Flagging the discrepancy against the dispatch's "three call sites"
rather than inventing one.

## Fixture — all eight schema-required keys + github block

`_full_fixture` (`test-gh-sync.py:1255-1268`) calls `write_feature_json` with all eight
feature-schema.json required keys — `feature_id`, `branch`, `pr`, `status`, `review_sha`,
`cycles_used`, `max_total_cycles`, `runs` — plus a `github` block whose `attached` key is
`["T-01"]`, a list of strings. Confirmed by direct read of `test-gh-sync.py:1255-1268`.

## Prose sites corrected

- `gh-sync.py` (diff against HEAD): two docstring sites removed, both reading `... "feature.json"
  is untouched"` — one in `cmd_abandon`'s docstring, one in `cmd_ship`'s docstring (pre-edit these
  claimed the status write does not happen; both are now replaced by the "LAST STATEMENT of the
  successful path" prose quoted above, at `gh-sync.py:641-644` and `:711-713`).
- `test-gh-sync.py` (diff against HEAD): one comment removed — `"and cmd_abandon must write no
  receipt so the absent line is never back-filled"` — confirmed absent by
  `grep -n "must write no receipt" test-gh-sync.py` (zero hits).
- Confirmed separately (per dispatch, already verified by the lead): zero occurrences of "feature.json
  is untouched" remain anywhere in `gh-sync.py` — `grep -n "untouched" gh-sync.py test-gh-sync.py`
  now returns only one unrelated hit, `test-gh-sync.py:896` ("(eleven-key) every non-github key
  survives untouched"), which is a different, correct claim about `save_recorded`, not the status
  write.

## files_touched

- `.claude/skills/harness/bin/gh-sync.py`
- `.claude/skills/harness/bin/test-gh-sync.py`

Both are `git diff --stat`-confirmed modified, no other files touched by this spawn: no `git add`,
no commit, no `gh` writes, tree left dirty.
