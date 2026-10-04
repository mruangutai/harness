# QA send-back — BUG-1898 c2-r1

**BLUF: FAIL — F-QA-01 remains active.** At exact object `4942950a83c1895d85922f7cd9e9cfd41e28daf8`, the copied-bin persona-release mutant produces the expected, non-crash signature: child exit `1`, `79/81 BUG-1898 exact-release checks passed`, and exactly two BUG-1898 failures. The permanent wrapper still tests only `code != 0 and reddened`; it does not require that signature or isolate the four known unrelated schema failures.

## Direct mutant observation

A disposable detached worktree at the exact object ran a child `tests/integration/test-validate-digest.py` with `VALIDATE_DIGEST_BIN` pointed to a temporary copied `.claude/skills/harness/bin`. Its copied `inflight_registry.py` received the same `PERSONA_RELEASE` override as `tests/integration/test-suite-claim-preservation.py:33-42`: `release()` ignores `agent_id` and delegates only `agent`, `feature`, `claim_id`, and `job_id`.

- Child process exit: `1`.
- Overall suite: `6 FAILING`.
- BUG-1898 subset: `79/81 BUG-1898 exact-release checks passed.`
- Every `FAIL  [bug1898]` line (exactly two):
  1. `FAIL  [bug1898] after the child settles the identical yield passes`
  2. `FAIL  [bug1898] and releases only the parent`
- The first line's detail reports exit `2` and the exact-child recovery command; the second reports all four claims remain: `['Main.Orch', 'Main.Orch-2', 'Main.Orch-2.Qa', 'Main.Orch.Lead']`.

These are causally exact-release failures, not a child crash: the child completed its normal per-check reporting and final `6 FAILING` summary, emitted no traceback, and stderr is the mutant registry's deliberate ambiguity refusal: `release('BUG-98-exact-release:*') is refusing — 4 live claims match; removing none rather than guessing.` The parent settlement attempts a release after the child is settled; ignoring its exact id instead sees all feature claims and refuses. Thus the parent remains held and both parent-settlement assertions fail.

## Unrelated failures

The other four failures are known unrelated relocated-config/schema expectation failures, all in the CLI/schema portion of the same child output:

1. `FAIL  drifted key spelling is caught`
2. `FAIL  enum near-miss is caught, not normalized`
3. `FAIL  code reviewer omission of code_grade is rejected`
4. `FAIL  code_grade's missing-field hint names the four legal values, not the list wording`

They account for `6 FAILING - 2 BUG-1898 = 4`; they do not alter the observed exact BUG-1898 count.

## Permanent-wrapper predicate

`test-suite-claim-preservation.py:106-110` defines `reddened` as every output line beginning `FAIL  [bug1898]` and passes its mutant arm exactly when `code != 0 and reddened`.

| scenario | predicate result | result |
|---|---:|---|
| (a) nonzero exit with no `FAIL  [bug1898]` line | false | rejects |
| (b) unrelated red plus one incidental `FAIL  [bug1898]` line | true | accepts |
| (c) more or different `FAIL  [bug1898]` failures | true | accepts |

The observed output proves the intended target signature is available to assert, but not that the wrapper asserts it. It only accepts a nonempty BUG-1898 failure set, so it cannot reject an extra/different regression or distinguish one incidental target line from the required two parent-settlement failures.

## F-QA-01 disposition

**Active — high, substance.** The user's exact discriminator requires child exit/result accounting, exactly `79/81`, the two named parent-settlement failures, and separate unrelated-failure classification. The permanent wrapper does none of those identity/count checks. Concrete failing scenario: a validator change leaves the four unrelated schema failures, introduces one incidental `[bug1898]` line, and suppresses or replaces either intended parent-settlement failure; `code != 0 and reddened` passes although the required mutant signature is absent.

All prior c2 matrix and SC evidence in `notes/review-harness-qa-c2.md` is preserved; this focused direct reproduction did not rerun a matrix kind. SC-07 remains `pending_operator_gate`.

## Cleanup

The temporary copied-bin directory was removed by the reproduction (`SCRATCH_REMOVED=True`). The detached scratch worktree was clean (`git status --porcelain` produced no rows), then removed; its path no longer exists. The assigned feature worktree was not removed or modified.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Exact mutant output is 79/81 with two parent-settlement BUG-1898 failures, but F-QA-01 remains active because the permanent wrapper accepts any nonempty BUG-1898 red set."
  suite: fail
  failures: 6
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "preserved: env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "preserved: env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 70 }
  coverage_gaps:
    - "F-QA-01: permanent mutation wrapper does not assert exit/result identity, 79/81, exactly two named parent-settlement BUG-1898 failures, or separate unrelated schema failures."
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-suite-claim-preservation.py:100-112" }
    - { id: SC-06, test: "tests/integration/test-validate-digest.py:5815-5844" }
  fail_first:
    - { sc: SC-01, evidence: "notes/review-harness-qa-c0.md:23" }
    - { sc: SC-02, evidence: "notes/review-harness-qa-c0.md:24" }
    - { sc: SC-03, evidence: "notes/review-harness-qa-c0.md:25" }
    - { sc: SC-04, evidence: "notes/review-harness-qa-c0.md:26" }
    - { sc: SC-05, evidence: "notes/review-harness-qa-c0.md:27" }
    - { sc: SC-06, evidence: "notes/review-harness-qa-c0.md:28" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-qa-c2-r1.md
```
