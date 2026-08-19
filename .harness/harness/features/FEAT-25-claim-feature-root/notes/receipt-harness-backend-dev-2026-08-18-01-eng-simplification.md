# SIMPLIFICATION angle — FEAT-25 plan surface — receipt

## Finding 1 — the "untouched files" rule is spelled twice in BRIEF.md with different membership

- **File**: `.harness/harness/features/FEAT-25-claim-feature-root/BRIEF.md`
- **Lines**: 87 (Constraints) vs 73-75 (SC-08)
- **Summary**: BRIEF Constraints says "Do not touch `.harness/factory/fleet.yaml`,
  `.harness/harness.json`, `gh_board.py` or `load_board`." SC-08 says "No file outside
  `.claude/skills/harness/bin/` is modified, and `factory_config.py`, `fleet.yaml`,
  `harness.json`, `gh_board.py` and `check-domain.sh` are untouched." These are the same fact
  (the forbidden-touch set) spelled with two different memberships: SC-08 adds
  `factory_config.py` and `check-domain.sh`, which Constraints never names as off-limits;
  Constraints names `load_board`, which SC-08 (a file-only list) cannot express.
- **Concrete cost**: SC-08's verify is `inspection`, not automated — nothing greps for this.
  A reader who checks only Constraints before touching `check-domain.sh` or adding a
  `factory_config.py` API sees no prohibition there; only SC-08, read separately at review
  time, would catch it. The two lists can drift further apart on a future edit to either one
  and nothing would notice.
- **Alternative**: state the forbidden-touch set once (Constraints is the natural home,
  since it is read before execution, not just at review) and have SC-08 reference it rather
  than restate it independently.
- **Severity**: low. **must_fix/advisory**: advisory — each task's own `files:` allowlist
  (T-01/T-02: `factory_claim.py` + its two test files; T-03: `layout_migration.py`,
  `layout_fixtures.py`, `test-layout-migration.py`) already bounds what gets touched in
  practice, so the drift is a documentation-hygiene risk, not a live execution risk on this
  plan as staged.

## Counter-rule check — confirmed load-bearing, not flagged

`layout_migration.py:81-89`'s `# balance: (` comment convention, which T-03's new
`factory_claim.py` row must also carry: read the docstring block at `layout_migration.py:81-86`
in the tree — it states plainly that `test-check-plan-routes.py case_20` joins physical lines
until paren depth balances, counting parens inside string literals, so an unmatched paren in a
new row's pattern string merges the whole table into one logical line. This is exactly the
"anchor that took rounds to get right" the SKILL calls out — not simplifiable, and T-03's intent
correctly requires the same convention on the new row. No finding here; explicitly not flagged.

## Known advisory (T-01 prose corrections ungated by verify) — CONFIRMED

Checked directly: T-01's verify block greps only the `factory_claim.py:43` constant, the two
new `test-factory-claim.py` ok-line texts/counts, and the `test-factory-integration.py` legacy
two-segment absence. None of its three grep/python checks touch `factory_claim.py:25-27`
(docstring), `test-factory-claim.py:5` (docstring), or `test-factory-integration.py:31`
(docstring paragraph) — the comma-form grep pattern used (`'".harness", "features")'` and
the three-segment positive) cannot match the slash-form prose these lines carry after a
prose-only edit, or catch a prose-only *omission*. The advisory is real: those three
corrections are intent-only, unverified by `verify:`. Carrying it deliberately (as stated) is a
legitimate call, since intent is still binding on the executing agent — but it remains true that
a doer who fixes the constant and skips the docstring sentences leaves T-01 GREEN.

## No other SIMPLIFICATION findings

Checked and cleared, not flagged:
- Ok-line text pairs (intent prose vs `verify:` `hasok` calls) in T-01/T-02/T-03 are
  character-identical, not two independent spellings that can drift — this is the plan's
  standard pin-then-verify pattern used throughout the tree, not new complexity.
- Ok-line count thresholds (T-01: 115 = 113+2, T-02: 119 = 115+4, T-03: 41 = 40+1) are
  internally consistent between the intent's stated new-case counts and the verify's
  arithmetic.
- REQ-02/SC-04/D-03/T-02-intent all describe the same no-plan-vs-edge-(i) split, but as a
  requirement -> success criterion -> decision -> task-intent chain, not duplicate
  independent assertions — this is the plan's normal traceability layering, not drift risk.
- T-03's inline audit-quote (five grep lines in the intent) matches the precedent already
  recorded in `layout_migration.py`'s own docstring (line 72-73: "the audit is quoted in
  FEAT-20's plan.yaml T-01 intent, per row"), so quoting the audit in T-03's intent rather
  than in code is reuse of an established convention, not new redundancy.
