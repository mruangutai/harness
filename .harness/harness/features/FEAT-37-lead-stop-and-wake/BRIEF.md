# BRIEF — FEAT-37 lead stop-and-wake

> **This BRIEF supersedes the version written on 2026-08-24 against issue #831's stated cause.**
> That cause was an inference. Measurement replaced it (below), and the fix it implies is larger by
> one clause. Nothing of the earlier draft is preserved by default.

## Problem

A domain lead that has dispatched a member has nothing to do until that member returns, and it
invents activity instead of stopping. Observed live on 2026-08-24 during FEAT-34's build (#831):
`harness-product-lead` agent `a8f1c68d9a0d69f25` alternated one line of text and one filler
`Read`/`Grep` — *"Waiting on pm."*, *"Standing by for pm's return."* — for ~40 cycles across ~3.5
minutes (sidecar lines 35 to 186), stopping only when the member's real return arrived. An agent has
exactly two moves, end its turn or call a tool, and **a tool call keeps the turn alive**, so a lead
that believes it must wait has no mechanism for waiting. It burns tokens and wall-clock and drifts
toward the 600s no-progress watchdog that killed an orchestrator and its whole subtree in FEAT-35.

**The cause is measured, and it is not what #831 said it was.** #831 named the missing playbook rule
but reasoned about it from the code's silence; the measurement settles it and adds a second cause.

1. **The missing rule is necessary and sufficient.** The `a8f1c68d9a0d69f25` specimen carries the
   loop signature with **ZERO** occurrences of `returned with children in flight` — that lead never
   attempted to stop, so #551's `SubagentStop` refusal was not in that loop. `check-domain`-lane
   aside, `.claude/skills/harness-team/SKILL.md` goes straight from **d. Dispatch** (`:97` at
   `9165162`) to **e. Collect returns** (`:112`) with nothing between.
2. **A compounding cause the harness cannot edit.** The `Agent` tool's own result text — *"continue
   other work or respond to the user in the meantime"* — is what the transcript literally obeys, and
   it explains why the loop manufactures filler rather than idling. It appears nowhere in `.claude/`,
   `.harness/` or `docs/`: it is **platform-supplied**. **Removing the silence is therefore not
   enough; the rule must explicitly override the tool's nudge**, the way
   `.claude/skills/harness/SKILL.md:45-56` already does for the orchestrator.
3. **After this fix, the refusal fires — measured, not feared.** Every dispatch's first turn-end will
   meet a live child and be refused. The bound is **at most once per CONSECUTIVE STOP SEQUENCE; it
   re-fires on each wake while a child is still live** — proven in `agent-a89be3fd837d1b779` line 178
   (children: eng-lead `22:59:07.135172`, product-lead `22:59:28.731235`) versus line 392 (child: the
   SAME eng-lead `22:59:07.135172`); different child sets prove a distinct event, not replayed
   context. A lead told only "end your turn" and then refused for doing it will read the refusal as
   an instruction to stay — which is the exact loop this feature removes. **So the rule must carry an
   INOCULATION: the refusal is expected, the correct response is to stop again, and it can recur.**
   `harness/SKILL.md:50` does this for the orchestrator and demonstrably works.

**A knock-on that is not optional.** `DECISIONS.md:6701` (DEC-199) states *"so a stop refusal fires
at most once"* as fact, and the same falsified bound is repeated in the message an agent reads at the
moment of refusal (`inflight_registry.py:274`) and in the orchestrator's own playbook
(`harness/SKILL.md:53`). Under PRINCIPLES rule 15 — never falsify the record — this is corrected
here, whatever the operator rules on scope below.

## Goal

Give the lead tier the rule the orchestrator already has, in the one file all three leads preload —
a lead never waits for a member, it ends its turn, the member's completion wakes it, and a refusal on
that turn-end is expected and answered by stopping again. Record its measured reason where the org's
decisions live, correct the bound the record states falsely, and guard both with an assertion a
reword cannot silently defeat.

## Scope — #831 only, by ruling

`source_issues` is **`[831]`**. This feature fixes the loop and the record corrections rule 15
forces, and nothing else. `plan.yaml` carries six tasks, T-01 to T-06.

**The #811 block was struck, and the shape it was struck from was chosen on purpose.** The plan
originally isolated the #811 hook work as three contiguous tasks with nothing depending on them,
precisely so an unruled scope question could not hold up a fix whose evidence was already settled.
The operator then struck the block on measurement, not preference: specimen `a8f1c68d9a0d69f25`
carries the loop signature with **zero** occurrences of `returned with children in flight`, so that
lead never attempted to stop and #551's refusal was never in that loop. With the inoculation shipped,
#831 is complete and independently verifiable without touching the refusal at all. Recorded as D-07.

**#811 stays OPEN and returns to the backlog.** Its "what a fix has to preserve" section argues from
the once-only bound this feature falsifies, so the ticket needs its premise rewritten before anyone
works it. The operator does that himself; no task here spends effort on it.

## Requirements

- REQ-01: A domain lead with a member in flight ends its turn instead of occupying itself, and
  continues when the platform delivers the member's completion.
- REQ-02: The lead's playbook **explicitly overrides** the dispatch tool's own "continue other work
  in the meantime" instruction, rather than merely being silent about waiting.
- REQ-03: A lead whose turn-ending return is refused answers by ending its turn again, and is not
  surprised when the refusal recurs on a later wake while a child is still live.
- REQ-04: No step of the lead's loop reads as stay-alive, receive-in-place or loop-in-place.
- REQ-05: The org's decision record states the never-wait rule for the **lead tier**, with its
  measured cause — not as narrative inside a skill file.
- REQ-06: Every place that states the refusal's bound states the **measured** bound: the decision
  record, the message an agent reads when refused, and the orchestrator's playbook.
- REQ-07: Neither the rule nor the corrected bound can silently revert, and the assertions guarding
  them survive a reword of the sentences they guard.

## Success Criteria

- SC-01: At the reviewed sha, the region of `.claude/skills/harness-team/SKILL.md` between the
  dispatch step and the collect step carries one instruction holding both halves — a turn-ending
  directive and a statement that the member's completion wakes the lead — with the two halves within
  600 characters of one another. Matched by synonym sets, so a meaning-preserving reword passes and a
  deletion or a move outside the region fails. Demonstrated failing against
  `git show 9165162:.claude/skills/harness-team/SKILL.md`, where the region contains neither half.
  verify: automated      evidence: unit
- SC-02: The same region carries the **inoculation**, as three separable clauses: the refusal on a
  turn-ending return is EXPECTED; the correct response is to END THE TURN AGAIN; and it can RECUR on
  a later wake while a child is still live. Each clause has its own assertion — a whole-region search
  would be satisfied by the two easy clauses and blind to the missing third. Demonstrated failing
  against the `9165162` extract.
  verify: automated      evidence: unit
- SC-03: The guard is proven discriminating by five completed runs against five inputs: the
  `9165162` extract FAILS; a fixture whose sentence is reworded into different words with the same
  meaning PASSES; a fixture with the sentence moved outside the d-to-e region FAILS; a fixture
  carrying both stop-and-wake halves but NO inoculation FAILS; and a fixture carrying the inoculation
  but only two of its three clauses FAILS. Evidence is five exit codes from **completed** runs, never
  a still-running job's partial output.
  verify: automated      evidence: unit
- SC-04: The shipped instruction **contradicts** the dispatch tool's text rather than being silent
  beside it. A reviewer cites the `file:line` of the clause that tells the lead not to treat
  "continue other work in the meantime" as licence to manufacture activity, and states in one line
  why a lead reading only the tool text and only this clause would resolve them the same way. If no
  such clause exists, this is not_met even when SC-01 passes.
  verify: inspection
- SC-05: No step of the lead's loop contradicts the new instruction. A reviewer reads step 3's
  framing, steps d, e and f, and the close-out section at `git show <review_sha>:.claude/skills/harness-team/SKILL.md`,
  and cites `file:line` for each step graded and for any surviving stay-alive, receive-in-place or
  loop-in-place reading. Must grade explicitly: `:81` ("Until every step is terminal, or you halt"),
  `:112` ("Collect returns") and `:181` ("you have no reliable view of your own turn boundaries").
  verify: inspection
- SC-06: The never-wait rule covers the lead tier in the decision record: DEC-201's entry in
  `DECISIONS.md` carries a lead-tier scope statement, its `DECISIONS-INDEX.md` row names the lead
  tier where at `9165162` it names only the orchestrator, and `gen-decisions-index.py --stdout | diff -`
  against the committed index is clean. Asserted in the test suite, not only by a one-off command.
  verify: automated      evidence: unit
- SC-07: No unqualified once-only claim survives at any of the three sites this feature touches —
  `.harness/harness/docs/DECISIONS.md`, `.claude/skills/harness/bin/inflight_registry.py`,
  `.claude/skills/harness/SKILL.md`. An occurrence of the once-only phrasing passes only when a
  per-consecutive-stop-sequence qualifier appears within the same sentence, or when it sits inside an
  entry marked STRUCK. Demonstrated failing at `9165162`, where all three sites carry it unqualified.
  verify: automated      evidence: unit
- SC-08: A real domain lead dispatches a member under the merged skill and does not invent activity:
  its sidecar shows no tool call made only to stay alive between dispatch and wake, and no lead
  killed at ~600s. **Expect exactly one refused return per dispatch and do not score it as filler** —
  the lead's second stop is the correct behaviour this feature installs. Evidence is the sidecar path
  and the dispatch-to-resume timestamps.
  verify: uat

**SC-08 is the operator's own, it is run by hand, and it stays `not_met` until he runs it.** The
goal-check does not grade it and must not: no artifact on disk can settle whether a real lead obeyed
the sentence. It ships outstanding, and that is stated here rather than discovered at ship time.

### Three criteria neither ticket asked for — for your signature

Each of these is what *done* also requires. One sentence on what breaks without it:

- **SC-02 — the inoculation is present, in three separable clauses.** Without it the rule installs
  the very loop it removes: after this fix every dispatch's first turn-end meets a live child and is
  refused, and a lead told only "end your turn" reads that refusal as an instruction to stay.
- **SC-03 — the guard is proven discriminating against five fixtures.** Without it the guard can be
  green while grading nothing, which is exactly what #804 measured on
  `test-orchestrator-playbook.py`, so the rule could silently revert with the suite still passing.
- **SC-07 — no unqualified once-only claim survives at the three sites.** Without it a statement
  measurement has falsified stays standing in the decision record, in the message an agent reads at
  the moment it is refused, and in the orchestrator's playbook — and this repository has no
  propagation checker, so nothing else would ever catch it.

## The assertion shape, and what it does and does not prove (#804)

`test-orchestrator-playbook.py` has 8 assertions, **4 of them exact-literal greps a reword defeats
while the file stays green**. This feature's guard deliberately does not copy that shape. It uses
**region-scoped synonym alternations plus a five-fixture self-check** (SC-03).

**What it proves:** that the sentence exists, that it sits between steps d and e rather than anywhere
in the file, that all three inoculation clauses are present and not just the easy two, that the
detectors reject a file missing any of them, and that a meaning-preserving reword does not break the
build. **What it does not prove:** that any lead OBEYS the sentence. No runner in this repository can
execute a markdown playbook. Conduct is carried by SC-08 alone, and SC-08 is `uat`.

## Verification gaps

- **A markdown playbook cannot be executed by any runner.** SC-01, SC-02, SC-03, SC-06 and SC-07
  grade *text on disk*. SC-04 and SC-05 are human reads. **SC-08 is the only evidence of conduct**,
  and it stays `not_met` until the operator runs it.
- `test_kinds.eval` has `cmd: null` and `status: unresolved`. T-02 and T-03 are
  `change_type: ai_behavior`, whose matrix requirement is `eval`, so that requirement **resolves to a
  soft skip and proves nothing**. Disclosed, not routed around: the criteria above carry the feature,
  and the missing `eval` runner is a standing dev-ops backlog gap this feature does not close.
- `test_kinds.functional` (excluded, DEC-187), `component`, `ui` and `typecheck` are also null; none
  covers a surface this feature touches.
- **SC-08's evidence is confounded by design** (see the run note
  `runs/2026-08-24-01-product/lead-stop-contradiction.md`): the refusal costs one turn per dispatch
  and prints `BLOCKED` on stderr. That is expected output, not a defect and not filler.

## Constraints

**What BLOCKS**

- **DEC-179 blocks a squad route on the two playbooks.** `check-domain.sh --resolve` returns
  **NOBODY** at `9165162` for `.claude/skills/harness-team/SKILL.md` and
  `.claude/skills/harness/SKILL.md`, so tasks touching them are `main-session-direct`.
- **DEC-158 bounds the rule skill:** the rule, one clause of why, a pointer. The measurement lives in
  `DECISIONS.md`. **The inoculation is part of THE RULE, not narrative** — it states the expected
  response to an event the rule itself makes certain, which is exactly what
  `harness/SKILL.md:50` carries for the orchestrator. A later DEC-158 reader must not strip it as
  bloat: without it the rule installs the loop it removes (measurement 3).
- **No lead gains a message-sending tool, in any form.** #610 and #552 are CLOSED. A lead that has
  ended its turn cannot send anything, and a message tool gives it a fresh reason to stay awake and
  watch. Recorded as D-03 so a future scan does not re-suggest it.
- **#804 blocks copying the orchestrator test's shape** — see the assertion-shape section above.
- **Any suite claim comes from a COMPLETED run.** FEAT-35 shipped a red PR on a false "ALL PASSED"
  read of a still-being-written background job.

**What SUPPLIES**

- **DEC-201 supplies the rule and its wake evidence, already paid for** — three probes on 2026-08-23
  measured that a stopped parent is woken by its child at every depth the org uses. Cited, never
  re-measured. Its index row scopes it to the **orchestrator**, which is why extending it to leads is
  a decision change (REQ-05) and not a line slipped into a skill.
- **DEC-199 supplies the entry that must be corrected** (`DECISIONS.md:6698-6705`), and the ruling is
  **AMEND**. The entry and its ruling stand — a verdict about a member still running is still a
  verdict about something the reporter cannot see. Only the subordinate clause about how often the
  refusal fires is false, and only that clause changes. **DEC-188 does not apply**: it governs a
  decision the tree *flatly contradicts*, which this is not. T-06 executes the amendment; it does not
  choose (D-11).
- **DEC-174 amendment 4 supplies the lane T-04 runs in, on a condition T-04 must discharge**
  (`DECISIONS.md:4882-4885`). A module a gate imports is not itself a gate, so `inflight_registry.py`
  is squad-writable (D-08) — but the grant is conditional on *"showing the gate's violation set is
  identical before and after"*. That is why `test-validate-digest.py` is in T-04's `verify:` and why
  T-04's intent says so: `check-plan-routes.py` reads domain grants and nothing else, so it prints
  `OK T-04` whether or not the condition is ever discharged.
- **`test_kinds.unit` supplies the runner**: its `detect` glob already matches
  `.claude/skills/harness/bin/test-*.py`, and `run-unit-tests.sh`'s `UNIT_SCRIPTS` array is where a
  new file is registered — its drift detector fails the suite on any `test-*.py` in neither array.
- **`gen-decisions-index.py` supplies the index check**; the hand-written half of a row survives
  regeneration verbatim.
- **DEC-118 and DEC-116 supply the shape** the rule must survive: a team is single-squad, the lead
  hosts its own DAG, the run dir is the lead's alone.
- **DEC-139 supplies the mission shape** — the diagnosis segment that produced this brief's evidence.

## Proposed backlog rows — not tasks, not REQs, not SCs

Found while planning, out of scope here, listed so they are filed rather than lost. Nothing in this
feature builds any of them.

- **`plan-merge.py` has no supersede mode.** It unions by `id`, which is right for two pm spawns and
  wrong for a strike: removing a task from a plan cannot be expressed as a proposal, so the edit has
  to bypass the tool. This BRIEF's own strike was applied that way.
- **`notes/root-cause-*.md` is in no member's domain.** `check-domain.sh --resolve` on such a path
  returns `harness-orchestrator` alone at `9165162`, so a diagnosing member cannot write the artifact
  its own diagnosis produces.
- **Engineer DIGESTs are landing without `files_touched`**, which the handoff contract requires as an
  explicit `[]` when empty. An absent field cannot be told apart from "nothing found".
- **DEC-198 does not point forward at DEC-201.** An orchestrator that reaches DEC-198 from
  `harness.json` `budgets.orchestrator_context_warn_tokens` sees a bare number with no calibration;
  the bands live in DEC-201, and `DECISIONS.md` at `9165162` carries no reference to DEC-201 outside
  its own heading. This was a second, unrelated edit inside the struck #811 block and went with it —
  it is filed here so the strike does not silently drop it.

**Recorded and not filed:** the single-flight registry keying is a known consequence of a session
standing in another feature's worktree. Noted, no action.

## Approval

status: pending
approved_by: none
date: none
