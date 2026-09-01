# Handoff — FEAT-50-run-artifact-integrity, plan → operator signature — written at 75daa3b, seq-1

## Next

Do not dispatch a squad. The plan phase ends at the user gate: the operator holds ONE
batched signature review (DEC-176) over the two `high` panel findings, the INV-32
ruling, and the fourth defect found live in this run. Only after a ruling does work
resume — resolving a finding means a pm fix cycle followed by a RE-TRANSCRIBE of
`plan.yaml`'s `panel:` key, because a reworded finding gets a new content-hash id and
the old ruling stops applying.

## Trust

- BRIEF.md and plan.yaml are complete and mutually consistent: 7 REQ all traced, no
  phantom traces, 16 SC, 8 tasks, 8 decisions, 12 lane rows — read from the loaded
  plan with `harness_yaml.load_plan` — verified-at 75daa3b
- `approval.status: pending`, four template keys, no `rulings` — verified-at 75daa3b
- `panel:` records 3 readers `ran` and 7 open findings, `severity_max: high`, ids from
  `panel_findings.py` — plan.yaml `panel:` — verified-at 75daa3b
- `check-plan-routes.py` exits 0, `0 violation(s) across 1 plan(s)`, `examined 46` — verified-at 75daa3b
- Suites are green and untouched: unit exit 0 / 0 `^FAIL ` / 1463 lines; integration
  exit 0 / 0 `^FAIL ` / 1945 lines — /tmp baselines, nothing under `bin/` was edited — verified-at 75daa3b
- `check-state.sh` exits 1 with 32 INV-32 rows BEFORE and AFTER this phase — FEAT-50
  adds none while pending — /tmp/f50-cs.txt vs /tmp/f50-cs2.txt — verified-at 75daa3b
- FEAT-50 adds 5 other check-state rows: BRIEF-not-approved and INV-6-no-review_sha
  both clear or are structural to the plan phase; three lead `digest.md` files fail
  DEC-156 — `validate-digest.py lead <path>` on each — verified-at 75daa3b
- The DEC-156 file check FAILS OPEN for every lead in a worktree: `check_artifact_file`
  joins the relative `artifact:` path to `_root_or_none()`, which returns the MAIN
  checkout, so the file is not found and the check is skipped — measured directly,
  `validate-digest.py:1408-1418` — verified-at 75daa3b
- Issue #1058 reproduced live in this run: `runs/2026-08-31-01-product/digest.md` was
  overwritten with cycle-2 content, destroying the cycle-0 authoring record — verified-at 75daa3b
- The two `high` panel findings are true, re-measured at source, not taken on report:
  `bash-write-guard.sh:747` allow-continues so the binding never reaches the Bash
  route; `test-validate-digest.py:738-739` asserts exit 0 for exactly the input D-01
  sends to exit 2 — verified-at 75daa3b

## Dead ends

- Do not plan INV-32 backfill or rescoping — outside the operator's stated scope until
  they rule — notes/answers-2026-08-31-plan.md `## Open question` — verified-at 75daa3b
- Do not route enforcement-layer files to a squad. `check-domain.sh --resolve` GRANTS
  them to backend-dev/dev-ops and DEC-174 overrides the grant — plan.yaml `lanes:` — verified-at 75daa3b
- Do not re-raise the three closed review rounds' findings — runs/2026-08-31-1-eng,
  -1-validator, and notes/research-FEAT-50-goalcheck-plan-c0.md — verified-at 75daa3b
- Do not rewrite the three non-conforming lead digests. Rewriting another agent's
  record falsifies it; the remedy is the fail-open fix — PRINCIPLES rule 15 — source

## Working set

- .harness/harness/features/FEAT-50-run-artifact-integrity/BRIEF.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml
- .harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/runs/2026-08-31-2-validator/digest.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/feature.json
