# Contract review — ESC-1 enforcement delta — receipt

**One high-severity omission: SC-13/SC-22's per-skip distinctness contract covers the BLOCKED skip
only, not the "claim marker already taken" skip — the exact path the D-13 residual takes. In a mixed
ready column (one residual + several genuinely blocked items), the operator's stderr shows N `blocked
by T-NN` lines and nothing for the residual, reads "healthy, waiting on blockers," and the residual
that BRIEF:125-126 says accumulates without bound stays invisible indefinitely.** Two lower-severity
gaps besides. Everything else audited holds on the text as written.

## Q1 — Does SC-22 genuinely falsify un-enforcement? PASS, with one low-severity note

Confirmed the three named directions falsify as claimed:
- **Direction 1** (SKIP AND CONTINUE, `BRIEF.md:159-163`, `plan.yaml:1191-1197`) — asserted on
  `create_ref`'s issue-number identity, not exit status. A blocker-ignoring tool claims the blocked
  (lowest-numbered) candidate here and fails.
- **Direction 2** (EVERY CANDIDATE BLOCKED, `plan.yaml:1198-1201`) — enumerates "no create_ref, no
  label, no assign, no field set", i.e. `create_ref` must be **absent from the call list**, not merely
  non-mutating in effect. This is what makes the direction order-independent: a blocker-ignoring tool
  attempts a claim on *whichever* candidate it reaches first, regardless of sort order, and that
  attempt alone fails this case. This is the load-bearing reason the "sorts candidates in some other
  order" and "hard-codes/correlates with the fixture" hunts came up empty — any implementation that
  still tries to claim in an all-blocked column is caught here regardless of which candidate it picks.
- **Direction 3** (ALL BLOCKERS CLOSED, `plan.yaml:1202-1205`) — explicitly "the same fixture with
  every blocker issue closed" (`:1202`), reusing direction 1's candidates. So the anti-vacuity clause
  **does** require the same ready column as direction 1; there is no gap from fixture drift between
  them. (BRIEF.md's own SC-22 prose does not say "same ready column" in so many words — it says "the
  formerly blocked lowest-numbered candidate" — so the identity guarantee currently lives in T-05's
  task text, not in the criterion's own wording. Low severity: not a live risk today since T-05
  pins it, but if T-05 is ever revised independently of BRIEF, the anti-vacuity guarantee could drift
  with no criterion text to catch it.)

**Fourth-way hunt, explicit results:**
- Blocker-ignoring tool: fails direction 2, any sort order (see above).
- Non-ascending sort order (correct or incorrect enforcement): does not open a false-green path,
  because direction 2 does not depend on sort order.
- Refuses everything: fails direction 3.
- **Reads the rendered `blocked_by` edge instead of `plan.yaml`→`feature.yaml` (D-01/C-2 forbid this):
  no criterion asserts this — SC-22 proves outcome, not mechanism.** In practice this is low risk
  today: the recorder's `issue_view` on a candidate returns only `number, title, state, assignees,
  labels` (`plan.yaml:1024-1025`), and blocker state comes from `issue_view` on the *blocker itself*
  (`:1058-1061`) — there is no rendered-edge field in the fixture for a wrong implementation to read,
  so it would find nothing, behave as never-blocked, and fail both direction 1 and direction 2. But
  this is incidental to the fixture's current shape, not asserted: if a later fixture ever populates a
  `blocked_by`-shaped field on the candidate payload (e.g. for an unrelated case), this direction
  reopens with nothing in SC-22 to catch it. Low severity, non-blocking.
- Hard-codes/correlates with the fixture: defeated by the three directions asserting three different
  expected issue-number identities against the same/related fixture (clear candidate in d1, none in
  d2, the *formerly* blocked candidate in d3) — a hard-coded tool that matches one fails the others.

## Q2 — Is SC-13 clause (b) genuinely untouched? PASS (text-only judgment, per dispatch)

Read at `BRIEF.md:252-254` as it now stands: requires stderr to read `no claimable work` and forbid
`no work available` on the all-unclaimable exit. Byte-identity to a pre-edit baseline was **not**
independently verified — there is no git baseline for this untracked feature dir, and the dispatch
explicitly says not to try reconstructing one. This verdict is scoped to the text as it reads today,
matching the dispatch's instruction.

Clause (a)'s widening reaches (b) legitimately: BRIEF.md states the linkage explicitly rather than
leaving it to inference — "The blocked case is... it widens clause (b) with it: a candidate the
blocker gate skips is unclaimable in exactly the sense (b) already uses" (`:248-251`). Mechanically
confirmed at `plan.yaml:1106-1108`: there is one unified exhaustion exit ("If every candidate is
exhausted without a win... exit 1") reached regardless of *why* each candidate was skipped, so the
blocked case does fall through to (b) by construction, not by hopeful reading.

**This is the same inheritance that produces Q3's finding.** (b) now aggregates five distinct
unclaimable reasons behind one stderr line; the per-skip disambiguation the digest offers as the
resolution is asserted for exactly one of the five (see Q3).

## Q3 — Does the residual signal survive? FAIL — high severity, must_fix

**The scenario that breaks it.** Ready column holds one D-13 residual (an unblocked root task whose
agent died between `create_ref` and step-6 bookkeeping — open, unlabelled, unassigned, per
`BRIEF.md:122-126`) plus several genuinely blocked items. The residual passes the step-5a pre-filter
by construction (open, no label, no assignee) and passes the a-bis blocker gate (it is a root, no
`depends_on`), so it fails only at step 5b's `create_ref` (ref already exists → `False`). A poll
exits 1 on `no claimable work`. stderr carries one `blocked by T-NN (#x)` line per genuinely blocked
candidate and **nothing at all** for the residual. The operator reads "healthy, waiting on blockers"
and the residual BRIEF:125-126 says "accumulate[s] without bound" stays invisible indefinitely.

**The gradient in the plan text itself shows this is an omission, not a design choice:**
- `plan.yaml:1078-1084` — dangling `depends_on` entry (unresolvable to an issue): report **on every
  poll**, **its own distinct reason**.
- `plan.yaml:1071-1073` — open blocker: report, **distinct from every other skip reason** — and
  `plan.yaml:1196` / SC-22's own test case asserts this distinctness against the 5a reasons
  specifically.
- `plan.yaml:1033-1035` — 5a pre-filter (already marked / assigned / closed): report the reason, no
  distinctness required or tested.
- `plan.yaml:1095-1105` — step 5b, poll-mode `create_ref` returns `False` (the "claim marker already
  taken" member of SC-13(a)'s enumeration, and the *only* one of the five that is the actual D-13
  residual path): **no stderr-reporting instruction at all.**

No criterion requires otherwise: SC-13(a) only requires skip-and-continue behaviour, not a stderr
message per reason; SC-22's distinctness assertion is scoped to the blocked-vs-5a-reasons comparison
(`plan.yaml:1196`, "differs from the already-marked and already-assigned skip reasons") and never
touches the ref-refused case; the EXHAUSTION test (`plan.yaml:1154-1167`) asserts only the aggregate
final line, not per-candidate stderr content.

**Why `high` and not `med`: enforcement made this worse, not neutral.** Pre-enforcement, `no
claimable work` firing at all was itself the operator's signal that something was stuck. Post-
enforcement, once the unblocked roots move to `building`, `no claimable work` is the **healthy steady
state** (`DESIGN.md:130-135` names the same asymmetry for the dangling-edge case: "stderr is the
operator's only view of it"). The distinct-reason resolution the amend-product digest credits with
resolving Q10 ("a distinct stderr reason per skip, contracted in DESIGN.md C-2 and asserted in
SC-22") is true for the blocked reason and untrue for the residual's own reason — the one D-13's
acceptance was actually about.

**must_fix:** extend SC-22's (or SC-13(b)'s) distinctness clause to cover *every* skip reason in the
candidate loop, explicitly naming the refused-claim-marker case — not merely "the criteria need
revision." Fixing only `plan.yaml`'s T-05 step-5b prose leaves the guarantee uncontracted at the
BRIEF/SC level, which is the surface a later implementer and a later reviewer actually check against.

**Open, non-blocking:** whether the remedy belongs in SC-22 (extend the blocker case's distinctness
requirement to a general one) or in SC-13(b) itself (require the exit-1 stderr trace to name every
skip's reason, not just the blocked one) is a decision for pm/eng-lead, not this review.

## Q4 — SC-09 and T-09. PASS, with a scope note

Walked SC-09 (`BRIEF.md:230-236`) clause by clause against T-09's instructions:
- "issues as the interface, the signed plan as the truth" → `plan.yaml:1457-1458`.
- "read-back permitted for exactly three purposes... a claim, a station, and whether a blocker issue
  is finished" → `plan.yaml:1459-1461`. "Exactly THREE" carries the "and no others" force; no
  separate instruction needed for that phrase.
- "names DEC-138 as the write-only baseline the third purpose amends" → `plan.yaml:1464-1465`.
- "states that the rendered `blocked_by` edge is never read back" → `plan.yaml:1475-1476`.
- "states the cost... one blocker-state read per candidate, bounded by the ready column" →
  `plan.yaml:1478-1480`.
- "The propagation checker is clean afterwards" → not a content instruction to the documentor; it is
  `bash .claude/skills/harness/bin/check-docs.sh` inside T-09's own `verify:` line
  (`plan.yaml:1450`), run mechanically as a gate, not asserted by prose.

**Scope of this verdict:** SC-09 is `verify: inspection` and its object, DEC-186, does not exist yet —
T-09 is `status: pending`. So SC-09 has not been and cannot yet be inspection-verified against an
actual record. What was verified here is narrower and is exactly what the dispatch asked: every
clause has a specific T-09 line instructing it, so SC-09 cannot go green on the documentor's
improvisation when T-09 eventually runs. That is a claim about the instruction, not about a record
that exists.

## Q5 — Placement (Q11). FAIL-adjacent — mismatch, med severity, does not block

Read SC-07 (`BRIEF.md:209-213`) in full: issues appear from one command, station moves as an agent
claims, the journey reaches a merged PR, and two concurrent claims on the same issue produce exactly
one winner on the real API. **No clause mentions a blocker, dependency ordering, or asks the operator
to close a blocker on the live board and observe the previously-blocked task become claimable.**

The gap note at `BRIEF.md:316-320` states the live hop — "a blocker issue's closed state on the live
board arrives correctly" — "is carried by SC-07 as an operator step, like every other live-board
claim here." That claim is not supported by SC-07's text as written: SC-22 *scripts* the blocker's
closed state against a recorder (`BRIEF.md:316-318`), so SC-07 is the only place in this feature the
live read would ever actually happen — and nothing in SC-07 obliges the operator to exercise it. An
operator can complete SC-07 in full without ever touching the one live hop the D-01 widening exists
to make trustworthy.

Verdict: **(b)** — SC-07's text needs a blocker clause (e.g. a task with an open blocker is not
claimed while the operator watches the board; closing the blocker on the live board and re-polling
claims it). The gap note as currently written is not accurate — it cites coverage that does not exist
in the criterion it points to.

## Severity summary

| Q | Verdict | Severity | Blocks |
|---|---|---|---|
| Q1 | PASS, one low note (mechanism-not-outcome gap on rendered-edge reads) | low | no |
| Q2 | PASS (scoped to text, not byte-identity) | n/a | no |
| Q3 | FAIL | **high** | **yes — must_fix** |
| Q4 | PASS (scope note: SC-09's object does not exist yet) | info | no |
| Q5 | mismatch (gap note overclaims) | med | no |

**VERDICT: FAIL** on `severity_max: high` per the review protocol's own gate (`must_fix` non-empty).
The must_fix item is narrowly scoped to Q3; Q1's low note and Q5's mismatch are advisory and do not
block.
