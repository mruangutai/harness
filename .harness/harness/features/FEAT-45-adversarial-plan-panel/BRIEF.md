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
- REQ-02: An **independent-model** reader — spawned OUTSIDE the dispatch chain that authored the
  plan, and therefore holding none of its reasoning, **and running on a different model** — answers,
  of the drafted plan: **what here should not be built at all?** The lead that hosts it must be
  *permitted* to spawn it: measured 2026-08-29, the host enforces an agent's `spawns:` list as a hard
  allowlist at preflight and refused a `general-purpose` dispatch with `Cannot spawn
  'general-purpose'. Allowed: harness-product-lead,harness-eng-lead,harness-validator-lead`, so a
  reader absent from `harness-validator-lead`'s list cannot answer anything. The MODEL half survives
  lead dispatch, measured 2026-08-30: `dispatch-guard.sh:41-51` blocks a lead from **passing**
  `model:` in a dispatch — its own comment states the rule it enforces, that a member runs on the
  model pinned in its agent frontmatter and that pin is org design — and it does not strip the
  target's own pin; it exits 0, recording no claim, for any persona not prefixed `harness-`. So a
  reader persona carrying its own `model:` pin runs on that model when a lead spawns it without
  passing one. The reader is therefore independent of the authoring chain AND of the authoring model.
  This is more than DEC-170's turn-level `advisor` channel can supply here, which is unattached on
  this workstation (`advisorModel` absent from `~/.claude/settings.json`, contradicting DEC-170's
  recorded `:112`) — that measurement bounds the CHANNEL, not the frontmatter pin, and the earlier
  inference from it that model independence was unavailable was FALSE.
- REQ-03: The drafted plan is goal-checked against the operator's **stated intent**, not against the
  brief the plan was written from.
- REQ-04: The plan is read for scope: **which tasks serve no live requirement, and what does the
  feature actually need to ship?** — covering orphan traces in both directions, dependency shape, and
  `verify:` blocks asserting something a predecessor deletes.
- REQ-05: The independent-model reader's return is normalized into a contract-compliant digest before
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
- REQ-14: Where the panel's independent-model reader cannot be resolved on the workstation the panel
  runs on, the panel **skips that reader and records the skip durably** in the panel result, naming
  the persona and stating the reason. This is not hypothetical: the reader's persona definition lives
  outside this repository (D-14) while the team file ships as standing doctrine (D-09) to every
  project the factory is pointed at, so a project where the persona simply does not exist is the
  normal case rather than the edge one. A skipped reader is never recorded as, or reported as, a
  reader that ran and returned no findings; and a reader missing from the record with no skip entry
  is refused rather than passed, so the panel can never report clean because a reader never ran.

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
  findings of substance, not padding to justify the run. **The zero-findings case is graded, not
  skipped:** where a reader returns an empty `findings` list, what the operator grades is the
  *transcript of that reader's return in the lead's digest* — an empty list, explicitly reported as
  empty with the reader named, IS "earned its spawn" and passes, because T-02's own prompt makes an
  empty list the correct and preferred result on a clean plan. It fails only if the reader's return
  is missing from the digest altogether, or the reader returned findings the operator judges to be
  padding. A reader that found nothing on a plan the operator believes is clean has done its job.
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
- SC-15: The adversarial reader's persona, read from the team file rather than hardcoded, is a member
  of `harness-validator-lead`'s `spawns:` list in `.omp/agents/harness-validator-lead.md` **and** of
  `SPAWNS["harness-validator-lead"]` in `sync-agent-adapters.py`, asserted as two separate checks.
  This criterion grades the allowlist's CONTENT, which is all a runner in this repository can reach:
  no runner here performs a live spawn, so nothing automated can observe the preflight decision
  itself. Falsified by either place omitting the persona — measured 2026-08-29, the host enforces
  that list as a hard allowlist at preflight (`Cannot spawn 'general-purpose'. Allowed:
  harness-product-lead,harness-eng-lead,harness-validator-lead`), so an omission there makes the
  panel unrunnable while every other criterion here still passes. Asserting only one of the two
  passes while the other drifts, and no assertion is made about `.claude/agents/**`, whose generated
  frontmatter carries no `spawns:` key at all. The persona graded is `fable-advisor` (D-14) — not one
  of the 16 harness agents, and carrying its own `model:` pin, which is what makes REQ-02's model
  half true rather than aspirational. Nothing here asserts that persona's own definition file exists
  in this repository, because it does not and must not: REQ-14 covers its absence.
  verify: automated      evidence: unit
- SC-16: On the first live `/harness-plan` after this ships, `harness-validator-lead`'s dispatch of
  the adversarial reader is not refused at preflight and the reader returns. Falsified by a
  `Cannot spawn ...` preflight refusal naming the reader, or by the persona resolving to no runnable
  agent. This is `uat` and not `automated` for a measured reason: SC-15 can only grade the list's
  content, and whether the host RESOLVES the pinned persona to a real agent once the allowlist admits
  it is not determinable from anything on disk — the observed refusal fired at the allowlist, before
  resolution. This is the one criterion that closes the gap the c1 fix cycle found, where all ten
  drafted tasks graded text on disk and none performed a spawn.
  verify: uat
- SC-17: Against a fixture whose panel result records the adversarial reader as `skipped` with a
  named persona and a stated reason, the machine check reports the skip and does NOT report the plan
  as having no panel result; against the same fixture with that reader absent from the record
  altogether and no skip entry, the check refuses the signed state. Falsified if a skipped reader is
  indistinguishable in the record from a reader that ran and returned an empty `findings` list, or if
  a reader's unrecorded absence passes. The refusing direction must be demonstrated failing on the
  pre-change tree before the change is accepted, by the same marker-anchored mutant D-13 mandates.
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
- **Model independence IS claimed, and what carries it is on disk rather than in a test.** The
  persona the team file names carries its own `model:` pin in its own frontmatter — greppable, not
  inferred — and measured 2026-08-30 the dispatch guard does not strip it: it blocks a lead from
  *passing* `model:` and exits 0 for any non-`harness-` target (see REQ-02's measurement). The
  earlier claim in this section, that model independence was unprovable and therefore not claimed,
  rested on a false inference from that guard and is struck. What remains ungraded is a different
  question: whether an independent MODEL finds MORE than a same-model reader would. That is
  unmeasured, n = 0, and is a platform question rather than this feature's. SC-15 grades the
  mechanical half — that the named persona is admitted by the allowlist — and SC-17 grades the case
  this repository cannot supply the definition for at all.
- **No runner here performs a live spawn**, so the preflight decision itself is unautomatable in this
  repository: SC-15 grades the allowlist's *content* and nothing more. What carries the live half:
  SC-16, the operator's own observation on the first `/harness-plan` after this ships. This gap is
  exactly how the c0 draft shipped an unrunnable panel past ten green tasks.

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
  reader and can never validate its return by running anything — and it can never compute a finding's
  `PF-` id either, which is why identity is `harness-pm`'s single write at transcription.
  **Corrected 2026-08-29 (c1):** holding `Agent` is necessary and *not sufficient*. The host also
  enforces the caller's own `spawns:` frontmatter as a hard allowlist at preflight, so the reader's
  persona must be added to `harness-validator-lead`'s list (`.omp/agents/harness-validator-lead.md`)
  or the dispatch is refused before the guard is ever consulted.
  **Extended 2026-08-30 (c2):** the persona this feature ships, `fable-advisor` (D-14), is likewise
  not a seventeenth agent — measured, its definition lives at `~/.omp/agent/agents/fable-advisor.md`,
  in the operator's HOME and outside this repository, and `.omp/agents/` still holds exactly 16
  `harness-*.md` files. Bringing that definition into the repository is agent distribution and is
  explicitly out of scope. That location is also precisely why REQ-14's absent-persona behaviour is
  mandatory rather than optional: the team file ships as doctrine (D-09) to projects where that HOME
  definition does not exist.
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

status: approved
approved-by: operator
date: 2026-08-30

**SIGNED 2026-08-30, first signature.** Covers REQ-01..REQ-14 and SC-01..SC-17.

The independent-**model** claim in REQ-02 and REQ-05 is signed as restored. An earlier draft weakened
it to independent-*context* on the finding that no `harness-` lead may select a model for what it
spawns. That finding is true and the inference from it was false: `dispatch-guard.sh:41-51` blocks a
caller from **passing** `model:`, and never touches a dispatched agent's own frontmatter pin — the
guard's own comment states that rule. The reader is therefore repinned from `general-purpose`, a
platform built-in with no definition file and so no pin, to `fable-advisor`, whose definition carries
`model: anthropic/claude-fable-5`.

**REQ-14 is the price of that pin and ships with it.** The advisor's definition lives in the
operator's HOME, not in this repository, while the team file ships as doctrine to every project the
factory is pointed at. Where the reader cannot be resolved the panel skips it and records the skip
durably; SC-17 grades that a recorded skip is distinguishable from a reader that never ran. The skip
WARNS rather than fails, deliberately: a hard failure would break the panel everywhere the definition
is absent, and bringing the advisor into the repository is agent distribution, which is out of scope.

**The honest limit is unchanged and signed as-is:** whether an independent model finds *more* than a
same-model reader with a clean context is unmeasured, n = 0. Finding quality stays ungraded; SC-11 is
an operator eyeball. That is a known gap, not an oversight.
