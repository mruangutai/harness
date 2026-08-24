# Operator answers — FEAT-35 build, T-04 unblocked — 2026-08-24

The operator answered both blocking questions. This is the ONE consolidated set (DEC-176).

## Q1 — APPROVED. T-04's decision id moves DEC-200 -> DEC-201.

**pm makes the edit, under the operator's re-signature.** The operator was offered the faster route
— the main session editing `plan.yaml` directly — and declined it: that file resolves to
`harness-orchestrator, harness-pm`, and going around the domain guard to save a spawn is not a
trade this project makes.

**Verified independently by the main session before the operator was asked, so pm need not
re-derive it:**
- `DEC-200` is FEAT-26's, `## DEC-200 — The pull request number is derived at ship time...` at
  `.harness/harness/docs/DECISIONS.md:6729`, index row 218, merged at `2c0a33c`.
- `DEC-201` is FREE: zero occurrences in `DECISIONS.md` and zero in `DECISIONS-INDEX.md`.

The edit is mechanical: T-04's `intent:` and `verify:` in `plan.yaml`, DEC-200 -> DEC-201
throughout, including the `grep -q "^- DEC-201 "` index assertion. **Change nothing else.** It is an
id correction forced by a collision, not a scope change, and the operator's re-signature covers
exactly that.

## Q2 — ALREADY FIXED by the main session, and the reason matters.

`.claude/skills/harness/SKILL.md:50` cited `(DEC-200)`. **That citation was the MAIN SESSION's
error**, not pm's and not the lead's: T-01's `intent:` said "Point at the decision recorded by T-04"
without naming a number, and the main session chose 200.

It now reads `(DEC-201)`, changed at the main session's own hand under T-01's existing
`main-session-direct` lane. Rationale for acting rather than asking: a citation pointing at
FEAT-26's LIVE decision reads as resolved and is wrong, which is strictly worse than one pointing at
a decision not yet written. Re-checked after the change — T-01 PASS, T-03 PASS,
`test-orchestrator-playbook.py` ALL PASS. `test-orchestrator-playbook.py` does not pin the number,
so nothing else moved.

**So T-04 has no SKILL.md work.** Land DEC-201 and the citation resolves.

## Q3 — ACCEPTED. The four INV-26 violations stand.

`#798`/`#799`/`#800` read `Backlog` against plan `done`; `#801` reads `Building` against plan
`pending`. Three close from the pull request's `Closes` lines at merge — `Done` is GitHub's write,
not ours, which is FEAT-33's whole ruling. **Do not move cards by hand to quiet the gate.** The
divergence existed before the mirror was opened and was invisible only because no cards existed;
opening it made a true state visible. That was the right call.

## Q4, Q5, Q6 — noted, not acted on in this feature.

- **Q4** (T-05 assertion 6 is line-scoped, so a reflow reddens it and a regression one line away
  stays green): a real weakness, correctly raised rather than silently edited. It is the signed
  plan's verbatim contract. The main session will file it.
- **Q5** (no DEC-NN collision guard, though `check-plan-routes.py` guards INV-NN as of `3df18d3`):
  this feature is the second instance — FEAT-26 and FEAT-35 both computed "next free is 200" and
  merge order decided it. The main session will file it. **It is not fixed here.**
- **Q6** (D-08 versus `run-unit-tests.sh` being a step of the required `integration` job at
  `.github/workflows/tests.yml:81` and `:87`): pre-existing DEC-174 enumeration gap, out of scope,
  already recorded in the plan.

## SC-05 — MEASURED AND PASSING. Your handoff note understates it.

The build-phase handoff records SC-05 as UNVERIFIED because that phase's own children ran 131s and
324s. **That is true of your phase and false of the feature.** The main session measured SC-05
directly against the PLAN-phase orchestrator's sidecar:

- agent `af05a0d5a321741b6`, sidecar under
  `~/.claude/projects/-Users-molchairuangutai-GitHub-harness/e69cbdc1-.../subagents/`
- **longest SURVIVED gap 1057.1s** — `15:34:10.019Z` -> `15:51:47.145Z`, over the 600s watchdog
- **0** Bash calls made only to stay alive; not killed at ~600s; closed with its own text
- lifespan 3275.8s, 216 events, 3 dispatches

**Control, so the measurement discriminates:** all 115 orchestrator sidecars on this machine were
swept and exactly two fail — `a95e1e6e97e80de87` with **342** `echo hold` calls, and
`a73a98fe020a2ce41` dead at **642.7s** with zero assistant events. Both are #744's incidents and the
numbers match that ticket independently.

**The limit, which must survive into the record:** that orchestrator ran under a DISPATCH-LEVEL
OVERRIDE, not under the rewritten playbook — the rewrite is committed at `d7e8c66` in the worktree
only, and a spawned agent loads its skills from the MAIN checkout. So this proves the BEHAVIOUR
survives a 1057s wait; it does NOT prove the rewritten playbook causes it. SC-05's wording is met
literally. Whether its spirit needs one post-merge run is a reviewer's call and must be written down
as such, not resolved silently.

Evidence file: `scratchpad/sc05-evidence.md` (session scratchpad, outside the repo). The checker
`sc05-check.py` was deliberately NOT added to the repository — that would be scope outside the
plan's five tasks.

## After T-04

Return `awaiting_user`. The main session commits, then decides the validate phase.
