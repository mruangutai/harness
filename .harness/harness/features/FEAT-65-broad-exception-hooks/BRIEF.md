# BRIEF — FEAT-65 broad exception hooks

## Problem

Operators and maintainers cannot distinguish expected environment, parse, process, and repository-boundary failures from unrelated programming defects in the eleven Python hooks invoked by `harness-hooks.ts`: 77 broad handlers absorb both classes of failure, eleven operator-visible own-failure lines disagree about what was checked, and the catch census still permits every legacy site. Four copied gate bootstrap prologues have also drifted from the fifth DEC-234 reference. Narrowing these hooks without byte-level receipts could silently change an enforcement verdict or make a hook's own defect look like a pass.

## Done when — by perspective

**operator** — I can rely on every affected hook to preserve its established fail-open or fail-closed verdict, stdout, and stderr except for the legacy own-failure lines whose classification routes them through `harness_boundary.hook_guard`; those paths say enforcement was off, nothing was checked, and the hook must be repaired. Shared authoritative direct commands, including `feature-record.py` and `inflight_registry.py`, remain outside a universal entrypoint guard so their unexpected failures stay loud and nonzero.

**code maintainer** — I can rely on all eleven hooks to catch typed failures only at their real boundaries, route only the classified legacy own-failure paths through the one `harness_boundary.hook_guard` template without catching process-control signals, keep typed-only authoritative command entrypoints unwrapped, keep all five DEC-234 bootstrap prologues byte-identical, and enforce a census budget of only the two designed broad catches in `harness_boundary.py`.

**reader** — I can trace every one of the 77 legacy sites to exactly one typed-boundary, deleted-absorber, or hook-guard treatment, inspect every operator-visible byte divergence and its ruling, and reproduce final receipts from a clean checkout of the named immutable implementation pin; the tracked receipt lands in a later feature-branch commit and does not claim to exist inside the pin it names.

## KPIs

| KPI | Baseline | Target |
|---|---|---|
| Broad catches in the eleven scoped hooks | 77 at `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` | 0 |
| Entries in `BROAD_CATCH_CEILINGS` | 13 at `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` | 1: `harness_boundary.py: 2` |
| DEC-234 prologues byte-identical to the `run-unit-tests.py` reference | 1 of 5 at `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` | 5 of 5 |
| Legacy operator-visible own-failure lines without a byte ledger | 11 at `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` | 0 |

## Success criteria

- SC-01 (operator): Red-first receipt cases demonstrate a pre-change failure, then every named owning suite preserves each hook's baseline exit status, stdout bytes, and stderr bytes; each intentional diagnostic replacement is the only difference recorded in `notes/build-divergences.md` with old bytes, new bytes, and its ruling.
  verify: automated
  evidence: integration
- SC-02 (operator): Red-first hook cases prove that each legacy own-failure path classified for `harness_boundary.hook_guard` produces its canonical `<name>: the hook failed internally (<Type>: <msg>) — passing through; this is not a pass, nothing was checked.` diagnostic, while already-closed boundary-load paths use its closed form and each guarded hook retains its established fail-open or fail-closed exit verdict.
  verify: automated
  evidence: integration
- SC-03 (code maintainer): Boundary tests demonstrated failing first and then prove that all 77 scoped sites catch only exported producer errors or the locally documented built-in boundary errors, deleted rule-level absorbers let unrelated programming exceptions reach `hook_guard` only on the classified guarded paths and otherwise escape loudly, and `KeyboardInterrupt` and `SystemExit` still escape.
  verify: automated
  evidence: integration
- SC-04 (code maintainer): An AST census demonstrated failing first and then reports zero broad catches across all eleven hooks and exactly `harness_boundary.py: 2` as the complete `BROAD_CATCH_CEILINGS` mapping; one representative unlisted-hook/default-zero increase mutant and a third-catch mutant in `harness_boundary.py` fail with the changed file named, while a reduction remains clean.
  verify: automated
  evidence: unit
- SC-05 (code maintainer): A red-first lock proves that the bootstrap prologues in `branch-create-gate.py`, `gh-close-gate.py`, `merge-gate.py`, `plan-sign-gate.py`, and `run-unit-tests.py` are byte-identical, including the FEAT-64 reciprocal-copy comment and the `(ModuleNotFoundError, ValueError)` catch, and mutating any one copy fails the lock.
  verify: automated
  evidence: unit
- SC-06 (reader): At the pinned review SHA, inspection confirms every one of the 77 baseline sites is represented exactly once by the classification in `notes/research-FEAT-65-hook-site-classification.md`, the shipped treatment matches that classification, no second hook-failure idiom exists, and no hook verdict changed.
  verify: inspection
- SC-07 (reader): At the pinned review SHA, `notes/build-divergences.md` records the old bytes, new bytes, ruling, and re-pinned owning case for every replaced or deleted operator-visible line, and inspection against `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` finds no unledgered operator-visible divergence.
  verify: inspection
- SC-08 (reader): At the final feature review SHA, `notes/clean-pin-byte-receipts.md` names the earlier immutable implementation pin tested from a clean checkout, records the invoked suites and their exit/stdout/stderr evidence, and records the zero-hook/two-boundary census plus five-way prologue identity; the receipt is committed later on the feature branch and does not claim to exist inside the implementation pin it names.
  verify: inspection
- SC-09 (operator): A red-first unit case proves `feature-record.py` remains outside a universal `hook_guard` entrypoint and an injected unexpected programming failure in its authoritative direct command is loud and exits nonzero.
  verify: automated
  evidence: unit
- SC-10 (operator): A red-first integration case proves `inflight_registry.py` remains outside a universal `hook_guard` entrypoint and an injected unexpected programming failure in its authoritative direct command is loud and exits nonzero.
  verify: automated
  evidence: integration

## Verification gaps

- None. The active unit and integration runners cover the Python hook, mutation, prologue-lock, census, and receipt surfaces; the null component and UI kinds do not match this non-UI feature.

## Constraints

- The behavior and catch-count baseline is commit `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` on branch `main`.
- The eleven scoped hooks are `check-domain.py`, `validate-digest.py`, `bash-write-guard.py`, `branch-create-gate.py`, `dispatch-guard.py`, `feature-record.py`, `gh-close-gate.py`, `inflight_registry.py`, `inject-expertise.py`, `merge-gate.py`, and `plan-sign-gate.py`.
- Preserve every hook's established exit status, stdout bytes, stderr bytes, and fail-open or fail-closed verdict except for the legacy operator-visible own-failure lines whose settled classification routes them through the canonical guard diagnostic; fully ledger those replacements and re-pin their tests. Programs whose classification contains only typed boundaries do not receive a universal entrypoint guard, and authoritative direct-command failures remain loud and nonzero.
- `harness_boundary.hook_guard` is the sole hook-level broad catch. Do not add a second wrapper, local broad absorber, alias, or compatibility path.
- `inflight_registry.py` catches `(OSError, ValueError, IndexError, StopIteration)` around `/proc/<pid>/stat` plus `/proc/stat`, `(OSError, subprocess.SubprocessError, ValueError)` around `ps -o lstart=`, and `(harness_boundary.AmbiguousWorktree, OSError)` around feature worktree lookup. The `ps` path retains `None`, and liveness retains its 24-hour fallback.
- The four gate prologues must match the `run-unit-tests.py` DEC-234 copy byte-for-byte, including its FEAT-64 comment, and one lock must protect all five copies.
- After build and simplify name an immutable implementation pin, final byte-identity tests run from a clean checkout of that pin. The tracked receipt names the tested implementation pin and lands in a later feature-branch commit; it never claims to exist inside the commit hash it names.
- DEC-174 BLOCKS builder-specialist execution: every task is `main-session-direct`. DEC-179 supplies the explicit lane declaration, DEC-231 supplies perspective-tagged criteria, DEC-232 supplies stable file anchors, and DEC-234 requires copied bootstrap prologues until the import seam is safe.

## Out of scope

- Changing any hook's established fail-open or fail-closed verdict.
- Changing `.omp/extensions/harness-hooks.ts` or adding/removing hook registrations.
- Extending the grader or review-skill rubric.
- Issue #1882 identity-less claim binding and host defect #1898.
- Turning an expected unavailable-environment silence into a new finding.
- Narrowing the additional `dispatch-guard.py` broad catch present only on the operator branch and absent from the pinned baseline.

## Approval

status: pending
approved-by:
date:
