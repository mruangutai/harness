# receipt — harness-dev-ops — distillation, feature close — FEAT-29-graphql-budget

Source read in full before judging: own receipt
`notes/receipt-harness-dev-ops-simplify-eng.md` (primary), and
`runs/2026-08-19-10-eng/digest.md` for context on the four relayed candidates.
No observations log existed for this agent on this feature (none logged).

## Accepted — craft (`.harness/expertise/harness-dev-ops.md`)

All four accepted here trace to the lead's relay (digest Q2 and the receipt lines the lead
quoted); none is self-derived beyond what the relay already named.

- **G-14** (from relayed candidate 1, craft half): assert an env-var-redirected root actually
  resolved before the first write, then delete and confirm. Source: digest.md:26 (Q2) +
  receipt:27-28, 60-64.
- **G-15** (from relayed candidate 4): treat an artifact already at your own output path as
  informative only, re-derive rather than trust. Source: receipt:3-5; side effect at digest.md:29.
- **P-15** (from relayed candidate 2): refuse to estimate a cost component measurable only via a
  forbidden action; scope the reported figure to what was actually measured. Source: receipt:33-34.
- **P-16** (from relayed candidate 3, part A only): skip re-running a suite kind the review's own
  diff did not touch, naming the specific reason. Source: receipt:44-48.

## Rejected

- **Candidate 3, part B** (reading deliberate boundary-step full-suite runs as "evidence the
  boundary exists" and declining to flag them, receipt:49-52): rejected as its own entry. It is a
  restatement of ordinary scope discipline already covered by P-16 and by the existing gates'
  own design — it does not add a discriminator six spawns from now in a repository that may not
  even have boundary-step full-suite runs as a concept. Kept out to avoid a story-shaped entry.

## Repository tier (`.harness/harness/expertise/harness-dev-ops.md`)

- **G-05** (from relayed candidate 1, repository half): `factory_config.harness_root()` falls
  back to the real checkout when `CLAUDE_PROJECT_DIR` points at a tempdir lacking `SPEC.md`.
  Source: digest.md:26 (Q2). Judged durable — a fact about this checkout's config resolution, not
  about my working style.

## Harness defect — routed to open_questions, not Expertise

Nothing enforces the harness_root()-before-write assertion outside `test-gh-cost-log.py`'s
`redirect()` helper for ad-hoc benchmarking generally (digest.md:26, Q2). This is a gap in
tooling, not a craft lesson — a workaround written into Expertise would outlive the fix. The craft
half (G-14: assert before you write) stands regardless of whether this gap ever closes.

## Section counts

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 13 | 15 |
| craft | Gotchas | 11 | 13 |
| craft | Outcomes | 0 | 0 |
| craft | Open | 0 | 0 |
| repository | Patterns | 1 | 1 |
| repository | Gotchas | 4 | 5 |
| repository | Outcomes | 0 | 0 |
| repository | Open | 0 | 0 |

## Verification

`check-expertise.sh` on both files:
```
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:22: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
---
OK   .harness/harness/expertise/harness-dev-ops.md
```
The advisory is on pre-existing G-03 (unchanged this run), not on any entry written today.
