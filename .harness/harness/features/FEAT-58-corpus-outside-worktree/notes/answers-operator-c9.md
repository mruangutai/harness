# Answers — FEAT-58-corpus-outside-worktree — operator disposition, cycle 9

**The plan is accepted. This file is the disposition of the seven open findings, and the terms I
signed under.**

## Q1 + Q2 — H-01 — CONVERT to a build-phase task, with M-01's remedy folded in

Take the panel's own cheapest close, which is Q2: the build task asserts that **the reached
feature-directory name set equals `os.listdir(<owner_root>/.harness/harness/features)`**. One
assertion closes H-01 and M-01 together and needs no SC-16 edit.

Two conditions on the converted task, and the first is the whole point:

- **It must carry a MISSING-producing mutation, never the cycle-8 wording.** My cycle-8 instruction
  said to stage the pre-fix `feature.json`-keyed derivation and record that clause 1 reddens naming
  the 89-versus-79 mismatch. That instruction is **wrong and is hereby withdrawn.** The pre-fix
  staging yields `MISSING=[]` / `UNEXPECTED=10` arithmetically — 89 directories, 10 record-less
  (#1640), 79 records bijecting over the rest — which clause 1 as PP-03 loosened it *tolerates*.
  A task worded from cycle 8 would inherit the contradiction rather than fix it, and worse, the
  tolerated report prints the very "89 versus 79" names my instruction predicted as the red. That
  is an invitation to record a false red, which is the one outcome worse than no proof at all.
- **The name-set equality is the assertion, not a count.** A count re-opens the pinned-literal
  problem SC-16 already rejects; a name set is stable under the tree gaining features.

**Naming this one honestly: PP-03 and PP-04 were each individually correct rulings of mine that
turn out to be jointly unsatisfiable.** Loosening clause 1 to "no refusal" was right, and demanding
a red proof was right, and together they mean the red proof has nothing left to redden on. That is
my error, not the team's, and it is the reason the remedy for a blind control came out blind. It is
recorded here so the build task is written from this reasoning rather than from my earlier
instruction.

## Q3 — M-01 — closed by Q1's folded assertion

No separate disposition. Note for the record that the unreachable print branch was the product
lead's cycle-8 addition endorsed in briefing — disclosed rather than buried, which is why it was
findable at all.

## Q4 — M-02 and L-03 — ACCEPTED in `approval.rulings`, not fixed

PART 2 clauses 3–4 still say "cwd at the probe", the spelling I struck at PP-01, and `cwd` is inert.
Build catches both the moment the test is written: a clause that sets `cwd` and expects it to select
a tree fails against a script that resolves its root from `_selfdir`. This is exactly the class my
cycle-8 terms said to accept rather than spend a cycle on.

## Q5 — L-02 — FIXED BY ME, at no cycle cost

`BRIEF.md:401-403` asserted `core.hooksPath` is "tracked so it travels with a clone" — the claim I
personally withdrew at cycle 8 and corrected in the DoD note. You were right to refuse to spend the
tenth cycle on it and right to flag that it is the document I sign. It is corrected at source now,
carrying the real mechanism: onboarding sets the config, INV-31 refuses a clone missing it.

"Low by mechanism, high by salience, and it is the document you sign" is the correct way to raise a
finding whose severity model understates it. Keep doing that.

## Q6 — L-01 and NF-01 — ACCEPTED in `approval.rulings`

A stale guard anchor with an over-broad `--force` claim, and a low that INV-31 catches on the next
`check-state.sh` run. Neither has runner exposure; neither justifies a cycle.

## The terms I am signing under

Recorded so that what I accepted is legible later without reading this whole thread:

1. **Four findings accepted as known residue** — M-02, L-03, L-01, NF-01. Build catches the first
   two; the second two have no runner exposure.
2. **One finding converted to build-phase work** — H-01 with M-01 folded in, under the two
   conditions above, and explicitly NOT worded from my cycle-8 instruction.
3. **One finding fixed by me at signature** — L-02.
4. **Nothing structural.** The panel enumerated a producing mechanism for all ten REQs rather than
   asserting soundness, and no open finding names a REQ the design cannot deliver. That is the
   claim I am relying on, and it is checkable in `runs/planpanellast-validator/digest.md`.
5. **One cycle unspent**, deliberately. It is the margin for build, not a resource to burn on plan
   text.

## On the three corrections against you, all from subordinates, all left in the record

The largest — telling the transcription segment that all six PP fixes landed when PP-01's and
PP-04's residuals *are* M-01 and H-01 — matters because pm followed the goal-check over your
dispatch and stamped each row with a `disposition_source` saying so. The record is right because a
subordinate checked, and you said exactly that instead of taking the credit.

Three self-reported errors across nine cycles, each one making you look worse and the record better,
is why I am prepared to sign on a panel digest I have not read line by line. That is what the
honesty rule is for, and it is the only reason a signature at cycle 9 is defensible rather than
fatigue.

## What happens next

Both artifacts are signed. Move the task sub-issues to `Ready` and hand off to build. The build
phase carries one extra task: H-01 converted, per Q1.

Signed by the operator at cycle 9.
