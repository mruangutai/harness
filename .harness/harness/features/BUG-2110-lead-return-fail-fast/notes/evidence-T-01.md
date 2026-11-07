# BUG-2110 T-01 — fail-first receipt

- Baseline pin: `63cac11a` (resolved `63cac11a3216aa8d34792665a05fcb185f7cf73b`)
- Recorded: 2026-10-07T12:42:29+00:00
- Procedure: disposable `/tmp/BUG-2110-fail-first-evidence.py --baseline 63cac11a` (removed after this receipt; never committed)
- Subjects: production bin tree extracted with `git archive` from the pin into a private temporary tree; current test files and `.omp/agents` persona fixtures copied beside it.
- Overall: **VALID** (procedure exit 0)

## Historical subjects

| file | sha256 at pin |
|---|---|
| `.claude/skills/harness/bin/dispatch-guard.py` | `2ae6fd1c6e9ea093` |
| `.claude/skills/harness/bin/digest_destination.py` | `2e23fec9bdbc559d` |
| `.claude/skills/harness/bin/validate-digest.py` | `ee10a77da9dfdf55` |
| `.claude/skills/harness/bin/inflight_registry.py` | `caac8af58a180ecd` |
| `.claude/skills/harness/bin/harness_boundary.py` | `6f1577a15371287f` |
| `.claude/skills/harness/bin/artifact_accessors.py` | `22e4236116d3e241` |

## Suite exits at the baseline

- `tests/unit/test-lead-start-preflight.py`: exit 1; 4/34 assertions pass
- `tests/integration/test-lead-start-return.py`: exit 1; 40/57 assertions pass
- `tests/integration/test-dispatch-guard.py` (updated positive fixtures) against the baseline guard: exit 0 — 113 of 113 cases passed

## Per case at the baseline

`startup` cases must FAIL because the baseline guard let the start through to a claim (`exit=0 claim=yes receipt=yes`); `control` cases must PASS.

| SC | case | kind | baseline | valid | reason | observed |
|---|---|---|---|---|---|---|
| SC-01 | `SC-01/eng/zero` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/zero/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/irrelevant-only` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/irrelevant-only/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/two` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/two/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/one` | control | PASS | yes | control executes successfully | — |
| SC-03 | `SC-03/eng/missing` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'exactly-one remedy', 'run-start command'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/eng/ambiguous` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'inspect the record', 'close surplus runs'] exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/zero` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/zero/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/irrelevant-only` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/irrelevant-only/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/two` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/two/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/product/one` | control | PASS | yes | control executes successfully | — |
| SC-03 | `SC-03/product/missing` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'exactly-one remedy', 'run-start command'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/product/ambiguous` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'inspect the record', 'close surplus runs'] exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/zero` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/zero/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/irrelevant-only` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/irrelevant-only/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/two` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/two/cause` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/one` | control | PASS | yes | control executes successfully | — |
| SC-03 | `SC-03/validator/missing` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'exactly-one remedy', 'run-start command'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/validator/ambiguous` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['feature', 'lead', 'binding error', 'inspect the record', 'close surplus runs'] exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/eng/unreadable-record` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/validator/no-record` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-01 | `SC-01/non-lead` | control | PASS | yes | control executes successfully | — |
| SC-03 | `SC-03/product/plan-approved` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['refused', 'target', 'observed status', 'before signature', 'pending-plan phase'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/product/plan-None` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['refused', 'target', 'observed status', 'before signature', 'pending-plan phase'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/validator/plan-approved` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['refused', 'target', 'observed status', 'before signature', 'pending-plan phase'] exit=0 claim=yes receipt=yes stderr='' |
| SC-03 | `SC-03/validator/plan-None` | startup | FAIL | yes | fails for the missing startup behaviour | missing=['refused', 'target', 'observed status', 'before signature', 'pending-plan phase'] exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/product/plan-approved` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/product/plan-absent-status` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/product/plan-pending` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/validator/plan-approved` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/validator/plan-absent-status` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/validator/plan-pending` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/product/draft-no-plan` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/validator/no-plan` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/validator/validate-approved` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/validator/fix-approved` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/product/patch-approved` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/eng/build-no-mission` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/eng/simplify-no-mission` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/eng/distill` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/product/distill` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/validator/distill` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/product/mission-missing` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/product/mission-conflicting` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/validator/mission-missing` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/validator/mission-conflicting` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/eng/zero-no-mission` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/eng/two-no-mission` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/scope/mission-missing` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' |
| SC-02 | `SC-02/scope/pending` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/scope/validator-code-review` | control | PASS | yes | control executes successfully | — |
| SC-02 | `SC-02/scope/approved-while-lead-running` | startup | FAIL | yes | fails for the missing startup behaviour | lead exit=0; reader exit=0 claim=yes receipt=yes stderr='' |
| SC-04 | `SC-04/eng/start-bind` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/missing-binding` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/wrong-child` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/wrong-parent` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/wrong-feature` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/wrong-checkout` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/wrong-artifact` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/authorized-append` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/eng/unregistered-witness` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' gap: bind_exit=2 bind_ok=False return_exit=2 |
| SC-04 | `SC-04/product/start-bind` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/missing-binding` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/wrong-child` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/wrong-parent` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/wrong-feature` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/wrong-checkout` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/wrong-artifact` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/authorized-append` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/product/unregistered-witness` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' gap: bind_exit=2 bind_ok=False return_exit=2 |
| SC-04 | `SC-04/validator/start-bind` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/missing-binding` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/wrong-child` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/wrong-parent` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/wrong-feature` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/wrong-checkout` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/wrong-artifact` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/authorized-append` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/validator/unregistered-witness` | startup | FAIL | yes | fails for the missing startup behaviour | exit=0 claim=yes receipt=yes stderr='' gap: bind_exit=2 bind_ok=False return_exit=2 |
| SC-04 | `SC-04/scope/pending-return` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/scope/approved-after-start` | control | PASS | yes | control executes successfully | — |
| SC-04 | `SC-04/scope/approved-witness` | startup | FAIL | yes | fails for the missing startup behaviour | lead exit=0 claim=yes receipt=yes stderr='' reader exit=0 gap: return_exit=2 "Your return does not satisfy the digest contract, so it cannot be accepted. Fix these and return again — every field is required; say nothing with an explicit `[]`, or `none` for a scalar that genuinely does not apply:\n  - plan review mode is only valid while approval.status is pending; '/private/va" |
| SC-04 | `SC-04/distill-pin` | control | PASS | yes | control executes successfully | — |

## Gate-loosening mutants (temporary private copies; real gates untouched)

- **missing-binding** (`digest_destination.py`): newly failing assertions ['SC-04/eng/missing-binding', 'SC-04/product/missing-binding', 'SC-04/validator/missing-binding']; expected only `^SC-04/\w+/missing-binding$` — discriminates
- **pending-only** (`validate-digest.py`): newly failing assertions ['SC-04/scope/approved-after-start']; expected only `^SC-04/scope/approved-after-start$` — discriminates
