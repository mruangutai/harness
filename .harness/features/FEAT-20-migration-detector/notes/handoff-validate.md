# Handoff — FEAT-20-migration-detector, validate → ship — written at 434307a, seq-2

## Next

**Dispatch nothing until the operator's ruling arrives.** Both gates passed and 14 of 15 criteria
are met; the last cannot be met as written and only the operator can settle it. The main session
writes `notes/answers-<runid>.md`; pass that **path** into the resumed run.

- **Branch A — the operator signs the shipped-surface reading (pm's recommendation).** The answers
  file IS the ruling record: cite it, treat SC-10 as closed, and go straight to close-out —
  ship-refresh and distillation as **two dispatches in ONE message** — then the briefing at
  `notes/ship-review-<runid>.md` plus `render-brief.py`. Do not edit `BRIEF.md`.
- **Branch B — the operator amends the wording.** That is a re-plan: pm, via product-lead, under the
  operator's approval. Re-verify SC-10 only; a wording change touches no code. Then close-out.

## Trust

- 14/15 SCs met, verified first-hand at this pin — pm re-ran both suites and read assertion bodies,
  not `ok` labels — `notes/uat-goalcheck-c0.md` — verified-at 434307a
- **SC-10 is unmet AS WRITTEN and unmeetable by any harness feature**: its closed set forbids the
  `.harness/` bookkeeping every feature necessarily writes. The shipped surface is still exactly the
  8 permitted files with zero renames — I re-derived this rather than inherit it:
  `git diff --name-only 88b1182..434307a` = 27 paths, 8 outside `.harness/`, `--diff-filter=R` empty
  — verified-at 434307a
- Blocking qa gate PASS, `matrix_ok: true`, union `{unit,integration}` green with registration greps
  fired — `runs/qa-gate-validator/digest.md` — verified-at ea476fd
- Panel PASS, `must_fix: []`, `severity_max: med` under `advisory_unless_high` — nothing gates —
  `runs/2026-08-14-1-validator/digest.md` — verified-at ea476fd
- The suite is **correct-today, not pinned against regression**. R-1: `check-state.sh:1302-1318`
  dispatches INV-27's wording across four `if/elif` branches on `_srep.cause` with **no trailing
  `else`**, only one cause rendered by any test — missing `else` confirmed by me at source. R-2:
  `_evidence()`'s count feeds only the printed `examined` line, never the verdict —
  `runs/2026-08-14-1-validator/digest.md` — verified-at ea476fd
- `review_sha` moved `ea476fd` → `434307a`, the tree the goal-check verified; qa measured the two
  identical across all 8 source files — `feature.json` — verified-at 434307a
- `cycles_used` 3/10 (plan 2, qa's in-run send-back 1); an ESCALATE is not rework. `len(runs)` 7/20,
  a floor — T-01/T-02 were main-session-direct — `feature.json` — verified-at 434307a

## Dead ends

- The unguarded CI step is settled: accepted at signature under DEC-183, and
  `test_matrix.config.always` is `[]`, so the row is satisfied, not unsatisfiable — `BRIEF.md`
  `## Approval` notes — verified-at 434307a
- The doc-root assertion absent from unit cases 1 and 15 is redundant, not a hole: `n == 0` implies
  CANNOT_VERIFY implies exit 2, reddening case 1 — `runs/qa-gate-validator/digest.md` V-1 —
  verified-at 434307a
- Do not edit `.github/workflows/tests.yml:110-114`; its false guard claim is pre-existing, byte-
  unchanged here, owned by issue #279 — `git diff 88b1182..434307a` — verified-at 434307a
- Never `git add -A`: two deleted `.harness/members/backend-dev/FEAT-02-*.md` and two untracked files
  under `.harness/logs/` and `.harness/notes/` predate this feature — `git status` — verified-at 434307a
- `verify:` clauses are not runnable verbatim — the write guard refuses redirects to a shell
  variable, so `>"$(mktemp)"` is blocked; use a literal path — verified-at 434307a

## Working set

- `.harness/features/FEAT-20-migration-detector/notes/uat-goalcheck-c0.md`
- `.harness/features/FEAT-20-migration-detector/runs/2026-08-14-1-validator/digest.md`
- `.harness/features/FEAT-20-migration-detector/runs/qa-gate-validator/digest.md`
- `.harness/features/FEAT-20-migration-detector/runs/plan-product/digest.md`
- `.harness/features/FEAT-20-migration-detector/BRIEF.md`
