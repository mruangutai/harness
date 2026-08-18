# Receipt — harness-documentor — FEAT-23 T-04 — DEC-195 one-fix ceiling (half two)

**PASS.** DEC-195 now records both bounds on the simplify apply, not one, and names
`.claude/skills/harness-simplify/SKILL.md`'s `## Applying what comes back` as their authoritative
home. The index was regenerated, never hand-edited. T-04's verify is green.

## What changed

`.harness/harness/docs/DECISIONS.md`, DEC-195 entry only. One hunk: `@@ -6004,2 +6004,10 @@`.
The existing assertion-bound paragraph keeps its wording; only its trailing "The step's position is
unchanged by this bound." moved into the new paragraph so it is not said twice. Appended one
paragraph carrying:

- the one-fix ceiling — an apply that reddens the suites and is not restored by a single fix is
  reverted, and the finding becomes a backlog row;
- its reason — this is the only permanent build step with no `max_cycles` of its own, because
  `max_cycles` is an `on_fail` field of the **team** schema (`.harness/harness/docs/SPEC.md:2000`)
  and this pass is an orchestrator-sequenced squad segment, so no file grants it one; without the
  ceiling the repair loop is unbounded at the last step before `review_sha` pins;
- the explicit pointer naming the skill's `## Applying what comes back` section (that heading is at
  `.claude/skills/harness-simplify/SKILL.md:101`) as where both bounds are authoritatively stated,
  and as what governs on drift.

Substance mirrored from `SKILL.md:125-128`, written in the record's own voice — not pasted; sentence
structure differs.

`.harness/harness/docs/DECISIONS-INDEX.md` regenerated with
`python3 .claude/skills/harness/bin/gen-decisions-index.py`. Two generator-recomputed effects of the
edit, reported as effects and not as generator defects: DEC-196's anchor shifted `@6049` → `@6057`
(8 lines added above it), and DEC-195's tag set recomputed `[domain,plan,cost,dispatch]` →
`[domain,plan,cost,skills]` — the generator derives tags from section body text, and the new
paragraph's skill-path mention outweighed the prior `dispatch` signal. Both hand-written right-hand
summaries were preserved verbatim by the generator; neither was touched.

## Acceptance

T-04 verify, run verbatim from repo root. Exact final line:

```
T-04 GREEN
```

exit 0.

Phrase counts inside the DEC-195 entry, whitespace-normalised (`re.sub(r'\s+',' ',...)`) so wrapped
phrases cannot read as false zeros:

- before: `{'delete or weaken': 1, 'ceiling': 0, 'one fix': 0, 'max_cycles': 0, 'harness-simplify': 1}`
- after:  `{'delete or weaken': 1, 'ceiling': 3, 'one fix': 1, 'max_cycles': 2, 'harness-simplify': 2}`

`harness-simplify` 1 → 2: the second mention is the mandated section pointer, not drift. The
pre-existing citation at the "Why harness-native" paragraph is untouched.

`python3 .claude/skills/harness/bin/test-gen-decisions-index.py` also run (index length budgets are
asserted only there): all tests ok, including `test_committed_index_matches_a_fresh_regeneration`
and `test_committed_index_is_complete_and_within_budget`.

## Boundary

Intact. `## DEC-195` heads line 5970 and `## DEC-196` heads line 6057; the single diff hunk sits at
6004, inside DEC-195 and above DEC-196. No other decision entry was read into or written. DEC-196's
body is byte-identical — its only change anywhere is its `@line` anchor in the regenerated index.
Arch finding G was not applied; DEC-196's accepted costs were not re-litigated.

No commit, no `git add`, no `gh`. `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md` untouched.
No enforcement-layer file touched (DEC-174).

## `git status --porcelain` at exit

```
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-product-lead.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-premerge.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-qa.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-validator-lead.md
?? .harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-documentor-2026-08-17-12-dec195-product.md
```

(Captured before this paste was appended to the receipt; the receipt itself is the last `??` row.)
Mine are exactly `DECISIONS.md`, `DECISIONS-INDEX.md` and this receipt.

`.harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-product-lead.md` was already
modified in the tree at spawn (present in `git status` before my first edit) and is **not** mine.
Every other listed path is a pre-existing untracked artifact from earlier features.
