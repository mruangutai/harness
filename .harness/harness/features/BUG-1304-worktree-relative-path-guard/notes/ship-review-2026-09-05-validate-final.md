# BUG-1304 — ship readiness review

**BUG-1304 is ready to ship.** Every gate that can pass has passed at the pinned commit
`c5869301`: the reviewer panel returns PASS with an empty `must_fix`, all twelve success criteria
are met, the blocking qa gate passes, the full suite is green with no loss of coverage, and
`check-state.sh` reports zero violations. Nothing is waiting on a decision and nothing was waived.
The merge itself is yours — the harness does not merge.

**What it does.** A governed agent given a feature worktree can now only write inside it. If it
spells a path so the write would land in the main checkout, or in another feature's checkout, both
governed write routes refuse before the write happens and the message names where the write
belongs. The rule turns on the write's **resolved destination**, never on how the path was spelled —
which matters because the two incidents that caused this bug were spelled relatively, but the
identical damage done with an absolute path would have gone unrefused by a spelling rule. An agent
holding no live claim, an agent whose claimed feature has no worktree, and the main session are all
unbound and unaffected.

## How this was verified — and how much of it you should trust

| Gate | Result | Where |
|---|---|---|
| Reviewer panel, cycle 2 | **PASS**, `severity_max: med`, `must_fix: []` | `runs/panel-c2-validator/digest.md` |
| Goal-check, cycle 2 | **PASS**, 12 of 12 criteria met | `runs/goalcheck-validate-c2-product/digest.md` |
| qa gate (blocking — the only one) | **PASS**, `matrix_ok: true` | `runs/qa-gate-validator/digest.md` |
| SIMPLIFY | **PASS**, empty | `runs/simplify-eng/digest.md` |
| UAT | **does not apply** — BRIEF carries zero `verify: uat` criteria | `BRIEF.md` |
| Full suite at the pin | exit 0, 0 failures, **73 files discovered — the same 73 as before the work began** | orchestrator-measured |
| `check-state.sh` | exit 0, zero violations | orchestrator-measured |

Two things are worth knowing about the *quality* of that green, because a gate that cannot go red
is worse than no gate.

**The discrimination proof is the real product here.** Every new refusal case is also fired against
a frozen, byte-for-byte copy of the guard as it existed *before* this change, and must come back
unrefused — otherwise the new assertion was never testing anything. That alone would not be enough,
because these guards fail *open* at exit 0 in several branches, so an unrefused write and a guard
that never ran look identical. So each pre-change call additionally proves the frozen guard actually
ran: its output must carry none of the fail-open markers, **and** a positive control fired at the
same frozen guard in the same environment must still be refused. Ten such proofs on the Write route,
twelve on the Bash route.

**One measurement was checked twice on purpose.** Four functions were split late in the cycle to
satisfy a complexity bar, and a split that quietly drops an assertion produces a *greener* suite —
so the suite passing proves nothing about it. The code reviewer diffed the four functions
byte-by-byte across the split and found every prior assertion intact, two of them strictly
tightened; independently, the runtime count of pre-change proofs was measured at both commits and
is unchanged at ten and twelve. The panel records honestly that nobody deleted an assertion and
watched it go red, which is the one form of evidence not obtained.

## What was found and fixed along the way

Cycle 1's panel and goal-check both failed, and the two most valuable findings came from places
nobody would have predicted.

**The UI reviewer found the specification violation.** It scoped itself out of rendered-UI review —
correctly, there is no UI — and then audited the refusal *messages* as the operator interface. On
the Bash route all three refusals were routed through a helper that appends "File changes go through
the Write tool". For a control-plane Expertise destination that advises a route which refuses the
identical path with the identical text, and the requirement is explicit that this destination class
gets the sanctioned merge command and nothing else. The code reviewer's own lens could not see it.
This is the argument for never letting a reviewer skip itself pre-emptively.

**The goal-check found two gaps that were records, not behaviour.** One criterion's message content
was correct in the code but unasserted in the tests on both routes; another required the plan to
record how an ambiguously-resolving claim is treated, which the shipped decision recorded but the
plan did not. Both were closed; neither was a defect in what the code does.

**A binding conflict was ruled against the orchestrator, and the record says so.** Narrowing this
guard collided with an existing invariant about unreadable registries. The orchestrator argued the
two never overlapped; the Advisor ruled otherwise and the losing reading is recorded in `STATE.md`
beside the ruling rather than quietly dropped.

## Proposed backlog

Nothing here gates the ship. **Anything you strike from this table dies silently**, so it is all
listed, including the items the panel assessed and dismissed.

| ID | Nature | What |
|---|---|---|
| B-1 | bug | A bound agent can release its own claim through the sanctioned CLI over Bash and thereby unbind itself for a session. Not a regression — before this change the same agent could write the main checkout with no guard at all — and the BRIEF already records that registry mutation via a CLI call is not a governed write. **The security reviewer rated this HIGH and wanted it gated; the orchestrator ruled it non-gating on the requirement text.** Recorded so you can overrule. |
| B-2 | bug | A hand-written registry entry missing its `feature` field passes through a broad exception handler instead of being refused. Pre-existing, and unreachable through the sanctioned CLI, which always populates the field. |
| B-3 | chore | The claim-set builder enumerates linked worktrees once, then re-enumerates them per matching claim. Measured at ~1.24ms against a ~38ms interpreter floor with at most one claim in practice, so today's saving is zero. The obvious fix was rejected as unsafe: it would restate a rule two criteria pin. |
| B-4 | chore | Five functions sit one grade below their complexity bar (medium severity, non-gating). Four higher-severity ones were already split. |
| B-5 | chore | Only the Bash test suite exercises the Expertise-destination refusal; the Write suite's fixture lacks the grant needed to reach it. Both routes share one message builder and the UI reviewer rebuilt the fixture and got byte-identical output, so this buys a demonstration rather than protection. |
| B-6 | chore | Two tasks' acceptance commands count call sites textually; the late splits moved that count while the runtime count held. A stale proxy inside an approved plan — record only, no defect behind it. |
| B-7 | chore | One criterion asks the refusal to name "the worktrees the agent holds", but in the ambiguous case the resolver fails while that set is still being built, so the refusal names the candidates instead. Graded clause by clause. Unmeetable as literally written rather than unimplemented. |
| B-8 | bug | **Harness:** the board invariant and the mirror contract contradict each other. A finished task's card is required to sit at the done station, but no command writes that station before ship, and the exemption that hides this applies only once the feature reaches review. Every feature is red between its last task landing and its review transition. Cost here: the plan's own final task could not pass until after the transition. |
| B-9 | bug | **Harness:** a panel record whose reader entries are keyed by persona instead of step name is reported as "reader never ran", which reads as a missing record and sends the reader looking for the wrong thing. |
| B-10 | bug | **Harness:** the documented route for writing a plan's panel record cannot amend an existing one — it exits with a conflict and writes nothing. A different, working command exists but is named nowhere in the playbook, so it has to be found by running the wrong one first. |
| B-11 | bug | **Harness:** a handoff note cannot be written from a worktree at all. The path is stripped of its worktree prefix but resolved against the main checkout, so a branch-only feature's pointers never resolve and absolute ones are refused. |
| B-12 | bug | **Harness:** several subagents returned complete, well-formed results while the host reported the job as failed. A caller routing on that status alone would re-spend the spawn. Observed four times in this feature. |
| B-13 | chore | **Harness:** a run directory's `state.yaml` is silently overwritten when a later run reuses its id; the digest beside it is protected and the state file is not. Happened three times here. Already owned by a sibling flow. |

Three follow-ups were already filed as issues during planning and are **not** backlog rows:
**#1341** (a worktree lookup that compares directory names where it should compare path prefixes —
this is the defect behind the one struck task, and striking it was only legitimate because #1341
owns it), **#1342** (an unreadable worktree pointer fails open where the registry fails closed —
now narrower than when filed, since the registry half was settled by ruling), and **#1343** (a
liveness check that cannot see a compatibility-host child past twenty minutes).

## Cost

Fourteen rework cycles of a sixteen-cycle allowance, and twenty-one runs against an informational
budget of twenty. **Thirteen of the fourteen cycles were spent in planning, not building** — three
adversarial panel cycles and four binding rulings, on a change whose whole difficulty was deciding
what to bind rather than how to bind it. The build itself passed every task first time; three
amending commits followed, one of which was a thirty-three-word sentence against a thirty-word cap.
The run count is over budget by one and that is informational, not a defect: on the three questions
the invariant asks, the runs resolved real issues and advanced the criteria, and the plan phase's
length bought a design the panel could not fault at the second attempt.

---

**No report round was spawned for this briefing.** It was assembled by reading the run digests on
disk, per DEC-69. Every digest under `runs/` was read or its conclusion read: the two eng
digests, the ten product digests, the eight validator digests, and the four this orchestrator ran
itself (`qa-gate-validator`, `simplify-eng`, `panel-c1-validator`/`panel-c2-validator`,
`goalcheck-validate-product`/`goalcheck-validate-c2-product`). The plan phase's findings were taken
from `plan.yaml`'s own `panel` record — thirteen findings across three cycles, all dispositioned —
rather than re-derived. `runs/2026-09-05-07-validator` is referenced in `feature.json` but its
directory does not exist and could not be read; nothing else was missing.
