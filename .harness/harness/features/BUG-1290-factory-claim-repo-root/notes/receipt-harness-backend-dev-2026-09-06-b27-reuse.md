# BUG-1290 · simplify · reuse angle — receipt

BLUF: one small, low-risk applyable finding (same-file duplicate report scaffolding in
`test-factory-claim-mutation.py`); the cross-file mutant-class duplication named in the dispatch is
real but NOT verbatim — reasoned NO to extracting it; scenario/helper reuse (`_case_line`,
`_run_suite`, `_run_5b_scenario`) is clean, no finding.

## Q1 — the two mutant `_BlockerCache` subclasses: verdict NO (do not extract)

`_FeatureOnlyIssueMapCache` (`tests/unit/test-factory-claim.py:1321-1328`) and
`_KeyCollapsingBlockerCache` (`tests/unit/test-factory-claim-mutation.py:159-175`, inside
`_mutate_and_run_key_collapse()`) share only the `__init__`/`issue_number` pair (~8 lines) that
collapses the cache key. They are NOT verbatim: `_KeyCollapsingBlockerCache` carries a class-level
`_reached` flag and a `print(..., file=sys.__stdout__)` marker that `_FeatureOnlyIssueMapCache` has
no equivalent of. That is load-bearing, not decorative — the mutation file drives the suite through
`runpy.run_path` + `_run_suite()`'s stdout-capture (line 82-91) and cannot otherwise observe whether
the mutant was exercised (B-27's reached-marker requirement, mirrored from `_MutantFactoryConfig`
at lines 46-79 in the same file). `test-factory-claim.py`'s 5g instead captures the verdict directly
through the `_capture` shim (line 1332-1333) and asserts the *specific* observable
(`mutant_out == ""`, `"952" in mutant_err`, etc.) — that strict assertion is itself the reach proof,
so it never needed a marker.

A shared home is technically feasible: neither file can import the other (`test-factory-claim.py` is
a script executed top-to-bottom via `runpy.run_path`, not a module — importing it runs the whole
suite), but both already import sibling modules from `.claude/skills/harness/bin` via the same
`_anchor_bin` sys.path insert (`test-factory-claim.py:15-19`, `test-factory-claim-mutation.py:27-31`).
A new tiny file, e.g. `tests/unit/_blocker_cache_mutants.py`, exposing a factory for the
`__init__`/`issue_number` pair, is buildable and importable by both.

**Cost of building it anyway:** a new file plus an import in two already-dense test files, to save
~7 lines that are each already wrapped in a longer, file-specific docstring explaining why THAT
file's copy needs (or doesn't need) the reached marker. The shared slice is smaller than the
docstrings around it. Net: more indirection for less duplication than it looks. **Not recommended.**

## Q2 — new arm's helpers vs `_mutate_and_run`/`_mutation_proof`: verdict YES, one real finding

1. **[rank 1 — recommended apply]** `tests/unit/test-factory-claim-mutation.py:128-147` vs
   `:185-201`. `_mutation_proof()` and `_key_collapse_proof()` share the same report scaffold:
   check `reached` → print `"...NEVER REACHED"` / `"...PROOF: INCOMPLETE"` / return False → look up
   case line(s) → print `"...MISSING: <id>"` / `"...PROOF: INCOMPLETE"` / return False on a miss →
   print the found line(s) → print a `"...PROOF: N/N ..."` success line → return True. The only
   real difference is the case-id list (`CASES` tuple of 3 vs the single literal `"5b"`) and the
   label strings (`"MUTATION"` vs `"KEY-COLLAPSE"`, `"BASELINE"` wording not involved here).
   **Concrete cost of leaving it duplicated:** a future change to the report contract (e.g. adding
   a fourth print line, changing the INCOMPLETE spelling QA greps for) has two call sites to edit
   in lockstep, and it is easy to update the one under active review and leave the older one stale
   — exactly the failure mode this feature exists to close.
   **Alternative:** one shared `_report_case_proof(output, reached, case_ids, label)` iterating
   `case_ids` (pass `("5b",)` for the collapse arm, `CASES` for the features-root arm), called by
   both `_mutation_proof` and `_key_collapse_proof`. Same-file, no cross-file coupling, no change to
   what gets asserted or printed — a pure restructuring, so it does not touch the HARD RULE (nothing
   about either gate's ability to report RED changes).
2. Whether a single parameterised pair (`_mutate_and_run` / `_mutate_and_run_key_collapse`,
   lines 117-125 vs 150-182) should merge: **NO.** One patches a module attribute
   (`factory_claim.factory_config`) and reads reach via an object method; the other patches a class
   attribute (`factory_claim._BlockerCache`) and reads reach via a class attribute. A generic
   `_patch_and_run(get, set, mutant, reached_fn)` for exactly two call sites trades a
   straightforward 9-line function for a harder-to-read indirection — not worth it.

## Q3 — `_case_line`, `_run_suite`, scenario builders: verdict NO finding, clean reuse

Both new call sites reuse the existing helpers rather than restate them: `_key_collapse_proof`
calls the existing `_case_line()` (`:94-102`) and `_mutate_and_run_key_collapse` calls the existing
`_run_suite()` (`:82-91`) unchanged. In `test-factory-claim.py`, the new `_emit_5b(record)`
(`:1226-1232`) reuses `_run_5b_scenario()` (`:1188-1205`) and `_5b_property_holds()` (`:1208-1223`)
verbatim — 5g's `_capture` path (`:1332-1333`) is the only new code, and it is a report shim, not a
scenario reimplementation. Nothing in scope reimplements a scenario builder.

## Ranked findings for the lead

1. Extract `_report_case_proof(...)` shared by `_mutation_proof`/`_key_collapse_proof` — same-file,
   no assertion weakened, cheapest to verify (re-run both suites after). **Recommended for the one
   allowed apply.**
2. Cross-file mutant-class sharing (Q1) — real but reasoned NO; not applyable, backlog only if
   ever revisited.
3. `_patch_and_run` merge (Q2.2) — reasoned NO, not applyable.

No finding proposes deleting or weakening any assertion; nothing here touches the HARD RULE.

## Verification run (read-only)

```
env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py
  -> 125/125 checks passed.  (exit 0)
env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py
  -> MUTATION PROOF: 3/3 cases reddened
     KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed  (exit 0)
```
