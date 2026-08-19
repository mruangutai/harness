# Receipt — harness-backend-dev — FEAT-29 T-04 (cycle 2)

## Scope of this cycle

Narrow: make the repository's own discriminator assertion in `test-factory-gh.py`
("run_gh: message carries the captured stderr", the check right after "run_gh: raises GhError
on non-zero exit", currently line 219) observably red under mutation 1, in-repo — not via the
scratchpad probe from cycle 1. No redesign, no new assertions added or removed.

## The fix

The blocker named in the dispatch: that fixture's `recorder` queued exactly one `Result`
(`Result(1, stdout="", stderr="permission denied\nmore detail")`), and mutation 1 (drop
`_looks_like_rate_limit` from `run_gh`'s detection guard, keeping only the `_is_rate_limit_query`
recursion guard) makes every non-zero exit take the budget path, which issues a SECOND
subprocess call (`gh api rate_limit`) the recorder was never built to survive.

Applied exactly the fix instructed — queue a second `Result` for that recorder — and, tracing the
same crash forward, found it recurs at two more single-Result recorders in the same file before
the target check's redness would otherwise even be visible in a full-suite run: `preflight`'s
"raises GhError telling the operator to run gh auth login" fixture, and `ensure_labels`'s
"stops at the failing label" fixture. Fixed both the same way (spare `Result`) so the suite could
run far enough to report what else reddens. No assertion was weakened, renamed or deleted in any
of the three — each spare `Result` is inert under unmutated code (confirmed below) and only
becomes reachable under the mutation.

Files touched, both already on the approved write list: `.claude/skills/harness/bin/factory_gh.py`
(mutation applied and reverted only, no net change), `.claude/skills/harness/bin/test-factory-gh.py`
(three recorders given a spare `Result` each, with an inline comment at each site explaining why).

## Unmutated confirmation (spare Results are inert)

`python3 .claude/skills/harness/bin/test-factory-gh.py` → `198/198 checks passed.` — same count
as cycle 1's GREEN, before and after adding the three spare `Result`s. Confirms the spares change
no unmutated-path behavior: `recorder`'s `fake_run` only raises when `next(it)` runs out, so an
unconsumed queued item is a no-op.

## Mutation 1 — applied, full suite run, reverted

Applied (`factory_gh.py`, `run_gh`'s non-zero-exit branch):

```
-        if not _is_rate_limit_query(list(args)) and _looks_like_rate_limit(r.stdout, r.stderr):
+        if not _is_rate_limit_query(list(args)):
```

`sha256sum factory_gh.py` before mutation: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8`.

### The in-repo discriminator check — exact FAIL line

```
FAIL  run_gh: message carries the captured stderr
        exc=gh reported a rate limit and the budget could not be read: issue list — the original gh failure is preserved as detail — re-run after checking gh auth status and network access
```

This is the repository's own assertion (`test-factory-gh.py`, in the "non-zero exit carries
stderr" section), not a reimplementation. It reddens because the mutant genuinely changed
`run_gh`'s behavior: an ordinary `"permission denied"` failure is now misrouted into the budget
path (my queued second `Result` — itself a non-zero exit — makes the inner `rate_limit` query
fail too, so the outer message becomes "gh reported a rate limit and the budget could not be
read", which does not contain `"permission denied"`).

### Every other check that also reddened, and why each is legitimate

```
FAIL  ensure_labels: stops at the failing label, does not run the remaining ones
        calls=[... 3 entries ...]
FAIL  ensure_labels: each call uses --force
```

- **`ensure_labels: stops at the failing label...`** (asserts `len(calls) == 2`) — under the
  mutation, the failing label's call is misrouted into the budget path, which issues one extra
  `gh api rate_limit` call that also lands in the shared `calls` list (the same `recorder`
  instance records every `subprocess.run` invocation, not just the loop's own). `len(calls)`
  becomes 3, not a fixture leak — the assertion is about exactly the behavior the mutation
  changed (an extra, unintended call now happens).
- **`ensure_labels: each call uses --force`** — the leaked `["api", "rate_limit"]` call has no
  `--force` flag (it isn't a label-create call at all), so `all(...)` over the now-3-entry
  `calls` list is legitimately False. Same root cause as above: the mutation makes a call that
  doesn't belong to this loop's contract, so a check enumerating "every call in `calls`" catches
  it correctly.

### Stopped here: a further, unpatched crash

Continuing the same full-suite run, `ensure_labels: passes repo verbatim` (line 335,
`c["argv"].index("--repo")` inside a generator expression with no `"--repo" in c["argv"]` guard)
raises a bare `ValueError`, not a clean check redness — the leaked `rate_limit` call's argv has no
`--repo` at all. This is the same inherent-blast-radius pattern (my earlier receipt and this
dispatch both name it: "every non-zero exit in the module routes through the budget path"), but
fixing it — and, by the same logic, every other `run_gh`-backed fixture later in this ~1700-line
file that could collide with an unguarded extra call — is not "queue a second Result for the
named recorder." It is rewriting fixture robustness across the file, which is out of this
narrow-scope cycle and was not asked for. Did not attempt it. The dispatch itself already
conceded the blast radius is inherent and unsatisfiable to contain to a single check; a further,
unrelated crash later in the file is that same concession playing out again, not evidence the
fix above is incomplete.

## Revert and clean re-run

`sha256sum factory_gh.py` after revert: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8`
— matches pre-mutation exactly (`diff` against the pre-mutation on-disk copy: identical).
`git status --porcelain` on `factory_gh.py` shows only the pre-existing T-04 cycle-1 net diff
(`M`), no mutation artifact. Full suite re-run: `198/198 checks passed.`

## `task_verify` — run exactly, verbatim from plan.yaml T-04

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Captured exit status into a variable, counted `^FAIL ` lines separately (`run-unit-tests.sh:51-54`
can exit 2 with MISCONFIGURED before any test runs, printing no `FAIL` line — exit status is the
only thing that catches that):

```
EXIT=0
FAIL count: 0
```

Tail: `19/19 cases passed.` / `PASS test-inject-expertise.py`. `task_verify: pass`.

## No live `gh` call

All runs drove `factory_gh.subprocess.run` through the recorder fake, per the hard constraint.
No `gh` binary invoked, `check-state.sh` not run, `gh_cost_log.py`/`test-gh-cost-log.py` not
created.
