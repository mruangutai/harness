# Receipt — harness-backend-dev — FEAT-29 T-03 SC-05 fix cycle (sc05-c1)

## Scope actually covered

The dispatch's own re-derivation of the gap was correct and is what I built: the wrap sites at
`test-gh-cost-log.py:335-346` (factory_gh.run_gh, OFF) and `:367-379` (gh-sync.py's gh(), OFF) were
already driving the real wrapper OFF, but only at `rc=0`. The truly absent case was **OFF + real
wrapper + non-zero rc** — mirroring the ON/FAILING case already at (pre-edit) `:381-410`.

Added one new block to `test-gh-cost-log.py` (now the file's final case, before the summary/exit
block), with 4 checks distinctively named `"OFF, FAILING: ..."`:

1. `OFF, FAILING: GhError was still raised` — the real error is not swallowed.
2. `OFF, FAILING: no log file is created`
3. `OFF, FAILING: no line is written`
4. `OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)`

Drives `factory_gh.run_gh` for real through `_counting_fake(rc=1)`, `HARNESS_GH_COST_LOG` popped
(genuinely unset, not `"0"`), catches the raised `_fgh.GhError`. Same shape as the existing
:335-346/:381-410 cases.

## Files touched

- `.claude/skills/harness/bin/test-gh-cost-log.py` — only file changed.

**Production code diff is empty**, confirmed:

```
$ git status --porcelain -- .claude/skills/harness/bin/gh_cost_log.py .claude/skills/harness/bin/factory_gh.py .claude/skills/harness/bin/gh-sync.py .claude/skills/harness/bin/test-gh-cost-log.py
 M .claude/skills/harness/bin/test-gh-cost-log.py
```
No other line — `gh_cost_log.py`, `factory_gh.py`, `gh-sync.py` are byte-identical to HEAD
(01548f9) after the mutation cycle below restored them; confirmed both by `git status --porcelain`
above and by sha256 match (next section).

## Standalone run (new case only, before full-suite mutation proof)

```
$ python3 .claude/skills/harness/bin/test-gh-cost-log.py
...
PASS  OFF, FAILING: GhError was still raised (the wrapper does not swallow the real error)
PASS  OFF, FAILING: no log file is created
PASS  OFF, FAILING: no line is written
PASS  OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)

39/39 checks passed
```

## Task verify (verbatim from dispatch, cross-checked against plan.yaml:286-287 — match)

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

**Predicted count, before running:** file had 175 `PASS ` lines pre-edit (re-measured myself, not
copied — matches dispatcher's figure). Adding 4 new checks predicts 179.

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit   # post-edit, pre-mutation
exit=0
$ grep -c '^PASS ' <log>
179
```
Prediction confirmed: 175 -> 179, +4, matching the 4 checks added. `task_verify: pass`.

Also ran (per dispatch instruction, not part of the declared `verify:`):
```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration
exit=0
106/106 checks passed.
PASS test-factory-integration.py
```

## Mutation proof — delete `not _enabled() or` at gh_cost_log.py:157

Pre-mutation hash: `b5d24cea70dcdf0eeadc097ae51faaea19f478fc8c82ad78f7f50e62ff198f5e`

Mutated `measured()`'s guard from:
```python
if not _enabled() or is_counter_call(argv):
```
to:
```python
if is_counter_call(argv):
```

### Run 1 — mutated, `--kind unit`

Exit code: **1**. This run did **not** abort — it printed clean `FAIL` lines with a trailing count
and continued to the next script, which is the load-bearing distinction the dispatch asked me to
report (contrast with `test-factory-gh.py`'s abort, below).

Full set of checks that reddened, by name:

- `test-gh-cost-log.py` (script exit 1, `3 of 39 FAILING.`, ran to completion — NOT aborted):
  - `factory_gh.run_gh wrap site, OFF: exactly one subprocess call (the real call only)`
    (pre-existing check, was at :344-345 pre-edit)
  - `gh-sync.py gh() wrap site, OFF: exactly one subprocess call (the real call only)`
    (pre-existing check, was at :377-378 pre-edit)
  - `OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)`
    (my new check)
  - All three carried the same `calls=[rate_limit, real-call, rate_limit]` detail — the mutation
    removed the OFF short-circuit, so `measured()` now reads the counter on both sides
    unconditionally regardless of rc.
  - The other 3 new "OFF, FAILING" checks (`GhError was still raised`, `no log file`, `no line
    written`) stayed green under this mutation — expected: `record()`'s own separate guard at
    `gh_cost_log.py:112` (`if not _enabled(): return`) still blocks the write and the raise is
    unaffected by either guard. Only the call-count check can see this particular mutation.

- `test-factory-gh.py` (**aborted**, not a clean FAIL): `run_gh: message carries the captured
  stderr` reddened first (one named `FAIL` line, detail
  `exc=gh issue list failed: issue list — rate_limit query itself failed` — the extra unconditional
  counter read consumed a queued fixture `Result` meant for the real call), then a **later**,
  unrelated fixture (`run_gh(["auth", "status"])`) raised an unhandled `StopIteration` /
  `AssertionError: recorder ran out of results` that crashed the whole script with a Python
  traceback — no `FAIL <script>` summary reached, no per-check tally past that point. This is the
  pre-existing B-1 property named in the dispatch, not something the new case introduced or could
  fix; `test-factory-gh.py` is outside my file list.

Command + full relevant stdout captured in
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/070b3f94-b495-4deb-b352-6896cfb60ad3/scratchpad/unit_mutant.log`.

### Restore + hash re-verify

```python
# reverted "if is_counter_call(argv):" back to
# "if not _enabled() or is_counter_call(argv):"
```
Post-restore hash: `b5d24cea70dcdf0eeadc097ae51faaea19f478fc8c82ad78f7f50e62ff198f5e` — **matches**
pre-mutation hash exactly. `git status --porcelain` on the three production files: empty (see
Files touched section).

### Run 2 — restored, `--kind unit`

```
exit=0
179 PASS lines
```

### Run 2b — restored, `--kind integration`

```
exit=0
106/106 checks passed.
PASS test-factory-integration.py
```

## Honest answer on mutation-discrimination power

**No** — I agree with the dispatch's own reading. There is no mutant my new check kills that the
existing checks (the two pre-existing call-count checks at what were `:344-345`/`:377-378`) do not
already kill. All three reddened together, from the same root cause (the removed OFF
short-circuit), under the one mutation tested. `record()`'s second guard at `:112` makes an
OFF-path *write* unreachable regardless of rc, so my check's write/no-write assertions
(`no log file`, `no line written`) can never distinguish a mutant the pre-existing OFF/rc=0 cases
don't already catch via the same guard. What the new case adds is **not** new mutation-kill power —
it is closing a grading/coverage ambiguity: SC-05's amended sentence explicitly names "including for
a failing invocation," and before this change no test drove the real wrapper OFF with a non-zero rc
at all. I am not claiming discriminating power beyond that.

## SC-08 / SC-09

Not touched, per LEAVE LIST instruction.
