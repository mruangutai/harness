# SIMPLIFY / REUSE angle — FEAT-38-decisions-current-knowledge

Scope: `7ebfc9e..384b800`, code surface only (`gen-decisions-index.py`,
`check-decision-anchors.py`, `check-decision-claims.py` and their three test files).
Read-only; no edits made.

## DECISIONS docs diff (must be empty)

```
git -C <worktree> diff --stat -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
```
Output: **empty** (verified — no lines).

## Findings

### 1. [advisory, HIGHEST VALUE — apply this one if only one is taken] `default_target()` and its backing path constants are copy-pasted verbatim between the two new checkers

- `check-decision-anchors.py:37-40` (`DOCS_DIR`/`DECISIONS_REL_PATH`) and `:50-58`
  (`default_target()`, full body + docstring) are near-byte-identical to
  `check-decision-claims.py:45-48` and `:62-66`. A third independent spelling of the
  same path lives in `gen-decisions-index.py:24-26` (`DOCS_DIR`/`DECISIONS_PATH`).
  The `main()` dispatch around it (try `args.file` else `default_target()`, open,
  catch `OSError`) is also duplicated near-verbatim:
  `check-decision-anchors.py:128-142` vs `check-decision-claims.py:147-161`.
- The comment at `check-decision-anchors.py:37-38` — "Mirrors gen-decisions-index.py's
  own DOCS_DIR/DECISIONS_PATH constants exactly — the default target is the same file,
  resolved the same way, never a second guess" — asserts the very thing that isn't
  true: it IS a second (third, counting the generator) guess. The docstring on
  `default_target()` (`check-decision-anchors.py:54-55`) says it "[r]euses
  gen-decisions-index.py's own root resolution... rather than hand-rolling a second
  one," but only the underlying `harness_boundary.resolve_root()` call is reused —
  the wrapping function and the path constant are not.
- **Cost:** three independent places encode "where is DECISIONS.md" and two
  independent copies of "how do I resolve `--file`, falling back to the default,
  with the same error-on-unreadable-target contract." If the docs move
  (`.harness/harness/docs` → anywhere else) or the `--file`/OSError-message contract
  changes, an editor working from any one of the three files has no compiler signal
  that the other two need the same edit; nothing but a human remembering ties them
  together, and this is exactly the class of drift `check-decision-anchors.py:37-38`'s
  own comment claims to have foreclosed.
- **Alternative:** all three scripts already `import harness_boundary` — a proven,
  shared, standalone `bin/` module. Move `DECISIONS_REL_PATH` and a
  `default_target(bin_dir)` helper into `harness_boundary.py` (or a new tiny
  `decisions_doc.py` sibling module), and have `check-decision-anchors.py`,
  `check-decision-claims.py`, and (for the constant, at least) `gen-decisions-index.py`
  all call it. This is infrastructure/bootstrapping, not the generator's parsing
  model — pulling it into a shared module does not cross the "checkers stay standalone,
  no generator import" line the anchors-checker docstring draws (line 2: "no model
  in it"); the generator's entry-parsing model (`parse_decisions`, `build_index`,
  etc.) stays untouched and un-imported.
- Not blocking: nothing here is wrong today: all three resolve to the same path and
  the checkers currently pass. It is improvable, not incorrect.

### 2. [advisory, lower value] two independent spellings of "how a decision entry heading begins" now exist in `bin/`

- `gen-decisions-index.py:28` — `HEADING_RE = re.compile(r"^##\s+(DEC-(\d+))\b")` —
  used for entry-boundary parsing (`parse_decisions`, `gen-decisions-index.py:113-116`)
  and duplicate-key detection.
- `check-decision-claims.py:50` — `HEADING_RE = re.compile(r"^##\s+(DEC-\d+.*)$")` —
  used only to label a claim with the nearest preceding heading text for reporting
  (`extract_claims`, `check-decision-claims.py:79-85`); it does not need the numeric
  group and never enforces uniqueness.
- `check-decision-anchors.py` has no heading regex at all — it does not attribute
  anchors to a decision, so this is not a third spelling, just an observation that
  the two existing spellings serve genuinely different jobs (structural vs.
  cosmetic-label).
- **Cost:** if the heading grammar changes (e.g. `## DEC-83 —` → `## DEC-83:`), the
  generator's regex is deliberately maintained (it gates a hard `sys.exit` on
  duplicate keys) but `check-decision-claims.py`'s copy has no test coupling to that
  change and could silently stop attributing claims to headings without any check
  going red — a claim would just report `(no preceding DEC heading)` where it
  shouldn't.
- **Alternative:** since `check-decision-claims.py` only needs the raw title text,
  not the parsed number, it could reuse `gen-decisions-index.py`'s `HEADING_RE`
  pattern (not its full `parse_decisions` model) via the same shared-module move as
  finding 1, or, if the isolation is intentional, a one-line comment cross-referencing
  the other definition so a grammar change is at least discoverable via search. Did
  **not** find any decision or docstring stating that heading-detection duplication
  is deliberate isolation the way anchors-checker's docstring explicitly disclaims
  storing snippets — so this reads as an unflagged gap rather than a settled choice.
  Lower priority than finding 1 because the two regexes back genuinely different
  behavior (parse-and-error vs. best-effort label), so collapsing them is a smaller
  win.

## Not flagged (checked, found to be within house convention)

- **Test-fixture duplication in the three `test-*.py` files.** Compared
  `test-check-decision-anchors.py` and `test-check-decision-claims.py` against a
  pre-existing house pattern (`test-check-plan-routes.py`'s local `write_plan`/`run`/
  `check` helpers). Confirmed by grep across all ~55 `bin/test-*.py` scripts: **no**
  shared test-helper module is imported anywhere in `bin/` — every test script
  hand-rolls its own local `write_fixture`/`run_checker`/`write_plan`-shaped helpers.
  The two new test files' identical 5-line `write_fixture()` (`test-check-decision-anchors.py:40-44`,
  `test-check-decision-claims.py:33-37`) and near-identical `run_checker()` match this
  established, repository-wide convention exactly — not a deviation, so not flagged.
- **`test-gen-decisions-index.py` rewrite (T-06/T-10 machinery removal).** Read the
  diff; it strips fixtures for the removed supersession/amendment machinery in step
  with the production removal — no restated business logic found there beyond what
  the house pattern already establishes.
- **Whether the two new checkers re-implement a `gen-decisions-index.py` check.** They
  do not: the generator never validates anchor freshness or runs claim commands: those
  are net-new checks, not restatements. `gen-decisions-index.py`'s own `ROW_RE`/
  `ROW_LOOKALIKE_RE` (lines 81/86) and `parse_decisions`/`build_index` machinery are
  untouched by, and not duplicated in, either new checker.

## Ranking

If the apply step takes exactly one fix, take **finding 1** (`default_target()` /
path-constant consolidation): it is the more concrete, mechanically-clean extraction
(move to `harness_boundary.py`, two call-site swaps, one shared constant), it removes
a real drift risk on two files that must already stay in lockstep by contract
(both check the same target, same `--file` UX, same error contract), and it directly
contradicts a comment in the tree that already claims this was solved. Finding 2 is
real but touches genuinely different-purpose code and is a smaller, more judgment-call
win — leave it as a backlog note if only one fix is taken.
