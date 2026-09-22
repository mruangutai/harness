# QA c3 — pinned matrix regate

**PASS.** The exact range `066638e8acf68b47e74637006a01c8823cff939c..f798e2e600ed08aeb49d61a3a229a626750a9ccb` was reviewed; no merge-base or `HEAD` substitution was used. `git diff --name-status` measured 75 changed paths in that range.

## Phase 1 expectations and matrix

- SC-01, SC-03, SC-05, SC-06, and SC-07 require integration coverage; SC-02 and SC-04 require unit coverage, with SC-04 also integration-covered because T-04 removes configuration keys (a config-shape change).
- T-01, T-02, and T-03 are correctly recorded as `cross_module`; each requires `unit` and `integration` (`plan.yaml:157,184,214`; `.harness/harness.json:174-178`). T-04's `config` predicate requires integration when configuration shape changes (`.harness/harness.json:226-233`). T-05 is `docs` and has no matrix floor.
- Both required active kinds passed: `unit` (41 files) and `integration` (68 files). No locally-run detect surface was changed.

## Signed verify chains

All exit 0 at the review pin:

1. T-01: `python3 tests/unit/test-factory-config.py && python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/unit/test-harness-boundary.py`
2. T-02: `python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-board-lifecycle.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/unit/test-gh-board.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/integration/test-gh-sync-record.py`
3. T-03: `python3 tests/integration/test-check-state-feat59.py && python3 tests/integration/test-check-domain.py && python3 tests/integration/test-check-domain-worktree.py && python3 tests/integration/test-bash-write-guard.py`
4. T-04: `python3 tests/unit/test-gate-policy.py && python3 tests/integration/test-validate-digest.py`
5. T-05: `python3 tests/integration/test-check-plan-routes.py && .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`

## SC evidence

- SC-01: byte-identical lifecycle receipt test, `tests/integration/test-check-plan-routes.py:2403-2421`.
- SC-02: ordered table, derived exports, and strict predicates, `tests/unit/test-factory-config.py:547-608`.
- SC-03: rejected review completion, non-work-started terminal cases, and invalid-status refusal, `tests/integration/test-plan-merge.py:3342-3389`.
- SC-04: review-only policy plus ignored legacy inputs and loud invalid/missing review, `tests/unit/test-gate-policy.py:59-92`.
- SC-05: tool and Bash route adapters retain their own byte-exact channels and absorb injected core failure, `tests/integration/test-check-domain-worktree.py:751-814`; `tests/integration/test-bash-write-guard.py:1036-1107`.
- SC-06: strict decoding and natural schema errors, `tests/unit/test-artifact-accessors.py:155-210`; loader/registration and gate outcomes, `tests/integration/test-check-state-feat59.py:520-544`.
- SC-07: clean-tree and independent station/loader mutants, `tests/integration/test-check-plan-routes.py:2477-2510`.
- SC-08 inspection: pin-visible reciprocal five-file comments at `.claude/skills/harness/bin/{branch-create-gate,gh-close-gate,merge-gate,plan-sign-gate,run-unit-tests}.py:46-49,39-42,39-42,65-68,41-44`; `DEC-234` and glossary lifecycle definitions are present at `.harness/harness/docs/DECISIONS.md` (DEC-234) and `.harness/glossary.md:35-45`.

## Fail-first evidence

The baseline-overlay receipts name a non-zero baseline run for every automated SC: SC-01/SC-07 `notes/fail-first-receipts.md:120-141`; SC-02 `:5-20`; SC-03 `:61-78`; SC-04 `:80-97`; SC-05 `:99-118`; SC-06 `:22-60`.

```yaml
VERDICT: PASS
DIGEST:
  headline: Exact pinned-range matrix and all five signed verify chains pass; every automated SC has recorded fail-first evidence.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 41 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 68 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-plan-routes.py:2403-2421" }
    - { id: SC-02, test: "tests/unit/test-factory-config.py:547-608" }
    - { id: SC-03, test: "tests/integration/test-plan-merge.py:3342-3389" }
    - { id: SC-04, test: "tests/unit/test-gate-policy.py:59-92" }
    - { id: SC-05, test: "tests/integration/test-check-domain-worktree.py:751-814; tests/integration/test-bash-write-guard.py:1036-1107" }
    - { id: SC-06, test: "tests/unit/test-artifact-accessors.py:155-210; tests/integration/test-check-state-feat59.py:520-544" }
    - { id: SC-07, test: "tests/integration/test-check-plan-routes.py:2477-2510" }
  fail_first:
    - { sc: SC-01, evidence: "notes/fail-first-receipts.md:120-141" }
    - { sc: SC-02, evidence: "notes/fail-first-receipts.md:5-20" }
    - { sc: SC-03, evidence: "notes/fail-first-receipts.md:61-78" }
    - { sc: SC-04, evidence: "notes/fail-first-receipts.md:80-97" }
    - { sc: SC-05, evidence: "notes/fail-first-receipts.md:99-118" }
    - { sc: SC-06, evidence: "notes/fail-first-receipts.md:22-60" }
    - { sc: SC-07, evidence: "notes/fail-first-receipts.md:120-141" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-61-control-plane-consolidation/.harness/harness/features/FEAT-61-control-plane-consolidation/notes/review-harness-qa-c3.md
```
