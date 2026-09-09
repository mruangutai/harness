# Receipt — harness-backend-dev — BUG-124 T-01

## Files touched
- `.claude/skills/harness/bin/harness_boundary.py` — added `import harness_yaml` and the four
  helpers `run_dir_grant_globs`, `run_dir_refs`, `run_dir_slug_ok`, `run_dir_forms`.
- `tests/unit/test-harness-boundary.py` — appended 6 new cases (`case_run_dir_grant_globs_live_shape`,
  `case_run_dir_grant_globs_synthetic`, `case_run_dir_grant_globs_absent_and_garbage`,
  `case_run_dir_refs`, `case_run_dir_slug_ok`, `case_run_dir_forms`) plus the
  `write_synthetic_run_dir_manifest` fixture helper, registered in `main()`. No existing case edited.

## RED proof (cases written first, watched fail, before the helpers existed)

Command:
```
unset HARNESS_AGENT_TYPE && python3 tests/unit/test-harness-boundary.py
```

Tail of output before implementation existed:
```
FAIL case_run_dir_grant_globs_live_shape_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_grant_globs'")
FAIL case_run_dir_grant_globs_synthetic_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_grant_globs'")
FAIL case_run_dir_grant_globs_absent_and_garbage_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_grant_globs'")
FAIL case_run_dir_refs_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_refs'")
FAIL case_run_dir_slug_ok_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_grant_globs'")
FAIL case_run_dir_forms_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'run_dir_grant_globs'")

6 FAILURE(S): [...]
```
All 6 new cases failed for the expected reason (helpers not yet defined); every other pre-existing
case passed unchanged. Helpers were then added and the suite re-run GREEN (`ALL PASS`, exit 0).

## Task verify (plan.yaml T-01 `verify:`, run verbatim, cross-checked against plan.yaml:243-244 — matches)

Command (run with `cwd` = worktree root, `HARNESS_AGENT_TYPE` unset first):
```
unset HARNESS_AGENT_TYPE
python3 tests/unit/test-harness-boundary.py && python3 -c 'import sys; sys.path.insert(0, ".claude/skills/harness/bin"); import harness_boundary as hb; g = hb.run_dir_grant_globs("."); assert g and all("/runs/" in x for x in g), g; assert hb.run_dir_slug_ok(("harness", "F", "t01-eng"), g), g; assert hb.run_dir_slug_ok(("harness", "F", "2026-08-26-2-plan-product"), g), g; assert not hb.run_dir_slug_ok(("harness", "F", "eng-t01"), g), g; q = "see /a/b/[.]harness/harness/features/F/runs/eng-t01/digest.md now"; assert hb.run_dir_refs(q.replace("[.]", ".")) == [("harness", "F", "eng-t01")], hb.run_dir_refs(q.replace("[.]", ".")); assert hb.run_dir_refs(q) == [], hb.run_dir_refs(q); f = hb.run_dir_forms(g); assert f and all(x.startswith("<task-or-purpose>-") for x in f), f'
```

Result: `tests/unit/test-harness-boundary.py` printed `ALL PASS` (all 54 cases, including the 6 new
ones); the inline `python3 -c` assertion chain raised nothing. Combined `&&` chain exit status: **0**.

## Notes
- Live manifest yields 3 run-dir grant globs (`*-product`, `*-eng`, `*-validator`) — asserted only
  by SHAPE in the permanent suite (non-empty, every entry contains `/runs/`, sorted+deduped), never
  by count or exact content, per plan constraint (REQ-04).
- Exact-value assertions (`run_dir_grant_globs_synthetic_exact`, `run_dir_forms_synthetic_exact`) run
  only against a synthetic manifest the test itself writes (`write_synthetic_run_dir_manifest`, an
  invented `gizmo` squad).
- `.harness/team-config.yaml` unmodified (read-only in this task).
- Unrelated concurrent modification observed in `git status --porcelain`:
  `.harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml` (task/plan `status:` fields
  flipped `ready`→`building`, `plan`→`building`) — not made by this task; diff confirms no touch to
  T-01's `verify:`/`intent:` text.
