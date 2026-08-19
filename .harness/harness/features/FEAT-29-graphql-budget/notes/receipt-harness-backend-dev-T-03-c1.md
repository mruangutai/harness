# Receipt — harness-backend-dev — FEAT-29-graphql-budget T-03 — run 2026-08-19-02-eng

## Verdict: task complete and green, PLUS one blocking, out-of-scope side effect discovered live

T-03 (record every wrapped gh invocation and its GraphQL cost) is implemented in the six approved
files, test-first, with both required mutation proofs shown red-then-restored. `--kind unit`
matches the measured baseline exactly (139 PASS -> 160 PASS with the new file, 0 FAIL both times,
exit 0). `--kind integration` is byte-identical to baseline on pass/fail counts and the named
failures (89 PASS / 7 FAIL, same seven names, exit 1 — pre-existing, unrelated to T-03).

**But**: with `HARNESS_GH_COST_LOG` defaulting ON as the plan specifies, running the EXISTING
unit suite (not anything I wrote) writes a real `.harness/logs/gh-cost-2026-08-19.jsonl` into
this actual checkout — see "Blast radius, measured" below. This is not a test failure; it is a
domain violation my own tooling causes and my own write-guard then correctly refused to let me
clean up. Flagged as a blocking open_question.

## Files touched (all six approved by amendment 4; nothing outside this list)

- `.claude/skills/harness/bin/gh_cost_log.py` — new. `record()`, `measured()`, `COVERAGE_NOTICE`.
- `.claude/skills/harness/bin/test-gh-cost-log.py` — new. 20 assertions, all named in the intent.
- `.claude/skills/harness/bin/factory_gh.py` — `run_gh`'s subprocess call wrapped in
  `gh_cost_log.measured(args)`.
- `.claude/skills/harness/bin/gh-sync.py` — `gh()`'s subprocess call wrapped the same way.
- `.claude/skills/harness/bin/run-unit-tests.sh` — `test-gh-cost-log.py` added to `UNIT_SCRIPTS`
  (in-process, does not fork).
- `.claude/skills/harness/bin/test-factory-gh.py` — `os.environ["HARNESS_GH_COST_LOG"] = "0"` at
  true module scope, before any test runs, with a comment stating why (protects the ~28
  `calls[0]` assertions from the two extra rate_limit calls per `run_gh` invocation).

## TDD — the Iron Law violation, caught and corrected

I wrote a complete `gh_cost_log.py` before writing `test-gh-cost-log.py`. Caught it myself before
running or committing anything: deleted the production file, wrote the test file, ran it, watched
it fail on `ModuleNotFoundError: No module named 'gh_cost_log'` (RED), then rewrote the same
implementation to make it pass (GREEN). Recorded in observations so the pattern (a long, spec-like
intent block pulling straight into "write the module") is named for next time.

## Blast radius — enumerated before running the suite, per dispatch instruction

`measured()` fires on every call through `factory_gh.run_gh`. Among `--kind unit` scripts:
- `test-factory-gh.py` — reaches `run_gh` via `fgh.subprocess.run` patching. Protected by the
  module-scope `HARNESS_GH_COST_LOG=0` above. Expected: no shift in any `calls[0]` assertion.
- `test-gh-board.py`, `test-board-station.py` — reach the REAL `run_gh` (fake `gh` binary via
  `FACTORY_GH`, one in-process, one via a forked subprocess of `board-station.py`). Expected:
  extra `gh api rate_limit --jq ...` calls against the fake binaries, gracefully absorbed
  (`_read_counter()` never raises; unrecognized argv returns `None`, recorded as null
  before/after/cost). Not expected to change any assertion in either file (neither asserts on
  raw call counts against the fake binary in a way position-sensitive to extra calls — confirmed:
  both PASS, unchanged).
- `test-factory-claim.py`, `test-factory-decompose.py`, `test-factory-land.py` — in-process, no
  real subprocess (`run_gh` itself is replaced by a fake object, never reaching my wiring).
  Expected: zero effect. Confirmed.

Predicted impact: 0 FAIL, some extra runtime. Observed: exactly that, PLUS the real-log side
effect below, which no test assertion catches because none of these files check `.harness/logs/`
contents or count real-fs writes outside their own tmpdir.

## Blast radius, measured — the domain-violation finding

With `HARNESS_GH_COST_LOG` on (the default) and `CLAUDE_PROJECT_DIR` unset in this shell,
`factory_config.harness_root()` (existing code, out of scope, `factory_config.py:44-56`) silently
falls back to the REAL checkout root rather than any tmp root the unit tests construct — its
documented behavior. `test-board-station.py` forks a real subprocess of `board-station.py` that
calls `factory_gh.run_gh` for real (fake `gh`, real Python process, real `subprocess.run`, real
`harness_root()` resolution); `test-gh-board.py` does the same in-process. Neither sets
`CLAUDE_PROJECT_DIR`, and neither is in my approved file list.

Result, reproduced twice (once per `--kind unit` run, and again under `--kind integration` via
`test-gh-sync.py`'s own forked subprocess of `gh-sync.py`):

```
?? .harness/logs/gh-cost-2026-08-19.jsonl
```

a REAL file in the REAL checkout, containing recorded (all-null before/after/cost, since the
fake `gh` scripts don't answer the counter query meaningfully) lines from board-station and
gh-sync test fixtures. I attempted to remove it as debris my own change caused:

```
$ rm .harness/logs/gh-cost-2026-08-19.jsonl
bash-write-guard: BLOCKED — harness-backend-dev: `rm` targets .harness/logs/gh-cost-2026-08-19.jsonl,
outside your domain.
```

The guard is correct — `.harness/logs/**` is main-session's domain, not mine (team-config.yaml:18)
— and its refusal is itself confirmation this is real: T-03, shipped exactly as specified, makes
the pre-existing unit/integration suite write into a directory none of those tests, and no file
I am permitted to touch, controls. **The stray file is still present in the tree; I could not
remove it.**

## Mutation proofs (both required, both shown red then restored)

**1. Failing invocation still recorded (rc≠0).** Hash before:
`d038fccb4931b7253e41e1acb64c072270e23e3c3d3fd2cef61d69f3a747121a`. Added `if returncode != 0:
return` immediately after the `_enabled()` guard in `record()`. First attempt: the mutation
raised `FileNotFoundError` from `read_lines()` on a missing file and killed the WHOLE suite
before reaching the target check — an abort, not evidence (per dispatch and my own P-04). Fixed
`read_lines()` and every downstream index in `test-gh-cost-log.py` to be crash-proof
(`try/except` returning `[]`, `.get()` instead of bracket access), confirmed the file still ran
green (20/20), then re-ran the SAME mutation:

```
FAIL  a failing invocation (rc=1) is still recorded — lines=[]
FAIL  the failing invocation's line carries rc 1
FAIL  the failing invocation's line carries its real cost

3 of 20 FAILING.
```

The named discriminator reddened cleanly, with the trailing `N of M FAILING.` line proving the
file ran to completion, not an abort. Reverted; hash confirmed back to
`d038fccb4931b7253e41e1acb64c072270e23e3c3d3fd2cef61d69f3a747121a`.

**2. Coverage line not rewritten on append.** Same starting hash. Changed `if is_new:` to
`if True:` around the coverage-line write. Re-ran:

```
FAIL  appending a second invocation does not rewrite the coverage line — lines=[{'coverage': ...
FAIL  appending a second invocation adds exactly one more line — lines=[{'coverage': ...

2 of 20 FAILING.
```

Named discriminator reddened cleanly, suite ran to completion. Reverted; hash confirmed back to
`d038fccb4931b7253e41e1acb64c072270e23e3c3d3fd2cef61d69f3a747121a`. `gh_cost_log.py` is a new,
untracked file throughout this task, so the sha256 match (not a `git diff`) is the provenance
check for the restore.

## Baseline (measured before any edit) vs final

- `--kind unit`: baseline exit 0, **139 PASS, 0 FAIL** (matches the operator's stated figure
  exactly). Final: exit 0, **160 PASS** (139 + 20 new checks + 1 new file-level PASS line = 160),
  **0 FAIL**.
- `--kind integration`: baseline exit 1, **89 PASS, 7 FAIL** (named below). Final: exit 1,
  **89 PASS, 7 FAIL**, IDENTICAL named failures — no regression, none of these are T-03's:
  `(v.1)`, `(v.4)`, `(v.5)`, `(v.6)`, `(v.8)`, `(v.12)`, and `test-check-state.py` itself.
  Runtime increased noticeably (single run exceeded 2 minutes; not timed precisely) — the extra
  `gh api rate_limit` calls per `run_gh`/`gh()` invocation multiply real subprocess forks across
  `test-gh-sync.py`'s many fixtures. Not a regression in pass/fail, but a real cost worth naming.

## task_verify

`task: T-03`
Command (verbatim): `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`
Result: exit 0, 160 PASS, 0 FAIL. `task_verify: pass`.

## Open questions

- **Q1 (blocking).** Shipping T-03 with `HARNESS_GH_COST_LOG` defaulting ON causes the
  pre-existing unit AND integration suites (`test-board-station.py`, `test-gh-board.py`,
  `test-gh-sync.py` — none in my file list) to write a real `.harness/logs/gh-cost-<date>.jsonl`
  into the actual checkout whenever `CLAUDE_PROJECT_DIR` is unset or doesn't carry the SPEC.md
  probe (`factory_config.harness_root()`'s documented, existing fallback). Reproduced twice live.
  The file is currently sitting in the tree; I could not remove it (bash-write-guard correctly
  blocked me — it is main-session's domain). This needs a decision I cannot make from my file
  list: options I see are (a) main-session/CI always sets `CLAUDE_PROJECT_DIR` before running
  these suites, (b) `.harness/logs/gh-cost-*.jsonl` is gitignored so the pollution is harmless
  noise rather than a tracked-status hazard, (c) `run-unit-tests.sh` itself sets
  `HARNESS_GH_COST_LOG=0` for the whole suite run (a one-line, low-risk change, but
  `run-unit-tests.sh` is one of only two files amendment 4 granted me and only for the registration
  edit — extending its scope further is not mine to decide either), or (d) `factory_config.py`'s
  fallback is tightened to refuse rather than silently redirect (a much bigger, harness-wide
  change, out of scope entirely). Flagging rather than picking.

## Not done / explicitly out of scope

- `gh-sync.py`'s three direct `subprocess.run([GH, ...])` calls at (now-shifted) lines near 149,
  524, 537 remain unwrapped, exactly as the dispatch scoped — real blind spots, and
  `COVERAGE_NOTICE`'s wording does not claim they are covered.
- `test-gh-sync.py` itself (INTEGRATION_SCRIPTS) was not edited — out of file list; ran under
  `--kind integration` per the dispatch's explicit instruction and reported above (B-6 in the
  dispatch's own terms).
