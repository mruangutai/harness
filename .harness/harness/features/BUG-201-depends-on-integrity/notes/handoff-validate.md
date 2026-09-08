# Handoff — BUG-201-depends-on-integrity, validate → ship — written at 69af7582, seq-3

<!-- BACKFILLED 2026-09-08, like its two siblings. The seam writes were refused at the time by
     check-domain.sh, which discarded the worktree root and resolved every Authority pointer
     against the main checkout; that defect shipped as BUG-1480 in PR #1497. This note records a
     seam already crossed rather than one ahead, and is written after PR #1476 merged, when the
     `done` station made the note required. Said plainly instead of dated as contemporaneous. -->

## Next

Ship acceptance is the main session's, not a squad's: present `notes/ship-review-2026-09-07-ship.md`
to the operator and file the unstruck backlog rows B-1..B-13 with `gh-sync.py backlog`. B-1 needs no
row — it shipped as BUG-1480 / PR #1497 while this feature was blocked. Nothing is left to build.

## Trust

- The panel returned clean at c2: `must_fix: []`, `matrix_ok: true` —
  `notes/review-harness-code-reviewer-c2.md`, `notes/review-harness-qa-c2.md` — verified-at 69af7582
- The ship goal-check MET SC-01..SC-09 at the pin, with no `verify: uat` criterion in BRIEF —
  `notes/research-BUG-201-depends-on-integrity-goalcheck-ship-c1.md` — verified-at 69af7582
- `review_sha` 626bb599 is unmoved and is an ancestor of `origin/main`; every commit after it is
  `notes/`, `STATE.md` or `feature.json` — `git merge-base --is-ancestor` — verified-at a063a738
- The branch reached `main` by MERGE, never rebase, so each reviewed commit survives by id —
  this note's own commit sits on merge `69af7582`, parents `202995a1` and `9ec2a037` —
  verified-at a063a738

## Dead ends

- Do not re-open the depends_on rule for a second validation site to catch dangling edges
  earlier: SC-04 pins one implementation in `validate_plan_doc`'s call tree —
  `BRIEF.md:89` — verified-at 69af7582
- Do not read the residual `gh-sync.py ship` audit STATUS rows as this feature's drift: they name
  other features' parents and predate this run — ship output 2026-09-08 — verified-at a063a738

## Working set

- .harness/harness/features/BUG-201-depends-on-integrity/notes/ship-review-2026-09-07-ship.md
- .harness/harness/features/BUG-201-depends-on-integrity/feature.json
- .harness/harness/features/BUG-201-depends-on-integrity/plan.yaml
- .harness/harness/features/BUG-201-depends-on-integrity/STATE.md
- .claude/skills/harness/bin/harness_yaml.py

## Done when

Scope: ship acceptance relayed and the surviving backlog rows filed
Authority: brief-sc:SC-03
Authority: brief-sc:SC-09
