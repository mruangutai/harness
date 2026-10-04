# BUG-1898 goal-check — validate c3

## BLUF

**PASS for the read-only validation panel** at immutable pin `6bfc21e3ccdf78eb86cdd0eb250067348d887096`. F-QA-01 is closed: the permanent mutation oracle now accepts only the complete set of two required `FAIL  [bug1898]` labels, rejects a singleton and a required-label replacement, and ignores the four unrelated unprefixed schema failures without letting them satisfy or spoil the oracle. F-01 and F-02 remain closed; SC-01 through SC-06 and SC-08 are met. SC-07 remains `pending_operator_gate`, requires the operator's credentialled live probe before merge, and is not a panel failure. No live receipt is claimed or fabricated.

## Provenance and scope

- Reviewed pin: `6bfc21e3ccdf78eb86cdd0eb250067348d887096`, matching `feature.json review_sha`.
- Canonical merge-base: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`; reviewed range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (47 changed paths).
- Focused c3 range: `4942950a83c1895d85922f7cd9e9cfd41e28daf8..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (9 changed paths). Its only executable change is `tests/integration/test-suite-claim-preservation.py`; the other eight paths are feature state and c2 validation records. No production, unit-test, lifecycle-integration-test, decision, config, or checklist code changed after c2.
- Required authorities read: `BRIEF.md`, `plan.yaml` T-03/T-04, `feature.json`, and `runs/validate-c2-validator/digest.md`.
- Pinned execution used `git archive` into an owned temporary directory. No scratch worktree was created; no live OMP, formatter, linter, unrelated build, or unrelated suite ran.
- QA independently ran the configured gates at the same pin: unit exit 0 with 42/42 named files PASS, integration exit 0 with 70/70 named files PASS, and the focused wrapper exit 0 (`notes/review-harness-qa-c3.md:5-22`).

## Perspective grades — exactly one line each

- **partial — operator** — SC-01 is now met and no automated/suite path releases an unrelated seeded claim; SC-07 alone remains the explicit credentialled operator merge gate.
- **pass — orchestrator** — SC-02, SC-04, and SC-06 remain met: c3 changes no lifecycle code or carrying tests, while pinned exact-id run-start, wake/reclaim, mixed-result reconciliation, held-child refusal, settlement, and exact recovery evidence remains intact.
- **pass — code maintainer** — SC-03 and SC-05 remain met; the focused c3 delta changes only the mutation wrapper, leaving the canonical resolver, one-PM/non-PM concurrency rules, DEC-100 pass-through, `pi.events` subscription, and F-02's graded production split unchanged.
- **pass — reader** — SC-08 remains met by pinned DEC-100/DEC-204/index/checklist inspection, with the live-probe note truthfully recording that SC-07 has no receipt yet.

## Success-criterion adjudication

| SC | Status | Method | Pinned evidence |
|---|---|---|---|
| SC-01 | met | automated | The archived-pin wrapper exited 0 with four PASS rows and `0 failure(s)`: all governed-persona sentinels were seeded, the pinned real validator suite passed, every unrelated claim remained byte-identical, and the persona-wide-release mutant reddened exactly the two parent-settlement checks. The green arm is `tests/integration/test-suite-claim-preservation.py:69-104`; exact expected labels and equality are at `:32-39,107-119`; missing identity, occurrence-1 QA/PM preservation, and exact worktree release remain at `tests/integration/test-validate-digest.py:5712-5783`. |
| SC-02 | met | automated | The focused c3 delta does not touch source or unit cases. The current pin retains exact claim-before-write, wake/reclaim, refusal cause/retryability, BLOCKED-only yield, and settlement cases at `tests/unit/omp-hooks.test.ts:1875-2001`; QA's current-pin configured unit gate passed 42/42 (`notes/review-harness-qa-c3.md:5-10,29`). |
| SC-03 | met | automated | The current pin retains run-start reuse/bind, legal non-PM multi-flight, one-PM retry, unreadable refusal, linked-root lookup, and exact resolver cases at `tests/integration/test-inflight-registry.py:1238-1418`; QA's current-pin configured integration gate passed 70/70 (`notes/review-harness-qa-c3.md:5-10,30`). |
| SC-04 | met | automated | The current pin retains actual-id mixed/reordered results, repeated/suffixed ids, never-started receipt rollback, and background settlement cases at `tests/unit/omp-hooks.test.ts:2003-2113`; QA's current-pin configured unit gate passed 42/42 (`notes/review-harness-qa-c3.md:9,31`). |
| SC-05 | met | automated | The wrong-bus mutant still requires failure while naming `pi.events` at `tests/integration/test-check-omp-port.py:194-214`; production subscribes through `pi.events` at `.omp/extensions/harness-hooks.ts:1314-1321`; QA's current-pin integration gate passed 70/70 (`notes/review-harness-qa-c3.md:10,32`). |
| SC-06 | met | automated | Strict reads precede held-child refusal and exact release at `.claude/skills/harness/bin/validate-digest.py:2233-2349`; exact held-child/recovery, post-settlement release, unreadable-parent, BLOCKED escape, leaf, and byte-preservation assertions remain at `tests/integration/test-validate-digest.py:5769-5889`. QA's current-pin integration gate passed 70/70, and the c3 mutant run specifically exercised the two post-settlement checks (`notes/review-harness-qa-c3.md:10-22,33`). |
| SC-07 | pending_operator_gate | uat | Pinned `notes/live-omp-probe.md:1-43` says “no live run recorded” and that dry-run output is not a receipt. The operator must run the credentialled live probe successfully from this feature worktree before merge. Its absence is not a panel failure, and no receipt is fabricated here. |
| SC-08 | met | inspection | Pinned DEC-100 preserves guard-crash pass-through plus child self-refusal (`DECISIONS.md:1373-1377`); DEC-204 records exact run-start identity and canonical-root/id-keyed release (`:6361-6438`); `notes/ship-checklist.md:13-116` requires a live PASS before merge, exact evidence per cutover row, individual release, re-enumeration, and non-gating post-merge follow-up. |

## F-QA-01 independent re-derivation

The c3 source defines `PERSONA_RELEASE_REDS` as exactly:

1. `after the child settles the identical yield passes`
2. `and releases only the parent`

The wrapper extracts only complete lines beginning with `FAIL  [bug1898] ` and requires both `code != 0` and exact set equality (`test-suite-claim-preservation.py:32-39,113-119`). In the archived pin, the real mutant run satisfied that predicate and the wrapper exited 0.

A separate read-only control evaluated the pinned extractor and constant against synthetic child-output rows:

- complete two-label set: accepted;
- only one required label: rejected;
- one required label replaced by a different `[bug1898]` label: rejected;
- all four unrelated schema failures without the prefix: extracted as the empty set;
- complete required set plus those four unprefixed failures: accepted unchanged.

The four unrelated relocated-copy failures are the c2-observed `drifted key spelling is caught`, `enum near-miss is caught, not normalized`, `code reviewer omission of code_grade is rejected`, and `code_grade's missing-field hint names the four legal values, not the list wording` (`notes/review-harness-qa-c2-r1.md:19-28`). Their lines begin `FAIL  `, not `FAIL  [bug1898] `, so they neither satisfy nor spoil the complete-set oracle. The concrete F-QA-01 failure scenario—one incidental target label or a changed target label amid those unrelated reds—now makes `reddened != PERSONA_RELEASE_REDS`; the permanent wrapper fails. **Disposition: closed** (`owner: T-03/T-04`; `kind: substance`; prior `severity: high`; `reader: harness-qa + harness-pm`).

## Prior findings and must-fix disposition

- **F-01 — closed, no regression.** Concrete scenario: an unreadable canonical registry lets a dispatch-capable parent return while a child may remain live, or a release rewrite destroys unreadable bytes. Owner task: T-03; kind: substance; severity: high; reader: harness-code-reviewer + harness-security-reviewer + harness-qa. At the pin, `_settle_in` performs strict own/child reads before either refusal or `_release_own`, and the focused c3 delta touches neither source nor these tests (`validate-digest.py:2290-2349`; `test-validate-digest.py:5850-5877`).
- **F-02 — closed, no regression.** Concrete scenario: concentrated settlement branching permits a later release-before-refusal change. Owner task: T-03; kind: substance; severity: high; reader: harness-code-reviewer + harness-qa. The c2 canonical grades remain `_registry_errand` 4, `_settle_in` 5, `_release_own` 5 (`notes/review-harness-code-reviewer-c2.md:20-30`), and c3 changes no production function.
- **F-QA-01 — closed.** Concrete scenario: one incidental or substituted `[bug1898]` failure is accepted while either intended parent-settlement failure is absent. Owner tasks: T-03/T-04; kind: substance; severity: high; reader: harness-qa + harness-pm. Exact set equality and both negative controls now reject that scenario.
- **Must-fix: none.** No active finding remains. SC-07 is remaining operator action, not a panel must-fix.

## Scratch cleanup

The owned archive directory `/tmp/bug1898-pm-c3.JEXRrX` was removed and confirmed absent. The wrapper removed its own temporary copied-bin directory. No scratch worktree was created, and the assigned feature worktree was not removed or otherwise modified except for this required namespaced note.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-QA-01 closes at 6bfc21e3: the exact full-set oracle and both negative controls discriminate correctly; F-01/F-02 remain closed, and SC-07 alone remains the operator merge gate."
  feasibility: clear
  surface: L
  flags: [mutation-oracle, exact-identity, lifecycle, operator-merge-gate]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: low
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "Current-pin QA and PM wrapper runs exited 0; exact two-label equality accepted, singleton and substituted-label controls rejected, unprefixed schema failures excluded" }
    - { id: SC-02, verdict: met, method: automated, evidence: "Current-pin QA unit 42/42; exact run-start, reclaim, held-run and settlement cases" }
    - { id: SC-03, verdict: met, method: automated, evidence: "Current-pin QA integration 70/70; canonical-root, one-PM, legal non-PM concurrency, unreadable refusal and DEC-100 cases" }
    - { id: SC-04, verdict: met, method: automated, evidence: "Current-pin QA unit 42/42; actual-id reordered results, receipt rollback, repeated/suffixed id cases" }
    - { id: SC-05, verdict: met, method: automated, evidence: "Current-pin QA integration 70/70; wrong-bus mutant rejects pi.on and requires pi.events" }
    - { id: SC-06, verdict: met, method: automated, evidence: "Current-pin QA integration 70/70; strict-read, held-child, exact recovery/release and unreadable no-write cases; c3 mutant exercised both post-settlement assertions" }
    - { id: SC-07, verdict: pending_operator_gate, method: uat, evidence: "Pinned live-omp-probe.md records no live run; credentialled operator PASS still required before merge and no receipt fabricated" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "Pinned DEC-100, DEC-204, generated index and ship checklist preserve current lifecycle, exact cutover, and non-gating follow-up truth" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c3.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c3.md
```
