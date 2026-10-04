# Reuse angle receipt — FEAT-495

## BLUF
One duplicate repository-lineage refusal adapter should be shared.

## Finding R-01
- **File and line:** `.claude/skills/harness/bin/bash-write-guard.py:871-906`; duplicate: `.claude/skills/harness/bin/check-domain.py:717-752`.
- **Summary:** `repository_claim_guard` is a second, near-byte-identical implementation of the repository-binding state normalization and refusal text already present in the Write/Edit gate.
- **Concrete cost:** Any new `inflight_registry.repository_binding()` denial state must be added to two `known` sets and two messages; a one-sided update silently coerces that state to `unreadable` on one write route, leaving the two enforcement surfaces semantically and diagnostically out of lockstep.
- **Alternative:** Put the accepted-state normalization and common refusal tail beside `inflight_registry.repository_binding` in `.claude/skills/harness/bin/inflight_registry.py`; retain only each guard's route-specific prefix/output primitive locally.

## Open questions
None.
