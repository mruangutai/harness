# BUG-2566 — cycle-2 apply receipt (run 2026-11-27-02-plan-product)

**Both form findings are fixed in plan.yaml and BRIEF.md; no substance edit made; panel recorded as cycle 2 with the ten cycle-1 findings resolved (T-01) and the six cycle-2 findings open; check exits 0; approval pending.**

## Fields changed

plan.yaml, via `plan-merge.py apply` (exit 0, six REPLACED lines, no `APPROVAL-RESET:` receipt, so no gh-sync call):

- D-02.choice — the persona refusal sentence is now "While this process is stale, you may yield only a BLOCKED digest that names this cause." (reader's Q-07 wording); adds that skipping the stale check admits a BLOCKED yield to normal validation and does not guarantee acceptance, run end or claim release.
- D-02.because — the child "can still submit a BLOCKED digest recording why"; completion and claim release stay subject to validate-digest.py (example: lead without an authorized durable artifact).
- D-03.because — agent rediscovery reaches each new spawn; a running child keeps its schema. The rejected-alternative gloss is now "(rediscovered on each new spawn)".
- D-04.choice — the grep is described as a text check for the known legacy import spelling `from "./digest-schema`, not import-aware; the file's absence carries the 2565-first condition; new code and comments must not contain that phrase. The 2565-first condition is kept.
- T-01.intent — the precondition paragraph has matching wording. The refusal sentence is replaced in both places: the handler spec and the test P definition.
- T-02.intent — the agent-definitions sentence now covers new spawns only. The BLOCKED-yield sentence is qualified as subject to normal validation, with the persona-refusal wording. The verify phrases are unchanged and still supplied: BLOCKED digest, restart omp, never opened and the rest.
- T-01.verify, T-02.verify — unchanged, because the grep command was already the legacy-spelling check.

BRIEF.md (edit tool): the operator perspective is qualified with "still faces normal yield validation". SC-02's refusal sentence now matches the new wording. The Constraints ordering bullet now has the grep caveat. The DEC-204/100 bullet now states the no-guarantee qualification.

Not applied (substance, routed to the operator through the team digest): the held+JSON BLOCKED and data-less finalize witnesses, the FIFO probe deadline, the stat/read FIFO race and the sidecar mtime recipe.

## Panel

- `record-panel --cycle 2`: exit 0, ADDED six PF ids. panel.cycle 2, last_run 2026-11-27-02-plan-product.
- `set-panel`: exit 0. The ten cycle-1 PFs are `resolved`, `resolved_by: T-01`, because every reader evidence anchor sits in D-02/D-03/D-04/T-01 lines and none names T-02. Severity, kind and summary are untouched.
- Open: PF-1cf493dc…, PF-3eb8320f…, PF-37c5f930…, PF-292338b0… (substance), PF-7f19ccf3…, PF-298aabb8… (form, text now fixed, left open per dispatch).

## Checks

- `plan-merge.py check --root <worktree>`: exit 0, 2 tasks, 3 anchors, 0 failures, no OVERLAP.
- approval: `{status: pending}`.
- check-state side output lists pre-existing VIOLATIONs that are not caused by this run: BRIEF not approved, INV-29 for FEAT-2557's worktree, and INV-37 because there is no Build-entry receipt.
