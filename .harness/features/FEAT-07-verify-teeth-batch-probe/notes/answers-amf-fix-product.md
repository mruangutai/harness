# Answers — FEAT-07 signature gate, round 2 — 2026-08-04

Four rulings, taken as ONE review pass, applied as ONE consolidated fix. The user raised
nothing beyond what is below. Do not solicit again.

## Q1 / D-07 — REDIRECT. The `no-task` recommendation is NOT taken.

RULING: implement the ALTERNATIVE — a declared `task: T-NN|none` field on the `dev` and
`dev-ops` schemas, with `task_verify` binding only when `task` names a real `T-NN`.

The user's reasoning, recorded so it is not re-litigated: `no-task` reinstates a self-declared
bypass with no receipt obligation, which is structurally the shape the user's own Q1 ruling
rejected one round trip earlier. PLAN.md:160-163 states plainly that `no-task` is cheaper to
abuse than a false `pass`, because REQ-08 makes a `pass` show its command and verbatim output
while `no-task` obliges nothing. The user accepts the priced cost: roughly double T-01's diff,
a new conditional-requirement mechanism in a DEC-174 file, and a new required field propagating
to T-02, T-03, T-06 and all nine fixtures.

Execution requirements:
- Work the SIX redirect sites you enumerated at `PLAN.md:144-159` — `:213`, `:319`, `:376`,
  `:469`, `:496`, `:586` — rather than re-deriving them. Re-grep at final state; your own note
  records that a bare `grep -n "⚠️"` returns eleven and that five of those are not redirect
  sites. Report the count you actually find.
- D-07 is REPLACED, not amended: it now records the task-id field as the decision, `no-task` as
  the rejected alternative, and the user's reason for the reversal. BRIEF SC-17 is replaced with
  it.
- The `task: none` escape must be cross-referenced, since that is the whole reason it was
  chosen over `no-task`: T-05 already requires the dispatch to carry the task's `T-NN` id
  verbatim. State how a return declaring `task: T-NN` is checkable against that, and be honest
  in BRIEF `## Verification gaps` about what remains unchecked — `task: none` is still
  self-declared; what it buys is a task-id-shaped string, not a proof.
- BRIEF's bypass bullet in `## Verification gaps` is written to the recommendation. Rewrite it
  to the ruling, and do not soften the residue.
- The conditional-requirement mechanism goes into a flat `SCHEMAS` dict that has none today.
  Whatever shape it takes, it is inside DEC-174: it needs its own fixtures, and the human
  reading the diff is the only other control.

## Q2 — COST: budget raised. Not a re-baseline, and nothing is hidden.

RULING: continue; raise `max_cost_usd` in `feature.yaml` for THIS feature. The plan phase spent
$180.37 against $120, and the crossing was bought by the architecture review the user ordered.

Main session's proposal, which you may revise upward with a stated reason: **$400**. Basis —
the plan phase is closed at $180.37; FEAT-03 and FEAT-04 spent $358 and $324 in total against
$120 budgets; this feature's build is eleven tasks, most of them main-session-direct, plus the
validator panel. A number that gets crossed again in week one is not a budget.

Carry actual-vs-budget in every return and in the ship briefing, per DEC-134. The raise is
recorded as a decision with its reason, never a silent edit. Do not let the raise become a
reason to spend to it.

## Q3 — INDEX DRIFT: already handled by the main session. Do not touch it.

`docs/harness/DECISIONS-INDEX.md` was committed on its own at `4091b36`, BEFORE the feature
branch, with the measurement in the message: 57 of 174 rows, all delta exactly +6, boundary
DEC-118, `DECISIONS.md` unchanged. The working tree is clean of it.

Consequence for T-09: its precondition is now KNOWN-CLEAN rather than conditional. At `4091b36`,
`gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md` exits 0. Simplify the
conditional wording if it is now dead weight, and re-measure rather than trusting this line.

Note for the record, since the plan cites it: the main session's earlier "no pre-existing drift"
statement was measured AFTER an undeclared agent edit had already regenerated the file, so it
described a fixed tree, not the committed one. Corrected to the user directly.

## Q4 — pm's missing receipt grant: FILED, out of scope.

GitHub issue #46. Do not fix it in FEAT-07 and do not plan around it — if a dispatch needs a
receipt path pm is not granted, name a granted path instead, exactly as pm did.

## Terminus

Return when the redirect is applied and re-verified. Every `verify:` that changes must be
EXECUTED against the tree and shown to discriminate — the standard that has already caused two
commands to be rewritten in this feature, and it does not relax on a third pass. No further
architecture review is ordered; the review's findings are resolved and D-07 is now a user ruling,
not an open finding.

The signature is the user's and the main session's to take.
