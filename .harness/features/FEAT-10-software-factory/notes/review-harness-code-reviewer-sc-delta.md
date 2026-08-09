# Receipt — FEAT-10 seg8 Q8 success-criteria delta (spec-compliance lens)

**BLUF: PASS.** The outcome-first rework is real, not relabelling. Two `med` findings on trace
semantics (REQ-07←SC-20, SC-01's edge-idempotence wording) — both already partially disclosed in
BRIEF.md, neither rises to `high`. Nothing `must_fix`.

**Path note:** the dispatch named `notes/receipt-harness-code-reviewer-sc-delta.md`; this role's
`check-domain.sh` write-guard permits only `notes/review-harness-code-reviewer-*.md`, so this
artifact is written there instead. Flagged as a non-blocking `open_question` below — if a downstream
consumer greps for the dispatched filename it finds nothing.

## Q1 — SC-19 outcome vs relabelled negative

**Achieved, not relabelled.** SC-19 (`BRIEF.md:165-171`) chains each step's issue number from the
*previous step's parsed payload* rather than a constant (`plan.yaml:1420-1421`, T-12 intent), so it
catches a real class of bug a mocked/in-process test cannot: an unwrapped `if __name__` entry point,
an interleaved stdout line, a broken payload contract between tools. That is genuine composition
proof, not merely "stubs called in order."

Boundary named precisely: SC-19 proves the four tools **compose** (exit codes, payload chaining,
stdout purity) against scripted `gh`/`git`; SC-07 alone proves GitHub's own behaviour (real
concurrent-claim exclusivity, real API responses). `BRIEF.md:169-171` states this inline ("The
live-board equivalent stays SC-07's...") and `BRIEF.md:275-279` (Verification gaps) restates it
plainly: "it proves the four tools compose into one working sequence, and it proves nothing about
GitHub's own behaviour." Honestly disclosed on both citations. No finding.

## Q2 — Trace semantics on the two single-SC REQs

**REQ-06 ← SC-18 alone (`BRIEF.md:159-164`): narrower proof, but the narrowing is self-disclosed.**
SC-18 proves one loader function round-trips board/station/repo values and that `workspace_root`
derivation is shared — real evidence the fleet file is the *mechanism*. It does **not** prove no
other code path infers a repo/board from elsewhere; SC-18's own last sentence hands that off
explicitly: "That every tool refuses to infer its board or repository from anywhere else is SC-08's"
(`BRIEF.md:163-164`). SC-08 (negative group, `BRIEF.md:214-216`) also traces REQ-06. The "positively"
matrix line (`BRIEF.md:254`, "REQ-06 by SC-18") names only the positive half by design — the
document's own grouping convention (positive group / refuses-correctly group) — not a claim SC-18
covers REQ-06 unaided. Low, not ranked as a separate finding: the split is coherent and disclosed
inside SC-18's own text.

**REQ-07 ← SC-20 alone (`BRIEF.md:173-176`): narrower proof, scattered disclosure. `med`.** SC-20
hashes the feature directory before/after **one publish run** — i.e. only exercises
`factory_decompose`. Verified structurally: `plan.yaml`'s T-05/T-06/T-07 intents never load
`plan.yaml` or `BRIEF.md` — grep across the whole file shows those two paths appear only inside
T-04's block (`plan.yaml:573,660-672,747-749` vs. no hits in T-05/T-06/T-07's ranges). So the tools
that *do* read GitHub state back (claim, station-set) structurally never open the files REQ-07
protects — the "different tool" risk the question poses is real in principle but closed by
architecture, not by SC-20's test. The gap: BRIEF.md never states this structural fact in one place
next to SC-20 or the "REQ-07 by SC-20" line; the closest disclosure is SC-03 (`BRIEF.md:204-206`,
inspection, general "no factory tool writes to a feature's plan, brief, or approval block") sitting
in the *other* (negative) SC group. A reader who reads only the positive-coverage line
(`BRIEF.md:254`) without connecting it to SC-03 could reasonably believe SC-20 alone proves the
general claim across all five tools; it proves it for one. Disclosed, but split across two sections
rather than stated once — hence `med`, not `high`.

## Q3 — Protected negatives

**Intact, no weakening — verified against a prior byte-level checkpoint, not inferred from current
text alone.** `.harness/features/FEAT-10-software-factory/` is entirely untracked in git (`git
status --short` shows `?? .harness/features/FEAT-10-software-factory/`), so there is no committed
"before" revision to `git diff`/`git log -p` against — the rework never went through a commit
boundary. The discriminating check that exists instead: a prior pipeline stage already did the
byte-level comparison this question asks for. `runs/revise2-product/digest.md:66-67` — written
*during* the Q8 rework, before this review — states: "**Protected clauses survive byte-identical**,
checked line by line: SC-13 clauses (a) and (b) (`BRIEF.md:227-234`) and SC-14 (`:236-237`) are
unchanged apart from gaining a `traces:` line." Those line numbers match the current file almost
exactly (I read SC-13 at `BRIEF.md:227-235`, SC-14 at `:236-238`) — this is the same text, not a
coincidence. Separately, `runs/final-product/digest.md:52` shows clause (b) is not new to this
rework at all — it was added in an earlier revision cycle ("(b) NEW: every candidate unclaimable →
exit 1 naming which exit-1 cause. A signable criterion moved") — so the Q8 rework's job on SC-13 was
only to add `traces:`, and an independent prior agent already confirmed it did only that.

Reading the current text against `plan.yaml:90` (D-13: "SC-13 clause (b) must land exactly as stated
below... protected wording... not to be re-balanced by any later criteria pass") and against the
revise2-product corroboration: SC-14 (`BRIEF.md:236-238`) still asserts over "the full recorded call
list rather than over one call"; SC-13 clause (b) (`BRIEF.md:232-234`) still reads exactly "stderr
reads `no claimable work` and never `no work available`" — the two strings remain textually distinct
and are independently asserted in T-05's exhaustion test case (`plan.yaml:1003-1016`, explicit
`redirect_stderr` assertion on the exact words). No finding.

## Q4 — SC-01's "and draws each edge exactly once"

**Over-claims as worded; disclosed, but not cross-referenced from SC-01 itself. `med`.** SC-01
(`BRIEF.md:177-179`) states an unqualified real-world guarantee ("draws each edge exactly once — the
second run mutates nothing"). What the automated unit test actually proves is narrower: the *ledger's
decision logic* is correct given an accurate ledger (T-04's "fourth disposition" case,
`plan.yaml:834-839`, simulates an interrupted-but-consistent ledger state, not a crash strictly
between a successful remote write and the ledger's `write feature.yaml immediately` that follows it
at `plan.yaml:721,732`). Per the ruling this run treats as closed, eng-lead has already found two
such unprotected windows. If the ledger and the remote diverge across one, SC-01 can be **false in
the world** (a re-run redraws an edge GitHub already has) while its unit test — which mocks the
`gh`-facing calls and never re-POSTs for real — still **passes**, because the test never exercises
"remote already has it, ledger doesn't know." `BRIEF.md:280-286` discloses the underlying fact
plainly ("SC-01's 'the second run mutates nothing' rests on that ledger and not on any API property"
and re-POST behaviour is explicitly unmeasured), so the boundary is stated — just not next to SC-01's
own line in the criteria block, which reads as unconditional on a first pass. Criterion wording could
be read as over-claiming without the Verification-gaps context; the gap itself is not new, matches
what eng-lead already ruled closed. No architectural comment offered, per scope.

## Q5 — SC-21 station-option guard

**Falsifies the described failure mode, and binds the one tool actually at risk.** SC-21
(`BRIEF.md:210-212`) includes the failure mode explicitly in its own text — "never zero items and
exit 0, which is indistinguishable from an empty queue forever" — so a build shipping that bug fails
SC-21 directly; it is not a bare "a guard exists somewhere" assertion. On placement: SC-21 doesn't
name `factory_claim` by tool, but checked against the other four tools' intents, `factory_claim`
(T-05) is the **only** one that performs a station-filtered board *query* (`plan.yaml:891-897`,
step 2, run before step 3's read) — `factory_decompose` only *writes* the `ready` option and
deliberately declines a third copy of the check (`plan.yaml:703-710`, matches the brief's framing);
`factory_land` sets station by known item id from `--issue`, never a station-filtered read
(`plan.yaml:1159`, T-07 step 5). So the generic wording is safe: there is exactly one surface with
this failure mode, and T-05's own test case matches SC-21's language almost verbatim ("BEFORE any
board read", `plan.yaml:992-993`). No finding.

## Q6 — First-pass on SC-16, SC-17, SC-18, SC-20

- **SC-16** (`BRIEF.md:147-153`): falsifiable (exact N-issue count, exact label set, exact 4-part
  body order), matched one-to-one by T-04 test cases (`plan.yaml:780-782` count/station,
  `plan.yaml:796-799` labels, `plan.yaml:804-805` body order). No over/under-claim found against
  REQ-01/REQ-02.
- **SC-17** (`BRIEF.md:154-158`): falsifiable, matched by T-04's eight DAG cases
  (`plan.yaml:806-839`) including the six-blocker case pinned to T-12's actual shape and the
  full-call-list assertion that the parent never appears in `project_item_add`. No over/under-claim.
- **SC-18**: see Q2 (low, not separately ranked).
- **SC-20**: see Q2 (med).

## Findings, ranked

1. `med` — REQ-07's positive coverage line (`BRIEF.md:254`) cites SC-20 alone; SC-20's automated
   test exercises only `factory_decompose`, and the fact that the other four tools structurally
   never open `plan.yaml`/`BRIEF.md` (so REQ-07 still holds) is nowhere stated next to SC-20 or the
   coverage line — the closest disclosure (SC-03, `BRIEF.md:204-206`) sits in a different section.
2. `med` — SC-01 (`BRIEF.md:177-179`) reads as an unconditional "exactly once / mutates nothing"
   guarantee; the actual guarantee is ledger-accuracy-conditional, given two ledger-write-timing
   windows eng-lead has already found and closed. Disclosed at `BRIEF.md:280-286`, not
   cross-referenced from SC-01's own line.
3. `low` — REQ-06's positive coverage line (`BRIEF.md:254`) cites SC-18 alone; SC-18 proves the
   loader/round-trip mechanics, and the "no other inference path" half is explicitly handed to SC-08
   inside SC-18's own text (`BRIEF.md:163-164`) — coherent, just worth naming.

## Verdict

```yaml
VERDICT: PASS
DIGEST:
  headline: "SC delta is a real outcome-first rework, not relabelling; two med findings on trace scope (REQ-07/SC-20, SC-01 wording), both disclosed elsewhere in BRIEF.md; nothing must_fix"
  severity_max: med
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Dispatch named notes/receipt-harness-code-reviewer-sc-delta.md but this role's team-config.yaml domain permits only notes/review-harness-code-reviewer-*.md; the receipt was written to the permitted path instead. If a downstream consumer greps for the dispatched filename it will find nothing.", blocking: false }
  files_touched: [".harness/features/FEAT-10-software-factory/notes/review-harness-code-reviewer-sc-delta.md"]
  expertise_update: []
artifact: .harness/features/FEAT-10-software-factory/notes/review-harness-code-reviewer-sc-delta.md
```
