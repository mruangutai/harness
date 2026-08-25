# Handoff — plan — FEAT-34-worktree-act3-enforced

## Next

The plan phase is complete and waiting on ONE act that is not an agent's: the operator
re-signs `BRIEF.md`'s Amendment 1 and writes `approved` into `plan.yaml`'s `approval:`
mapping, then runs `gh-sync.py status <feature-dir> Ready`. Nothing else is outstanding.
Build starts at T-01 (`plan.yaml`), which has no `depends_on`.

Do NOT re-plan. 13 tasks and 9 decisions are settled and gate-clean.

## Trust

- plan.yaml holds 13 tasks and 9 decisions, approval pending — parsed with safe_load — verified-at 9165162
- check-state.sh exits 0 with zero VIOLATION lines — run as `bash -c "cd <worktree> && ..."` — verified-at 9165162
- check-plan-routes.py exits 0, `0 violation(s)`, exactly 4 DEVIATION lines (T-06/T-08 on check-state.sh, T-07/T-09 on test-check-state.py) — verified-at 9165162
- The 4 DEVIATIONs are CORRECT and must not be "fixed" by moving tasks to team — D-09 records why — verified-at 9165162
- Act-3 prose is at SKILL.md:430, the exit-0-from-inside fact at :434 — direct read; the brief's `:321` is stale — verified-at 9165162
- Amendment 1 covers BOTH #806 and core.hooksPath, one re-signature; original `## Approval` untouched — verified-at 9165162
- The operator's four rulings are in notes/answers-plan-2026-08-24.md and are the authority for how D-07/D-08/D-09 were written — verified-at 9165162
- SC-14 was added by pm beyond the scope the operator set; it closes a hole where a shim pointing at a nonexistent path satisfied the whole brief — UNVERIFIED, re-read the amendment before relying on the reasoning

## Dead ends

- Do not run check-state.sh or check-plan-routes.py from the default Bash cwd — they resolve `.harness/` against the working directory and silently scan the MAIN checkout, which produced one wrong conclusion in this phase already.
- Do not record a run in feature.json whose dir is absent from THIS worktree — it manufactures a review_sha violation and a cycles_used violation. Tried and reverted.
- Do not put a task's lane reasoning in `execution_reason` for a `team` task — the schema has no such field; the rows under `lanes:` are the home.
- Do not send an `approval:` mapping through plan-merge.py — it exits 8. The block is the main session's write.
- Do not write a DEC-174 amendment for this feature — D-07 settles that nothing joins the enumeration.

## Working set

- .harness/harness/features/FEAT-34-worktree-act3-enforced/plan.yaml
- .harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/answers-plan-2026-08-24.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/runs/2026-08-24-1-product/digest.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/STATE.md
