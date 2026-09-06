# Handoff — FEAT-55, validate → ship — written at 76ba5f41, seq-10

## Next

Present `notes/ship-review-2026-09-05-02-eng.md` to the operator and take the ship decision. Nothing
is outstanding below it: twelve of twelve tasks verified, twelve of twelve SCs met, the qa matrix
PASS, the panel PASS with its one `must_fix` closed and re-confirmed by the reviewer that raised it.
Do NOT re-open the build or the panel. On ship acceptance the MAIN SESSION runs `gh-sync.py ship`
from the MAIN checkout (it refuses at exit 1 from inside `.claude/worktrees/`) with `--body-file`
pointing at that briefing, files the unstruck backlog rows, merges, and only then dispatches
feature-close distillation. Cited: STATE.md `## Current`, plan.yaml `status: review`.

## Trust

- Both approval fragments still signed and byte-intact after the plan amendment — plan.yaml
  `approval.status: approved`, `approved_by: molchairuangutai`, 2026-09-05, all five original
  `approval.rulings` ids present — verified-at 76ba5f41
- All ten FEAT-55 suites exit 0 / FAIL 0, per-file exit code and per-file `^FAIL ` count, never a
  tail read — my own census — verified-at 76ba5f41
- The unit driver `.claude/skills/harness/bin/run-unit-tests.sh` exit 0 / FAIL 0 — my own census,
  exit status captured in a variable — verified-at 76ba5f41
- Zero `SEVERITY: high` across the whole feature diff —
  `code-grade.py --base eb9d044e --head 76ba5f41` — verified-at 76ba5f41
- `write_factory.transform` GRADE 4 / ABC 9.0 and the new `_factory_block` GRADE 4 / ABC 14.1, both
  clearing bar 4 — measured by me at HEAD and independently by the code reviewer — verified-at 76ba5f41
- The two `typed` mappings are declared on both closed schema objects, neither in a `required` list,
  both objects still `additionalProperties: false` — verified-at 76ba5f41
- gh-sync's capability query calls `capability_query_args(repo)` bare, no `--repo`, no false comment
  — verified-at 76ba5f41
- All twelve SCs met and REQ-01..REQ-11 traced — pm's `notes/research-FEAT-55-goalcheck-c1.md` —
  UNVERIFIED per criterion by me; I verified the suite evidence the automated ones rest on
- qa, security and ui panel verdicts are INHERITED from the cd6a3c0d pin across a 30-line
  behaviour-preserving extraction and a 7-line comment fix; only code-reviewer re-ran — UNVERIFIED

## Dead ends

- Do not run `gh-sync.py status <dir> review`: it REFUSES because no task carries a `status:` key and
  `set-task-station` can only splice an existing line — STATE.md Q5, briefing B-5 — verified-at 76ba5f41
- Do not work around that by editing plan.yaml: `plan-merge.py` is the only write route and the shape
  gate denies Edit, Write and shell redirect — D-04 — verified-at 76ba5f41
- Do not re-sign the plan: `amend` and `apply` preserve approval bytes by construction, so the
  original signature covers the F-01/F-02 amendments — plan-merge.py step 7 — verified-at 76ba5f41
- Do not try to recover `runs/2026-09-05-01-product/state.yaml`: the runs tree is gitignored, so
  `git checkout --` answers `did not match any file(s) known to git` — measured — verified-at 76ba5f41
- Do not spend a cycle without a raise: `cycles_used` is 13 of 13 — feature.json — verified-at 76ba5f41
- Do not remove this worktree from inside it — DEC-95/DEC-193 — verified-at 76ba5f41

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-02-eng.md
- .harness/harness/features/FEAT-55-issue-types-created-work/notes/research-FEAT-55-goalcheck-c1.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-32-validator/digest.md
- .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
- .harness/harness/features/FEAT-55-issue-types-created-work/notes/answers-build-blockers-20260905.md

## Done when

Scope: the operator's ship decision on the FEAT-55 briefing
Authority: approval:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md#Approval
Authority: finding:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-01-eng.md#F-03
