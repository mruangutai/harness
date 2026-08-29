# Verify-block amendment recommendation — FEAT-38 segment-D S7

**Three signed `verify:` blocks in `plan.yaml` are unsatisfiable as written. The WORK is correct in
all three; only the gate text is wrong.** Confirmed at source, not inherited from the dispatch.
Each defect below carries exact paste-in replacement text. **This note recommends; it changes
nothing.** `plan.yaml` is untouched by this run.

Observed at worktree HEAD `0a120c6`, `.harness/harness/docs/DECISIONS.md` working tree 6277 lines
(the 6291 figure handed to me is stale).

## T-15 — `check-expertise.sh` invoked with no argument

`plan.yaml` T-15 `verify:` line reads:

```
      bash .claude/skills/harness/bin/check-expertise.sh || exit 1
```

The script requires at least one path: run bare it prints `usage: check-expertise.sh
<file-or-dir> ...` and exits **2**, so `|| exit 1` fires and the block can never pass. Passed the
file it exits 0 (`OK   .harness/harness/expertise/harness-documentor.md`). `$E` is already bound two
lines above. **Replacement line, verbatim:**

```
      bash .claude/skills/harness/bin/check-expertise.sh "$E" || exit 1
```

With that one change the whole T-15 block runs green today: no `amendment` match, `P-01: WHEN`
present, `P-02:` present, checker exit 0. Verified by dry run.

## T-19 — `KIND-DRIFT` grep is non-discriminating

`plan.yaml` T-19 `verify:` line reads:

```
      printf '%s\n' "$OUT" | grep -q 'KIND-DRIFT' && { echo 'KIND-DRIFT fired'; exit 1; }
```

My own measurement of `bash run-unit-tests.sh --kind integration 2>&1` (160 s, runner exit 1):
**6 bare `KIND-DRIFT` matches, 0 matches for `^KIND-DRIFT:`.** All six are passing-case labels from
`test-run-unit-tests-kinds.py`, the suite *for* the drift detector — e.g. `ok    case 2: a
KIND-DRIFT line NAMES test-check-state.py`. The clause therefore fires on green, and the block
exits 1 while both required lines are present (`PASS test-check-decision-anchors.py`, `PASS
test-check-decision-claims.py` both observed). The real detector prints at column 0 —
`print("KIND-DRIFT: %s is in INTEGRATION_SCRIPTS…", file=sys.stderr)`,
`run-unit-tests.sh:112,123,128`. **Replacement line, verbatim:**

```
      printf '%s\n' "$OUT" | grep -q '^KIND-DRIFT:' && { echo 'KIND-DRIFT fired'; exit 1; }
```

**Anchoring, not stderr-scoping, is the recommendation:** every real emission is column-0
`KIND-DRIFT: `, while the false positives are all indented `ok    case` labels, so the anchor
separates them with a one-token edit. Stderr-scoping would require splitting streams that the
block deliberately merges with `2>&1`, and the nested suite's own stderr would leak in anyway.

## T-10 — wrong exclusion list, AND red-requirement that inverts after T-11

**Two independent faults; a fix to either alone leaves the block unsatisfiable.**

*Fault 1 — the exclusion list names two by-construction failures; there are three.* Confirmed by
running the suite: the third is `test_root_resolves_through_harness_boundary_not_the_retired_variable
(a)`. Its case (a) sets `HARNESS_PROJECT_DIR` to a bare `tempfile.TemporaryDirectory()`
(`test-gen-decisions-index.py:755-766`); the override is discarded because the temp dir carries no
`.harness/team-config.yaml`, the generator falls back to the real root where the un-regenerated
index still has orphans, and line 763 asserts `returncode == 0`. Identical cause to the other two.

*Fault 2 — the block also REQUIRES a red.* Line `grep -q '^FAIL -
test_committed_index_matches_a_fresh_regeneration' /tmp/t10.out || exit 1` demands that case be
failing. **T-11, later in this same segment, regenerates the index and turns it green** — at which
point the block exits 1 again for the opposite reason. Repairing only the exclusion list yields a
block that passes in the pre-T-11 window and fails forever after. **The fix is to drop the
red-requirement entirely:** index freshness is T-11's claim, not T-10's, and the same reasoning is
already written into T-19's own intent ("a suite-wide FAIL sweep would go red or green on
interleaving rather than on your work"). **Replacement for the three lines from `grep -q '^ok -
test_no_amendment…` through the `&& exit 1`, verbatim:**

```
      grep -q '^ok - test_no_amendment_construct_survives_in_the_authority$' /tmp/t10.out || exit 1
      grep '^FAIL' /tmp/t10.out \
        | grep -vE 'test_(committed_index_(matches_a_fresh_regeneration|is_complete_and_within_budget)|root_resolves_through_harness_boundary_not_the_retired_variable)' \
        && exit 1
      exit 0
```

Window-agnostic by construction: pre-T-11 the three names are excluded while red; post-T-11 they go
green and the exclusion simply matches nothing. T-10's retained claim — machinery gone, orphan
detection kept, new case ok, no other FAIL — is unweakened.

## Open questions

- **Q1 (non-blocking):** a fourth FAIL, `test_row_per_distinct_dec_matches_authority: fence guard
  harvested a heading inside a code fence`, is red right now from a **sibling's in-flight edit**, not
  by construction: `git show HEAD:` DECISIONS.md has 22 `^```` fences, the working tree has 23. It is
  correctly NOT excluded above. T-10's verify must be re-run after segment D settles; if it is still
  red then, that is a real finding against the DECISIONS.md edit, not a gate defect.
- **Q2 (blocking on signature, not on me):** all three replacements need the operator's signature.
  Only the main session may amend a signed `plan.yaml`.

## Porcelain — verbatim

Worktree (`git -C <worktree> status --porcelain`), post-write, my note present. Other entries are
concurrent members' work, still moving as I write; `plan.yaml`'s modification is **entirely
pre-existing** — `git diff -U0` on it is exactly three `status: pending` -> `status: building` flips
at lines 870, 1167 and 1431, no `verify:` or `intent:` line touched, and all four defective lines
quoted above are still present in the file (`git grep -c` = 4):

```
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/observations/harness-documentor.md
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-documentor-2026-08-29-08-product-S2.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-documentor-2026-08-29-08-product-S3.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-residual-amendment-formats.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-verify-block-defects.md
?? .harness/notes/grilling-decisions-current-knowledge-2026-08-24.md
```

Main checkout (`git -C /Users/molchairuangutai/GitHub/harness status --porcelain`) — no FEAT-38
path appears; the listed entries are pre-existing and unrelated:

```
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/analysis-path-accessors-2026-08-26.md
?? .harness/notes/analysis-pr-922-omp-supervision-2026-08-28.md
?? .harness/notes/analysis-pr-922-omp-supervision-c1-2026-08-28.md
?? .harness/notes/grilling-845-one-vocabulary-2026-08-25.md
?? .harness/notes/grilling-root-resolution-2026-08-26.md
?? .harness/notes/probe-746-foreground-dispatch-2026-08-26.md
?? .harness/notes/triage-decisions-authority-2026-08-26.md
```

HEAD unmoved at `0a120c6`. Nothing staged, nothing committed. `DECISIONS-INDEX.md` untouched.
