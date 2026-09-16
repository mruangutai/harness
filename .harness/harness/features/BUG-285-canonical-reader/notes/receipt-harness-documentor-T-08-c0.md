# T-08 documentor receipt

**Result:** PASS. DEC-174 now lists `branch-create-gate.py` in the current enforcement-layer enumeration without changing the category-governs wording or removing any pre-existing Python filename.

## Changed locations

- `.harness/harness/docs/DECISIONS.md:4408-4412` — DEC-174 paragraph beginning **The enforcement layer, enumerated:**; added `branch-create-gate.py`. The existing `check-domain.py`, `bash-write-guard.py`, `validate-digest.py`, `check-state.py`, `check-plan-routes.py`, and `dispatch-guard.py` entries remain.
- `.harness/harness/docs/DECISIONS-INDEX.md:178-232` — generator-updated source anchors from DEC-175 through DEC-232 after DEC-174 gained one source line. The generated DEC-174 row remains at `.harness/harness/docs/DECISIONS-INDEX.md:177` with the current `@4344` anchor and unchanged ruling.

## Regeneration and verification

- Before editing, the live T-08 `verify:` string was cross-checked and matched the dispatched command exactly.
- Regeneration command, run from the feature worktree: `python3 .claude/skills/harness/bin/gen-decisions-index.py`
  - Exit: 0
  - Output: zero bytes
- Signed T-08 verification command, run exactly once after both documentation files were updated: `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`
  - Exit: 0
  - Diff output: zero bytes
- Focused re-read confirmed `branch-create-gate.py`, all six prior Python filenames, the unchanged category-governs wording, and the generated/current DEC-174 `@4344` index anchor.

## Files touched

- `.harness/harness/docs/DECISIONS.md`
- `.harness/harness/docs/DECISIONS-INDEX.md`
- `.harness/harness/features/BUG-285-canonical-reader/notes/receipt-harness-documentor-T-08-c0.md`
