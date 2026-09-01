# Handoff — FEAT-50-run-artifact-integrity, plan → operator signature — written at 5d12e68, seq-2

## Next

Do not dispatch a squad. The plan phase ends at the user gate and the plan is SIGNABLE on
panel grounds: no `high`, `critical` or unrated finding survives. The operator holds one
batched signature review (DEC-176) over eleven advisory findings at `severity_max: med`.
The external INV-32 hold is LIFTED — the fix merged into `main`, so D-09's precondition is
met. After signature the FIRST act, before any build dispatch, is updating the feature
branch from `origin/main` (main session's); SC-11 is ungradeable until then. Build
sequences T-08 first — both T-03 and T-09 need its `worktree_for_feature` seam — and T-07
last, which depends on all eleven others.

## Trust

- No `high`/`critical`/unrated finding survives; eleven `open` at `severity_max: med` — I
  recomputed the gating set against `check-state.sh:218-219` — verified-at 5d12e68
- All ELEVEN `PF-` ids recompute exactly from `panel_findings.finding_id(reader, summary)`,
  which is also the proof the five carried cycle-0 summaries are verbatim — verified-at 5d12e68
- `panel.readers` carries `should-not-exist`, `scope` AND `goalcheck`, each `ran`;
  `check-state.sh:220-233` VIOLATES on a missing one — verified-at 5d12e68
- `approval.status: pending`, `rulings` ABSENT; nothing under `.claude/skills/` modified
  this phase — `git status --porcelain` — verified-at 5d12e68
- `check-plan-routes.py` exits 0, `0 violation(s) across 1 plan(s)`, 9 DEVIATION lines all
  DEC-174 carve-outs; `load_plan` gives T-01..T-12, D-01..D-11, 14 lanes — verified-at 5d12e68
- Both cycle-0 `high` findings are true at source and their fixes land where they must:
  `bash-write-guard.sh:747` allow-continue (T-09), obsolete case at
  `test-validate-digest.py:738-739` (T-02 step 5) — re-measured myself — verified-at 5d12e68
- The fourth defect's remedy has an in-file precedent: `check_artifact_file` joins to
  `_root_or_none()` (`:1413`) while `_hook_feature_dir` (`:1359-1372`) already resolves the
  feature's checkout correctly — verified-at 5d12e68
- `PF-f52c5043…` (`med`) is INERT today: `HARNESS_PROJECT_DIR` is READ in exactly one
  production file, `harness_boundary.py`, and SET by none — verified-at 5d12e68
- The three DEC-156-failing digests cannot reach the default branch: `.gitignore:7` excludes
  `.harness/*/features/*/runs/**` — `git check-ignore -v` — verified-at 5d12e68
- **UNVERIFIED**: that INV-32 passes once APPROVED. I read the gate against the actual data
  and every condition holds, but could not run it approved — `check-domain.sh` denies my
  Edit of `approval:`, correctly. Re-check after signature.
- **UNVERIFIED**: every `verify:` block. A panel grades a specification; they are prose
  until someone runs them.

## Dead ends

- Do not re-open INV-32 options (a)/(b)/(c) — a fourth option was taken and the fix landed
  externally — notes/answers-2026-08-31-plan.md `## Operator ruling — INV-32` — verified-at 5d12e68
- Do not write `approval.rulings` — no overrule was taken; an entry is validated against
  `panel.findings` and emits two INV-32 rows naming FEAT-50 — check-state.sh:189-204 — verified-at 5d12e68
- Do not rewrite the three non-conforming lead digests; a third party editing another
  agent's record falsifies it — PRINCIPLES rule 15 — verified-at 5d12e68
- Do not reword any finding `summary:` — it is the content-hash input — panel_findings.py — verified-at 5d12e68
- Do not start build before the branch is updated from `origin/main` — the operator's
  instruction — notes/answers-2026-08-31-plan.md — source

## Working set

- .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml
- .harness/harness/features/FEAT-50-run-artifact-integrity/BRIEF.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/runs/2026-08-31-6-validator/digest.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/feature.json
