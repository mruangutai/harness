# Red-first — T-04 host slice (expertise_apply + Main merge route)

Owned files: `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`.

## Command

    bun test tests/unit/omp-hooks.test.ts

## Red — new tests against the pre-change hooks (mocks already adapted to registerTool/zod)

Result: 140 pass, 9 fail.

- FEAT-2225: registers expertise_apply with the exact closed argument schema
- FEAT-2225: persona, feature, run id, root, destination, base and state arguments are refused before the core runs
- FEAT-2225: an unidentified, non-distill, held, unready, unplaced or unauthorized caller is refused
- FEAT-2225: the custom mutator takes the existing claim authorization and held-run refusal in tool_call
- FEAT-2225: craft and repository destinations run member-ops with host-derived identity and return its receipt verbatim
- FEAT-2225: a repository segment with separators, traversal, an undeclared name or a symlink is refused before the core runs
- FEAT-2225: any nonzero member-ops exit, or a missing receipt, is a tool failure carrying the core's words
- FEAT-2225: supersedes carries exact batch ids and the host-resolved main base, never a caller base
- FEAT-2225: Main's Bash git merge and gh pr merge reach merge-gate before the non-governed return

The pre-change hooks registered no tool, so `tools.get("expertise_apply")` was undefined in the first eight.
The ninth failed because Main's Bash call returned at the non-governed early return, so merge-gate.py never ran.

## Green — after the implementation

Result: 149 pass, 0 fail (the 140 existing tests unchanged in behavior).

## Schema probe

The registered schema was also built with the installed OMP omptype zod
(`@oh-my-pi/omptype@18.14.1/src/zod.ts`, a throwaway probe that was deleted afterwards). It accepted
craft and repository+supersedes calls. It rejected a top-level `persona` argument, an op-level
`state` key, a `../x` repository segment, and a drop op that carried `entry`.
