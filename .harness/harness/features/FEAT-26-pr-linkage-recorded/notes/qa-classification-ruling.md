# The qa gate's classification for FEAT-26 — settled before the gate runs

Written by the main session, 2026-08-23. Raised as Q3 by T-04's eng lead, verified here.

## The ruling

**`touches_db_or_external` is YES for this feature's diff.** So the `api` row's conditional
fires and **`integration` is REQUIRED**, not just `unit`.

## Why, and why the obvious answer is wrong

`harness.json`'s matrix:

```
api  {"always": ["unit"], "when": [{"kind": "integration", "if": "touches_db_or_external"}]}
```

**The trap:** judged on T-04 alone, the honest answer is NO — `closes` makes no GitHub call at
all, and making no external call is the entire point of it. A reader classifying task by task
would answer NO in good faith.

**Classify on the DIFF, not on one task.** T-03's `_record_pr` shells out to
`gh pr list --repo <repo> --head <branch> --state merged`. That is a real external call, added
by this feature, in the same file pair. So the diff touches external.

## What a NO would have cost — measured, not argued

`run-unit-tests.sh` resolves two disjoint lists. Measured at this worktree:

| Test file | UNIT_SCRIPTS (19) | INTEGRATION_SCRIPTS (22) |
| --- | --- | --- |
| `test-gh-sync.py` | no | **YES** |
| `test-check-state.py` | no | **YES** |
| `test-validate-feature-json.py` | **YES** | no |

**A `unit`-only gate runs neither `test-gh-sync.py` nor `test-check-state.py`** — which is the
entire evidence for T-02, T-03, T-04 and T-05. **Four of the eight tasks would have passed a
satisfied gate having never been exercised.**

That is this repository's recurring defect one level up: not an assertion that cannot go red,
but a whole suite the gate never runs. A green matrix would have said nothing true.

## For qa

Run `--kind all`, or at minimum `unit` AND `integration`. And **do not run the full suite while
agents are in flight** — issue #741: `test-validate-digest.py`'s hook cases read the live claim
registry and report false failures. Confirm the registry is `{}` first.
