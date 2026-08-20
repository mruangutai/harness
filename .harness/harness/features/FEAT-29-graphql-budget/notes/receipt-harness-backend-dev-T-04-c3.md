# Receipt — harness-backend-dev — FEAT-29 T-04 (cycle 3, FINAL)

## Scope of this cycle

Surgical: make the actual named discriminator in `test-factory-gh.py`
("run_gh: unrelated failure never contains the GraphQL budget headline", the check right after
"run_gh: unrelated exit-1 raises a plain GhError, not a budget error") observably red in-repo, by
mutating the MARKER LIST (`_RATE_LIMIT_MARKERS` in `factory_gh.py`), not the guard mutated in
cycles 1 and 2. That check has never been observed red before this cycle.

## The fix

Two test-file edits, both at the discriminator's own fixture (the "an unrelated exit-1 does NOT
produce the budget message" section):

1. Queued a second `Result` on that fixture's `recorder` — a spare, exactly like the three cycle-2
   additions, given for the same reason: under the mutation the call is misrouted into the budget
   path, which issues a second subprocess call (`gh api rate_limit`) the recorder was not built to
   survive with only one queued item.
2. Rewrote the fixture's comment, which previously stated (as "deliberate design") that the
   fixture queues only ONE `Result`. That rationale is superseded by the spare — the comment now
   explains why a second Result is queued and why it is inert under unmutated code.

The spare `Result` is a **success** (`Result(0, stdout=_RATE_LIMIT_JSON)`), not another failure —
this differs from all three cycle-2 spares, which were failures. Reasoning, verified live (see
"Wrong spare tried first" below): the target check's whole purpose is to prove the string
`"GraphQL budget exhausted"` does not appear. That headline is only produced when
`_rate_limit_budget_error`'s own inner `run_gh(rate_argv)` call **succeeds** and returns valid
JSON. A second failing Result routes the inner call's own `except GhError` branch instead,
producing the *different* message `"gh reported a rate limit and the budget could not be read"` —
which also does not contain "GraphQL budget exhausted", so the target check would stay green even
though the call was misrouted. Only a successful inner call exercises the actual headline the
check watches for.

Mutation applied (`factory_gh.py`, `_RATE_LIMIT_MARKERS`):

```
 _RATE_LIMIT_MARKERS = (
     "api rate limit exceeded",
     "was submitted too quickly",
     "rate limit",
+    "could not resolve",
 )
```

This matches the discriminator fixture's own stderr text verbatim
(`"could not resolve to a Repository with the name 'o/nope'"`) and no other fixture's text in the
file (confirmed by the two-check blast radius below — every other `run_gh`-backed fixture's
stderr/stdout text was left alone).

Files touched, both on the approved write list: `.claude/skills/harness/bin/factory_gh.py`
(mutation applied and reverted only, no net change), `.claude/skills/harness/bin/test-factory-gh.py`
(discriminator fixture given a spare `Result`, its comment rewritten).

## Wrong spare tried first — recorded per rule 15, never hidden

Before the successful attempt, ran the mutation once with the spare Result set to a **second
failure** (`Result(1, stdout="", stderr="rate_limit query itself failed")`) — the same shape used
for cycle 2's three spares. Result: the named check stayed green
(`msg2` was `"gh reported a rate limit and the budget could not be read: ..."`, which does not
contain `"GraphQL budget exhausted"` either) and only the sibling "preserves the original gh text"
check reddened. That is not the target — switched the spare to success (above) and re-ran, which
reddened the actual named discriminator. Both runs are reproducible from the mutation state
described in this receipt; the failing-spare version is not committed to the tree.

## Unmutated confirmation (spare Result is inert), both before and after the mutation cycle

`python3 .claude/skills/harness/bin/test-factory-gh.py` → `198/198 checks passed.`, run three
times: (a) immediately after adding the spare Result, before any mutation; (b) after reverting the
mutation the first time (hash-verified below); (c) as the final clean re-run. Same count in all
three. Confirms the spare changes no unmutated-path behavior — `recorder`'s `fake_run` only raises
when `next(it)` runs out, so an unconsumed queued item is a no-op, success or failure alike.

## Mutation — applied, full suite run, reverted

`sha256sum factory_gh.py` before mutation: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8`.

### The named discriminator — exact FAIL line, with `msg=` detail

```
FAIL  run_gh: unrelated failure never contains the GraphQL budget headline
        msg='GraphQL budget exhausted: 5000 of 5000 points used, resets at 2025-08-19T10:40:00Z — this is the GraphQL budget, not the REST budget — REST currently sits at 42 of 5000'
```

This is the repository's own assertion, unmodified — the check named in the dispatch, at the
location named in the dispatch (`test-factory-gh.py`, the "an unrelated exit-1 does NOT produce the
budget message" section). It reddens because the mutant genuinely changed `run_gh`'s routing: an
ordinary "could not resolve to a Repository" failure is now misrouted into the budget path, and
the inner `rate_limit` query (the spare success) lets that path complete and produce the exact
headline the check exists to rule out.

### File ran to completion — the trailing summary line

```
2 of 198 FAILING.
```

`M` is 198, unchanged from every unmutated run in this cycle and from cycle 1/2's baseline. The
file printed its full trailing summary — not a crash, not a partial run.

### Every other check that also reddened, named, with justification

```
FAIL  run_gh: unrelated failure message preserves the original gh text
        msg='GraphQL budget exhausted: 5000 of 5000 points used, resets at 2025-08-19T10:40:00Z — this is the GraphQL budget, not the REST budget — REST currently sits at 42 of 5000'
```

- **`run_gh: unrelated failure message preserves the original gh text`** — asserts
  `"could not resolve to a Repository" in msg2`. Under the mutation the message is replaced
  entirely by the budget headline, which does not contain that substring. Same root cause as the
  target check, same fixture, same misrouting — the direct sibling assertion of the one named in
  the dispatch, not a stray.

Total blast radius: **exactly two checks**, both at the one fixture the mutation targets. No other
check in the 198-check file reddened — confirmed by the `2 of 198 FAILING.` count and the grep for
`^FAIL ` lines above (only these two lines matched).

## Revert and clean re-run

`sha256sum factory_gh.py` after revert: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8`
— matches pre-mutation exactly. `git diff --stat -- factory_gh.py` shows only the pre-existing
T-04 cycle-1 net diff (170 insertions, the module's original T-04 addition); a targeted grep for
`RATE_LIMIT_MARKERS` in the diff shows the tuple's three original entries only — no fourth
`"could not resolve"` entry survives. `git status --porcelain -- factory_gh.py` shows only the
pre-existing `M`, no mutation artifact. Full suite re-run: `198/198 checks passed.`

## `task_verify` — run exactly, verbatim from plan.yaml T-04

Cross-checked against `plan.yaml` T-04's `verify:` field directly (`python3 -c "yaml.safe_load(...)"`)
— matches the dispatch's string verbatim:

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Captured exit status into a variable, counted `^FAIL ` lines separately
(`run-unit-tests.sh:51-54` can exit 2 with MISCONFIGURED before any test runs, printing no `FAIL`
line — exit status is the only thing that catches that):

```
EXIT=0
FAIL count: 0
```

`test-factory-gh.py`'s own line inside the full run: `198/198 checks passed.` / `PASS
test-factory-gh.py`. `task_verify: pass`.

## No live `gh` call

All runs drove `factory_gh.subprocess.run` through the recorder fake, per the hard constraint. No
`gh` binary invoked, `check-state.sh` not run, `gh_cost_log.py`/`test-gh-cost-log.py` not created.

## Assertion integrity

No assertion weakened, renamed or deleted. The only test changes: one spare `Result` queued (a
no-op under unmutated code, confirmed above) and one comment rewritten because its prior claim
("queues only ONE Result by deliberate design") became false the moment the spare was added.
