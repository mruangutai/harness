# BUG-2171 ship briefing — 2026-11-21

**Conclusion: ready to merge once PR #2230 CI is green.** Both perspectives are met. The one validation must-fix was overruled by the operator. The only CI failure, T-01 exceeding the DEC-182 plan budget, was trimmed and re-signed.

No report round was spawned. Assembled from these digests on disk:
`runs/2026-11-08-01-patch-product/digest.md`, `runs/2026-11-21-02-patch-product/digest.md`,
`runs/2026-11-08-02-smoke-product/digest.md`, `runs/2026-11-21-03-validate-validator/digest.md`,
`runs/2026-11-21-04-validate-validator/digest.md`, `runs/2026-11-21-05-patch-product/digest.md`,
`runs/2026-11-21-06-patch-product/digest.md`.

## Definition of done, graded (validate c1 goal-check)

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator**: a fresh OMP session completes a Harness child return and records a lead return automatically; told not to copy hook-injected fields | met | SC-01, SC-03 | `notes/research-BUG-2171-task-structured-goalcheck-validate-c1.md`; `notes/receipts/live-smoke*.txt`; `runs/2026-11-08-02-smoke-product/` |
| **code maintainer**: the port gate rejects loss of the setting; object and JSON-object string yield data validated identically; red at base, green at the fix | met | SC-02, SC-04 | `notes/review-harness-qa-c1.md`; `notes/receipts/red-*.txt`, `green-offline.txt` |

## Lead summaries

- **Intake** (product, runs 01 and 02): patch plan with one main-session-direct task, T-01. Run 02's lead returned text because the session's `task.structured` had reset (#2171 itself); it was closed as an operator-authorized refused return.
- **Smoke** (run 2026-11-08-02): on OMP 19.1.0 in a fresh process, both a pm child and a product lead made real `yield` calls, and the hook appended the fenced record itself.
- **Validate c0** (run 03): BLOCKED, no must-fix. QA's string-data yields were refused by the pre-fix hook loaded in the operator session, the SC-04 defect live.
- **Validate c1** (run 04, from a fresh worktree-rooted session): FAIL. All SCs met; the one must-fix (single-use smoke run id) was overruled by the operator: `notes/operator-ruling-validate-c1-2026-11-21.md`.
- **Trim** (runs 05 and 06): CI's plan-route gate found T-01 at 75/50 machine-field lines (DEC-182). The proofs moved verbatim into `notes/verify-task-structured.py`, bringing T-01 to 25 lines. Re-signed: `notes/operator-resignature-2026-11-21.md`.

## Open questions and escalations
- None open. QA-RETURN-CONTRACT (c0) was resolved by revalidating from a fresh session.

## Spend
`feature-record.py spend`: 7 runs, 77 wall-clock minutes, 43 rework minutes, 0 rework rounds. Ruling: 1 round / 45 min. Judgements: 8.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-21T16:47:01Z | T-01.verify | DEC-182 form-only budget trim; main owns unchanged extracted helper | no |
| 2026-11-21T16:47:05Z | T-01.intent | DEC-182 form-only budget trim; main owns unchanged extracted helper | no |

overrule rate: 0/2

## UAT
Not required (BRIEF: no personal UAT).

## Proposed backlog

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `plan-merge.py check` passes plans that CI's `check-plan-routes.py` refuses (DEC-182 machine-field budget); the intake should run the route gate so the signature never lands on an unmergeable plan. |
| B-2 | enhancement | Agents read hook-injected `outputSchema`/`schemaMode` in their own transcript as fields they sent: seen four times in this feature, three without any refusal. The refusal-text hint only appears on refusal; consider a dispatch-time note. |
| B-3 | chore | A session-only `task.structured` override silently reset to default mid-session (OMP behaviour); after merge the project config makes it moot, but worth an upstream report. |
| B-4 | bug | Signed live-smoke recipes that hard-code a run id cannot be re-run by validation (validate c1 must-fix, overruled); pm guidance should parameterize smoke run ids. |
| B-5 | chore | The #2171 issue text's cause line is wrong; correct it in the closing comment (wording in `notes/research-intake.md`). |
