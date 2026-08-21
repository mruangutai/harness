# BRIEF — FEAT-31 Orchestrator context watch

## Problem

**The instrument that watched this already existed and was deleted.** DEC-148 measured the dominant
cost term as context length × turn count, and built two halves against it: a **context watchdog** in
`cost-report.py`, flagging any agent whose average cache-read per turn crossed a 200k threshold, and
a **relay rule** in the playbook. DEC-159 hardened the relay half into policy — one phase per
orchestrator, ending at the seam is normal termination, the successor reads `notes/handoff-<phase>.md`
— and closed with a sentence that is now false: *"the watchdog remains the post-hoc audit."*
DEC-178 removed cost tracking entirely, and the watchdog went with `cost-report.py`. The index row
for DEC-148 already records this: *"DEC-178 dropped the watchdog with the meter."* The threshold was
never a config key — FEAT-08's own handoff note records it hardcoded at `cost-report.py:338`
(`notes/handoff-plan.md:26`). So the policy that replaced the measurement is the only thing left, and
nothing measures whether it is followed.

**What that costs, measured 2026-08-20 over this project's subagent transcripts.** 76 orchestrator
transcripts inside the 30-day retention window (`log_retention_days: 30`, oldest subagent file
2026-07-25). Two columns, because the obvious way to compute this is wrong — see below:

```
                        naive        corrected
median peak           243,080          136,406
peak > 200k              48/76            28/76
peak > 400k              24/76            10/76
largest peak        1,497,025          750,837   docs-migration planner, 992 entries
FEAT-29's orchestrator 696,472          696,472   1,046 entries, monotonic, peak == last
```

**The naive method is wrong on all 76 transcripts, and I published it before checking.** Summing a
request's top-level `input_tokens` + `cache_read_input_tokens` + `cache_creation_input_tokens` looks
like the prompt size. It is not. Where a request makes nested sub-calls, Claude Code records them in
`usage.iterations` and the **top-level field is their sum**. Confirmed exactly on the docs-migration
planner, transcript line 990: three iterations reading 746,878 + 0 + 747,992 = **1,494,870**, which is
that request's top-level `cache_read_input_tokens` to the token. So 1,497,025 was never a 1.5M prompt
and never a double-count bug — it is the correct total of tokens READ across three sub-calls, and I
read it as the size of one context. Every one of the 76 transcripts carries `iterations`, so the naive
column overstates the median by 78%.

**This weakens the case and the corrected numbers are the ones that count.** The corrected median,
136,406, sits BELOW the 200k threshold DEC-148 chose — the claim that the median already crosses it,
which this brief made in an earlier draft, is false. What survives: 28 of 76 orchestrators peak above
that threshold, 10 above twice it, the largest at 750,837, and FEAT-29's at 696,472 with peak equal to
last and no plateau. The problem is real at the top of the distribution and not at its middle.

**The measurement defect is the more important finding.** Context size and tokens read are two
quantities, one field carries both depending on shape, and the wrong one is the one that looks
obvious. An instrument that confuses them reports 1.5M for a 750k context — and would report it
green, in a table, as evidence.

**Why it was not caught.** Cycles and runs are the only counters left, and neither is a proxy for
context. FEAT-29 sat at 10 of 10 cycles and 17 of 20 runs — nominally inside both — while its
orchestrator was resumed six times against DEC-159's one-phase rule, with nothing reading either
fact.

## Goal

Put back the measurement DEC-159 assumes exists, make it honest, and close the loop it leaves open.
The operator can ask what an orchestrator's context is while it is still running. The orchestrator
itself is told, at the moment it crosses the threshold, in its own context. It then finds the nearest
seam, writes the state a successor needs, and ends — and a fresh orchestrator picks up from disk with
a clean context and loses nothing. Nothing here re-opens cost accounting: DEC-178 removed money, and
this measures context only.

**Two operator rulings, 2026-08-20, fix the shape of the mechanism.**

**The warning advises; it does not refuse.** A hook that blocks tool calls at the threshold would
guarantee the relay, and would also trap an orchestrator whose handoff writes fell outside the
allow-list. The warning is delivered and the orchestrator decides. The stated risk accepted: this is
how DEC-148's watchdog died — a signal nobody was obliged to read. What makes this different is
delivery, not obligation. DEC-148's figure sat in a report nobody opened; this one arrives inside the
agent's own context at the moment it matters, and DEC-159's seam rule is already an instruction
orchestrators follow — FEAT-30's planner ended at its own plan seam unprompted at a 407,424 peak.

**A mid-phase crossing gets a handoff, not a hold.** DEC-159 already sanctions the mid-phase relay as
its bounded escape. Waiting for the real seam is what produced FEAT-29: an orchestrator deep in a fix
loop, growing past every threshold, with the next seam far ahead.

## Requirements

- REQ-01: The operator can read a named running orchestrator's current and peak context size with one
  command, without hand-parsing transcript JSONL.
- REQ-02: The reading is checkable. Where the underlying record cannot support a figure, the tool says
  so and names the record it distrusts, instead of reporting the number.
- REQ-03: The operator is warned while there is still room to act, against a threshold that lives in
  `.harness/harness.json` `budgets` rather than in code.
- REQ-04: The operator can tell, per feature and from disk, which orchestrator ran each run, so an
  orchestrator that ended at its phase seam is distinguishable from one carried past it. **Ruled
  2026-08-20: `feature.json`'s `runs` items gain an agent identifier under DEC-191, and NO existing
  `feature.json` is migrated — the field starts from this feature forward.**
- REQ-05: The reading works for an orchestrator running inside a worktree, not only one running in the
  primary checkout.
- REQ-06: Wherever the figure is reported, what the instrument cannot see is reported beside it.
- REQ-07: An orchestrator the tool cannot measure is reported as unmeasured, naming the file that
  defeated it. It is never silently omitted from the watch.
- REQ-08: An orchestrator that crosses the threshold is told so in its own context, while it is
  running, without the operator asking.
- REQ-09: A warned orchestrator determines the nearest seam and writes the state a successor needs
  before it ends. Where no seam is reachable, it writes a mid-phase handoff rather than continuing.
- REQ-10: A fresh orchestrator resumes from those files alone, with no access to its predecessor's
  context, and the work it does next is the work the predecessor had decided on.

## Success Criteria

- SC-01: Run against a live orchestrator, the tool prints its current and peak context and its entry
  count. The peak matches, to the token, an independent computation that resolves `usage.iterations`
  per iteration rather than reading the top-level sum — the corrected method, not the naive one. The
  check must not import the tool's own arithmetic; sharing that code would make the criterion compare
  a function to itself.
  verify: automated      evidence: integration
- SC-02: The tool reports the largest single prompt, never a sum across sub-calls. Against a fixture
  copied from the docs-migration planner's transcript line 990 — top-level `cache_read_input_tokens`
  1,494,870 over `usage.iterations` of 746,878, 0 and 747,992 — the tool must report 747,992 for that
  request and must not report 1,494,870. Removing the per-iteration resolution must make this test
  fail, and the fixture must keep the two values distinct so it cannot pass by coincidence.
  verify: automated      evidence: unit
- SC-03: The tool selects orchestrators without being told which agents they are, by reading
  `agentType` from `subagents/agent-<id>.meta.json`; a fixture directory holding one
  `harness-orchestrator` and two other agent types returns exactly one row.
  verify: automated      evidence: unit
- SC-04: With the threshold set below a fixture's peak the tool warns and exits non-zero; set above
  it, the same fixture is silent and exits zero. Both runs read the threshold from
  `.harness/harness.json`, and deleting the key produces a stated default rather than a crash.
  verify: automated      evidence: unit
- SC-05: The warning is demonstrated to fail first: the test asserts the warning is absent before the
  threshold check exists, then present after.
  verify: automated      evidence: unit
- SC-06: For a cwd inside `.claude/worktrees/harness/<id>/`, the tool resolves the transcript
  directory for that cwd rather than for `harness_root`. Asserted against the real existing directory
  `-Users-molchairuangutai-GitHub-harness--claude-worktrees-fix-harness-tooling-backlog`.
  verify: automated      evidence: integration
- SC-07: `feature.json`'s `runs` items carry an agent identifier, and **the write path refuses a run
  entry that omits it** — enforced where DEC-191's closed key set is already enforced, on
  `check-domain.sh`'s `feature.json` write route. This is what makes "from here on out" mean
  something: absence can then only mean the entry predates the change, so the read-side check skips
  it safely instead of confusing an old run with a failure to record. No existing `feature.json` is
  migrated (operator ruling, 2026-08-20). Tested both ways: a run entry without the field is refused
  at write, and a `feature.json` whose existing entries lack it still validates.
  verify: automated      evidence: unit
- SC-08: The tool's own output carries its blind spots, and the list is derived rather than asserted:
  at minimum, that it cannot see a context that has already compacted, that it reads a 30-day
  retention window, and that a figure it prints is the prompt size the API recorded, not the window
  limit. Graded by reading `git show <review_sha>:<path>` on the shipped file, not the working tree.
  verify: inspection
- SC-09: DEC-159 states what to do when a phase is genuinely mid-flight at the threshold — the case
  its per-phase seam does not cover. Written by **editing DEC-159 in place**, including the clause
  that says the watchdog still audits. No `am.N` block, no parallel rule elsewhere: one statement,
  one home. Graded by reading `git show <review_sha>:.harness/harness/docs/DECISIONS.md` and
  confirming the entry reads as a single current rule.
  verify: inspection
- SC-10: **The UAT, stated as steps, because "the operator can run the command" names no command
  and cannot fail.** With at least one orchestrator ALIVE — measuring a finished one proves nothing
  about the case that matters — the operator runs the tool with no argument and then with that
  orchestrator named, and from the output alone can answer all four of:
    1. which orchestrators are running, and which feature each is on;
    2. what each one's context is NOW and what it PEAKED at;
    3. how far each is from the threshold, without the operator doing arithmetic;
    4. whether any orchestrator could not be measured, and which file defeated it (REQ-07).
  It fails if any figure has to be divided, subtracted or compared by hand to be useful, if a
  running orchestrator is missing from the no-argument output, or if the operator has to ask what a
  number means. The invocation is a `python3 .claude/skills/harness/bin/<name>.py` call taking an
  optional agent id — the plan names the file; this criterion does not, because a filename is a
  decision and the brief does not make those.
  verify: uat
- SC-11: **This feature DEFINES NO FILE FORMAT AND WRITES NO SIDECAR.** `agent-<id>.meta.json` is
  Claude Code's own file, written by Claude Code at spawn into
  `~/.claude/projects/<slug>/<session-id>/subagents/` — a persistent user directory, NOT a temp one.
  The tool only ever READS it.
  What this criterion builds is a **throwaway fixture directory under `tempfile.mkdtemp()`**,
  hand-written in that same shape, because the malformed cases below cannot be obtained any other
  way: Claude Code does not emit invalid JSON on request. The fixture is a test input with a
  one-run lifetime; it is not a new artifact, not a format this repository owns, and nothing under
  `.harness/` or `.claude/skills/` gains a file from it.
  The four fixture cases: one complete, one with `agentType` but no `toolUseId`, one that is not
  valid JSON, and one whose `.jsonl` is missing. The tool must report four orchestrators, two of
  them as unmeasured with the offending path named, and exit non-zero. Deleting the unmeasured
  branch must make this test fail, and the test asserts the total row count equals the number of
  sidecar files in the fixture, so a silent drop cannot pass.
  verify: automated      evidence: unit

- SC-13: An orchestrator whose context crosses the threshold receives the warning in its own context,
  and the warning names its current size, the threshold, and the nearest seam. Demonstrated on a
  fixture that crosses and one that does not: the crossing one warns, the other is silent. Removing
  the threshold comparison must make the crossing fixture stop warning.
  verify: automated      evidence: integration
- SC-14: A warned orchestrator's successor is handed `notes/handoff-<stem>.md` carrying DEC-159's four
  required sections within the 60-line cap, and INV-17 accepts it. Where the crossing is mid-phase and
  the stem is not one of `plan`, `build` or `validate`, INV-17 accepts that shape too — asserted by a
  test that fails before INV-17's seam table learns the mid-phase stem.
  verify: automated      evidence: integration
- SC-15: A fresh orchestrator given only the feature directory does the work the predecessor had
  decided on. Graded against the predecessor's `## Next`: the successor's first dispatch must match
  it. This is the criterion that proves the relay preserved intent rather than merely producing a
  file, so it must be shown to fail when the handoff's `## Next` is emptied.
  verify: automated      evidence: integration

## Verification gaps

None material to this feature. **Five** kinds carry `cmd: null` in `.harness/harness.json`
`test_kinds` — `functional`, `component`, `ui`, `eval` and `typecheck` — and no criterion above rests
on any of them. This feature
touches a Python script under `.claude/skills/harness/bin/`, a `budgets` key, `check-state.sh`, and a
decision entry; `unit` and `integration` both have real runners and cover all of it. This section says
so explicitly because DEC-163 makes a null kind a soft skip: an SC resting on one can never be met and
never fails loudly, so the absence of that case is worth stating rather than leaving inferred.

## Constraints

**BLOCKS:**

- **`subagents/agent-<id>.meta.json` is a Claude Code internal file with no contract.** No decision
  in this repository governs it and no harness code writes it. Across the 1,406 sidecars on this machine at 2026-08-20 08:30 (the count grows with every spawn)
  its keys fall into **10 distinct shapes**: `agentType`, `description` and `spawnDepth` appear in all
  ten, `toolUseId` in nine, and `parentAgentId`, `worktreePath`, `model`, `isFork`, `name`,
  `stoppedByUser`, `worktreeCleanlyRemoved` and `spawnedWithWorktree` each appear in some and not
  others. **Nothing this feature does can make it stable** — the constraint is that the tool may
  depend on only the three universal keys and must treat every other as optional. How it behaves when
  the file defeats it is REQ-07, not a constraint.

- **DEC-174** (am.1-am.4) — `check-state.sh` is named enforcement layer, and the list is
  non-exhaustive. The harness plans this feature but does not execute the change. **The relay half
  widens this reach considerably:** SC-07 changes `check-domain.sh`'s write route, SC-13 needs a hook
  registration in `settings.json`, and SC-14 changes INV-17's seam table in `check-state.sh`. That is
  three enforcement-layer surfaces, all main-session-direct, all declared as such at plan time under
  DEC-179. A squad may write the modules those gates call; every cutover is the operator's hands. This
  is the single largest cost of the relay scope and it is not negotiable under DEC-174.
- **DEC-178** — cost tracking is removed entirely: meter, budgets, invariant and reporting surfaces.
  This feature may not reintroduce a money figure, a per-model rate table, or a spend budget. Context
  tokens are not currency.
- **DEC-188** — a decision the tree flatly contradicts is STRUCK, never marked, and striking needs
  the operator's word. **Ruled 2026-08-20: DEC-159 is NOT struck.** Its core — the per-phase seam and
  the handoff note — holds and is the basis of this feature. Only the clause *"the watchdog remains
  the post-hoc audit"* is false, and it is corrected in place under SC-09. This is the softer case
  DEC-188 leaves to amendment, not the flat contradiction it strikes.
- **DEC-150** — `DECISIONS.md` is never read whole; state files have caps enforced at write.
- **DEC-90** — single-operator by design. No lock, no cross-machine case; the tool reads one
  machine's transcripts.

**SUPPLIES:**

- **DEC-159 is the basis of this feature, by the operator's ruling of 2026-08-20** — the per-phase
  seam, `notes/handoff-<phase>.md`, the four required sections and the 60-line cap, and INV-17 at
  `check-state.sh:462` which already enforces them. REQ-04 extends this mechanism; it does not invent
  one. The feature restores the measurement DEC-159 assumed and corrects the one clause that claims
  the measurement still exists.
- **DEC-191** — `feature.json`'s closed key set, eleven keys, `additionalProperties: false`. `runs` is
  where REQ-04's per-feature evidence already lives. Note that DEC-159's proposed `phase:` field does
  not exist in `feature-schema.json`; `status` carries the station instead.
- **DEC-148** — the 200k figure and the reasoning behind it. REQ-03's default starts there rather than
  from a fresh guess.
- **Claude Code's own per-agent sidecar, which the harness neither writes nor reads.** Each spawned
  agent gets `subagents/agent-<id>.jsonl` beside `subagents/agent-<id>.meta.json` under the session's
  project directory. The sidecar carries `agentType`, `description`, `spawnDepth` and `toolUseId`, so
  orchestrators are selectable without the harness recording anything. Verified live on 2026-08-20
  against the FEAT-30 planning orchestrator, `agent-aebb8688976e006c9`, reading 89,587 tokens at 87
  entries while it ran.
- **The sidecar already records the worktree**, which is REQ-05's cheapest path. 39 of those 1,406 sidecars
  on this machine carry `worktreePath` and `worktreeBranch`, and 38 of those also carry
  `spawnedWithWorktree`. Reading the recorded path beats deriving one from cwd.

**PREREQUISITE — SETTLED 2026-08-20, before planning. Evidence:
`notes/probe-hook-payload-identity.md`.**

- **The assumption this brief rested on was FALSE, and the mechanism survives anyway.** A probe
  captured one real `PreToolUse` payload from inside a subagent. `transcript_path` holds the
  **PARENT session's** transcript, not the subagent's, and `session_id` is the parent's id. Built as
  originally written, the hook would have measured the MAIN SESSION on every orchestrator tool call
  — a number that exists, grows, and is wrong.
- **The payload carries `agent_id`, which nobody had named.** For the probe agent that was
  `a169d08f65bcba077`, and `{session_id}/subagents/agent-{agent_id}.jsonl` exists. So the hook
  locates the calling agent's own transcript exactly, with no guessing and no race against
  concurrent orchestrators. The source is `session_id` + `agent_id`, **never** `transcript_path`.
  `agent_type` is in the payload too, so the orchestrator filter is free, and `cwd` is there, which
  is what REQ-05 needs once orchestrators run in worktrees.
- **`harness_yaml.py:479` is not a defect and must not be "fixed".** `_resolve_identity` returns the
  SESSION identity, which is correct for the bootstrap marker it serves. It was only wrong as
  evidence about agent identity, which is what this brief cited it for.
- The probe modified `bash-write-guard.sh` and reverted it. `test-bash-write-guard.py` reported
  `27/27` with the probe in place and again after the revert, and the file is clean in git.

**DISCLOSED, for the operator's call:**

- **Retention is settled, not open. Ruled 2026-08-20: nothing older than a week matters.** The tool
  reads live transcripts only. It writes no durable record of an orchestrator's peak, adds no key to
  `feature.json`, and answers only "what is this orchestrator at now, and what did it peak at during
  this run". The 30-day window is four times the horizon the operator asked for, so it is margin
  rather than a gap — but it is still a blind spot the output must name (SC-08), because the figure
  goes stale silently rather than erroring. The consequence accepted: the 76-transcript distribution
  measured for this brief is not reproducible after those files expire, and this brief is the only
  record of it.
- FEAT-30 moves orchestrators into worktrees, which changes the transcript directory per checkout.
  REQ-05 covers reading it. The two features touch the same surface and their order matters.

- **Ordering against the amendment fold (#615).** SC-09 edits DEC-159 in place and adds no `am.N`
  block, which is the convention #615 exists to establish. Either order works: if the fold runs
  first, SC-09 follows a rule already in force; if FEAT-31 runs first, DEC-159 is one entry the fold
  then finds already folded. No dependency, stated so nobody discovers it as a conflict.

## Approval

status: pending
