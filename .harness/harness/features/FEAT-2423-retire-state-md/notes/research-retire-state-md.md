# Research — FEAT-2423 retire STATE.md

Observed at worktree HEAD `3c49011652cc396e7717e799c49173ed8f452edb` (main `36ee67e5` + feature seed), BRIEF pending.
The grilling artifact's inventory (`.harness/notes/grilling-retire-state-md-2026-11-28.md`, Facts) holds; this note
records only what it did not list and the per-decision dispositions.

## Inventory the grilling did not list (all `git grep 'STATE\.md' HEAD`)

- Tracked files: 39 under `.harness/harness/features/*/STATE.md` **plus one more**,
  `.harness/kaya/features/FEAT-01-kaya-platform/STATE.md` (served-repo segment; see BRIEF open question Q-03).
- Live docs: `.harness/README.md` (state table row, orchestrator ownership, template list), `.harness/harness/docs/SPEC.md`
  (§1 runtime-load sentence, §2 state table rows for STATE.md and logs, §2.2 consistency row "STATE points at a task absent
  from PLAN", §2.3 writer-ownership bullet, §2.4 growth, §2.5 pause/resume + commit policy, §3.x template list, §10.1 loop
  steps 1 and 5, §10.2 cost-accepted bullet and the flow diagram line, §10.5 worktree callout, §10.6 ad-hoc mode,
  §15.1/15.2 single-operator and worktree table, cost section's spawn-load bullet), `.harness/harness/docs/org.html` (two cells).
- Templates beyond the grilling list: `templates/HANDOFF.md` (`## Next` placeholder "validates this against PLAN/STATE"),
  `templates/gitignore.snippet` (comment "BRIEF, PLAN, STATE, notes, ...").
- bin beyond the grilling list: `check-domain.py` has 12 mention sites (comments, `ROUTING`, `_SWEEP_PATTERNS`,
  `RE_STATE_MD`, `SHAPE_PATTERNS`, `_rule_state_md`, `SHAPE_RULES`); `structure_audit.py` also maps INV-2 and INV-5 in its
  module-to-invariant table; `harness_yaml.py` names INV-5 in a comment.
- Tests beyond the grilling list: `tests/integration/test-checker-structure-locks.py` uses `inv_2`/`INV-2` as its audit
  fixture; `test-check-state-table.py` drives `--only`, `--feature`, `--changed` and the rename case through INV-5/INV-2.
- Expertise: `.harness/harness/expertise/harness-code-reviewer.md` G-05 and `harness-validator-lead.md` G-01 name the file.
  DEC-145/DEC-253: only the owning persona edits them, at distillation. Not a build task (BRIEF Q-04).
- Historical, byte-identical by design: shipped `runs/`, `notes/`, `observations/`, three shipped `plan.yaml`
  (BUG-2187, BUG-2239, BUG-2451), kaya FEAT-01 notes/observations, `council/`, `.harness/harness/docs/BUILD.md` (completed
  build log), `tests/integration/fixtures/prior-*.fixture` (frozen prior-hook controls loaded by
  `test-check-domain-claims.py` and `test-check-plan-routes.py#write_prior_route_validator`).

## Product guidance

`docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent in the harness checkout (only `docs/PRINCIPLES.md`
and `docs/invalid-states-audit.html` are tracked). Harness's own SPEC.md and DECISIONS.md are the authorities edited.

## Decision dispositions (plan rows; one row per affected clause)

| DEC | Disposition | Clause anchor (DECISIONS.md text) | Why |
|---|---|---|---|
| DEC-45 | strike, heading + strike record kept | `STATE.md` holds no history at all | the decision is only about the file |
| DEC-71 | amend x2 | "would put un-assessed work into\n`STATE.md`."; "In exchange `STATE.md` sees a" | present-tense claim about the file |
| DEC-95 | amend | "`STATE.md ## Current` being singular is *correct within a worktree*" | reasoning names the file as current |
| DEC-120 | amend | "**`STATE.md` moves per-feature.**" paragraph | specifies the file and the main-session scan |
| DEC-129 | amend x2 | "`STATE.md`/`feature.json` in"; "INV-1..5 are per-feature now, and INV-4/5 accept" | operator: rewrite in place; INV-2/5 retire |
| DEC-138 | amend | "competes with `STATE.md` and drifts from it" | table row names the file as the status channel |
| DEC-150 | amend x4 | spec sentence, the 120-line clause, proof-shape list, relay sentence | operator: rewrite in place |
| DEC-159 | amend x4 | transitions as log entries, PLAN/STATE validation, single durable truth, separate writes | present-tense duties |
| DEC-181 | amend | "STATE.md 120." peer list | the peer budget no longer exists |
| DEC-182 | amend x2 | "`STATE.md` and the\nhandoff note are both."; "INV-3/4/5 must keep working for them." | shape list; INV-5 retires |
| DEC-199 | amend | "this entry and the feature's `STATE.md` are" | names the file as durable record |
| DEC-201 | amend | "re-reads `STATE.md` and `feature.json` from disk" | wake-time read changes |
| DEC-31 | keep | `.planning/STATE.md` | GSD's file, not this one |
| DEC-121 | keep | "what preserves `STATE.md` granularity under hierarchy" | dated quote of the spec at the time |
| DEC-160 | keep | "not-a-second-STATE.md" | dated narrative of the first live handoff |
| DEC-173 | keep | "FEAT-03-subissue-mirror's `STATE.md`" | records where a question was raised, past tense |
| DEC-180 | keep | "FEAT-05's `STATE.md` at 165 lines" | dated measurement narrative |
| DEC-131, DEC-171, DEC-191, DEC-193 | keep | state-tagged; no mention of the file | grilling asked for a disposition; DEC-191 SUPPLIES the no-new-field rule |
| DEC-174, DEC-188, DEC-205 | keep | routing, strike rule, in-place rewrite | supply the mechanism |

DEC-90 (STRUCK) also names the file; a struck entry takes no keep/amend row and stays byte-identical.

## Baselines (exit, FAIL lines), worktree HEAD 3c490116, HARNESS_AGENT_TYPE unset

All exit 0, zero `^FAIL` lines: test-check-state-plans (58s), -table (16s), -shipped (28s), -entry (6s), -records (49s),
unit/test-check-state-shipped-ctx (1s), test-harness-yaml (8s), test-check-domain-approval (6s), -post (12s),
-worktree (5s), test-validate-feature-json (1s), unit/test-answers-provenance (0s), test-merge-gitignore (1s),
test-structure-audit-single-pass (2s), test-checker-structure-locks (3s), test-check-plan-routes (46s).

## INV-2 replacement check

At HEAD, 48 harness feature directories; the only one without BRIEF.md is this feature (just seeded). Retiring INV-2 loses
the "a running flow has a goal of record" signal for directories that never had a STATE.md anyway; INV-1 still grades a
present BRIEF. Retarget rejected as new-gate scope (plan D-02).

## plan-merge receipts (2026-11-28)

- `apply` ×2 (control-plane `plan-merge.py`): both printed `APPLIED`, neither printed `APPROVAL-RESET:`, so no `gh-sync.py
  status` call was made. The first apply's post-check refused `env -u ...` verify lines as not runnable, and BRIEF SC-04 for
  invoking `check-state.py` with no feature argument (INV-41). Both were fixed and re-applied.
- `check --root <worktree>`: T-01..T-05 resolved 38 anchors. **40 FAIL**, all in T-06/T-07: each STATE.md "does not exist
  under <worktree> and neither does its directory". The worktree is sparse (FEAT-1559): its cone holds only this feature's
  directory, so no other feature's file is on disk.
- `check --root /Users/molchairuangutai/GitHub/harness` (main checkout at 36ee67e5, full tree): `7 task(s), 78 anchor(s)
  resolved, 0 failure(s)`, exit 0. No OVERLAP line. The plan's only defect against the worktree root is the sparse cone.
- `check-plan-routes.py <plan.yaml>`: `0 violation(s)`. The TASK deviations (main-session-direct over granted paths) are
  the expected DEC-174 carve-out (G-12).
- `check-state.py --feature FEAT-2423-retire-state-md` (worktree copy): no INV-38/41/49 finding. The remaining lines are
  the expected pending-approval and INV-37 (no gh-sync open receipt yet) lines.
