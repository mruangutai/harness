# Operator answers — FEAT-35 validate, all five questions — 2026-08-24

One consolidated set (DEC-176). Nothing else is open.

## Q1 — SC-03 AMENDED. The criterion was wrong, not the mechanism.

**Accepted: SC-03 is unclosable as written.** A reviewer is never `agentType`
`harness-orchestrator` — measured 0 of 31 in-session — so the required single-match citation can
never be produced by the persona the criterion names. Your finding, and it is a real defect in a
signed BRIEF.

**Re-specify it so the reviewer runs the mechanism against its OWN `agentType` as stand-in.** That
still exercises what the criterion was for: the two-call sequence (a nonce grepped in a LATER call,
because a same-call grep finds nothing), the match-count logic, and `context-watch.py` accepting the
derived id. The reviewer records the single matching sidecar path, the id derived from it, and the
`context-watch.py` row, cited `file:line` in its note — exactly as before, with the glob's
`agentType` filter set to its own persona rather than `harness-orchestrator`.

**State plainly in the amended criterion what this does NOT cover:** the orchestrator-typed glob
itself stays unexercised until a real orchestrator runs it after merge. Do not paper over that.

Route the BRIEF edit to `harness-pm` (BRIEF.md resolves to harness-orchestrator, harness-pm). Amend
SC-03 only. The main session re-signs both artifacts after — see Q4.

## Q2 — SC-05 is `partial`, with a post-merge obligation ON THE RECORD.

**What SC-05 exists to measure, stated so the record is not ambiguous:** whether a stopped
orchestrator actually survives a child running past the 600s watchdog. The whole feature rests on
it. If a stopped parent does NOT survive, this change removes a noisy death and leaves a silent one.

**What was measured:** an orchestrator stopped, waited **1057.1s** (`15:34:10.019Z` →
`15:51:47.145Z`), was woken, and continued — with **0** Bash calls made to stay alive, not killed,
closing with its own text. Control: two known failing sidecars discriminate.

**What was NOT measured:** that the REWRITTEN PLAYBOOK causes that behaviour. That run followed a
dispatch-level override, because the rewrite is committed in the worktree while a spawned agent
loads its skills from the main checkout. **The gap is unsatisfiable before merge by construction.**

**Record it `partial`.** The obligation: one orchestrator round-trip over 600s under the MERGED
skill, with no override in its dispatch, measured the same way — longest survived gap, stall-call
count, killed-at-600s. **Owner: the main session, on the next feature that runs a build or validate
phase.** That run supplies the evidence for free; no dedicated run is needed. Name the owner and the
method in the record, not just the obligation.

## Q3 — `matrix_ok: FALSE` ACCEPTED EXPLICITLY.

T-01/T-02/T-03 are `change_type: ai_behavior`, whose matrix requirement is `eval`, and
`test_kinds.eval` has `cmd: null`. The requirement soft-skips and proves nothing.

**This was disclosed in the BRIEF's own Verification gaps before signature and is accepted on that
basis.** What carries the weight instead: SC-01/SC-02/SC-04 assert the playbook's text at the
reviewed sha, SC-06 is a human read of its coherence, and SC-05 is the only evidence of conduct.
The missing `eval` runner is a standing dev-ops gap, not this feature's to close.

**Do not record `matrix_ok: true`.** The honest false value with a recorded acceptance is the point.

## Q4 — RE-SIGNATURE APPROVED, and it covers three edits.

The approval reads `2026-08-23` while `source_issues: [751]` was added `2026-08-24`, so the
signature predates its content. Correct catch.

The main session re-signs BOTH artifacts at `2026-08-24` once pm's SC-03 amendment lands. The
re-signature covers exactly: `source_issues`, the DEC-200→DEC-201 id correction, and SC-03's
amendment. **Nothing else may ride on it.**

## Q5 — LEAVE `parent_origin` AS IT IS. You were right to refuse.

**The main session's instruction to write `created` was WRONG and you correctly did not follow it.**
`created` is set only where gh-sync itself runs `gh issue create`; `adopted` where a number is
supplied. `#751` was authored by `mruangutai` at `2026-08-23T15:27:34Z`, before any harness command
touched it — the adopted branch. You checked the code and the timestamp rather than taking the
dispatch's word, and the hazard you named is real: `cmd_abandon` closes a `created` parent
`not_planned` and labels it `abandoned`.

Writing `adopted` explicitly is optional and immaterial — `Closes #751` renders and closes the
parent at merge. Leave it.

## The panel's best finding — FILED, not fixed here

**Four of the eight assertions are exact-literal greps defeated by rewording.** "Await the team
digest" passes all eight green while the defect is fully restored. That is now on **#804**, widened
from its original line-scoping finding, with the operator's ask attached: **first decide whether
these assertions are required at all** — a test that cannot fail on the case it guards may be worse
than none, because it reads as coverage — and **if they are, find a better data-structure pattern**
for these and every assertion like them: more performant, less buggy, more efficient. Not six patched
string comparisons.

**Not fixed in this feature.** It would edit T-05's signed contract mid-validate and require the
panel to re-run.

## Also filed from this phase, so you do not re-file them

#803 (DEC-NN collision guard), #805 (a team task's `done` write has no owner), #806 (`ship` skipped;
ten unclosed milestones), #808 (`ship` and `abandon` duplicate four of five terminal steps and
`ship` omits the sub-issue close — extract one core, do not copy the loop).

## The unrecorded run you surfaced

`2026-08-24-01-product` completed at 06:41 and was never recorded in `runs:`, and its send-back was
uncounted — hence `cycles_used: 4` rather than 3. **Recorded, and correct to have raised.** Nobody
asked for that check.

## After this

Return `awaiting_user`. The main session re-signs, commits, and takes the ship decision. Do not
commit, do not open the PR, do not run `ship`.
