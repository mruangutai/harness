# BRIEF — FEAT-64 broad exception libraries and tools

## Problem

Operators and maintainers cannot distinguish expected environment, parse, process, and repository-boundary failures from unrelated programming defects in ten shared `bin/` libraries and eight tools: 43 broad handlers absorb both classes of failure, duplicate reparses obscure which reader owns a source, and the catch census still permits every legacy site. Narrowing those handlers without a byte-level contract could also change deliberately quiet behavior, printed diagnostics, or command verdicts.

## Done when — by perspective

**operator** — I can rely on the affected commands to produce the same exit status, stdout, and stderr for their established suites, including offline and unavailable-environment cases, while no hook is wired or changes verdict in this feature.

**code maintainer** — I can rely on the ten shared libraries and eight tools to catch typed failures at their real boundaries, let unrelated programming defects and process-control exceptions surface, and have a ratcheted census that permits only the two designed broad catches in `harness_boundary.py` within this feature's scope.

**reader** — I can identify why every remaining silence is intentional, verify that moved rationales and comments are byte-identical to the baseline, and trace any deliberate output divergence and every removed duplicate reparse to red-first evidence.

## KPIs

| KPI | Baseline | Target |
|---|---|---|
| Broad catches in the ten scoped shared libraries | 24 handlers at `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` | 2, both in `harness_boundary.py` |
| Broad catches in the eight scoped tools | 19 handlers at `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` | 0 |
| Scoped files with a ceiling above their shipped catch count | 17 catch-bearing files at `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` | 0 |

## Success criteria

- SC-01 (operator): Red-first receipt cases demonstrate a pre-change failure, then every named FEAT-64 suite preserves its baseline exit status, stdout bytes, and stderr bytes; any intentional difference is the only difference recorded in `notes/build-divergences.md` with old and new bytes and the ruling that permits it.
  verify: automated
  evidence: integration
- SC-02 (code maintainer): An AST census reports 2 broad catches across the ten scoped shared libraries, both in `harness_boundary.py`, and 0 across the eight scoped tools; independent increase mutants fail with one finding naming the changed file, while a reduction remains clean, with the failing states demonstrated before implementation.
  verify: automated
  evidence: integration
- SC-03 (code maintainer): Boundary tests demonstrated failing first and then prove that the scoped shared-library consumers catch exported typed errors or the documented `OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError`, and subprocess error classes, while unrelated programming exceptions propagate; `harness_boundary.hook_guard` catches `Exception` but not `BaseException`, explicitly lets `KeyboardInterrupt` and `SystemExit` escape, preserves a successful `main` result, and is not called by a hook.
  verify: automated
  evidence: unit
- SC-04 (operator): The pinned review tree contains no FEAT-64 change to the eleven hook entry scripts or `.omp/extensions/harness-hooks.ts`, and running their existing callers therefore retains every measured fail-open or fail-closed verdict; inspection uses `git show <review_sha>:<path>` rather than the working tree.
  verify: inspection
- SC-05 (reader): At the pinned review SHA, inspection of `git show <review_sha>:.claude/skills/harness/bin/<file>` against `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` confirms every moved silence rationale and copied-bootstrap comment is byte-identical, and every new explanatory sentence is separate prose marked `FEAT-64`.
  verify: inspection
- SC-06 (reader): Red-first tests prove that the scoped route-discovery path cannot reparse a plan, manifest, or config source already parsed and reported in the same execution, and the final implementation consumes the existing parsed value without adding a second shared loader or a second parse diagnostic.
  verify: automated
  evidence: integration
- SC-07 (code maintainer): Boundary tests demonstrated failing first and then prove that the scoped tool consumers `board-station.py`, `check-omp-port.py`, `check-plan-routes.py`, `check-skill-weight.py`, `gh-sync.py`, `post-merge-sweep.py`, `run-unit-tests.py`, and `upgrade-config.py` catch exported typed errors or the documented `OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError`, and subprocess error classes, while unrelated programming exceptions propagate.
  verify: automated
  evidence: integration
- SC-08 (reader): Red-first tests prove that the scoped handoff-authority path cannot reparse a feature or plan source already parsed and reported in the same execution, and the final implementation consumes the existing parsed value without adding a second shared loader or a second parse diagnostic.
  verify: automated
  evidence: unit

## Verification gaps

- None. The active unit and integration runners cover the Python library, CLI, mutation, and receipt surfaces; the null component and UI kinds do not match this non-UI feature.

## Constraints

- The behavior and catch-count baseline is commit `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` on branch `feat/FEAT-64-broad-exception-libs-tools`.
- Preserve established exit status, stdout bytes, stderr bytes, operator verdicts, and documented silence for every affected handler. An offline machine must not make a gate red.
- The ten shared libraries are `factory_decompose.py`, `factory_gh.py`, `feature_schema.py`, `gh_cost_log.py`, `handoff_done_when.py`, `handoff_policy.py`, `harness_boundary.py`, `harness_yaml.py`, `run_identity.py`, and `worktree_terminal.py`. The eight tools are `board-station.py`, `check-omp-port.py`, `check-plan-routes.py`, `check-skill-weight.py`, `gh-sync.py`, `post-merge-sweep.py`, `run-unit-tests.py`, and `upgrade-config.py`.
- `harness_boundary.py` ends with exactly two broad catches: one shared `RepoModuleError` boundary for repository-module load and call execution, and one unwired `hook_guard`. Neither catches `BaseException`-only process-control signals.
- Delete a duplicate reparse when the same source is already parsed and reported in that execution; do not hide it behind another helper or add a second diagnostic.
- Move existing silence rationales and the `run-unit-tests.py` copied-bootstrap comment byte-for-byte. Put new facts in separate prose marked `FEAT-64`.
- DEC-174 BLOCKS builder-specialist execution: every implementation task is `main-session-direct`. DEC-179 SUPPLIES the explicit lane declaration. DEC-231 SUPPLIES perspective-tagged criteria, and DEC-232 SUPPLIES stable file anchors.
- DEC-234 BLOCKS changing or sharing the five copied bootstrap prologues. FEAT-64 may narrow `run-unit-tests.py` handlers after the prologue but must not change that prologue or its reciprocal comment.

## Out of scope

- Wiring or narrowing any of the eleven hook entry scripts; FEAT-65 owns that work and the per-hook message receipts.
- Changing any hook's measured fail-open or fail-closed verdict; a posture change requires a separate ruling.
- Issue #1882 identity-less claim binding, because the grilling investigation did not reproduce it and it is unrelated to this boundary sweep.
- Extending the grader or review-skill rubric; that is the wave after FEAT-65.
- Turning any environment-related silence into a finding.
- Resolving `inflight_registry` process-identity reads; it belongs to FEAT-65's hook work.

## Approval

status: approved
approved-by: operator (molchairuangutai), via the main session
date: 2026-09-23
