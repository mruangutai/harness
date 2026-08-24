# Code review — FEAT-36 — c2

**BLUF: PASS.** Stage 1 spec compliance passed before Stage 2 code quality began. The immutable range `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..f494553bd9fbb987b4a19f91dcf4c3f37253fe38` satisfies REQ-01..REQ-05 and SC-01..SC-06. The c2 delta strengthens SC-05 by proving the requested target changes while a pre-existing caller `.gitignore` remains byte-identical. No high-severity or must-fix finding exists; F-02 remains one non-blocking `med` advisory.

## Review coordinates

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `f494553bd9fbb987b4a19f91dcf4c3f37253fe38`
- Reviewed: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..f494553bd9fbb987b4a19f91dcf4c3f37253fe38`
- Special-attention delta: `df23bdaa7113700977ec43e617e293c854c0854e..f494553bd9fbb987b4a19f91dcf4c3f37253fe38`
- Human commits in scope: none; all eight commits in the reviewed range are tagged `[harness:t-01]`, `[harness:T-01]`, or `[harness:review]`.
- Scoped verification: `python3 .agents/skills/harness/bin/test-merge-gitignore.py` exited 0 with all 7 named cases passing. No formatter, linter, build, project-wide suite, or all-kinds runner was run.

## Stage 1 — spec compliance: PASS

Stage 1 completed before any code-quality judgment.

- **REQ-01 / SC-01:** the real subprocess case starts with a distinctive byte sequence, requires the merged file to retain that exact prefix and order, and requires every canonical rule once (`test-merge-gitignore.py:18-23,34-45`).
- **REQ-02 / SC-02:** separate complete and incomplete `--check` cases require exit 0/1 and byte identity; the incomplete case checks every missing canonical rule is named (`test-merge-gitignore.py:48-70`).
- **REQ-03 / SC-03:** absent and partial targets are separate; both require every canonical rule exactly once, and the partial case retains its unrelated line (`test-merge-gitignore.py:73-97`).
- **REQ-04 / SC-04:** the first merge's bytes are captured and required unchanged after the second merge (`test-merge-gitignore.py:100-110`).
- **REQ-05 / SC-05:** the case invokes the absolute utility with an explicit absolute project root from a sibling caller outside both project and utility. The requested target is absent before invocation and required to exist afterward, proving it changes; the caller begins with `caller-only-rule`, its bytes are captured, and the post-run bytes must be identical (`test-merge-gitignore.py:113-125`). A missing/deleted caller file raises `OSError`, a mutated caller fails equality, and a missed requested target fails existence, so these checks fail closed.
- **D-01 / SC-06:** calls cross the real subprocess/filesystem seam (`test-merge-gitignore.py:18-23`). `run-unit-tests.sh:17-18` enumerates exactly **23 unit + 23 integration = 46 total** registrations; `test-merge-gitignore.py` appears only in `INTEGRATION_SCRIPTS`. Its exact path is also in the active integration detector (`.harness/harness.json:118-122`). This independently corrects c1's inherited 24-integration narration. Base and review resolve `merge-gitignore.sh` to the same blob `4610430764205c16a627edc9764a37dcb54af75c`, so the production utility is unchanged.
- **D-02 / scope:** production stayed untouched after the behavioral test passed. The only non-feature-test executable delta repairs the mandatory all-kinds mutation fixture without changing either production guard (`test-bash-write-guard.py:452-507`); feature-local state, notes, and run records are workflow evidence rather than product expansion. No provider behavior, unrelated production utility, or undocumented merge behavior changed.

Spec violations: none (`scope_creep: 0`, `omission: 0`, `mismatch: 0`).

### c2 delta from `df23bdaa`: compliant

The only executable/config change after c1 is four added lines and one replaced assertion in `test-merge-gitignore.py`: the caller now starts with a pre-existing `.gitignore`, captures its bytes, and requires byte identity instead of merely requiring that no caller file appeared (`test-merge-gitignore.py:119-125`). This is the requested stronger SC-05 proof, not scope creep. The requested project remains absent-before/existent-after, so both halves of SC-05 are asserted in the same case.

## Stage 2 — code quality: PASS with advisory

Stage 2 began only after Stage 1 passed. The tests remain at the production interface, use isolated temporary directories, pair process status with filesystem state, and make missing target, wrong target, destructive write, duplicate-rule, and second-run mutation outcomes fail closed. The c2 caller check is stronger than the prior absence-only assertion and does not introduce a silent-success path. The prior F-01 mutation-fixture issue remains closed at the pinned lines (`test-bash-write-guard.py:469-507`).

### F-02 — OPEN advisory, unchanged

- Severity: `med`; disposition: advisory, non-blocking.
- Failure scenario: if `--check` regresses to emit a fabricated superset such as `.claude/worktrees/NOT-THE-RULE` while canonical `.claude/worktrees/` is missing, `rule in result.stderr` still succeeds, so the suite accepts a diagnostic that does not name the exact rule an operator must add.
- Evidence: substring membership remains at `test-merge-gitignore.py:67-70`; production emits one bullet per missing rule at `merge-gitignore.sh:55-60`. The c2 delta touches only SC-05 and does not change F-02's likelihood, impact, or reachability.
- Recommended later action: compare the exact emitted bullet-rule set with the expected missing-rule set, rejecting fabricated or extra bullets.

No new correctness, silent-failure, fail-open, resource, dead-code, or maintainability finding has a concrete failure scenario. Final severity is `med`; `must_fix: []`; `open_questions: []`.
