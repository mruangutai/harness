# Receipt — harness-backend-dev — BUG-2161 SIMPLIFY ALTITUDE (code surface)

**BLUF: empty finding set. Every candidate resolves to `leave`; no fold-in, no briefing-row.**

Diff inspected: `git -C <PRODUCT> diff 5094e854 21bfa01d -- .claude/skills/harness/bin/gh-sync.py` read in full (cmd_abandon, `_abandon_plan`, `_apply_abandon_plan`, `_post_abandon_reason`, `_report_abandon_gaps`, `main` flag parsing), plus `_record_station` (gh-sync.py:630) and the AS-19 / re-entry test anchors. Read first: harness-simplify SKILL, angle-altitude.md, delete-first.md. Nothing run.

## Altitude questions, answered
- **Capability at the right home?** Yes. Sources are planned inside the existing `_abandon_plan` seam and executed by the existing `_apply_abandon_plan` / `close_and_reseat`; no second close path, no new module. Reuse of `_feature_station` and `parse_source_issues` (plan.yaml authority) is correct.
- **One authoritative statement of each rule?** Yes. `_ABANDON_COMMENT_TARGET` is the single kind-to-word map consumed by both apply and gap report. The close/backlog/label order lives once, in `_close_and_reseat`.
- **Accepted residuals right?** Shared-ticket corpus check absent by D-01 (operator confirmation) — settled, not re-litigated.

## Candidates considered, all `leave`
1. **Re-entry guard sits in `cmd_abandon` (`already_abandoned`, gh-sync.py:1711/1768), not in `_record_station` / `plan-merge.py set-feature-station`.** Deeper home would make the verb idempotent on same-station for every caller (ship, reject too). Cost of that alternative: changes shared infrastructure behaviour for unrelated commands and reopens D-02's settled "abandoned-specific write" scope. Present placement costs one local boolean read twice. **leave.**
2. **`_report_abandon_gaps` now derives "no parent recorded" from plan kinds, not `rec["parent"] is None` (gh-sync.py:1812).** With sources but no parent, the line is suppressed because a source comment was planned. The predicate really asks "was any reason comment planned", and the AS-19 unit case pins the no-target path. Alternative (restore the `rec["parent"]` test) would print a parent-gap line next to successful source posts; no reader acts on it. **leave.**
3. **Parallel plan kinds `comment`/`source_comment` and `parent`/`source`** differing only in the printed word. Alternative: carry the word in the plan tuple. Saves one dict and one tuple-membership; adds a fourth tuple field to every existing consumer and test. Net reader load not lower. **leave.**
4. **Docstring rewrite "last STATEMENT" -> "last DECISION"** (gh-sync.py:1762) records a deliberate invariant relaxation under D-02; it is stated once at the single site. **leave.**

## Findings
None.

## Flag-only candidate decisions
None. No apply authorized here; if a later serialized apply happens, `harness-backend-dev` owns `bin/gh-sync.py` (CLI lifecycle logic).

## Principles applied
- Delete First (read `references/delete-first.md`): tested each addition for a smaller or more direct home; the diff already adds no layer or seam (reuses the plan/apply seam, one dict constant), so no removal was left to recommend.

## Verification
None run (read-only pass); no verification claim.
