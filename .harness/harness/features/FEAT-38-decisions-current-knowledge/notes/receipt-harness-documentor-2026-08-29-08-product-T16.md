# T-16 — anchor repair receipt

**All four unresolvable anchors are gone and `check-decision-anchors.py` resolves 20 anchors with 0
failures.** The verify exits 0. Baseline before my edits: 24 anchors examined, **4** failed — one more
than the plan's "exactly three", because DEC-205's own justification paragraph (added later in this
feature) re-cited two of the rotted anchors as evidence. Three of the four sites still existed at HEAD;
the fourth (`FEAT-03-subissue-mirror/feature.yaml:73`, at `7ebfc9e:4490`) had already been deleted with
its entry by segment B2, surviving only inside DEC-205's evidence sentence.

## Per-site repair and why

| Site | Anchor removed | Repair | Why |
|---|---|---|---|
| DEC-159 "What forced it" | `feature.yaml:63-64` | **no anchor** | The fact was a YAML *comment* warning the author wrote beside the `squad:` line. JSON has no comments, so the fact died with the file under DEC-191 — nothing in `feature.json` to re-derive against. Names the field (`squad:`) instead of a line |
| DEC-173 item 1 (B-13) | `FEAT-03-subissue-mirror/feature.yaml:97` | **re-derived onto a live file, no line** | `:97` was FEAT-03's `pending:` block; `feature.json` has no `pending` key (keys: `feature_id, branch, pr, status, review_sha, cycles_used, max_total_cycles, runs, github`). The fact survives at `.harness/harness/features/FEAT-03-subissue-mirror/STATE.md` under `Open Questions`. **No line number** — STATE.md is rewritten by the harness, which is exactly the rot this task exists to stop |
| DEC-205 check 1 | `.../feature.yaml:73` + `feature.yaml:63-64` | **no anchor, past tense, era named** | This is the checker's *evidence* paragraph. Rewritten to "at `7ebfc9e` three anchors … named FEAT-03's execution-state file by its pre-DEC-191 YAML name". Keeping any anchor here would re-fail the very check the paragraph describes; present tense would have gone false the moment I edited |

Three diff hunks, `git diff -U0` headers `@@ -4117,2 +4112,2 @@`, `@@ -4262,2 +4254,3 @@`,
`@@ -6271,4 +6259,5 @@` — those and only those are mine; the other 11 hunks in the file were
present at spawn from segments A–C.

## Evidence

- verify exit **0**; output `examined 20 anchor(s), 0 failed`. 24 − 4 removed = 20, so no anchor was
  silently dropped from the population and the count is non-zero.
- The checker is shown *rejecting*: the same binary printed four `file not found in the tree` lines and
  exited 1 against the pre-edit file.
- `wc -l .harness/harness/docs/DECISIONS.md`: **6277 → 6279** (+2). T-11 owns the index regeneration
  after me.
- `DECISIONS-INDEX.md` **not touched**; `gen-decisions-index.py` **not run**. Both confirmed absent from
  the worktree porcelain.
- Nothing staged (`git diff --cached` empty), nothing committed, HEAD still `0a120c6`.

## Host defect

The first edit call, using the worktree-*relative* path, was **rejected** with "hash #F253 is not from
this session … current file hashes to #7669" and rendered MAIN's text at those line numbers — i.e. the
tool resolved against `/Users/molchairuangutai/GitHub/harness`. Re-issuing with the worktree-qualified
path from the `read` header succeeded. MAIN's porcelain shows no `DECISIONS.md`, so the rejection wrote
nothing. **Path qualification, not luck, is what kept this out of MAIN.**

## Advisory, out of scope

`.claude/skills/harness/bin/test-harness-yaml-corpus.py:17,19,20` carry three `FEAT-0x/feature.yaml:NN`
provenance labels in a module docstring. They are era-correct history for a YAML corpus and are not in
T-16's file list, so I left them. A future sweep widening beyond `DECISIONS.md` will hit them.
