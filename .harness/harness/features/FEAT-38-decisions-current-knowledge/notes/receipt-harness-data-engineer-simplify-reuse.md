# REUSE pass — FEAT-38, code surface (7ebfc9e..8a7c75c)

**BLUF: `findings: []`.** No restated constant/helper/regex and no newly-hand-rolled check found
in the code surface this feature actually touched. The one lockstep-spelling risk named in the
dispatch (`.harness/harness.json` detect globs vs. `run-unit-tests.sh`'s script arrays) is already
enforced by a standing mechanism, not left to drift.

## What I read

`git diff 7ebfc9e..8a7c75c -- .claude/skills/harness/bin .harness/harness.json .github/workflows`
(26 files, 654+/240-). Of those, all but four are pure prose edits inside comments/docstrings
renumbering `DEC-186`→`DEC-203`, `DEC-171 am.1`→`DEC-171`, `DEC-138 am.N`→`DEC-138` (`board_lifecycle.py`,
`check-domain.sh`, `check-plan-routes.py`, `check-state.sh`, `factory_decompose.py`, `gh-sync.py`,
`harness_yaml.py`, `plan-merge.py`, `test-board-lifecycle.py`, and `tests.yml`'s two comments) — no
REUSE surface there.

The four with real code delta:
- `gen-decisions-index.py` — T-06/T-10 strip the amendment/supersession machinery
  (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`, `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE`,
  `compute_amendments`, `format_amendment_span`, `compute_supersession_target`, per SC-06) and add
  `live_nums` filtering to `compute_refs` (`:134-141`, `:174`). `live_nums` is a two-line local set
  comprehension over `headings`, not a restatement of anything that exists elsewhere in the file or
  in `check-decision-anchors.py` — read both, no overlap.
- `check-decision-anchors.py` — new file this diff, but **frozen by contract** (SC-18, byte-identical
  to `99bb52c`); any REUSE finding against it is out of scope by the dispatch's own terms and I did
  not evaluate it as a candidate.
- `run-unit-tests.sh` — one `INTEGRATION_SCRIPTS` entry removed (T-24, the deleted claims test).
- `.harness/harness.json` — one `test_kinds.integration.detect` pipe-entry removed (T-25, same test).

## The lockstep check named in the dispatch

`run-unit-tests.sh:76-140` already carries a standing "KIND CROSS-CHECK" (FEAT-31 T-12) that
re-derives `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` at every invocation and asserts set-membership
against `harness.json`'s `test_kinds.integration.detect` pipe-list — every `INTEGRATION_SCRIPTS`
name must appear as `.claude/skills/harness/bin/<name>` in `detect`, no `UNIT_SCRIPTS` name may.
It runs on every `--kind`, including `all` (`:94-95`'s own comment states why). This is not a case
of two spellings the feature must remember to keep in sync by hand — the sync is mechanically
enforced, so T-24 (bash array) and T-25 (`harness.json` detect) removing the same entry in the same
commit pair is exactly the case the check exists to catch a *miss* on, and I confirmed no third
spelling exists: `tests.yml` only ever invokes `run-unit-tests.sh --kind unit`/`--kind integration`
(`.github/workflows/tests.yml:86,92`) and never re-lists script names itself.
Verified empirically, not just read: `python3 -c 'json.load(...)'` over `.harness/harness.json`'s
`detect` string, and a plain substring check over `run-unit-tests.sh`'s full text — neither
contains `claims` or `decision-claims` anywhere; `check-decision-anchors.py`'s test **is**
registered in both (`run-unit-tests.sh` text contains `test-check-decision-anchors.py`; `harness.json`
lists it too). No stale reference, no third untracked list.

## ROW_RE / ROW_LOOKALIKE_RE — the named single-sourcing check

Grepped every occurrence across `bin/`: both patterns are defined exactly once
(`gen-decisions-index.py:99,104`), and every consumer imports the compiled object from the module
(`test-gen-decisions-index.py:43` binds `ROW_RE = gdi.ROW_RE`, four call sites `:234,438,589-590`
all use the imported object — no local re-`re.compile` of the row grammar anywhere). Unrelated
`*_RE` names elsewhere in `bin/` (`DEC201_INDEX_ROW_RE` in `test-lead-stop-and-wake.py`,
`INDEX_DEC113_ROW_RE`/`INDEX_DEC12_ROW_RE` in `test-no-distribution.py`) target different, narrower
facts (one specific DEC's row) and are pre-existing, untouched by this diff.

## What I explicitly did not re-flag

Several prior-cycle receipts in this feature's `notes/` (e.g.
`receipt-harness-backend-dev-2026-08-29-11-eng-simplify-reuse.md`,
`receipt-harness-dev-ops-2026-08-29-11-eng-simplify-altitude.md`) found genuine duplication between
`check-decision-claims.py` and `check-decision-anchors.py` (shared `DOCS_DIR`/`DECISIONS_PATH`
literal, near-identical `main()` dispatch, a second heading regex). That file no longer exists in
this diff's final state — `check-decision-claims.py` and its test are deleted (contract item 1,
confirmed: neither file is on disk, `git status --porcelain` on both paths is empty) — so every one
of those findings is moot at the diff range under review here and I did not re-report them.

```yaml
VERDICT: PASS
DIGEST:
  headline: "REUSE pass over FEAT-38's code surface finds nothing restated; the one lockstep-spelling risk named in the dispatch is already mechanically enforced"
  findings: []
  files_touched:
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-data-engineer-simplify-reuse.md
  open_questions: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-data-engineer-simplify-reuse.md
```
