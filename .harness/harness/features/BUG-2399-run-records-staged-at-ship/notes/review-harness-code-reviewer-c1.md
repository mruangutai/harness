# BUG-2399 — code review c1

PASS with one nonblocking medium T-01 finding: directory-enumeration errors can silently omit retained records.

Reviewed `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..9db1ba98209df49017e73fae13da56f3e240086c`. Full commit list inspected; human commit: `6ad54d0f [harness:human] BUG-2399-run-records-staged-at-ship: operator signature (rework 1 round / 45 min, main-session-direct T-01)`. Only feature STATE.md/feature.json were dirty; executable review used pinned bytes. Live feature.json agrees with the dispatched pin.

## Stage 1 — specification

SC-01/SC-02 ordinary-path implementation and regression subjects match BRIEF/D-01: recorded-run recursive staging, exact index blobs, ignored real-Git fixtures, multiple absent-evidence paths, and refusal immutability (`tests/unit/test-prune-run-evidence.py:172-265`). Red-first receipts report assertion failures against the base, not import failures; these are inspected receipts, not independently executed evidence.

SC-03 inspection: keep/pin/explicit-keep selection and existing refusal/symlink deletion code are unchanged in the pinned diff (`.claude/skills/harness/bin/prune-run-evidence.py:71-159`). Missing evidence refuses before `_prune` and `_stage`, including previews (`:216-220`). Staging uses one literal, NUL-delimited force-add; dry-run returns before Git (`:191-203`). Unsafe run ids and linked runs/files are excluded; linked subdirectories are not descended (`:170-188`). Only the run's top-level `ui/` directory is excluded, not nested directories named ui. Missing evidence checks disk file presence, not hash validity.

The base ship command contained no manual force-add instruction to remove. The pin preserves both invocations and the human ship-commit message while describing automatic staging (`.omp/commands/harness-ship.md:43-59`). DEC-238's ship bullet alone changed; index changes are subsequent line offsets (`.harness/harness/docs/DECISIONS.md:8057-8071`). Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent; the approved BRIEF explicitly settles this patch without substitute product guidance. No scope change or amended task is claimed.

## Stage 2 — quality

- **MED, substance, T-01 / SC-01:** `.claude/skills/harness/bin/prune-run-evidence.py:183` calls `os.walk` without `onerror`. If a recorded run's digest is readable but its surviving `qa/` directory cannot be enumerated (permissions or filesystem I/O error), traversal silently skips that subtree. Git receives only the remaining paths and can succeed; the command exits 0 despite omitting its manifest from the ship record. Surface traversal errors rather than treating an incomplete listing as complete. Inspection-only finding; no permission probe executed. Uncommon filesystem state, therefore advisory rather than a gate.

Pinned code-grade command completed: 18 passing functions, production grades 4, tests grades 4–5; no reason-required records. No tests, builds, linters, formatters or mutants executed. QA owns final T-01 verification, including index regeneration comparison.

## Principles applied

Delete First: retain the existing selection/pruning seam; the new behavior stays local to the module already owning these inputs, without a speculative adapter or replacement selection system.

Open questions: none.
