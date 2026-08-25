# Product goal-check — FEAT-36 — df23bdaa7113700977ec43e617e293c854c0854e

**Overall: FAIL.** SC-01 through SC-04 and SC-06 are met, but SC-05 is not met because its automated case proves the requested project gains `.gitignore` and the caller directory does not; it does not prove the criterion's quantified claim that *only* that project's `.gitignore` changes. Any unmet criterion makes the product goal-check fail.

## Plan and requirement coverage

Pinned `plan.yaml` records T-01 as `status: done`, traces REQ-01 through REQ-05, and contains the exact required verify scalar:

    python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
    .agents/skills/harness/bin/run-unit-tests.sh --kind all

The pin-specific QA panel records that exact command exiting 0 at the review SHA and all seven named cases passing (`notes/review-harness-qa-c1.md:3-17`). This establishes execution, but does not supply an assertion absent from the pinned test.

## Success criteria

- **SC-01 — automated — met.** The pinned real-subprocess case starts with four distinctive ordered lines, requires the merged bytes to start with the exact original byte sequence, and checks every canonical rule once (`df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:18-23,34-45`). QA records the named case passing at the pin (`notes/review-harness-qa-c1.md:10-17`).
- **SC-02 — automated — met.** Separate pinned cases assert complete exit 0 and incomplete exit 1; both compare target bytes with their originals, and the incomplete case iterates over every missing canonical rule and requires its text in stderr (`df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:48-72`). QA records both cases passing (`notes/review-harness-qa-c1.md:10-17`).
- **SC-03 — automated — met.** Separate absent and partial cases derive counts for every canonical rule: each must equal one; the partial fixture begins with one canonical rule and unrelated content, whose retention is also asserted (`df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:26-29,75-97`). QA records both cases passing (`notes/review-harness-qa-c1.md:10-17`).
- **SC-04 — automated — met.** The pinned case captures bytes after the first successful merge, runs the real utility again, and requires byte identity after the second run (`df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:100-110`). QA records the case passing (`notes/review-harness-qa-c1.md:10-17`).
- **SC-05 — automated — not_met.** The pinned case invokes the absolute real utility from a sibling caller directory outside the project and utility, with the explicit absolute project root; it asserts the requested target exists and the caller gains no `.gitignore` (`df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:18-23,113-123`). It does not snapshot or inspect the utility location or any scope beyond the caller, so it cannot prove the broader clause that *only* the project's `.gitignore` changes. The QA pass confirms this narrower case ran, not the missing quantified assertion (`notes/review-harness-qa-c1.md:17,23`).
- **SC-06 — inspection — met.** At the pin, `test-merge-gitignore.py` is in `INTEGRATION_SCRIPTS` and not `UNIT_SCRIPTS` (`df23bdaa:.agents/skills/harness/bin/run-unit-tests.sh:17-18`), and its exact path is in `test_kinds.integration.detect` (`df23bdaa:.harness/harness.json:118-122`). Base and review resolve `merge-gitignore.sh` to the identical blob `4610430764205c16a627edc9764a37dcb54af75c`; the pinned reviewer independently records the unchanged utility and registration (`notes/review-harness-code-reviewer-c1.md:19-25`). Because production was unchanged, the alternative test-first-production-fix branch is inapplicable; the receipt records the untouched utility passing 7/7 before and after identical hashes (`notes/receipt-harness-dev-ops-T-01-c0.md:36-61,91-94`).

## UAT disposition

No UAT is required because no success criterion declares `verify: uat`.

## Open questions

None.
