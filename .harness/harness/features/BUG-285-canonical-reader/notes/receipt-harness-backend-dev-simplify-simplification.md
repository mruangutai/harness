# Simplification receipt — BUG-285-canonical-reader

**Angle:** simplification  
**Pinned diff:** `8c3143bd..2367a1881ea483d5326a23268dc034c2a3b82134`

## Assessment
One qualifying source-comment simplification was found. The reviewed change otherwise keeps its added strict-reader logic and permanent audit free of behavior-preserving simplifications that would disturb settled anchoring or assertion semantics.

## Findings

### SIMP-01
- **Surface:** code
- **Location:** `.claude/skills/harness/bin/factory_decompose.py:115-116`
- **Summary:** The two-line comment records BUG-285 migration history and restates the immediately following accessor call instead of only documenting the present local conversion.
- **Concrete cost:** The historical boundary explanation duplicates scope/architecture records and must be maintained when that boundary evolves; it also makes the local read path carry obsolete migration narrative.
- **Compatible alternative:** Replace both lines with one present-tense comment, e.g. `# Convert the validated factory record into this tool's local output shape.`, or remove them if the function body remains self-explanatory. This preserves the accessor call, validation boundary, and every assertion.
