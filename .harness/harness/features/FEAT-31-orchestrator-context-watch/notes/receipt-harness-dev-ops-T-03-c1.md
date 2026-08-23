# Receipt — harness-dev-ops — T-03 — c1

## Task
T-03: add `orchestrator_context_warn_tokens` (200000, int) and
`_orchestrator_context_warn_tokens_rationale` to the `budgets` object in
`.harness/harness.json`. Cross-checked the dispatch's quoted `verify:` against plan.yaml's
own T-03 block — byte-identical, no mismatch.

## Change
File: `.harness/harness.json`, `budgets` object only. Appended the two new keys after the
existing `_max_total_cycles_rationale` entry, preserving key order and two-space indent.
`log_retention_days: 30` (sibling, above `budgets`) untouched. `gates`, `test_matrix`,
`test_kinds` untouched — confirmed by diff below.

Rationale string states, per intent: this is a CONTEXT token count not money (DEC-178
removed cost tracking, this does not reintroduce it); 200000 is DEC-148's deleted watchdog
figure, kept not re-guessed; crossing it advises and never refuses; and the measured
distribution — 28/76 orchestrator transcripts peaked above it, 10 above twice it, largest
750837, corrected method, measured 2026-08-20 within the 30-day retention window. **These
figures are the plan's own measurement (D-11 in plan.yaml, and cited in T-03's intent
verbatim), relayed here — not independently re-derived by me.**

## verify: — run verbatim from plan.yaml T-03

```
python3 -c "import json;d=json.load(open('.harness/harness.json'));assert d['budgets']['orchestrator_context_warn_tokens']==200000, d['budgets'];print('VERIFY-OK')"
```
Output: `VERIFY-OK`
Exit status: `0`

## Standing duty — what would make this verify fail

The command loads the JSON, indexes `budgets['orchestrator_context_warn_tokens']`, and
asserts `== 200000` (a Python `int` literal). It WOULD fail (non-zero exit, `AssertionError`
printing the whole `budgets` dict) on:
- the key absent (`KeyError`, also non-zero)
- the value written as anything not equal to the int `200000` — **including the STRING
  `"200000"`**. In Python, `"200000" == 200000` is `False`, so a string-typed value is
  caught, not passed vacuously.
- any other integer value (e.g. 199999, 400000)

It would NOT fail, and gives NO coverage at all, on:
- the rationale key `_orchestrator_context_warn_tokens_rationale` being **absent entirely**
- the rationale string being **present but wrong/garbled/missing required content**
- key order or indentation drifting
- any other part of the file being touched (gates, test_matrix, test_kinds)

The rationale content is UNASSERTED by this gate — it is enforced only by the intent's prose
and by manual review, not by any automated check. Stating this plainly rather than implying
coverage exists.

## Supplementary checks (this dispatch's "standing duty")

- `python3 -c "import json; json.load(open('.harness/harness.json'))"` — exit `0`, no output.
  JSON syntax break proven absent.
- `git -C .../FEAT-31 diff --stat -- .harness/harness.json` → `1 file changed, 3 insertions(+),
  1 deletion(-)` (the deletion is the pre-existing line gaining a trailing comma, not content
  loss).
- `git -C .../FEAT-31 diff -- .harness/harness.json` → confirmed the only hunk touched is
  inside `budgets`; no lines outside it appear in the diff.
- `git status --porcelain` at the end shows other files modified/untracked in this shared
  worktree (STATE.md, feature.json, plan.yaml, observations, context-watch.py, other
  receipts) — these are concurrent work from other lanes (T-01 etc.), not touched by me. Only
  `.harness/harness.json` reflects my change.

## Decisions consulted
DEC-160 @3996 (a decision adding a harness.json key must say so — T-09's job, not mine, noted
and left alone), DEC-148 @3553 and DEC-178 @5015 (source of the two cited figures/claims in
the rationale).

## Scope respected
Did not touch `test_kinds` (T-11's territory), `gates`, or `test_matrix`. Did not touch the
harness.json template (T-04, main-session-direct) or write any decision entry (T-09).
