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

Put back the measurement DEC-159 assumes exists, and make it honest. The operator can ask what an
orchestrator's context is **while it is still running**, get a figure that refuses rather than
guesses, be warned before compaction rather than after, and tell a compliant per-phase orchestrator
from one that has been resumed past the seam. Nothing here re-opens cost accounting: DEC-178 removed
money, and this measures context only.

## Requirements

- REQ-01: The operator can read a named running orchestrator's current and peak context size with one
  command, without hand-parsing transcript JSONL.
- REQ-02: The reading is checkable. Where the underlying record cannot support a figure, the tool says
  so and names the record it distrusts, instead of reporting the number.
- REQ-03: The operator is warned while there is still room to act, against a threshold that lives in
  `.harness/harness.json` `budgets` rather than in code.
- REQ-04: The operator can tell, per feature and from disk, an orchestrator that ended at its phase
  seam from one that was resumed past it.
- REQ-05: The reading works for an orchestrator running inside a worktree, not only one running in the
  primary checkout.
- REQ-06: Wherever the figure is reported, what the instrument cannot see is reported beside it.
- REQ-07: An orchestrator the tool cannot measure is reported as unmeasured, naming the file that
  defeated it. It is never silently omitted from the watch.

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
- SC-07: **BLOCKED — needs the operator's decision before this brief is signed. Do not plan against
  it as written.** The criterion assumed `feature.json` `runs` records which orchestrator ran a run.
  It does not: `feature-schema.json` closes each `runs` item to exactly `id`, `squad` and `verdict`
  with `additionalProperties: false`, so no field links a run to an agent and nothing on disk can
  detect a seam crossing. The criterion also had no ground truth — DEC-159 sets no numeric bound on
  its sanctioned fix-loop exception, so "was FEAT-29 compliant" has no rule to test against until
  SC-09 writes one. Either REQ-04 gets a schema change under DEC-191, or REQ-04 narrows to what the
  existing record can answer. Both are the operator's call.
  verify: pending operator decision
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
- SC-10: The operator can run the command, read the answer, and act on it without asking what a
  number means.
  verify: uat
- SC-11: Against a fixture directory holding four sidecars — one complete, one with `agentType` but
  no `toolUseId`, one that is not valid JSON, and one whose `.jsonl` is missing — the tool reports
  four orchestrators, two of them as unmeasured with the offending path named, and exits non-zero.
  Deleting the unmeasured branch must make this test fail, and the test asserts that the total row
  count still equals the number of sidecars on disk, so a silent drop cannot pass.
  verify: automated      evidence: unit

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
  non-exhaustive. The harness plans this feature but does not execute the change that makes
  `check-state.sh` read the new invariant. A squad may write the module the gate calls; the cutover is
  main-session-direct, and SC-07's task must be declared that way at plan time under DEC-179.
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
