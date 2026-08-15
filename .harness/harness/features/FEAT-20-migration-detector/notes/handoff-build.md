# Handoff — FEAT-20-migration-detector, build → validate — written at 11cb644, seq-1

## Next

Dispatch the `review` team to `harness-validator-lead` with `review_sha` pinned at the commit
that carries all four tasks — **not** `88b1182`, which predates every change. The qa segment
already ran and PASSED (`notes/qa-c0.md`), so the panel's `qa` step is gate-only and must write
`notes/review-harness-qa-c0.md`, never `notes/qa-c0.md`. After the panel, pm's goal-check against
BRIEF's 15 SCs via product-lead, then close-out and the briefing.

## Trust

- All four tasks done; each `verify:` re-run in this session, not read from a receipt — unit and
  integration suites exit 0 with zero FAIL lines; T-03's `python3 -c` yaml assertion exits 0; T-04's
  index diff and five greps exit 0 — `plan.yaml` tasks T-01..T-04 `status: done` — verified-at 11cb644
- The blocking qa gate passes: matrix union is `{unit, integration}`, both green, and both
  registration greps fired so neither suite exited 0 without running —
  `notes/qa-c0.md`, `runs/qa-gate-validator/digest.md` — verified-at 11cb644
- T-03 and T-04 are pure additions — 52 and 65 insertions, zero deletions between them; the false
  guard-claim comment at `.github/workflows/tests.yml:110-114` is byte-unchanged —
  `git diff 88b1182..11cb644 --stat` — verified-at 11cb644
- The detector is live and non-vacuous on this tree: `features: CLEAN`, `docs: CLEAN`,
  `examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)`, exit 0; `check-state.sh` exits 0
  with zero INV-27 lines — `.claude/skills/harness/bin/layout_migration.py` run directly — verified-at 11cb644
- Nothing in the repository asserts the `Layout gate` step exists — re-derived twice, by T-03's squad
  and by qa: the only `.py` naming the workflow is a back-pointer comment at
  `layout_migration.py:236` plus an unrelated domain fixture at `test-check-domain.py:715` —
  verified-at 11cb644
- **The suite is correct-today, NOT pinned against regression** — no mutation or perturbation proof
  was run, so a green result cannot distinguish a discriminating suite from one that would pass on a
  broken module — `runs/qa-gate-validator/digest.md` `adequacy_notes` — verified-at 11cb644
- `cycles_used` is 3 of 10: two from the plan phase, one from qa's in-run send-back. Both build
  dispatches were clean first passes and added zero — `feature.json` — verified-at 11cb644

## Dead ends

- Do not re-open T-03's unguarded CI step. The operator accepted it at signature (BRIEF `## Approval`
  notes, Q1) under DEC-183, and qa confirmed `test_matrix.config.always` is `[]` so the row is
  satisfied, not unsatisfiable — `BRIEF.md:237`, `runs/qa-gate-validator/digest.md` — verified-at 11cb644
- Do not re-open the missing doc-root assertion in unit cases 1 and 15. qa read the module and ruled
  it redundant: `n == 0` implies empty shapes implies CANNOT_VERIFY implies exit 2, which reddens
  case 1's `code == 0` — `runs/qa-gate-validator/digest.md` V-1 — verified-at 11cb644
- Do not edit `.github/workflows/tests.yml:110-114`. The false claim there is out of scope and owned
  by issue #279 — `plan.yaml` T-03 `intent:` — verified-at 11cb644
- Held dirt in the tree is not this feature's: two deleted `.harness/members/backend-dev/FEAT-02-*.md`
  and two untracked files under `.harness/logs/` and `.harness/notes/` predate this run. Stage by
  explicit pathspec, never `git add -A` — `git status --porcelain` — verified-at 11cb644

## Working set

- `.harness/features/FEAT-20-migration-detector/BRIEF.md` (15 SCs, the goal-check's subject)
- `.harness/features/FEAT-20-migration-detector/plan.yaml` (four tasks, all `done`)
- `.harness/features/FEAT-20-migration-detector/notes/qa-c0.md` (gate evidence for SC-10/11/12)
- `.harness/features/FEAT-20-migration-detector/runs/qa-gate-validator/digest.md`
- `.claude/skills/harness/bin/layout_migration.py` (the artefact under review)
