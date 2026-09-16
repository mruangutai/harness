# Receipt — harness-backend-dev — T-01 — BUG-276

## Order of work (as mandated)

1. Wrote `case_u23()` (sub-cases a/b/c) in `tests/unit/test-expertise-ops.py`, registered after
   `case_u22()` in `main()`'s explicit list. No production edit yet.
2. Ran the verify command (STEP 1 RED). **Observed exit 1.** The three new checks reddened
   exactly as predicted by the measured pre-fix behaviour (first entry silently wins, no
   exception raised):
   ```
   FAIL  u23a: MergeRefusal raised
         | no exception raised
   FAIL  u23b: MergeRefusal raised
         | no exception raised
   FAIL  u23c: MergeRefusal raised
         | no exception raised
   FAIL test-expertise-ops.py
   EXIT:1
   ```
   (The named `u23a/b/c: ... refuse with code 11` checks never printed at all — they live in the
   `except` branch, which was never reached, confirming `compute_union` did not raise.) All 96
   pre-existing checks still printed `PASS`.
3. Made the production edit in `.claude/skills/harness/bin/expertise-merge.py`:
   - Added `_check_proposal_duplicate_ids(prop_sections, prop_order)` immediately above
     `compute_union` (mirrors `_check_proposal_ambiguity`'s message shape, substituting
     "entries" for "ops"), raising `harness_merge.MergeRefusal(11, ["AMBIGUOUS TARGET
     section=<s> id=<i> reason=two entries in one proposal name this target"])`, comparing no
     text.
   - Called it as the first statement of `compute_union`'s body, before `order` is built.
   - `compute_union`'s return arity and existing conflicts behaviour are unchanged — `case_u10`
     still unpacks three values and passes (see step 4 output, 0 FAIL).
   - Added one docstring clause to `compute_union` for the new refusal.
   - Added exactly two lines (9, 11) to the module docstring's exit-code table; did not add 10
     or 12.
4. Re-ran the same verify command. **Observed exit 0.**
   ```
   VERIFY_EXIT:0
   ```
   `grep -c '^PASS'` on the full suite output = 121, `grep -c '^FAIL'` = 0. All three new
   markers present and passing:
   `PASS  u23a: different texts refuse with code 11`
   `PASS  u23b: identical texts refuse with code 11`
   `PASS  u23c: no base refuses with code 11`
   The verify block's standalone Python smoke assertion (code 11, `AMBIGUOUS TARGET` prefix,
   `section=Patterns`/`id=P-02` tokens) also passed (`SMOKE OK`).
5. Confirmed no pre-existing case reddened: FAIL count is 0 across the whole suite, both before
   step 3 (only the three new u23 checks failed) and after (none).

## Files touched
- `tests/unit/test-expertise-ops.py` — added `case_u23()` + registration.
- `.claude/skills/harness/bin/expertise-merge.py` — added `_check_proposal_duplicate_ids`,
  wired as `compute_union`'s first statement, docstring updates (function + module).
- `.agents/skills/harness/bin/expertise-merge.py` NOT touched (same inode as the `.claude`
  path per the task constraint; no sync step added).

## Observed but not mine
`git status --porcelain` also shows `.harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml`
modified — not touched by this task; concurrent lead/orchestrator activity in the shared worktree (O-06).

## Verify command
Exact block from the plan, cross-checked against the dispatch's quoted `verify:` — identical, run
verbatim from the worktree root. Final run: exit 0.
