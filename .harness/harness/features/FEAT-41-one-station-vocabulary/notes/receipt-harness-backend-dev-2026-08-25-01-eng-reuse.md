# REUSE angle — FEAT-41 plan.yaml, read-only

One finding. Everything else checked (T-01 verify grep, T-08's gh-close-gate.py model, T-10's
`harness_boundary.WORKTREES_SEGMENT`/`worktree_owner`, T-06's `project()`, T-09's SHAPE_PATTERNS
vocabulary rule) is either already-correct reuse the plan itself cites, or genuinely new logic
with no existing script performing it — confirmed by reading the cited files, not assumed.

## Finding: TERMINAL_MARKER declared "once" (D-05, T-03) but restated as a bare literal in two
other tasks

- **Files/lines**: `plan.yaml` T-03 intent (`declare TERMINAL_MARKER = "abandoned" once in this
  module`, plan-merge.py), T-04 intent (`the terminal marker "abandoned"` — twice, once for the
  legal-set check and once for `FINISHED_STATUSES = ("done", "abandoned")`), T-09 intent (`... or
  the terminal marker` in check-domain.sh's new VOCABULARY shape rule, no import named).
- **Verified against the tree**: `plan-merge.py` (`.claude/skills/harness/bin/plan-merge.py:1-40`)
  is a CLI, never imported as a module by any other bin script today (`grep -rn "import plan_merge"
  .claude/skills/harness/bin/*.py` returns nothing). `check-plan-routes.py` currently declares its
  own `LEGAL_TASK_STATUSES` tuple (line 415) and does not import `factory_config` today — but T-04's
  own intent already adds that import (`factory_config.station_names`). `check-domain.sh` imports
  local bin modules only inside function bodies (`import feature_schema`, `import harness_boundary
  as _hb`), never at module top — the same pattern T-09 would need for a `factory_config` import.
- **Summary**: D-05's mandate is "declared once in code" and T-03 places that single declaration
  inside `plan-merge.py`, a script no other file in the plan imports as a module. T-04 and T-09 each
  independently write the bare string `"abandoned"` rather than importing T-03's constant — three
  independent spellings of the same terminal marker across `plan-write.py`, `check-plan-routes.py`,
  and `check-domain.sh`.
- **Concrete cost**: exactly the cost this angle exists to name — if the terminal marker's spelling
  or the constant's name ever changes, three call sites move in lockstep and the plan as written
  gives no mechanism (no shared import) forcing that; the one nobody remembers goes stale silently.
  It also makes D-05's own claim ("declared once in code") false the moment T-04 and T-09 land as
  currently specified — the decision record would assert something the shipped code does not do.
- **Alternative**: move `TERMINAL_MARKER = "abandoned"` into `factory_config.py` (T-01's own module,
  already the stated single home for `MANDATED_STATIONS`) instead of `plan-merge.py`. T-04 already
  imports `factory_config` for `station_names`, so its two literal spellings become one import. T-09
  already has the local-import-inside-function pattern for exactly this kind of dependency
  (`feature_schema`, `harness_boundary`), so importing `factory_config.TERMINAL_MARKER` there costs
  nothing structurally new. `plan-write.py` (T-03) would then import it from `factory_config` too,
  making all three call sites read one declaration instead of one declaration plus two literals.

Not a blocker — flag-only, for `harness-pm` to apply or decline.
