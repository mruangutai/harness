# Research — FEAT-31 plan2b: the three gaps, re-measured

BLUF: **one of the three dispatched gaps was real.** GAP 1 was already closed in the plan before I
started. GAP 3's premise misread the plan — the plan already adopts the probe's channel, and the open
item is the MATCHER, which I measured decisively. GAP 2 was real and is now T-10 + D-16.

The dispatch's description of `plan.yaml` was wrong in five checkable ways. Corrected below, because
the next reader must not re-derive from it.

## The plan's actual state (measured at 06:14, worktree FEAT-31, HEAD 6f651f1)

| dispatch claimed | measured |
|---|---|
| 1002 lines | 514 before my edits, 595 after |
| tasks T-01..T-14 | T-01..T-09 (now T-01..T-10) |
| decisions D-01..D-14 | D-01..D-15 (now D-16) |
| `uat:` block for SC-10 | **no `uat:` key exists** — not in the plan, not in any live plan, not in `templates/plan.yaml` |
| `resolved_at: 6f651f16c1e1...` | `resolved_at: 6f651f1` (short sha) |
| zero hits for `templates/harness.json` | 3 hits (lanes row, D-04, T-04) |

**The file was being written during my run.** 14350 bytes at 06:06 → 35016 at 06:08:40 → 35021 at
06:09:26, and at 06:09:26 it changed from `yaml.safe_load` **FAILING** (`mapping values are not
allowed here`, line 71 col 55, a `": "` inside D-04's plain scalar) to parsing. That is the FIRST
HALF being completed by another writer, which D-02 describes. It has been byte-stable since 06:09:26.
No transcript under `~/.claude/projects` shows an mtime in the last 6 minutes — including my own — so
transcript mtime is **not** a liveness signal on this machine. I edited only after 5 minutes of
stability, via `Edit` anchored on unique strings, so a colliding writer would have failed my edit
rather than silently lost content.

## GAP 1 — already closed. Nothing added.

- lanes row for `.claude/skills/harness/templates/harness.json` exists: `lane: main-session-direct`,
  `reason: resolves to NOBODY at 6f651f1; forced, not a carve-out choice`.
- **T-04** adds the key to the template, `execution_mode: main-session-direct`, with the correct
  `execution_reason` citing DEC-160.
- **T-05** already does exactly what the dispatch asked me to "check rather than assume" — it
  establishes whether `upgrade-config.py` propagates a new budgets key and proves the answer with
  `test-upgrade-config.py`. Its own lanes row exists too (`lane: team`, `harness-backend-dev`).

Adding a task here would have duplicated T-04. **Two notes for the operator, not acted on
(extend-only):**

1. The key name in force is `budgets.orchestrator_context_warn_tokens` (D-03, T-03, T-04). The
   dispatch called it `budgets.orchestrator_context_tokens`. The plan's name governs.
2. T-03/T-04's `verify` asserts the value `== 200000` but **does not assert a `_rationale` sibling.**
   The repo convention exists — `budgets._max_total_runs_rationale` and
   `_max_total_cycles_rationale` are both present in `.harness/harness.json`. If the operator wants
   the sibling, T-03/T-04's verify needs one clause added. I did not edit approved-shape tasks.

## GAP 2 — real. Delivered as T-10, and SC-15 is SPLIT (D-16).

**The finding that makes it automatable.** INV-17's shape check tests only heading PRESENCE:
`check-state.sh:509` is `HANDOFF_HEADINGS = ["## next", "## trust", "## dead ends", "## working set"]`
and `:614` is `miss = [h for h in HANDOFF_HEADINGS if h not in hl]`. So **a handoff with all four
headings and nothing under `## Next` passes the gate today.** That is precisely the mutation SC-15
names, and it is currently invisible. The assertion therefore goes red before the change — a real
mutation seam, not an exit-status assertion (D-08, D-10).

**What is NOT automatable.** SC-15's other half — "a fresh orchestrator … the successor's first
dispatch must match it" — needs a live orchestrator to produce a first dispatch. No test can spawn
one, and D-12 forbids reading `~/.claude/projects` because CI is ubuntu-latest. Routed to the
operator alongside SC-10, recorded as **D-16**, mirroring D-12's established pattern in this plan.

**Why D-16 and not a `uat:` block, contrary to my dispatch:** there is no `uat:` key in
`templates/plan.yaml`, in any of the 4 live plans, or in `check-state.sh`. Writing one would put a
narrowed criterion in a key **no validator reads** — invisible at exactly the gate that should catch
it. D-12 is how this plan already records a no-task UAT routing.

**T-10 needs no new registration.** `test-check-state.py` is already in `run-unit-tests.sh`'s
`INTEGRATION_SCRIPTS` and already listed in `test_kinds.integration.detect`. Reusing the gate's paired
test is also what DEC-174 am.4 requires. So the drift detector at `run-unit-tests.sh:41-51` and the qa
matrix both already see it, and no new `test-*.py` file is created.

## GAP 3 — the premise misread the plan, and the real open item is now settled on evidence

**There is no PreToolUse anywhere in the plan.** D-06 is about whether editing `run-unit-tests.sh` is
a team task — nothing to do with hooks. **D-13 already says PostToolUse + exit 2**, adopting probe
Finding 1 verbatim, and D-14 puts `settings.json` in the operator's hands. The dispatch's `Task|Agent`
/ `additionalContext` / `systemMessage` description matches no text in this file.

So the live question is the one D-13 itself names: **which matcher.** Measured across every
orchestrator sidecar and transcript on this machine:

```
total sidecars 1968 | harness-orchestrator 94 | with a matching .jsonl 89
transcripts issuing >=1 of Write|Edit|Bash:  89 of 89  (100%)
  Bash   5770 calls  in 89/89 transcripts
  Write   946 calls  in 86/89
  Read    597 calls  in 87/89
  Agent   415 calls  in 82/89
  Edit      3 calls  in  3/89
  Task      0 calls  in  0/89
Write|Edit|Bash subtotal: 6719 calls
```

Method: walked `~/.claude/projects` for `*.meta.json`, selected `agentType == harness-orchestrator`,
read the sibling `agent-<id>.jsonl`, counted `message.content[].type == "tool_use"` by `name`.

**Two consequences.**

1. Finding 1's self-named defect is **falsified.** `Write|Edit|Bash` is not "a matcher that never
   fires for an orchestrator" — it fires for 89 of 89, and `Bash` alone covers 89 of 89 at 5770
   calls. The already-registered `PostToolUse` matcher is sufficient; no new matcher is needed.
2. **`Task` is not a tool name on this machine.** 0 calls in 0 transcripts; the spawn tool is
   `Agent` (415 calls, 82/89). Any matcher written as `Task|Agent` has a dead half and would miss 7
   of 89 orchestrators entirely. If that string is anywhere in the operator's notes, it is wrong.

Per the dispatch I edited **nothing** in D-13 or D-14. The channel is returned as a blocking question
with the count attached.

## The four SCs still with no task — the reason this plan is not approvable yet

D-02 assigns the second half to "a second planning run": SC-07, SC-09, SC-13, SC-14, SC-15. I was
dispatched for SC-15 only and delivered it. **SC-07, SC-09, SC-13 and SC-14 remain untasked.** Each
needs a mechanism choice that is D-NN grade and is not mine to invent unbriefed (the hook script's
filename and language; where the handoff writer lives; whether INV-17's mid-phase stem lands in the
same edit as T-10's empty-body check). D-02's claim that "decisions are already complete for BOTH
halves" is falsified by D-16 having been necessary.

## Route checker — verbatim

Tree mode, `CLAUDE_PROJECT_DIR` set to the worktree root, exit 0:

```
0 violation(s) across 4 plan(s)
examined 30 feature dir(s); 26 skipped as shipped
```

FEAT-31's own block is all `OK` for T-01..T-09 plus, for my addition:

```
DEVIATION T-10 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/test-check-state.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
```

That DEVIATION is the expected DEC-174 shape and T-10's `execution_reason` predicts it. **The
dispatch's predicted DEVIATIONs for T-06 and T-11 did not occur in FEAT-31** — T-06 is a team task on
granted paths and T-11 does not exist. The `DEVIATION T-06` line in tree mode belongs to a different
feature's plan.

## Open questions

- **Q1 (blocking)** — SC-13's delivery channel and matcher. Evidence above says register on the
  existing `PostToolUse` `Write|Edit|Bash`; do not write `Task`.
- **Q2 (blocking)** — SC-01's `verify: automated evidence: integration` versus "against a live
  orchestrator". D-09 already split it; the operator's word is needed on whether that split stands.
- **Q3 (blocking)** — SC-15 narrowed to two halves by D-16.
- **Q4 (blocking)** — SC-07, SC-09, SC-13, SC-14 have no tasks.
- **Q5 (non-blocking)** — the `_rationale` sibling for the new budgets key.
- **Q6 (non-blocking)** — a second writer had `plan.yaml` invalid YAML for at least 46 seconds
  mid-session. Nothing gates plan.yaml parseability at write time.
