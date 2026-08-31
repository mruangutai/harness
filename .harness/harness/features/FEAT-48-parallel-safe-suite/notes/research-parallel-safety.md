# Research — the #1053 collision, identified

Measured 2026-08-31, main session, 12-core M3 Pro. This note exists because the plan that
became FEAT-48 originally carried an *unidentified* partner and an unbounded hunt for it.
The hunt is over. What follows is the answer and the evidence, so no later task has to
re-derive it.

partner: .claude/skills/harness/bin/test-check-domain.py
mechanism: overwrites the shared feature_schema.py in the bin directory for ~90ms per run

## The mechanism

`test-check-domain.py:1475-1490`, inside `run_schema()`, deliberately breaks the schema
checker to prove that a crashing checker DENIES a write rather than failing open. It does so
by rewriting the real module on disk:

```python
fs = os.path.join(os.path.dirname(os.path.realpath(__file__)), "feature_schema.py")
before = open(fs, "rb").read()
try:
    open(fs, "w").write(src[:j + 1] + '    raise ValueError("injected: checker is broken")\n' + src[j + 1:])
    r = fire(root, rel, content=illegal)      # <- the window
finally:
    with open(fs, "wb") as f:
        f.write(before)
```

`os.path.dirname(os.path.realpath(__file__))` is the **live bin directory**, not a copy and
not a tempdir. For the duration of one `fire()` call, every process on the machine that
imports `feature_schema` gets a module whose `problems_for_text` raises immediately.

## Why it was hard to see

The code is *careful*. It restores in a `finally`, then asserts the restoration is
byte-identical, and says so in a comment:

> *"Restored byte-identically, and the restore is ASSERTED — a probe that silently failed to
> restore would leave the tree mutated and every later case measuring the wrong file."*

That reasoning is correct and complete **for serial execution**. The invariant it protects is
*"the file is intact afterwards."* The invariant concurrency needs is *"no other process reads
this file while it is broken,"* and no amount of care inside one process can supply it. The
defect is not sloppiness; it is an invariant that stopped being sufficient when the execution
model changed.

## Evidence

Direct observation beats sampling here, because the window is ~0.5% of the run and assertion
sampling is badly underpowered — a 2-worker pairwise reproduction returned 0/4 red and proved
nothing either way.

Polling the shared file while `test-check-domain.py` ran once:

| | |
|---|---|
| polls | 1,032,849 |
| polls observing a BROKEN `feature_schema.py` | **5,105** |
| first observation | 8.68s into the run |
| restored byte-identically afterwards | True |

The hazard is therefore proven by observation, not inferred from a failure rate.

Corroborating capture from a 12-worker suite run, `test-gh-sync.py` failing:

```
FAIL  ship leaves a parent with no recorded origin open
GHSYNC_NONZERO rc=1 args=['ship', '.../FEAT-07-ship-noorigin']
  stderr='... feature_json_write.py, line 168, in _transform
           feature_schema.py, line 289, in problems_for_text
           ValueError: injected: checker is broken'
```

The victim carries the injector's own string in its traceback.

## Why test-gh-sync is the usual victim, and why it is not the only one

`gh-sync` imports `feature_schema` (via `feature_json_write`) on nearly every invocation, and
`test-gh-sync.py` invokes `gh-sync` several hundred times across 258 checks. It therefore has
by far the most exposure to a ~90ms window. It is not special otherwise: **any** concurrently
running test that imports `feature_schema`, directly or through a script it shells out to, is
exposed. Fixing this for `test-gh-sync` alone would be fixing the symptom.

This also explains an observation that misled the investigation twice: **which** assertion
fails varies between runs, because the victim is whichever call happens to land inside the
window. Two hypotheses were refuted on the way here — a shared `FAKE_LOG` (all three users
isolate it per-tempdir) and a worktree-vs-main-checkout differential (did not survive
repetition) — and one apparent reproduction was an artifact of the diagnostic harness itself
resolving `SYNC` relative to `/tmp`. Recorded so they are not re-walked.

## Fix direction (not yet implemented)

Do not mutate a shared source file. The child process is the only one that needs to see a
broken checker, so give it a broken one privately: write the faulty `feature_schema.py` into a
temporary directory and place that directory first on the child's `PYTHONPATH` for the single
`fire()` call. Nothing outside that child observes anything.

This removes the hazard rather than narrowing it. Narrowing — shrinking the window, retrying
the victim, ordering the tests — leaves a race that reappears under a different scheduler.

## What must NOT be accepted as proof of the fix

That the flake stops reproducing. It went quiet for 6 consecutive 8-worker runs in the middle
of this investigation while the defect was fully present and unfixed. A fix is proven by the
hazard being absent — re-run the poll above and observe zero broken reads — not by a green
suite.
