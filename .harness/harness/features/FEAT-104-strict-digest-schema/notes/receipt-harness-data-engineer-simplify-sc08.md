# Receipt — harness-data-engineer — simplify/reuse — SC-08 assertion delta

BLUF: PASS, no findings — the new four-clause `and`-chain matches the file's established idiom (inline conjunction of `returncode` + `in ... .stderr` clauses inside a case tuple); no substring-set assertion helper exists anywhere in the file to duplicate, and none should be proposed at `med`+ severity for a 9-case file.

## What I checked

Read the whole file (`tests/integration/test-check-domain.py`, 190 lines) end to end: `_state`, `_fire_new`, `_full_step_state`, `_existing_write` (helpers, lines 22–73) and every case builder — `_undeclared_cases` (76–90), `_evidence_cases` (93–113), `_declared_shape_case` (116–126), `_floor_creation_cases` (129–147), `_floor_update_cases` (150–162) — plus `_report` (165–177) and `run_t06_cases` (180–186).

**No helper anywhere asserts a set of substrings against `stderr`.** Every case in every builder inlines its predicate directly as the second element of its `(name, bool, result)` tuple: `returncode == N and "x" in result.stderr [and "y" in result.stderr ...]`. This is the file's one idiom for asserting expected failure content — used 6 times across the 9 cases that check stderr content, with anywhere from one to three `in ...stderr` clauses chained by `and`.

**Closest sibling, as directed:** `_floor_creation_cases()`'s string-2 case (`test-check-domain.py:144-146`):
```
string.returncode == 2 and "schema_version floor" in string.stderr and "string" in string.stderr
```
— returncode + 2 stderr substring clauses, same `and`-chain shape. The new version-2 case (`:85-89`) is `returncode == 2` + 3 stderr substring clauses — one clause longer, same pattern, same file, same idiom. It does not introduce a new spelling.

**`DECLARED` (`:14-19`) and the schema read in `_declared_shape_case()` (`:116-126`):** checked; the delta does not touch either — confirmed by `git diff 168f875f..790023f0 -- tests/integration/test-check-domain.py`, which shows only lines 85–89 changed.

**Q7 (standing predicate-spelling residual across check-domain.sh/check-state.sh):** carried forward, not re-raised — out of this file's scope entirely.

## Emitter cross-check

`check-domain.sh:1653-1658` (`undeclared step key or evidence shape.` head + `offending key(s): …` body naming `run-state-schema.json` and the backtick-quoted `` `evidence` `` guidance) is the single source the assertion targets. The new clauses (`"run-state-schema.json" in strict.stderr`, `` "`evidence`" in strict.stderr ``) each match literal substrings the emitter actually produces — the assertion is not vacuous and does not test for text the emitter can't emit.

## Findings

`[]` — none at any severity. The chain is not a re-implementation of an existing importable/local helper; no such helper exists to duplicate, and the file's one established idiom for this exact job is precisely what the new clauses use.

`would_have_applied: false` — there is nothing to apply; DEC-174 read-only was moot for this angle's conclusion.

## Weakest-sufficient-form verdict

The four-clause `and`-chain is already the weakest sufficient form for this file: it matches the established one-idiom convention (no new spelling, no new abstraction), and each clause pins a distinct, real substring the emitter produces (denial code path, undeclared-key phrase, the offending key name, the schema-file route, and the `` `evidence` `` field name) — nothing in it is redundant with another clause.
