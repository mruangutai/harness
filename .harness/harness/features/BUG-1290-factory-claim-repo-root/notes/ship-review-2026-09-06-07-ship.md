# BUG-1290 — ship review, second pass

**You struck B-3 and asked for the fix first. B-3 is closed, every gate is green again, and all
nine success criteria are still met. The change is ready for your ship decision.**

Nothing else about the feature moved. Production code is **byte-identical** to the tree you were
looking at yesterday — I measured it: `git diff 76e26386 7104aa43 -- .agents/ .claude/skills/` is
empty. The entire delta is 14 added and 9 removed lines in one test file.

**One thing in here deserves your push-back if you want to give it: the fix is proven but not
defended.** That is row **B-16**, and it is the same *shape* of gap B-3 was. Detail below under
"the one honest weakness". I am not calling it a gate and neither did the panel or the product
manager; you may reasonably disagree.

---

## What actually changed

`tests/unit/test-factory-claim.py` builds two fixture feature trees that carry the **same feature
id** under two different repository segments — `kaya-ai` and `harness`. Case `5b` polls both and
proves neither repository is served the other's data.

Before: both trees carried an **empty** `factory.issues` map, so the harness candidate's issue map
was never consulted at all. The code was correct; nothing could see it. A mutant that re-keyed the
issue-map cache on feature alone — throwing away the repository — broke nothing.

After: each tree carries its **own, non-empty, different** issue map, and the harness tree's task
now depends on a blocker that only *its own* map can resolve. Now the same mutant breaks case `5b`.

Here is the measurement, which I ran myself rather than taking from any agent:

| | before the fix | after the fix |
|---|---|---|
| suite unmutated | all pass | all pass |
| plan cache keyed on feature alone | `5b` **fails** | `5b` **fails** |
| issue-map cache keyed on feature alone | **everything passes — blind** | `5b` **fails** |

The middle row is the one I was watching for. The obvious way to write this fix is to give both
fixture trees the *same* dependency — and that would have made the two plans identical, quietly
destroying the plan-cache half of the proof while the new half lit up. Trading one proof for
another would have looked exactly like progress. It did not happen: the engineer used different
dependency ids, and I confirmed the plan half is still red.

---

## The gates, in order

| Gate | Result |
|---|---|
| **Engineering** | Fix landed, no send-backs. A second, independent persona re-measured all eight of the first one's claims and reproduced 8 of 8, including the load-bearing before-the-fix control. |
| **QA — the test matrix, the only blocking gate** | **PASS.** No `must_fix`. |
| **Simplify — four angles** | **Empty pass.** Nothing applied; the file is byte-identical before and after the pass, which is itself the proof all four readers stayed read-only. |
| **Validation panel — four reviewers at the new pin** | **PASS**, `must_fix: []`. All four ran; none skipped. Three of them reproduced the mutant independently rather than trusting my numbers. |
| **Goal-check — nine success criteria** | **9 met, 0 unmet.** SC-02, the one this cycle exists for, re-graded from scratch with the product manager's own mutant. The other eight carried forward with their evidence commands re-run at the new pin, not transcribed. |

`review_sha` is re-pinned at `7104aa43`. The board is at Review (parent #1359, sub-issues
#1360–#1364). Nothing is merged, no pull request exists, nothing is shipped.

---

## The one honest weakness

Row **B-16**. The property is proven **at this commit**, but nothing committed *defends* it.

Delete one fragment — `depends_on=["T-99"]`, one line of the fixture — and case `5b` goes straight
back to the blind state B-3 described, while the suite still reports 124 of 124 passing. The panel
found this; I reproduced it independently before writing this paragraph.

So: is B-3 closed? Yes, on its own terms. The clause you asked to have proven is proven, and the
proof is real. But the proof rests on a fixture detail with no guard on it, and a future engineer
tidying that file would not be warned. The product manager graded SC-02 **met-with-residue** and
recommended a durable fix as a backlog chore: a second committed mutant that discards the
repository at the issue-map seam and requires `5b` to redden. That is the same remedy B-1 and B-2
ask for on two other seams, and the three of them together are one coherent piece of work rather
than three chores.

**My read: ship it and take B-16 as backlog.** Spending another cycle here buys a guard on a guard,
and the underlying code has now been graded correct by five independent readers across two panels.
But you asked for B-3 rather than shipping with it, so if you want B-16 closed the same way, say so
— there is budget for exactly one more cycle of this size.

---

## Two questions the squads escalated, and neither needed you

**Both engineering and QA stopped and asked me to get you.** I answered both myself from the
record. You should know they happened, because in each case the alternative was a plan amendment
you would have had to sign.

**1. "T-01's verify command cannot pass, so how do we close the task?"** Raised twice, blocking
both times. T-01 is the write-the-failing-tests task, and its verify command asserts that the six
new cases **fail** — that is what a test-first gate does before the implementation exists. T-03
then landed the implementation, the cases went green, and the gate became unsatisfiable by
construction. It was satisfiable exactly once, in the window between T-01 and T-03, and the build
record shows it green there.

I measured it exits 1 on this tree **and** exited 1 on the tree before this cycle started, so this
cycle did not move it. No amendment is owed and no criterion depends on it.

**Correction to the record.** Yesterday's briefing and handoff asserted that "all five task verify
commands pass on the committed tree." **That was false for T-01 and always was.** My predecessor
verified the test *file* was green and recorded it as the *gate* being green. The two are not the
same thing, and it took two squads independently tripping over it to surface. Recorded here rather
than quietly fixed.

**2. "The test matrix demands an integration test and this diff has none."** QA failed the gate on
this. **The failure was mine, not the change's.** I dispatched QA to grade the *incremental
uncommitted diff* instead of the feature's change. A fix cycle inside a feature is not a change
type of its own; the matrix grades what the feature ships, and the feature ships two changed
integration files. Re-scoped correctly, the leg does not even fire, and QA withdrew the finding
explicitly rather than dropping it. It cost one rework cycle. Row **B-22** proposes stating the
matrix's diff object in the protocol so it cannot recur.

---

## Budgets

**8 rework cycles of a hard 10.** Two remain. Four were spent yesterday closing architecture and
panel findings before code was written; this cycle spent four more — two send-backs inside the
simplify pass, one for my QA mis-scoping, and one for the fix itself.

**19 runs against an informational budget of 20.** This crosses into the territory the budget
exists to notice, so here is my one-line read rather than an apology: the runs still earn their
place, but *this cycle's* four extra runs are not all honest work. One was my dispatch error, and
two were simplify send-backs on a 14-line test diff — a four-angle simplify pass over a fixture
change is heavier machinery than the change warranted, and I sequenced it because the playbook says
to, not because I expected it to find anything. It found nothing. If you want one process change
out of this run, it is that simplify should scale to the diff.

---

## How this briefing was assembled

**No report round was spawned.** I did not ask any lead to summarise anything for this document.

For this cycle I used the six lead digests as they were returned to me in-session, and verified
their artifacts existed on disk by listing them — the four panel review notes
(`notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-b3-c2.md`), the two QA
notes (`notes/qa-2026-09-06-02-validator.md`, `notes/qa-2026-09-06-03-validator.md`), the
goal-check (`notes/research-BUG-1290-factory-claim-repo-root-goalcheck-ship-c2.md`), and the run
digests under `runs/2026-09-06-0{1..6}-*/digest.md`.

For the plan, build and earlier validation phases I used **yesterday's briefing on disk**
(`notes/ship-review-2026-09-05-13-ship.md`), which was itself assembled from those phases' digests.
I did not re-read them individually. If you want a phase re-derived from primary sources, say
which.

Every number in the "what actually changed" table, the empty production diff, the T-01 verify
status on both trees, and the B-16 one-line-deletion result are **my own measurements**, not any
agent's. Everything else is attributed above.

---

## Proposed backlog

Strike any row by its ID. Unstruck rows become backlog issues on acceptance. **B-3 is gone — you
had it fixed.** Rows B-16 onward are new since yesterday.

### Product residue — this change

| ID | Nature | Finding |
|---|---|---|
| B-1 | chore | **REQ-08 has no committed defender.** Deleting the `factory_config.py` features reader row entirely still yields `CLEAN`; only T-04's probe discriminates, and it lives in `plan.yaml`'s verify block, which CI never re-runs. Promote it into a committed case. |
| B-2 | chore | **Mutation depth is one seam.** `features_root` has a dedicated mutation proof; `segment_of` does not. A `segment_of` mutant *does* redden case `5d`, so the property is caught — only the committed proof is missing. |
| B-4 | chore | **`factory_claim.py:38` `_BIN_DIR` is dead within its module.** Its only reader is unit case `5d`, via `claim._BIN_DIR`. A later cleanup deletes it and reddens `5d` for a reason unrelated to what `5d` tests. Repoint `5d` at `fc._BIN_DIR`. |
| B-5 | chore | **`features_root`'s join is not traversal-safe in isolation.** `"owner/../../etc/passwd"` escapes the harness root; `"owner/"` collapses the segment. **Not attacker-reachable today** — candidate filtering matches exact `fleet.yaml` membership first. Defence in depth only. |
| B-6 | bug | **The `feature`-label-derived join is unvalidated, and `feature` *is* attacker-influenced** (`factory_claim.py:170,190`). **Pre-existing**; belongs to the factory owner, not this diff. |
| B-7 | chore | **`segment_of`'s docstring claims to be "the one home of that rule" and the tree disagrees.** Four identical derivations survive (`post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231`). Correctly out of scope; nothing indexes them. |
| B-8 | chore | `_BlockerCache._plan` and `.issue_number` build the `(repo, feature)` key inline in two places rather than through one accessor. Declined at the pin boundary. |
| B-9 | chore | `features_root(repo)` is resolved at three call sites in `_BlockerCache`. Measured inert (13.32 µs per call, at most twice per unique pair per poll). Shape note only. |
| B-10 | chore | **REQ-05's wording correction.** The requirement says the segment rule is called by `factory_claim.py`; measured, it reaches it transitively through `features_root`. SC-06 is met on its own words. You declined to rule on it; queued here so it survives. |
| B-16 | chore | **SC-02's new proof is not defended by anything committed.** Deleting `depends_on=["T-99"]` at `tests/unit/test-factory-claim.py:382` returns case `5b` to the pre-B-3 blind state with 124/124 still green. Remedy: a committed mutant discarding the repository at the issue-map seam. **Natural companion to B-1 and B-2 — one piece of work, not three.** |
| B-17 | chore | **`build_features_root()`'s docstring overstates the fixture.** It presents both segments' issue maps as load-bearing; measured, only the harness side discriminates — kaya's `{"T-77": 850}` entry is inert. The same docstring now also restates case `5b`'s comment nearly verbatim. Reword, or make kaya's side load-bearing (which also discharges B-16). |

### Harness defects observed during these runs

Defects in the factory itself, not in the change. Listed because this repository *is* the harness.

| ID | Nature | Finding |
|---|---|---|
| B-11 | bug | **`check-domain` matches inflight claims by bare agent-type across every linked worktree, with no session scoping.** A concurrent same-role session on an unrelated flow becomes that role's only binding. Refused six read-only agents' note writes across two runs yesterday. The single most expensive defect in this feature. |
| B-12 | bug | **Nothing stops a lead writing its digest into a run directory another run already owns**, and `runs/` is gitignored, so the overwrite is unrecoverable. Destroyed two digests yesterday. The guard *does* refuse this for the orchestrator; leads are not covered. |
| B-13 | bug | **Edit-tool/filesystem desync on hardlinked files.** `Edit` reported success and read back new content while `sed`/`md5sum`/`stat` showed unchanged bytes. Compounded by `check-domain` blocking `xd://report_issue` from a worktree, so the member could not file it. |
| B-14 | bug | **Lead dispatches return a null yield while complete, correct work sits on disk.** **Recurred twice this cycle**: the validation panel's own lead exited 1 while returning a well-formed `PASS`, and its code reviewer hit the same shape a second consecutive panel. Work survived only because I verified artifacts on disk instead of routing on job status. |
| B-15 | bug | **Agents leak edits into the main checkout via relative paths.** Two incidents yesterday, one leaving the main tree's layout gate red. Nothing detected it automatically. *No recurrence this cycle — I re-checked; the working tree stayed confined to `tests/` and the feature directory.* |
| B-18 | chore | **The test matrix keys a required test kind on a directory label, not on the changed surface.** `test_kinds.integration.detect` is `tests/integration/**`, so any fix-only cycle that strengthens unit-resident fixtures looks structurally ungate-able. This is the mechanism behind the withdrawn finding described above; it will recur. |
| B-19 | bug | **The write-guard refuses an agent a shell append to its own in-domain path while permitting an editor write to the same path.** `harness-backend-dev` was refused `>>` on its own receipt and completed via a Python heredoc. Inconsistent enforcement between the two write routes. |
| B-20 | bug | **Reviewer digests are parsed from the assistant-text fence rather than from `yield`'s structured data**, and agents burn turns rediscovering it. Second consecutive panel affected. |
| B-21 | bug | **Two panel reviewers returned `files_touched: []` while their notes did land at the cited paths.** Self-reports understated what was written. A consumer trusting `files_touched` would conclude two reviewers produced nothing. |
| B-22 | chore | **State the test matrix's diff object in the protocol.** A fix cycle is not a change type; the matrix grades the feature's change. Leaving it implicit cost one rework cycle in this run, on my error. |

---

## What the factory still cannot tell you

Unchanged from yesterday, and worth repeating because it is easy to misread as a failure:

- **After this fix, a live claim run from `main` still reports `no_plan` for FEAT-04.** That feature
  tree exists only in the FEAT-04 worktree. The brief disclosed this before you signed. This change
  fixes the resolver; it does not by itself light up the Kaya lane. That proof belongs to FEAT-04.
- **The panel verifies the resolver and its tests, not the multi-repository lane end to end.**
  `mruangutai/harness` is deliberately out of the live fleet, so no reviewer could exercise the real
  thing.
- **The new coverage was proven with one mutation operator on one case.** It is adequate for exactly
  the claim B-3 made — that the repository is part of the cache key. Other cache-isolation failure
  shapes (wrong-repo population, eviction) are untested, and case `5b` alone carries the property.
