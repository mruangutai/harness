# Handoff — BUG-201-depends-on-integrity, build → validate — written at b44005a8, seq-2

<!-- BACKFILLED 2026-09-08, not written at the seam, for the same reason as handoff-plan.md:
     check-domain.sh refused the worktree write until BUG-1480 shipped in PR #1497. Recorded
     as a backfill rather than presented as contemporaneous. -->

## Next

Pin `review_sha` at the build tip and run `gh-sync.py status <feature-dir> review` BEFORE
dispatching the reviewer panel to `harness-validator-lead` (INV-6, lowercase station). The
panel reads the six task receipts under `notes/`; the QA matrix is already green, so the
panel grades code, not coverage.

## Trust

- All six tasks reached station done — `plan.yaml` T-01..T-06 `status: done` at :307, :365,
  :404, :474, :504, :575 — verified-at b44005a8
- The QA matrix PASSED and its evidence is a real artifact, not a claim —
  `notes/qa-harness-qa-c1.md` — verified-at b44005a8
- SIMPLIFY ran before the pin and applied its one permitted fold-in —
  `notes/receipt-harness-backend-dev-simplify-c1.md` — verified-at b44005a8
- T-01's pre-rule run failed for the right reason, which is SC-05's actual subject —
  `notes/receipt-harness-backend-dev-T-01-c1.md` — verified-at b44005a8

## Dead ends

- Do not re-run SIMPLIFY after the pin: an apply commit moves the tip and invalidates the
  panel's verdict — `notes/receipt-harness-backend-dev-simplify-c1.md` — verified-at b44005a8
- Do not treat `code-grade.py` grading an unchanged function as changed as a build defect;
  it is a pre-image line-offset bug, raised as Q-H — `STATE.md` Open Questions —
  verified-at b44005a8

## Working set

- .harness/harness/features/BUG-201-depends-on-integrity/plan.yaml
- .harness/harness/features/BUG-201-depends-on-integrity/notes/qa-harness-qa-c1.md
- .claude/skills/harness/bin/plan-merge.py
- .claude/skills/harness/bin/gh-sync.py
- .harness/harness/features/BUG-201-depends-on-integrity/feature.json

## Done when

Scope: review_sha pinned, station at review, the reviewer panel dispatched and graded
Authority: brief-sc:SC-03
Authority: brief-sc:SC-08
Authority: brief-sc:SC-09
