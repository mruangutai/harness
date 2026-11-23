# Ship review — BUG-2399-run-records-staged-at-ship

**Ship-ready at `74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd`** (base `9eb07b4f`). Validate c2 passed every reader; both c1 must-fix items are resolved; all three success criteria are met. Branch tip is `5a1becd6` (feature-record only above the pin). Merge, PR and deploy are yours; nothing was pushed.

No report round was spawned. Assembled from the digests on disk:
- `runs/2026-11-23-01-patch-product/digest.md` (patch intake, PASS)
- `runs/2026-11-23-02-validate-validator/digest.md` (validate c1, ESCALATE over 9db1ba98)
- `runs/2026-11-23-03-fix-validator/digest.md` (validate c2, PASS over 74e6896c)
- `notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c2.md` (goal-check c2)
- `notes/answers-2026-11-23-c1-ruling.md` (operator ruling after c1)

## Done when — by perspective, graded (validate c2 goal-check)

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator** — I can ship with every retained run record included automatically, without a manual force-add. Missing pinned evidence is reported explicitly, and running a preview does not change my files or index. | met | SC-01, SC-02 | goal-check c2 §Perspective outcomes; `tests/unit/test-prune-run-evidence.py:194–224, 239–296` at the pin; qa c2 receipt `runs/2026-11-23-03-fix-validator/qa/manifest-unit.json` (65 unit files, exit 0, tested_commit 74e6896c) |
| **code maintainer** — I have a failing-then-passing regression for automatic staging and missing evidence, while existing pruning and safety behavior remain protected and ship instructions match the implementation. | met | SC-01, SC-02, SC-03 | `notes/red-first-T-01.md` (base red: 9 assertion failures; c1-fix red: 3 failures, green 40/40, hash-bound); goal-check c2 §Criterion evidence SC-03 (pinned `harness-ship.md:43–59`, unchanged keep/prune/refusal/symlink semantics by base-to-pin inspection) |

| SC | Verdict | Method | Pointer |
|---|---|---|---|
| SC-01 | met | automated (unit) | c2 digest `sc_status`; qa c2 note `notes/review-harness-qa-c2.md` |
| SC-02 | met | automated (unit) | c2 digest `sc_status`; `notes/red-first-T-01.md:20–24,73–84` |
| SC-03 | met | inspection | c2 digest `sc_status`; clause "the manual force-add is removed" accepted as vacuous by operator ruling (base never contained the text); remaining clauses met |
| DEC-238 amendment | met | inspection | `DECISIONS.md:8058–8070` at the pin; index regenerated (input-equivalence check at 3fa183eb, blobs identical at the pin) |

## What landed

One task, T-01, built main-session-direct (DEC-174): `prune-run-evidence.py` now force-stages every surviving non-ui/ file of each recorded run at ship, refuses (exit 2, naming every path) on missing `cycle_evidence`, and — after fix-c1 — refuses (exit 1, naming every path) when any recorded-run subtree is unreadable, before any prune or stage, dry-run included. `harness-ship.md` documents the automatic staging; DEC-238's ship bullet amended; DECISIONS-INDEX regenerated.

## Leads' summaries

- **Patch intake** (`runs/2026-11-23-01-patch-product/digest.md`, PASS): BRIEF 45 lines, one bugfix task tracing SC-01–03, main-session-direct route with reason, plan check exit 0. No panel or goal-check in intake (DEC-225).
- **Validate c1** (`runs/2026-11-23-02-validate-validator/digest.md`, ESCALATE over 9db1ba98): qa/code/security/ui PASS, goal-check FAIL. MF-1 (substance, med): `os.walk` without `onerror` silently omitted unreadable subtrees. MF-2 (form): SC-03's removal clause had no target at base — escalated to the operator.
- **Validate c2** (`runs/2026-11-23-03-fix-validator/digest.md`, PASS over 74e6896c): all five readers PASS; MF-1 resolved (pruner:186–200, 238–243; regression executed as uid 501, 40 checks, no skips); MF-2 resolved by ruling; `severity_max: none`, `matrix_ok: true`, no new findings.

## Open questions

None. The one escalation (SC-03 disposition) was answered by the operator ruling in `notes/answers-2026-11-23-c1-ruling.md`; no pm amendment, no re-approval.

## Spend and ledger

- `feature-record.py spend` at close: runs 3, wall_clock_minutes 22, tokens 160185, rework_minutes 16, rework_rounds 1.
- Rework ruling: 1 round / 45 min — round 1 of 1 spent (fix-c1, main-session-direct at 74e6896c), 16 of 45 minutes.
- `cycles_used`: 0 / 10. The rework round is recorded as the `regate` judgement, not as a cycle on a run: the c1 digest binds its own `cycles_used` to 0 (the lead hosted no fix) and `run-end --cycles-used 1` on run 02 was refused on that evidence; the c2 lead reported 0. The ledger therefore counts the round (`rework_rounds: 1`) while `cycles_used` stays 0 — stated here so nobody reads 0 as "no rework".
- Judgements: 5 (mission patch; succession ×2 — build seam, and this resumed orchestrator; regate "validate cycle 2"; continue to briefing).
- Runs 3 of 20 (informational).

## Amendments (DEC-229/DEC-230)

None — no `amendment` judgement in the ledger. overrule rate: 0/0

## UAT

Not required (BRIEF `## Verification gaps`: existing operator CLI, no visual or interactive surface; ui reader scoped out on a measured 21-file diff).

## Proposed backlog

Residual findings that survived collation but do not gate. Strike rows by ID; unstruck rows become backlog issues on ship acceptance.

| ID | Nature | Finding | Source |
|---|---|---|---|
| B-1 | chore | Dedicated regressions for the pruner's advisory edge cases: `git add` failure, unsafe run ids, nested `ui/` inclusion, linked files, evidence hash mismatch, escaped evidence paths | qa c1/c2 coverage gaps; c2 digest `coverage_gaps` |
| B-2 | chore | Attributing a main-session-direct rework round to `cycles_used`: `run-end --cycles-used 1` is refused when the lead digest says 0, so a direct fix leaves `cycles_used` 0 with `rework_rounds` 1; decide whether the regate judgement is the intended sole record or the ledger needs a verb for it | this run's ledger (see Spend) |

## Next

Your call: ship (merge), fix, re-scope, or stop. Nothing was pushed, no PR opened.
