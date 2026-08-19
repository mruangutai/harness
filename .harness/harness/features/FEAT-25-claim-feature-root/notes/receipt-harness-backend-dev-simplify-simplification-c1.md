# SIMPLIFICATION receipt — FEAT-25-claim-feature-root, angle c1

**BLUF:** One low-severity finding on `factory_claim.py`. Everything else in the six-file diff
is either mandated plan text (SETTLED / LEAVE list), or genuinely load-bearing anchoring the
diff fought to get right — nothing to trim there.

## Finding 1 — duplicated prefix across `_blocker_reason_text`'s `no_plan` branch

- **File:** `.claude/skills/harness/bin/factory_claim.py`
- **Lines:** 189–199 (the `if kind == "no_plan": ... return (...) \n return (...)` pair)
- **Summary:** the two return statements share an ~80%-identical prefix
  (`"issue #{num} carries a feature: label that resolves, but no plan could be [read] at
  {path} - "`), split only by where the line wraps and by the trailing clause
  (`"the feature root does not exist"` vs `"the feature directory or its plan.yaml is missing or
  unparseable"`).
- **Concrete cost:** if the shared prefix ever changes (wording, issue-number format, etc.), two
  near-identical f-strings must be edited in lockstep; a future editor fixing one copy and
  missing the other ships a silently inconsistent pair of otherwise-parallel messages.
- **Concrete alternative:** collapse to one return with the branch reduced to a single suffix
  variable, e.g.
  ```python
  suffix = ("the feature root does not exist" if not root_exists else
            "the feature directory or its plan.yaml is missing or unparseable")
  return (f"issue #{num} carries a feature: label that resolves, but no plan could be read "
          f"at {path} - {suffix}")
  ```
  Produces byte-identical output text for both branches.
- **`verify:` grep check:** T-02's verify (plan.yaml lines 232–266) checks this branch only
  behaviourally — `absent in text` and `"no matching plan task" not in text` via a Python probe,
  plus `test-factory-claim.py` ok-line greps on the *test case names*, not the source text. No
  `verify:` clause greps the literal strings `"the feature root does not exist"` or `"the feature
  directory or its plan.yaml is missing or unparseable"` inside `factory_claim.py` itself — I
  grepped both plan.yaml and the source for these phrases and the only occurrences are the plan's
  own `intent:` prose (lines 322–326, which specifies the two full sentences as required *output*
  text, not as a mandated *source shape*) and the two return statements. **Safe to apply**;
  produces identical emitted text.
- **Severity:** advisory / low — two extra lines, no runtime cost, no risk. Backlog-worthy, not
  urgent.

## Checked and found clean

- `_BlockerCache.plan_path`, `_plan`, `plan_loaded`, `root_exists`, `task` (`factory_claim.py`
  ~lines 98–133): four short single-purpose methods added around one shared private loader. No
  redundant conjuncts, no dead code. `_plan()`'s docstring sentence about "the sole file-reading
  path" is LEAVE-listed (item 7) — did not touch.
- `FEATURES_ROOT` constant line and its two docstring paragraphs (`factory_claim.py` :19–23,
  :44): the three-segment join is unchanged in shape from the pre-diff two-segment join, just a
  literal segment added. LEAVE-listed (item 1) — did not touch, and the reformatted paragraph
  above it is prose tightening the diff itself did, not something I need to re-tighten.
- `layout_migration.py`'s new `READER_TABLE` row and its `# balance: (` comment: LEAVE-listed
  (item 2) as the highest-risk item on this angle. Confirmed the comment is untouched and the
  regex `r'"\.harness", [^,)]+, "features"'` still matches. No proposal.
- `layout_fixtures.py`'s new `factory_claim.py` STUB entry (4 lines): a plain legacy/migrated
  fragment pair matching the established shape of every other entry in the table. Nothing to
  simplify — it is already minimal.
- `test-factory-claim.py`'s new module-scope RED-pinning pair (`check(...)` x2) and the B5-ter /
  sc13b_fixture additions: straightforward, no redundant conjuncts. The inline comment
  immediately above the two module-scope checks (lines 29–32 of the diff) restates the module
  docstring's "deliberate exception" sentence in different words. I considered flagging this as a
  duplicate-fact-in-two-places, but it does not cleanly fit any of my angle's three code-surface
  categories (redundant conjunct / comment narrating a *change* / simplifiable pipeline) — both
  statements assert a present fact, not a change, and locating the same fact once in an overview
  docstring and once at the point of use is a defensible readability choice, not waste. Not
  flagged; noting it here rather than manufacturing a finding.
- `test-factory-integration.py`'s docstring/path updates and `test-layout-migration.py`'s case 22:
  mechanical `.harness/features` → `.harness/harness/features` substitutions plus one new case.
  No added complexity. Case 22 and the report block are DO-NOT-TOUCH (LEAVE item 4) — did not
  read them as a change surface, only confirmed the diff doesn't touch lines 412–419.
- The "seven"→"eight" test-count updates: LEAVE item 5 says leave `test-factory-claim.py:997,1003`
  (stale "seven" labels); the ones I saw in the diff (lines ~99–105, ~113, ~140–146) are *correct*
  updates from seven to eight reflecting the new no_plan branch, not the stale pair — did not
  touch either way.

```yaml
VERDICT: PASS
DIGEST:
  headline: one low-severity SIMPLIFICATION finding (duplicated prefix in factory_claim.py's no_plan reason branches); rest of the six-file diff is either mandated plan text or already minimal
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-25-claim-feature-root/notes/receipt-harness-backend-dev-simplify-simplification-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-25-claim-feature-root/notes/receipt-harness-backend-dev-simplify-simplification-c1.md
```
