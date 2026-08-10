# Review — FEAT-10 prose-delta (plain-English rewrite + enforcement fixes), pre-signature

**Step 0 result: feature dir is UNTRACKED.** `git ls-files --error-unmatch BRIEF.md` fails (no match);
`git status --porcelain .harness/features/FEAT-10-software-factory/` shows the whole directory as
`??`. No `git diff`/`git show` baseline exists. Fell back to the two prescribed alternatives: (1) the
operator's own approved worked example for SC-12 (`notes/answers-esc1-a1.md:87-89`), and (2) the
independent, unrewritten `plan.yaml` cases/`verify:` blocks as the falsification-set cross-check for
SC-01, SC-13, SC-18, SC-19 and SC-22, using pre-rewrite fragments quoted in the two baseline reviews
(`review-harness-code-reviewer-enforce-delta.md`, `review-harness-code-reviewer-sc-delta.md`) as the
only available pre-rewrite text.

**BLUF: PASS.** Both prior FAILs (Q3's D-13 residual-signal gap, Q1's SC-22 mis-quantification hole)
are closed and verified at source, not relayed. Three `med`/`low` advisory findings, none gating:
SC-01 gained a semantic precondition during the rewrite that, on inspection, matches exactly what
`plan.yaml`'s T-04 case set proves (previously over-claimed, now honest) but was not a named/ruled
remedy and is technically outside the FOURTH ruling's "prose only" scope; SC-18 lost an inline
boundary statement with no replacement anywhere in the document; and `plan.yaml`'s T-05 intent reuses
the label "edge (i)" for a scenario DESIGN.md/D-01 already define under that name for something else.

## Q1 — Did the plain-English rewrite change any meaning?

- **SC-12** (`BRIEF.md:199-203`) vs. the operator's approved text (`answers-esc1-a1.md:87-89`):
  compared literally. Substantive content identical; two word-level substitutions, both acceptable —
  "emits a payload" for "reports success" (more precise, matches SC-11/T-05 step 7's own vocabulary)
  and "station move" for "card move" (the actual field name used throughout the document — SC-16
  "station set", T-05 step 6 "the item's station field" — so this is a correction toward consistency,
  not a drift). The added lead-in "takes ownership with a create-if-absent marker" is exposition, not
  a changed assertion. The SC-07 cross-reference the FOURTH ruling named as the shape being removed
  is confirmed gone from SC-12's body. No finding.
- **SC-13** (`BRIEF.md:238-250`): clause (b) is **byte-identical** to the pre-edit baseline quoted in
  `runs/amend2-product/digest.md:54-58` ("A ready column in which *every* candidate is unclaimable
  exits 1 having mutated nothing... stderr reads `no claimable work` and never `no work available`") —
  cross-checked character-for-character against the current file, independent of that digest's own
  claim. Clause (a) gained the fixture's fifth reason (blocked by an unfinished blocker) and, load-
  bearing, a new sentence naming the D-13 residual explicitly and requiring it a distinct reason. This
  is B1 edit 3 landing as instructed — a named, ruled remedy, not incidental drift. See Q3.
- **SC-22** (`BRIEF.md:159-172`): all three original directions (SKIP AND CONTINUE, EVERY CANDIDATE
  BLOCKED, ALL BLOCKERS CLOSED) plus the new MIXED-blocker sentence map one-to-one onto `plan.yaml`'s
  seven named cases (`:1219-1263`). No direction lost, none broadened past what the fixture proves.
  This is B2, a named remedy.
- No criterion in the block still folds a scope caveat or a cross-reference to another `SC-NN` into its
  own assertion (checked the full `:132-283` range) — matches the FOURTH ruling's rule literally.
- REQ-01..REQ-08 (`:24-40`) read internally consistent with D-05/REQ-03 "stand unchanged," D-01's
  widened bound, and the SC coverage matrix (`:274-281`); no baseline text exists anywhere in this
  tree to diff them against word-for-word (checked — no prior review or digest quotes REQ prose), so
  this is a coherence read, not a byte-diff, and is disclosed as such.

### SC-01 — a precondition appeared that was not a named remedy. `med`, advisory, does not gate.

`BRIEF.md:189-192` now reads: "...draws each edge exactly once. **Given a `feature.yaml` ledger that
accurately records the first run**, the second run mutates nothing." The pre-rewrite baseline, quoted
in `notes/review-harness-code-reviewer-sc-delta.md:82-97`, had no such clause — that review's own
`med` finding was precisely that the old wording read as an *unconditional* guarantee while the proven
behaviour was conditional on ledger accuracy. This is not on the list of named/ruled edits (B1, B2, B3,
Q12, Q13) — it appears to be a self-initiated correction folded into the "plain English" pass, which
the FOURTH ruling explicitly scopes to prose only ("a criterion that changes what it asserts has been
re-authored, not rewritten, and that is out of scope here"). On its face this is exactly the shape Q1
was dispatched to hunt for.

**Ruled non-gating because the new text now matches its fixture exactly, rather than diverging from
it.** Checked `plan.yaml`'s T-04 case set directly: the only case that tests "second run mutates
nothing" (`plan.yaml:845-850`) does so against a `feature.yaml` that "by then records the parent, both
issue numbers, both item ids AND every edge" — i.e. an accurate ledger, and the recorder shows "zero
calls of any kind." No T-04 case tests the pure unconditional claim under an *inaccurate* ledger — the
adjacent case that comes closest (`:907-918`, the narrowed 422 exception) is a *different* guarantee:
it asserts the run **continues to draw every later edge** and records the recovered receipt, which is
resume-and-finish behaviour, not "mutates nothing." `plan.yaml:95` (the D-14 decision `because` text)
states outright that "SC-01's second run mutates nothing is false without [the narrow exception]" and
that the attach/hierarchy half of the same crash window "REMAINS OPEN by construction" — i.e. the
decision record itself already treats the unconditional reading as false in a known residual case.
**The rewritten SC-01 text is the first place in this document that states that conditionality inside
the criterion's own line rather than only in a disclosure two pages away** — it resolves sc-delta's
`med` finding rather than reopening it. Flagged as advisory because the correction is substantively
right and improves the document, but it was not an instructed edit, and a reader of just the FOURTH
ruling would not expect a semantic clause to have moved during this specific pass.

## Q2 — SC-22 mixed-blocker case: does it kill a mis-quantifying tool? PASS

`plan.yaml:1234-1241` (MIXED BLOCKER SET): "Give the blocked lowest-numbered candidate a `depends_on`
with THREE entries... **the first CLOSED, the middle CLOSED, the last OPEN**." Ordering is pinned
explicitly by position, not left to a builder's discretion — the open blocker sits at index 2, never
index 0. A `depends_on[0]`-only tool reads position 0 as CLOSED, treats the candidate as clear, tries
`create_ref` on it, and fails the case's assertion (`create_ref` called on the clear higher-numbered
candidate only). The mirror error (blocked only when *every* blocker is open) also dies here
regardless of order, as the dispatch predicted. **Ordering is load-bearing and is pinned.**

**Buildability, confirmed at the spec level, not inferred from a lead's reasoning:** `plan.yaml:1211-
1218` instructs the fixture directly — "one candidate may carry SEVERAL blockers resolving to several
distinct issue numbers; the scripted recorder answers `issue_view` PER ISSUE NUMBER, so each blocker's
open or closed state is set independently." This is an instruction to the builder inside T-05's own
task text, not merely a lead's after-the-fact assurance that it's buildable.

## Q3 — Does D-13's residual signal survive? PASS — the prior FAIL is closed

Two things decide it, both confirmed:

- **(a) Does the 5b stderr reason fire on every poll?** `DESIGN.md:73-77` (B1 edit 1) contracts it
  explicitly: "that skip reports on stderr on **every poll**, with a reason distinct from every other
  skip reason in the loop, naming the issue and the fact that `refs/heads/factory/issue-<n>` already
  exists. Poll mode only." `plan.yaml:1106-1121` (T-05 step 5b, B1 edit 2) matches verbatim in
  instruction — two explicit, independent "every poll" contracts, not an inference from statelessness.
- **(b) Does SC-13 assert it, not just T-05 instruct it?** Yes — `BRIEF.md:247-249` names the
  claim-marker-already-taken skip explicitly and requires its reason be distinct from every other
  clause-(a) reason. `plan.yaml:1184-1191` (the EXHAUSTION test's Route One) makes this concrete:
  captured stderr must name each candidate's issue number and that its claim ref already exists, "in a
  form distinct from the already-marked and already-assigned skip reasons," and the test asserts Route
  One's and Route Two's stderr sets are **not equal**.

A healthy all-blocked poll (stderr full of `blocked by T-NN` lines) is now distinguishable from a
silting queue (stderr carries the distinct "ref already exists" line) — both by contract (DESIGN.md
C-2) and by an asserted, falsifiable test case (`plan.yaml:1184-1191`), not merely by task-text
instruction. **The `high` FAIL from `notes/review-harness-code-reviewer-enforce-delta.md` Q3 is
closed.**

## Q4 — An instructed refusal nobody asserts (Q12) — advisory, plus one new finding

Confirmed: no case in T-05's test list (`plan.yaml:1150-1264`) exercises "candidate whose `feature:`
label resolves but whose T-NN matches no plan task." Per the dispatch's own discriminator, there is no
concrete in-tree candidate that hits this path — `factory_claim.py` does not exist yet (T-05
`status: pending`). **Stays advisory, does not gate.** pm was right not to add a case unilaterally
against a one-sentence dispatch.

**New finding, not previously raised — `med`, advisory, does not gate.** `plan.yaml:1069-1072` labels
this scenario "**edge (i)**": "A candidate whose `feature:` label DOES resolve but whose title yields
no matching plan task is edge (i) — it counts as BLOCKED... report it on stderr with edge (i)'s
reason." But `DESIGN.md:121-124` and `D-01`'s decision text (`plan.yaml:43`) both define **edge (i)**
as a *different* scenario — a `depends_on` entry the issue map cannot resolve (a dangling blocker
reference). `plan.yaml:1251-1253`'s own UNRESOLVABLE BLOCKER test case correctly cites this true
edge (i). Neither `DESIGN.md` nor `D-01` was updated to define the Q12 scenario as any numbered edge
at all — it exists only inside T-05's task prose, under a label that already means something else one
document over.

**Failure scenario:** if a builder follows the label literally and emits the same stderr string
("edge (i)" or its associated reason text) for both the dangling-`depends_on` case and the resolvable-
feature-no-task-match case, that violates SC-13's own requirement — "no two of those reasons read
alike" — because "a blocker reference doesn't resolve" and "this candidate's own task identity is
lost" are different facts about the board, exactly the kind of collision SC-13 exists to prevent for
every other skip pair.

**Smallest closing edit** (does not require re-litigating Q12's substance): rename the Q12 scenario in
`plan.yaml:1070-1072` away from "edge (i)" — e.g. "edge (iii)" — so it cannot collide with the existing
label, and add one line to `DESIGN.md`'s C-2 amendment section and/or `D-01`'s `choice`/`because` text
naming it as a third edge with its own distinct stderr reason. A test case is optional given Q4 stays
advisory, but the label collision itself is cheap to fix now and expensive to catch once code exists.

## Q5 — Anything orphaned by SC-07's removal? Resolved, no finding

- **(a)** The prior false framing flagged in `notes/review-harness-code-reviewer-enforce-delta.md`
  Q5 — the gap note claiming the live blocker hop "is carried by SC-07 as an operator step, like every
  other live-board claim here" — does **not** survive. `BRIEF.md:329-335` now reads: "An earlier
  version of this note claimed the deleted `verify: uat` criterion carried it as an operator step.
  That claim was false even before the deletion, because that criterion's text never contained a
  blocker clause." This is B3, explicitly closed, and it is a correction rather than a silent drop.
- **(b)** `BRIEF.md:260-265` gives SC-02 an explicit retirement note naming its id; `BRIEF.md:267-272`
  gives the former SC-07 a structurally parallel retirement note that deliberately omits the id, which
  is the correct resolution of the LATE ruling's zero-reference requirement — not two inconsistent
  conventions. Both retired ids get a note; one names itself, the other cannot by design. No finding.

## Spot-check on sibling pre-rewrite quotes (bounded, per the two baseline reviews' own citations)

- **SC-19** (`BRIEF.md:178-184`): the pre-rewrite cross-reference "The live-board equivalent stays
  SC-07's..." (quoted in `review-harness-code-reviewer-sc-delta.md:22-25`) is gone, as required. The
  boundary it stated survives as a **separate line** in `## Verification gaps`
  (`BRIEF.md:325-328`: "it proves the four tools compose into one working sequence, and it proves
  nothing about GitHub's own behaviour") — exactly the FOURTH ruling's prescribed shape. No finding.
- **SC-18** (`BRIEF.md:173-177`): the pre-rewrite hand-off sentence "That every tool refuses to infer
  its board or repository from anywhere else is SC-08's" (quoted in
  `review-harness-code-reviewer-sc-delta.md:33-34`) is gone and, unlike SC-19, **has no replacement
  anywhere in the document** — a full grep for "SC-08" and "infer" outside SC-08's own bullet turns up
  nothing. `low`, advisory, does not gate: `BRIEF.md:274-281`'s coverage line still reads "REQ-06 by
  SC-18" alone, and SC-08 sits in the negative group tracing the same REQ-06, so a reader who checks
  the SC list (rather than only the coverage sentence) still finds the boundary — but the explicit
  disclosure the pre-rewrite review credited for keeping this "coherent, not a separate finding" is
  now absent, and this is a case where removing a caveat took a stated boundary down to an inferable
  one rather than leaving it stated separately, as the FOURTH ruling's own carve-out prefers.
- **SC-21** (`BRIEF.md:217-219`): the "never zero items and exit 0, indistinguishable from an empty
  queue forever" clause (quoted in `review-harness-code-reviewer-sc-delta.md:102-104`) is intact
  verbatim in substance. No finding.

## Severity summary

| Item | Verdict | Severity | Gates |
|---|---|---|---|
| Q1 — SC-12, SC-13, SC-22 meaning preserved | PASS | n/a | no |
| Q1 — SC-01 gained an unruled precondition | matches its fixture; ruled correction | **med** | no |
| Q2 — SC-22 quantifier | PASS | n/a | no |
| Q3 — D-13 residual signal | PASS (prior `high` FAIL closed) | n/a | no |
| Q4 — Q12 instructed-not-asserted | advisory | none | no |
| Q4 — "edge (i)" label collision (new) | advisory | **med** | no |
| Q5 — SC-07 orphans | resolved | n/a | no |
| Sibling check — SC-18 lost boundary, no replacement | advisory | **low** | no |
| Sibling check — SC-19, SC-21 | PASS | n/a | no |

**Nothing gates.** `must_fix: []`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both prior FAILs closed and verified at source (SC-22 mixed-blocker case kills a depends_on[0]-only tool with ordering pinned; SC-13 now asserts the D-13 residual's distinct stderr reason with a test case behind it); the plain-English rewrite did not change SC-12/SC-13/SC-22/SC-19/SC-21's falsification sets; three non-gating advisories: SC-01 gained an unruled precondition that turns out to match its fixture exactly, SC-18 lost a boundary statement with no replacement anywhere, and plan.yaml's Q12 fix reuses the label 'edge (i)' for a scenario DESIGN.md/D-01 already define differently"
  severity_max: med
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "BRIEF.md:189-192 (SC-01) gained a semantic precondition ('Given a feature.yaml ledger that accurately records the first run...') during the plain-English pass. It was not on the named-remedy list (B1/B2/B3/Q12/Q13) and is technically outside the FOURTH ruling's prose-only scope, but plan.yaml:845-850's T-04 case tests exactly this conditional claim and no case tests the unconditional one, so the new text matches its fixture and resolves a pre-existing med finding (review-harness-code-reviewer-sc-delta.md) rather than reopening one. Non-blocking: confirm pm intended this as a deliberate fix, not an accidental scope drift, for the record.", blocking: false }
    - { id: Q2, question: "BRIEF.md:173-177 (SC-18) lost its inline hand-off to SC-08 ('...is SC-08's') during the rewrite per the FOURTH ruling's caveat-removal rule, but no separate line states that boundary anywhere in the document (unlike SC-19's equivalent, which survived at BRIEF.md:325-328). Non-blocking: add one line near SC-18 or in the coverage paragraph (:274-281) if the boundary is worth keeping explicit.", blocking: false }
    - { id: Q3, question: "plan.yaml:1070-1072 labels the Q12 BLOCKED scenario (feature: label resolves, T-NN matches no plan task) 'edge (i)', but DESIGN.md:121-124 and D-01 (plan.yaml:43) already define edge (i) as a different scenario (unresolvable depends_on entry). If a builder reuses the same stderr text for both, it violates SC-13's 'no two skip reasons read alike' requirement. Smallest fix: rename to a distinct edge label in plan.yaml and mirror it in DESIGN.md/D-01 with one line.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-10-software-factory/notes/review-harness-code-reviewer-prose-delta.md
```
