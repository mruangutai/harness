# Ship review — FEAT-04-decisions-index

**For Mike. Written at `fff5591` on branch `feat/decisions-index`. Validate phase complete.**

## The conclusion

**The feature is done and I recommend shipping it.** All 12 success criteria are met, verified at
`363b539` against the methods your own signed BRIEF declared for each one. The reviewer panel
passed with nothing on its must-fix list. The validate phase needed no rework at all — three runs,
three first-pass passes.

**What you are shipping.** `docs/harness/DECISIONS-INDEX.md`: one row per live decision, 170 of them,
190 lines total. Each row is a hand-written one-sentence ruling of what that decision decided, capped
at 30 words. An agent greps the index, opens the two or three entries that bear on its task, and skips
the rest — instead of reading a 4,400-line authority file whole. `CLAUDE.md` and the `harness-handoff`
skill now point agents at it, and the skill is the surface that travels to every deployed project.

**One number to be aware of, because it looks like a discrepancy and is not.** The BRIEF's prose says
169 rows; the index has 170. `DEC-170` was appended to the authority during the build, and the
criterion's operative words are "counted at run time rather than against a frozen number." 170 is
correct. I chose not to amend the BRIEF for it — the criterion as written is satisfied, and a third
signature round-trip to correct a stale example is not worth your time. Same for a second stale figure
in SC-11, which cites the pre-remediation over-cap count.

**A correction to my own dispatch.** I was told this feature had 13 success criteria. It has 12,
SC-01 through SC-12. I checked (`grep -cE '^- SC-[0-9]+'` returns 12). Nothing was dropped; the
count I was handed was simply wrong, and I am flagging it so no later reader reads a gap into it.

## Cost — over budget, and the figure is a floor

**$324 against a $120 budget. 2.7x.** It never gated anything and was never meant to (DEC-134 makes
cost informational), but you should see it plainly:

- The validate phase itself was **~$49** across three runs — the cheap part.
- The single largest line in the feature's history is run 09 at **$45.5**: six documentor spawns, each
  reading a ~1,100-line slice of the authority to write its rulings by hand. **That is exactly the
  mandatory-reading cost this index exists to remove.** The feature paid the toll once so that every
  future feature does not.
- **The $324 is a floor, not a total.** Advisor-model spend appears in no row of the cost reporter, so
  it is unmetered. This is the same measurement gap `DEC-170` leaves open, and this feature is its
  first live exercise.

The honest read: the budget was set at $120 with an explicit note that it should come down "once the
DECISIONS.md index lands and the mandatory-reading floor drops." This feature is that landing. Whether
$324 was worth it is your call, and the answer depends on how much cheaper the next feature is — which
is measurable, and is the post-ship outcome measure the BRIEF already names.

`cycles_used` stands at **6 of 10**. The validate phase added zero, because a cycle counts rework and
there was none.

## What was verified, and how

| | |
|---|---|
| Success criteria | **12 of 12 met.** Seven by automated test, five by inspection. Evidence per criterion in `notes/research-goal-check-c1.md` |
| Reviewer panel | **PASS.** Code review, security review and the QA gate, dispatched in one turn at the pinned SHA. Nothing blocking; worst severity `med`, and the review gate blocks only on `high`. `runs/2026-08-02-14-validator/digest.md` |
| The live receipt build skipped | **PASS.** The one criterion that needed a real mutation of this repo to prove: a declared-stale phrase planted bare into `docs/harness/SPEC.md` drove the docs checker from clean to a single correct failure and back to clean, tree byte-verified afterwards. `runs/2026-08-02-13-product/digest.md` |
| Repo gates | `check-docs.sh` clean at 45 patterns · unit suite green with the generator's six tests all passing · state invariants hold. All run by me, not taken on report |

**Two panel steps I cut, with reasons.** The UI review was skipped — this is a markdown-and-Python
change with no user-facing surface and no design contract to audit. And I *added* a QA step the shipped
review team does not have, because your config marks the QA gate blocking and the team file would have
exited the phase with that gate never run.

**Two steps I deferred rather than ran.** The feature-close Expertise distillation belongs after your
acceptance, not before it: the four members who did the validate work have written no observation logs
yet, so distilling now would distill the build phase twice and this phase not at all. And I wrote this
briefing myself instead of spawning all three domain leads to report — I hosted every validate run and
cite each digest by path, one lead had no activity at all, and three spawns to re-narrate documents I
already hold is spend with nothing to surface it. Both are recorded in `feature.yaml`. Say the word if
you want either round run properly.

## Proposed backlog

Nothing here gates the ship. Anything you do not strike becomes a backlog item; anything not listed
dies silently, so this is the full list.

**`Status` added 2026-08-02, after this briefing was written.** Six of these were fixed before the
merge, on this branch, each with a regression test: B-2 and B-3 in the generator, B-4, B-5 and B-7 in
the rule surfaces, B-6 in the write guard. Only the rows marked `open` still need a backlog issue.
One correction to the row text itself: **B-4 is not a disagreement about *who* writes the cost figure**
— both documents agree the orchestrator does. The defect was that both said `>>`, which appends a
second `cost:` key instead of replacing the lead's placeholder.

**Engineering — the generator (3)**

| ID | Nature | Status | Item |
|---|---|---|---|
| B-1 | `chore` | open | The generator's tests freeze the authority's decision counts as literal constants. They pass today, but **the next feature that appends a decision reddens the unit gate until someone bumps them.** The remedy is documentation, not code: the plan records the write-the-ruling duty on every future feature and omits the bump-the-constants duty beside it |
| B-2 | `bug` | **fixed** | The generator and its row test use **two different grammars for one row format.** A malformed row is treated as "no prior row" and passes silently in the generator, then fails loudly at the gate. Recoverable from git, but silent where it should be loud |
| B-3 | `bug` | **fixed** | `DEC-102`'s row states a conclusion that has since been superseded, with no superseded-by marker, so a reader can act on a dead ruling. The marker is harvested from the superseding decision's title, and `DEC-120` declares the supersession in its body prose instead |

**Harness itself (4, plus one small one)**

| ID | Nature | Status | Item |
|---|---|---|---|
| B-4 | `bug` | **fixed** | Two of the harness's own rule documents contradict each other on who writes the cost figure into a run's state file. The collision trips an invariant check and was hand-repaired on every run of this feature until I suppressed it by dispatch. Unfixed at source |
| B-5 | `bug` | **fixed** | Every per-feature `.harness/**/*.md` artifact is itself a scan target for the docs checker — documented nowhere an agent writing one would see it. It cost this feature three trips. The checker also prints the offending pattern on two separate lines, so escaping one occurrence is not enough |
| B-6 | `bug` | **fixed** | The shell write guard reads `>` and `<` inside heredoc bodies, and operands across a compound `;` line, as file redirects. Every occurrence this phase refused a legitimate command. The earlier quoted-string fix does not cover these two shapes |
| B-7 | `bug` | **fixed** | A member whose deliverable is code or a verification receipt has no writable per-feature artifact path except its observations log — which by design is never injected anywhere, so it gets overloaded as a handoff channel |
| B-8 | `chore` | open | The QA note invented a verify-method label (`audit-only`) that the BRIEF does not define. Small, but it is the kind of drift that makes a criterion's method unauditable |

**Process (1)**

| ID | Nature | Status | Item |
|---|---|---|---|
| B-9 | enhancement | open | All three panel members re-derived gate results they were explicitly told to audit rather than reproduce. The receipts came out independent, which is a genuine gain — but the instruction did not hold, and that is worth pricing deliberately rather than rediscovering |

**One standing obligation, not a backlog item — a new rule of the road.** From now on, any feature that
appends a decision to `DECISIONS.md` must regenerate the index **and** write that row's ruling in the
same commit, or the unit gate fails. `DEC-170` was the first exercise of it and it worked.

## Disclosure — advisor influence on this run

`DEC-170` requires me to say where a stronger reviewer changed a decision of mine. It changed seven,
and this is the decision's first live run:

1. SC-08's live receipt was run as its own step **before** the panel rather than alongside it — the
   plant is a live mutation of a reviewed file, and a reviewer reading mid-plant sees a tree that does
   not match the pinned SHA.
2. The panel was told to **audit** that receipt rather than attempt it — no reviewer can write the file
   in question, so a reviewer would have reported the criterion unmet for being unable to run it.
3. The documentor was warned not to reproduce the pinned phrase bare in its own report, which would
   have left the phrase live in a second scanned file and defeated the revert.
4. QA's dispatch was scoped to matrix conformance plus an anchored check, with the false-failure trap
   named — the runner's output contains test *names* that look like skip lines.
5. Expertise distillation was not folded into the briefing spawns to save cost: the two are a write
   protocol and a read-only summary, and merging them makes a rejected candidate indistinguishable
   from an unmentioned one.
6. Distillation was then **deferred entirely**, on the ground that validate-phase members hold no logs
   yet — I had been about to run it early.
7. The three-lead briefing round was **dropped** and disclosed rather than run.

Items 6 and 7 are the two that saved real money — roughly $100 of lead spawns on a feature already at
2.7x budget. Items 1 through 4 each prevented a specific false result.

## What I did not do

I never wrote an `## Approval` block, never merged, never opened a PR. The ship decision is yours. The
GitHub mirror is off in this project's config, so all three sync points skipped.
