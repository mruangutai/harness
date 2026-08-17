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
spawns, none of them editing. The value comes from four independent readers, not one reader
carrying four checklists — a single reader trades one angle's depth for another's. The lead
does not read the angles itself and does not collapse two angles into one spawn. Where the
squad is smaller than four, the nearest specialist takes more than one angle in separate
dispatches.

Readers are drawn from the eng squad by adjacency to the domains the change touches.

**Every dispatch names two things:** the scope, as a concrete diff or file set; and what is
already settled and therefore not flaggable. A signed decision re-litigated as a finding is
noise, and it costs a reader's whole run.

**Every finding carries five parts:** file, line, one-line summary, the concrete cost, and the
alternative. **An empty return is a real and expected result** — say so in the dispatch, so a
reader does not manufacture findings to look useful.

The angle prompts these four sections distil from are recorded verbatim, eight of them, in
`research-FEAT-23-simplify-angles-source.md`.

## REUSE

Flag work that re-implements something the tree already has.

On a **plan surface**: a verify clause that hand-rolls a check an existing script already
performs, or a task intent restating a procedure another task owns.

On a **code surface**: a constant, helper or fixture restated where an importable one exists.

Name the existing thing by file and line, and name the concrete cost — usually that two
spellings must now be edited in lockstep, and the one nobody remembers goes stale silently.

## SIMPLIFICATION

Flag unnecessary complexity the change adds.

On a **plan surface**: the same fact asserted twice through different spellings, one rule
restated in two places that can drift apart, and dead references to a shape that no longer
exists after a revision.

On a **code surface**: redundant conjuncts, comments that narrate a change instead of stating
the present fact, and pipelines with a simpler equivalent — but **only where the simpler form
preserves the anchoring semantics the original fought for**. An anchor that took rounds to get
right is not complexity to be trimmed.

## EFFICIENCY

Flag wasted work the change would actually do, costed honestly.

Judge **minutes, and hot-path milliseconds**. A gate that runs at every session entry or every
write earns scrutiny that a one-shot build step does not. Measure before flagging: a suite run
you suspect is slow may be a fraction of a second.

Deliberate full-suite runs at boundary steps are **not** waste — they are the evidence the
boundary exists. Say so rather than flagging them.

On a **plan surface**: a step that re-runs a whole suite where a targeted case binds equally,
or the same file read repeatedly across sequential tasks where one pass could feed several.

On a **code surface**: repeated I/O, work added to startup, and long-lived objects built from
closures that keep an entire scope alive.

## ALTITUDE

Judge whether each change sits at the right depth, and give an explicit recommendation.

Ask: is the capability at the right home, or bolted onto a caller? Is there **one**
authoritative statement of a rule, or several that can drift? Are the accepted residuals right
to accept — and does a deeper fix exist that does not reopen a settled scope?

A special case layered on shared infrastructure is a sign the fix is not deep enough. So is a
methodology that lives only in one session's prompts.

**Every altitude finding ends with one of three words: fold-in, briefing-row, or leave.** A
finding with no recommendation makes the reader decide twice.

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
  gap in the rule that this pass is a build-side step applied before `review_sha` pins. It does
  not weaken that rule and it does not move the step.

Skip any finding whose fix would change intended behaviour, reach well outside the reviewed
scope, or that you judge a false positive — and **note the skip with its reason** rather than
arguing with the reader.

## Who never runs this pass

Nobody in the validation tier. The fixer is never the judge: a reviewer's authority comes from
being read-only on the source it rules on, and a seat that has already applied edits to a diff
cannot then certify it. This pass applies edits, so it belongs to the build side.

The skill depends on nothing outside this repository. It names no plugin, no slash command,
and no file outside the tree.
