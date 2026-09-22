# Answers — FEAT-1821 distill after OMP restart — 2026-09-22

OMP restarted so the 1a32fe93 hook forwards HARNESS-MISSION. Re-run the validator distill only. Cycle ceiling 12→15: the three distill runs were counted as cycles although distillation is post-ship housekeeping (DEC-145) with no rework; the ceiling is raised so the ledger stays consistent rather than reclassifying runs after the fact. Backlog: distill runs should not consume rework cycles.
