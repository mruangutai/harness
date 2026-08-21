# Handoff — FEAT-30-worktree-per-feature, plan → build — written at 49c528a, seq-1

<!-- RECONSTRUCTED, not inherited. Both plan-phase orchestrators ended at this seam without writing
     it (the first at a corrected context peak of 407,424 tokens), so this was assembled from disk
     by the build successor on the DEC-159 disk-only path. Every claim re-measured at 49c528a. -->

## Next

Dispatch the `build` team to **harness-eng-lead** with exactly the five `execution_mode: team` tasks
— **T-01, T-02, T-06, T-08, T-10** — DAG-ordered T-01‖T-06 → T-02 → T-08 → T-10, team definition
`.claude/skills/harness/teams/build.yaml`, specification `plan.yaml` (`prompt: from_task_intent`).
Then the qa segment (`gates.qa_gate: blocking`), then simplify, then commit. **Stop at T-03**, the
DAG's first `main-session-direct` task, and return `notes/layer0-segments-FEAT-30.md`.

## Trust

- Both approval gates read `approved` and are COMMITTED, not just in the tree — `BRIEF.md:275-279`,
  `plan.yaml:2-5`, present in `git show 49c528a:…/plan.yaml` — verified-at 49c528a
- R-01/R-02 intact in `approval.rulings`; `max_total_cycles` 13, `cycles_used` 5, so **8 cycles
  remain for the whole rest of the feature** — `feature.json`, `plan.yaml:16-79` — verified-at 49c528a
- **The team lane has ZERO dependencies on the main-session-direct lane** — `plan.yaml`
  `tasks[].depends_on` — verified-at 49c528a
- Baseline, counted by `^FAIL ` lines with exit status in a variable (a tail read of this runner
  reports red as green): unit exit 0/179 PASS/0 FAIL; integration exit 0/90 PASS/0 FAIL — verified-at 49c528a
- `check-plan-routes.py plan.yaml` exits 0, `0 violation(s)`, expected DEVIATIONs on T-03/T-04/T-05,
  `OK T-10` — verified-at 49c528a
- All four `NOBODY` resolutions behind the T-07/T-09 lanes still hold — `check-domain.sh --resolve`
  — verified-at 49c528a
- T-04's anchors are still valid: `check-domain.sh` and `harness_boundary.py` byte-identical
  `eeabc59`→HEAD, and `:37`, `:602`, `:644`, `test-bash-write-guard.py:491-506` land on the claimed
  content — verified-at 49c528a
- **Fail-open ordering hazard, measured not inferred:** `harness_boundary.py:37` and
  `check-domain.sh:644` both hard-code `[^/]+/`, exactly ONE segment below `.claude/worktrees`, while
  T-01's `dest_for` builds `<segment>/<id>`, two. Until T-04 lands, a REAL worktree from the new CLI
  escapes the sweep and the boundary strip — silent fail-open, not a block — verified-at 49c528a
- Mirror open: milestone #19, parent #572 adopted, sub-issues #616–#625 — `feature.json` — verified-at 49c528a
- `check-state.sh` foreign noise is 9 rows (FEAT-26/FEAT-28 unapproved BRIEFs, 7 FEAT-29 board
  drift); a violation COUNT is a shared mutable global across concurrent flows, so scope any
  assertion to FEAT-30 by name — `notes/orchestrator-M13-d08-baseline-unstable.md` — verified-at 49c528a

## Dead ends

- Do NOT re-litigate R-01 or R-02 — `plan.yaml:16-79` — source: operator, 2026-08-20
- Do NOT re-open T-10's `team` lane; no tool can settle it and it was accepted with the signature.
  Evidence that `feature-worktree.py` is hook-registered is a finding to REPORT — `plan.yaml:13-15`
- Do NOT split T-05; any split lands a red suite between tasks — `runs/archreview-eng/` — source: archreview-eng
- Do NOT round-trip `plan.yaml` through a YAML dumper — it carries the signature comments and
  `approval.rulings`; edit status lines in place and diff-verify — `plan.yaml:6-15` — verified-at 49c528a
- Do NOT touch `.claude/worktrees/FEAT-31`; it is the operator's — source: dispatch
- `feature.json` will NOT accept a `phase:` key — `check-domain.sh --post` denies it against the
  execution-state schema, contradicting the DEC-148/159 playbook. Phase lives in `STATE.md` — verified-at 49c528a

## Working set

- `…/FEAT-30-worktree-per-feature/plan.yaml` — the specification; grep by task id, never whole (94 KB)
- `…/FEAT-30-worktree-per-feature/STATE.md` — current truth and open questions
- `…/FEAT-30-worktree-per-feature/feature.json` — budgets, runs, mirror ids
- `…/notes/orchestrator-M16-sc01b-is-automatable.md` — why SC-01b is automatable, and its measured shape
- `…/FEAT-29-graphql-budget/notes/layer0-segments-FEAT-29.md` — the handover shape to match
