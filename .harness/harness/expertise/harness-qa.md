# Expertise — harness-qa
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN gating a change to `team-config.yaml`'s per-agent repository-tier grants DO know the only regression protection is a one-shot task `verify:` block — `run-unit-tests.sh` never re-runs `check-domain.sh --resolve` across all agents, so a dropped grant will not redden CI.
- G-02: WHEN citing `check-expertise.sh`'s live-corpus `verify:` (greps `.harness/expertise/` for `ADVISORY`) DO note it is coupled to the craft tier still holding token-carrying entries — nothing pins that corpus state, so a full migration to the repository tier would silently drop this check's only positive signal.
- G-03: WHEN running `test-check-expertise.py` DO know it registers under `run-unit-tests.sh`'s `--kind integration` only, not `unit` — even when the task touching it is flagged `cross_module` (which obligates both kinds), the unit half is not separately exercised by any standing script.
- G-04: WHEN citing run-unit-tests.sh's printed PASS-line count as a test-case total DO discount it — line ~139 emits exactly one PASS per script regardless of internal case count, so a script using its own ok/FAIL convention contributes one line for dozens of real cases, deflating any cross-run comparison.
- G-05: WHEN a merge from `main` creates a Harness layout violation DO expect the runner to exit 2 for `--kind unit`, `--kind integration`, and `--check-layout` alike — layout validation precedes kind dispatch, so no selected kind avoids it.
- G-06: WHEN bash-write-guard blocks a Bash-tool scratch-copy (cp/redirect) for a perturbation proof DO create a disposable git worktree under .claude/worktrees/ instead — the guard permits `git worktree add` there while denying ad hoc scratch copies elsewhere, and Bash-copy permissiveness is not reliable session to session.
- G-07: WHEN invoking run-unit-tests.sh DO always unset HARNESS_AGENT_TYPE first (env -u HARNESS_AGENT_TYPE) — with it set, test-plan-merge.py fails 11 checks and the suite exits 1, a false regression unrelated to the diff under test.
- G-08: WHEN a task's change_type resolves to bugfix in .harness/harness.json's test_matrix DO note its when: match_bug_class clause is currently an unresolvable placeholder — no bug-class taxonomy entry fires for any diff yet, so the floor stays at unit alone despite the clause's presence.
## Outcomes (max 10)
## Open (max 5)
