# BRIEF — FEAT-35 orchestrator stop-and-wake

## Problem

An orchestrator that has dispatched a lead has nothing to do until that lead returns, and its
playbook tells it to stay. So it invents activity: on 2026-08-23 one spent **354 of its 450** Bash
calls on `echo hold` and `sleep`, went quiet, and was killed by the 600s no-progress watchdog —
taking its lead and its member down with it (recorded in commit `f5194d2`). Within one phase the
orchestrator sequences several whole-team round-trips (build, then qa, then simplify, then the
goal-check, then the briefing — DEC-118), each far longer than 600s, so the failure is not an
outlier: it is what the loop asks for. The cost is the whole feature's work, unresumable, and a
transcript of fabricated holding activity that no reader can distinguish from progress.

Measured the same day, three probes with unguessable UUIDs written to disk: **a parent subagent that
stops IS woken by its child's completion**, at every depth the org actually uses. One parent stopped
at 15:17:14, received the completion at 15:18:05, and resumed at 15:18:09 quoting the child's UUID
exactly. The platform already pumps the loop. Only the playbook does not know it.

## Goal

Rewrite the orchestrator playbook so that an orchestrator never waits. Every dispatch ends its turn;
the platform wakes it with the child's completion; on waking it re-establishes state from disk,
treats what it was told as a claim until an artifact confirms it, and weighs its own context against
the configured threshold to decide whether to continue this phase or hand it to a fresh
orchestrator. One rule, one loop, no step left standing that says otherwise.

## Requirements

- REQ-01: An orchestrator with work in flight ends its turn instead of occupying itself, and
  continues when the platform delivers the completion.
- REQ-02: The playbook gives exactly one instruction for what to do while a dispatch is in flight,
  and no step reads as stay-alive, receive-in-place, or loop-in-place.
- REQ-03: A woken orchestrator re-reads its state from disk and treats a reported completion as a
  claim until an artifact on disk confirms it.
- REQ-04: On waking, an orchestrator can measure its own context against the configured threshold
  and decide, advisorily, whether to hand the phase over rather than continue.
- REQ-05: A handoff triggered by context leaves the successor a note it can act on without reading
  the feature directory wholesale.
- REQ-06: The playbook instructs no write that the tree refuses.
- REQ-07: The rule and the reason for it are recorded where the org's decisions live, not as
  incident narrative inside the playbook.

## Constraints

**What bounds the solution**

- **Scope is the orchestrator playbook's BEHAVIOUR.** `.claude/skills/harness/SKILL.md` is the only
  behaviour this feature changes, and it travels with exactly two sanctioned companions: the
  decision record that carries the rule's measured reason (`.harness/harness/docs/DECISIONS.md` and
  its generated index — DEC-158 forbids that measurement living in the playbook) and the regression
  test that proves the rewrite cannot silently revert. Nothing else, and no third companion. The
  three domain leads run the same wait-for-a-member pattern through `harness-team` and are
  deliberately untouched; they are ticketed as #610 and #552. Widening to them fails this brief.
- **DEC-179 BLOCKS a squad route.** `check-domain.sh --resolve .claude/skills/harness/SKILL.md`
  returns `NOBODY` at `569d417`, so every task touching the playbook is `main-session-direct`.
- **DEC-198 SUPPLIES the threshold and bounds its force.** `budgets.orchestrator_context_warn_tokens`
  is `200000`; crossing it ADVISES and never refuses. Turning it into a gate is out of bounds.
- **DEC-158 BOUNDS the text.** A rule skill carries the rule, one clause of why, and a decision
  pointer. Incident measurements belong in `DECISIONS.md`, which is why REQ-07 exists.
- **DEC-192 BINDS the correction in REQ-06.** `phase` was deleted; there is one `status` field whose
  six values are the board's column names, and the feature schema refuses anything else.
- Branch `chore/744-never-wait-for-a-lead` (`f5194d2`, unmerged, 5 insertions to SKILL.md and
  nothing else) is **absorbed and abandoned** — the plan's D-03 records why.

**What supplies the mechanism**

- **`check-domain.sh` SUPPLIES the operative lane test, and DEC-174 am.4 supplies only the
  CATEGORY.** The test that actually forces the lane is
  `check-domain.sh --resolve .claude/skills/harness/SKILL.md` returning `NOBODY` at `569d417`: no
  agent may write the playbook, so every playbook task is `main-session-direct`. That result is
  independent of am.4. Am.4's own heading is *"the enumeration is a list of examples, not a
  boundary"* and it rules *"The category governs"* (`DECISIONS.md:4854`, `:4862`), so its
  parenthetical list is NOT the enforcement layer and the playbook's absence from that list settles
  nothing either way. Am.4 is cited here for the category — "hooks, validators, gate scripts" — and
  for nothing else.
- **DEC-159 and DEC-148 SUPPLY the seam.** One phase per orchestrator, the phase boundary is normal
  termination, and the successor reads a capped handoff note (`templates/HANDOFF.md`, four sections,
  ~60 lines, shape-gated). No new seam is introduced.
- **DEC-120 and DEC-118 SUPPLY the shape** the loop must survive: layer 1, one orchestrator per
  feature, and one phase spanning several single-squad lead round-trips.
- **DEC-199 SUPPLIES the harm shape behind REQ-03.** During the probes a parent FABRICATED a
  completion for its child, complete with an invented UUID that appears nowhere but in its own
  messages, and wrote a wrong verdict to disk before the real notification arrived.
- `context-watch.py` SUPPLIES the meter. It is read-only and decides nothing; the orchestrator does.

## Success Criteria

- SC-01: At the reviewed sha, the playbook carries the never-wait rule and no stay-alive
  instruction: `git show <review_sha>:.claude/skills/harness/SKILL.md` contains no occurrence of
  "Receive the team digest" or "Loop until DONE", and does contain the never-wait rule. Each
  assertion must be demonstrated failing at `569d417` before the change.
  verify: automated      evidence: unit
- SC-02: The playbook's wake step names both `context-watch.py` and
  `budgets.orchestrator_context_warn_tokens`, and no line that mentions the threshold also says
  refuse, refused, blocked or prevented. Demonstrated failing at `569d417`, where neither token
  appears anywhere in the file.
  verify: automated      evidence: unit
- SC-03: The self-identification mechanism the playbook prints actually works from inside an
  agent's own turn. A reviewer executes it verbatim, in its own two separate Bash calls, with the
  glob's `agentType` filter set to its OWN `agentType` as stand-in rather than
  `harness-orchestrator` — a reviewer never carries that type, so the criterion is unclosable if it
  names it. It records in its review note the single matching sidecar path, the agent id derived
  from it, and the `context-watch.py` row for that id, each cited as `file:line`. **What this does
  NOT cover:** the orchestrator-typed glob itself — the literal string
  `"agentType":"harness-orchestrator"` as the playbook prints it — is never executed by this
  criterion and stays unexercised until a real orchestrator runs it after merge. What is proven is
  the mechanism's shape: the two-call sequence (the nonce must be grepped in a LATER call, because
  a same-call grep finds nothing), the match-count logic, and `context-watch.py` accepting the
  derived id. What is not proven is that an orchestrator's own sidecar satisfies that filter.
  verify: inspection
- SC-04: The playbook instructs no write the tree refuses:
  `git show <review_sha>:.claude/skills/harness/SKILL.md` contains no instruction to write
  `feature.json` `phase:`, and its phase-exit paragraph names `status:`. Demonstrated failing at
  `569d417`, where line 344 carries that instruction.
  verify: automated      evidence: unit
- SC-05: A real feature phase runs with an orchestrator that completes at least one lead round-trip
  longer than 600 seconds, and its sidecar transcript shows no orchestrator killed at ~600s and no
  Bash call made only to stay alive. Evidence is the orchestrator's sidecar path and the
  dispatch-to-resume timestamps.
  verify: uat
- SC-06: The rewritten loop reads as one document: steps 3 through 7 agree about what happens while
  a dispatch is in flight, and nothing outside the loop contradicts them. A reviewer cites
  `file:line` for each step it graded, and for any surviving contradiction.
  verify: inspection
- SC-07: The rule and its measured reason are recorded as a decision, and the generated index
  carries its row: `gen-decisions-index.py --stdout | diff -` against the index is clean and the
  new row greps.
  verify: automated      evidence: integration

## Verification gaps

- `test_kinds.eval` has `cmd: null`: the three playbook tasks are `change_type: ai_behavior`, whose
  matrix requirement is `eval`, so that requirement resolves to a soft skip and proves nothing. What
  carries it instead: SC-01, SC-02 and SC-04 assert the playbook's text at the reviewed sha, SC-06
  is a human read of its coherence, and SC-05 is the only evidence of actual conduct. **A markdown
  playbook cannot be executed by any runner** — no test in this repository can prove an orchestrator
  obeys it. The missing `eval` runner is a standing dev-ops gap worth a backlog row, not something
  this feature closes.
- `test_kinds.functional`, `component`, `ui` and `typecheck` are also null; none covers a surface
  this feature touches.

## Approval

status: approved
approved-by: operator
date: 2026-08-24
