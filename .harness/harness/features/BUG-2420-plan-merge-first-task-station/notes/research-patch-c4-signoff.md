# C4 pre-signature correction — accepted

The bounded text amendment is complete; approval remains pending. No implementation verification was executed.

## Changes and acceptance

- BRIEF.md: only the Verification gaps paragraph changed; SCs, constraints, out-of-scope and approval text were untouched by the single-line edit.
- plan.yaml: control-plane plan-merge.py amend replaced only T-01.intent and T-01.verify using each field's --show compare-and-swap hash. Both calls exited 0 and printed AMENDED followed by APPLIED. Neither printed APPROVAL-RESET:, so no remote sync was invoked.
- Parsed before/after plan comparison asserted exact equality after substituting only those two intended values. This preserves files, lanes, top-level status: plan, approval.status: pending, T-01.status: ready, main-session-direct, all other task fields and any rework data.
- Both artifacts now point to PRODUCT-relative .harness/harness/docs/SPEC.md and .harness/harness/docs/DECISIONS.md. Consulted SPEC.md §2.2–2.3 and DEC-120, DEC-174 and DEC-225 in this feature checkout. Settled intake remains binding.
- Acceptance assertions found neither the removed environment variable identifier nor any of the three false lower-case product-document paths in either artifact. The verify still contains the exact adjacent checkout cd and unset HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE lines. Its export line alone was removed; intent isolation credit for that variable was removed.
- Amendment post-write diagnostics reported unsigned BRIEF, unrelated standing-worktree INV-29, missing Build-entry receipt INV-37, pending approval and historical-cycle/layout notes; both amendments nevertheless returned 0. These diagnostics were not treated as implementation evidence or repaired outside scope.

## adequacy_notes

The authorized acceptance check passed with exit status 0. Exact command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station
```

Exact stdout:

```text
OK T-01 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station: 1 task(s), 3 anchor(s) resolved, 0 failure(s)
```

Exact stderr: empty (zero bytes). Exit status: 0.

This proves amendment shape, anchors and protected-field preservation only, not the future implementation. No builds, tests, linters, formatters, literal T-01 verify, readers, panel, goal-check or signature were run. Open questions: none.
