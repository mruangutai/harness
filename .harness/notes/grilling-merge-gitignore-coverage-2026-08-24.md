# Grilling — merge-gitignore behavioral coverage — 2026-08-24

## Destination
A fully traceable Harness cycle adds executable behavioral coverage for `merge-gitignore.sh`, produces a stacked pull request, and stops at user-controlled merge. Every model-backed Harness agent in this cycle resolves through the OpenAI provider overlay; the resulting repository change remains provider-neutral.

## Settled
- Should the cycle be test-only? → Start test-first and change production only when a failing test proves a documented contract violation.
- What behavior must be covered? → Existing `.gitignore` content survives; `--check` distinguishes complete from missing rules; absent and partially populated targets receive only missing rules; reruns are idempotent; project-root handling is independent of caller cwd.
- What does “using OpenAI” mean? → Every model-backed Harness agent participating in this cycle uses `.omp/providers/openai.yml`. It does not remove Anthropic support, disable Claude Code compatibility, or make the resulting code provider-specific.
- Where does delivery stop? → Planning, build, QA, simplification, review, goal-check, and ship review complete; the pull request remains unmerged for the user.
- How is the work traced? → GitHub issue #814 is a sub-issue of host-neutral utilities issue #594.

## Not yet specified
- None.

## Out of scope
- Expanding coverage to unrelated `bin/` utilities.
- Changing documented `merge-gitignore.sh` behavior without a failing behavioral test.
- Provider-specific production logic.
- Merging the resulting pull request.

## Facts I verified (so pm does not re-derive them)
- `merge-gitignore.sh` documents append-without-overwrite, whole-line rule matching, partial merge, `--check`, cwd-independent snippet lookup, and idempotence — source inspection at OMP-port SHA `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`.
- The canonical `bin/` directory contains 83 Python files, 9 shell scripts, and 45 registered Python test programs; `merge-gitignore.sh` is the only shell script with no direct `test-*.py` reference — measured in the OMP-port worktree on 2026-08-24.
- GitHub issue #594 broadly covers host-neutral utilities but does not explicitly identify this missing behavioral test — issue body inspected on 2026-08-24.
- GitHub issue #814 was created for this work and linked as a sub-issue of #594.
