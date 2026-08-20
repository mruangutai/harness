# Receipt — harness-backend-dev — FEAT-29-graphql-budget — simplify pass, REUSE angle

## Verdict

One applicable finding. Read-only: nothing edited. `.harness/logs/gh-cost-2026-08-19.jsonl`
confirmed byte-identical (39504 bytes) before and after this pass — no live `gh` call made,
`check-state.sh` not run.

## Scope reviewed

`git diff bee6234..8c7d7bc` across `factory_gh.py`, `gh_board.py`, `gh_cost_log.py` (new),
`gh-sync.py`, `run-unit-tests.sh`, and the three test files
(`test-factory-gh.py`, `test-gh-board.py`, `test-gh-cost-log.py`). Checked for: constants/helpers
restated where an importable one exists; duplicated fake-`gh` test scaffolding across the three
test files; residue from superseded amendments (amendment 5 flipped the recorder default
mid-flight).

## Finding 1 — APPLICABLE

**File/line:** `.claude/skills/harness/bin/factory_gh.py:54-57` (`_iso_utc`) vs.
`.claude/skills/harness/bin/gh_cost_log.py:119` (inline in `record()`).

**Summary:** The UTC-timestamp-with-`Z`-suffix formatting (`datetime.fromtimestamp/now(...,
tz=utc).isoformat().replace("+00:00", "Z")`) is spelled twice in this diff — once factored into a
named helper `_iso_utc()` in `factory_gh.py` (used to format the GraphQL-budget reset time), once
inline, unfactored, in `gh_cost_log.record()` (used to format the log line's `ts` field). Both
spellings are new in this diff (T-03/T-04), not pre-existing code — this is same-cycle
duplication, not multi-cycle residue.

**Concrete cost:** two independent spellings of "format a UTC instant as ISO-8601 with a literal
`Z`" now have to be kept byte-identical by hand. A future change to the timestamp convention (e.g.
switching to `datetime.UTC` on a newer Python, or adding millisecond truncation) applied to one
site and not the other produces two different timestamp formats in the same tool's output with no
test catching the mismatch — neither file's suite compares the two formats against each other.

**Alternative:** `factory_gh.py` already does `import gh_cost_log` (one-way; `gh_cost_log.py`
does not import `factory_gh` — the module docstring at `gh_cost_log.py:29-31` calls this out
explicitly as the reason `_counter_binary()` re-reads `FACTORY_GH` independently rather than
importing `factory_gh`). That existing one-way edge means the shared helper's natural home is
`gh_cost_log.py`: add a small public function there (e.g. `iso_utc(epoch_seconds=None)`, defaulting
to "now" when called with no argument) and have both `record()`'s `ts` line and
`factory_gh._iso_utc`'s call site use it. No new import cycle — `factory_gh` already depends on
`gh_cost_log`.

**Disposition:** APPLICABLE — pure helper extraction, no assertion touched, no test-file edit
required (`_iso_utc` in `factory_gh.py` has no direct unit test asserting its literal
implementation, only the value it produces; moving the formatting logic changes no observable
behavior).

## Not flagged, and why

- The three test files' `check()`/`FAILURES`/`RAN` print-and-count harness is duplicated across
  essentially every `test-*.py` in this directory, this diff included — but that convention
  predates this diff (checked: identical shape in files this diff never touches, e.g.
  `test-factory-config.py`). Not this feature's residue.
- `test-gh-cost-log.py`'s `_counting_fake()` and `test-factory-gh.py`'s `recorder()`/`Result`
  are both "fake `subprocess.run` doubles queueing canned results," but they model genuinely
  different things — `recorder()` returns one queued `Result` per call regardless of argv shape;
  `_counting_fake()` branches on argv shape (counter call vs. real call) because it must drive
  the wrap sites' *two* subprocess calls per invocation. Collapsing them would cost more than it
  saves — judged a false positive, not a finding.
- `_RATE_LIMIT_MARKERS`/`_looks_like_rate_limit`/`_is_rate_limit_query` (`factory_gh.py`, new):
  grepped `check-state.sh` and the rest of `bin/` for any prior rate-limit-detection text or
  helper — none exists. Genuinely new, not a restatement.
- `gh_cost_log.py`'s `_MAX_ARG_LEN`/`_truncate`/`_sanitize_argv` (argv value truncation for log
  lines): grepped the whole `bin/` tree — no prior truncation helper of this shape exists to
  restate. Genuinely new.
- Did not re-derive B-2 (`gh_board.py:142`'s unreachable `or {}` guard) — out of this angle
  and already settled per dispatch.
- Did not touch `test-check-state.py` (DEC-174 carve-out) — no reuse finding was found there
  either; it was read only to confirm it was in scope-list, not analyzed for findings since this
  angle found nothing there worth flagging.

## Log integrity

`.harness/logs/gh-cost-2026-08-19.jsonl`: 39504 bytes before this pass (confirmed via `wc -c`
at read time) and 39504 bytes after (re-checked before writing this receipt) — unchanged. No
`HARNESS_GH_COST_LOG=1` set at any point. No `gh` invoked.

## Suite (baseline confirmation, no code touched)

This is a read-only review with no `T-NN` task and no `verify:` command of its own. As
confirmation nothing in the tree is broken while forming the finding above, ran the full unit
suite: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0, 18/18 scripts PASS,
including `test-gh-cost-log.py` at 35/35 checks. `.harness/logs/gh-cost-2026-08-19.jsonl` stayed
at 39504 bytes across the run (re-checked after).
