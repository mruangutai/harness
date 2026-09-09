# Receipt — harness-backend-dev — simplify apply (REUSE-2)

## BLUF

Applied REUSE-2 exactly as specified: one hunk in `_check_product_configs`
(`.claude/skills/harness/bin/factory_config.py`). Both suites green. No repair
cycle needed. Nothing else touched.

## The edit

`_check_product_configs`'s `--repo` narrowing previously called `repo_entry(fleet,
repo_name)` for its validating side effect only, discarded the returned entry, then
re-derived the same "match by name" rule with a list comprehension using a different
accessor (`e["name"]` vs. `repo_entry`'s `entry.get("name")`). Replaced the
two-statement narrowing with:

```
entry = repo_entry(fleet, repo_name)
fleet = dict(fleet, repos=[entry])
```

`repo_entry` still raises `FleetError` on an undeclared name, so the refusal path
via `factory_cli.run()`'s trap is unchanged. Validation and selection are now the
same call. The function's docstring already described the narrowing as "resolved
through repo_entry" — that claim was already true and is unchanged; no docstring
edit was needed. No comment narrating the change was added.

## Duplicate-name question

Grepped `tests/` for duplicate-repo-name fleet fixtures (searched "duplicate",
repo-shape fixtures in `test-fleet-product-config.py`, and `load_fleet`/`repos`
literal shapes). **No test or fixture anywhere in `tests/` exercises a fleet with
two entries sharing the same `name`.** `load_fleet` does not reject duplicate
names either.

Consequence of the edit: the old comprehension collected every matching entry
(silently coalescing duplicates into a >1-entry "narrowed" fleet); `repo_entry`
returns only the *first* match, so narrowing now always yields exactly one entry
regardless of whether the fleet has a live duplicate. The `declared`/`ok`/
`unreachable` payload counts stay self-consistent in both the old and new
behaviour, because `declared` is computed as `len(fleet["repos"])` *after*
narrowing in both versions — it never diverges from what `product_config_report`
actually walked. The only behavioural change on a (currently impossible, per the
grep above) duplicate-name fleet is that `--repo` now silently narrows to the
first-declared duplicate rather than reporting both — a narrower, more specific
result, not a new source of inconsistency. Not exercised by any existing test
because no such fleet fixture exists.

## Suites (exit status captured, not inferred)

- `run-unit-tests.sh --kind unit`: **exit 0**. Grepped `^FAIL ` — exactly 4 lines,
  all from `test-factory-claim-mutation.py` (which itself PASSed):
  ```
  FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
  FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
  FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
  FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
  ```
  Matches the known by-design baseline exactly — no others.
- `run-unit-tests.sh --kind integration`: **exit 0**, zero `^FAIL ` lines.

## Direct exercise of the changed path (throwaway script, `factory_gh.file_at_ref`
stubbed per `test-fleet-product-config.py`'s `patched_file_at_ref` convention)

- `_check_product_configs(fleet, "mruangutai/repo-one")` (declared member) →
  stdout payload `{"declared": 1, "ok": 1, "unreachable": 0, "members": [...]}`.
- `_check_product_configs(fleet, "mruangutai/does-not-exist")` (undeclared name) →
  raised `fc.FleetError: repository not in fleet: mruangutai/does-not-exist —
  known repos: mruangutai/repo-one, mruangutai/repo-two — ...`.

## git status --porcelain (verbatim)

```
 M .claude/skills/harness/bin/factory_config.py
 M .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-ai-dev-simplify-altitude.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-backend-dev-simplify-reuse.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-data-engineer-simplify-efficiency.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-simplification.md
```

`feature.json` and sibling receipts are concurrent activity from other agents in
this run, not touched by me and not reverted, per instructions.

## Not applied (backlogged by the lead, out of scope for this dispatch)

- REUSE-1 (`<repo>@<ref>:<path>` locator helper)
- REUSE-3 (shared test-fixtures module)

Neither was touched.
