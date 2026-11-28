# BUG-2565 — panel cycle 3 apply (form fix + record)

**BLUF.** The one low form finding is fixed in T-01's `verify:`. The two med substance findings stay open for the operator. The panel is recorded as cycle 3. PF-9a0f… is now resolved by T-01. `plan-merge.py check` reports 6 tasks, 36 anchors and 0 failures (exit 0). `approval.status` is still `pending`, and no `APPROVAL-RESET:` receipt was printed.

## Finding → disposition map

| PF | Sev/kind | Disposition | Change |
|---|---|---|---|
| PF-6cd5d02cb2ff1de49c5f2a16a5be474f (T-01 Result grammar vs blank-line handling, new c3) | low form | applied, left `open` for the operator's panel ruling | I kept the prose rule ("exactly these twelve lines … nothing else"), and the parser now matches it. The T-01 `verify:` loop changed from `for line in [x for x in lines[b[0] + 1:e[0]] if x.strip()]:` to `for line in lines[b[0] + 1:e[0]]:`. A blank line inside the block now fails the key regex and is reported as `stray line in Result block: `. The T-01 intent is unchanged. |
| PF-3e23c499bba318c133baf80026c1592a (T-01: equal totals do not prove every invocation matched, new c3) | med substance | open, **carried to the operator**, not applied | none |
| PF-50024d3fe46e0d0aeb31788c55e947bf (T-02: identical batch task strings, new c3) | med substance | open, **carried to the operator**, not applied | none |
| PF-9a0f853dff44e05bcf533eebd405abac (T-01 refusal threshold vs Run C) | high substance | **resolved, resolved_by T-01** | The reader graded it CLOSED (`notes/review-harness-code-reviewer-plan-c3.md`) |
| PF-cbf8dece633693ce07ab5a284be1a0cf | high substance | stays open | The reader graded it PARTIAL |
| PF-25a87adffad1fd1f463f52b21ddb5b3e | high substance | stays open | The reader graded it PARTIAL |
| PF-120f5374d27296822e9d10ea9d8adab9 | med substance | stays open | The reader graded it PARTIAL |

No other disposition changed. PF-64c3… and PF-3425… are still resolved from cycle 2. PF-dc87…, PF-7436…, PF-d6fb…, PF-24f8…, PF-6b29… and PF-09df… are still open. The panel now holds 15 findings: 3 resolved and 12 open.

## Mechanics
- `apply` (proposal on stdin, T-01 `verify` only) printed `REPLACED T-01.verify` and `APPLIED`, exit 0. No `APPROVAL-RESET:` was printed, so `gh-sync.py status` was not run. Its check-state output listed existing tree-level VIOLATIONs that this edit did not cause: the brief is unapproved, INV-29 for the FEAT-2557 worktree, and INV-37 for the Build-entry receipt.
- `record-panel --cycle 3 --digest runs/2026-11-27-04-plan-product/panel-c3.md` added the three PF ids above, carried the 12 earlier findings byte for byte, and set `last_run: 2026-11-27-04-plan-product`. Exit 0.
- `set-panel --value-file notes/research-panel-c3-set-panel.yaml` holds the whole panel mapping, with only PF-9a0f… changed to resolved/T-01. Exit 0.
- `check --root <worktree>`: 6 tasks, 36 anchors resolved, 0 failures, exit 0.
- `approval:` was not touched and is still `status: pending`. No builds or tests were run.
