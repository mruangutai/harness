# BUG-2566 ship review: refuse governed calls when the loaded hook code no longer matches disk

**Conclusion:** ready to merge. Validate run 05 is PASS at pin `f4048ad3` with nothing left to fix, and your UAT for SC-10 passed. The merge is yours.

**After merging, restart every open omp session once.** A session started before this change cannot detect that it is stale. From then on, a change to the hook shows up as a one-line "restart omp" refusal rather than a misleading error.

**How this was assembled.** No report round was spawned. This review was assembled from:
- the plan run digests: `runs/2026-11-27-01-plan-product/digest.md` to `runs/2026-11-27-03-plan-product/digest.md`;
- the validate run digests: `runs/2026-11-27-04-validate-validator/digest.md` and `runs/2026-11-27-05-validate-validator/digest.md`;
- `notes/research-BUG-2566-stale-hook-detection-goalcheck-validate-c2.md`;
- `notes/receipt-main-session-build.md`, `notes/fail-first-T-01.md` and `notes/uat.md`;
- your rulings: `notes/answers-2026-11-27-signoff.md` and `notes/answers-2026-11-27-validate-c1.md`.

## Definition of done, graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator:** a running session never enforces hook code that no longer matches its checkout; governed calls are refused with one restart-omp line, except a persona's BLOCKED yield; Main's own reads, edits and ordinary shell keep working; the record says which sessions cannot detect it | met | SC-01, SC-02, SC-03, SC-09, SC-10 | `omp-hooks.test.ts` SC-01..SC-03 cases (26 red before the change, 8 preserved); SPEC §4.2 "Stale hook code (BUG-2566)"; `notes/uat.md` PASS with the verbatim refusal |
| **orchestrator:** refused only on a real content change, never on a timestamp touch, a schema or agent-definition edit, or another checkout; no noticeable slowdown | met | SC-04, SC-05 | the SC-04 cases, with the mtime mutant failing 4 of them; median check time 0.063 ms against a 5 ms bound |
| **code maintainer:** the fingerprinted set is stated in one place in the hook module, derived from where it was loaded; the existing suite and typecheck pass | met | SC-06, SC-07, SC-08 | `HOOK_FINGERPRINT_MODULES` derived from `import.meta.url`, with `staleHookRefusal` the only new export; omp-hooks 274/0; typecheck exit 0 |

## Lead summaries

- **Plan.** Three product runs: 01 and 02 FAIL, 03 PASS. You signed with a budget of 2 rounds / 90 minutes. You re-decided the fingerprint set at signature: the hook module only.
- **Build.** Built by the main session directly (DEC-174). T-01 (hook plus tests, test-first, mutant-proven) is `a9691cbb`. T-02 (SPEC §4.2) is `07cf4954`. The simplify pass applied nothing.
- **Validate round 1 (run 04): ESCALATE.**
  - Two test gaps: the FIFO probe didn't check that `mkfifo` succeeded, and the path in the refusal wasn't checked to be relative to the checkout root.
  - E-01: a baseline that isn't a content hash at startup. You ruled it next to impossible and not worth documenting.
- **Validate round 2 (run 05): PASS.** Both gaps are closed and proven by mutation. `must_fix` is empty and `severity_max` is low.

## Questions and escalations

There are no open questions.

| Run | Item | Ruling |
|---|---|---|
| 04 | E-01: a load-time baseline that isn't a content hash, including the case where the file is swapped during startup | Accepted as is and not documented, because the timing is next to impossible. This case is what prompted the practicality rule, #2622 |
| 04 | OQ-02: a UAT script | Steps copied to `notes/uat.md`, not authored by the PM |

## Spend

- `feature-record.py spend`: 5 runs, 88 wall-clock minutes, 35 of them rework, against a budget of 2 rounds / 90 minutes. Tokens were not measured by the host.
- 3 judgements.

## Amendments

None. overrule rate: 0/0

## UAT

SC-10: **PASS**, 2026-11-27. I ran it at your request in two headless omp sessions in the worktree:
1. After the hook file changed, a `task` dispatch was refused with the restart line.
2. In the same session, a read and an edit still worked.
3. A fresh session's dispatch completed.

The verbatim refusal is in `notes/uat.md`.

## Proposed backlog

Strike either row by ID. Unstruck rows become issues when you accept the ship.

| ID | Nature | Item | Source |
|---|---|---|---|
| B-1 | chore | `staleTree()` in `tests/unit/omp-hooks.test.ts` never removes its temp directories: about 13 per suite run under the OS temp dir. The fix is a one-line `afterAll`. Not applied after the PASS pin, because that would have meant another review round | run 05, code reviewer |
| B-2 | chore | No test pins that the carve-out requires `VERDICT` to be exactly `"BLOCKED"` (mutant M6 survives). It is pinned by inspection (SC-06), and `validate-digest.py` still judges the yield. Under #2622 this is likely not worth a test | runs 04 and 05, QA |
