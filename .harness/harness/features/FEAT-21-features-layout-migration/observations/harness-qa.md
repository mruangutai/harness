# Observations — harness-qa — FEAT-21

- 2026-08-15: `bash-write-guard.sh` cannot resolve a domain when the redirect/cp/rm target is an
  unresolved shell variable (e.g. `cp -R src "$SCRATCH/dest"`) — it blocks even when `$SCRATCH`
  itself expands to an allowed scratchpad path, because the guard checks the literal command text,
  not the expanded path. Workaround: always spell scratch paths out in full in the command string,
  never via a variable. Hit this three times during FEAT-21's re-review before finding the pattern.
