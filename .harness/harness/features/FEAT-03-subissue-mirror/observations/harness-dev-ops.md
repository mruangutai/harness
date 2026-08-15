# Observations — harness-dev-ops — FEAT-03-subissue-mirror

- 2026-07-31: this Bash tool's shell is `/bin/zsh` (5.9), not bash — `${PIPESTATUS[0]}` expands
  empty there. A verify written as `cmd | grep ... ; echo ${PIPESTATUS[0]}` must be wrapped
  `bash -c '...'` to get bash's `PIPESTATUS` semantics; run as-is under this tool's default shell
  it silently reads empty, not the pipeline's real exit code.
- 2026-07-31: this macOS's default `bash` (invoked via `bash -c`) is 3.2.57 — no associative
  arrays (`declare -A` errors `invalid option`). `run-unit-tests.sh`'s drift-detector membership
  check uses a nested for-loop instead, for this reason.
- 2026-07-31: `check-state.sh` exited 0 here (not 1 as a prior receipt recorded) — state drifts run
  to run; do not treat a captured `check-state.sh` exit code as durable across sessions.
