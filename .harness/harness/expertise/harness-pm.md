# Expertise — harness-pm
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN a step must create, copy or move a file DO use the file tools or a Python script — `bash-write-guard.sh` denies redirects, `cp`, `mv` and `rm` in Bash whatever the target, including the session scratchpad and paths with no repo-like component.
- G-02: WHEN a Bash command names a path the guard should allow DO spell it as a literal absolute path. The guard reads the command line, not the resolved path, so the same target written through a shell variable is refused.
- G-03: WHEN sizing a task for `check-plan-routes.py` DO count the `files:` list first: machine fields are capped at 50 lines per task and `intent:` is not counted, so a long file list steals the room `verify:` needs.
- G-04: WHEN a task edits .harness/harness/docs/DECISIONS.md DO also list DECISIONS-INDEX.md and re-run gen-decisions-index.py, even when no row's text changes: the index stores a per-row source line, so lengthening one entry shifts every later anchor and the regeneration test reddens.
- G-05: WHEN running check-plan-routes.py DO pass your own plan's path. With no argument it reports over every live plan, so other features' DEVIATION lines land in your output and read as yours; only the summary line is global.
- G-06: A detect value in harness.json test_kinds is a pipe-separated string, not a list: iterating it yields one character per step, which prints like a successful enumeration of globs. Split on the pipe before matching anything.
- G-07: WHEN creating a plan.yaml that does not exist yet DO write the file directly: plan-merge.py treats an absent base as an empty mapping, so any approval block in the proposal differs from nothing and it refuses with exit 8. The merge tool is for the second and later spawns.
- G-08: WHEN a plan adds or deletes a test-*.py under the harness bin directory DO account for two run-unit-tests.sh gates: a per-kind one-directional KIND-DRIFT cross-check against harness.json detect, and a file-presence check flagging any on-disk test file in neither script array. Both exit 2, not a test failure.
- G-09: WHEN editing a file that a domain guard protects DO put the ABSOLUTE path in the edit's section header: a bare filename resolves against the working directory rather than the file you read, and the write is denied even where the lane grants it.
- G-10: WHEN running check-plan-routes.py DO pass a plan.yaml FILE: handed the feature directory it raises IsADirectoryError and exits 1, which reads as a gate failure rather than as a bad argument.
## Outcomes (max 10)
## Open (max 5)
