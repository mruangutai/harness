# Send-back criteria — run 2026-11-27-03-plan-product (written before any return)

## apply (pm)
Send back if any holds:
- Any of the four T-01 remedies is missing from T-01 (intent and/or verify as the plan carries tests):
  - PF-1cf493dc: a held + JSON-encoded BLOCKED positive case, AND a stale data-less finalize (`{type: "result"}` without `data`) asserted refused with the exact stale reason and no policy calls.
  - PF-3eb8320f: the FIFO probe runs in a killable, deadline-bounded subprocess and requires normal return plus the diagnostic (a regression fails, never hangs).
  - PF-37c5f930: one descriptor serves both the kind check and the read (nonblocking open of the regular path, fstat on the opened descriptor, then read) so a FIFO swapped in after the stat cannot block; the static non-regular kind check is retained.
  - PF-292338b0: controlled mtime offsets are limited to the hook timestamp cases; no load-time mtime instruction applies to the new sidecar.
- Any of the six cycle-2 PFs (the four above plus PF-7f19ccf3, PF-298aabb8) is not `resolved`, `resolved_by: T-01` after set-panel.
- Persona refusal suffix is not exactly "While this process is stale, you may yield only a BLOCKED digest that names this cause." wherever it appears (D-02, T-01, BRIEF SC-02); Main gains a suffix.
- Edits outside plan-merge verbs for plan.yaml; `record-panel --cycle 3` or `check` not exit 0; `approval:` touched (must stay `pending`); severity/kind/summary of any finding altered.
- Scope beyond the answers file: new decisions, new tasks, or fingerprint set changed.

## goalcheck (pm)
Send back if: graded against the cycle-1 (pre-ruling) intent rather than the grilling as amended by run-01 answers (fingerprint = loaded hook module only; BLOCKED-yield carve-out); any SC left ungraded; the note at notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md not updated for this cycle; a gap reported without a plan anchor.
