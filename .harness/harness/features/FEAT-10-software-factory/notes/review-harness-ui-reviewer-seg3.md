# harness-ui-reviewer — FEAT-10 seg3 — Mode A (pre-build) — DESIGN.md contract review

VERDICT: FAIL. `prototype_required: false` is correct and not disputed. C-3, the CLI exit/stream
contract that this dispatch specifically hands down, is not yet sound: three findings change what
must be *built*, not just what is written down, so this is not a wording pass.

## Scope taken

Judged: C-1 (station predicates), C-2 (issue-authoritative / stderr-report), C-3 (stream split, exit
vocabulary, failure grammar, exception trap), C-4 (issue body/label shape), the squad-convention
clause, and the `prototype_required: false` call — against `BRIEF.md`'s REQs/SCs and `plan.yaml`'s
tasks/decisions. Not judged: rendered board legibility (column-header width, card density, five
factory labels sharing one colour `5319e7` per T-03) — GitHub renders it, this role reads source, so
that dimension is **not verifiable from source; SC-07's UAT step is the only thing that carries it.**

## Q1 — Is DESIGN.md a sound contract?

Mostly. C-1/C-2/C-4 are falsifiable and appropriately scoped (predicates, not adjectives; a named
visibility gap instead of a silent one). C-3 is where soundness breaks — see Q3 below, three findings,
all `must_fix`.

## Q2 — Clause ↔ task mapping, both directions

Forward (clause → task) is solid: C-1 → T-01 (station keys) + T-04/T-05/T-07 (station writes); C-2 →
T-05 steps 5–6 (lost_race, no corrective write); C-3 → T-11 (shared module) + every CLI-bearing task;
C-4 → T-04 step 5–6.

Reverse (task → clause) has a gap: **T-01 is the task that records the operator's three station
display-name answers (Q1) and cites no clause.** C-1's naming rule — one word, distinguishable at a
glance, 1:1 to a predicate, not a verb — does not travel to the task that writes the words, so nothing
in T-01's verify or intent checks the rule the contract exists to enforce.

- **must_fix (low-med), T-01 / C-1:** add a one-line citation of C-1's naming rule to T-01's intent, so
  the rule that discharges the prototype's job for Q1 (see Q5) is actually attached to the task that
  records the answer.

## Q3 — Is the C-3 exit vocabulary consistent at every exit path?

Traced T-04, T-05, T-06, T-07, T-11 against the exit table. Two real defects, both on the clause this
dispatch names as load-bearing.

**(A) Exit 2's "Nothing was mutated" <!-- ok-stale --> does not hold uniformly, and recovery is
asymmetric across the three tools where it breaks — that asymmetry is the actionable part, not the
wording.**

- T-04: plan.yaml's own test case says feature.yaml "carries the issue number after the first creation
  even when the board add then raises GhError" — that GhError is in `expected`, so the tool exits 2
  after a harness file was already mutated. **Recoverable by design** — T-04 step 4 skips
  already-recorded tasks, so a re-run resumes cleanly. Not a defect on its own.
- T-07: step 3 pushes the branch before step 4's `gh pr create`; a GhError there exits 2 with the
  branch already pushed to the target repo. **Recoverable on retry** — pushing the same branch again
  and creating the PR is idempotent enough to complete the journey.
- T-05: steps 5–6 write `factory:claimed` + assignee, confirm ownership, **then** step 7's
  `project_field_set` can raise GhError → exit 2. At that point the issue is claimed but the board
  still shows `ready`. **Not recoverable by the tool that hit it** — the confirmed-owner agent has no
  path back to finish the claim, and the *next* `factory_claim.py` run re-reads the issue, finds
  `factory:claimed`, and exits 3 (lost race) against an owner who no longer knows it won. The issue is
  now permanently stuck: claimed, station `ready`, nobody working it, and nothing in DESIGN.md or
  plan.yaml names this state or what the operator does about it. This is exactly the C-2 drift clause
  ("the issue is claimed while the board still shows ready ... the next poller re-reads the issue and
  exits 3") — but C-2 frames that as a benign, correctable-on-next-poll case, when for the agent that
  actually holds the claim it is a dead end.

  **must_fix (high), C-3 / T-05:** C-3's exit table must name each tool's point of no return instead
  of asserting one invariant across all six, and T-05 must state what happens to a claim stuck between
  steps 6 and 7 — at minimum, a documented manual/operator recovery path, since the design's own
  reconciliation clause explicitly excludes automatic correction from this increment.

**(B) The board's 200-item page limit makes exit 1 unsound — the same failure class SC-10 exists to
prevent, in a different place.**

T-03's `project_items` is specified as `project item-list <number> --owner <owner> --format json
--limit 200` with no pagination. T-05 step 2 filters that one page for `ready` items; step 3 reports
"no work available" (exit 1) when none remain **in the page it read**, not when none exist on the
board. A fleet with more than 200 open items in flight will report exit 1 — "nothing to do" — while
ready work exists beyond the cutoff. SC-10's entire point is that exit 1 must mean only "nothing to
do," never a masked failure; an untested page boundary produces exactly that confusion through a
different door than the one SC-10 closed.

**must_fix (high), C-3 / T-03 / T-05:** either paginate `project_items` to completion or make the
200-item cutoff an explicit, load-bearing assumption in C-3/D-04 with a stated ceiling on the fleet's
concurrent open-item count, so exit 1's meaning stays uniform as designed.

**(C) The failure-message grammar is one declared shape and three actual ones.**

C-3 states one 5-part grammar and says "SC-10's 'loud message' is checkable against it." T-11 in fact
specifies three incompatible shapes: the full grammar (`factory: {tool}: {what}: {value} — {next}`);
`nothing_to_do`'s short form (`factory: {tool}: {why}`, no value slot, no em dash); and the `expected`
branch, which prints `factory: {tool}: {str(exc)}` with the whole four-part body already preformed at
the raise site. No single assertion covers all three, so the grammar as written is not checkable
end-to-end. Separately, `: ` is both the field separator and legal content inside `<what failed>` and
`<value>` (T-03's own GhError example puts captured `gh` stderr — which routinely contains colons —
after the em dash), and the generic-exception fallback embeds `{type(exc).__name__}` in the value
slot, which is a bare exception class name and contradicts C-3's own "never a bare exception class."

**must_fix (med), C-3 / T-11:** state plainly that stderr is human-facing only and machine callers use
the exit code plus stdout's single JSON document — nobody should be building a stderr parser against
this grammar — and add an explicit, named carve-out for the generic-trap message's type-name slot
rather than leaving it as an unstated exception to the class-name rule. Do not remove the
`FACTORY_DEBUG` affordance; it is the right debugging tool, just not what C-3 as written permits.

T-06 (workspace) and the `nothing_to_do`/`lost_race`/happy paths on T-04/T-05/T-07 were traced and are
consistent — no further exit-path defects found there.

## Q4 — CLI accessibility: colour-only signalling, machine-readability

No colour-only signalling: station is a text option name and every factory label carries a distinct
name, so meaning is never colour-dependent. T-03's single shared label colour (`5319e7` for every
factory label) cannot be assessed as good or bad from source — it is a rendered-board appearance claim
this role cannot observe; flagging it as a positive would be exactly the false all-clear the role
exists to avoid. Machine-readability: see Q3(C) above — that is the substantive a11y/parseability
finding for this review.

## Q5 — Is `prototype_required: false` correct, and are its flip conditions right?

**Correct, not disputed.** The operator-facing surfaces are GitHub's own rendering (board, issue) and
terminal text with no component model; nothing here is a surface the harness renders. C-1's naming
rule (one word, distinguishable at a glance, 1:1 to a predicate, not a verb) is what discharges the
prototype's job for Q1's three words — a falsifiable rule stands in for a mockup precisely because
there is no rendering to mock up. The three flip conditions (harness gains a rendered surface; #186's
saved views land as harness-configured pre-issue-existence; the user asks) are concrete and correctly
scoped — no addition needed.

## must_fix (recap, each names its clause/task)

1. **C-3 / T-05 (high):** exit-2 recovery is asymmetric; T-05's steps 6→7 gap leaves a claim
   permanently stuck with no stated recovery. Name the point of no return per tool; state T-05's
   recovery path.
2. **C-3 / T-03 / T-05 (high):** `project_items`' unpaginated 200-item limit can make exit 1 report
   "nothing to do" while ready work exists — the SC-10 failure class through an untested door.
3. **C-3 / T-11 (med):** one declared failure-message grammar, three actual shapes; state stderr is
   human-only and add a named carve-out for the trap's exception-type slot.
4. **C-4 / Q3 / D-09 (med):** DESIGN.md's "Open questions" still lists Q3 as open and C-4 still says
   "do not implement it ahead of Q3" <!-- ok-stale -->, while plan.yaml's D-09 already resolved it and
   T-04 already implements the `feature:<FEAT>` label. DESIGN.md and plan.yaml ride one signature
   (DEC-75) — the user should not be asked to sign a document that misstates what the plan it is
   paired with already does. Mark Q3 resolved by D-09; drop "(proposed, Q3)" from C-4's label
   vocabulary line.
5. **T-01 / C-1 (low-med):** the task recording Q1's answers cites no clause; add the citation.
6. **T-05 / REQ-03 (low, cheap fix, high consequence if skipped):** step 4 reads `assignees` (GitHub's
   field is plural/additive) but step 6 compares "the assignee is not exactly `--as`" (singular).
   `assignees == [login]` (exact single-element match) and `login in assignees` are both defensible
   readings of that sentence and disagree on whether a concurrent-assign race is detected. Pin the
   exact semantics in T-05's intent.

## Open questions

- Even with (6)'s exact-match semantics pinned, GitHub's `--add-assignee` is additive, not exclusive:
  under a true concurrent claim both agents' assign calls can succeed, both re-reads then see
  `assignees != [self]`, and both exit 3 — leaving the issue labelled `factory:claimed`, station
  `ready`, and **owned by nobody**. Exit 3's stated meaning is "another agent owns the issue," which
  this scenario falsifies (nobody owns it). This is a REQ-03 atomicity question for validator-lead /
  backend-dev, not a CLI-legibility question for this role, so it is raised here rather than folded
  into a must_fix.

## Verification

- Reasoning traced directly against `DESIGN.md`, `BRIEF.md`, `plan.yaml` at the paths given in the
  dispatch (no diff exists; files read from disk).
- `docs/harness/DECISIONS-INDEX.md` greps for `DEC-75`, `DEC-62`, `DEC-138`, `DEC-174`, `DEC-179`,
  `DEC-182`; `DEC-75` (prototype trigger = end-user interaction, one signature with plan) and `DEC-62`
  (mode split, authorship vs audit) opened in full — both directly load-bearing for Q5 and this
  dispatch's framing.
