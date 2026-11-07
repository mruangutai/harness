# omp_session_accessor — live run receipt (validate Q-1), 2026-11-07

Locally-run kind `omp_session_accessor` (`tests/manual/probe-omp-session-accessor.py`) was touched by
FEAT-71 (extension moved byte-identical to `tests/manual/probe-session-accessors.ts`). Run live on
this host: omp/18.18.0 at `/Users/molchairuangutai/.bun/bin/omp`, model anthropic/claude-sonnet-5.

| Checkout | Command | Result |
|---|---|---|
| FEAT-71 worktree (tree = review_sha 3e6add2a for these paths) | `python3 tests/manual/probe-omp-session-accessor.py` | 3/4: case1 x2 PASS, case2 PASS, **case3 FAIL** — "a subagent session was observed with getContextUsage undefined" (sessions `pd8h`, `kimb`) |
| baseline 4a05030d (old evidence path) | same | **identical**: 3/4, case3 FAIL (sessions `o5qn`, `swpp`) |

Raw observations of the baseline run (`$TMPDIR/feat44-accessor-772cj893/out.jsonl`):

| session | getContextUsage defined | getSessionFile |
|---|---|---|
| o5qn (main) | true | `…/sessions/2026-11-07T15-21-52-837Z_01a1b69a-….jsonl` (flat) |
| swpp (subagent) | true | `…/sessions/2026-11-07T15-21-52-837Z_01a1b69a-…/YouthfulTern.jsonl` (nested, its own) |

Verdict: the relocation changed nothing (same failure on baseline). The property the live hook
depends on (`.omp/extensions/harness-hooks.ts` `SESSION_FILE_ACCESSOR`) holds — `getSessionFile`
resolves in the subagent to its OWN nested transcript and in the main session to a flat one. The
probe's case3 fails because its premise is stale: it identifies "the subagent" as the session where
`getContextUsage()` is undefined, and omp 18.18.0 defines it in subagent sessions too. Pre-existing
probe defect, outside FEAT-71's scope; proposed as backlog (identify the subagent by nested
session-file shape instead of the usage accessor).
