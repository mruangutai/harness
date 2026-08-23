# T-08 decision renumber — DEC-197 → DEC-200

T-08's `verify:` and `intent:` now name **DEC-200**, which is the next free decision number.
The task was unsatisfiable as signed: DEC-197 already exists with other content, so a grep for
`^## DEC-197 ` passed against someone else's entry and writing one would have duplicated or
overwritten a signed heading.

## Number re-derived independently (worktree, 2026-08-23)

```
grep -oE '^## DEC-[0-9]+' .harness/harness/docs/DECISIONS.md | grep -oE '[0-9]+' | sort -n | tail -1
  -> 199
grep -oE '^- DEC-[0-9]+ @' .harness/harness/docs/DECISIONS-INDEX.md | grep -oE '[0-9]+' | sort -n | tail -1
  -> 199
grep -rn 'DEC-200' .harness   -> only runs/t08-product/{state.yaml,digest.md} (dispatch notes)
```

Both authorities top out at 199 and nothing claims 200. **Agrees with the operator's DEC-200.**
DEC-197 = the two-`detect`-globs decision, DEC-198 = `orchestrator_context_warn_tokens`,
DEC-199 = `harness_merge` — all three landed after T-08 was signed.

## Occurrence count: the dispatch undercounted

The dispatch said six occurrences (five in `verify:`, one in `intent:`). Actual count in T-08 was
**ten** — `verify:` carried nine on lines 632, 633, 637, 639, 640, 642, 645, 646, 647 (the python
heredoc's error strings and the `print` were not in the dispatch's list), plus one in `intent:`
line 653. All ten were changed; `grep -c DEC-197 plan.yaml` is now 0 and `DEC-200` appears exactly
ten times, all inside T-08.

## Constraints held

- `approval:` byte-unchanged — `git diff` on the file shows no hunk touching it; keys still
  `approved_by, date, status`.
- `verify: |` intact (line 631); `yaml.safe_load` parses, T-08's `verify` holds 18 newlines.
- Only T-08 lines appear in my diff hunks (632-653). The `status: pending -> building` hunks at
  109/179/265/347 pre-existed in the working tree and are not mine.
- `check-plan-routes.py` exits 0 (the two T-05/T-06 DEVIATION lines are pre-existing advisories,
  not violations).
- Nothing committed.

## Open item for whoever executes T-08

`intent:` line 653 still carries backticks around the decision heading (`` `## DEC-200` ``), which
DEC-182 forbids in plan values. Out of scope for this repair — left as-is rather than widened.
