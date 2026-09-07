# Receipt — harness-backend-dev — T-05 — c1

## Task
Mutation-prove the per-repository resolution at the unit boundary (SC-08). Added exactly
one new file: `tests/unit/test-factory-claim-mutation.py`. No production file touched, no
other test file touched.

## Verify — run verbatim, cross-checked against plan.yaml's T-05 `verify:` block (matches, no discrepancy)

Command:
```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && out=$(python3 tests/unit/test-factory-claim-mutation.py 2>&1); printf '%s\n' "$out" | grep -q '^BASELINE 3/3 ok' && printf '%s\n' "$out" | grep -q '^MUTATION PROOF: 3/3 cases reddened'
```
Result: **exit 0**.

Actual output of `python3 tests/unit/test-factory-claim-mutation.py` (verbatim):
```
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
MUTATION PROOF: 3/3 cases reddened
```
Both required marker lines present (`BASELINE 3/3 ok`, `MUTATION PROOF: 3/3 cases reddened`),
`MUTANT ACTIVE` observed (the proxy's `features_root` wrapper was actually reached), and all
three captured `FAIL BUG-1290 5a/5b/5c` marker lines printed as required.

## `tests/unit/test-factory-claim.py` — unchanged, still green standalone

Not touched by this task. Confirmed via `git status --porcelain`: shown modified only from
T-01/T-02 (prior landed tasks), no further diff from this task. Ran on its own:
```
python3 tests/unit/test-factory-claim.py
```
Exit 0, tail: `124/124 checks passed.`

## Mechanism, and one implementation pivot from the intent's literal wording

The mutant is `_MutantFactoryConfig`, substituted for `factory_claim.factory_config`. Its
`__getattr__` delegates every name to the real module via `getattr(real, name)` except
`features_root`, whose returned wrapper discards `repo_name` and always calls
`real.features_root("acme/harness")` (owner-qualified, segment `harness`) — `real` is looked
up fresh at call time, so the proxy sits in front of the suite's own
`factory_config.features_root` monkeypatch rather than bypassing it (T05-mechanism, panel
finding PF-44a651d61bd7f1be96864fc9b7256f46).

**Pivot, discovered empirically, not assumed:** the intent's step 3 says "the wrapper prints
MUTANT ACTIVE" with no further qualification, which I first wrote as a plain `print(...)` to
`sys.stdout`. That broke the suite: `features_root` is called from deep inside
`run_main`'s own `contextlib.redirect_stdout(out)` (the suite's tool-output capture), so the
marker landed inside `out` and corrupted an unrelated assertion — `test-factory-claim.py`
line 473's `json.loads(out)` on the M3/M6 happy-path case, aborting the whole run before it
ever reached 5a-5c (measured: `out` became `'MUTANT ACTIVE\n'`, verbatim, via a standalone
repro that called `run_main` directly with the mutant installed). Fixed by writing the
marker to `sys.__stdout__` explicitly, which no `redirect_stdout` in either file ever
retargets, so it reaches the real process stream without entering any captured buffer. I
also added a `reached()` self-check: if `features_root` is never called under mutation, the
proof prints `MUTANT NEVER REACHED` / `MUTATION PROOF: INCOMPLETE` and exits 1 rather than
silently passing zero cases (matches the intent's own reasoning for the marker's existence).

## Acceptance checklist
- File exists at `tests/unit/test-factory-claim-mutation.py`; spawns no subprocess; imports
  no test framework (only stdlib: `contextlib`, `io`, `runpy`, `sys`, plus `factory_claim`
  and `factory_config`); restores `factory_claim.factory_config` to the real module in a
  `finally` block before returning control, on every path (mutation success or incomplete).
- Mutant wrapper discards `repo_name` and calls through with one fixed harness-segment fleet
  name (`"acme/harness"`), a plain string constant used as an argument, not a path join or a
  dict lookup keyed on the candidate.
- Only one file added (`tests/unit/test-factory-claim-mutation.py`, shown `??` in
  `git status --porcelain`); no other file modified by this task.
