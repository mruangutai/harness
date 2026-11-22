# Receipt — harness-backend-dev — r-20261121-simplify-eng — angle: reuse

BLUF: 1 finding (T-01 plan text invites a third decisions-index parser and a second DEC-section locator where importable ones exist). Route: fold-in to pm. Everything else on the reuse angle is clean or settled. Read-only; nothing edited, nothing run.

## Finding R-1 — T-01 re-specifies index-STRUCK and DEC-section parsing that already exist

- File/line: `.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml` T-01 intent, lines 184-200 ("Reuse ... the established index format for STRUCK status ... locate the exact decision heading's section up to the next same-level heading"). The plan names reuse for anchor normalization only, and for the index only as a "format".
- Summary: the plan leaves the implementer to write new code for (a) reading DECISIONS-INDEX.md into {DEC: struck?} and (b) slicing a DEC section out of DECISIONS.md. Both exist:
  - (a) `bin/check-plan-routes.py:2394-2407` `_decisions_index(root)` returns exactly {DEC-NNN: struck?}. `plan_merge/check.py:59` already loads that module as `routes.cpr` in `cmd_check`, so it is one attribute away. The row regex also lives at `bin/gen-decisions-index.py:81` (`ROW_RE`), so a third spelling would make three.
  - (b) `bin/gen-decisions-index.py:109-130` `parse_decisions(text)` returns key -> {line, body} per `## DEC-N` heading, ending at the next DEC heading. It is loadable via `harness_boundary.load_repo_module` (`bin/harness_boundary.py:533`), the sole sanctioned loader (`check-plan-routes.py:1694`).
- Concrete cost: three index parsers and two section slicers edited in lockstep. They already disagree. `_decisions_index` uses a case-sensitive `startswith("STRUCK")` (`check-plan-routes.py:2406`), but the live index carries a title-case "Struck" (`.harness/harness/docs/DECISIONS-INDEX.md:97`, DEC-86). T-01 requires case-insensitive STRUCK detection, so a new parser fixes the miss only for itself. The existing authority audit (`check-plan-routes.py:2410-2428`) keeps reading DEC-86 as live. Likewise `parse_decisions` strips ``` fenced lines (`gen-decisions-index.py:89-106`), so a clause quoted from inside a fence would differ between the two slicers.
- Alternative: say in T-01's intent that the check calls `routes.cpr._decisions_index` (extended to be case-insensitive and to take the segment's index path) and `gen-decisions-index.parse_decisions` via `load_repo_module`, rather than new parsers. Pin one rule for fenced text in the clause check, since "exact substring" is currently ambiguous against the defenced body.
- Route: fold-in to pm. It is a one-sentence intent edit. It does not weaken any assertion: the exact-substring, STRUCK-keep/amend and wrong-section tests all stay. Caveat for pm: widening `_decisions_index` to be case-insensitive changes `check-plan-routes` behaviour (it could newly flag a cited Struck authority). T-01's files list does not name check-plan-routes.py, so pm should either add it as an anchor or have the new check wrap the helper locally. Either choice is pm's.

## Clean on this angle (no finding)

- Ownership anchor normalization: T-01 already says to reuse it (`plan_merge/check.py:73` `_literal_paths`). Settled.
- Writer routes: T-01 uses `panel._set_top_key` and `union._merge_plain_key` and adds no new write route. Settled.
- Grading return shape: T-02 reuses the `sc_status` contract with no new schema. Settled.
- T-03 verify reuses `gen-decisions-index.py --stdout | diff`. It re-implements nothing.
- Five-field block restated in template, plan draft prompt, patch-lane and pm Mode 2 (T-02): this is the operator-settled design, SC-04/SC-07 require an assertion per canonical owner, and the panel already applied the trims. Leave.

## Principles applied
- Redesign From First Principles (read this run): had "index status and DEC sections" been part of the design from the start, the new check would sit on the existing readers, not beside them. This shaped R-1's alternative.
