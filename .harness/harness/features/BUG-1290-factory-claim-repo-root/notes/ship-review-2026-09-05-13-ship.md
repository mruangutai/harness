# Ship review — BUG-1290, factory claim resolves the feature repository root

**Recommendation: SHIP.** Every gate is green and no gate is hedged. All nine success criteria are
MET, verified by the product manager running the tests itself rather than reading anyone's report.
The four-reviewer validation panel returned PASS with an empty `must_fix`. The blocking qa
test-matrix gate passed. The simplify pass found nothing worth applying and said so instead of
inventing work.

Two things need your decision, neither of which blocks the ship, and both are below under
**Decisions for you**. Fifteen residual findings survived collation without gating; they are the
backlog table at the end. **Anything you do not strike becomes a backlog issue on acceptance, and
anything not in that table dies here** — so it is deliberately long.

---

## What the bug was, and what now happens instead

`factory_claim.py` read every claimed issue's plan under one hardcoded root. The factory could
*decompose* a feature stored under another registered repository's segment, but claim could never
*read* that plan back, so it reported `no_plan` and refused. The live consequence was that the
factory lane ran end to end for this repository and for nothing else.

Claim now resolves each candidate's features root from that candidate's own repository, through one
shared segment rule with a single home. The old hardcoded global is gone — not aliased, not kept as
a fallback. Both of `_BlockerCache`'s caches were re-keyed onto the `(repository, feature)` pair, so
two repositories carrying the same feature id can no longer be served each other's plan.

**One disclosure that is easy to misread as a failure, and is not.** After this fix, a live claim
run from `main` *still* reports `no_plan` for FEAT-04. That feature's tree exists only in the
FEAT-04 worktree and landing it is FEAT-04's work, not this bug's. The brief disclosed this before
you signed. This change fixes the resolver; it does not by itself light up the Kaya lane.

---

## The gates, in order

| Gate | Result | Evidence |
|---|---|---|
| Build, T-01..T-05 | PASS, 1 send-back | `notes/build-digest-reconstructed-2026-09-05-07-eng.md`, six receipts |
| qa test-matrix (the project's only blocking gate) | PASS | `notes/qa-test-matrix-c1.md`, `runs/2026-09-05-09-validator/digest.md` |
| Simplify, four angles | PASS, empty | `runs/2026-09-05-10-eng/digest.md` |
| Validation panel, four reviewers | PASS, `must_fix: []`, `severity_max: med` | `runs/2026-09-05-11-validator/digest.md` |
| Goal-check, SC-01..09 | PASS, all nine MET | `runs/2026-09-05-12-product/digest.md`, `notes/research-BUG-1290-factory-claim-repo-root-goalcheck-ship-c1.md` |

Reviewed at pinned `review_sha 76e2638622a8e4095d1ef11a769a0b598ff06e25`. Branch
`feat/BUG-1290-factory-claim-repo-root`; no pull request opened, nothing merged.

**Four things in this run were checked by measurement where a report would have been accepted**, and
they are why the PASS is worth something:

- The build was test-first *by reconstruction*, not by assertion. QA cut disposable checkouts at the
  two test commits and ran the suites against pre-fix production: all six new unit cases printed
  `FAIL`, and the integration file showed 12 failing checks including every `(F)` and `(H)` claim
  line. The red state the plan demanded was real.
- The panel's two self-scoping reviewers **both looked and both stayed in scope**, which is a
  stronger result than a decline. Security judged repository-name-to-path the trust boundary and
  audited it. The UI reviewer judged the `no_plan` refusal a real operator-facing surface, and
  traced where that message goes — the operator's own terminal, never a shared GitHub issue. Neither
  could have closed that question alone.
- QA did not reason about the two coverage worries it inherited; it *measured* them, in throwaway
  checkouts. One turned out true and became a backlog row; the other turned out **less** severe than
  it had been described.
- The product manager built its own mutants during the goal-check rather than trusting case names.
  That is how it separated a clause that is proven from a clause that is merely delivered — the
  distinction behind decision 2 below.

---

## Decisions for you

**1. REQ-05's wording is inaccurate about the code that satisfies it. Correct the record, or leave
it?**

REQ-05 and D-01 both say the segment rule is "called by `factory_claim.py`,
`feature-worktree.py:resolve_repo` and `factory_config.workspace_path`". Measured at the pin,
`segment_of`'s direct callers are `features_root`, `workspace_path` and `feature-worktree.py:86`;
`factory_claim.py` reaches the segment only *transitively*, through `features_root` — which is
exactly the split you signed knowingly. Both the code reviewer and the product manager found this
independently.

The code is right and the criterion is MET: SC-06 is worded as "reaching the segment through that
one definition", which transitive reach satisfies, and SC-06's own measurement (0 / 0 / exactly 1)
passes. What is wrong is the sentence. The product manager recommends a one-line correction —
"reaches, directly or through `features_root`" — recorded as your ruling on the approved brief. No
agent may edit an approved artifact, which is why it comes to you. **Doing nothing is defensible**:
the risk is only that a future reader greps `factory_claim.py` for `segment_of`, finds nothing, and
either concludes the seam was never wired or "restores" a direct call that duplicates the rule.

**2. One clause of REQ-02 is delivered but unproven. Spend a cycle now, or ship it as disclosed
residue?**

REQ-02 says neither repository reads the other's plan "from disk or from cache". The *plan* half is
proven: the product manager's mutant that re-keys the plan cache on feature alone reddens case `5b`
and only `5b`. The *issue-map* half is delivered in the code but nothing catches its removal — a
mutant that re-keys the issue map on feature alone reddens nothing, because both `5b` fixtures carry
an empty issues map.

This is a **test-only** gap, not a behavioural one. The code is correct; the fixture is thin. It is
roughly two lines in T-01: give one segment a non-empty `factory.issues` map. SC-02's own text gates
the cached *task*, which is proven, so this gates nothing and the panel did not call it `must_fix`.
It is listed as **B-3**. Striking B-3 and asking for a fix cycle instead is a reasonable call; so is
shipping and letting the row stand.

---

## Two things that went wrong in the process, which you should know about

Neither affects the delivered code. Both are recorded here rather than smoothed over.

**A build member edited the main checkout.** Three of T-04's edits landed in
`/Users/molchairuangutai/GitHub/harness` instead of the feature worktree, and left the main tree's
layout `features` surface at `CANNOT_VERIFY` — a red gate on your working checkout, caused by this
run. The engineering lead reported that a *different* stray edit had been reverted and that both
trees were clean; that report was **wrong**, and only a direct `git status` on the main checkout
caught the rest. The files were backed up to `/tmp/bug1290-main-residue/` and restored; the main tree
re-measures `CLEAN`. Your unrelated work in that checkout was left untouched.

**Two run digests were destroyed and cannot be recovered.** The qa lead and the simplify lead each
wrote into a run directory an earlier run already owned, overwriting the plan-phase panel digest and
the build digest respectively. `runs/` is gitignored here, so there was no copy. The build digest was
reconstructed from the engineering lead's own returned summary, held verbatim at the time of loss,
and is labelled as a reconstruction at
`notes/build-digest-reconstructed-2026-09-05-07-eng.md`; the plan panel's substance survives in
`plan.yaml`'s `panel:` key, which is its canonical home by design. Both clobbered directories now
carry a `CLOBBERED.md` explaining what is missing. Rows **B-12** and **B-14** track the causes.

---

## How this briefing was assembled

**No report round was spawned.** Every claim above was read from a digest already on disk, or
measured directly. The digests assembled from, all under
`.harness/harness/features/BUG-1290-factory-claim-repo-root/`:

`runs/2026-09-05-01-product/digest.md` (plan authored) · `runs/2026-09-05-02-eng/digest.md` (plan
architecture review, FAIL, 9 findings) · `runs/2026-09-05-03-product/digest.md` (findings applied) ·
`runs/2026-09-05-04-product/digest.md` (plan goal-check against stated intent) ·
`runs/2026-09-05-05-product/digest.md` (verify-integrity fixes, T-05 added) ·
`runs/2026-09-05-06-validator/digest.md` (adversarial plan panel, FAIL, 2 blockers) ·
`runs/2026-09-05-07-product/digest.md` (blockers closed, panel transcribed) ·
`runs/2026-09-05-09-validator/digest.md` (qa gate) · `runs/2026-09-05-10-eng/digest.md` (simplify) ·
`runs/2026-09-05-11-validator/digest.md` (validation panel, with both lost reviewer notes as
verbatim appendices) · `runs/2026-09-05-12-product/digest.md` (ship goal-check) ·
`notes/build-digest-reconstructed-2026-09-05-07-eng.md` · `notes/qa-test-matrix-c1.md` ·
`notes/review-harness-security-reviewer-c1.md` · `notes/review-harness-ui-reviewer-c1.md` ·
`notes/handoff-plan.md`.

`runs/2026-09-05-08-validator/digest.md` is the plan panel's slot and no longer holds the plan
panel's content; see the clobber note above.

The orchestrator additionally re-ran all five task `verify:` commands itself on the committed tree
rather than accepting the build digest's word for them, and measured the main checkout's layout
surface before and after restoring the residue.

**Budgets.** 13 runs against an informational budget of 20 — comfortably inside it, and the count is
honest work: three plan rework cycles closed nine architecture findings and two panel blockers before
a line of code was written, which is why the build cost exactly one send-back. 4 rework cycles used
of a hard 10.

---

## Proposed backlog

Strike any row by its ID. Unstruck rows become backlog issues on acceptance.

### Product residue — this change

| ID | Nature | Finding |
|---|---|---|
| B-1 | chore | **REQ-08 has no committed defender.** QA measured it: deleting the `factory_config.py` features reader row entirely still yields `CLEAN`, because the other four readers alone supply migrated evidence. Only T-04's reader-row probe discriminates, and it lives in `plan.yaml`'s `verify:` block, which CI never re-runs. Promote the probe into a committed case in `tests/integration/test-layout-migration.py`. Not a shipped defect — SC-09's signed wording already declares its evidence to be the suite *plus* the probe — but real forward-looking regression risk. |
| B-2 | chore | **Mutation depth is one seam.** `features_root` has a dedicated mutation proof; `segment_of` does not. QA measured that a `segment_of` mutant *does* redden case `5d`, so the property is caught — only the committed proof is missing. Extend a T-05-style proof to `segment_of`. Low priority; the earlier description of this gap overstated it. |
| B-3 | chore | **REQ-02's issue-map clause is unproven.** See decision 2 above. ~2 lines in T-01: give one `5b` fixture a non-empty `factory.issues` map so a mutant re-keying the issue map on feature alone reddens something. |
| B-4 | chore | **`factory_claim.py:38` `_BIN_DIR` is now dead within its module.** Its only remaining reader is unit case `5d`, reaching it as `claim._BIN_DIR`. Harmless today — both resolve to the same directory — but a later reader deletes it and reddens `5d` for a reason unrelated to what `5d` tests. Repoint `5d` at `fc._BIN_DIR` and drop the leftover. |
| B-5 | chore | **`features_root`'s join is not traversal-safe in isolation.** Reproduced: `"owner/../../etc/passwd"` escapes the harness root and `"owner/"` silently collapses the segment. **No attacker-reachable path today** — candidate step 4 filters on exact `fleet.yaml` membership before any call, and no writer in the tree derives a fleet entry from issue or pull-request content. Reaching it needs an operator-authored malicious `fleet.yaml`. Defence in depth only; the security reviewer marked it not-actionable itself. |
| B-6 | bug | **The `feature`-label-derived join is unvalidated, and `feature` *is* attacker-influenced** (it comes from an issue label): `factory_claim.py:170,190`. **Pre-existing** — identical in shape before this change, which only altered which root it joins under. Raising it against this diff would have been scope creep; it belongs to the factory owner. |
| B-7 | chore | **`segment_of`'s docstring claims to be "the one home of that rule" and the tree disagrees.** Four identical derivations survive at `post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231`. They are correctly out of scope and stay; the gap is that nothing indexes them where a future reader would look. Index them as consolidation candidates. |
| B-8 | chore | `_BlockerCache._plan` and `.issue_number` each construct the `(repo, feature)` key inline (`factory_claim.py:103,135`) rather than through one accessor — two spellings to keep in lockstep. A `_key(repo, feature)` helper. Declined during simplify as not worth a production edit at the pin boundary. |
| B-9 | chore | `features_root(repo)` is resolved at three call sites in `_BlockerCache` rather than once per repository. The efficiency angle costed it and found it inert (`harness_boundary.resolve_root` measured at 13.32 µs per call, and the pair keying reaches it at most twice per unique pair per poll), so this is a shape note with no measured consequence. |
| B-10 | chore | **REQ-05's wording correction** — decision 1 above. Listed here so it survives if you would rather queue it than rule on it now. |

### Harness defects observed during this run

These are defects in the factory itself, not in the change. They are listed because this repository
*is* the harness and each one cost real work today.

| ID | Nature | Finding |
|---|---|---|
| B-11 | bug | **`check-domain` matches inflight claims by bare agent-type across every linked worktree, with no session scoping.** A concurrent same-role session on an unrelated flow becomes that role's only binding and refuses every other instance of the role. Read-only dispatches never hold a claim of their own and cannot self-service. **This refused six agents' note writes across two consecutive runs** — all four simplify readers, then the code reviewer and the qa reviewer on the panel. No agent shortened its work; every analysis was returned inline and transcribed. It is the single most expensive defect in this run. |
| B-12 | bug | **Nothing stops a lead writing its digest into a run directory another run already owns**, and `runs/` is gitignored, so the overwrite is unrecoverable. It happened twice today and destroyed two digests. Notably, the guard *does* refuse this for the orchestrator ("run digest already holds a recorded digest") — the leads are not covered by it. |
| B-13 | bug | **Edit-tool/filesystem desync on hardlinked files.** During T-04, `Edit` calls on `.claude/skills/harness/bin/layout_migration.py` reported success and read back as new content while `sed`, `md5sum` and `stat` all showed unchanged bytes; a later read reverted to stale content. Worked around with an in-place `python3` replace. The member could not file it — `check-domain` blocks `xd://report_issue` from a feature worktree, which is a second defect inside the first. |
| B-14 | bug | **Two lead dispatches returned a null yield** despite complete, correct work sitting on disk. Their results survived only because the orchestrator went looking for the artifacts. A third dispatch, the panel's code reviewer, **exited 1 while returning a well-formed `PASS`**; the same shape was recorded in the plan phase for the dev-ops reader. A lead routing on job status rather than on the digest would misroute a completed reviewer. |
| B-15 | bug | **Agents leak edits into the main checkout via relative paths.** Two separate incidents this run, one of which left the main tree's layout gate red. Nothing detected it; the orchestrator found it by running `git status` on a checkout it was not working in. |

---

## What the factory could not tell you

- **REQ-04 and SC-04 are fixture-only and stay that way.** DEC-174 keeps `mruangutai/harness` out of
  the live fleet, so no reviewer could exercise the real multi-repository lane. The panel verifies
  the resolver; it does not verify the Kaya lane end to end. That proof belongs to FEAT-04.
- **Three of the four panel reviewers re-ran suites the qa segment had already run.** The genuinely
  new measurements this cycle were qa's two experiments and the code reviewer's independent probe
  run. The convergence is real, but it is not four independent samples.
- **The plan panel's own digest is gone** (see above). Its findings survive transcribed in
  `plan.yaml`'s `panel:` key; its prose does not.
