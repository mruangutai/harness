# Handoff — plan phase — FEAT-42-one-root-resolver

## Next

Get the operator's ruling on Q5 (STATE.md), then dispatch `harness-product-lead` -> `harness-pm` for
ONE edit: add a fourth exclusion to SC-01 in `BRIEF.md` for the harness's own record tree
(`.harness/harness/features/**`, `.harness/notes/**`, `.harness/logs/**`), re-pin the baseline over
the corrected scan set, and mirror the same exclusion into T-07's `intent` in `plan.yaml:519-529`.
Then the plan is signature-ready. Do NOT commit before that edit lands — committing is what breaks
SC-01. Everything else in the plan is verified and finished.

## Trust

- plan.yaml has 20 tasks, 15 main-session-direct / 5 team, all with id/files/execution_mode/verify —
  verified-at 3952814 by parsing the YAML myself, not relayed.
- SC-01's true count over its own scan set is 21 occurrences across 17 files — verified-at 3952814 by
  re-running `git ls-files` minus the three exclusions. Matches the recorded baseline exactly.
- The feature directory is UNTRACKED — verified-at 3952814 via `git ls-files --error-unmatch`, which
  fails on plan.yaml, and `git status --porcelain` showing `??`. This is why the lead's "72 across
  19" was wrong and why its conclusion is still right after a commit.
- `.omp/extensions/harness-hooks.ts:144` injects `HARNESS_PROJECT_DIR: cwd` — verified-at 3952814 by
  reading the line; it is the only such occurrence outside `bin/`.
- T-07's three earlier edits and the re-lane all landed — verified-at 3952814 by reading the task.
- `approval: pending` in both artifacts — verified-at 3952814.
- The lead's claim that backend-dev's writable domain cannot host the mutant — verified-at 3952814
  against `team-config.yaml:164-175`; `src/` does not exist in this repo.
- UNVERIFIED: pm's claim that issue #869 carries the DEC-174 am.4 amendment. I never opened it.
- UNVERIFIED: the lead's report of a `bash-write-guard.sh` false positive on an ASCII arrow in a
  heredoc body (Q7). Plausible and self-consistent, but I did not reproduce it.

## Dead ends

- Do not re-open D-1..D-5. Operator rulings, settled 2026-08-26 — see
  `/Users/molchairuangutai/GitHub/harness/.harness/notes/analysis-path-accessors-2026-08-26.md` from line 167.
- Do not narrow SC-01 back to `.claude/skills/harness/bin/`. The operator ruled repo-wide explicitly
  to catch `harness-hooks.ts`; the fourth exclusion must not undo that.
- Do not re-lane T-07 back to `team`. DEC-179 forces main-session-direct — backend-dev's writable
  domain and the widened scan set have an empty intersection.
- Do not reuse `test-no-distribution.py`'s `is_excluded_from_scan()` (`:108-111`) for SC-01. Its
  exclusion set (`:92-93`) is case2-specific and wrong in both directions here.
- Do not use `release-all` on the inflight registry. It wipes every claim of every agent.
- Do not treat "the lead's number disagrees with mine" as the lead being wrong. Re-derive first; on
  Q5 the wrong method had accidentally simulated the post-commit state.

## Working set

- `.harness/harness/features/FEAT-42-one-root-resolver/STATE.md` — Q5/Q6 carry the blocking detail
- `.harness/harness/features/FEAT-42-one-root-resolver/BRIEF.md` — SC-01 at :77-92 is the edit target
- `.harness/harness/features/FEAT-42-one-root-resolver/plan.yaml` — T-07 at :490-530
- `.harness/harness/features/FEAT-42-one-root-resolver/runs/2026-08-26-6-plan-product/digest.md`
- `.harness/harness/features/FEAT-42-one-root-resolver/notes/ship-review-2026-08-27-plan.md`
