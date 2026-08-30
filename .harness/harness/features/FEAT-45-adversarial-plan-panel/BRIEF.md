# BRIEF — FEAT-45-adversarial-plan-panel

Source of settled design: `.harness/notes/grilling-adversarial-plan-panel-2026-08-29.md`. Its
`## Settled` section is the authority for the shape; this brief states the outcomes.

## Problem

A plan reaches the operator's signature having been read only by agents that ask whether it conforms
to the brief it was written from. Nothing asks whether the work should be done at all. Measured: a
panel run **once by hand** against FEAT-38's already-signed plan found what two prior review rounds
did not, including one high-severity defect that would have burned a build cycle. That panel was ad
hoc — it was dispatched directly from the main session, bypassing the orchestrator (a DEC-120
deviation), and it exists nowhere on disk. The next plan gets signed without it, and the cost of a
plan that should not have been built is a whole build phase.

## Goal

`/harness-plan` gains a standing adversarial panel that reads the **drafted** plan before the
operator signs it. Its readers ask whether the work should exist — not whether it matches the brief,
which the simplify pass and the architecture review already cover. A high-severity finding stops the
plan from reaching the signature until it is resolved or the operator explicitly overrules it, and an
overrule is a recorded act rather than a conversation nobody can find afterwards.

## Requirements

- REQ-01: Every plan drafted by `/harness-plan` is read by the panel before it is presented for the
  operator's signature — every plan, with no size threshold and no opt-in. A re-plan that changes the
  task set resets `approval.status` to `pending` and is therefore presented again, so it is read
  again, scoped to the tasks that are not `done`.
- REQ-02: An **independent-context** reader — spawned OUTSIDE the dispatch chain that authored the
  plan, and therefore holding none of its reasoning — answers, of the drafted plan: **what here should
  not be built at all?** Model independence is **not** claimed: measured 2026-08-29, no governed spawn
  in this repository can select a model (`dispatch-guard.sh:36-53` exits 2 on any `harness-`-prefixed
  caller passing `model:`, whatever the target), and the turn-level `advisor` channel is unattached on
  this workstation (`advisorModel` absent from `~/.claude/settings.json`, contradicting DEC-170's
  recorded `:112`). Independence here is independence **from the dispatch chain**, which is the
  property DEC-170 actually credits.
- REQ-03: The drafted plan is goal-checked against the operator's **stated intent**, not against the
  brief the plan was written from.
- REQ-04: The plan is read for scope: **which tasks serve no live requirement, and what does the
  feature actually need to ship?** — covering orphan traces in both directions, dependency shape, and
  `verify:` blocks asserting something a predecessor deletes.
- REQ-05: The independent-context reader's return is normalized into a contract-compliant digest before
  anything routes on it, and the agent roster does not grow to accommodate it. The reader's own return
  is validated by **nothing** — `validate-digest.py:900-907` returns 0 for any non-`harness-`
  `agent_type` — so the normalization is the only place the contract is enforced, and the only stop
  event that is checked is the wrapping lead's own.
- REQ-06: A finding at `high` or worse prevents the plan from being presented for signature until it
  is either resolved or explicitly overruled by the operator.
- REQ-07: The operator can overrule any panel finding by a stated act, and that overrule is recorded
  durably in the artifact set the signature itself belongs to — not only in the conversation.
- REQ-08: An overruled finding is distinguishable from a resolved one, afterwards, from the record
  alone, together with who overruled it and when.
- REQ-09: Every panel record lands on a path its producing agent is already granted to write, or the
  grant is added deliberately in the same change.
- REQ-10: A plan presented for signature with no panel result recorded, or with the panel's presence
  in the plan sequence removed, is detectable by machine rather than by someone remembering.
- REQ-11: The two precedents this feature sets are each recorded as a signed decision: a wrapped
  non-harness reader whose return is structurally unvalidated, and a gate that fires in the **plan**
  phase before any code exists.
- REQ-12: Panel findings enter the operator's single batched review pass at the signature gate and do
  not open a separate pre-signature fix ping-pong.
- REQ-13: A re-run of the panel does not overwrite the record of the run whose findings caused it.

## Success Criteria

- SC-01: The panel is three readers across the two squad segments, and **each** of the three prompts
  contains its own question from REQ-02, REQ-03 and REQ-04 — asserted per reader, never as a
  file-global match or a count. Two of the three are steps of the validator-squad team file, which
  resolves under the team runner; the third is the product segment's goal-check, whose question is
  asserted in the orchestrator playbook text that dispatches it. A team is single-squad (DEC-118), so
  a single team file carrying all three is not a shape this repository can run — falsified by any
  reader whose question appears nowhere, and by a team file naming a **harness** persona from outside
  the validator squad. The non-harness reader of SC-14 is the one permitted exception, and it is the
  point of the design rather than a leak in it.
  verify: automated      evidence: unit
- SC-02: `check-domain.sh --resolve`, run over every rendered **non-empty** `outputs:` path of every
  panel step and over the goal-check note path the playbook names, reports the path granted to that
  step's own persona. Falsified by one step whose output path no grant covers, which is the measured
  hand-run failure (the goal-check was denied `notes/goalcheck-plan-*.md`). A step declaring
  `outputs: []` is in scope for SC-14, not for this one: a read-only reader that writes nothing
  cannot be denied a path, and counting it here would grade an empty set as a pass.
  verify: automated      evidence: unit
- SC-03: Every panel step and playbook-named artifact that can re-run resolves `{{cycle}}` in its
  output path (DEC-117), and the run-scoped record of a superseded run survives the re-run.
  Falsified by one re-runnable writer with a cycle-free path, or by a second run overwriting the
  first's record.
  verify: automated      evidence: unit
- SC-04: Against a fixture plan carrying a `high` panel finding that is neither resolved nor
  overruled, the machine check refuses the signed state; against the same fixture with the finding
  overruled, and again with it resolved, it passes. The refusing direction must be demonstrated
  failing on the pre-change tree before the change is accepted.
  verify: automated      evidence: unit
- SC-05: Given a fixture whose panel raised two `high` findings — one resolved, one overruled — the
  check names which is which, and rejects an overrule missing its operator attribution or date.
  Falsified if both dispositions read identically, or if an unattributed overrule passes.
  verify: automated      evidence: unit
- SC-06: The roster census still reports 16 agents with unchanged membership. Falsified by a
  seventeenth agent.
  verify: automated      evidence: unit
- SC-07: A plan presented for signature with no panel result recorded is reported by the machine
  check. Falsified if the check passes such a state.
  verify: automated      evidence: unit
- SC-08: Every test file this feature adds is executed by the project's own runner invocation
  (`run-unit-tests.sh --kind unit`), not only standalone. Falsified if the file exists and the runner
  never names it, which leaves the assertion permanently unrun.
  verify: automated      evidence: unit
- SC-09: `git show <review_sha>:.harness/harness/docs/DECISIONS.md` carries one entry per REQ-11
  carve-out, each naming the precedent it sets, and `DECISIONS-INDEX.md` at the same sha is the
  regenerated index of that file.
  verify: inspection
- SC-10: The plan door's own text at `<review_sha>` routes panel findings into the one consolidated
  revision of DEC-176 and introduces no separate pre-signature fix dispatch.
  verify: inspection
- SC-11: On a live plan, the operator judges each of the three readers to have earned its spawn —
  findings of substance, not padding to justify the run.
  verify: uat
- SC-12: On a live plan whose panel raises nothing at `high`, the operator reaches the signature with
  no extra step beyond reading the panel's result.
  verify: uat
- SC-13: A panel finding carries an identity that is stable across a re-run of the panel and changes
  when the finding's own content changes, and a recorded overrule naming an identity absent from the
  current panel result is refused. Falsified if a re-run renames an unchanged finding (an overrule
  silently stops applying), or if a stale overrule passes as covering the current set.
  verify: automated      evidence: unit
- SC-14: The panel's adversarial reader step names a persona that is **not** one of the 16 harness
  agents and declares no `outputs:` path, which is what makes it a spawn outside the authoring chain
  with nothing of its own to write. Falsified by a reader step naming a harness persona, or one
  declaring an output path no persona is granted.
  verify: automated      evidence: unit

## Verification gaps

- `eval` has `cmd: null` and `status: unresolved` in `.harness/harness.json`, so **no runner in this
  repository can grade the panel's finding QUALITY** — whether the independent reader asks its
  question well and catches real defects is LLM behaviour. Nothing here proves it. What carries it
  instead: SC-11 (the operator, by eye) plus the single recorded hand-run against FEAT-38's signed
  plan, n = 1. Every automated criterion above grades the panel's *wiring*, not its judgement. A
  standing `eval` runner is a dev-ops backlog row, not this feature's work.
- `component`, `ui` and `typecheck` are also null; this feature touches none of their surfaces, so
  they are not gaps here.
- **Model independence is unprovable here and is therefore not claimed.** No test can assert a
  property no repo mechanism can select or detect (see REQ-02's measurement). What carries the
  reader's differentiation instead: SC-14, which grades the one thing that IS on disk — that the
  reader is spawned outside the authoring chain as a non-harness type. Whether an independent MODEL
  would find more is unmeasured, n = 0, and is a platform question rather than this feature's.

## Constraints

**These SUPPLY the mechanism — none of them obstructs this feature:**

- Settled by the grilling artifact and not open for re-litigation: `harness-validator-lead` wraps the
  independent reader, dispatching it and normalizing its findings into its own collated digest;
  hosting is TWO orchestrator-sequenced squad segments, `harness-product-lead` hosting the
  goal-check and `harness-validator-lead` hosting the adversarial readers; `harness-code-reviewer`
  takes the scope hunt.
- DEC-118 — a team is single-squad, so a two-squad panel is an orchestrator playbook sequencing one
  lead-owned run per squad segment. This is why hosting is two segments and not one team.
- `harness-validator-lead` already computes `must_fix` and `severity_max`, and already returns `FAIL`
  on `severity_max >= high` (its own agent definition; DEC-31). REQ-06's gate is that existing
  mechanism reaching the signature, not a new severity scheme.
- DEC-116 — a team step's `outputs:` resolve to the producing agent's own domain; DEC-117 — `{{cycle}}`
  resolves in the output path of anything that re-runs. Together they are SC-02 and SC-03.
- DEC-113 — a project team override at `.harness/teams/<name>.yaml` resolves before the shipped set.
- DEC-42 and DEC-43 — an approval step sits at a team boundary, never mid-DAG; a subagent cannot ask
  the user, so questions ride up as `open_questions` and the orchestrator asks. DEC-44 — the user's
  answers are written durably under `notes/answers-*.md`, which the orchestrator owns.
- DEC-120 — the main session is the only tier with a user channel and the only writer of
  `plan.yaml approval:`. REQ-07's recorded overrule is therefore the main session's write.
- DEC-176 — the signature gate is batched: one review pass, one consolidated fix. REQ-12 keeps the
  panel inside that pass; a panel that dispatches its own fixes recreates the seven-run ping-pong
  DEC-176 exists to stop.
- DEC-170 — an agent whose verdict changed because of advisor input discloses that in its DIGEST.
- DEC-172 — the three-part return is a fenced `yaml` block, `safe_load`ed; that is the shape REQ-05's
  normalization must produce.
- DEC-195 — the four-angle simplify pass is already a plan-flow step whose findings return to
  `harness-pm`. The panel is a second plan-flow reader set and must be ordered against it, not
  merged into it.

**These BLOCK or bound the solution:**

- DEC-174 — the harness plans its own work but never EXECUTES changes to its own hooks, validators or
  gate scripts, and the list is non-exhaustive. Any REQ-10 or SC-04 machine check that lands in
  `check-state.sh`, `validate-digest.py` or `check-domain.sh` is a `main-session-direct` task, decided
  at plan time via DEC-179's `check-domain.sh --resolve`, never discovered mid-build.
- Measured by the eng squad (`notes/receipt-harness-dev-ops-arch-eng.md`): the only reader channel
  that mechanically exists is a **spawned non-harness subagent**; `Explore`, `fork`, `general-purpose`
  and `Plan` are platform built-ins with no agent-definition file in this repo, so none of them is a
  seventeenth agent. `harness-validator-lead` holds `Agent` but not `Bash`, so it can dispatch the
  reader and can never validate its return by running anything.
- DEC-106 and DEC-151 — a reviewer's `Write` reaches exactly its namespaced report and its own
  Expertise; it holds no `Edit`. `harness-validator-lead`'s only per-feature grant is
  `runs/*-validator/**`. A panel step's `outputs:` must land inside those, or the grant is widened
  deliberately in this change (REQ-09).
- `main_session.writes` in `.harness/team-config.yaml` is three approval paths plus
  `.harness/logs/**`. Whatever REQ-07's overrule record is, the main session must be granted the path
  it lands on, and `check-domain.sh` reads that list.
- Editing `.harness/harness/docs/DECISIONS.md` requires regenerating `DECISIONS-INDEX.md` in the same
  change; the index stores a per-row source line, so lengthening one entry shifts every later anchor.
- The plan sequence is PROSE today, in `.claude/commands/harness-plan.md`'s `**Target state:**`
  bullet. That is the trigger site REQ-10 acts on, and nothing enforces its composition now.
- `integration`'s `detect` in `.harness/harness.json` is an explicit file enumeration, and
  `run-unit-tests.sh` names its scripts in `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays. A new test
  file is invisible to both unless it is registered — SC-08.

**Out of scope, settled by the operator in the grilling artifact:**

- The `/harness-ship` review panel. It grades a diff against a pinned sha and already exists.
- Fixing `check-domain.sh`'s fail-open approval guard. Same class of problem, a later feature.
- Whether the wrapped-reader pattern generalizes to further outside models. Not sharp until there is
  a second candidate.
- Re-litigating FEAT-38's own panel findings; a revision is in flight elsewhere.

**Ruled out of scope by pm, with a destination — the plan-door id collision.** The no-argument branch
of `.claude/commands/harness.md:40` lists in-flight features from
`.harness/harness/features/*/feature.json`, which in the main checkout cannot see a feature whose
directory exists only on its own branch or worktree. That is what let `FEAT-44` be coined twice
today. It is a real defect in the plan door, and it is **not this feature**: it fires at feature
CREATION, before a brief or a plan exists, so none of the three readers could reach it, and its fix
is an enumeration source rather than a reader question. It belongs in the backlog as its own row
against the plan door's feature enumeration. Named here so it is not lost, not so it is absorbed.

## Approval

status: pending
