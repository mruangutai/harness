# STATE

## Current

- feature: BUG-2295-handoff-one-per-phase
- run: .harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-02-validate-validator/state.yaml
- squad: validator
- status: in_progress
- mission: patch
- station: building (must-fix boundary)
- review_sha: 253cdf2aedf8f1b40fe712aa4e9301cdb764bf34 (validated; stale once the fix lands)
- approval: approved (operator, 2026-11-22; rework 1 round / 45 min)
- validate: FAIL, must_fix 1 (substance, high), matrix_ok true, SC-01 partial, SC-02..SC-04 met, operator partial / code maintainer pass
- must_fix: T-01 (main-session-direct) — `_RE_HANDOFF_CYCLE` in check-domain.py is case-sensitive while RE_HANDOFF routes case-insensitively; `notes/handoff-Build-c1.md` and `notes/handoff-build-C1.md` exit 0 at the pin (orchestrator probe). Fix: match the cycle regex with `_I`; add mixed-case Write and Edit refusal regressions beside `_handoff_cycle_suffix_cases`.
- cycles_used: 0 / 10; rework round 1 of 1 opens with this fix
- next: main session — land the fix test-first on feat/BUG-2295-handoff-one-per-phase; then orchestrator re-pins, `status review`, one `fix` run (readers re-verify over the new tip, `--regate`), re-close run 02 with `--cycles-used 1` (cycle attribution for the main-direct fix)

## Open Questions

- none
