# BRIEF — FEAT-37 lead stop-and-wake

> **This BRIEF supersedes the version written on 2026-08-24 against issue #831's stated cause.**
> That cause was an inference. Measurement replaced it (below), and the fix it implies is larger by
> one clause. Nothing of the earlier draft is preserved by default.
>
> **Re-anchored 2026-08-27 at `8fc87f8`.** Both signatures were withdrawn after an eight-reader
> panel. Every sha reference, line anchor and quoted string below was re-measured at `8fc87f8`; the
> old pin `9165162` survives only where a sentence contrasts what was true then with what is measured
> now. One commit caused the re-plan — `c5e59aa` (#815), which trimmed the orchestrator playbook 51%
> nine hours after the withdrawn plan pinned `9165162`. It took a task's subject away, emptied a
> success criterion's third site, and removed a rule from the tier above this one. All three are
> answered below.

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
   `8fc87f8`) to **e. Collect returns** (`:112`) with nothing between.
2. **A compounding cause the harness cannot edit.** The `Agent` tool's own result text — *"continue
   other work or respond to the user in the meantime"* — is what the transcript literally obeys, and
   it explains why the loop manufactures filler rather than idling. It appears nowhere in `.claude/`,
   `.harness/` or `docs/`: it is **platform-supplied**. **Removing the silence is therefore not
   enough; the rule must explicitly override the tool's nudge.** The orchestrator playbook used to
   carry exactly that override at `.claude/skills/harness/SKILL.md:45-56`. **It does not any more** —
   see the regression below — so there is no model in the tree to copy and the wording is specified
   in full in `plan.yaml`'s T-02 instead.
3. **After this fix, the refusal fires — measured, not feared.** Every dispatch's first turn-end will
   meet a live child and be refused. The bound is **at most once per CONSECUTIVE STOP SEQUENCE; it
   re-fires on each wake while a child is still live** — proven in `agent-a89be3fd837d1b779` line 178
   (children: eng-lead `22:59:07.135172`, product-lead `22:59:28.731235`) versus line 392 (child: the
   SAME eng-lead `22:59:07.135172`); different child sets prove a distinct event, not replayed
   context. A lead told only "end your turn" and then refused for doing it will read the refusal as
   an instruction to stay — which is the exact loop this feature removes. **So the rule must carry an
   INOCULATION: the refusal is expected, the correct response is to stop again, and it can recur.**
   The orchestrator playbook carried this and it worked. At `8fc87f8` it no longer does.

**A knock-on that is not optional.** `DECISIONS.md:6869` (DEC-199) states *"so a stop refusal fires
at most once"* as fact, `:6870` repeats it as *"REFUSED once on that hook, the same
one-correction-round strength"*, and the same falsified bound is repeated in the message an agent
reads at the moment of refusal (`inflight_registry.py:274`). Under PRINCIPLES rule 15 — never
falsify the record — this is corrected here, whatever the operator rules on scope below.

**A third site was named here and is now empty, which matters more than the correction.** At
`9165162` `harness/SKILL.md:53` carried the same false bound. On 2026-08-24 commit `c5e59aa`
(*"Trim the orchestrator playbook 51%: 6,409 → 3,157 words"*, #815) took that file from 527 lines to
288 and deleted the whole **NEVER WAIT FOR A LEAD** paragraph the sentence sat in. At `8fc87f8`,
`grep -nEi "single-flight refusal|fires at most once|fires ONCE" .claude/skills/harness/SKILL.md`
**exits 1**. The false sentence went — and so did the rule and the inoculation around it. What
survives is `:60`, *"There is no waiting anywhere in this loop"*, **with nothing saying the refusal
for stopping is expected.** That is the regression REQ-08 closes; see the scope call below.

## Goal

Give the lead tier the never-wait rule, in the one file all three leads preload — a lead never waits
for a member, it ends its turn, the member's completion wakes it, the dispatch tool's own nudge is
not licence to stay alive, and a refusal on that turn-end is expected and answered by stopping again.
Record its measured reason where the org's decisions live, correct the bound the record states
falsely, and guard all of it with assertions a reword cannot silently defeat. **The orchestrator had
this rule and lost it to `c5e59aa`'s trim on 2026-08-24; restoring it is REQ-08, the one addition the
operator made at re-plan, and it is strikable on its own.**

## Scope — #831 only, by ruling

`source_issues` is **`[831]`**. This feature fixes the loop, the record corrections rule 15 forces,
and — by the operator's call at re-plan — the regression `c5e59aa` left one tier up. Nothing else.
`plan.yaml` carries six tasks, T-01 to T-06; **T-03 was rewritten at re-plan** because its old
subject no longer exists.

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

### The one scope addition — the operator's call, taken on 2026-08-27, and strikable in one line

**This is the operator's decision, not the planner's.** He made it when he commissioned this re-plan,
after the eight-reader panel surfaced the `c5e59aa` regression; it is written here because he signs
this BRIEF and the signature is the approval.

The orchestrator tier lost its never-wait rule and its inoculation to `c5e59aa`, nine hours after the
withdrawn plan pinned `9165162`. It enters this feature as **REQ-08**, carried by **T-03 alone**, and
graded by **SC-09 alone**. T-03 depends only on T-01's guard, **nothing depends on T-03**, and
striking `REQ-08`, `T-03` and `SC-09` leaves #831 whole — one line at signature does it, and the only
knock-on is that T-01 drops its `orchestrator` test group. It is not folded into REQ-04 or any other
requirement, and it is deliberately not deferred to a ticket.

**Why not a ticket.** Deferring would ship a lead-tier never-wait rule while the tier directly above
it stays uninoculated. It is live, not theoretical: `inflight_registry.py:263`
`children_refusal_lines` is keyed on **having children**, not on `SINGLE_FLIGHT_AGENTS` (`:32`, which
holds `harness-pm` alone), so an orchestrator with a lead in flight — every orchestrator ending a
dispatch turn — takes that refusal routinely. T-04 already edits that exact function's text.

**The planner's own new-vs-covered judgement, and it agrees.** REQ-04 is *"No step of the **lead's**
loop reads as stay-alive"* — its subject is `harness-team/SKILL.md`, and no task tracing it touches
`harness/SKILL.md`. REQ-06 is the bound, and the orchestrator playbook no longer states any bound to
correct. So the regression is covered by nothing here, and folding it into either would silently
widen a requirement's subject to a second file. It is genuinely new. **A reader who thinks the
orchestrator can wait for its own reasons should strike it; nothing else in the feature moves.**

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
  record, and the message an agent reads when refused. **Two sites, not three** — the orchestrator's
  playbook stated it at `9165162` and states nothing at `8fc87f8`, `c5e59aa` having deleted the
  paragraph.
- REQ-07: Neither the rule nor the corrected bound can silently revert, and the assertions guarding
  them survive a reword of the sentences they guard.
- REQ-08 *(the operator's scope addition — strike this line, T-03 and SC-09 together to remove it)*:
  The orchestrator's playbook again tells the orchestrator that it never waits for a lead, that
  ending its turn is how it waits, that the dispatch tool's own nudge does not license staying alive,
  and that the refusal on that turn-end is expected, answered by ending the turn again, and recurs —
  stated at the measured bound.

## Success Criteria

- SC-01: At the reviewed sha, the region of `.claude/skills/harness-team/SKILL.md` between the
  dispatch step and the collect step carries one instruction holding both halves — a turn-ending
  directive and a statement that the member's completion wakes the lead — with the two halves within
  600 characters of one another. Matched by synonym sets, so a meaning-preserving reword passes and a
  deletion or a move outside the region fails. Demonstrated failing against
  `git show 8fc87f8:.claude/skills/harness-team/SKILL.md`, where the region contains neither half.
  verify: automated      evidence: unit
- SC-02: The same region carries the **inoculation**, as three separable clauses: the refusal on a
  turn-ending return is EXPECTED; the correct response is to END THE TURN AGAIN; and it can RECUR on
  a later wake while a child is still live. Each clause has its own assertion — a whole-region search
  would be satisfied by the two easy clauses and blind to the missing third. Demonstrated failing
  against the `8fc87f8` extract.
  verify: automated      evidence: unit
- SC-03: The guard is proven discriminating by **six** completed runs against six inputs: the
  `8fc87f8` extract FAILS; a fixture whose sentence is reworded into different words with the same
  meaning PASSES; a fixture with the sentence moved outside the d-to-e region FAILS; a fixture
  carrying both stop-and-wake halves but NO inoculation FAILS; a fixture carrying the inoculation but
  only two of its three clauses FAILS; and **a fixture carrying both halves and all three inoculation
  clauses while saying nothing about the dispatch tool's own text FAILS**. The sixth is what proves
  SC-04's detector is not vacuous. Evidence is six exit codes from **completed** runs, never a
  still-running job's partial output.
  verify: automated      evidence: unit
- SC-04: The shipped instruction **contradicts** the dispatch tool's text rather than being silent
  beside it. A reviewer cites the `file:line` of the clause that tells the lead not to treat
  "continue other work in the meantime" as licence to manufacture activity, and states in one line
  why a lead reading only the tool text and only this clause would resolve them the same way. If no
  such clause exists, this is not_met even when SC-01 passes.
  **Where it is delivered, because the withdrawn plan delivered it nowhere:** the clause is written
  into `plan.yaml` T-02 part THREE, in the shipped playbook — not into T-05's decision-record edit,
  which is where the withdrawn plan's only mention of "continue other work" sat. It has a mechanical
  floor too: T-01 `case7_overrides_tool_text` requires the tool's nudge and its denial **in one
  sentence** of the d-to-e region, and SC-03's sixth fixture proves that case can fail. The reviewer
  still owns the second half — whether a lead reading both would resolve them the same way — which is
  why this stays `inspection` and not `automated`.
  verify: inspection
- SC-05: No step of the lead's loop contradicts the new instruction. A reviewer reads step 3's
  framing, steps d, e and f, and the close-out section at `git show <review_sha>:.claude/skills/harness-team/SKILL.md`,
  and cites `file:line` for each step graded and for any surviving stay-alive, receive-in-place or
  loop-in-place reading. Must grade explicitly: `:81` ("Until every step is terminal, or you halt"),
  `:112` ("Collect returns") and `:181` ("you have no reliable view of your own turn boundaries").
  verify: inspection
- SC-06: The never-wait rule covers the lead tier in the decision record: DEC-201's entry in
  `DECISIONS.md` carries a scope sentence naming the **lead tier and the turn-ending act together**,
  its level-two heading names the lead tier, its `DECISIONS-INDEX.md` row names the lead tier **in the
  hand-written half of the row**, and `gen-decisions-index.py --stdout | diff -` against the committed
  index is clean. Asserted in the test suite, not only by a one-off command.
  **Why "together" and "hand-written half" are in the criterion:** at `8fc87f8` DEC-201's body already
  contains the word `lead` three times incidentally, so a bare word match is green before any work is
  done; and the row's generated half is derived from the heading, so it would carry the word for free
  once the heading is renamed. Both narrowings exist so the assertion grades the change.
  verify: automated      evidence: unit
- SC-07: No unqualified once-only claim survives at either of the **two** sites that still carry the
  claim — `.harness/harness/docs/DECISIONS.md` and
  `.claude/skills/harness/bin/inflight_registry.py`. An occurrence of the once-only phrasing passes
  only when a per-consecutive-stop-sequence qualifier appears within the same sentence, or when it
  sits inside an entry marked STRUCK. Each site also carries a **floor assertion**: zero occurrences
  found at a site is a named FAIL, never a pass, so a deletion or a path typo cannot turn the check
  green by emptying its subject. Demonstrated failing at `8fc87f8`, where both sites carry it
  unqualified.
  **A third site was in this criterion and has been removed, deliberately.**
  `.claude/skills/harness/SKILL.md` carried the claim at `9165162` and carries nothing at `8fc87f8`
  (`c5e59aa`); grading it would have run an occurrence loop over an empty list and exited 0 having
  proven nothing — the #804 shape, arriving by drift. That file is graded on **presence** by SC-09
  instead.
  verify: automated      evidence: unit
- SC-08: A real domain lead dispatches a member under the merged skill and does not invent activity:
  its sidecar shows no tool call made only to stay alive between dispatch and wake, and no lead
  killed at ~600s. **Expect exactly one refused return per dispatch and do not score it as filler** —
  the lead's second stop is the correct behaviour this feature installs. Evidence is the sidecar path
  and the dispatch-to-resume timestamps. **Run AFTER MERGE, from the main checkout** — see the note
  below.
  verify: uat
- SC-09 *(the operator's scope addition — strike with REQ-08 and T-03)*: At the reviewed sha, the
  window around `.claude/skills/harness/SKILL.md`'s "There is no waiting anywhere in this loop"
  sentence carries all of: a turn-ending directive; a statement that the platform resumes the
  orchestrator when the child completes; the refusal being EXPECTED; the response being to end the
  turn again; the refusal RECURRING; and the measured per-consecutive-stop-sequence bound in one
  sentence. Six separate assertions, matched by the same synonym alternations SC-01 to SC-03 use.
  **Graded on presence, not on absence**, so it cannot pass on an empty subject. All six fail at
  `8fc87f8`.
  verify: automated      evidence: unit

**SC-08 stays `not_met` at ship, and the reason is measured rather than procedural.** The cheapest
option was tested first: **can this feature's own build phase grade it**, since the build is a real
lead dispatching real members? **No, and the answer is decisive.** DEC-201 records that *a spawned
agent loads its skills from the main checkout* while a rewritten playbook is committed in a worktree
— which is exactly why DEC-201's own 1057.1s data point had to be taken under a dispatch-level
override. Every lead spawned during this build therefore reads the **unedited**
`.claude/skills/harness-team/SKILL.md`, so any sidecar this build produces grades the old text.
Scoring SC-08 from it would be evidence for the wrong file, which is worse than no evidence.
(#866's per-worktree registry keying is a second reason and not the deciding one.)

**So SC-08 is a declared post-merge step, owned by the operator**: after this feature merges to
`main`, dispatch one lead from the main checkout, then read that lead's sidecar between its dispatch
and its wake and confirm no tool call was made only to stay alive, and no kill at ~600s. The goal-check
does not grade it and must not. It ships outstanding, stated here rather than discovered at ship time.
Recorded as D-13.

### Four criteria neither ticket asked for — for your signature

Each of these is what *done* also requires. One sentence on what breaks without it:

- **SC-02 — the inoculation is present, in three separable clauses.** Without it the rule installs
  the very loop it removes: after this fix every dispatch's first turn-end meets a live child and is
  refused, and a lead told only "end your turn" reads that refusal as an instruction to stay.
- **SC-03 — the guard is proven discriminating against six fixtures.** Without it the guard can be
  green while grading nothing, which is exactly what #804 measured on
  `test-orchestrator-playbook.py`, so the rule could silently revert with the suite still passing.
- **SC-09 — the orchestrator's own rule and inoculation are back.** Without it the tier directly
  above the one this feature fixes keeps a bare "no waiting" instruction and no clause telling it the
  refusal for obeying is expected — the same defect, one level up, which `c5e59aa` introduced
  unnoticed. Strike it and nothing else in the feature moves.
- **SC-07 — no unqualified once-only claim survives at the two remaining sites.** Without it a statement
  measurement has falsified stays standing in the decision record and in the message an agent reads
  at the moment it is refused — and this repository has no propagation checker, so nothing else would
  ever catch it.

## The assertion shape, and what it does and does not prove (#804)

`test-orchestrator-playbook.py` has 8 assertions (8 `check(` calls at `8fc87f8`), **4 of them
exact-literal greps a reword defeats while the file stays green** (#804). This feature's guard
deliberately does not copy that shape. It uses **region-scoped synonym alternations plus a
six-fixture self-check** (SC-03).

**And a floor, which is the lesson of this re-plan.** An occurrence-grading group over an empty
subject exits 0 having looked at nothing — that is how a signed plan came to point a check at a
paragraph `c5e59aa` had already deleted. Every occurrence group here asserts a minimum count, and the
one surface whose text was deleted is graded on presence instead.

**What it proves:** that the sentence exists, that it sits between steps d and e rather than anywhere
in the file, that all three inoculation clauses are present and not just the easy two, that the tool's
own nudge is named and denied in one sentence, that the detectors reject a file missing any of them,
and that a meaning-preserving reword does not break the
build. **What it does not prove:** that any lead OBEYS the sentence. No runner in this repository can
execute a markdown playbook. Conduct is carried by SC-08 alone, and SC-08 is `uat`.

## Verification gaps

- **A markdown playbook cannot be executed by any runner.** SC-01, SC-02, SC-03, SC-06, SC-07 and
  SC-09 grade *text on disk*. SC-04 and SC-05 are human reads. **SC-08 is the only evidence of
  conduct**, and it stays `not_met` until the operator runs it — after merge, from the main checkout,
  because a spawned agent loads its skills from there and not from this worktree (D-13).
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
  **NOBODY** at `8fc87f8` for `.claude/skills/harness-team/SKILL.md` and
  `.claude/skills/harness/SKILL.md`, so tasks touching them are `main-session-direct`.
- **DEC-158 bounds the rule skill:** the rule, one clause of why, a pointer. The measurement lives in
  `DECISIONS.md`. **The inoculation is part of THE RULE, not narrative** — it states the expected
  response to an event the rule itself makes certain. A later DEC-158 reader must not strip it as
  bloat: without it the rule installs the loop it removes (measurement 3). **This is not
  hypothetical — it already happened once.** `c5e59aa` trimmed the orchestrator playbook 51% and the
  inoculation went out with the bulk, which is the whole of REQ-08's case.
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
- **DEC-199 supplies the entry that must be corrected** — heading at `DECISIONS.md:6836`, the
  paragraph at `:6866-6873` at `8fc87f8`. **The entry is CORRECTED IN PLACE**: it keeps its ruling —
  a verdict about a member still running is still a verdict about something the reporter cannot see —
  and only the subordinate clause about how often the refusal fires is false, so only that clause
  changes, rewritten inside the entry's own sentences in the entry's own voice. **There is no
  amendment sub-section, no dated note and no changelog line**; `plan.yaml` D-09 retired that form,
  and this paragraph previously spelled the ruling *"AMEND"* and *"T-06 executes the amendment"* —
  those words are withdrawn here. **DEC-188 does not apply**: it governs a decision the tree *flatly
  contradicts*, which this is not. T-06 executes the correction; it does not choose (D-11).
- **DEC-174 amendment 4 supplies the lane T-04 runs in, and it supplies it UNCONDITIONALLY**
  (`DECISIONS.md:5011` at `8fc87f8`). Read at the sentence: *a module a gate imports is not itself a
  gate*; *a squad may write the library*; and *the **cutover** that makes a gate use it is
  main-session-direct, proven by showing the gate's violation set is identical before and after*.
  **The proof burden attaches to the cutover, not to the squad's write** — and T-04 is not a cutover,
  since `validate-digest.py` already imports `inflight_registry.py`. An earlier draft of this BRIEF
  said the grant was conditional on T-04 discharging that proof; **that was a paraphrase stronger
  than the text, and it is corrected here.** `test-validate-digest.py` stays in T-04's `verify:`
  anyway, as this plan's own evidence discipline: a gate's behaviour is downstream of that diff, and
  `check-plan-routes.py` reads domain grants and nothing else, so it prints `OK T-04` regardless.
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
  returns `harness-orchestrator` alone at `8fc87f8` (re-run, same result), so a diagnosing member
  cannot write the artifact its own diagnosis produces.
- **Engineer DIGESTs are landing without `files_touched`**, which the handoff contract requires as an
  explicit `[]` when empty. An absent field cannot be told apart from "nothing found".
- **DEC-198 does not point forward at DEC-201.** An orchestrator that reaches DEC-198 from
  `harness.json` `budgets.orchestrator_context_warn_tokens` sees a bare number with no calibration;
  the bands live in DEC-201, and `DECISIONS.md` at `8fc87f8` contains exactly **one** occurrence of
  the string `DEC-201`, its own heading — so nothing points forward. This was a second, unrelated
  edit inside the struck #811 block and went with it — it is filed here so the strike does not
  silently drop it.
- **`inflight_registry.py:258` attributes the wrong issue.** The line in `refusal_lines` reads
  *"this is issue #551: the second writer would otherwise overwrite the first's plan.yaml"*, where
  #866 measures the two-writers bug as **#628**. **Deliberately not fixed here.** It is a different
  function on a different code path from the `children_refusal_lines` T-04 corrects, with its own
  tests, and it rests on #866's measurement rather than on this feature's — folding it in would widen
  T-04 past what this feature measured. **Disclosed residual, for the backlog.**

**Recorded and not filed:** the single-flight registry keying is a known consequence of a session
standing in another feature's worktree. Noted, no action. Its blast radius was re-checked and is
`leave`: `SINGLE_FLIGHT_AGENTS` at `inflight_registry.py:32` holds `harness-pm` alone, so a lead's
higher stop/wake rate never reaches `refusal_lines` and this feature adds no exposure.

## Approval

status: pending
approved_by:
date:
withdrawn: 2026-08-27 — the plan is being re-derived against HEAD. SC-04 has no delivering
instruction (the required override of the dispatch tool's text lives only in T-05's decision-record
edit, never in T-02's playbook edit), and SC-07's third site carries no once-only claim at all
because c5e59aa deleted the paragraph, so its check grades an empty set. BRIEF.md:213 and :216 also
still spell the DEC-199 ruling AMEND, which plan.yaml's D-09 retired as a form.
