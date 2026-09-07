# Handoff — BUG-1290-factory-claim-repo-root, plan → build — written at eb9d044e, seq-1

## Next

Take the operator's signature on `BRIEF.md` (`## Approval`) and `plan.yaml` (`approval.status`),
then `plan-merge.py sign-approval` and `gh-sync.py status <feature-dir> Ready` — both the main
session's acts, not the orchestrator's. Three items ride to the operator with the packet: Q1 the
D-01 shape deviation (blocking, only the operator can accept it), Q2 the case-22 comment reword in
T-04 (adopted scope), Q3 the `workspace_path` rewrite in T-03 step 1 (adopted scope). Only after
the signature does a build orchestrator start at T-01 (`plan.yaml` tasks T-01..T-05, DAG:
T-01 and T-02 first, T-03 after both, then T-04 and T-05).

## Trust

- Both panel blockers are genuinely closed, measured not attested (regex run against the compliant and non-compliant join; whole-file grep re-run independently) — `runs/2026-09-05-08-validator/digest.md` — verified-at eb9d044e
- The `panel` key transcription is faithful to the panel digest, both readers `ran`, no reader skipped — `runs/2026-09-05-08-validator/digest.md` — verified-at eb9d044e
- `tests/integration/test-factory-integration.py` and `tests/unit/test-factory-claim.py` are GREEN at the base commit, so every planned `verify:` red-state is a real discriminator — `runs/2026-09-05-02-eng/digest.md` — verified-at eb9d044e
- Every plan anchor was re-checked at the base commit after two were found wrong in the first draft — `runs/2026-09-05-03-product/digest.md` — verified-at eb9d044e
- Case 5d's discrimination is unbound: T-05's mutation proof covers 5a/5b/5c only — `runs/2026-09-05-08-validator/digest.md` — UNVERIFIED
- No agent has enumerated hardcoded-segment fixtures repository-wide; only `test-factory-integration.py` was swept — `runs/2026-09-05-08-validator/digest.md` — UNVERIFIED

## Dead ends

- Do not widen the moved reader row's migrated pattern to `[^,]+`; T-03 binds a paren-free local instead — `plan.yaml` T-04 step 1 — verified-at eb9d044e
- Do not re-open D-01's shape to chase the operator's original wording without the operator's answer to Q1 — `notes/research-BUG-1290-factory-claim-repo-root-goalcheck-plan-c1.md` §1 — verified-at eb9d044e
- Do not migrate `post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231` onto the new resolver — `.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md` `## Out of scope` — verified-at eb9d044e

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/BRIEF.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-05-08-validator/digest.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/research-BUG-1290-factory-claim-repo-root-goalcheck-plan-c1.md`
- `.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md`

## Done when

Scope: the operator's signature is recorded on both plan artifacts
Authority: approval:.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/BRIEF.md#Approval
