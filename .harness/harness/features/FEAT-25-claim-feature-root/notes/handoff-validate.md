# Handoff — FEAT-25-claim-feature-root, validate → ship — written at 8d7b273, seq-3

## Next

Nothing until the operator returns a ship decision on
`notes/ship-review-2026-08-19-ship.md`. On acceptance the MAIN SESSION runs
`gh-sync.py ship <feature-dir>` and `gh-sync.py backlog <feature-dir> <unstruck rows>`, then the PR
and merge — no PR is open and nothing is merged. On rejection of either judgement call in the
briefing's section 2, the fix routes back through a lead, not through an edit here.

## Trust

- All eight SCs met, six on pm's own measurements, two named as inherited —
  runs/2026-08-19-5-goalcheck-product/digest.md — verified-at 8d7b273
- No UAT criteria exist; pm and its lead each read BRIEF end to end — same digest — verified-at 8d7b273
- The blocking qa gate is GREEN at the commit: clean worktree at 8d7b273, `--kind integration` exit 0
  all 12 scripts PASS, `--kind unit` exit 0 — notes/gate-measurement-2026-08-19.md — verified-at 8d7b273
- The working-tree exit 1 is held dirt only: uncommitted DECISIONS.md vs a fresh index regeneration.
  Absent from the graded diff — same note — verified-at 8d7b273
- Panel PASS, severity_max med, must_fix [], nothing high under advisory_unless_high —
  runs/2026-08-19-4-panel-validator/digest.md — verified-at 8d7b273
- The fail-open is ONE site in ONE file, not four in two: test-check-state.py keeps
  `allok = allok and ok` outside the guard and holds zero `fails += 1` — my own read; correction
  appended to the panel digest — verified-at 8d7b273
- Expertise: check-expertise.sh exit 0 on all 15 files, per-section counts held, no wipe — my own
  run after applying the write-less tier's ops — verified-at 8d7b273
- cycles_used 4 of 10, runs 14 of 20, both under — feature.json — verified-at 8d7b273

## Dead ends

- Do NOT regenerate the decisions index to green the working tree. It is another workstream's
  uncommitted edit, outside this feature's diff and outside my domain; it is backlog row B-5 —
  notes/gate-measurement-2026-08-19.md — verified-at 8d7b273
- Do NOT fix B-2, B-3, B-4, B-6 or B-7 in this branch. Each is either pre-existing or a plan change
  under the operator's approval (T-03 says "add nothing else"), and none falsifies an SC — panel
  R-1..R-5 with my appended correction — verified-at 8d7b273
- Do NOT re-run the qa gate from this working tree and read its exit code as a FEAT-25 result; four
  agents have now done that and reached the wrong conclusion — same note — verified-at 8d7b273
- Never stage the held dirt: `.claude/agents/harness-{eng,product,validator}-lead.md`,
  `.harness/harness/docs/{DECISIONS,SPEC}.md`, and the untracked FEAT-26 and FEAT-27 directories —
  `git status --porcelain` — verified-at 8d7b273

## Working set

- .harness/harness/features/FEAT-25-claim-feature-root/notes/ship-review-2026-08-19-ship.md
- .harness/harness/features/FEAT-25-claim-feature-root/notes/gate-measurement-2026-08-19.md
- .harness/harness/features/FEAT-25-claim-feature-root/feature.json
- .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-19-5-goalcheck-product/digest.md
- .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-19-4-panel-validator/digest.md
