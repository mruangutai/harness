# BUG-440 — plan review, for signature

**The plan is ready to sign, and it needs one answer from you first.** Merging this fix turns
`/harness` entry red with four blocking findings, because four records in your control plane
already contradict their own digests. That is the bug doing its job — but you choose when it
starts shouting. Pick **A**, **B** or **C** below.

**Nothing is built yet.** This was a planning run only: no production code, no test code, no
approval signature. One task is planned, and it is yours to execute — `check-state.sh` and its
tests are enforcement-layer files under the DEC-174 carve-out, so the harness plans that change
and does not dispatch it to a squad.

## The ruling you owe

Four run records in `.harness/harness/features/` disagree with their own durable digests. I
measured them independently, and pm re-measured them separately; the two measurements agree
exactly. Written as *what `feature.json` records* → *what the digest says*:

| Feature | Run | Recorded | Digest |
|---|---|---|---|
| FEAT-07-verify-teeth-batch-probe | goalcheck-product | FAIL | ESCALATE |
| FEAT-22-docs-layout-migration | 2026-08-16-15-distill-product | INCOMPLETE | PASS |
| FEAT-22-docs-layout-migration | 2026-08-16-15-distill-validator | INCOMPLETE | PASS |
| FEAT-25-claim-feature-root | 2026-08-19-6-distill-validator | PASS | FAIL |

- **(A) Merge now, accept the red.** Every `/harness` entry reports four blocking findings until
  you or a delegate reconciles those four records under a separate ticket.
- **(B) Reconcile first, then merge.** You correct the four records before this lands, and the
  gate is green on day one. These are four data edits in the control-plane root, independent of
  the code change, so B adds no scope to this feature and changes no requirement, criterion,
  decision or task. It is sequencing, and the records are yours to order.
- **(C) Send it back** for repair or grandfathering scope the plan does not have today.

The panel added option B; the plan as first drafted offered only A or C, which it called a false
dilemma, and it was right.

**One correction to your own intake, on the record.** Your grilling note states that FEAT-22
recorded a `FAIL` digest against a `PASS` entry. The disk says otherwise: FEAT-22's two rows are
`PASS` digests against `INCOMPLETE` entries, and the single `PASS`-over-`FAIL` record is FEAT-25's.
This changes nothing about what gets built — the contract quantifies over every mismatch whatever
its direction — but the record should be right.

## What is planned

One task, `T-01`, `main-session-direct`. It adds invariant **INV-37** to `check-state.sh`: for
every `feature.json` run entry whose run directory is complete, lead-hosted and carries a
structurally valid digest, the digest's final verdict must equal the recorded verdict. A mismatch
becomes a blocking finding naming the feature, the run id, both values and both file paths.
Nothing is repaired automatically — the gate reports, and a human decides which record is wrong.

Everything outside that intersection keeps today's behaviour exactly: non-lead runs, incomplete
runs, a missing digest, a digest that fails its contract, and a run directory no `feature.json`
claims. The test-first red proof is part of the task, not an afterthought.

Scale, measured at `772790be`: 308 complete lead-hosted runs, all 308 carrying a structurally
valid digest, 298 of them claimed by a `feature.json` entry, 4 contradicting it.

## How I assembled this

**I spawned no report round.** I read the run digests from disk, as the five recorded runs name
them:

- `runs/plan-draft-product/digest.md` — pm drafted BRIEF (4 requirements, 7 criteria) and
  plan.yaml. PASS.
- `runs/plan-goalcheck-product/digest.md` — pm graded the drafted plan against your grilling note,
  not against the BRIEF derived from it. PASS, four defects corrected in place — including one
  that would have made the new check stack a second finding on a digest that already fails its
  contract.
- `runs/plan-panel-validator/digest.md` — the adversarial panel. Two readers ran; five findings;
  worst severity `med`; nothing gating.
- `runs/plan-record-product/digest.md` and `runs/plan-record-fix-product/digest.md` — pm recorded
  the panel into `plan.yaml` and then added the third reader the state gate requires.

I verified the load-bearing claims myself rather than relaying them: the four mismatches, the
corpus counts, the duplicate-id exposure, the panel's central finding at source, and the gate
condition that would have fired on your signature.

## What the panel found, and what happened to it

The plan survived adversarial reading. Both readers independently cleared the five angles that
mattered — blocking rather than warning, the direction of the comparison, exact string equality,
the narrowed task verify, and the single-task granularity. Five findings survived, all resolved in
the plan text before it reached you, none gating:

- **med** — the task text anchored new code beside a line that only runs for validator squads, so
  two of the four disclosed mismatches would never have been caught. I confirmed this at source;
  the anchor now names the unconditioned line.
- **low** — the false dilemma in the ruling above; option B now exists.
- **low** — duplicate run ids would have been compared last-wins. I measured the exposure: it is
  real, not hypothetical — 1 of 65 files carries a duplicate id (both entries agree, so today's
  instance is harmless). The plan now compares every entry, as your contract says.
- **low** — the task's own check could have passed on a fabricated red proof; it now requires the
  pinned sha, the invocation and a recorded result.
- **info** — what the red proof can honestly witness; the note's reasoning was corrected, its
  conclusion stood.

**One panel run returned BLOCKED, and the reason is not about your plan.** The code-reviewer
finished its review and could not write its own note: a live claim held by a different feature's
run refused the write. I measured that claim rather than assuming it was stale — the owning
process is genuinely running — so I did not force it open, because that is the second-writer
hazard the claim system exists to prevent. The findings survived in the lead's digest and are now
in `plan.yaml`. Two harness defects came out of this run and are listed below.

## Proposed backlog

Unstruck rows become issues when you accept. Anything not listed here dies silently.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `claim_worktrees()` unions live dispatch claims for a bare agent type across every linked worktree with no feature or destination filter, so one feature's live claim refuses another feature's in-domain write. It blocked the plan panel's reviewer here. |
| B-2 | bug | A handoff note's `Done when` authorities resolve against the main checkout, so no feature born in a worktree can write one until it merges. Measured: the identical note validates clean under the worktree root and fails only under the main root. This feature has no handoff note as a result. |
| B-3 | chore | Reconcile the four mismatched records above. Required under ruling A; unnecessary under B, which does it before the merge. |
| B-4 | chore | `validate-digest.py` inlines the tail-anchor verdict idiom four times and exports no extractor; INV-37 will be the fifth copy. A shared helper is the deeper fix, deliberately out of this feature's scope. |
| B-5 | chore | Nothing asserts that `feature.json` `runs[]` ids are unique. Duplicates are legal today and one exists. |
| B-6 | bug | A subagent that returned a valid PASS digest was marked `failed (exit 1)` because its yield carried null data. The work had landed; only the job status lied. |
| B-7 | chore | 10 complete lead-hosted run directories are claimed by no `feature.json` entry. Out of scope by construction here — the check runs from the record outward — but nothing else notices them either. |

## Budget

Five runs, one cycle used of ten. The single cycle was my error, not a squad's: I told pm to record
two panel readers when the state gate requires three, and pm raised it as a question instead of
guessing. Run count is well inside its informational budget.

## What happens after you sign

The main session — not a squad — runs `gh-sync.py open`, moves the station to `ready`, and executes
`T-01` directly. Everything needed is in `plan.yaml`; the task text carries the exact structure,
the join key, the comparison and the finding's required contents.
