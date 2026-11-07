# Ship review — BUG-2161-abandon-source-tickets

**Recommendation: ship.** `gh-sync.py abandon --close-sources --yes` now disposes of a feature's plan.yaml source tickets under explicit operator confirmation, and `abandon --yes` finalizes an unopened or already-abandoned record locally. Validation failed once (two high-severity substance findings), one fix round inside the signed 2-round / 90-minute ruling resolved both, and every reader passed over the fix tip. The merge, and SC-07 (live FEAT-1774 / #1774 disposal), are yours.

review_sha: `38008d4237d7148bbbf0e54181d1a1fc6bb7de88` (feature.json; code reviewed at `c404a81d`, code-identical). Branch `feat/BUG-2161-abandon-source-tickets`. No PR, push, merge or live disposal was performed.

No report round was spawned (DEC-69). Assembled from disk: `runs/2026-11-02-01-product/digest.md`, `runs/2026-11-02-03-simplify-plan-eng/digest.md`, `runs/2026-11-02-04-simplify-apply-product/digest.md`, `runs/2026-11-03-05-build-eng/digest.md`, `runs/2026-11-03-06-t02-docs-product/digest.md`, `runs/2026-11-03-07-simplify-eng/digest.md`, `runs/2026-11-03-08-validate-validator/digest.md`, `runs/2026-11-03-09-fix-c1-validator/digest.md`; reader notes `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c{0,1}.md`, `notes/research-BUG-2161-abandon-source-tickets-goalcheck-validate-c0.md`; receipts `notes/receipt-harness-backend-dev-{T-01-c1,T-01-c2,fix-c1}.md`, `notes/receipt-harness-documentor-T-02-c1.md`. Run `2026-11-02-02-engineering` (BLOCKED, zero cycles) was a slug refusal with no digest.

## Definition of done — by perspective, graded

The validate goal-check (`notes/research-BUG-2161-abandon-source-tickets-goalcheck-validate-c0.md`, pin 1ef80c26) graded once per SC-09; the fix-round readers (`notes/review-harness-code-reviewer-c1.md`, `notes/review-harness-qa-c1.md`) re-verified the two findings that carried the failed perspective.

| Perspective (as signed) | Goal-check c0 | After fix-c1 | SCs | Evidence |
|---|---|---|---|---|
| **operator** — I can see and explicitly authorize the complete disposal of a dropped feature's source tickets, or leave every source untouched. This works even when its mirror never opened or the feature was already abandoned, including the archived FEAT-1774 record. | fail (SC-01 not met: source/task or source/parent alias was closed without `--close-sources`; SC-03 partial: a refused station write still pruned `runs/`) | met for SC-01..SC-04 | SC-01, SC-02, SC-03, SC-04; SC-07 not graded | goalcheck c0 lines 10, 18–21; code-reviewer c1 (F1, GC-01 resolved); qa c1 (alias zero-write cases, station-refusal case, pre-fix failures reproduced) |
| **code maintainer** — I can rely on one reported disposal matching what executes, the signed explanation reaching every opted-in source unchanged, and the existing rejection, shipping and close guard remaining intact. The governing decision explains the new contract and its operator-owned shared-ticket risk. | pass | pass | SC-05, SC-06 | goalcheck c0 line 9 (unit AS-01/04/10; reject/ship regression; DEC-203 §8, index and CLI inspected at the pin) |

SC-07 (operator, `verify: uat`): **not graded — post-merge operator acceptance** per BRIEF `## Verification gaps`. The sequence is in BRIEF SC-07; the documentor receipt points to it rather than duplicating it.

## What landed

- `.claude/skills/harness/bin/gh-sync.py` — `abandon --close-sources` (abandon-only; refused on other subcommands before mutation); opted-in sources resolved from plan.yaml `source_issues`; per source: comment with the parent's original `--reason-file`, close `not_planned`, Backlog after close, label `abandoned`; dry run lists every intended write including label setup, station recording and pruning; unopened-mirror early skip removed, so `--yes` records `abandoned` then prunes `runs/`; already-abandoned re-entry rewrites nothing, prunes retained `runs/`; prune happens only after the station is recorded (fix F1); a plan.yaml source that aliases a task issue or the parent receives zero writes without `--close-sources` and is reported as a GAP naming the flag (fix GC-01). Commits 88e15438, 767e1f0f, af83b980 (simplify: `_source_plan`, `_report_abandon_dry_run` extractions, test-fixture folds), 0474ae66, b5929a92.
- `tests/unit/test-gh-sync-abandon-sources.py` (new) and `tests/integration/test-gh-sync-abandon.py` — red-first cases; qa reproduced 17 unit / 39 integration pre-change failures at validate and 5 / 7 at the fix round.
- `.harness/harness/docs/DECISIONS.md` DEC-203 §8 amended in place; `DECISIONS-INDEX.md` regenerated (21bfa01d).

## Lead summaries

- Plan (product, `runs/2026-11-02-01-product/digest.md`, ESCALATE→handled): BRIEF and plan drafted, panel c0 ran four readers, two task-scope proportionality findings applied; simplify-plan (`…-03-simplify-plan-eng`) folded F-01/F-02 into T-01; simplify-apply (`…-04-…`) closed BLOCKED on a contract-shape refusal after its disk work was verified. Signed by operator 2026-11-03.
- Build (eng, `runs/2026-11-03-05-build-eng/digest.md`, PASS, 1 cycle): T-01 by backend-dev; one in-run send-back corrected a missing task/source reason comment and dry-run label setup.
- T-02 (product, `runs/2026-11-03-06-t02-docs-product/digest.md`, PASS, 0 cycles): documentor amended DEC-203 §8; index diff empty.
- Simplify (eng, `runs/2026-11-03-07-simplify-eng/digest.md`, PASS, 0 cycles): four angles; four `form` applies, zero corrective fixes; signed chain green after.
- Validate (validator, `runs/2026-11-03-08-validate-validator/digest.md`, FAIL): matrix green with fail-first evidence; code-reviewer F1 (high), goalcheck GC-01 (high), code-reviewer F2 (med), F3 advisory. F1 and GC-01 routed; F2 **not routed** by orchestrator judgement — the signed SC-02 orders only "reseat Backlog after its close" and the source comment placement mirrors the settled parent order the intent says to preserve (ledger `continue` judgement; you may overrule by sending "fix F2").
- Fix c1 (validator hosting backend-dev, `runs/2026-11-03-09-fix-c1-validator/digest.md`, PASS, 1 cycle): F1 and GC-01 resolved at b5929a92; qa, code, security, ui PASS; one med test-only complexity advisory (B-2).

## Open questions

None blocking. One judgement for you to confirm or overrule at ship: GC-01's remedy shape — held-back aliases are skipped and reported as a GAP (the feature still abandons) rather than refused outright. Both satisfy SC-01; skip-and-report was chosen so an abandonment never stalls on an alias.

## Resolved escalations

None in the ship phase. Plan phase: the product lead's simplify-pass escalation was routed to eng-lead and applied by pm (runs 03/04).

## Spend and judgements

`feature-record.py spend`: 9 runs, 94 wall-clock minutes, 424,745 tokens; rework 1 round of 2, 28 of 90 minutes. `cycles_used: 2` of 10 (build send-back 1, fix round 1). Judgements: 5 (`mission: plan`, `succession: continue` ×2, `continue`, `regate`). `len(runs)` 9 of 20 informational.

## Amendments (DEC-229)

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | no builder-side departure from signed task text; `signed_task_hashes` unchanged | — |

overrule rate: 0/0

## UAT

SC-07 after merge: run `gh-sync.py abandon <FEAT-1774 dir> --reason-file <signed reason> --close-sources` (dry run), inspect the reported writes, then `--yes`; confirm #1774 closed `not_planned`, in Backlog, labelled `abandoned`, with the parent's reason text verbatim, and the archived record's station unchanged with `runs/` absent.

## Before merge

- `feature-worktree.py behind` against the **refreshed** remote default branch: the validate goal-check measured local `main` at c5233803 while origin/main is e817d357 — refresh before comparing.
- `gh-sync.py ship` from the main checkout (it refuses inside `.claude/worktrees/`), then ship again with `--body-file` pointing at this note so the briefing posts on parent #2162.

## Proposed backlog

| ID | nature | finding | source |
|---|---|---|---|
| B-1 | chore | Source comment is posted before the source close (mirrors parent order); if close-first is preferred for sources, reorder and assert — F2, med, not routed as a spec violation | `notes/review-harness-code-reviewer-c0.md` |
| B-2 | chore | Test helpers at grade 2: `main._src_ops` (integration, cyclomatic 12) and `touches` (unit, cognitive 17) — nonblocking, accepted test-only reasons recorded | `notes/review-harness-code-reviewer-c0.md`, `-c1.md` |
| B-3 | chore | Leads in this OMP runtime return by final message, so the SubagentStop hook never appends the fenced YAML to `runs/<id>/digest.md`; the orchestrator appends it by hand before `close-run` on every run — a harness defect, not a feature one | `observations/harness-orchestrator.md` |
| B-4 | chore | `feature-record.py` has no verb for pinning `review_sha`; this run wrote it through `feature_json_write.write_feature_json` directly (lock + schema) — a `pin-review` verb would close the gap | this note |
