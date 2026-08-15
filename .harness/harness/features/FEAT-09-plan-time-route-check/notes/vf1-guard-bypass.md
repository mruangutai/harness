# VF-1 — an environment variable silently disables the write guard

**Status: BLOCKING. Found by the four-wide panel at `review_sha 4918d06`, reproduced independently
by the orchestrator. The fix is one line plus one test case, and it is a DECLARED MAIN-SESSION
STEP that no agent in this feature may perform or dispatch.**

## What happens if this ships

| | Outcome |
|---|---|
| **With the fix** | The guard behaves as documented. One line, one new test case. |
| **Without it** | Any agent whose environment carries `HARNESS_RESOLVE_PATH` can write **any** path. Exit 0, no stderr, nothing logged. An audit afterwards cannot distinguish "the guard permitted this" from "the guard was off." |

This is the `PreToolUse` guard that decides which agent may write which path — the authorization
boundary of the whole org. It is not a cosmetic defect.

## The mechanism — read, then measured

- `check-domain.sh:38` exports `HARNESS_RESOLVE_PATH` inside the `--resolve` branch.
- The `else` branch at `:39-41` — the hook path — **never unsets it**.
- `:133-134` selects resolve mode on `os.environ.get(...) is not None`, so even an **empty string**
  qualifies.
- `:202` exits before enforcement begins at `:204`.

So mode is chosen by the *environment*, not by argv — while the approved criterion is written in
argv terms.

## The measurement

Payload **files**, never inline — an inline escaped-quote payload yields a false exit 0 that looks
like a regression, and that measurement error has already burned time on this feature. The same
payload was used all three times: `harness-documentor` writing `.claude/skills/harness/bin/evil.py`.

| Environment | Exit | Output |
|---|---|---|
| clean (`env -u HARNESS_RESOLVE_PATH`) | **2** | `BLOCKED — harness-documentor may not write ...` |
| `HARNESS_RESOLVE_PATH=.harness/harness.json` | **0** | `harness-dev-ops` |
| `HARNESS_RESOLVE_PATH=` (empty string) | **0** | `NOBODY` |

## Why it gates, when security graded it `med`

The validator lead overruled security's `med`, and that is correct — but the decisive reason is
narrower than reachability.

`BRIEF.md:48-49` states **SC-04** in argv terms: *"with a Write payload on stdin and no `--resolve`
in argv, an out-of-domain write still exits 2."* Row two above is exactly that shape, and it exits
0. **SC-04 is false as written, not merely under-tested.**

Existing cases (g)/(h) at `test-check-domain.py:459-469` pass today **only because the environment
happens to be clean.** They assert the right thing and cannot see this.

**No single reviewer could have produced this finding.** Security found the mechanism without
checking it against SC-04; code verified SC-04 correctly, under a clean environment. The defect
lived in the *union* of the scopes. This is the standing no-pre-emptive-skips ruling being
vindicated rather than merely obeyed.

## The fix, as specified by the panel

1. Add `unset HARNESS_RESOLVE_PATH` to the **else** branch at `check-domain.sh:39-41`.
2. **Do NOT restructure to branch on argv.** `:105` already consumes `sys.argv[2]` as `argv_agent`,
   so branching on argv touches the hook path's identity contract on a DEC-174 file, and would
   drift from the mechanism DEC-179 documents.
3. Add a `test-check-domain.py` case that sets `HARNESS_RESOLVE_PATH` **explicitly in the subprocess
   environment** and asserts an out-of-domain Write payload still exits 2.

## Why it must go to the main session — the feature's own thesis, applied to itself

Measured, not inferred:

- `check-domain.sh --resolve .claude/skills/harness/bin/check-domain.sh` returns
  `harness-backend-dev` and `harness-dev-ops`. **The manifest grants it.**
- But **DEC-174** forbids dispatching a change to `check-domain.sh` through a team run whose gates
  are the thing being changed. `PLAN.md` T-01 already carries
  `execution_mode: main-session-direct` for this exact file.
- The domain hook separately **BLOCKS** `harness-orchestrator` from writing it.

So the orchestrator may neither perform this fix nor delegate it. It is precisely the `DEVIATION`
shape `check-plan-routes.py` was built to surface: a path the manifest grants, that policy
nonetheless routes to the main-session lane.

## Not a re-plan

SC-04 is approved and **achievable** — the one-line fix makes it true. That is approved-but-unmet,
which is a fix cycle, not a criterion that cannot be met as written. pm does not need to re-plan.
