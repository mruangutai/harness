# Handoff — BUG-1305-run-state-clobber, validate → ship — written at 252a18a9, seq-3

## Next

Present `notes/ship-review-2026-09-05-final.md` to the operator for the ship decision and the
backlog strikes. On acceptance the main session runs `gh-sync.py ship <feature-dir> --body-file
<that briefing>` from the MAIN checkout, then `gh-sync.py backlog` for the unstruck rows, then merge;
the `post-merge` hook removes this checkout and feature-close distillation follows. Four scratch
worktrees named in the briefing's cleanup section must be removed first — INV-29 sees them.

## Trust

- SC-07 MET at the pin and every other live criterion carries — runs/goalcheck-build-c5-product digest, inline in its lead's return — verified-at 252a18a9
- Production code byte-unchanged since the reviewed pin: `git diff 154ff2a0 252a18a9 -- .claude/skills` is empty — verified-at 252a18a9
- The handoff PRE permit reddens under two independent live mutants — notes/review-harness-qa-c5.md — verified-at 252a18a9
- Suites at the seam: test-check-domain exit 0 markers 27/27, integration 46 files 0 FAIL, checker exit 0 — Main-reported, not re-run by me — UNVERIFIED
- Every governed Edit is forced to Write on this host: the omp bridge sends `{ file_path }` only — .omp/extensions/harness-hooks.ts preDomain edit branch — verified-at 252a18a9

## Dead ends

- Fixing anything with a squad: every surface is main-session-direct under DEC-174 — plan.yaml lanes.rows — verified-at 252a18a9
- A directory-shaped Bash guard for SEC-01: ruled a follow-up, filed as #1376 — notes/review-harness-security-reviewer-c2.md — verified-at 252a18a9
- Spending cycle 18 on citation and provenance polish: operator ruled against it — briefing rows B-2 to B-4 — verified-at 252a18a9
- Re-reviewing the guards or re-grading carried criteria: Advisor's revalidation scope, production bytes unchanged — agent://AdviseBug1305Sc07Conflict — UNVERIFIED

## Working set

- .harness/harness/features/BUG-1305-run-state-clobber/notes/ship-review-2026-09-05-final.md
- .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c5.md
- .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c5.md
- .harness/harness/features/BUG-1305-run-state-clobber/feature.json
- .harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md

## Done when

Scope: operator takes the ship decision and the backlog strikes
Authority: brief-sc:SC-07
