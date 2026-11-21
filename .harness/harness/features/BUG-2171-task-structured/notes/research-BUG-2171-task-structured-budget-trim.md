# T-01 contract-budget maintenance

Complete: machine-field budget reduced from **75 to 25**, with the final feature-scoped route checker reporting **0 violations**. Approval remains pending, unchanged. No implementation, suite or live smoke was executed by PM.

## Historical disposition and prerequisites

The preceding maintenance attempt was blocked before amendment: no main-owned helper existed and automatic approval reset did not apply to replacement-field amendments. That attempt changed no plan field. Main subsequently supplied notes/verify-task-structured.py and explicitly revoked approval; this dispatch therefore amended an already-pending plan. Main reports its three helper steps are byte-identical extractions and exit zero; those executions were not repeated here.

## Meaning preservation

Only T-01 verify and intent changed in loaded plan data. Structural assertions compared the complete pre/post loaded plan, permitting exactly these two replacements; approval, statuses, lanes, decisions, files, traces and all other fields were equal. BRIEF bytes were equal. No SC changes.

Verify replaced exactly three complete Python heredocs, in order, with:

- python3 .harness/harness/features/BUG-2171-task-structured/notes/verify-task-structured.py port-red-green
- python3 .harness/harness/features/BUG-2171-task-structured/notes/verify-task-structured.py hook-red-green
- python3 .harness/harness/features/BUG-2171-task-structured/notes/verify-task-structured.py append-check

An exact string equality assertion reconstructed this replacement from the current authoritative original verify, proving EVERY non-heredoc byte unchanged, including all existing test commands, shell preamble, QA comment and full credentialled live-smoke command. Final verify SHA-256: 108c4eb1867e43d7c01d847ac45b843b0f9a7e8bc12fdba0d09e4196fcb71bad. Unchanged live-smoke line SHA-256: dc4c49f54f95c096c44215deb690bfc9ec270327a9289302031b9daf83f201a1.

The existing helper remains MAIN-OWNED and was not edited. It is a read-only verification dependency, not a task implementation target; T-01 files remains unchanged. All normative intent, including no re-investigation, intact validator, actual yield traces, append ownership, literal verification, regression fixtures and shipment blocking without live proof, remains verbatim. Only the following settled-cause justification moved here, replaced by a useful reference to this note:

The settled cause is native OMP 18.10.2 task.structured defaulting off while Harness never opted in. Revalidation strips injected outputSchema/schemaMode with that setting off, so the child lacks yield and the existing yield hook is never reached.

The canonical reader proves readable appended bytes, not the writer; the original intent still requires actual child/lead yield calls and hook-triggered append from traces.

## Commands and receipts

From PRODUCT /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured, before and after:

    python3 .claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/BUG-2171-task-structured/plan.yaml

Before: exit 1, T-01 75 machine-field lines, budget 50, 1 violation across 1 plan. After: exit 0, 0 violations across 1 plan. Structural inspection through the same script's _budget_lines function measured exactly 25 final lines (runpy.run_path with run_name budget_inspection, yaml.safe_load of the feature plan, _budget_lines(tasks[0])).

Both replacements used the control-plane interface, capturing stdout:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml --key tasks --id T-01 --field FIELD --show
    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml --key tasks --id T-01 --field FIELD --expect-sha256 SHA_FROM_SHOW --value-file /dev/stdin --reason 'DEC-182 form-only budget trim; main owns unchanged extracted helper'

FIELD was verify, then intent; each SHA was read immediately from --show. Both exited 0 and printed AMENDED tasks:T-01.FIELD judgement=amendment and APPLIED plan.yaml plus APPLIED feature.json. The tool's automatic check-state reported stale review_sha d3792019e74ff266c2414708124512544d1fc9f6 (INV-33), expected pending approval and historical/layout notes. This is not a passing review claim. No APPROVAL-RESET receipt occurred and no GitHub sync was invoked. The feature.json write was a plan-merge side effect, not manual bookkeeping.

PRODUCT AGENTS.md and mapped SPEC section 8.3 plus DEC-182 were consulted; mapped DEC-174/229/237 guidance was already recorded in the prior research. Conventional docs/spec.md, docs/decisions.md and docs/architecture.md remain recorded absent in unchanged intent; no substitute documents were authored. SPEC's string refusal versus the settled JSON-object-string ruling remains explicitly recorded in unchanged intent.

## Touched paths and open questions

Repository: feature plan.yaml; this research note; feature.json (automatic plan-merge side effect). Scratch: /tmp/bug2171-verify.txt (literal replacement input). No helper/source/test/config/BRIEF edits. No open questions. Main must refresh review provenance through its normal approval/review flow; this amendment makes no implementation or SC-outcome claim.
