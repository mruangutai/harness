# Operator ruling — rendered ship-review scope

## Decision

The generated `ship-review-c1.html` contrast finding does not gate FEAT-36. The feature's approved destination is behavioral coverage for `merge-gitignore.sh`; changing the shared briefing renderer is unrelated product work.

## Evidence

The B-1 panel found the requested functional change sound: code, QA, and security passed, the exact diagnostic-set assertion discriminated the fabricated-superset mutant, all 46 registered scripts passed, and `merge-gitignore.sh` remained byte-identical. The UI-only failure concerned a pre-existing color token in `.agents/skills/harness/bin/render-brief.py`, reached because the Harness ship phase generated a reading artifact.

## Disposition

- Preserve the B-1 test-strengthening change at `b3ea5e459cc95ac55047dbbeb98c307b580e3b0a`.
- Revert the unrelated renderer/test/generated-HTML rework.
- Record the contrast finding as non-gating follow-up evidence; do not expand FEAT-36 to fix it.
- Complete FEAT-36 review against its approved requirements and success criteria.
