# Plan-panel review — scope reader — FEAT-52 cycle 4

**BLUF: one HIGH finding.** The checker's own rule, as specified in T-02, enforces the two-anchor
direction split in only one of its two directions — it can never flag a READ path (F1/F2 and most of
T-06/T-07/T-08/T-10/T-11's sweep) that was wrongly anchored with `<HARNESS_FEATURE_TREE_ROOT>/`
instead of `<HARNESS_CONTROL_PLANE_ROOT>/`. BRIEF's SC-04 explicitly demands a per-site, automated,
direction-correctness assertion for exactly this ("each of the five canonical sites S1-S5 ... shows
its path written with the correct anchor prefix for its direction ... verify: automated, evidence:
unit"), and no task in the plan implements it. This is not a re-hash of cycle-0's H1/H2/M1/M2/M3/L1/
L2/L3 — those are all genuinely fixed — it is new. Recommend: send back, not sign.

Traceability, dependency order and the two other hunted defect shapes (N-1 blind spots, gates that
can't go red) are otherwise clean; see sections 1-5 below. Files read in full per assignment:
`plan.yaml` (1006 lines), `BRIEF.md`, the c0 goal-check, the c2 consolidation crosswalk. Confirmed
`.agents/skills/...` and `.claude/skills/...` both resolve at repo root — `.agents/skills` is a
git-tracked symlink to `../.claude/skills`, present in both the main checkout and this worktree.

## 1. Traceability — clean, both directions

REQ-01..06 each traced by >=1 task (`plan.yaml` tasks dump): REQ-01 T-03,T-13 · REQ-02
T-04,05,06,07,08,10,11,13 · REQ-03 T-05,08,13 · REQ-04 T-02,03,12 · REQ-05 T-03,14 · REQ-06
T-01,02,04,06,07,08,09,10,11,13. Every task's `traces:` cites an id that exists — no dangling. SC-07
is the one explicit no-change criterion; I looked for a second silent instance and did not find one —
SC-01..SC-06 and SC-08..SC-14 each have a task cited in the crosswalk's "SC-01..SC-14 all carried"
table, but see §4 below: "carried" is not the same claim as "correctly discharged," and SC-04 is
where that gap actually lands.

## 2. Dependency shape — clean

`depends_on` is a strict DAG matching ascending task-id order, no forward reference, no cycle
(`plan.yaml` tasks dump, verified programmatically). Confirmed T-02's own constraint holds: no task
before T-12 invokes `check-instruction-paths.py` with zero positional args (whole-scope). T-04
(`plan.yaml:351`), T-05(`:431`), T-06(`:492`), T-07(`:547`), T-08(`:595`) all scope the checker to
their own file lists; only T-12 (`:831`) runs it bare. T-11 (`:784-786`) is the one anchoring task
whose verify never calls the checker at all — see §6, low.

## 3. Verify clauses as artifacts — the finding

**T-02's rule, `plan.yaml:166-181`, is directionally asymmetric.** THE RULE (166-174) flags any
matching span *not immediately preceded by* `<HARNESS_CONTROL_PLANE_ROOT>/` **or** by
`<HARNESS_FEATURE_TREE_ROOT>/` — either placeholder satisfies it, regardless of which direction the
site actually requires. THE SECOND VIOLATION CLASS (176-181) adds exactly one more rule: a span
beginning `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<segment>/features/` is a violation. That catches
only the write-misdirected case (a feature-directory WRITE wrongly anchored to the control plane —
SC-11's subject). **There is no rule, and no task-level test anywhere in the 14 tasks, that catches
the mirror mistake: a control-plane READ (F1 `harness.json`, F2 the Expertise path, and the bulk of
T-06/T-08/T-10/T-11's swept skills) wrongly anchored with `<HARNESS_FEATURE_TREE_ROOT>/`.** Concretely:
an implementer who writes `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json` in
`harness-qa-gate/SKILL.md` satisfies rule 1 (a placeholder precedes it) and rule 2 doesn't apply (no
`/features/` segment) — the checker exits 0.

This is exactly the BRIEF's own "wrong read (silent and dangerous — the qa gate applies the wrong
matrix)" severity class, and it defeats D-06's "not negotiable per family" framing for every READ site
the plan sweeps.

**SC-04 already names the missing test and nobody built it.** BRIEF.md SC-04: "each of the five
canonical sites S1-S5 ... separately shows its path written with the correct anchor prefix for its
direction — one assertion per site, read via `git show <review_sha>:<path>` ... verify: automated,
evidence: unit." I grepped `plan.yaml` for `git show`/`review_sha` and for any per-site
direction-correctness check: none exists. T-02's "SCOPE COMPLETENESS" test (`:212-222`) only asserts
`--list-scope` *contains* the five sites — that discharges SC-03, not SC-04's direction claim. The c2
crosswalk's "SC-04 T-12 (whole-scope run) with the per-site anchoring in T-04/06/07/08" overstates
what those tasks' verify blocks actually check.

**The gap is not uniform, and that is the tell.** `T-07`'s verify (`:547-548`) is the one place the
plan does it right: it checks `cp+x in r` for each read path and `ft+x in r` for each write path,
individually, i.e. prefix-plus-path together — this is a genuine per-site direction assertion, and it
proves the pattern was known and available. Every other anchoring task's Python positive control
(T-04 `:353`, T-06 `:493`, T-10 `:736`, T-11 `:786`) instead greps only for the bare string
`HARNESS_FEATURE_TREE_ROOT` (or `HARNESS-FEATURE-TREE-ROOT`) appearing *anywhere* in the file — which
is satisfied by prose mentioning the placeholder and says nothing about which path it sits in front
of, and says nothing at all about the `HARNESS_CONTROL_PLANE_ROOT` sites needing to be absent the
wrong prefix. (T-08's `:596` check is the documentation-content shape, not path-correctness, and is
fine on its own terms since the file's own path anchoring is separately covered by the checker call
in the same chain — flagged only for completeness, not as part of this finding.)

One site is provably safe despite the checker's gap: T-05's own test (`:462-467`) does a literal
substitution of the real repo root for `<HARNESS_CONTROL_PLANE_ROOT>` and asserts the file *opens* —
if the wrong placeholder had been used, the substitution would leave the literal angle-bracket text in
the path and the open would fail. That is the T-07-grade pattern; it just isn't applied anywhere else.

**Severity: high.** Concrete failure scenario: an implementer executing T-04 exactly as written
anchors `harness-qa-gate/SKILL.md`'s `harness.json` reference (F1, a READ) with
`<HARNESS_FEATURE_TREE_ROOT>/` instead of `<HARNESS_CONTROL_PLANE_ROOT>/`. T-04's verify passes
(checker: no rule violated; positive control: doesn't even name this file). T-12's later whole-scope
run passes for the same reason. The mistake ships, gated into CI as a required check (DEC-183) that
now certifies a wrong-direction path as clean. At runtime, on a Harness self-development run with its
own worktree, that READ resolves against the feature's worktree instead of the main checkout — for a
file that can legitimately diverge between branches (`harness.json`'s own `test_matrix`, for
instance) — reproducing the exact "qa gate applies the wrong matrix" scenario the BRIEF opens with.

## 4. The two flagged shapes

- **(a) N-1 blind spot from a single file-global command.** Not present as a fresh defect: SC-03's
  scope-completeness and the RED-PROOF/second-class cases in T-02 (`:198-224`) are each itemized,
  five and two separate assertions respectively, matching cycle-0's L2 fix. SC-13's four
  dispatch-guard cases and SC-08's two CI mutants are likewise itemized, not counted. The one
  N-quantifying shape that *is* weak is the positive-control greps discussed in §3 — but their defect
  is direction-blindness, not an N-1 counting gap; they do check every named file individually.
- **(b) Gate asserted green with nothing proving RED.** SC-05 (T-02 RED PROOF, both inline and fenced
  shapes), SC-08 (T-12's two independent mutants — deleted step, and step-present-but-failure-branch-
  removed), SC-12 (T-03's same-fixture-plus-one-line RED case), and T-14 (the `exit 2` positive
  control, correctly done via `grep -E` rather than Python `re` to dodge the `[[:space:]]`
  character-class trap) are all genuinely discriminating — each names a fixture that must fail and
  shows the assertion firing on it. No finding here; cycle 0's H2/M1/M3/L1 read as fixed.

## 5. Dead weight

None found. Every task traces to a live REQ and (per §1) is needed for coverage; if anything §3 shows
the plan is under- rather than over-provisioned — SC-04 needs a task, not fewer tasks.

## 6. Minor, not gating

T-11's verify (`plan.yaml:784-786`) never calls `check-instruction-paths.py` on its own four edited
files, unlike every sibling anchoring task (T-04/05/06/07/08/10). A regression introduced by T-11's
new paragraph would go undetected until T-12's whole-scope run, which does depend on T-11 and would
still catch it before ship — so this is a detection-latency gap, not a shippable-defect gap. Not
rated as a finding on its own; noted for the record per Expertise P-15.

## Already-ruled items — not re-raised

No disagreement with the `approval:` absence or the `UNRESOLVED-GLOB`/NOBODY glob acceptance for T-04
and T-11; both are correctly out of this panel's scope per the dispatch's pre-briefed context.
