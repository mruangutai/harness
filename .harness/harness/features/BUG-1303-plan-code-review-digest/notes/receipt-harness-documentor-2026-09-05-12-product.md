# Receipt — harness-documentor — BUG-1303 T-04 fix (mirror-site pointer)

**BLUF.** DEC-216's mirror-site pointer named `required_by_persona` in
`run_documented_contract_cases`; it now names `_required_contracts`, which
`run_documented_contract_cases` calls. That is DEC-216's whole payload — the site a future inline
per-persona extension in `validate()` must also update — so the stale name defeated the entry.
One clause changed, plus the wrap it forces on the rest of the paragraph. Verify exits 0.

## Why the plan's identifier went stale

The plan text for T-04 was written before main-session commit `8596745f`, which refactored
`tests/integration/test-validate-digest.py`: the per-persona required-field mapping — including the
reviewer's inline extension `required["harness-code-reviewer"].update(("code_grade", "reviewed"))` —
now lives in `_required_contracts` (def at line 385). `run_documented_contract_cases` (line 475)
only calls it (line 482). `required_by_persona` survives solely as the parameter name of
`documented_contract_results` (line 317), i.e. a consumer, not the mirror. The documentor followed
the plan; the plan's identifier rotted under it.

## The sentence as it now reads on disk

`.harness/harness/docs/DECISIONS.md`, DEC-216, paragraph `**The check runs one way.**`,
lines 6806–6810 (hard-wrapped ~100 cols; line breaks marked `⏎`):

> those plus the reviewer's inline per-persona extension, `code_grade` and `reviewed`, which `validate()` ⏎
> applies in code rather than as data: `_required_contracts`, which `run_documented_contract_cases` ⏎
> calls (`tests/integration/test-validate-digest.py`), is that extension's hand-written mirror, so a ⏎
> future inline extension must update that site or the guard silently under-checks the persona it ⏎
> extends.

Everything else in DEC-216 is byte-unchanged; the only other delta is the re-wrap the longer clause
pushes into the following "Scope is the persona's own block…" sentence (same words, new line
breaks). `git diff --stat`: `1 file changed, 6 insertions(+), 5 deletions(-)`.

## Commands and outputs

T-04's `verify:` (cross-checked against `plan.yaml:546` under `- id: T-04` at line 533 — byte-equal
to the dispatch), run verbatim from the worktree root after regenerating the index with
`.agents/skills/harness/bin/gen-decisions-index.py` (exit 0):

```
grep -qF "documented output block" .harness/harness/docs/DECISIONS-INDEX.md && .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff -q - .harness/harness/docs/DECISIONS-INDEX.md
verify exit=0                 # diff printed zero bytes: index == its regeneration
```

Regeneration left `DECISIONS-INDEX.md` byte-identical (it is absent from `git status`), because
DEC-216 is the last entry, so its body growing by one line shifts no other row's `@line` anchor.

```
grep -n "required_by_persona" .harness/harness/docs/DECISIONS.md
old exit=1                    # zero bytes of output; absence is the pass condition

grep -n "_required_contracts" .harness/harness/docs/DECISIONS.md
6807:applies in code rather than as data: `_required_contracts`, which `run_documented_contract_cases`
new exit=0                    # exactly one line
```

```
git status --porcelain
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/qa-BUG-1303-build.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-ai-dev-simplify-altitude.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-backend-dev-simplify-reuse.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-backend-dev-simplify-simplification.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-dev-ops-simplify-efficiency.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/observations/harness-qa.md
```

Only `DECISIONS.md` outside the feature directory. `feature.json`, `plan.yaml` and the six
untracked notes/observations were already dirty at spawn (siblings' work), not touched by me; this
receipt adds one more untracked path under the feature dir. Nothing staged, no commit, HEAD unmoved.

## Caveat on the verify's reach

T-04's `verify:` only proves the index carries the phrase "documented output block" and matches its
regeneration. No clause tests the identifier — the substance of this fix is covered solely by the
two greps above plus my read of `tests/integration/test-validate-digest.py` at lines 317, 385, 475
and 482.
