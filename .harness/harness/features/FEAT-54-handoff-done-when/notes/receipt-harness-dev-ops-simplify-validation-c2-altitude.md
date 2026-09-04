# FEAT-54 validation repairs — ALTITUDE receipt

## Verdict

PASS — the repairs are placed at the right module depth, with one authoritative validator and thin enforcement/probe adapters. No fold-in or briefing-row candidate is warranted.

## Overall placement recommendation

**leave**

`handoff_done_when.py` is the authoritative home for `## Done when` shape, grammar, safe authority-target reading, and resolution. `check-domain.sh` owns hook-route concerns—fail-closed module invocation and pre-mutation Edit reconstruction—then delegates the handoff contract to that module (`.claude/skills/harness/bin/check-domain.sh:1546-1569,1819-1876`; `.claude/skills/harness/bin/handoff_done_when.py:9-17,178-270`). The integration and unit cases remain beside the observable surfaces they exercise, while the manual probe keeps its input-selection and bounded-read policy local because those are probe execution boundaries rather than handoff-contract rules (`tests/integration/test-check-domain.py:3994-4248`; `tests/integration/test-check-state.py:2141-2266`; `tests/unit/test-handoff-done-when.py:46-159`; `tests/manual/probe-handoff-comprehension.py:23-108`; `tests/unit/test-probe-handoff-comprehension.py:23-101`).

## Structured findings

[]

## Placement checks

- Authority rule has one home: `handoff_done_when.problems`; callers do not reimplement its Scope/Authority grammar or resolution.
- Hook-specific Edit reconstruction remains in `check-domain.sh`, where complete tool payload and pre/post route semantics are available; pushing it into the handoff validator would couple a document module to one editor protocol.
- Probe-specific path admission and bounded descriptor read remain in the manual probe; folding them into the authority resolver would merge two different trust boundaries and expose probe-only selection policy as shared validation API.
- Direct tests remain at their owning surfaces. Consolidating fixtures across the two integration executables would increase coupling without removing an authoritative rule copy, and every individual case is intentionally preserved.
