# Code review — FEAT-45-adversarial-plan-panel — feature-close Expertise distillation

Not a code review. FEAT-45 merged as PR #1069 at `d7f31bb`; this is the mandatory
feature-close distillation dispatch (DEC-145). No diff was reviewed this cycle — the
worktree was removed and there is nothing new to review. This note exists only to
satisfy the digest gate's artifact-under-`notes/` requirement (`code_grade_bound_to_review`
runs unconditionally for `harness-code-reviewer`, as I found live in cycle 3 — see
`review-harness-code-reviewer-c3.md`, "On my own yield"). The Target for this dispatch
otherwise restricted me to my two Expertise files only.

## What happened

Read my own five review notes across cycles c0–c4 (my only material this run — no
observation log exists for this persona) plus the cross-cutting `handoff-validate.md`
and `ship-review-2026-08-31.md`, and distilled the durable lessons.

- **Repository tier** (`.harness/harness/expertise/harness-code-reviewer.md`): ADDED
  `G-05` (Gotchas 4→5) — the worktree/main-checkout artifact-path split that rejected
  my own write in c0 and misdirected my own write in c1.
- **Craft tier** (`.harness/expertise/harness-code-reviewer.md`): UNCHANGED. Four
  strong candidates (the sibling-defaults-diverge fail-open that justified the whole
  feature; the verify-clause-blind-to-its-own-mandate gap; the additive-only-guard
  live-data-absence technique that found F1 twice; the all-skipped-roll-up vacuous
  truth that found SEC-01 Risk 2) were judged ACCEPT-IN-PRINCIPLE but could not be
  written: Patterns and Gotchas are both at their DEC-145 cap (15/15), and
  `expertise-merge.py apply` is verified (live, exit 8) to have no drop/replace
  primitive — only strict addition with a hard cap refusal. Three further self-derived
  candidates were REJECTED on their merits.

Full per-candidate reasoning, before/after section counts, and the verbatim ops
attempted are in this run's structured DIGEST, not restated here.

**Note on this digest's `reviewed`/`code_grade` fields**: no code was reviewed or graded
this cycle (distillation only). `reviewed` is set to the feature's already-closed range
ending at its recorded `review_sha` because the digest gate requires the head to match
`feature.json`, and `code_grade: n_a` because nothing was graded this run — the prior,
already-recorded grade for that range was `pass` (cycle 4, PASS, no must_fix). The gate
also separately reported that this checkout's branch (`main`, post-merge, per this
dispatch's explicit instruction) does not match the feature's recorded branch
(`feat/FEAT-45-adversarial-plan-panel`) — expected and correct for a merged feature;
not a defect in this note.

```yaml
VERDICT: PASS
DIGEST:
  headline: "1 repository-tier Gotcha added; 4 strong craft candidates ACCEPT-IN-PRINCIPLE but mechanically blocked by full sections and an add-only merge tool (verified live); 3 more self-derived candidates REJECTED on merits."
  severity_max: none
  findings: 0
  must_fix: []
  code_grade: n_a
  reviewed: "302ae9d..bdd566679377eb5a55d1092064fe444e86d2f49f"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "expertise-merge.py apply is add-only: same-id-different-text is a hard CONFLICT (exit 7), and any net growth past a full section is CAP EXCEEDED (exit 8) with the whole apply refused. harness-distill's ops schema (add|replace|merge|drop) and this dispatch's 'displace a weaker entry' instruction both presume a removal path the shipped CLI does not have. A distilling agent at a full section can only add-and-die or attempt a prohibited whole-file write. Recommend a --drop/--replace mode for a dedicated curation pass, or correcting harness-distill's promise.", blocking: false }
  files_touched: [".harness/harness/expertise/harness-code-reviewer.md", ".harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-distill.md"]
  expertise_update:
    - op: add
      target: G-05
      section: Gotchas
      tier: repository
      entry: "WHEN writing a feature artifact from inside this repo's FEAT worktree DO use an absolute path — feature.json/plan.yaml/STATE.md live only in the worktree copy while notes/ and runs/ also sync to the main checkout, so a relative write can land in the main checkout and later fail code_grade binding."
      result: "APPLIED — ADDED G-05, PRESERVED G-01..G-04, exit 0. Repository Gotchas 4/15 -> 5/15."
artifact: ".harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-distill.md"
```
