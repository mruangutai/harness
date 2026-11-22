# Receipt — harness-ai-dev — ALTITUDE angle — r-20261121-simplify-build-eng

BLUF: placement is sound; one non-blocking finding (briefing-row), four leave notes. No source edited, nothing run beyond read-only git/sed/grep/date.

## Inspected scope
Diff dfa52536..6c4da464 over the full source set: harness_yaml.py (disposition shape rules), plan_merge/check.py (era gate, `_Authority`, row faults), panel.py/union.py (drafted_at ownership), patch-lane.md, teams/plan.yaml + validate.yaml prompts, templates (plan.yaml, harness.json), .harness/harness.json, harness-pm.md Mode 2, harness-validator-lead.md gate, test-plan-team.py section 10 (read for how prompt obligations are pinned). Other tests skimmed only for placement, not correctness.

## Findings

### A-1 — second DECISIONS-INDEX row parser, already diverging — `briefing-row`
- Location: `plan_merge/check.py:198-200` (`INDEX_ROW_RE`), `:262-266` (`_struck_by_dec`) vs `check-plan-routes.py:2394-2408` (`_decisions_index`).
- Same row regex copied; the check.py comment names the original. Behaviours differ: check.py strikes case-insensitively (`.lower().startswith("struck")`, so `Struck under DEC-188` counts); check-plan-routes is case-sensitive `startswith("STRUCK")`. check-plan-routes also reads one fixed `DECISIONS_INDEX_REL`; check.py reads per-segment. So one index can read "struck" to one gate and "live" to the other.
- Cost: a decision indexed `Struck under ...` passes the route-authority gate as live while the disposition gate refuses keep/amend on it. Fix on either side alone widens the split.
- Alternative: one shared index reader (e.g. in a package module both import; check-plan-routes is a hyphenated script, so it imports from the package). Treat as a behaviour question first: which case rule is intended (DEC-188 text decides). Not an apply: check-plan-routes.py is outside the apply lane, and a behaviour change is not simplification.
- Recommendation: briefing-row.

### A-2 — row shape stated in five prose places plus one code constant — `leave`
- `templates/plan.yaml` comment, `teams/plan.yaml` draft prompt, `patch-lane.md`, SPEC, and `harness_yaml.DISPOSITION_FIELDS`.
- Each prose copy serves a different reader (template author, draft writer, patch lane). Drift is caught: `check`/loader reject a wrong shape, and test-plan-team.py section 10 pins each copy at its own slice. No single home could replace them, since a prompt must say what to write.

### A-3 — two functions named `_successor_fault` — `leave`
- `harness_yaml.py` (shape: `none` for keep, D-NN/DEC-NNN otherwise) and `check.py` (resolution: in plan ids or indexed). Distinct layers, distinct questions, and the loader/check split is the settled design. Name overlap only, no behaviour overlap.

### A-4 — semantic vs mechanical split — `leave`
- Right altitude. Mechanical row checks (shape, verbatim clause, successor, owner) live in loader and `check`; completeness and strike-vs-amend (DEC-188) live in the scope reader's prompt, which explicitly defers mechanical defects to `check`. Mode 2 grading rule has one authority (harness-pm.md); validate.yaml and the validator gate point at it rather than restating it.

### A-5 — drafted_at ownership across union.py and panel.py — `leave`
- Constant defined at the writer (`union.DRAFTED_AT`), refused on apply/seed in union and on set-key in panel `OWNED_KEYS` via import. Two verbs, one constant, one rule; no shared home missing.

## Skips
- Python complexity grading: not this angle.
- Correctness of dispositions logic, tests' assertions: other readers' angles.
- check-plan-routes.py read only at the cited lines (not in the diff).

## No-source-edit status
Entirely read-only. Only this receipt written. files_touched: [].
