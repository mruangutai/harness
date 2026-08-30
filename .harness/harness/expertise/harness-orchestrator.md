# Expertise — harness-orchestrator
## Patterns (max 15)
- P-01: WHEN reading `run-unit-tests.sh` output DO count `^FAIL ` lines and capture the runner's exit status in a variable — its final line is the last script's own `N/N checks passed`, so a tail read reports a red suite as green, and a piped `$?` returns the pipe's last command.
## Gotchas (max 15)
- G-01: WHEN quoting `check-state.sh`'s board-read cost DO re-measure rather than recall it — the figure moved from ~500 points (board 3, 486 items, `e1bcdc1`) to 5 (board 3, 473 items, `8c2c24d`), and a cost recalled without its conditions is the rot this repository keeps rediscovering.
- G-02: WHEN invoking `validate-digest.py` DO pass the PERSONA first and the path second. Path-only prints `BLOCKED (contract violation) — unknown persona '<the path>'`, which reads exactly like a malformed digest and will make you reject a valid one.
- G-03: WHEN a distillation returns ops for an agent you think holds no write path DO check the grant first — all three reviewers hold `Write` and both Expertise tiers, so ops go back to the owner via its lead; the orchestrator can write no Expertise file but its own.
- G-04: WHEN a lead run directory is absent from git status DO NOT read that as a false digest claim. The runs tree is gitignored here, so its artifacts are invisible to status by design, and git check-ignore -v settles it in one call.
- G-05: WHEN a plan MOVES or deletes a file DO run check-domain.sh --resolve on the OLD path too. check-plan-routes.py treats a NOBODY path as a violation under team execution, so create-at-new-path stays squad work while remove-at-old-path must go main-session-direct.
## Outcomes (max 10)
## Open (max 5)
- O-01: Shared `.harness/expertise/` has no lineage protection. Nothing reconciles a landed diff against the plan's declared files, so an undeclared edit to a per-spawn-injected file rides any cluster commit and only a human notices. Whether the fix is diff-vs-plan reconciliation, write-guard scoping, or keeping Expertise off feature branches is undecided.
