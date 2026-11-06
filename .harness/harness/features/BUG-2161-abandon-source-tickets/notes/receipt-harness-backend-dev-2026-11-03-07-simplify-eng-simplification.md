# Receipt — BUG-2161 SIMPLIFY · simplification angle (read-only)

BLUF: Two findings, both the same shape — the diff pushes two production functions (`_abandon_plan`, `cmd_abandon`) over the grade-4 cognitive band; each has a small named-helper extraction. No finding against the plan/apply seam itself: the `_ABANDON_COMMENT_TARGET` dict, the extra plan kinds and `_apply_abandon_plan` dispatch pass the deletion test. Flag-only; nothing applied; no checks run.

Diff inspected: `git diff 5094e854 21bfa01d -- .claude/skills/harness/bin/gh-sync.py` (cmd_abandon, _abandon_plan, _apply_abandon_plan, _post_abandon_reason, _report_abandon_gaps, `_feature_station` reuse, main flag parsing). Tests read only to confirm which messages are locked (`tests/unit/test-gh-sync-abandon-sources.py:400-401`). Read: harness-simplify, angle-simplification, delete-first, codebase-design, code-risk-grading (thresholds in `code_grade.py:37-41`: cyclomatic 4→≤8, cognitive 4→≤9, 3→≤15).

## Findings

### F-1 `_abandon_plan` — source planning inflates the function past the grade-4 cognitive band
- kind: simplification (reader load / grading) · scope: in-diff · severity: high IF the tool confirms grade 3 (static estimate; tool not run)
- file/line: `.claude/skills/harness/bin/gh-sync.py:1606-1652` (source loop at 1643-1651)
- summary: the new `for … if num == parent: continue … if num not in task_issues` block nests inside a function that already carries a ternary and four ifs.
- concrete cost: hand-count with `code_grade.py` rules ≈ cognitive 11 (was ≈6: if 1, for 1, IfExp 2, if 1, if 1; added: for 1, if 2, if 2). Band for grade 4 is ≤9, so grade 3 → production blocking finding under harness-code-risk-grading. Cyclomatic ≈8, at the edge of grade 4. Reader must also hold the source rules (dedupe, skip parent, comment-but-not-close for task issues) alongside the four task/milestone/parent entries.
- alternative: extract `_source_plan(rec, sources)` returning the source entries; `_abandon_plan` ends `return plan + _source_plan(rec, sources)`. Net: no behavior change, same order (sources last), `_abandon_plan` back to ≈6 cognitive, helper ≈5 cognitive / cyclomatic 4. The three docstring sentences about sources move to the helper (locality). Flag-only; apply must not touch assertions.

### F-2 `cmd_abandon` — dry-run branch and two `plan`/`already_abandoned` guards push it over the cognitive band
- kind: simplification (reader load / grading) · scope: in-diff · severity: high IF the tool confirms grade 3 (static estimate)
- file/line: `gh-sync.py:1708-1773` (dry-run block 1712-1722; guards 1724-1725, 1768-1769)
- summary: the diff adds `if plan`, `if not already_abandoned` inside the dry-run block plus two more top-level guards and a ternary.
- concrete cost: hand-count ≈ cognitive 10 (if-not-yes 1, nested if 2, for 2, nested if 2, IfExp 1, two top-level ifs 2) vs. band ≤9 → grade 3 (was ≈4-5, grade 4/5). Cyclomatic 7 is fine. The nested `_close_and_reseat` is graded separately, so it does not help.
- alternative: extract the dry-run report into `_report_abandon_dry_run(feat_dir, plan, already_abandoned)` (prints label line, would-lines, station line, runs/ prune dry run, closing prompt) and `cmd_abandon` does `if not yes: _report_abandon_dry_run(...); return`. Drops ≈6 cognitive (cmd_abandon ≈4), keeps output text byte-identical, mirrors the existing `_prune_abandoned_runs(dry_run=True)` / `_report_abandon_gaps` helper convention in the same file. Optionally fold the two `plan` ensure-label checks into one `_ensure_abandoned_label(repo, plan)` — not required.

## Checked, empty
- `_ABANDON_COMMENT_TARGET` (1603): carries both membership (`_apply_abandon_plan`, `_report_abandon_gaps`) and the printed word; deleting it re-spreads the kind→word mapping over two callers. Earns its keep.
- `kind in ("parent","source")` passing `kind` as `what` to `close_and_reseat` (1787-1788): reuses the existing nested closer; no new wrapper.
- `dict.fromkeys(sources)`: needed — `parse_source_issues` (474-502) filters types but does not dedupe.
- `_report_abandon_gaps` `not any(kind in _ABANDON_COMMENT_TARGET …)` (1812): wording now broader than "no parent", but locked by test AS-19 (`test-gh-sync-abandon-sources.py:400-401`); changing it would weaken an assertion — not flaggable.
- `_feature_station` reuse (1711): existing reader, no duplicate parse.
- Comments/docstrings: ticket-tagged narration matches the file's existing convention; the rewritten "LAST DECISION" comment states the present fact. No finding.
- Seam: no new seam introduced; plan list remains the one renderer for dry run and apply, interface unchanged for other callers (`sources=()`).

## Flag-only candidate decisions
- Whether to apply F-1 and F-2 before `review_sha` pins (backend-dev owns `bin/gh-sync.py` for a serialized apply; ceiling one fix per harness-simplify). Alternatively run `code-grade.py --base … --head …` once to confirm the grades first; the estimates above are static.

## Principles applied
- Delete First (`delete-first.md`, read): judged additions against removals; the findings only relocate code (no new layer), and the dict/dispatch additions were kept because deleting them respreads decisions across sites.
- harness-codebase-design reader-load axes (skill, not a principle): F-1/F-2 cut layers-to-trace inside one function.

files_touched: [] · no verification run (read-only).
