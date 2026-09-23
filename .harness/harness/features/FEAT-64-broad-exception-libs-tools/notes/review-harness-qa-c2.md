# FEAT-64 QA c2 — blocked pinned matrix

## BLUF

**BLOCKED:** the only permitted worktree is not the immutable review pin. Its checked-out `HEAD` is `531efa4ca110a5252bd2a591df988073b7c5a563`, while this review is bound to `721b690e3578fbaba2b88d93774667d94ac4d8a3`; it also has a pre-existing modification to `feature.json`. Running T-01, T-02, or T-03 here would be an execution at neither the specified immutable object nor a clean checkout, so no matrix command was run.

## Phase 1 matrix

The signed `BRIEF.md` requires automated evidence for SC-01, SC-02, SC-03, SC-06, SC-07, and SC-08. Every signed task is `cross_module`; `.harness/harness.json:174-179` requires **unit** and **integration**. Their active configured commands are `.agents/skills/harness/bin/run-unit-tests.py --kind unit` and `... --kind integration` (`.harness/harness.json:285-289,320-324`). The signed task-level gates are T-01, T-02, and T-03 in `plan.yaml:123-124,173-174,207-208`. None was eligible to execute outside the pin.

Expected evidence at a valid pin: SC-01 byte/exit preservation and divergence ledger; SC-02 census plus increase/reduction mutants; SC-03 library/boundary escape behavior; SC-06 route one-parse behavior; SC-07 tool-consumer escape behavior; SC-08 handoff-authority one-parse behavior. Retained red-first evidence is required for each.

## Pin-object and evidence checks reachable without executing code

`git diff --name-status a4a3d7f8e9b91181fb6cc3ae058df8e02275d983 721b690e3578fbaba2b88d93774667d94ac4d8a3` reports a 67-object union (production, test, and feature-record surfaces). The content review and test execution of that union remain blocked because the supplied checkout is not the pin.

### GC-64-04 — closed

Direct object measurement supports the claimed remedy:

- `git diff --name-status a4a3d7f8 220feabb -- '.harness/**/*.yaml' '.harness/**/*.yml'` reports exactly three additions: the feature `plan.yaml`, `runs/validate-validator/state.yaml`, and `runs/validate-c1-validator/state.yaml`.
- The pin's `notes/build-divergences.md` §A4 names those same three additions and states the clean-checkout corpus result `104` total / `.harness=100`.
- The pin's `notes/byte-evidence.md` records the same `104` total / `.harness=100` output, with digest `3a1860010aa8ff56`.

This removes the previous cross-record contradiction. I could not independently execute the clean-checkout test at `220feabb`, because no checkout of that object is available under the dispatch's only permitted tree.

### QA-64-01 — closed

`git ls-tree -r --name-only 721b690e3578fbaba2b88d93774667d94ac4d8a3 -- .harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/build-main-direct/digest.md` returns the path, and `git cat-file -e` for that pinned object succeeds. The formerly absent shared build digest is tracked at the review pin.

## Finding

- **QA-64-02 — kind: form; severity: high.** The dispatch requires audit at immutable SHA `721b690e3578fbaba2b88d93774667d94ac4d8a3` but supplies only a dirty worktree checked out at `531efa4ca110a5252bd2a591df988073b7c5a563`. A green T-01/T-03 run on this tree could validate different production and tests; a red run could be unrelated. Provide a clean detached worktree at the stated pin (or authorize a permitted pinned checkout) and rerun the two configured kinds plus all three signed verify chains.

## Principles applied

- **Build the Lever:** used immutable Git object queries to establish tracked-object facts without substituting the mutable checkout for the required review pin.
