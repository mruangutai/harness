# Receipt — harness-backend-dev — T-02 fix cycle (case27 ABC grade-1)

## What changed
New sibling helper `_assert_case27_ambiguous(root, stem, exit_check_name, message_check_name,
texts, base_sections=None)` at `tests/integration/test-expertise-merge.py:1310-1338`, immediately
above the rewritten `case_duplicate_proposal_ids` at `:1341-1371`. The helper is written against
the APPLY path (`write_entries`/`run_apply`), not `_assert_case24_ambiguous`'s OPS path — that
helper is untouched, at its original `:1190-1209`.

Three call sites, each passing the full pinned check-name strings verbatim (not built via a
label-in-f-string, unlike case24's `(label)` shape):
- `:1347-1353` case27a — `base_sections=[("Patterns",[("P-01","one")])]`, texts `("ALPHA","BRAVO")`
- `:1357-1363` case27b — same base_sections, texts `("ALPHA","ALPHA")`
- `:1366-1371` case27c — `base_sections` omitted (defaults `None` = absent destination)

## Proposition -> post-refactor home mapping
- (a) exit 11 -> `check(exit_check_name, ...)` at helper `:1326`, called with
  `"case27a: duplicate ids exit 11"`.
  AMBIGUOUS TARGET + section=Patterns + id=P-02 + reason= -> `check(message_check_name, ...)` at
  `:1328-1333` (the `base_sections is not None` branch), called with `"case27a: message carries
  AMBIGUOUS TARGET, section, id and reason"`.
  destination bytes unchanged -> `check(f"{stem}: destination bytes unchanged", ...)` at `:1335`,
  producing `"case27a: destination bytes unchanged"`.
- (b) identical mapping, same three `check` lines, invoked with the case27b args (`:1357-1363`),
  producing `case27b: identical duplicate ids exit 11` / `case27b: message carries ...` /
  `case27b: destination bytes unchanged`. Refusal is still keyed on `stem`/id, not on the literal
  ALPHA/ALPHA equality, since both branches run the identical helper body.
- (c) exit 11 -> same `:1326` line, called with `"case27c: absent destination exits 11"`.
  AMBIGUOUS TARGET (no section/id/reason token requirement, matching the original) ->
  `check(message_check_name, "AMBIGUOUS TARGET" in combined, combined)` at `:1337` (the `else`
  branch, since `base_sections is None`), called with `"case27c: message carries AMBIGUOUS
  TARGET"`. Nothing created -> `check(f"{stem}: nothing created at the absent destination",
  os.path.exists(path) is False)` at `:1338`.
No base file is written and no before-hash is taken for (c) — the `if base_sections is not None`
guard at `:1319-1321` skips both, matching the original absence of a `before` hash for case27c.

## Measurements
- BEFORE (pre-edit, `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-expertise-merge.py`):
  219 `^PASS  ` lines, 0 `^FAIL  ` lines, exit 0.
- AFTER (same invocation, post-edit): 219 `^PASS  ` lines, 0 `^FAIL  ` lines, exit 0. AFTER >=
  BEFORE (equal — the refactor is check-count neutral, no check was dropped or added beyond the
  original nine case27 checks, all nine present and PASSing: lines 211-219 of
  `/tmp/case27-after.txt`).
- Grader (`code-grade.py tests/integration/test-expertise-merge.py`, working-tree mode since HEAD
  has no commit of this edit): `_assert_case27_ambiguous` at line 1310 — cyclomatic 6, cognitive 5,
  ABC 25.2, **GRADE 3** (bar 3, pass). `case_duplicate_proposal_ids` at line 1341 — cyclomatic 1,
  cognitive 0, ABC 3.0, **GRADE 5**.
- Full plan `verify:` block (T-02, cross-checked byte-for-byte against
  `plan.yaml:296-321`) run from worktree root: all three grep lines matched, the direct-CLI
  `python3 -c` assertion (exit 11, AMBIGUOUS TARGET, id=P-02) passed, exit 0.

## git status
`git -C <worktree> status --porcelain`:
```
 M .harness/harness/features/BUG-276-expertise-merge-duplicate-id/feature.json
 M tests/integration/test-expertise-merge.py
```
`feature.json` was not touched by this dispatch — concurrent orchestrator/sibling activity,
observed not investigated (O-06). The sole file this task modified is
`tests/integration/test-expertise-merge.py`.

## Leave list respected
`_assert_case24_ambiguous`, `_assert_case25_malformed`, `case_ops_target_grammar*`, and every other
case/helper in the file are byte-identical to their pre-edit form (only the case27 region,
:1310-1371, changed). No production file touched.
