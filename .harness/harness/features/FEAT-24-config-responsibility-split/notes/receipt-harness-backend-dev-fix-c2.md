# FIX-C2 receipt — harness-backend-dev

## Primary fix — `file_at_ref` decodes line-wrapped base64

`.claude/skills/harness/bin/factory_gh.py:456` changed from

    decoded = base64.b64decode(raw, validate=True)

to

    decoded = base64.b64decode("".join(raw.split()), validate=True)

`validate=True` is kept, as required — `"not-valid-base64!!!"` still raises (existing case
`file_at_ref: undecodable content raises rather than returning empty` stayed green throughout).

### New test case (TDD, RED before GREEN)

`.claude/skills/harness/bin/test-factory-gh.py`, inserted between the existing "undecodable"
case and the existing "null"/absent-content case — a fifth, distinctly-named `file_at_ref` case:

    file_at_ref: decodes GitHub's line-wrapped base64 content

Fixture: `b"the quick brown fox jumps over the lazy dog " * 5` (220 bytes), base64-encoded and
then re-wrapped at 60 chars/line with embedded `\n`s plus a trailing `\n` — the real shape
GitHub's contents endpoint returns, not a synthetic unwrapped string. Assertion: the decoded text
equals the original plaintext (call wrapped in try/except so a raise fails the check instead of
crashing the script, keeping the rest of the suite executing under RED).

**RED (written and run before any production change):**
- Ran `python3 .claude/skills/harness/bin/test-factory-gh.py` against the unmodified `raw` decode.
  Verbatim FAIL line: `FAIL  file_at_ref: decodes GitHub's line-wrapped base64 content`
- `1 of 163 FAILING.` — exactly the new case, nothing else. `grep -E "^FAIL"` on the full output
  confirmed only that one line.

**GREEN:** applied the `"".join(raw.split())` change. Re-ran: `163/163 checks passed.`, rc=0.

### Reddening proof (post-fix, per dispatch)
- sha256 of `factory_gh.py` before mutating: `88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`.
- Mutation: reverted line 456 to the pre-fix `base64.b64decode(raw, validate=True)`.
- Ran the suite. Verbatim FAIL line: `FAIL  file_at_ref: decodes GitHub's line-wrapped base64 content`
- `1 of 163 FAILING.` — `grep -E "^FAIL"` confirmed ONLY the new named case reddened; every other
  case, including the four pre-existing `file_at_ref` cases and `default_branch_sha`, stayed green.
- Restored the strip. sha256 after restore: `88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`
  — matches exactly, byte-identical. `git diff --exit-code` against HEAD shows only the intended
  2-line functional diff (expected — HEAD carries the bug; this restore is to the fixed state, not
  to HEAD).

## Secondary — `raw == "null"` vs `raw.strip() == "null"`

**Verified empirically: the change is INERT, exactly as the dispatch's reading predicted.**

- Applied `raw.strip() == "null"` in isolation (primary fix left in place). Ran the full suite:
  `163/163 checks passed.`, zero cases changed state in either direction.
- Tried to construct a fixture where `raw` reaches this guard carrying trailing whitespace: cannot.
  `run_gh` (factory_gh.py:107) returns `r.stdout.strip()`, and `raw = run_gh(argv)` (line 442) is
  `file_at_ref`'s only source of `raw` — confirmed by reading both lines directly. `.strip()`
  removes all leading/trailing whitespace before `raw` exists, so `raw` can never carry trailing
  whitespace when it reaches the guard, by construction of the seam it comes through, not by luck
  in any one fixture.
- Reverted the change — sha256 confirmed byte-identical to the primary-fix-only state
  (`88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`) before proceeding.

**Decision: did NOT land it.** It closes no real defect (proven above, not just asserted per the
dispatch's reading) and touches a line neither this cycle's defect nor its test exercises. Landing
a provably-inert change would be undocumented scope with no test that could ever fail on it — the
opposite of "cheap and reversible" once someone downstream reads it as a fix for something real.
Recording it here as inert/defensive would still be inaccurate, since it defends against nothing
reachable; not landing it is the more honest record. If a future caller of `file_at_ref` (not
`run_gh`) can produce unstripped `raw`, this guard should be revisited then, against that caller.

## T-01 verify

Ran verbatim (matches `plan.yaml:306-316` exactly, cross-checked before running):

    T-01 GREEN

## Live acceptance call (not the suite — the actual read)

    python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin');
    import factory_config as fc; f=fc.load_fleet('.harness/factory/fleet.yaml');
    print(fc.board_for(f,'mruangutai/kaya-ai')); print(fc.board_station(f,'mruangutai/kaya-ai','ready'))"

Output (verbatim):

    {'owner': 'mruangutai', 'number': 2, 'station_field': 'Status', 'stations': {'backlog': 'Backlog', 'ready': 'Ready', 'building': 'Building', 'review': 'Review', 'done': 'Done'}}
    Ready

Matches the acceptance criteria exactly: owner `mruangutai`, number 2, `station_field` `Status`,
five stations, and `board_station(..., "ready")` returns `Ready`. `board_for`/`board_station` no
longer raise `FleetError: product config unreadable`.

## Full-suite red set (`.claude/skills/harness/bin/run-unit-tests.sh`, run from the worktree)

**Red set is EMPTY.** `rc=0`, zero `^FAIL` lines anywhere, all 28 test files report
`PASS test-*.py` in their header line (`grep -cE "^(PASS|FAIL) test-"` → 28, `grep -E "^FAIL
test-"` → none).

This differs from fix-c1's receipt, which recorded two pre-existing red files
(`test-no-distribution.py`, `test-check-state.py`). Both are green now — neither file was touched
in this fix cycle, and `grep -n "factory_gh\|factory_config\|file_at_ref" test-check-state.py
test-no-distribution.py` shows no reference to the changed code, so this fix did not clear them.
No red is attributable to this change: the red set went from fix-c1's two-file baseline to empty,
not the reverse.

## `validate=True` — confirmed load-bearing, but not by the case the dispatch names

Checked whether the existing case `file_at_ref: undecodable content raises rather than returning
empty` (`"not-valid-base64!!!"`) actually discriminates `validate=True` from `validate=False`.
It does not: in an isolated `python3 -c` check (production file untouched), `"not-valid-base64!!!"`
raises under BOTH — `binascii.Error: Incorrect padding` either way, because after alphabet-stripping
it's 14 chars, a padding error, not an alphabet error. So that case would still pass green even if
`validate` were silently flipped to `False`. Confirmed by directly setting `validate=False` in the
source and asking to run the suite — the auto-mode Bash classifier blocked the run outright rather
than let a weakened validation flag execute test code, which is itself a form of confirmation this
matters. Restored to `validate=True` immediately; sha256 unchanged
(`88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`), suite re-confirmed
163/163 pass.

This is a real gap, not fixed here (out of this cycle's scope — the dispatch authorized one new
case). Flagged as Q2 below.

## Branch/commit reconciliation

Dispatch named `feat/FEAT-24-config-responsibility-split` at `b88cbfd`. Confirmed `git
branch --show-current` is that branch, and `b88cbfd` is an ancestor of HEAD
(`git merge-base --is-ancestor b88cbfd HEAD` → true). HEAD itself is NOT `b88cbfd` — the branch
had already moved on to `d80f1c4` ("FEAT-24: reconcile the record with the tree after the
sleep-interrupted session") before I started.

**Mid-run discovery, disclosed rather than smoothed over:** partway through this run, before I had
returned anything, `git log` showed my exact two-file diff already present as a new commit,
`574f73c` — "[harness:t-01] file_at_ref decodes GitHub's line-wrapped base64" — landed on top of
`d80f1c4` while I was still working (sha256 of `factory_gh.py` on disk matched what I'd have
committed, byte for byte; `git status` showed those two files clean against HEAD). I did not run
`git commit` at any point in this session. Something outside my own tool calls — consistent with
"the pen is the orchestrator's" — committed the work while it was in progress. I left it as found:
did not amend it, did not attempt to re-commit, did not revert it. `git log --oneline -1` at the
time of this receipt is `574f73c`.

## Decisions / refusals
- Landed the whitespace-strip fix, `validate=True` unchanged, per the dispatch's primary.
- Did NOT land the `raw.strip() == "null"` change — proven inert, decision above.
- Added exactly one new named case; did not delete, renumber, or weaken any existing case.
- No other `recorder([Result(...)])` call sites were touched — see open question below.

## Open questions
- Q1 (non-blocking): `test-factory-gh.py:904` (happy-path) and `:910` (argv-shape case) still feed
  `file_at_ref` synthetic unwrapped base64 via `base64.b64encode(...).decode()` directly, not the
  line-wrapped shape GitHub actually returns. They're not wrong — the new wrapped case now covers
  the class this fix cycle was about — but they're two more instances of the same "recorder fed a
  synthetic-clean payload, not a wire-realistic one" pattern the dispatch flagged. Not fixed here,
  per the dispatch's explicit scope boundary (note only, don't fix).
- Q2 (non-blocking): the existing case `file_at_ref: undecodable content raises rather than
  returning empty` does not actually discriminate `validate=True` — `"not-valid-base64!!!"` raises
  under `validate=False` too (padding error, not alphabet error). `validate=True` is genuinely
  correct to keep (per the dispatch), but nothing in the suite would catch a regression to
  `validate=False`. Would need a fixture that is the right LENGTH (correct padding) but contains an
  out-of-alphabet character, to actually pin the flag. Not added here — out of this cycle's
  one-new-case scope.

## Files touched
- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/test-factory-gh.py`
