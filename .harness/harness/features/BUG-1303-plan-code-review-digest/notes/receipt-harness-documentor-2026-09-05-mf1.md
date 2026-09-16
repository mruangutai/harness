# Receipt — harness-documentor — BUG-1303 — MF-1 regenerate decisions index

**MF-1 is cleared.** `.harness/harness/docs/DECISIONS-INDEX.md` was regenerated from
`.harness/harness/docs/DECISIONS.md`. The DEC-217 row's hand-written tag list
`[tests,qa,state]` is gone, replaced by the generator-computed `[tests,docs,digest,plan]`.
Regeneration is now byte-identical, so SC-06's byte-identity clause holds and the standing
idempotence gate is green. One file changed; nothing was hand-edited; no commit was made.

## Commands

**1. Apply — `gen-decisions-index.py` (bare, in place), exit 0.**
The dispatch named `--apply`; that flag does not exist. The tool rejected it with
`unrecognized argument(s): --apply. Wrote nothing.` (exit 2) and printed its usage, which
states the bare invocation *is* the in-place write and that only `--stdout` and `--help` are
read-only. Re-ran bare — exit 0, silent. Nothing was written by the rejected call.

**2. Scope — `git diff --stat -- .harness/harness/docs/DECISIONS-INDEX.md`, exit 0.**
`1 file changed, 1 insertion(+), 1 deletion(-)`. The full diff is the single DEC-217 row at
line 217, tags only. No other row moved, so no revert was needed.

Because the diff renderer truncates the long row, the ruling tail was checked separately
rather than eyeballed: the text right of ` :: ` was extracted from `git show HEAD:<index>`
and from the worktree copy and compared — identical, exit 0. The hand-written ruling
("Bugfix test kinds follow the changed surface…") survived regeneration verbatim, as the
generator contract requires.

**3. Idempotence — `gen-decisions-index.py --stdout | diff -q - <index>`, exit 0.**
Emitted zero bytes; emptiness is the pass condition. A fresh regeneration is byte-identical
to the committed file. The same command *before* the fix reported `217c217`, the tag list
being the only difference — that pre-fix run is the independent re-derivation of the panel's
evidence.

**4. Gate — `tests/integration/test-gen-decisions-index.py`, captured exit status 0.**
14 cases, all `ok`, including `test_committed_index_matches_a_fresh_regeneration` (the case
MF-1 reddened) and `test_committed_index_is_complete_and_within_budget` (the length budgets
that live only here). Verdict read from the captured `rc`, not from the tail line. Only this
gate was run — no formatter, linter, or suite.

## Tree state — `git status --porcelain`, verbatim

```
 M .harness/harness/docs/DECISIONS-INDEX.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-code-reviewer-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-qa-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-security-reviewer-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-ui-reviewer-c4.md
```

The one modified path outside the feature directory is the index. The four untracked files
are sibling reviewers' cycle-4 notes inside the feature directory, present at spawn and not
mine. `DECISIONS.md`, `.harness/harness.json`, every test file, agent markdown, and
`.claude/skills/**` are untouched — including
`tests/integration/test-validate-digest.py`, which the sibling squad owns.

## Divergence worth knowing

HEAD is `07b97fc21fe189315a493dac13fcb855bac628f4`, one commit ahead of the pinned
`review_sha 59c5de9764c363eebd67a55cd2f55285bacda69a`. That commit touched neither
`DECISIONS.md` nor `DECISIONS-INDEX.md` (empty `git diff --stat` across the range for both
paths), so the fix applied at HEAD is identical to the fix at the pin and the pinned review
evidence still describes this file exactly. Non-blocking; recorded so the orchestrator
commits knowing the base moved.

## For whoever commits

The index is a generated artifact. If any later commit edits a DEC entry's body, this row's
tags, refs and `@line` anchor recompute — rerun the generator rather than repairing a row by
hand. Only the text right of ` :: ` is hand-written and preserved.
