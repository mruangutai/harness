# Handoff — FEAT-27, plan → build — written at 253287f, seq-2

<!-- RECONSTRUCTED, not contemporaneous. The plan-phase orchestrator did not write this
     note before the seam was crossed; INV-17 reported the gap as a VIOLATION. It is
     written by the BUILD-phase orchestrator from the plan run's own digest and
     state.yaml, and every Trust claim below carries the pointer it was re-derived from
     and whether I re-measured it myself. Nothing here is recalled. -->

## Next

Dispatch the `build` team's eng segment to `harness-eng-lead` with tasks **T-02 and T-03 only** —
they are the sole dependency-free `execution_mode: team` tasks (`plan.yaml` tasks T-02, T-03;
`build.yaml` expansion rule). T-01, T-04 and T-06 are `main-session-direct` and hand over as one
ordered batch afterwards (`notes/layer0-segments-FEAT-27.md`); T-05 waits on T-01.

## Trust

- BRIEF and plan are both `approval.status: approved`, signed operator via main session — `plan.yaml:4-6`, `BRIEF.md ## Approval` — verified-at 253287f
- `lanes.resolved_at` is `b4659cd` and all six `execution_mode` values reproduce from `check-domain.sh --resolve` today — I re-ran the resolver on all ten literal paths — verified-at 253287f
- All sixteen T-04 anchors resolve to exactly one line each in their owning craft file — `plan.yaml` T-04 `verify:` ROWS — verified-at 253287f, re-run by me
- `harness-frontend-dev` holds a craft grant and has NO craft file; 16 grants, 15 files — confirmed by running `inject-expertise.sh`, which returns 0 bytes for it — verified-at 253287f
- T-06's `374`-entry figure is correct AT `ada8e99` and the live tree now holds 413 across the same 15 files — I recounted at both shas — verified-at 253287f
- Every `verify:` was proven RED on the unbuilt tree at plan time, and T-04's additionally proven GREEN on a scratch migration — plan run digest `runs/2026-08-18-1-product/digest.md` — UNVERIFIED by me, reported by pm
- Two pm instances wrote BRIEF.md and plan.yaml concurrently during the plan phase; the product lead found no damage in the final state — same digest, `## A process error of mine` — UNVERIFIED by me beyond the counts and anchors above

## Dead ends

- Do not split this unit into "grant now, migrate later" — an empty repository tier and a forgotten migration are indistinguishable — plan digest `## The three MUST-resolves` item 1 — source: signed plan
- Do not move the craft tier; this feature moves no files out of `.harness/expertise/` — `harness-distill/SKILL.md:43-46` places craft there permanently — verified-at 253287f
- Do not dispatch T-04 as sixteen distillation runs — D-03; the preloaded `harness-expertise` rule makes every agent refuse a mid-run Expertise write — source: signed plan
- Do not escalate T-02/T-03 under DEC-174 — its carve-out names four scripts and neither file is among them — `DECISIONS.md` DEC-174 table — verified-at 253287f
- Do not re-fix DEC-152's tier census on this branch; it is stale here only, and `origin/main` carries the amendment — `git log origin/main` shows `1dea32d` — verified-at 253287f

## Working set

- `.harness/harness/features/FEAT-27-expertise-repository-tier/plan.yaml` — the six tasks; read the one you are running
- `.harness/harness/features/FEAT-27-expertise-repository-tier/notes/layer0-segments-FEAT-27.md` — the three tasks no agent may execute
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/2026-08-18-1-eng/arch-review.md` — why several intent clauses look fussy
- `.harness/harness/features/FEAT-27-expertise-repository-tier/runs/2026-08-18-1-product/digest.md` — the plan phase's own record, incl. six carried questions
- `.harness/harness/features/FEAT-27-expertise-repository-tier/BRIEF.md` — `## Success Criteria`, what the goal-check will bind
