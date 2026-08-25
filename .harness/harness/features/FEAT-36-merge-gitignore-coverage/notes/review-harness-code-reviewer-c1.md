# Code review — FEAT-36 — c1

**BLUF: PASS.** Stage 1 spec compliance passed before Stage 2 code quality began. The exact pinned range implements REQ-01..REQ-05 and SC-01..SC-06 without a production-utility change. The c0 mandatory matrix defect F-01/MF-01 is closed by inspection; c0 advisory F-02 remains a non-blocking `med` assertion weakness. No new finding or must-fix item was found.

## Review coordinates and scope

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `df23bdaa7113700977ec43e617e293c854c0854e`
- Reviewed: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..df23bdaa7113700977ec43e617e293c854c0854e`
- Pin check: HEAD was `4ac60a2bab8c94b57388513af4ecb7dbc5d638ae`, newer than the immutable review SHA. `git diff df23bdaa..HEAD` was empty for every implementation/config/template path reviewed, so citations below match the pinned bytes; grading used the explicit base and review SHAs, never `..HEAD`.
- Human commits in scope: none. All five commits in the range carry `[harness:t-01]` or `[harness:review]`, not `[harness:human]`.
- Executable/config changes: `.agents/skills/harness/bin/test-merge-gitignore.py`, `.agents/skills/harness/bin/run-unit-tests.sh`, `.agents/skills/harness/bin/test-bash-write-guard.py`, `.harness/harness.json`. The other 39 changed paths are feature-local approved authority, state, notes, and run records. The production utility and canonical snippet were inspected but are unchanged.
- Review method: inspection only as dispatched. No test, build, formatter, or linter was run; QA owns the required matrix execution.

## Stage 1 — spec compliance: PASS

Stage 1 completed before any code-quality judgment.

- REQ-01 / SC-01: the real subprocess case preserves a distinctive byte prefix, including order, then independently requires each canonical rule exactly once (`test-merge-gitignore.py:18-23,34-45`).
- REQ-02 / SC-02: complete and incomplete `--check` cases separately require exit 0/1 and byte identity; the incomplete case checks every missing rule is named (`test-merge-gitignore.py:48-72`).
- REQ-03 / SC-03: absent and partial targets are separate and require every canonical rule exactly once; the partial fixture retains unrelated content (`test-merge-gitignore.py:75-97`).
- REQ-04 / SC-04: first-run bytes are captured and required unchanged after the second merge (`test-merge-gitignore.py:100-110`).
- REQ-05 / SC-05: an absolute project root is invoked from a sibling caller directory outside both project and utility; the project target must exist and the caller target must not (`test-merge-gitignore.py:113-123`).
- D-01 / SC-06 inspection: calls cross the real process seam (`test-merge-gitignore.py:18-23`); the exact filename is in `INTEGRATION_SCRIPTS` and absent from `UNIT_SCRIPTS` (`run-unit-tests.sh:17-18`), and the exact repository path is in `test_kinds.integration.detect` (`.harness/harness.json:118-122`). Base and review resolve `merge-gitignore.sh` to the identical blob `4610430764205c16a627edc9764a37dcb54af75c`; the pinned diff has no production-utility hunk. The original receipt records the controlled red, untouched-real 7/7 pass, and identical utility hash (`notes/receipt-harness-dev-ops-T-01-c0.md`, “Test-first evidence”).
- D-02 and scope: the only c1 executable delta stabilizes an existing required-matrix mutation fixture; it adds no unrelated behavioral coverage and changes no production guard. Feature records are review/verification bookkeeping. No provider, Anthropic/Claude compatibility, unrelated production utility, or undocumented merge behavior changed.

Spec violations: none (`scope_creep: 0`, `omission: 0`, `mismatch: 0`).

## c0 dispositions

### F-01 / MF-01 — CLOSED by inspection

- Severity at c0: `high`; owner: Engineering / `harness-dev-ops`; prior disposition: `must_fix`.
- Failure scenario: an equal-size mutation within one timestamp tick could reuse baseline bytecode, leaving both hook routes at `(0, 0)` and falsely failing the mandatory matrix instead of observing the intended `(2, 2)` mutation result.
- Closure evidence: the isolated fixture creates a fresh `m_bin` and copies source into it (`test-bash-write-guard.py:452-460`). `_both_routes` sets `PYTHONDONTWRITEBYTECODE=1` once and passes that same environment to both the Bash and Write hook subprocesses (`test-bash-write-guard.py:474-488`). Thus the baseline creates no `.pyc` in the fresh fixture before the equal-size source mutation; the retained post-mutation assertion still requires both routes, not a partial flip, to equal `(2, 2)` (`test-bash-write-guard.py:493-507`). The engineering receipt reports the exact matrix command exiting 0, but that runtime claim is receipt evidence for QA to re-establish, not a test run by this reviewer (`notes/receipt-harness-dev-ops-review-fix-eng.md`, “T-01 verification”).
- Disposition: closed; remove from `must_fix`.

### F-02 — OPEN advisory, unchanged

- Severity: `med`; owner: Engineering / `harness-dev-ops`; disposition: advisory follow-up, non-blocking.
- Failure scenario: if `--check` regresses to emit `.claude/worktrees/NOT-THE-RULE` while `.claude/worktrees/` is missing, `rule in result.stderr` passes, so the suite accepts a fabricated diagnostic that does not name the exact rule an operator must add.
- Evidence: substring membership remains at `test-merge-gitignore.py:69-71`; production emits one exact bullet per missing rule at `merge-gitignore.sh:55-62`. The c1 rework did not touch this test, so continuity—not resolution—is the correct disposition.
- Recommended later action: compare the exact emitted bullet-rule set with `RULES[1:]`, rejecting missing and extra/fabricated bullets.

## Stage 2 — code quality: PASS with advisory

Stage 2 began only after Stage 1 passed. The test stays at the process/filesystem interface, uses isolated temporary projects, and pairs exit status with state assertions. Missing targets, wrong targets, duplicate rules, destructive writes, and second-run mutations fail closed. The F-01 repair preserves the discriminating before/after assertion and applies one shared environment to both adapters. No new correctness, silent-failure, resource-lifetime, dead-code, or maintainability finding has a concrete failure scenario beyond retained F-02.

## Dismissed and scoped-out items

- **Dismissed — F-01 fix as scope creep:** it repairs a false failure in the feature's mandatory all-kinds verification and neither expands unrelated coverage nor alters unrelated production behavior.
- **Dismissed — `PYTHONDONTWRITEBYTECODE` might still read an old cache:** the mutation fixture's bin directory is freshly created, receives only copied source files, and its baseline subprocesses cannot write bytecode; there is no fixture-local cache to read after mutation.
- **Dismissed — SC-05 needs an unbounded filesystem side-effect sweep:** the approved plan specifically requires the requested project target to change and the unrelated caller to gain no `.gitignore`; the case pins both. Auditing arbitrary undocumented side effects would exceed the weakest sufficient contract.
- **Scoped out:** QA execution and matrix verdict, security audit, and UI audit, per dispatch. Production error-path changes are also absent because `merge-gitignore.sh` is byte-identical.

## Final disposition

- New findings: none.
- Continuing advisory findings: F-02 (`med`, Engineering / `harness-dev-ops`).
- `severity_max: med`
- `must_fix: []`
- `open_questions: []`
- Files touched by this reviewer: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c1.md` only.
