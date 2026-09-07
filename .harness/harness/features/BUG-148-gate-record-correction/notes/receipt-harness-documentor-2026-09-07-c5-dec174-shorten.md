# Receipt — harness-documentor — BUG-148 T-01 fix cycle 5 (wording only)

**DEC-174's evidence paragraph is now 88 words over 8 lines, down from 115/10, with every measured
fact intact and the mechanism stated in STATE.md's own terms.** Two paths changed:
`.harness/harness/docs/DECISIONS.md` (one hunk, the paragraph only) and
`.harness/harness/docs/DECISIONS-INDEX.md` (script-regenerated, anchor shifts only). Nothing staged,
nothing committed.

## The replacement paragraph (`.harness/harness/docs/DECISIONS.md:4308-4315`)

```
**The evidence, all from 2026-08-03 and all on this repo.** `run-unit-tests.sh`, `check-docs.sh` and
`check-state.sh` were green, and the fourth gate, `gen-decisions-index.py --check`, was no gate at
all: `--check` was never a supported mode. Before argv validation landed at `ffbdbfa1` (2026-08-05),
an unrecognized argument fell through to the WRITE path, so that exit 0 was a regeneration of
`DECISIONS-INDEX.md` that overwrites exactly the drift a check would have reported; it could not
prove index drift. Use
`gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`. Those three
real gates were green while:
```

## What the words came out of

Only the three sanctioned places: the quoted commit subject `"perf(140): validate argv so --help
stops rewriting the index"`, the source narration `main()` read `stdout_mode = "--stdout" in
sys.argv[1:]` (now "an unrecognized argument fell through to the WRITE path"), and the trailing
hedge "one way or the other". "recorded that day" also went, as pure connective tissue — the
sentence still says the gate was one of the four logged on 2026-08-03. No fact was dropped: the
date, the repo, the three green gates by name, `--check` never a supported mode, `ffbdbfa1`
(2026-08-05), the fall-through to WRITE, exit 0 as a regeneration that overwrites the drift, "could
not prove index drift", the read-only `--stdout | diff` form, and the terminal `while:` all survive.

**D-05 ruling 3 (panel finding PF-ed3ec57922f582bd208169c1120d0946) is satisfied by mirroring, not
by narrowing.** The frozen passage at
`.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md:14-20` states the mechanism as: never
a supported mode → unrecognized argument fell through to the WRITE path → that exit 0 was a
regeneration of `DECISIONS-INDEX.md` that overwrites exactly the drift a check would have reported →
could not prove index drift. DEC-174 now uses those same four clauses in that order, in the same
terms. No automated check discriminates this; it rests on reading both passages, which I did.

No dated sub-section, no `Amendment` heading, no appended note. Backtick convention preserved.

## Measurements — actual output

1. **T-01 verify, verbatim from `plan.yaml:110-119`** (cross-checked character-for-character against
   the dispatch before running; cwd = worktree root, so `git rev-parse --show-toplevel` resolved to
   the worktree). No `T-01 stale claim survives`, no `T-01 MISSING:` line. All 14 integration tests
   printed `ok - …`, including `test_committed_index_matches_a_fresh_regeneration`,
   `test_no_amendment_construct_survives_in_the_authority` and
   `test_preserves_hand_written_rulings_by_dec_number`. **Exit status 0.**
2. `sed -n '4308,4315p' … | wc -w -l` → `8      88`. **88 words ≤ 92, 8 lines ≤ 8.**
3. `git diff --stat` → exactly two paths: `DECISIONS-INDEX.md | 84 +/-`,
   `DECISIONS.md | 12 +/-`, "2 files changed, 47 insertions(+), 49 deletions(-)".
   `git diff -- …/DECISIONS.md` → **one hunk**, `@@ -4306,13 +4306,11 @@`, confined to the evidence
   paragraph. The index's 84 lines are 42 rows whose only difference is the `@NNNN` anchor: after
   normalizing `@[0-9]+` → `@N`, every changed line occurs exactly twice (once `-`, once `+`), so no
   row's tags, refs or hand-written ruling text changed — including DEC-174's own.
4. `git status --porcelain -- .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md`
   **emitted zero bytes.** That emptiness is the pass condition: the operator-approved file is
   byte-identical to HEAD.

## Notes for the next reader

- The paragraph sits 4 words under the 92-word cap. Any further addition to it needs a compensating
  cut, and the five graded contiguous strings plus the terminal `while:` are all load-bearing.
- `wc -w` counts the `|` and `-` of the `--stdout | diff -` pipeline as two words; a rewrite that
  drops the pipeline would gain them back but would violate the graded-string contract.
