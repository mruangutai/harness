# BUG-2349 — premerge goalcheck c1

PASS — all assigned premerge outcomes and five advisor conditions are met. SC-04's postmerge receipt remains main's outstanding ship obligation; full-lifecycle completion is not claimed.

Review: e239d88156c508c948d49cd31238ea13b3b39865 → 0174f364483df5c8d49f04e35d2308e5dca33257. HEAD and live feature.json review_sha match the assigned pin. The feature.json committed at that pin retains the previous c0 review_sha; it is not the current dispatch registration. BRIEF, plan, implementation, tests, amendment ledger and build receipts were read at the pin. PM ran no tests, gates, builds, lint or formatting. Evidence paths below are feature-relative unless repository-rooted.

## Perspective coverage

- operator — met premerge: SC-01 independently covers decisions/tasks additions and reload; SC-04 adds a fresh scratch-repository proof at the exact pin (notes/review-harness-qa-c1.md:18,33,36). The merged-tool proof remains outstanding.
- code maintainer — met: SC-02 retains exit-5 alignment refusal; SC-03 retains the bounded selector and amended three-file scope (notes/review-harness-code-reviewer-c0.md:9-11; notes/review-harness-qa-c1.md:3,23,35).

## SC outcomes

- SC-01 — met, automated: tests/integration/test-plan-merge.py case_2349_inline_empty_decisions_gains_items and case_2349_inline_empty_tasks_gains_items assert exit 0 and complete reloaded items. QA identifies these tests and exact-pin green at notes/review-harness-qa-c1.md:17-18,33. Original natural red: notes/receipts/sc01-sc02-red.txt:681-707 (both applies and reloads fail); unit base-red reproduction is additionally commit-bound (QA:24).
- SC-02 — met, automated: case_2349_nonempty_flow_base_still_refused asserts exit 5, alignment message and unchanged bytes. Exact-pin green: QA:17,34; committed green notes/receipts/c1-verify-green-prefix.txt:685-686. This preservation control already passed on the base (red receipt:709-710); it is not misrepresented as a newly failing assertion or a performed refusal mutation.
- SC-03 — met, inspection under the authorized amendment: pinned .claude/skills/harness/bin/plan_merge/union.py:511-521 selects the proposal head for empty base ranges plus nonempty proposal ranges, retaining the other precedence. _aligned_items:494-508 is unchanged. C0 review:9-11 supplies inspection evidence; comparison confirms production and integration bytes unchanged since c0. The cumulative implementation/test diff is exactly union.py, tests/integration/test-plan-merge.py and tests/unit/test-plan-merge-union-head.py. The ledgered T-01.files/verify amendment supersedes the old two-file wording in SC-03/constraints/intent; that settled authority change is not a new scope failure.
- SC-04 — met for premerge only, automated: QA:18,20,36 records the literal T-01 verify at 0174f364, explicit BUG2349_TOOL_ROOT, rc 0 and scratch reload {'decisions': [{'id': 'D-01', 'choice': 'x'}]}. The committed c1 receipt:1-2,698-701 is earlier working-tree evidence, not falsely labeled execution at this pin. Postmerge verification remains ungraded here.

## Advisor conditions — individually verified

1. Exact scope — met: c0-to-c1 implementation/test delta adds only tests/unit/test-plan-merge-union-head.py; no further production delta. Pinned T-01.files and verify include it; feature.json judgements ledger both authorized amendments.
2. Commit-bound red and pinned green — met: base union.py SHA-256 is 2d595c8186b32802a144e369c3dc5e4fb6a892e4581357b2bfbd6586ab35bb3d, matching notes/receipts/unit-red-base.txt:2. QA:18,24 independently reproduces six failures against that source and nine passing assertions at the exact review pin.
3. Fixed rule only — met: unit cases at :53-76 cover both inline-empty keys plus the existing-item base-head control. No dismissed neighbor variants were added.
4. No waiver — met: notes/unit-floor-c1.md:11 and QA:16,26 explicitly retain the unit requirement; the newly discovered unit test satisfies it. No integration-as-unit exception or systemic #2293 work is inferred.
5. Ship obligation unchanged — met: pinned T-01.intent and QA:27,36 retain main's postmerge run with the surviving merged owner checkout and explicit BUG2349_TOOL_ROOT.

## Decision dispositions, limits and next action

Pinned plan.yaml declares decisions: [] and decisions_affected: []; there are no amend/strike rows to grade or decision-document remediation tasks. T-01 traces all four SCs and owns all three amended implementation/test paths. No premerge must-fix or open question.

Main must preserve a second literal-verify receipt after merge: merged tool SHA, explicit surviving owner-root override, command, stdout/stderr, exit status and scratch reload. This is an outstanding ship obligation, not a premerge failure. Product guidance /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union/docs/{spec,decisions,architecture}.md is absent in the assigned checkout and at the pin; no contents or substitute product guidance were invented.
