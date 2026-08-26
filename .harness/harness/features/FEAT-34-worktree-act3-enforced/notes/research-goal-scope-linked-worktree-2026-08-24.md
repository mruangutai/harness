# Goal-scope: is the linked-worktree sweep case an emergent success criterion?

**Shape 2 — a new SC-16, under Amendment 3. But NOT a new requirement.** The requirement is already
signed; what is missing is the criterion that can falsify it. This is the identical shape the
operator already signed as Amendment 2 (`BRIEF.md:357-404`), in this same brief.

## The requirement that already covers it — REQ-11, verbatim

> REQ-11: When a merge lands the default branch locally and **a feature it carries** has reached its
> terminal state, that feature's terminal status and its milestone closure are recorded without
> anyone running a command. (`BRIEF.md:309-311`)

"a feature **it** carries" — the antecedent is the default branch the merge landed on. In the
measured repro the sweep recorded a terminal status and closed a milestone (811) for a copy the
landed default branch does **not** carry, and left the copy it does carry (810) unrecorded. Both
clauses of REQ-11 are violated. Nothing emergent at the requirement level.

REQ-07 (`:73-74`) is secondary: it binds removal, and in the repro the removal itself was of the
right checkout — the harm was the write. Cite REQ-11 first.

## REQ-05 does not cover it — the operator's caution, closed rather than skated past

REQ-05 (`:64-66`) has two scoping problems and either one is fatal to citing it here.

1. **Its subject is "the refusal"** — `check-state.sh` / INV-29. The hook is REQ-07/REQ-11's
   territory, and the brief keeps the two mechanisms deliberately distinct ("the hook closes the
   window, the invariant proves it closed", `:41-42`).
2. **Its predicate is a branch, not a root.** REQ-05 says which *branch's* copy of `feature.json`
   is read. The defect is which *repository root* `feat_dir` resolves under, and the two come apart
   mechanically: a linked worktree shares the object store, so `git rev-parse main:<rel>` from
   inside WT_CALLER returns the landed blob correctly. The defect bypasses branch resolution
   entirely — `feat_dir` was a **filesystem path** handed to `gh-sync.py ship`, which reads and
   writes the working-tree file. REQ-05's mechanism was never engaged.

Citing REQ-05 would be a same-shape/different-claim substitution. Do not.

## DEC-95 is the decision that makes the defect a corruption, not just a wrong path

DEC-95 (index `:114`) fixes `.harness/` as **per-worktree state**. A linked worktree's copy of a
feature directory is therefore *legitimately* divergent — which is exactly why writing a terminal
record into it destroys rather than duplicates. The brief cites DEC-95 under SUPPLIES (`:105-106`)
and no criterion grades that the sweep respects it. Nothing else in the index bears (DEC-143 is the
domain guard's path matching; DEC-193 is the two legal code locations).

## Why not shape 3, a recorded verification gap

A verification gap records something **not proven**, carried by something else. This is proven:
`test-post-merge-sweep.py` `case_linked_worktree_main_checkout` (`:664`) asserts six clauses and is
green — measured now, at the working tree: 47 PASS, 0 FAIL, exit 0. Recording it as a gap would
falsify the record in the flattering direction.

**The adjacent gap is genuinely a different gap — the operator's belief is confirmed.** "This
operator's own clone is graded by nobody" (`:347-351`) is about an act the *operator* performs in a
*real* clone (repointing `core.hooksPath`), and its stated reason for not being an SC is that "a
fixture can fake it and this one cannot be faked." The linked-worktree case is the exact inverse: it
is fixture-gradable, already graded in a fixture, and the fixture cannot fake it because the
assertion turns on a resolved path equal to one directory and unequal to another. Different subject,
opposite gradability, opposite conclusion.

## Cost, both sides

**Cost of SC-16:** one third re-signature; the `## Approval` note grows a fourth clause and the date
moves again. **No engineering cost** — the behaviour is implemented, the test exists, and it is
registered in both integration enumerations (`harness.json:119` and `run-unit-tests.sh:18`, both
verified). No task changes, no re-approval of the task set.

**Cost of no SC-16:** the only evidence for a failure mode that destroyed the sole carrier of a
record, and that consumed three rework cycles, is ungraded. The goal-check would trace REQ-11 to
T-03/T-04 and find SC-06, SC-07 and SC-11 all met — every one of them passes against the defective
implementation. If case (i) were weakened or dropped in a later refactor, nothing in the brief would
notice. Who carries it: nobody. That is the whole finding.

## Paste-ready wording — the operator's to sign, nobody else's

Note on the red-proof clause: the failing state is already recorded, in the case's own docstring
(`test-post-merge-sweep.py:665-687`, "Against TODAY's code this line does not exist at all
(RED: not found)"). The clause is kept in the brief's register; the operator can check it is already
discharged rather than owed.

---

## Amendment 3 (2026-08-24) — the sweep's own on-disk location is graded

**PURELY ADDITIVE. NOT YET RE-SIGNED.** This amendment adds one success criterion, `SC-16`. It
changes no existing requirement, no existing success criterion and no existing verification gap;
every word of `REQ-01`..`REQ-13` and `SC-01`..`SC-15` above stands exactly as signed. The
`## Approval` block below records the signature of Amendment 2 and is therefore **stale from the
moment this amendment lands** — it needs one re-signature covering `SC-16`, and nothing else.

**The gap, measured rather than reasoned.** `REQ-07` and `REQ-11` both bind the sweep to "a feature
**it** carries" — carried by the default branch the merge landed on. No criterion grades **which
copy** of that feature's directory the sweep acted on. `SC-06` grades the two merge shapes, `SC-07`
grades the self-exclusion guard, `SC-11` grades that each terminal feature is recorded, and all
three pass against an implementation that resolves the feature directory under whichever checkout
the sweep script itself happens to sit in. Measured during the build: the sweep closed milestone
**811** — a linked worktree's own never-landed copy — while the landed milestone **810** went
untouched, and `os.path.isdir(feat_dir)` was **true** throughout, so no skip branch was ever
reached. `gh-sync.py ship` then wrote `status: Done` into that copy and the sweep removed the
worktree, destroying the only carrier of the record. It is reachable in normal operation and not
only in a fixture: `harness-init/SKILL.md:73` writes a **relative** `core.hooksPath`, so every
worktree resolves to its own hooks directory and its own copy of this script.

**No new requirement.** `REQ-11` already commits the outcome, and `DEC-95` already fixes `.harness/`
as per-worktree state — which is what makes a linked worktree's copy legitimately divergent, and
therefore the wrong thing to write into. Adding a requirement here would restate `REQ-11` in
narrower words and give the goal-check two homes for one commitment.

**It costs no new work.** The behaviour graded is already specified by the approved plan's `T-03`
and already exercised by `test-post-merge-sweep.py` case (i), `case_linked_worktree_main_checkout`,
registered in both integration enumerations. This makes evidence that exists anyway into graded
evidence.

### Added success criterion

- SC-16: **The sweep's own on-disk location never decides which copy of a feature it acts on.** In a
  fixture where the sweep script runs from inside a **linked worktree** that carries its own
  divergent, never-landed copy of the same feature id as the main checkout, six clauses, each
  asserted separately and never by one substring match: **(a)** the sweep exits 0; **(b)** the root
  derived from the script's own location resolves to that linked worktree, which is what proves the
  fixture is the per-worktree-hooks scenario and not an accidental main-checkout run; **(c)** the
  root the feature directory is resolved under is the **main checkout**, asserted as an exact path
  both equal to the main checkout and unequal to the linked worktree, read from a resolved-path line
  the sweep prints unconditionally — **never from a skip**, because the wrong copy exists on disk
  and no skip branch is ever reached; **(d)** the landed copy's milestone is closed; **(e)** the
  divergent copy's own milestone is never touched, asserted on the absence of any call naming it;
  **(f)** the terminal worktree under the main checkout is removed, proving the correct copy was
  found rather than merely not written to. **Red proof:** an implementation that resolves the
  feature directory from the same root it locates its sibling scripts under passes (a), (b) and (f),
  closes the divergent milestone, and fails (c), (d) and (e) — and that failing state must be
  demonstrated, not asserted.
  verify: automated        evidence: integration
