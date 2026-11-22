# Ship review — BUG-2294-prune-keeps-run-digests

**Ready to merge.** The pruner now deletes only `runs/<id>/ui/` for runs outside the keep set, never a run record or a digest, and never anything reached through a symlink. The validate panel is clean at `88bf039f6ff31edbb1d5a4b2f6620762e3cc095a` (code commit `e51277a4`, base `c1724230`) after one rework round, which is the whole of the signed ruling (1 round / 45 min; 16 rework minutes used). Nothing gates. Merge, PR and deploy are yours.

No report round was spawned. This briefing is assembled from the digests `feature.json` names:
- `runs/2026-11-22-01-patch-product/digest.md` (patch intake, PASS)
- `runs/2026-11-22-02-validate-validator/digest.md` (validate c1, FAIL — SEC-01)
- `runs/2026-11-22-03-validate-validator/digest.md` (validate c2, PASS)
plus the c2 reader notes under `notes/` and the orchestrator's probe record `notes/must-fix-c1.md`.

## Definition of done — graded (validate c2 goal-check)

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator** — I can prune obsolete UI evidence without losing any run's durable record or breaking its cycle-evidence checks. The existing keep rules and ship invocation remain available unchanged. | met | SC-01, SC-03 | `notes/research-BUG-2294-prune-keeps-run-digests-goalcheck-validate-c2-final.md`; qa execution `notes/review-harness-qa-c2.md:28–45` (literal T-01 verify 25 PASS / 0 FAIL at the pin) |
| **code maintainer** — I have a regression that catches the empty-keep-set, final-BLOCKED, no-UI failure before it can ship again, and the affected retention instructions describe the behavior that actually runs. | met | SC-02, SC-03 | same goal-check note; base RED audited: all ten hash-bound digests lost and post-prune INV-7 fails on `c1724230` (`notes/red-first-T-01.md`) |

SC-01 met (automated), SC-02 met (automated), SC-03 met (inspection), DEC-238 amendment disposition met (inspection: `DECISIONS.md:7990–7998` at the pin reads UI-only deletion with the three protected files).

## What happened, per lead

- **Product (patch intake)** — `runs/2026-11-22-01-patch-product/digest.md`: pending BRIEF and a one-task plan (T-01, bugfix, main-session-direct because `.omp/commands/harness-ship.md` is owned by no squad). You signed on 2026-11-22 (`notes/answers-2026-11-22-signoff.md`).
- **Build** — main-session-direct, test-first: `51f7db2b` (UI-only deletion, unit test, ship prose, DEC-238 text, index), `d225287c` simplify pass with no findings. Red-first evidence `notes/red-first-T-01.md`: 7 assertion failures against the base pruner.
- **Validate c1** — `runs/2026-11-22-02-validate-validator/digest.md`: qa, code, ui, goal-check PASS; security FAIL on SEC-01 — a run-directory symlink let `rmtree(alias/ui)` delete a kept run's real `ui/` or an outside `ui/`. The orchestrator reproduced it by probe at the pin and confirmed the base refused the same shape (`notes/must-fix-c1.md`).
- **Fix c1** — main-session-direct, `e51277a4`: `_ui_targets` skips a symlinked run entry and a symlinked `ui` with a named `skipped runs/<id>[/ui] (symlink)` line; rmtree receives only a real `ui/` under a real run directory. Regressions `symlink_dry_run` / `symlink_prune`: red 4 against the `70981edd` pruner, green 25/25.
- **Validate c2** — `runs/2026-11-22-03-validate-validator/digest.md`: all five readers PASS, `must_fix: []`, `severity_max: none`, `matrix_ok: true`. qa executed the literal verify (25/25, rc 0) and the unit runner (63 files, rc 0). Security's original raiser closes SEC-01 for the three static link shapes. Goal-check needed one in-run evidence sendback (its first grade was conditional on qa finishing); no code changed between the two grades.

## Open questions

- **SEC-C2-Q1 (non-blocking, from security c2)** — the pruner's feature-directory selection trusts lexical ancestors: a symlinked `.harness/…/features/<feat>` or `runs/` container, or a traversal-bearing `--feature` argument, can still point deletion outside the checkout. Pre-existing at base (where it reached whole-run rmtree); the fix narrows it to `ui/`. Recommendation: a separate authorization task (realpath containment of the feature dir), not an expansion of T-01. Listed as B-1 below.

## Resolved escalations

- Q-QA-C2-1 — qa copied two execution logs (`qa-c2-verify.txt`, `qa-c2-kind.txt`) into the validator run directory, outside its domain; the validator lead retained them as supplemental evidence and recorded the domain violation (`runs/2026-11-22-03-validate-validator/digest.md`). Listed as B-3.

## Spend and ledger

`feature-record.py spend`: 3 runs (budget 20, informational), 27 wall-clock minutes, 150,188 tokens, rework window 16 minutes / 1 round (ruling: 1 round / 45 min — spent). `cycles_used` 1 / 10: the c2 lead's reported in-run goal-check sendback; the code rework round is the `regate` judgement. Judgements: 5 (mission, succession, continue, regate, continue). No UAT required (BRIEF).

## Amendments (DEC-229/DEC-230)

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | the build made no departure from the signed T-01 text | — |

overrule rate: 0/0

## Proposed backlog

| ID | Nature | Item |
|---|---|---|
| B-1 | enhancement | `prune-run-evidence.py`: authorize the selected feature directory by realpath containment; reject linked ancestors and traversal-bearing `--feature` arguments; state concurrent-writer expectations (SEC-C2-Q1, `notes/review-harness-security-reviewer-c2.md:18–22`). |
| B-2 | chore | Symlink coverage gaps left advisory by qa c2: a symlink named in `--keep`; symlinked children inside a real `ui/`; `ui-link-run` `digest.md` byte preservation not asserted in the new fixture (`notes/review-harness-qa-c2.md`, `## coverage_gaps`). |
| B-3 | chore | qa in gate-only mode wrote two logs (143 KB) into the validator run directory, outside its domain grant; decide whether the run directory may hold reader logs or the guard should refuse them. |
| B-4 | bug | The host hook injects `outputSchema`/`schemaMode` into orchestrator → lead `task` calls although the dispatch instruction forbids them (seen on both validate dispatches); the leads returned valid digests regardless. |

Unstruck rows become backlog issues on ship acceptance; anything not listed here dies.
