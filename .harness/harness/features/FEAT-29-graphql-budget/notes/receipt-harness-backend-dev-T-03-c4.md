# Receipt — harness-backend-dev — T-03 cycle 4

## Task
T-03, cycle 4 of `plan.yaml` (approval amendment 6, `why_cycle`). Scope: pin
`_cost.returncode = r.returncode` at `factory_gh.py:162` with one new assertion. No production
edit — `factory_gh.py` ends this cycle byte-identical to how it started.

## What was added

One new case in `.claude/skills/harness/bin/test-gh-cost-log.py`, appended after the four
existing wrap-site cases and before the `if FAILURES:` block: `_counting_fake(rc=1)` drives a
**failing** invocation through the real `factory_gh.run_gh`, catches the raised `GhError` (forced
by `run_gh`'s own non-zero-exit branch — not a design choice), and asserts three things:
1. `GhError` was raised
2. exactly one non-coverage line was written
3. **the logged record's `rc` field equals `1`** — the clause SC-05 names and the one no prior
   case inspected.

Case names, verbatim, all three new:
- `factory_gh.run_gh wrap site, FAILING: GhError was raised`
- `factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation`
- `factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)`

## RED proof (mandatory — B-1 aborts do not count)

Recorded `sha256` of `factory_gh.py` before mutating: `110d07c7053e3ff627c818504174a7ce4c271b0cf37eae9355101f5cfb46c252`.

Deleted line 162 (`_cost.returncode = r.returncode`) with `sed -i '' '162d'`. Ran
`python3 .claude/skills/harness/bin/test-gh-cost-log.py`. Exit was non-zero (`1 of 35 FAILING.`).
The **named** check reddened, and only that one:

```
PASS  factory_gh.run_gh wrap site, FAILING: GhError was raised
PASS  factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation
FAIL  factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1) — non_cov=[{'ts': '2026-08-20T04:00:40.663640Z', 'argv': ['issue', 'view', '1'], 'before': 1001, 'after': 1003, 'cost': 2, 'rc': -1}]

1 of 35 FAILING.
```

`rc: -1` is exactly the fallback in `gh_cost_log.measured`'s `finally` clause (`m.returncode if
m.returncode is not None else -1`) — proof the mutation removed the only write to `.returncode`,
not an unrelated break. This reddened a **named check**, not an abort — the suite ran to
completion and printed `1 of 35 FAILING.` with an exit code.

Restored via `git checkout -- .claude/skills/harness/bin/factory_gh.py` (file had zero prior
uncommitted changes — confirmed against the earlier `git status`, so this is not the G-13 trap).
Re-hashed: `110d07c7053e3ff627c818504174a7ce4c271b0cf37eae9355101f5cfb46c252` — identical.
`git status --porcelain .claude/skills/harness/bin/factory_gh.py` — empty output, confirming the
file is absent from the working diff.

## GREEN proof

`python3 .claude/skills/harness/bin/test-gh-cost-log.py` on the restored tree: `35/35 checks
passed`, exit 0. Same three new checks, all `PASS`.

## `verify:` cross-check

`plan.yaml`'s T-03 `verify:` field, read via `yaml.safe_load`:
`.claude/skills/harness/bin/run-unit-tests.sh --kind unit\n` — matches the dispatch verbatim.

### `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`

Exit 0. 0 `FAIL` lines. 18 `PASS <script>` lines (script-level convention, unchanged count).
`test-gh-cost-log.py` reported **35/35 checks passed** — up from 32/32 recorded at HEAD 3fbfd0a,
confirming the check count rose by exactly the 3 new checks (not a `SyntaxError`-style silent
zero-FAIL false green).

Full tail:
```
PASS  factory_gh.run_gh wrap site, FAILING: GhError was raised
PASS  factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation
PASS  factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)

35/35 checks passed
PASS test-gh-cost-log.py
```

### `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` (additional, per dispatch)

Exit 0. 0 `FAIL` lines. 12 `PASS <script>` lines, unchanged. `test-factory-integration.py`
reported `106/106 checks passed.` — same count as before this cycle (no integration check was
added or expected to be; amendment 6 scopes this cycle to the unit file only).

## Log discipline

Every new case redirects `factory_config.harness_root()` to a `tempfile.TemporaryDirectory()` via
the existing `redirect(tmp)` helper (which itself asserts the redirect took effect, at
`test-gh-cost-log.py:54`) before any write. `.harness/logs/gh-cost-2026-08-19.jsonl` mtime is
`Aug 19 14:09:22 2026`, predating every test run in this cycle (all run after 21:02 the same day)
— confirms the operator's log file was never touched by any run in this cycle. No
`HARNESS_GH_COST_LOG=1` was ever set outside a redirected temp root.

## Files touched

- `.claude/skills/harness/bin/test-gh-cost-log.py` — +31 lines, one new test case, three new
  assertions. This is the only file this cycle changed.
- `.claude/skills/harness/bin/factory_gh.py` — touched only transiently during the RED probe;
  `git diff` on it is empty at report time, confirmed by hash and `git status --porcelain`.

Other working-tree modifications present (`plan.yaml`, `feature.json`, `CLAUDE.md`,
`observations/harness-eng-lead.md`) predate this cycle and were not touched here — confirmed via
`git diff --stat` scoped to just those paths versus the two files this cycle owns.

## Scope discipline

Did not touch `check-state.sh`, `test-check-state.py`, `test-gh-sync.py`, `.harness/notes/**`, or
`.harness/logs/**`. Made no live `gh` call. Did not run `check-state.sh`. Did not act on B-1, B-2,
B-3, or the `hasNextPage`/null-`endCursor` item at `factory_gh.py:359-363`.
