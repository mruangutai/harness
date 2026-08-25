# Code review — T-01 — c0

**BLUF: PASS.** Stage 1 passed before Stage 2 began. The pinned change implements REQ-01..REQ-05 and SC-01..SC-06, has both exact integration registrations, and leaves the production utility byte-identical. Stage 2 found one non-blocking `med` diagnostic-assertion weakness; no high-severity or must-fix issue remains.

## Review coordinates and census

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `ce29a059e37af5133ae5b4f87df6f622ed966a92`
- Reviewed range: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..ce29a059e37af5133ae5b4f87df6f622ed966a92`
- Human commits in scope: none. The two commits are `ac8533876d5539bfa5db50802b3a3c321add89a8` and `ce29a059e37af5133ae5b4f87df6f622ed966a92`; neither is tagged `[harness:human]`.
- Changed files inspected: `.agents/skills/harness/bin/test-merge-gitignore.py`, `.agents/skills/harness/bin/run-unit-tests.sh`, `.harness/harness.json`.
- Intentionally unchanged production file inspected at both pins: `.agents/skills/harness/bin/merge-gitignore.sh`.
- Authority/evidence inspected: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md`, `.harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml`, `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-T-01-c0.md`.
- Supporting contract input inspected: `.agents/skills/harness/templates/gitignore.snippet`.

## Stage 1 — spec compliance: PASS

- REQ-01 / SC-01: the real subprocess starts from distinctive ordered bytes, requires those exact bytes as the merged prefix, and independently requires each canonical rule once (`test-merge-gitignore.py:34-45`).
- REQ-02 / SC-02: complete and incomplete `--check` cases separately pin exit 0/1 and byte identity; the incomplete case checks every currently missing canonical rule is reported (`test-merge-gitignore.py:48-72`).
- REQ-03 / SC-03: absent and partial targets are separate; both require every rule exactly once, and the partial fixture also requires its unrelated line to survive (`test-merge-gitignore.py:75-97`).
- REQ-04 / SC-04: the test captures bytes after the first successful merge and requires equality after the second (`test-merge-gitignore.py:100-110`).
- REQ-05 / SC-05: the absolute project root is invoked from a sibling caller directory; the project target must exist and the caller target must not (`test-merge-gitignore.py:113-123`).
- D-01 / exact registrations: execution crosses the real process seam through `subprocess.run` (`test-merge-gitignore.py:18-23`); the filename appears in `INTEGRATION_SCRIPTS` and not `UNIT_SCRIPTS` (`run-unit-tests.sh:17-18`), and its exact repository path appears in `test_kinds.integration.detect` (`.harness/harness.json:118-122`).
- D-02 / SC-06 / no production change: the base and review pins resolve `merge-gitignore.sh` to the same Git blob, `4610430764205c16a627edc9764a37dcb54af75c`; the scoped pinned diff contains no production-script hunk. The receipt retains the controlled-red result, untouched-real seven-case pass, and identical pre/post SHA-256 (`receipt-harness-dev-ops-T-01-c0.md:7-61`). This satisfies the inspection-only SC-06 (`BRIEF.md:49-52`).
- Scope: the shared product diff is exactly the new behavioral program plus its two integration registrations. Reordering the pre-existing `integration.detect` alternatives is semantically inert: the existing members remain and the only set addition is the exact new path. No provider handling, unrelated utility, or production behavior changed.
- Spec violations: none (`scope_creep: 0`, `omission: 0`, `mismatch: 0`).

## Stage 2 — code quality: PASS with one note

The test uses isolated temporary projects, resolves the real utility by default, exposes one narrow mutant seam, and keeps assertions at the process/filesystem interface (`test-merge-gitignore.py:8-23,34-123`). Exit statuses and state mutations are paired, so a no-op, wrong exit, destructive write, duplicate rule, wrong target, or second-run mutation fails rather than sailing through. The retained controlled mutant proves the complete-check assertion discriminates (`receipt-harness-dev-ops-T-01-c0.md:15-34`); the other cases have direct non-vacuous state/return assertions against the eight non-comment canonical rules (`gitignore.snippet:1-18`; `test-merge-gitignore.py:11-15,34-123`). Production miss paths remain fail-closed for invalid roots and unreadable snippets, and use whole-line fixed-string lookup before check-mode exit (`merge-gitignore.sh:15-31,36-63`). No silent-success or unhandled production branch was introduced.

### F-01 — partial diagnostic match can accept a fabricated rule

- Reviewer: `harness-code-reviewer`
- Severity: `med`
- Defect class: fail-open partial-match coverage.
- Failure scenario: if `--check` regresses to print `.claude/worktrees/NOT-THE-RULE` while the actual missing rule is `.claude/worktrees/`, the substring assertion passes and the suite can stay green even though the diagnostic does not identify the exact canonical rule an operator must add.
- Evidence: `.agents/skills/harness/bin/test-merge-gitignore.py:69-72` uses `rule in result.stderr`; the production contract emits one exact missing rule per bullet at `.agents/skills/harness/bin/merge-gitignore.sh:55-62`.
- Recommendation/disposition candidate: non-blocking follow-up; parse the emitted bullet lines and compare their exact rule set with `RULES[1:]`, which would also reject fabricated extra entries.

## Final disposition

`severity_max: med`; `must_fix: []`; `open_questions: []`. PASS is appropriate because Stage 1 passed, Stage 2 found no blocking issue, and the sole finding is a resilience gap rather than a current production defect.
