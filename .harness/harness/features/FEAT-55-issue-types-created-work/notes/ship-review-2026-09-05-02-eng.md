# FEAT-55 — native issue types on created work: ship review

**FEAT-55 is ready to ship.** Your four rulings closed every blocker. All twelve tasks are complete
and verified, all twelve success criteria are met, every gate is green, and the review panel's one
gating finding has been fixed and confirmed closed by the reviewer that raised it.

Two things you should know before you decide, neither of which blocks:

- **The cycle budget is exactly spent** — 13 of the 13 you authorised. One fix cycle was needed and
  it was the panel's finding. If anything else surfaces, I cannot fix it without another raise.
- **The GitHub mirror did not advance to Review.** It refused, correctly, for a reason that is a
  harness defect rather than a problem with this feature. Detail below; it is never a gate.

## What changed since the last briefing

| Ruling | What I did | Cost |
|---|---|---|
| **F-01** schema authority | pm amended T-04 to own `feature-schema.json`; backend-dev declared the optional `typed` mapping on both closed objects. Recorded as decision **D-21** | 0 cycles |
| **F-02** the dead query | The `--repo` flag and its false comment are gone; the test now pins the exact GraphQL `owner=`/`name=` values instead of flag presence. Recorded as decision **D-22** | 0 cycles |
| **F-03** SC-10 | Graded **met** on your ruling, cited to it. The optional live probe is backlog row B-1, not a gap | 0 cycles |
| **F-04** budget | Raised to 13 cycles / 40 runs | — |

**The plan never needed re-signing.** `plan-merge.py`'s amendment verbs preserve the approval bytes
by construction, so your signature of 2026-09-05 still stands, with all five original rulings
intact. I verified that on disk after the amendment rather than assuming it.

## Where the feature stands

| | |
|---|---|
| Tasks | **12 of 12** complete and verified |
| Success criteria | **12 of 12 met** — SC-10 on your ruling F-03 |
| Requirements | REQ-01…REQ-11 all traced to a verified task |
| Test matrix (the only blocking gate) | **PASS** |
| Review panel | **PASS** — one finding raised, fixed, and confirmed closed |
| Complexity grade over the diff | **zero high** |
| Committed at | `76ba5f41` on `feat/issue-1289-issue-types` |
| Cycles | **13 of 13 — spent** |
| Runs | 39 of 40 |

Measured by me at the final commit, each suite separately with its own exit code and failure count —
never a tail read, because a truncated capture already produced one false green on this feature:
all ten FEAT-55 suites and the whole unit driver at **exit 0, zero failures**.

## The three things that went wrong, and how they were caught

**The qa gate failed on a two-line documentation defect.** The new prose in `github-mirror.md`
carried two file paths written the short way, and a repo-wide guard requires them anchored. The task
that wrote that prose passed its own checks — its checks were narrower than the guard it had to not
break. That file belongs to no agent's domain, so you landed the fix yourself; I committed it and
the guard went green.

**The review panel caught a complexity regression this feature introduced.** One serialization
function in the factory crossed a maintainability threshold, and it crossed it because of a line
*this feature added*. I checked the panel's reasoning against the repository's own grader before
spending the last cycle on it — the premise held. The fix was a ten-line extraction, and the
reviewer re-measured it rather than taking my word: the function and its new helper both clear the
bar, the extraction changes no behaviour, and it found nothing new.

**A comment that this feature made false was still shipping.** Ruling F-02 ordered one false comment
deleted; a second copy of the same claim lived in a file that ruling never touched. The panel found
it. It is fixed, because a maintainer who believes it would revert correct code.

## What I could not do

**The mirror did not move to Review.** `gh-sync.py status … review` refused: *"not every task in
plan.yaml is done or abandoned."* It is right that no task reads done — but no task can, because
this plan's tasks carry no status field at all, and the verb that records one can only edit a field
that already exists. It cannot create one. That is backlog row B-5, and I did not work around it:
writing plan content outside that verb is exactly what the single-write-route rule forbids. The
mirror is never a gate, and the plan on disk is the authority regardless.

**Two archived run checkpoints were destroyed and are unrecoverable.** Two different agents wrote
this session's checkpoint into an older run's directory, because the runs tree is excluded from
version control, so a search for existing runs returns nothing and a live directory reads as free.
Both times the guard refused the *digest* write and allowed the *checkpoint* write. The lost files
are spent archive artifacts and both affected runs' digests survived intact, so nothing of record
was lost — but the guard has a hole in it. Backlog row B-6.

## How I assembled this

**I spawned no reporting round.** I read from disk:

- `notes/ship-review-2026-09-05-01-eng.md` — the previous, blocked-state briefing, which carries the
  plan and build phases
- `notes/research-FEAT-55-goalcheck-c1.md` — pm's per-criterion goal-check
- `notes/qa-2026-09-05-01-validator.md` and `notes/review-harness-qa-c1.md` — the gate, twice
- `notes/review-harness-code-reviewer-c1.md`, `…-security-reviewer-c1.md`, `…-ui-reviewer-c1.md`
- `runs/2026-09-05-30-validator/digest.md` and `runs/2026-09-05-32-validator/digest.md` — the panel
  and its re-check
- `STATE.md` and `plan.yaml`

Every number in this briefing that gates a decision — the suite results, the complexity grades, the
schema refusal, the missing `--repo` flag — is one I measured myself in this checkout.

**One correction to the record:** two test files were named in the wrong directories in an earlier
dispatch. `test-factory-gh.py` lives under `tests/unit/`, and `test-anchor-directions.py` under
`tests/integration/`. Both are green where they actually live, and every measurement in this
briefing used the correct paths. Noted so a later reader does not read a stale exit 2 as a
regression.

## Proposed backlog

Anything you do not strike becomes an issue. **Anything not on this list is forgotten.**

| ID | Nature | What |
|---|---|---|
| B-1 | chore | **Your ruling F-03's follow-up.** Run the live capability probe against an organization-owned repository with Issue Types enabled. It is the only check that can falsify the test double's assumed API shape — everything today is verified against a fake |
| B-2 | bug | An agent's edit reported success, issued a new snapshot, and never reached disk; a re-read showed the old content and an identical retry was rejected as a duplicate. A write tool that reports success without writing can manufacture a false green anywhere |
| B-3 | bug | The shell write guard blocked `cp` onto a protected file but allowed `python3 -c` to write the identical path in the same call — it reads command names, not what actually writes |
| B-4 | bug | A truncated capture of the unit suite showed zero failures while the suite had failed four files. Captured output cannot be read for absence of failure |
| B-5 | bug | The task-station verb cannot record any station on a plan whose tasks carry no status field — it edits an existing field and cannot create one — and it misreports the cause by naming the task it just called absent. This is what stopped the GitHub mirror above |
| B-6 | bug | Two agents overwrote an older run's checkpoint file because the runs tree is excluded from version control, so a search returns nothing and a live directory reads as free. The guard protects the digest in that directory but not the checkpoint |
| B-7 | bug | An agent's edit resolved a relative path against its process directory instead of its assigned worktree, briefly writing into the main checkout. It caught and reverted this itself |
| B-8 | chore | A documentation task's own checks passed while a repo-wide guard it had to not break was red. Every docs task touching a guarded file carries this hole |
| B-9 | bug | The manual probe's read-back builds its GraphQL query by string formatting instead of parameters, unlike every other call site. Reachable today only behind an operator-only flag on a host-only script, so nothing crosses a boundary — but it stops being safe the moment that function gets a second caller |
| B-10 | chore | One legal configuration override key is exercised only at unit level on the backlog route; the criterion that binds it is fully covered elsewhere. A thin spot, not a gap |
| B-11 | chore | Seven of the eight read-back rows are duplicated across two files with no drift protection; only this feature's is guarded |
| B-12 | chore | The backlog receipt is flat on disk while the plan's prose describes it nested. Behaviour is unaffected; ratify one or correct the other |
| B-13 | bug | The digest validator rejects a plan-phase review's `code_grade: n_a` — the exact value the plan-phase panel is supposed to use |
| B-14 | bug | A run digest cannot be repaired in place, so every malformed first write permanently costs a second run directory |
| B-15 | chore | The plan-writing verb list omits `amend`, which every revision after the first needs |
| B-16 | chore | `amend --key` accepts only tasks and decisions, so an edit inside the panel block has no route |

## What happens next

Say ship and the main session merges, closes the mirror and files whichever backlog rows you leave
standing. Nothing else is outstanding, and nothing is waiting on me.
