# Verifier-order correction receipt

T-01.verify alone was amended by the authorized compare-and-swap verb; task completion now uses the five static checks, with independent review and all 27 live assertions retained after build. No task execution, signature, production edits or verification commands were run. cycles_used: 0. Authorization: notes/answers-verification-order-2026-10-05.md; acceptance: runs/correction-verify-product/digest.md. Open questions: none. Main retains the operator-authorized re-sign step.

## Shown original

Shown sha256: 7ab4196040070d3d8bba3cdae6f6c7bb247207098c972a3e044c9b415cfb42b2. Full --show stdout was captured at artifact://5 and cross-checked against the assignment's original verifier and original plan bytes; they agree. The original verifier was never executed.

## Exact amended text

```text
Task build verification is the static checks below, run from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance after the four guidance edits.
Expected: exit 0, no structural errors or suite FAILs; preload-weight NOTE is advisory and recorded; static results are not behavioural proof.
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-weight.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-refs.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 .agents/skills/harness/bin/check-instruction-paths.py
python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit
python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration
Independent reviewer reads all four files at review_sha (SC-04), and live notes/uat-product-document-guidance-c0.md U-01 through U-04 with all 27 assertions, operator alone recording passed, and not run at intake remain feature acceptance gates AFTER build and NOT prerequisites of task completion.
```

Value file: notes/research-correction-verify-value.md. Applied with --key tasks --id T-01 --field verify --expect-sha256 7ab4196040070d3d8bba3cdae6f6c7bb247207098c972a3e044c9b415cfb42b2 and reason: Operator 2026-10-05 verification-order ruling: build verify is the five static checks; SC-04 review and 27-assertion UAT stay post-build feature gates.

## Verbatim amend output

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.harness/harness/features/FEAT-2037-product-document-guidance/feature.json:
  note       INV-32: FEAT-2037-product-document-guidance is a patch mission, which runs no pre-build panel; its diff is graded by the validate run instead. Not graded.
  note       INV-17 FEAT-2037-product-document-guidance: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan.
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the CI blocker, and what fixing it uncovered', '## Carried forward'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
AMENDED tasks:T-01.verify judgement=amendment
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.harness/harness/features/FEAT-2037-product-document-guidance/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.harness/harness/features/FEAT-2037-product-document-guidance/feature.json
```

The verb succeeded. It emitted no APPROVAL-RESET: receipt; no gh-sync was invoked. Approval bytes remain exactly date '2026-10-05', approved_by operator, status approved; no approval was authored or signed here. The canonical verb appended only its amendment judgment to feature.json; removing that single judgment and serializing in the existing format reproduces the baseline feature.json hash exactly.

## Preservation evidence

Before/after byte hashing used only the explicit comparison authorization. plan.yaml with only the approval block and verify literal body replaced by stable markers had identical SHA-256 dad10f61f87cdcef50d6fcabf8e04926df61db1eea3d4a7f92331a470dea3df2. Approval bytes were separately identical. Thus every other plan byte is preserved, including all other T-01 fields, literal intent with PRODUCT-root consultation and real nested dispatch requirements, files, traces, routing, change_type, task status ready, plan status building, lanes, decisions and source issues. Decoded amended verify bytes equal the value-file bytes exactly; all five command lines match the originals.

Matching before/after SHA-256 values:

- BRIEF.md: 82ec69c5226fd2fab8db7109516bdff190ea6ccc7eef1f26fef329f86a03d908 — all SCs unchanged.
- notes/uat-product-document-guidance-c0.md: 942b2b536e42372e9ed8e8b888ecfa9f24d862a8dda8edfddeaebb97bdf77cb6 — status draft; execution NOT RUN YET; exactly 27 letter-suffixed assertions and 27 NOT RUN YET results.
- .claude/skills/harness-principles/SKILL.md: ff4fbd534a68beaa3f81e7d2facd016a2a907c62ff7388ce160b235326c97a34.
- .claude/skills/harness-spec-driven/SKILL.md: d27c8aafa3ec499f2eb422598697d271c8a0066b60c799ccf99654a947cbd975.
- .claude/skills/harness-zero-micro-management/SKILL.md: cdd6da0b2eeb017d46f80912f0fa55efb00ae84e81778c070edd02256fad5b91.
- .harness/harness/docs/SPEC.md: 6c923d10f934a2dfdcb0969f6babc13e7aad0e0ca5dde23f0e6f5abb3daf630a.

feature.json baseline SHA-256: 2d204fabee1b7e89e52fedbf73f4dd083154ad8ebe57be7c0304ca6375bd7a8d; after canonical judgment append: ed037b48cf790e924b96d961a8b942e01059816c3386fc9256280346ca2b4bef. Removing that judgment restores the baseline hash; all other metadata therefore remains byte-equivalent, including github.build_entry opened, signed_task_hashes, rework ruling and cycles_used 0. No tests, hooks or schemas were touched. No checks, builds, lint, tests, formatters, evals, commits, review pins or PR operations were executed; check-state output above was internally produced by the required amendment verb.
