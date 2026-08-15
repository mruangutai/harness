# QA delta bless — /simplify commit 6296149..d15daa3 (c3)

**BLUF: PASS.** The delta preserves the c2 PASS. One real wording change confirmed (session-entry
undeclared-segment text de-capitalized), harmless — nothing asserts the old capitalized form. One
class of vacuous assertions found and confirmed pre-existing (not introduced by this delta): several
blame-list checks in `test-layout-migration.py` never bound the `; readers: ` separator, before or
after, because they only check tag presence (`"[legacy]" in line`). Import-time guard in
`layout_fixtures.py` fires correctly in both directions. Mutation re-proven live in a worktree.

## 1. Output contract — verbatim at d15daa3

- CI regexes (`.github/workflows/tests.yml:202,209`) — `layout: N surface(s) clean, N mixed, N
  cannot-verify` and `examined N feature dir(s), M doc root(s), R reader file(s)` — both trailer
  lines untouched in the diff; confirmed byte-identical at `layout_migration.py:345-346`.
- `NOT APPLICABLE: no harness control-plane marker at %s` — untouched, `layout_migration.py:323-324`.
- `"no evidence of either shape under %s"` — `layout_migration.py:293`.
- `"no reader rows for this surface"` — `layout_migration.py:295`.
- The unrecognised-cause fallback is now the function's terminal `return`
  (`layout_migration.py:299-300`), a total fall-through — improvement, not a regression.
- Every literal CI greps for was diffed against source: no mismatch.

## 2. Session-entry undeclared-segment wording — CHANGED, confirmed harmless

`check-state.sh`'s (now-deleted) `_cv_wording` used `"evidence under an UNDECLARED segment: "`;
the unified `cause_text()` (`layout_migration.py:296`) uses render()'s pre-existing lowercase
`"evidence under undeclared segment: "`. **The session-entry string changed at d15daa3.**

- No test asserts the capitalized form. `test-layout-migration.py:322` labels its check "an
  UNDECLARED segment" in the *comment/check-name string* only — the actual assertion at line 323
  (`"undeclared segment" in out and "archive" in out`) is lowercase and was already testing
  render()'s CLI output, not check-state.sh's session entry, at 6296149 too. Grepped repo-wide for
  `UNDECLARED`: only that one comment string exists; no CI grep, no doc quotes the capitalized form.
- `DEC-194` amendment 1 (`docs/harness/DECISIONS.md:5898-5913`) describes the cause by its **key**
  `undeclared-segment`, never quotes the rendered sentence in either case — not stale.
- Blast radius: **none identifiable.** This was pure duplication removal; no consumer depended on
  the old casing.

## 3. Vacuity check on the `"; readers: "` reformat

`render()`'s per-surface blame line changed from `"; %s [%s]" * n` to `"; readers: " + blame_text()`
when non-empty; INV-27's CANNOT_VERIFY session-entry line similarly moved from `" — {named}"` to
`"; readers: {named}"`.

- **`test-check-state.py` x.2** (`:1648-1652`) asserts only `"CANNOT VERIFY" in l and "[neither]" in
  l` — never binds the separator, before or after this delta. Genuinely loose, not "passes both
  formats because it was updated to."
- **`test-layout-migration.py` cases 3, 5a, 5b, 9, 10, 12** (`:139-227`) all assert tag presence
  (`"[legacy]" in line`, `"[both]" in line`, etc.) via the `reader_line()` helper, never the `"; "`
  vs `"; readers: "` prefix. Same class: passes under either format, was never format-bound.
- **`test-check-state.py` x.1** (`:1630-1642`) is the strongest of the group — asserts
  `"gen-decisions-index.py" in l and "[migrated]" in l and "atomic commit" in l` — still tag/remedy
  presence, not the separator.
- **Conclusion:** no test in the diff was silently left on the old format — none of them ever
  encoded the format at all. This is a real coverage gap (Phase-1 expectation: "the exact MIXED/
  CANNOT_VERIFY line format is pinned somewhere"), but it predates this delta (same assertions
  existed, unchanged, at 6296149) and this delta did not weaken it further. **Not a delta
  regression; a standing gap**, reported per O-01.

## 4. `layout_fixtures.py` import-time RuntimeError — both directions fired

- Real tree: `python3 -c "import layout_fixtures"` succeeds; `FEATURES_READERS`/`DOCS_READERS`
  derive correctly from `_lm.READER_TABLE` (4 + 3 paths, matches STUB keys).
- Perturbed: added a bogus `STUB` key in a scratch copy
  (`/private/tmp/.../scratchpad/binperturb/layout_fixtures.py`), import raised:
  `RuntimeError: layout_fixtures.STUB keys do not match layout_migration.READER_TABLE:
  {'bogus/path/not/in/table'}` — loud, correct message.
- Collection unaffected on the real tree: `test-layout-migration.py` run standalone passes 29/29
  checks, exit 0; the full unit+integration run (below) also collects and passes.

## 5. Suites and gates at d15daa3

| Command | Exit |
|---|---|
| `run-unit-tests.sh --kind unit` | 0 |
| `run-unit-tests.sh --kind integration` | 0 (includes `test-check-domain.py`,
  `test-validate-digest.py`, `test-check-expertise.py` meta-gates) |
| `check-state.sh` live against the real repo | 0 (notes only, no INV-27 findings — real tree is
  clean/migrated so INV-27 never fires; consistent with expectation) |

## 6. Mutation re-proof (worktree `.claude/worktrees/qa-c3-probe` @ d15daa3, per DEC-153)

Mutated `layout_fixtures.STUB[".harness/team-config.yaml"]["legacy"]` to equal its `"migrated"`
value (collapsing the distinguishing evidence). `run-unit-tests.sh --kind all` in the worktree:
exit 1, 5 named failures including `test-layout-migration.py` cases 3/8/12/15/18 and
`test-check-state.py` x.3. Restored with `git checkout --`; `git status --porcelain` confirmed
clean before `git worktree remove`. The binding demonstrated at 6296149 carries at d15daa3 despite
the derived-fixtures rewrite.

## Test matrix

`matrix_ok: true` for this delta — it is a same-behavior internal refactor (dedup + derivation), the
plan's own T-0x already required unit+integration coverage of `layout_migration`/`check-state.sh`,
and both kinds ran green with no reduction in test count or removed assertions (`test-check-state.py`
and `test-layout-migration.py` diffs are var-renames/consolidations only, no deleted checks).

## Coverage gap (standing, not introduced here)

None of the existing MIXED/CANNOT_VERIFY assertions pin the exact separator/prefix text
(`"; readers: "` vs the old `"; "`/`" — "`) — they check tag and phrase presence only. A future
reformat of that joiner would pass this suite silently. Not blocking this bless (pre-existing,
unchanged by this delta), but worth a follow-up test if the joiner is considered part of the
contract.
