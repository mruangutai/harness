---
name: harness-simplify
description: The four-angle quality pass — reuse, simplification, efficiency and altitude, each a separate read-only reader. Run it as the last build step before `review_sha` pins, and on a plan draft before it goes for signature. NOT preloaded; read it when you are about to run the pass.
user-invocable: false
---

# The four-angle quality pass

This pass improves the quality of changed work. It does not hunt for correctness bugs — the
review panel does that, later, against the pinned diff.

**Run it before the gate that pins the text.** On a ship flow it is the last build step,
after the qa gate and before `review_sha` is pinned, so the panel reviews the final text. On
a plan flow it runs on the draft before the operator signs. A pass that runs after the pin
costs a re-review round; a pass that runs after the signature can apply nothing at all.

**The pass is four separate, parallel, read-only dispatches.** One spawn per angle, four
spawns, none of them editing. The lead does not read the angles itself and does not collapse
two angles into one spawn — one reader carrying four checklists trades one angle's depth for
another's. Where the squad is smaller than four, the nearest specialist takes more than one
angle in separate dispatches.

Readers are drawn from the eng squad by adjacency to the domains the change touches.

**Every dispatch names three things:** the scope, as a concrete diff or file set; what is
already settled and therefore not flaggable — a signed decision re-litigated as a finding is
noise, and it costs a reader's whole run; and the one angle file the reader follows, by path:
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-simplify/references/angle-<reuse|simplification|efficiency|altitude>.md`.
The angle file carries the finding shape (five parts: file, line, summary, concrete cost,
alternative) and the rule that an empty return is a real result; you do not restate either.

Source prompts (eight, verbatim):
`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/FEAT-23-ship-flow-fixes/notes/research-FEAT-23-simplify-angles-source.md`.

## The four angles, in one line each

- **REUSE** — the change re-implements something the tree already has.
- **SIMPLIFICATION** — the change adds complexity a simpler form would not, judged by the
  deletion test in `harness-codebase-design`.
- **EFFICIENCY** — the change does wasted work, costed in minutes and hot-path milliseconds;
  deliberate boundary suite runs are not waste.
- **ALTITUDE** — the change sits at the wrong depth; every finding ends fold-in, briefing-row,
  or leave.

On a **plan surface** the readers judge `plan.yaml`/`BRIEF.md` drafts; on a **code surface**,
the changed diff. Each angle file spells both.

## Applying what comes back

Deduplicate findings that point at one line or one mechanism, then route each by the surface
it touches.

- **On a plan surface the pass is FLAG-ONLY.** Findings go back to `harness-pm`, which applies
  them to its own draft. No other seat may edit `plan.yaml` or `BRIEF.md` — the domain guard
  grants those to `harness-pm` alone. This is forced, not stylistic.
- **On a code surface the build side applies**, by whichever specialist owns the touched file,
  and the suites re-run after the apply. Where two specialists both hold a touched path — `bin/`
  resolves to `harness-backend-dev` and `harness-dev-ops` — the lead picks one and **records
  which it picked and why** in the segment digest. An unattributed pick is unreviewable.
- **Where the domain guard resolves a touched path to NOBODY, the finding is FLAG-ONLY.** It
  returns to the orchestrator with its concrete alternative, and the pass does not attempt the
  apply: a dispatched write to an ungranted surface is refused mid-run, and the segment comes
  back with nothing applied and the findings lost. State this plainly — it is an implementation
  gap in the rule that this pass is a build-side step applied before `review_sha` pins.

**The apply may not delete or weaken an assertion.** This step runs after the qa gate has
PASSed, and that gate is more than a green suite — it is the test-matrix judgement and coverage
adequacy, which nothing re-assesses afterwards. So a finding of the form "this conjunct asserts
the same fact twice" becomes a backlog row, never an apply.

**The apply has a ceiling of one fix.** If an apply reddens the suites and one fix does not
restore green, revert the apply and file the finding as a backlog row. This is the only
permanent build step with no `max_cycles` of its own, so without the ceiling the loop is
unbounded at the last step before the pin.

Skip any finding whose fix would change intended behaviour, reach well outside the reviewed
scope, or that you judge a false positive — and **note the skip with its reason** rather than
arguing with the reader.

## Who never runs this pass

Nobody in the validation tier. The fixer is never the judge: a reviewer's authority comes from
being read-only on the source it rules on, and a seat that has already applied edits to a diff
cannot then certify it. This pass applies edits, so it belongs to the build side.
