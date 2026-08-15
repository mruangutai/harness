# Observations — harness-qa — FEAT-16

- 2026-08-12: SC-13's own narrative ("C1 hands its recorder an empty item list ... C1 passes on that
  mutant") did not hold under mutation testing of the literal mutant it describes (removing the
  `if not candidates: nothing_to_do(...)` check) — that mutant kills both C1 and P6 together, because
  both converge on the single call site at `factory_claim.py:292-293` regardless of whether the fleet
  declares one or two repos (`--repo` always reduces `repos_to_serve` to one element). Couldn't find a
  mutant, within reasonable tries, that P6 kills and C1 survives. P6 is still real, non-vacuous
  coverage (proven by Mutant 1) — just not proven "uniquely necessary over C1" as the BRIEF states it.
  Full detail in `notes/qa-c0.md`.
- 2026-08-12: `bash-write-guard.sh` parses Bash command TEXT, not shell-expanded values — a `cp ...
  $SCRATCH/dir/` destination using a shell variable gets flagged as an in-repo relative path and
  denied, even when the variable expands to an absolute out-of-repo path. Use the literal absolute
  path in the command, not a variable, when copying to scratchpad for mutation testing.
