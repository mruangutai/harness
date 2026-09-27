# FEAT-67 build — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "check-domain.approval_guard, check-omp-port.check and validate-digest.parse_digest are drivers over per-rule / per-phase functions at bar 4 (from grade 1: cyc 44/42/30), every function they leave behind is at bar 4 or exactly 2, and all eleven owning suites are byte-identical to the baseline at a clean checkout of the implementation pin e9ed16de."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/check-domain.py
    - .claude/skills/harness/bin/check-omp-port.py
    - .claude/skills/harness/bin/validate-digest.py
    - tests/unit/test-code-grade.py
    - .harness/harness/features/FEAT-67-complex-function-second-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-67-complex-function-second-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-67-complex-function-second-wave/notes/clean-pin-byte-receipts.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-67-complex-function-second-wave/notes/clean-pin-byte-receipts.md
```

One run covers T-01: `b8eabf48` (check → `CHECKS` driver, seven ordered check functions),
`d99eea6a` (approval_guard → driver over per-tool rules with a read-once `_GovernedFragment`),
`107f7c58` (parse_digest → phased scanner with explicit cursors; stale grade-1 exemption removed
from `test-code-grade.py`), `e9ed16de` (the four-angle simplify pass applied: four fold-ins, one
reverted under the one-fix ceiling) — the implementation pin — then `76873226` for the receipts.
Runners at the pin: unit exit 0 (42 files), integration exit 0 (70 files, `0 failure(s)`).
Evidence: `notes/clean-pin-byte-receipts.md` (11/11 owning suites identical at a clean detached
checkout of the pin after the ruled checkout-root normalisation; the plan's inline grade
assertion green at the pin and red verbatim in the baseline checkout), `notes/red-first-receipts.md`,
`notes/build-divergences.md` (no output divergence; D-01..D-06 structural rulings; the simplify
applied/reverted/skipped record).

Things the reviewer should weigh:
1. **Seven checks, not five (D-01).** The grilling undercounted; the driver has one row per block.
2. **Dead `denied_a` flag removed (D-03)** — `_deny_fragment` exits, so limb B's guard on it was
   always true. Output-identical; a pre-existing dead branch the decomposition would otherwise have
   documented.
3. **Grade-2 helpers kept at 2**: `_edit_introduce_limb`, `config_errors`, `agent_file_errors` —
   the grader's exception; splitting each would land at 3.

Residual (briefing rows, not applied): `runtime_pin_errors`/`runtime_probe_errors` are a second
check list in `main()` beside `CHECKS` (R1); the key-token spelling differs between
`_signature_child_keys` and `_edit_introduce_limb` on a `key :` edge (R2 — a real drift risk, not
byte-equivalent to unify); `_block_list_step` closes entries in place while returning the cursor (A3).
