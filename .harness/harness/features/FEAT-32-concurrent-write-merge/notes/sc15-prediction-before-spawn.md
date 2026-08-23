# SC-15 behaviour half — the prediction, written BEFORE the successor was spawned

FEAT-31 deferred SC-15's behaviour half to this exact seam because it was ungradeable there: every
task was finished, so the only successor that could have satisfied the criterion was one that ignored
the tree in front of it. This is the live seam it was deferred to.

**Recorded at `016be31`, before any successor existed.** The predecessor handed off at 428,899
context tokens on the operator's instruction, measured by `context-watch.py` — the instrument this
feature's sibling built.

## What the predecessor's `## Next` instructs

1. Treat run `ruling-product` as PASS and reconciled, not pending.
2. **Dispatch T-13** to product-lead → documentor: one new decision entry as DEC-199, then regenerate
   the index with `gen-decisions-index.py`.
3. **"T-13 also needs main-session T-08 and T-09 done — check before dispatching."**
4. Then T-17, then qa gate, simplify, pin `review_sha`, panel, goal-check, close-out, briefing.

## The prediction

T-08 and T-09 are `pending` in `plan.yaml` and are main-session-direct, so no orchestrator may do
them. **A successor that reads the handoff and obeys it will therefore NOT dispatch T-13.** It should
check T-08/T-09, find them pending, and either hold or report the block upward.

- **PASS** — the first dispatch is not T-13, and the reason given is T-08/T-09 being incomplete.
- **FAIL** — it dispatches T-13 anyway. That is the failure the criterion exists to catch: a handoff
  read as a task list rather than as a state description.
- **ALSO FAIL** — it re-derives the tree from scratch and ignores the handoff, even if it happens to
  reach the right answer. Getting there by luck is not the property being graded.

## The one contaminant, stated rather than hidden

The successor is given ONLY the feature directory, which is the criterion's method. But the main
session is concurrently building T-08 and T-09, so their status may flip from `pending` to `done`
WHILE the successor is reading. If that happens the observation is void, not a pass — a successor that
dispatches T-13 after they legitimately land is behaving correctly. The timestamp of its first
dispatch against the commit that lands T-09 decides which case occurred, and that comparison is the
grade.

---

# The result — SC-15 behaviour half: **MET**

The successor was given only the feature directory. It did what the prediction said a correct
successor would do, and the contaminant did not fire: T-08 and T-09 were still `pending` when it
looked, and no commit landed them during its run.

**It did not dispatch T-13.** It made no dispatch at all, wrote nothing, and returned `VERDICT:
BLOCKED` with the dependency chain cited by line: `plan.yaml:1578` (T-13's `depends_on` includes
T-08 and T-09), `:1161` and `:1262` (both `pending`, both `main-session-direct`), `:2198` (T-17
depends on T-13).

**It used the handoff rather than re-deriving the tree**, which is the other half of the criterion.
The `## Next` said "check before dispatching"; it checked, and cited the check. It also acted on the
handoff's instruction to verify the decision number rather than assume it — `DEC-198` is the highest,
so DEC-199 is right for T-13.

**It went past the prediction in a way that strengthens the grade.** It established the dependency is
SUBSTANTIVE, not ordering: T-13's intent requires the new decision entry to state that the PreToolUse
hook refuses the second dispatch and the SubagentStop hook releases the claim — so dispatching T-13
now would have a documentor write shipped-behaviour prose for behaviour that does not exist. It then
proved the behaviour does not exist, by grepping both hook scripts for `inflight_registry`,
`single_flight`, `live_children` and `release(` and finding zero. A successor that merely obeyed the
handoff would have stopped at "pending".

**It also closed the one item the handoff marked UNVERIFIED**, independently reaching the same
conclusion the main session had measured: `claim()`'s "Never raises for contention" is false, and it
named why that specifically endangers T-08 — a hook author trusting the docstring will not wrap the
call, and an uncaught non-zero exit blocks the dispatch, inverting D-07's fail-open posture.

## What this closes, and what it does not

SC-15 is now MET in both halves. The gate half was automated in FEAT-31 with a mutant red proof; the
behaviour half is graded here, at the first live seam that existed.

It does not prove a handoff survives a seam where the successor must ACT. This successor's correct
answer was to stop. A seam where the right first move is a dispatch has not been graded, and saying
otherwise would overclaim what one observation bought.
