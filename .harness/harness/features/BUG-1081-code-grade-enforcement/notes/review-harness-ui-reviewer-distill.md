# Distillation — harness-ui-reviewer — BUG-1081-code-grade-enforcement

## Source material read

- `notes/review-harness-ui-reviewer-c1.md` — Mode B decline, measured census (28-file diff,
  zero rendered-UI extensions, no `DESIGN.md` at pin), plus advisory look at CLI text per
  dispatch item 4 (surfaced the `_classify_canonical_range` catch-all-missing-remediation gap).
- `notes/review-harness-ui-reviewer-c2.md` — cycle-2 decline on the 7-file delta, same two
  measured checks, carry-forward confirmation the advisory note's target string was untouched.
- `runs/2026-09-01-02-validator/digest.md` (cycle 1) — panel FAIL on a security `must_fix`
  (F1); explicitly credits the ui-reviewer's decline as "valid... a decline that looked, not
  one that predicted" and elevates the CLI-text finding as F2, calling it "a second instance of
  the union effect" — "the reader that scoped itself out produced a finding no in-scope reader
  had".
- `runs/2026-09-01-c2-validator/digest.md` (cycle 2) — panel ESCALATE on unrelated
  `team-config.yaml` drift; ui-reviewer PASS unchanged, no new UI-relevant content.

## Per-section counts

| File | Section | Before | After |
|---|---|---|---|
| `.harness/expertise/harness-ui-reviewer.md` (craft) | Patterns | 15 | 15 |
| | Gotchas | 15 | 15 |
| | Outcomes | 5 | **6** |
| | Open | 0 | 0 |
| `.harness/harness/expertise/harness-ui-reviewer.md` (repository) | Patterns | 1 | 1 |
| | Gotchas | 0 | 0 |
| | Outcomes | 0 | 0 |
| | Open | 0 | 0 |

Craft file: 40 → 41 lines (well under the 150-line budget). Repository file: unchanged at 10
lines (well under the 40-line budget).

## Accepted

- **O-06** (craft, Outcomes, `add`): "WHEN a dispatch names an adjacent non-rendered surface
  for you to check despite a no-UI decline DO produce advisory findings from it — panel review
  has credited a scoped-out reader's finding there as covering a gap no in-scope reader
  supplied (the union effect)." Evidence: `runs/2026-09-01-02-validator/digest.md` F2 and its
  "assessed and dismissed" note on the ui-reviewer's scope-out. Applied via
  `expertise-merge.py apply` against the craft file — tool reported `ADDED O-06`, all 20 prior
  entries `PRESERVED`.

## Rejected (relayed candidates)

1. **"Declined both cycles on a measured census, credited as evidence not absence."** —
   Rejected as a no-op: this is already fully stated by existing craft **O-01** ("a scoped-out
   review that looked holds up under cross-review scrutiny; one that merely predicted absence
   does not"). The c1/c2 panel language ("a decline that looked, not one that predicted") is a
   restatement of O-01, not a new fact about how to work. Adding a second entry saying the same
   thing would be an instance list, which distillation exists to compress, not grow.

2. **(Displacement question re: existing craft P-06)** — Judged that candidate 2 (accepted
   above as O-06) is *not* redundant with P-06 despite surface similarity. P-06 is prescriptive
   about scope ("an adjacent surface named in dispatch is in-remit, audit it") — it already
   governed the act of looking at the CLI text at all. What P-06 does *not* say, and what the
   panel digest newly confirms, is the outcome: that panel review specifically credits the
   finding produced from a formally-declined lens as covering ground no in-scope reader
   supplied. That is an Outcomes-shaped fact (verified-by-review), not a Patterns-shaped
   instruction, so it was added as O-06 rather than folded into or displacing P-06. No
   displacement was needed — Outcomes had room (5/10) — so this did not force a choice against
   any existing entry.

3. **"Repo-tier P-01 already predicts zero rendered UI by default — do two more confirming
   censuses change anything?"** — Rejected, explicitly. Repository-tier P-01 already reads "…
   confirmed via extension census on multiple diffs (0 html/css/scss/tsx/jsx/vue/svelte/less
   hits)" — it is already phrased as a standing, repeatedly-confirmed default, not a one-shot
   observation. The c1 (28-file) and c2 (7-file) censuses are two more zero-match runs against
   that same standing claim; they change no wording and support no new action. No-op, per the
   candidate's own honest framing.

## expertise_update (ops actually applied)

- `add` / `Outcomes` / `O-06` → `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-ui-reviewer.md`

No ops applied to the repository-tier file (`.harness/harness/expertise/harness-ui-reviewer.md`)
— both candidates that could have targeted it were rejected as no-ops (see above).

## Verification

`check-expertise.sh` run in single-file mode against both touched-or-considered files: both
report `OK`, exit 0.

```yaml
VERDICT: PASS
DIGEST:
  headline: One craft Outcome entry (O-06) added on the union-effect finding; two of three relayed candidates rejected as redundant no-ops against existing O-01 and repo-tier P-01.
  expertise_update:
    - op: add
      section: Outcomes
      target: O-06
      file: "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-ui-reviewer.md"
  open_questions: []
  files_touched:
    - "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-ui-reviewer.md"
    - "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-ui-reviewer-distill.md"
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-ui-reviewer-distill.md
```
