# Goalcheck — BUG-2294 — validate c1

PASS. Both perspectives are discharged; SC-01–SC-03 and the sole amend disposition are met. No findings or open questions.

Review pin: `70981edd6f9f110965a0148b4490ed2673d262dc`; baseline: `c1724230c4d931ad46d433c8ba93df8cf312f898`. Product paths below refer to committed files at this pin, inspected with git show/diff. T-01 owns all five changed product files and traces all three SCs.

## Perspectives

- **operator — pass:** SC-01 preserves every run record while removing only obsolete UI; QA's passing `dry_run_cases`, `retention_cases` and `explicit_keep_cases` cover bytes, retained UI, absent UI and repetition (`tests/unit/test-prune-run-evidence.py:100-135`). Compatibility is additionally inspected under SC-03: selectors/refusals and ship invocations are unchanged (`notes/review-harness-code-reviewer-c1.md:11`).
- **code maintainer — pass:** SC-02's `blocked_no_ui_cases` exercises ten hash-bound digests, final BLOCKED, no UI and empty keep; clean-before/after INV-7 and each recorded hash are asserted (`tests/unit/test-prune-run-evidence.py:138-194`). SC-03 aligns the pinned pruner, ship prose and DEC-238/index with actual UI-only retention (`notes/review-harness-code-reviewer-c1.md:11`).

## SC outcomes

- **SC-01 — met, automated:** QA DIGEST reports the literal T-01 verify exiting 0, 20 PASS/0 FAIL, and the unit-kind runner passing with this file included (`notes/review-harness-qa-c1.md:11-18`). Assertions at test lines 105-108, 115-123 and 133-135 cover every clause. QA independently reproduced destructive-scope failures against the exact base pruner, not a setup error.
- **SC-02 — met, automated:** QA independently reproduced loss of all ten digests and post-prune cycle-evidence violations on the base; fixture clean-before and empty-keep exit-0 preconditions passed. The same tests pass at the review pin (`notes/review-harness-qa-c1.md:13-19`; test assertions at 186-194). The settled `--only INV-7` scope is retained.
- **SC-03 — met, inspection:** Reviewer cites unchanged pruner selectors/CLI/refusals at `.claude/skills/harness/bin/prune-run-evidence.py:47-115,134-145`, unchanged ship placement/invocations at `.omp/commands/harness-ship.md:38-54`, and bounded DEC-238 amendment/index regeneration metadata (`notes/review-harness-code-reviewer-c1.md:11`). Direct pinned diff corroborates that only destructive scope and matching prose changed.

## Decision disposition

- **DEC-238 — met, inspection.** Plan row identity: amend; clause “it deletes engineering, product, reconciliation and distill run directories”; successor D-01; reason UI-only removal with unchanged keep/refusal policy. `git show 70981edd6f9f110965a0148b4490ed2673d262dc:.harness/harness/docs/DECISIONS.md` lines 7993-7996 replace that clause with removal of only `runs/<id>/ui/`, explicitly protect the run directory, digest.md, state.yaml and .run-identity.json, and give the #2177 cycle-evidence rationale. Baseline diff leaves Abandon/INV-51 (7986-7989), keep selection and refusal policy unchanged; the pinned index records coupled metadata updates at 232-237. Owning task: T-01. Five keep rows are not graded; no strike rows exist.

## Evidence discipline

No tests/builds/linters/formatters were run by pm. Automated verdicts consume QA's terminal DIGEST and durable note; inspection consumes the reviewer note and pinned contents. Pinned subject/test SHA-256 values match `notes/red-first-T-01.md` exactly (fixed pruner d3f2c38e…32fe9; test f6cfe5ea…ad0b; base pruner cd58e0b9…8c0). Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent; no Harness document was substituted as product guidance.
