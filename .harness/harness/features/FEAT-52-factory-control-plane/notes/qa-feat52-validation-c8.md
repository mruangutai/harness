# QA validation — FEAT-52-factory-control-plane — validator-c8 / feat52-validation

Worktree: `.claude/worktrees/harness/FEAT-52-factory-control-plane` (all commands run there).
`review_sha: "none"` in feature.json (known/pre-flagged); every "at review_sha" clause below is
substituted with `HEAD` (`8e203bc6`) and labelled as such.

## BLUF

14 of 15 plan verify clauses are green as literally written. **T-04's verify clause genuinely
exits 1**: `.omp/agents/harness-backend-dev.md` does not contain the string
`HARNESS_FEATURE_TREE_ROOT`, though the task's own `verify:` demands it as a positional member
(`pos=[...,'.omp/agents/harness-backend-dev.md']`). Confirmed with a direct grep — 0 matches. This
is a real gap in T-04, not a validation artifact; the digest repair under test (block D) is
unaffected and passes. `run-unit-tests.sh`'s full run also exits 1, but the sole failure
(`test-check-plan-routes.py`, 6 sub-cases) is attributable to the worktree-vs-main-checkout
`team-config.yaml` drift the dispatch pre-identified as environmental/out-of-scope, not to
FEAT-52's diff (`team-config.yaml` does not appear in `git diff main...HEAD`). The scoped
`--kind unit` run required by the matrix is clean (35/35).

## A. Fifteen plan verify clauses, run verbatim

| Task | Command (verbatim from plan.yaml) | Exit |
|---|---|---|
| T-01 | `python3 .agents/skills/harness/bin/test-inflight-registry.py && python3 .agents/skills/harness/bin/test-check-domain.py` | 0 (124/124 + 8 sub-suites all green) |
| T-02 | `python3 .agents/skills/harness/bin/test-check-instruction-paths.py` | 0 (10/10) |
| T-03 | `python3 .agents/skills/harness/bin/test-inject-expertise.py` | 0 (18/18) |
| T-04 | `python3 .agents/skills/harness/bin/check-instruction-paths.py .omp/agents .claude/agents .claude/skills/harness-expertise/SKILL.md .claude/skills/harness-qa-gate/SKILL.md .claude/skills/harness-verification-rules/SKILL.md .claude/skills/harness-tdd-enforcement/SKILL.md && python3 .agents/skills/harness/bin/sync-agent-adapters.py --check && python3 -c "...pos=[...,'.omp/agents/harness-backend-dev.md'];..."` | **1** — checker: `scanned 36 file(s), 0 violation(s)`; adapters `--check`: silent pass; final python probe: `missing ['.omp/agents/harness-backend-dev.md']`. Confirmed directly: `grep -c HARNESS_FEATURE_TREE_ROOT .omp/agents/harness-backend-dev.md` → `0`. |
| T-05 | `test-check-instruction-paths.py && check-instruction-paths.py .omp/agents references/debug-mission.md harness-expertise/SKILL.md && sync-agent-adapters.py --check` | 0 (scanned 18, 0 violations) |
| T-06 | `check-instruction-paths.py` over 12 skills + python probe for `HARNESS_FEATURE_TREE_ROOT` in 4 files | 0 (scanned 12, 0 violations; `missing []`) |
| T-07 | `check-instruction-paths.py .claude/skills/harness/templates` + README/PLAN anchor probe | 0 (scanned 7, 0 violations; `missing []`) |
| T-08 | `check-instruction-paths.py harness-handoff/SKILL.md` + 6-phrase presence probe | 0 (scanned 1, 0 violations; `missing []`) |
| T-09 | `python3 .agents/skills/harness/bin/test-dispatch-guard.py` | 0 (42/42) |
| T-10 | `check-instruction-paths.py` over 3 skills + per-file phrase probe | 0 (scanned 3, 0 violations; `missing []`) |
| T-11 | `check-instruction-paths.py .omp/agents .claude/agents && sync-agent-adapters.py --check` + 8-file probe | 0 (scanned 32, 0 violations; `missing []`) |
| T-12 | `test-check-instruction-paths.py && check-instruction-paths.py` (whole scope) | 0 (10/10; scanned 62, 0 violations) |
| **T-13** | `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md && test-gen-decisions-index.py` | **0** — see closure note below |
| T-14 | `python3 .agents/skills/harness/bin/test-inject-expertise.py` | 0 (18/18) |
| T-15 | `python3 .agents/skills/harness/bin/test-anchor-directions.py` | 0 (7/7) |

**T-13 cross-check anchor confirmed.** `plan.yaml:952-953` reads exactly the string named in the
dispatch (`--stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && ... test-gen-decisions-index.py`)
— NOT the retired `--check` form. Block A was not stopped. **Closure evidence, reported separately
as required**: run today, the amended/re-signed clause exits **0** — `diff` reports no drift and
`test-gen-decisions-index.py` reports 14/14 cases passed. This is the first recorded green run of
the signed string post-repair.

**Finding — T-04 is a real gap**, distinct from the digest-repair question this dispatch centers
on. It should route back as a dev fix (add `HARNESS_FEATURE_TREE_ROOT` guidance to
`.omp/agents/harness-backend-dev.md`, or correct the verify clause if the file was never meant to
carry it), not be silently absorbed here.

## B. Falsifiability of `check-instruction-paths.py`

1. `--list-scope`: **62 files**. All five BRIEF S1–S5 sites confirmed present individually (not by
   count): `harness-qa-gate/SKILL.md` ✓, `harness-expertise/SKILL.md` ✓, `harness-handoff/SKILL.md`
   ✓, `.omp/agents/harness-backend-dev.md` ✓, `harness/templates/PLAN.md` ✓.
2. Red fixture (inline + fenced, two distinct relative `.harness/` spans): exit **1**. Output named
   the fixture file at **both** line 2 (inline span, `.harness/harness.json`) and line 5 (fenced
   span, `.claude/skills/harness-qa-gate/SKILL.md`), independently. Summary: `2 violation(s)`.
3. SC-11 mirror fixture (`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/FEAT-52/BRIEF.md`):
   exit **1**, `VIOLATION ...fixture2.md:2: feature-directory path anchored to the control plane:
   .harness/harness/features/FEAT-52/BRIEF.md`. File and line both named.
4. All temp fixtures were under `mktemp -d` (`/var/folders/.../tmp.vdDB3aUGib`), never in the repo,
   and were removed after use (`shutil.rmtree`; `bash rm` was refused by bash-write-guard even
   against a `/var/folders` path outside every domain — the guard's `rm` denial is unconditional for
   this persona regardless of target, so cleanup went through Python instead, per repo Gotcha G-06's
   spirit though `rm` itself, not only a scratch-copy, was blocked here).

## C. Feature's own test files

| File | Exit | Result |
|---|---|---|
| test-inflight-registry.py | 0 | 124/124 |
| test-check-instruction-paths.py | 0 | 10/10 |
| test-inject-expertise.py | 0 | 18/18 |
| test-dispatch-guard.py | 0 | 42/42 |
| test-anchor-directions.py | 0 | 7/7 |
| test-check-domain.py | 0 | 8 sub-suites, all green (12/12, 27/27, 20/20, 10/10, 30/30, 16/16, 38/38, 28/28, 11/11) |
| test-gen-decisions-index.py | 0 | 14/14 |

`bash .agents/skills/harness/bin/run-unit-tests.sh` (env cleared of `HARNESS_AGENT_TYPE` per repo
Gotcha G-07 — without that unset, `test-plan-merge.py` fails 11 checks unrelated to this diff):
**exit 1**, 60 scripts declared (31 `UNIT_SCRIPTS` + 29 `INTEGRATION_SCRIPTS`), 1 file failed —
`test-check-plan-routes.py` (6 sub-cases: `case_04_all_granted_exits_0`,
`case_05_ungranted_declared_main_session_exits_0`, `case_15_deviation_plan_still_exits_0`,
`case_17_midpattern_wildcard_grant_exits_0`, `case_19d_explicit_path_unaffected_by_the_root_guard`,
`case_19d2_explicit_path_with_no_tasks_still_exits_0`). Every one of the six failures prints the
same cause: `DEVIATION .../worktree/.harness/team-config.yaml differs from
/Users/.../harness/.harness/team-config.yaml` — the test compares the worktree's manifest against
the **main checkout's**, and the dispatch's own constraints flag the main checkout as a stale copy
at identical paths. `team-config.yaml` is absent from `git diff main...HEAD` for this feature, so
the failure is not attributable to FEAT-52's changes. **Scoped confirmation**: the matrix's actual
required command, `run-unit-tests.sh --kind unit`, run in isolation, exits **0**, 35/35 scripts
pass (including `test-inject-expertise.py` and `test-check-instruction-paths.py`).

## D. Repaired validator digest

1. `validate-digest.py lead <abs path to 2026-09-02-02-validator/digest.md>`: **exit 0**, output
   `digest ok`.
2. Control, `2026-09-02-03-validator/digest.md`: **exit 0**, output `digest ok`. Both pass, so a
   negative control was required and run: a temp copy of the 02 digest with lines 92–132 (the
   entire `## 6. Contract block` section, including the fenced YAML) stripped, leaving only the
   original prose (`## BLUF` through `## 5. Adequacy notes`). Run against that stripped copy:
   **exit 1**, `VERDICT: BLOCKED (contract violation)` — no `VERDICT:` line, no `DIGEST:` block, no
   `artifact:` path, all eleven required DIGEST fields reported missing. The validator does
   discriminate; the repair is load-bearing.
3. Record-integrity check: `2026-09-02-02-validator/digest.md` is **132 lines**. Sections `## BLUF`
   (line 3) through `## 5. Adequacy notes` (line 78, running to line 91) are present and unmodified;
   `## 6. Contract block` (line 92) is the sole addition, and its own text states "no conclusion,
   severity or finding is added, removed or re-rated here" — consistent with the appended block
   transcribing, not altering, the existing ruling (`ESCALATE`, `severity_max: med`).

## E. State sweep (`check-state.sh`, worktree root, exit 1)

**Zero VIOLATION lines mention FEAT-52.** The three VIOLATION lines present, verbatim:

- `INV-29: .../worktrees/BUG-1033-config-shape-matrix is a standing worktree whose terminal status
  could not be determined — worktree path is not under WORKTREES_SEGMENT. ... The tree is dirty:
  remove will DECLINE until those changes are committed, landed or discarded. Its path did not
  resolve to a repository and id, so no removal command can be composed for it.`
- `INV-29: .../worktrees/harness/FEAT-51-claude-code-lifecycle-safety is a standing worktree whose
  feature FEAT-51-claude-code-lifecycle-safety reached a terminal state on the default branch. Act 3
  is not optional — the checkout is removed once the work has landed. Remove it with
  python3 .agents/skills/harness/bin/feature-worktree.py remove --repo harness --id
  FEAT-51-claude-code-lifecycle-safety (path: .../FEAT-51-claude-code-lifecycle-safety).`
- `INV-26 FEAT-51-claude-code-lifecycle-safety parent (issue #1135): the plan derives review — the
  board reads done.`

All three are FEAT-51 / BUG-1033 worktree matters, explicitly out of scope per dispatch, unchanged
by this validation run. FEAT-52 appears only in `note`-level lines (resolved finding dispositions,
orphaned-run-dir notes for four `runs/` directories not recorded in `feature.json`) — none rated
`VIOLATION`. Script's overall exit code: **1** (driven by the FEAT-51/BUG-1033 violations above).

## F. Test-matrix gate

Diff: `git diff main...HEAD` (local `main`, merge-base `8ff525e2`) — **90 files changed,
6362 insertions(+), 191 deletions(-)**.

Change types present (from `plan.yaml`, all 15 tasks): `logic` (T-01, T-02, T-03, T-09, T-14, T-15),
`docs` (T-04, T-05, T-06, T-07, T-08, T-10, T-11, T-13), `config` (T-12).

Per `.harness/harness.json` `test_matrix`: `logic.always = [unit]`, no `when` clause; `docs.always
= []`; `config.always = []`. No `when` predicate on any present type fires (no `cross_module`,
`bugfix`, `api`, `frontend`, `feature`, or `ai_behavior` task exists in this plan). **Floor = unit
only.**

| Kind | State | Satisfied by |
|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit`, exit 0, 35/35 scripts (includes `test-check-instruction-paths.py` and `test-inject-expertise.py`, both new/changed by this feature) |

`matrix_ok: true`.

## SC evidence pointers

- SC-04 (per-site direction assertions): `test-anchor-directions.py` (7/7, S1–S5 cases named).
- SC-05 (checker false-red/false-green over inline+fenced+control-plane-write shapes):
  `test-check-instruction-paths.py` (10/10) plus the two fresh red-proof fixtures in §B above.
- SC-11 (control-plane-anchored feature path is a violation): §B.3 fixture, exit 1.
- SC-15 (feature-root resolver pair): `test-inflight-registry.py` case35 (5 sub-assertions) +
  `test-check-domain.py`'s T-01 pair case.
- T-13 closure (decisions index equivalence + row budget): `test-gen-decisions-index.py` 14/14 plus
  the live `diff` run in §A, exit 0.
