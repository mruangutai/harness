# BRIEF — FEAT-2398 QA test-kind status

## Problem

QA and validate-digest.py currently infer exclusions from a null cmd and read Harness policy even for fleet-product features. An operator can therefore receive an accepted QA report that silently skips required unresolved coverage or applies another repository's matrix (issue mruangutai/harness#2398; grilling facts at 9eb07b4f3cd235c234a10edddbfe5542c1e85fba).

## Done when — by perspective

**operator** — I can rely on a required undecided or unusable runner blocking QA rather than being excused or omitted. A refusal tells me the two legitimate repairs, and disclosing a verification gap does not grant a waiver.

**reader** — I judge the repository and commit actually under review, including its test matrix and kind statuses. Conditional requirements remain QA's judgment rather than silently becoming unconditional or being mechanically guessed.

**code maintainer** — I have one consistent QA policy across the validator, QA instructions and adopted decision record, with regression evidence distinguishing the former false acceptance from the corrected behavior.

## Success criteria

- SC-01 (operator): For each required kind with status unresolved, and separately active with cmd null, validation accepts only state misconfigured with VERDICT BLOCKED. Independently refuse satisfied, not_applicable, missing, locally_run and omission, including non-PASS reports; every such refusal names a verified runner becoming active and a signed exclusion with status excluded, excluded_because and signed: DEC-NNN. QA demonstrates the failing pre-fix behavior first for each newly enforced branch.
  verify: automated evidence: integration
- SC-02 (operator): Only explicitly excluded kinds with the signed exclusion record may soft-skip or leave the required set; a locally_run report is accepted only for a configured locally_run kind. Preserve valid active/satisfied, excluded/not_applicable and locally_run controls, and prove that a BRIEF Verification gaps disclosure changes none of these outcomes. QA demonstrates the failing pre-fix behavior first for the newly enforced branches.
  verify: automated evidence: integration
- SC-03 (reader): A fleet-product feature loads test_kinds and test_matrix from that product's code repository at its authoritative review pin, not from the Harness planning tree, dirty code checkout or remote default branch. Harness features use the same pinned-policy path and refuse an absent pin, not the former current-tree policy. Disagreeing pins, an invalid binding, unavailable commit and missing/invalid pinned config refuse explicitly without fallback. Two-repository/two-commit fixtures prove both policy tables select the pinned product policy; QA demonstrates the failing pre-fix behavior first.
  verify: automated evidence: integration
- SC-04 (reader): Policy checks on every reported kind apply under every verdict. For the started tasks' always floor, unresolved and active/null omissions refuse under every verdict regardless of matrix_ok; the full satisfied-kind floor remains required only for PASS with matrix_ok true. Otherwise contract-valid early BLOCKED and FAIL reports may omit configured runnable or locally_run kinds without inventing not-yet-run states or treating omission as exclusion. Mixed-floor controls accept BLOCKED with only its unresolved or active/null kind reported as misconfigured and refuse omission of that same kind; controls retain the full PASS floor, omitted-conditional latitude and conservative all-excluded no-kind exemption. The validator does not compute when predicates; a reported unresolved conditional must be misconfigured/BLOCKED. QA demonstrates the failing pre-fix behavior first for new refusals.
  verify: automated evidence: integration
- SC-05 (code maintainer): At git show <review_sha>:<path>, the changed validator, QA rules skill, SPEC and decision record state the same status/pin/conditional contract; DEC-256's default-branch-only clause is replaced with the QA review-pin exception while non-QA product_config consumers remain default-branch based. DEC-187 records the accepted Kaya BLOCKED consequence; the changed instructions explicitly say INV-49 is disclosure only and explain the two repairs. Inspection cites each owned file and the regenerated DECISIONS-INDEX.md at the pin.
  verify: inspection

## Verification gaps

No required automated criterion rests on a null or excluded kind: SC-01–SC-04 use the active integration runner whose detect includes tests/integration/test-validate-digest.py; the cross_module task also retains the active unit floor for final QA. Harness component and ui remain unresolved, but this feature changes no browser/component surface and makes no UI claim. Functional and eval are signed exclusions under DEC-187, not evidence for these SCs. SC-05 is pinned-content inspection; it does not prove agent conduct or live Kaya runner availability. Kaya's unresolved runners remain a genuine BLOCKED condition, not covered or unblocked by this disclosure.

## Constraints

- DEC-174 BLOCKS team execution of this gate and its tests; execution is main-session-direct in the assigned feature worktree. Planning remains self-hosted. No UI prototype is required because no end-user interaction is introduced; the operator may override this scope decision.
- DEC-187 SUPPLIES the per-project matrix/status policy and signed-exclusion mechanism; null cmd and unresolved never imply exclusion. Kaya features requiring one of its unresolved kinds will become BLOCKED until verified runners or signed exclusions exist. This accepted consequence is plan D-03, not runner work in this feature.
- DEC-212 and DEC-35 SUPPLY QA-judged when predicates and the always floor. D-02 retains the complete satisfied floor at PASS/matrix_ok true, adds only unresolved/active-null omission refusal to other verdicts, and checks every reported kind; it authorizes no predicate evaluator, not-yet-run state or new digest field.
- DEC-256 SUPPLIES load_harness_json and schema-v3 validation. D-01 proposes one review-pin QA policy path for both fleet products and unbound Harness features, with no current-tree compatibility fallback; factory_config.product_config and board/mirror/fleet reads remain default-branch based, as does DEC-221's onboarding routing. Proposed signature cost: migrate affected fixtures in the owned validator integration test to real Git commits and trusted feature/pin bindings while preserving their assertions; runtime adds local commit/blob reads and one config validation per QA return, no network lookup. Compatibility impact: unpinned Harness QA reports that previously used current-tree policy now refuse until a trusted review pin exists; this feature does not bulk-backfill historical records.
- Product checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no guidance is invented or authored there. AGENTS.md identifies the existing specification at .harness/harness/docs/SPEC.md and decision authority at .harness/harness/docs/DECISIONS.md; those existing surfaces govern this Harness change.
- Preserve the pending signature, source_issues [2398] and plan station. No builds, lint, tests or formatters run during this planning task; only the assigned plan-merge check runs.

## Out of scope

- code_grade.py — unresolved-kind files already stay at the conservative production bar.
- INV-49 / check_state/brief.py — its planning-time null-cmd gap disclosure is already correct and never unblocks QA.
- Giving Kaya runners or exclusions — Kaya #7 owns that work.
- Backlog #2400–#2404 from FEAT-2297 — separate work, including the ran-and-red QA state in #2403.
- UI work — no new end-user interaction is introduced.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-23
