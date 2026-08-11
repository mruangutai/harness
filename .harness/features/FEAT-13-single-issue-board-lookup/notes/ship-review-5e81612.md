# FEAT-13 — ship review

**One targeted GraphQL call now answers what used to cost a whole-board download.** Measured live on
board 3: **1 point**, against 203 for `decompose` and 102 each for `land` and `claim`. All ten
success criteria are met, every gate is green, and the reviewer panel found no defect in the shipped
code. **It is ready to merge.**

**Two things need you.** One is a decision I already took that you may want to reverse. The other is
a collision with FEAT-12 that I deliberately did **not** resolve, because it is not mine to.

---

## What changed

Three factory tools answered a question about **one** issue by downloading the **whole** project
board. They now share one helper, `factory_gh.issue_board_item_id`, whose query is scoped to a
repository and an issue number.

| | Before | After |
|---|---|---|
| `decompose` recovery lookup | 203 points | 1 |
| `land` review-station move | 102 points | 1 |
| `claim --issue` | 102 points | 1 |
| claim poll ("what is claimable now") | unchanged, by your constraint | unchanged |

The cost tracked board size — roughly +102 points per additional 100 items — so every factory run was
getting more expensive as the board filled. That growth is gone.

**Two behaviours that used to be side effects are now deliberate checks.** `land` and `claim` both
refused closed issues only because an `is:open` board filter hid them. That filter is gone, so each
tool now checks the issue's state explicitly. `land` refuses at exactly the same point in its
sequence as before — after the branch push, after the PR create, station never set — so it ships zero
observable change, which is what you ruled.

---

## The one decision I made that you may want to reverse

**I overruled two leads and routed a fix cycle instead of sending you a plan amendment.**

The goal-check returned **SC-05 as partial**, and the reviewer panel returned three missing-guard
findings. Both recommended the same thing: bring it to you, because adding a test assertion exceeds
the assertion list you signed in `plan.yaml` step 5.

I disagreed and acted. **SC-05 was an approved criterion that was unmet.** Approved-but-unmet needs
no new signature — only a criterion that *cannot be met as written* does. An enumerated assertion
list is an implementation floor, not a ceiling; read as a ceiling, an approved criterion stays
permanently undischargeable because the plan's prose did not anticipate a gap. Nothing about scope,
the goal, or any signed decision moved, and no production code changed — tests only, in files already
in T-01's approved `files:` list.

**pm subsequently confirmed the reasoning against me.** The BRIEF's own proof standard
(`BRIEF.md:104-106` — "unit call-shape assertions plus one live read. No `factory_decompose` run
against the live board") **forbids the only technique that could instantiate a closed issue at the
unit layer, so it cannot also demand it.** pm recorded that its own earlier recommendation had been
the wrong one.

If you disagree with the principle, the remedy is cheap: the fix is one commit (`5e81612`) and
reverting it returns SC-05 to `partial`.

---

## The one thing I did NOT resolve, because it is yours

**FEAT-12 is distilling into the same shared Expertise files right now, and nothing in the harness
detects the collision.**

`.harness/expertise/` is shared across features, not feature-scoped. FEAT-12 is mid-close in the main
checkout with **six of those files modified and uncommitted**, and its write set **grew while my run
was in flight** — which is how I know it is live rather than stale. FEAT-13 modified nine.
`check-expertise.sh` validates **format, not lineage**, so a file that silently loses another
feature's rules passes it cleanly. Two leads hit this independently and both returned it blocking.

**What I did.** I committed only the three files FEAT-13 alone touched. The six contested ones are
left **modified but uncommitted** in the worktree — nothing destroyed, everything inspectable.

| Expertise file | FEAT-12 writing | FEAT-13 writing | Committed here |
|---|---|---|---|
| `backend-dev`, `code-reviewer`, `eng-lead`, `pm`, `qa`, `security-reviewer` | yes | yes | **no — contested** |
| `product-lead`, `ui-reviewer`, `validator-lead` | no | yes | yes |
| `documentor` | yes | no | not mine |

**Why not just commit them.** `eng-lead`'s member, acting in good faith, reconciled its file against
the main checkout's *live* copy — so committing would import FEAT-12's half-finished distillation
into this branch and freeze a snapshot of work that is still moving.

**The contested ops are written out in full at the end of this document** so they survive even if the
worktree is discarded. Re-apply them against the settled tree once FEAT-12 lands.

**The systemic issue is worth a ticket on its own:** shared Expertise + concurrent features + one
worktree per feature = a memory-wipe hazard with no detector. A lineage check, or excluding
`.harness/expertise/` from feature branches entirely, would close it.

---

## Verification

**Goal-check: 10 met, 0 partial, 0 not_met.** Nine criteria are automated, one is the live inspection.

- Unit suite: 10/10 scripts, exit 0. Integration: 97/97, exit 0. **I re-ran both myself at every
  commit** rather than accepting them on report.
- The blocking `test_matrix` qa gate passed. qa caught that my own dispatch named a narrower runner
  than the configured one; I re-ran the configured command.
- Reviewer panel: **PASS**, `must_fix` empty, max severity `med`, advisory. Four reviewers, four PASS.
- Live spot-check: **1 GraphQL point**, item id matched an independently derived live reference.
  **Taken twice** because board 3 carries other flows' traffic and a stray point would have read as a
  failure. Both rounds agreed, so nothing was chosen or suppressed.

**The sharpest finding of the whole feature came from a mutation, not from reading.** Nothing pinned
the field list that `claim` and `land` request from `issue_view`. Dropping `"state"` from both left
**every test green**, because the test doubles ignored the `fields` argument they were handed — while
in production that same one-line edit makes both tools **refuse every issue**. A total outage,
invisible to the entire suite. It is now pinned at both sites, and each new assertion was proven to
redden under a real mutation before I accepted it.

**Honest limits on what green buys you**, volunteered by qa and agreed by the panel:

- Assertion *strength* is proven by mutation for some criteria, not all. The rest pass, but a passing
  test is not a test that can fail.
- SC-08 proves the tools and the forked stub `gh` agree — **not** that the stub matches real GitHub.
  The stub was authored in the same task as the helper it answers.
- The panel cannot bound its own calibration: three of four reviewers returned zero or one finding on
  a nine-file diff, which fits a genuinely clean change and equally fits a shallow pass.

---

## How this briefing was assembled — no report round was spawned

I did **not** spawn any lead to report on its own work. Every run wrote a digest and I read them from
disk. Assembled from, all under
`.harness/features/FEAT-13-single-issue-board-lookup/runs/`:

`2026-08-10-01-product/digest.md` · `2026-08-10-02-eng/digest.md` · `2026-08-10-03-product/digest.md`
(the plan phase, which I did not run and inherited) · `t01-eng/digest.md` · `qa-validator/digest.md` ·
`t02-eng/digest.md` · `panel-validator/digest.md` · `goalcheck-product/digest.md` ·
`fix01-eng/digest.md` · `sc05recheck-product/digest.md` · `distill-eng/digest.md` ·
`distill-validator/digest.md` · `distill-product/digest.md`

**Those run directories are gitignored** (`.harness/features/*/runs/**`), so they exist only in the
worktree and will not survive its removal. This document is the durable record.

I copied the three plan-phase run directories into the worktree at setup for exactly this reason —
without that, this briefing would have silently omitted an entire phase.

**Budget: 4 cycles of 10. 13 runs against an informational ceiling of 20 — not crossed.** Two cycles
were the plan phase's, one was the SC-05 fix, one was a send-back inside the eng distillation. Every
other run was first-pass clean and charged nothing.

---

## Proposed backlog

Anything not listed here dies silently, so this is everything that survived collation without gating.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | **Shared Expertise has no concurrency or lineage protection.** Two features distilling at once into `.harness/expertise/` can silently revert each other; `check-expertise.sh` checks format, not lineage. Rank this first — it silently destroys the factory's memory. |
| B-2 | bug | `plan.yaml:368` tells a future reader to assert `argv[:2] == ["project", "item-list"]`, which can never match — `run_gh` prepends the `gh` binary. `:367` is already correct and the shipped tests are right. pm recommends **no amendment** (editing a signed artifact makes it stop being what was approved); record the idiom instead. |
| B-3 | chore | The grilling note this feature's BRIEF and plan cite as binding is **not reachable from the feature branch** — it lives only on `chore/203-end-copy-distribution`. A reviewer on this branch cannot open a document the approved plan calls binding. |
| B-4 | bug | `bash-write-guard.sh` does not expand shell variables when extracting a `cp` target, so `cp … "$SCRATCH/x"` is denied even though the resolved destination is outside the repo and would pass the guard's own carve-out. Literal absolute paths work. (DEC-174 carve-out file — yours alone.) |
| B-5 | bug | `validate-digest.py` keys the `suite: n/a` exemption by **persona** when the discriminator that matters is the task's `change_type`. A backend-dev on a `docs` task cannot say "no tests applied" the way a dev-ops on the identical task can. (DEC-174 carve-out file.) |
| B-6 | bug | `harness-documentor.md` fails `check-expertise.sh` — one entry is 53 words against a 50-word cap — which makes the **whole directory** check exit 1. Pre-existing, not this feature's. |
| B-7 | chore | `test-factory-claim.py:336` is a bare `json.loads(out)` with no guard. Under exactly the total-outage regression B-1's sibling fix now catches, it raises uncaught and kills the rest of the script. |
| B-8 | enhancement | No `--issue` case asserts that a **fresh open issue claims successfully**. I deliberately excluded it from the fix cycle to keep it tight; four existing assertions already redden on an always-refuse. |
| B-9 | chore | A fixture named `ITEM-CLOSED` and a label reading "resume with a closed issue" still read as instantiating a closed issue, which they do not. A corrective comment is in place. Cosmetic. |
| B-10 | chore | Creating a worktree fires a one-time shape-sweep burst over historical state files the checkout duplicates (`FEAT-02`, `FEAT-05`). Pre-existing violations, not in scope — but the noise is where a real violation could hide. |
| B-11 | chore | Sub-issues #245 and #246 were closed at T-02's commit, before the fix cycle changed T-01's test files. Reopening is not in the mirror's vocabulary; recorded, not corrected. |

---

## Open questions

None block the merge.

1. **Do you accept the SC-05 routing call?** I treated approved-but-unmet as a fix cycle rather than
   a plan amendment. Reversing it means reverting `5e81612`.
2. **How should the contested Expertise ops land?** My recommendation: let FEAT-12 finish and commit,
   then re-apply the ops below against the settled files, letting each owner re-pick displacement
   targets where a section is at cap. Do not merge those six files textually.
3. **The worktree is still in place** at `.claude/worktrees/FEAT-13-single-issue-board-lookup`, with
   the six contested files dirty. I did not remove it, because removing it discards them.

---

## Appendix — contested Expertise ops, verbatim

Recorded here because the digests that hold them are gitignored. Apply against the settled tree.

**`harness-eng-lead`** — add to Gotchas:
- `G-04: WHEN a receipt path is named both by the team file's outputs: template and by the approved plan's files: list DO write the plan's literal path — a verify: clause greps the plan's string, so the rendered template leaves the gate red on correct work.`
- `G-05: WHEN dispatching a distillation from a worktree DO grep the entry IDs from both that copy and the main checkout's and compare — a worktree branched before the last distillation carries a stale copy whose write reverts the prior feature's entries, every format check still green.`

**`harness-backend-dev`** — 5 entries accepted (3 self-derived, 2 relayed), Patterns 12→15 at cap,
Gotchas 8→9, with one Pattern displaced to hold the cap. Its file in the worktree is a full-file
renumber; take it wholesale or re-derive, never hunk-by-hunk.

**`harness-qa`** — Patterns 10→11: one entry on argument-blind test doubles. Both relayed candidates
rejected with reasons.

**`harness-code-reviewer`** — Patterns 14→15 (now at cap), Gotchas 2→3. It filed the
fake-ignores-arguments lesson as a Gotcha rather than spend its last Patterns slot.

**`harness-security-reviewer`** — Patterns 9→11, Gotchas 5→6, Outcomes 0→1 (section opened).

**`harness-pm`** — 3 ops: replace `P-07` with the signed-proof-standard rule (if a standard forbids
the only technique that could instantiate a condition, it cannot also demand it); replace `P-10` with
content-anchoring over line numbers; add a Gotcha on confirming which checkout a `file:line` resolved
in. Note `P-10` is a **merge**, not a kill — both sides widened the same incumbent in different
directions.

**Already committed** (uncontested): `harness-product-lead` (Patterns 10→11, Gotchas 4→6),
`harness-ui-reviewer` (Patterns 8→10, both self-derived), `harness-validator-lead`
(Patterns 7→10, Gotchas 6→9).
