# FEAT-20 — migration detector — ship review

**FEAT-20 is ready to ship.** All 15 success criteria are met, the one blocking gate passed, the
review panel found nothing that gates, and the four tasks landed as four commits on
`feat/FEAT-20-migration-detector`. Merge is yours; nothing else waits on anyone.

**What you now have.** A detector that says whether this tree is half-migrated between the old
`.harness/features/…` + `docs/harness/…` layout and the per-repository root — judged **per coupled
surface**, so a tree with features migrated and docs not is a sanctioned state that passes rather
than a false alarm. It runs at session entry and in the required CI job, and a reader it cannot
classify is **cannot-verify, never clean**. On today's tree it reports `features: CLEAN`,
`docs: CLEAN`, `examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)`, exit 0.

**Why that last line matters more than the verdict.** This feature exists because of issue #148 — a
check that passes forever. A detector that searched nothing would also print CLEAN. The examined
counts are what distinguish the two, and both call sites refuse to pass when any of the three reads
zero.

## How this was assembled

**No report round was spawned.** Every claim below is drawn from a digest already on disk, cited by
path, so this costs zero extra spawns — and so you can tell a complete briefing from one missing a
phase:

- `runs/plan-product/digest.md` — the plan phase (the eng review is nested inside it)
- `runs/plan-eng/review-architecture.md`, `-c2.md`, `-c3-delta.md` — **this run wrote no `digest.md`**;
  those three files are its entire record
- `runs/t03-eng/digest.md`, `runs/t04-product/digest.md` — the two dispatched build tasks
- `runs/qa-gate-validator/digest.md` — the blocking gate
- `runs/2026-08-14-1-validator/digest.md` — the review panel
- `runs/2026-08-14-2-product/digest.md` and `notes/uat-goalcheck-c0.md` — the goal-check
- `runs/2026-08-14-3-{eng,product,validator}/digest.md` — close-out distillation
- Receipts for the two hand-built tasks: `notes/receipt-main-session-t-01.md`, `-t-02.md`

**Ship-refresh was skipped, correctly:** no codebase map exists in this repo, so there is nothing to
mark stale. Verified, not assumed — there is no `.harness/map/` and no `INDEX.md` anywhere.

## The record, by phase

**Plan.** Two send-backs killed two silent-pass holes. One mattered enormously: `CLEAN` was
**vacuously true over an empty reader set** — issue #148's own shape inside the feature built to
eliminate #148. It was found by the UI reviewer as advisory and promoted to blocking by the product
lead, which that digest calls "the one call that changed what this squad shipped."

**Build.** T-01 and T-02 were hand-built by you under the enforcement-layer carve-out, red-first,
with the red run recorded. T-03 and T-04 went out concurrently and both returned clean first-pass.
Both are pure additions — 52 and 65 insertions, **zero deletions between them**. I re-ran every
task's verification here rather than trust a receipt.

**Validate.** The blocking test gate passed with both registration greps firing — the part that
matters, since a suite exiting 0 without running the new file is this feature's own subject. The
panel passed with nothing gating, and it earned that: the code reviewer **built a live mutant and
proved it live** before claiming the shipped cases survive it; security **timed the regexes against
a 400k-character adversarial string**; QA re-ran both kinds in a throwaway worktree rather than
relay the gate that had already passed.

**Goal-check.** 15 of 15, each verified first-hand at the pinned commit. One criterion needed your
ruling and got it — recorded twice, at `notes/answers-sc10-ruling.md` and
`notes/answers-2026-08-14-2-product.md`. Both records agree; the duplication is harmless.

**Close-out.** Three squads distilled cold and concurrently. **38 operations across twelve files —
25 additions, 12 replacements, 1 deletion — for a net 269 to 293 entries**, measured against the
commit predating every distillation write rather than taken on three leads' word. Eight candidates
were rejected with reasons. Most sections were already at cap, which is why a third of the ops had
to kill something to land. The one deletion is the most valuable line here: a dev-ops rule asserting
this repo has no `.github/` and that hooks are its only wiring mechanism — both clauses false, and
the same squad had just edited a CI workflow. No entry present before the close-out is missing
after it.

## The one thing I would not ship quietly

**The suite is correct today; it is not pinned against regression.** No mutation proof exists, so a
green run cannot distinguish a suite that discriminates from one that would pass on a broken module.
The panel turned that from a worry into two named, specific holes — see B-3. This does not gate, and
it is the item most likely to cost you later, because units 3 through 7 are told to lean on this
detector.

## Three corrections to the record

Rather than quietly absorb these: **two leads caught false premises in my own dispatches.** I wrote
that three reviewers hold no `Write` on their Expertise files (they do — their agent files and the
org config both say so), that the UI reviewer ran once (it ran twice), and I credited a member with
a check its lead had actually run. Each cost part of a lead's run to correct. That failure is now the
replacing entry in my own Expertise file.

## Proposed backlog

Unstruck rows become issues on your acceptance. **Anything not listed here dies silently**, so this
is everything that survived collation and does not gate.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `check-state.sh` runs `cd "$root"` before its heredoc, so the scanned tree precedes `PYTHONPATH` on `sys.path` and a planted `harness_yaml.py` or `layout_migration.py` executes at **every session entry**. Pre-existing and byte-identical before this feature — not a regression here, but RCE-shaped on any root not fully trusted. |
| B-2 | chore | `plan.yaml:663-665` and DEC-194 both claim every finding names the reader path; two cannot-verify causes correctly name none. **Narrow both** — a docs-only fix leaves the approved plan contradicting the code. Wanted before unit 3, which is told to cite DEC-194 as its maintenance contract. |
| B-3 | chore | Mutation follow-up, first target named: `check-state.sh:1302-1318` dispatches the finding's wording across four `if/elif` branches with **no trailing `else`**, and only one of four causes is rendered by any test. Delete the `no-rows` branch and every suite stays green while session entry reports a clean tree over a surface nobody verified. |
| B-4 | chore | Containment criteria that **enumerate permitted files** will trip on the harness's own bookkeeping every time, as SC-10 just did. Consider stating the outcome instead — "nothing is renamed, no reader is migrated" — which this feature's own detector can verify. Includes rewording SC-10 if you want the trap closed rather than ruled around. |
| B-5 | bug | `bash-write-guard` refuses redirects whose target is a shell variable, so the plan's `verify:` clauses — which redirect to `$(mktemp)` — are **not runnable verbatim by the agent required to run them**. Every clause here was run with literal paths instead. It also cost the code reviewer a detour through another tool. |
| B-6 | bug | The orchestrator playbook says to record the phase in `feature.json` `phase:`; `feature-schema.json` sets `additionalProperties: false` and defines no `phase`, so that write fails validation. One of the two is wrong. |
| B-7 | bug | `validate-digest.py:92` binds `qa` to gate fields and `:612-615` rejects a placeholder alongside `PASS`. A distillation dispatch runs no gate, so **every feature-close distillation returns BLOCKED** and drags its lead up with it. The file already has the mechanism to fix it — the `CONDITIONAL` table governs one field's obligation by another's. |
| B-8 | bug | The repository layer of Expertise, `.harness/<repo>/expertise/<agent>.md`, appears in **no domain grant**, so no agent at any tier can write it. The craft/repository split shipped without the grant that makes its second half usable; one entry this feature was returned unwritten because of it. |
| B-9 | chore | The ops schema has no verb for a rejection, and a member reached for `op: reject` unprompted. Either add one so rejections are machine-visible receipts, or say in the skill that prose is the intended home. |
| B-10 | chore | A member's runs can sit outside its owning lead's view at distillation. The UI reviewer is a validator-squad member whose plan-time run was hosted by the product lead; the product lead correctly refused to distill it and the validator lead caught it, but a missed run is a lesson lost permanently. |
| B-11 | chore | Shared `.harness/expertise/` has **no concurrency or lineage protection**. Two features distilling at once would silently revert each other. Met as a near-miss this run and avoided by a lead's judgement, not by a mechanism. |

**Already ticketed, not a new row:** `.github/workflows/tests.yml:110-114` carries a comment falsely
claiming a test asserts the neighbouring CI step is wired. Pre-existing, byte-unchanged here, and
owned by issue #279 — deliberately left standing.

**Considered and dropped:** the new decision entry's line wrapping is wider than the file's average.
Measured before deciding — 16% of the file's existing lines already exceed 100 characters against
25% of the new entry's. Within existing practice; not worth a row.

## Numbers

- **4 cycles of 10.** Two from the plan phase, one from a QA send-back, one from a distillation
  send-back. Every dispatched run was otherwise clean first-pass.
- **10 runs of 20** — inside the informational tripwire, and a **floor**: T-01 and T-02 were
  hand-built and are not counted.
- **8 files shipped**, zero renames, 4 tagged commits.

## What is left for you

Merge, and accept the ship. Both stay yours — nothing in the harness does either. On acceptance the
unstruck backlog rows become issues, the milestone closes, and this document is posted to the parent
issue as its ship review.
