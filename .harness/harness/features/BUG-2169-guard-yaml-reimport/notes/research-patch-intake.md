# BUG-2169 patch intake assessment

BLUF: Pending signature-ready patch artifacts: BRIEF.md is 53 lines; plan.yaml has one direct bugfix task, seven anchors, five SC traces, zero plan-check failures, status: plan and approval.status: pending. No implementation, reproduction, test, lint, formatter, panel, goal-check or GitHub write ran.

## Scope and sources

- Operator grilling (control plane): .harness/notes/grilling-guard-yaml-reimport-2026-11-07.md, Destination/Settled/Facts I verified, supersedes original diagnosis and comment-1 install tension in https://github.com/mruangutai/harness/issues/2169#issuecomment-6707286655. Facts reused, not re-derived. Baseline c4e8bbc87e858bb2a0320efd766c7036cbcebb8b.
- Product CLAUDE.md → AGENTS.md maps actual SPEC.md section 13 and decision authority under .harness/harness/docs. Missing generic PRODUCT docs/spec.md, docs/decisions.md, docs/architecture.md provide no additional architecture contract; no replacement authored. Control-plane DEC-174 and DEC-225 consulted. Backlog list read; #2171 remains excluded.
- Actual named suite paths are tests/integration/test-dispatch-guard.py, tests/unit/test-lead-start-preflight.py and tests/integration/test-lead-start-return.py. Two requested unit paths do not exist; exact-name glob located integration copies and parent was notified. Seven-file ownership is unchanged in substance. SC evidence uses active unit/integration kinds, not a unit runner that misses integration files.
- Operator/fleet owner, CI and code maintainer judge done; five SCs use unit (2), integration (1), pinned inspection (2). No personal UAT. Single-install fail-first at c4e8bbc8 or explicitly pinned pre-fix state and fixed-pin green must come from harness-2169-repro or CI's image-owned PyYAML, never this Mac. These sources appear in SCs, Verification gaps and T-01 verify.
- No new D-NN: operator settled the approach; warning placement and non-yaml compiled-module handling remain builder choices inside the fixed boundary. No new public interface or unbounded diff. No prototype required for this noninteractive hook patch (operator override available). No panel under DEC-225.

## Principles applied

- Experience First (.agents/skills/harness-craft/references/experience-first.md): refusal guidance must actually clear the isolated-mode failure and disclose Homebrew's risk; convenience of --user advice does not override the fleet owner's working bootstrap.

## Exact command receipts

Root resolution: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/inflight_registry.py feature-root --feature BUG-2169-guard-yaml-reimport returned /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport.

Both apply invocations used this exact command (exit 0 each):

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/plan.yaml --proposal /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/notes/research-patch-proposal.md
```

First stdout:
```text
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/plan.yaml
```

First apply's automatic check-state stderr reported verify beginning with comments was not runnable. Corrected proposal by putting executable suite command first, comments after, then reapplied. Reported apply's invalid-plan/exit-0 inconsistency to xd://report_issue. Second stdout (complete):
```text
REPLACED T-01.verify: "# Execute inside harness-2169-repro (ubuntu:26.04 + python3-yaml) OR CI on the image's own single PyYAML, never use the Mac as the regression source.\n# Preserve named fail-first stdout/stderr and exit statuses at c4e8bbc8 or an explicitly pinned pre-fix state before edits; repeat at fixed review pin. Identify interpreter, yaml path, version, libyaml availability and single-install layout in both receipts.\n# Fixed state: all three commands exit 0, no FAIL cases, focused run under 60 seconds; pre-fix receipts must discriminate the bootstrap/advice defect, not an invocation failure.\npython3 tests/integration/test-dispatch-guard.py && python3 tests/unit/test-lead-start-preflight.py && python3 tests/integration/test-lead-start-return.py\n" -> "python3 tests/integration/test-dispatch-guard.py && python3 tests/unit/test-lead-start-preflight.py && python3 tests/integration/test-lead-start-return.py\n# Execute inside harness-2169-repro (ubuntu:26.04 + python3-yaml) OR CI on the image's own single PyYAML, never use the Mac as the regression source.\n# Preserve named fail-first stdout/stderr and exit statuses at c4e8bbc8 or an explicitly pinned pre-fix state before edits; repeat at fixed review pin. Identify interpreter, yaml path, version, libyaml availability and single-install layout in both receipts.\n# Fixed state: all three commands exit 0, no FAIL cases, focused run under 60 seconds; pre-fix receipts must discriminate the bootstrap/advice defect, not an invocation failure.\n"
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/plan.yaml
```

Neither apply emitted APPROVAL-RESET:; no remote sync invoked. Automatic check-state stderr on corrected apply still reported intentionally unsigned BRIEF, missing github.build_entry (INV-37), and unrelated outside-root archive worktree INV-25/29; it no longer reported malformed plan. These are not a passing repository-state claim and were not repaired outside assignment.

Required explicit check (exit 0):
```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport
```
```text
OK T-01 7 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport: 1 task(s), 7 anchor(s) resolved, 0 failure(s)
```

Line-count command: wc -l /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport/.harness/harness/features/BUG-2169-guard-yaml-reimport/BRIEF.md returned 53. Station result: plan.yaml status: plan, approval.status: pending (controlled apply); feature.json has mission: patch and no station field. No feature.json or STATE.md writes. Open scope questions: none. Next gate is operator signature; later main-session implementation must supply the preserved fail-first and fixed-state evidence, not intake.
