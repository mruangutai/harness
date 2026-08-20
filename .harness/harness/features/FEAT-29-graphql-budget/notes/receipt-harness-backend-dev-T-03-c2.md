# Receipt — harness-backend-dev — FEAT-29-graphql-budget T-03 c2 — SCOPE CHANGE (amendment 5)

## Verdict: complete, green, and the c1 open_question (Q1) is now resolved as a side effect

This is a re-open under approval amendment 5 (dated 2026-08-19, in `plan.yaml`
`approval.amendments[-1]`): REQ-03 and SC-05 amended so `gh_cost_log.py`'s recorder becomes
**opt-in, default OFF**. Not a defect fix — T-03's first pass (c1) was correct against the
original REQ-03 and is unchanged in that respect; this pass implements the operator's inversion
of the default.

**The stale `intent:` paragraph in T-03 ("defaulting to ON", "HARNESS_GH_COST_LOG=0 writes no
line") was NOT rewritten when amendment 5 was signed.** Per this dispatch's explicit instruction,
amendment 5's `what_changes` is treated as authoritative and the intent's default-ON paragraph
was NOT implemented. Whether `plan.yaml`'s `intent:` block should be rewritten to match is raised
as an open_question below, not edited by me.

## Files touched (exactly two source files, per the dispatch's scope)

- `.claude/skills/harness/bin/gh_cost_log.py` — `_enabled()` (line 47) flips from
  `os.environ.get("HARNESS_GH_COST_LOG", "1") != "0"` to
  `os.environ.get("HARNESS_GH_COST_LOG", "0") == "1"`: only an explicit `HARNESS_GH_COST_LOG=1`
  enables recording. Docstring and the function's own docstring rewritten to state the new
  default; the module docstring no longer implies always-on.
- `.claude/skills/harness/bin/test-gh-cost-log.py` — five existing blocks that relied on the
  default to record (`record()` keys/coverage-line block, failing-invocation block, `-f`/`-F`
  truncation block, `measured()`-raises block, `measured()`-recursion-guard block) now set
  `HARNESS_GH_COST_LOG=1` explicitly around the call, cleaned up in `finally`. Names and meanings
  of all their assertions are unchanged. Added a new SC-05 section (4 checks, two
  `tempfile.TemporaryDirectory()` blocks) proving the OFF state with the variable genuinely
  unset (`os.environ.pop(..., None)`, not merely `"0"`): both a successful (rc=0) and a FAILING
  (rc=1) invocation write no file and no line. Scoped to a redirected tmp root the same way
  every other case in the file is (`redirect()`, asserted to have taken effect first).

## TDD — RED then GREEN, both watched

1. Added the four new SC-05 checks only, production code still at the OLD default (ON). Ran
   `test-gh-cost-log.py` directly: **4 of 24 FAILING** — exactly the four new checks, all 20
   pre-existing checks still PASS, suite ran to completion (not an abort). RED confirmed.
2. Flipped `_enabled()`'s default and updated the five existing blocks to set the var explicitly.
   Ran again: **24/24 checks passed**. GREEN confirmed.

## Mutation proof (required by dispatch) — reddened a named check, not an abort

Hash before mutation: `b5d24cea70dcdf0eeadc097ae51faaea19f478fc8c82ad78f7f50e62ff198f5e`
(`sha256sum gh_cost_log.py`).

Mutated `_enabled()` to `return True  # MUTATION PROBE` (unconditionally enabled, ignoring the
env var). Ran `test-gh-cost-log.py`:

```
FAIL  HARNESS_GH_COST_LOG=0 writes no line at all — exists=True
FAIL  with HARNESS_GH_COST_LOG unset, a successful invocation creates no log file — exists=True
FAIL  with HARNESS_GH_COST_LOG unset, a successful invocation writes no line — lines=[...]
FAIL  with HARNESS_GH_COST_LOG unset, a FAILING invocation creates no log file — exists=True
FAIL  with HARNESS_GH_COST_LOG unset, a FAILING invocation writes no line — lines=[...]

5 of 24 FAILING.
```

Five checks reddened, not four — the pre-existing `HARNESS_GH_COST_LOG=0` case also reddened,
because that case's correctness depends on `_enabled()` actually reading the env var, and the
mutation removes that read entirely. This is a **named-check redness**, not an abort: the
trailing "N of M FAILING." line proves the suite ran to completion. Distinguishing this from
`test-factory-gh.py`'s abort-on-mutation property (backlog B-1, explicitly out of scope here) —
this file's mutation produced a clean partial-fail report, every unrelated check still ran and
still reported PASS.

Reverted (`return True  # MUTATION PROBE` replaced back with the real line). Hash after revert:
`b5d24cea70dcdf0eeadc097ae51faaea19f478fc8c82ad78f7f50e62ff198f5e` — matches. Re-ran the suite:
**24/24 checks passed**. Restore verified both by hash and by re-running GREEN.

## task_verify

`task: T-03`
Command (verbatim, cross-checked against `plan.yaml` T-03 line 265-266 — matches this dispatch's
quoted string exactly): `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`

Expected count set BEFORE running (per dispatch instruction): PASS count must go UP from the
baseline 160.

Result:
- Pre-edit baseline (measured live, this run, before any edit): exit 0, **160 PASS, 0 FAIL** —
  matches the dispatch's stated baseline exactly.
- Post-edit: exit 0, **164 PASS, 0 FAIL** (160 + 4 new SC-05 checks). PASS count went up as
  predicted. `task_verify: pass`.

`--kind integration`: exit 0, **90 PASS, 0 FAIL** — matches the dispatch's stated baseline
exactly (this differs from the c1 receipt's own integration baseline of 89/7 FAIL; those seven
pre-existing failures are gone as of this checkout state, unrelated to T-03, confirmed by the
dispatch's own stated expected baseline matching what I measured).

## The real proof — `.harness/logs/gh-cost-2026-08-19.jsonl` byte size, before and after

Recorded per dispatch instruction, immediately before and immediately after each suite run,
with the variable left genuinely UNSET (the normal invocation, no export anywhere in my shell):

| Point | Size |
|---|---|
| Before any edit (this session's first check) | 32739 bytes |
| After the PRE-EDIT baseline `--kind unit` run (old default, ON) | 39504 bytes — grew, confirming the old behavior live |
| Immediately before the POST-EDIT `--kind unit` run | 39504 bytes |
| Immediately after the POST-EDIT `--kind unit` run | 39504 bytes — **unchanged** |
| Immediately before the POST-EDIT `--kind integration` run | 39504 bytes |
| Immediately after the POST-EDIT `--kind integration` run | 39504 bytes — **unchanged** |

The file exists in the tree (pre-existing, not created by me) and its size is unchanged across
both post-edit suite runs — the expected evidence per the dispatch, not absence. Did not delete
or otherwise touch this file; it is main-session's domain (`.harness/logs/**`), consistent with
the LEAVE LIST.

## Not done / explicitly out of scope

- Did not rewrite T-03's stale `intent:` paragraph in `plan.yaml` — flagged as an open_question,
  not edited.
- Did not touch `check-state.sh`, `CLAUDE.md`, `.harness/notes/**`, `.harness/logs/**`,
  `factory_gh.py`, `gh-sync.py`, `run-unit-tests.sh`, or `test-factory-gh.py` — all on the LEAVE
  LIST, none needed touching for this scope change.
- Did not run `check-state.sh` and made no live `gh` call, per dispatch instruction.

## Open questions

- **Q1 (non-blocking).** T-03's `intent:` block in `plan.yaml` still reads "Make it opt-outable
  with an environment variable HARNESS_GH_COST_LOG set to 0, defaulting to ON" and lists
  "HARNESS_GH_COST_LOG=0 writes no line" as a required test case — both superseded by amendment
  5 but left unedited in the signed artifact. Per this dispatch's own instruction this is the
  operator's call, not mine, to decide whether to rewrite. Raising it so it does not silently
  persist as a source of confusion for whoever next reads T-03's intent without also reading the
  amendment.
