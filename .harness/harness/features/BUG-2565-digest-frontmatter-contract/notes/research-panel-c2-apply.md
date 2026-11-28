# BUG-2565 — panel cycle 2 apply (form fix + record)

**BLUF.** The low form finding is applied to T-02. All three substance findings stay open and go to the operator. The panel is recorded as cycle 2. Two cycle-1 findings are marked resolved because the reader graded them CLOSED. `plan-merge.py check` reports 6 tasks, 36 anchors and 0 failures. The plan was pending, so no `APPROVAL-RESET:` receipt was printed.

## Finding → change map

| PF | Sev/kind | Disposition | Change |
|---|---|---|---|
| PF-09dfb53f96962654c91322daa41e5b9e (T-02 case_30 docstring conflates host call and guard input) | low form | applied, left `open` for the operator's panel ruling | T-02 `intent:` now replaces the first sentence of case_30's docstring with "…it leaves the host call unrevised and hands this guard a normalized target for each dispatch…" (see `normalizeTaskDispatches` and the task branch in `.omp/extensions/harness-hooks.ts`). It also replaces the stale final sentence ("A guard that refused them too would be a second, divergent copy of the hook's rule; …") with "A guard that skipped the claim would leak a slot." No case body changes. T-02 `verify:` gains a last line: an `ast` docstring check on `case_30_schema_controls_are_not_the_guards` that requires both corrected phrases and rejects the old phrases. Probed on temp copies: the current file gives exit 1, the corrected docstring gives exit 0, and the corrected docstring with the new sentence deleted gives exit 1. |
| PF-9a0f853dff44e05bcf533eebd405abac (T-01 refusal threshold vs Run C) | high substance | **carried to operator**, unapplied | none |
| PF-25a87adffad1fd1f463f52b21ddb5b3e (T-01 contradictory/unsupported refusal receipt) | high substance | **carried to operator**, unapplied | none |
| PF-120f5374d27296822e9d10ea9d8adab9 (T-02 SC-03 dispatch-contract coverage) | med substance | **carried to operator**, unapplied | none |
| PF-64c3c27737fcbcc75d87663a269264f8 (cycle-1 T-04 typed equality) | high | resolved, resolved_by T-04 | reader graded it CLOSED in `notes/review-harness-code-reviewer-plan-c2.md` (#2) |
| PF-3425c074828c8b5fd51904f8dce82bba (cycle-1 T-02/T-03 failure behaviours) | med | resolved, resolved_by T-02 | reader graded it CLOSED (#3) |
| PF-cbf8dece633693ce07ab5a284be1a0cf (cycle-1 T-01 refusal probe) | high | stays open | reader graded it PARTIAL (#1) |

The other cycle-1 findings (PF-dc87…, PF-7436…, PF-d6fb…, PF-24f8…, PF-6b29…) and the readers list are unchanged from the record-panel output.

## Mechanics
- `apply` changed T-02 only: REPLACED T-02.intent and T-02.verify, exit 0, no `APPROVAL-RESET:`, so `gh-sync` was not run.
- `record-panel --cycle 2` from `runs/2026-11-27-03-plan-product/panel-c2.md`: ADDED the four PF ids above and carried the 8 cycle-1 findings unchanged. Exit 0.
- `set-panel` from `notes/panel-c2-set-panel.yaml` (the whole panel mapping with the two dispositions changed): exit 0.
- `check`: 6 tasks, 36 anchors, 0 failures, exit 0.
