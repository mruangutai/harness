# Observations — harness-data-engineer — FEAT-27

- 2026-08-19: bash pathname expansion (`for f in "$root"/.harness/*/expertise/"$agent.md"`) is
  lexicographically sorted by the shell before the loop body ever runs — confirmed empirically by
  globbing a directory whose subdirs were created in non-alphabetical order (zeta, alpha, mid) and
  getting alpha/mid/zeta back. Worth remembering next time a diff adds an explicit sort step after a
  bash glob: check whether the glob already guarantees the order before treating the sort as
  necessary.
