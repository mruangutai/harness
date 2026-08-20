# Receipt — harness-data-engineer — FEAT-29-graphql-budget — simplify-eng (SIMPLIFICATION angle)

## Verdict: no findings — empty return

Read every production and test file the dispatch names, and specifically hunted the likely
find named in the dispatch: **residue of the amendment-5 default flip (cost logging ON → OFF)**.
Found none live in code. One instance of exactly that residue exists in the tree already, but it
is (a) in `plan.yaml`, a pm-owned file outside my domain, and (b) already recorded as backlog row
**B-5** by the prior ship-review pass (`ship-review-2026-08-19-02.md`) — not a novel finding, so
not re-flagged per the dispatch's own instruction not to re-litigate settled findings.

## Scope covered

`git diff bee6234..8c7d7bc` — read in full: `factory_gh.py`, `gh_board.py`, `gh_cost_log.py`
(new), `gh-sync.py` (wrap only), `run-unit-tests.sh`, `test-factory-gh.py`, `test-gh-board.py`,
`test-gh-cost-log.py` (new), `test-check-state.py` (carve-out, read only).

## Checks performed (P-04 — enumerate a zero so it reads as coverage, not silence)

1. **Amendment-5 residue hunt** — grepped every touched file for `default`, `amendment`,
   `ON-by-default`, `OFF-by-default`, `opt-in`. Every hit in `gh_cost_log.py`, `factory_gh.py`,
   `test-gh-cost-log.py`, `test-factory-gh.py` states the CURRENT (opt-in, default-OFF) behaviour
   correctly. No docstring or comment still describes always-on recording.
2. **`gh_cost_log.py` (new module, full read)** — docstring, `_enabled()`, `record()`,
   `measured()`. All internally consistent with the amendment-5 default. No dead reference to a
   shape superseded by a revision.
3. **`factory_gh.py` diff** — `project_item_stations` (new), the rate-limit budget path
   (`_rate_limit_budget_error`, `_looks_like_rate_limit`, `_is_rate_limit_query`), and the
   `measured()` wrap at `run_gh`. Comments here anchor measured facts (e.g. "MEASURED
   2026-08-19 ... one 100-node page cost exactly 1 GraphQL point") rather than narrating a
   since-superseded change — these are exactly the anchors the dispatch says not to trim.
4. **`gh_board.py`** — `board_stations` rewired from `project_items` to `project_item_stations`.
   Docstring was rewritten in the same diff, not left stale; no dead reference to the old
   flat-shape lookup (`field`/`field.lower()`) remains.
5. **`test-factory-gh.py`, `test-gh-cost-log.py`, `test-gh-board.py`** — read every new block.
   The "spare `Result()` queued but never consumed" pattern (T-04 misroute guard,
   ~6 occurrences) and the P-04 fixture-isolation comments are anchoring semantics for named
   mutation-kill checks, not narration — matches the dispatch's explicit caveat, not flaggable
   under this angle. Per hard bound 2 I did not evaluate these as assertion-weakening candidates
   either way — out of bounds regardless.
6. **`test-check-state.py` (carve-out, DEC-174 am.4)** — read the diff (`_inv26_fixture` dual
   GraphQL/item-list shape). Comment is present-tense and justified (why both shapes are kept).
   No finding; noting only because the dispatch requires any carve-out finding be flagged —
   there is none to flag.
7. **Stray-import style check** — `test-factory-gh.py` gains one mid-file `import re as
   _re_station` (line 861). Checked: this matches an existing pre-diff convention in the same
   file (`import re as _re` at line 372, `import re as _re_query` at line 893, both pre-existing)
   — not new complexity, it is REUSE of the file's own established pattern. Not flagged.
8. **Log-integrity confirmation (hard bound 4)** — `.harness/logs/gh-cost-2026-08-19.jsonl` is
   39504 bytes, unchanged. No `gh` call made, no suite run, no `check-state.sh` run.

## Not flagged (already settled, per dispatch)

- B-2 (`gh_board.py:142` `or {}` guard) — not independently re-derived as a finding; visible in
  the diff but out of bounds per dispatch.
- B-3 (T-04 fixture tolerance) — visible, not flagged.
- B-13 (`hasNextPage`/null `endCursor` spin) — visible at `factory_gh.py:359-363`, not flagged.
- `test-factory-gh.py:25`'s module-scope `HARNESS_GH_COST_LOG=0` — read, understood, left alone
  per explicit instruction.
- **B-5** (plan.yaml `intent:` block for T-03 still reads "defaulting to ON") — confirmed still
  present at `plan.yaml` (T-03's `intent:` block, the `HARNESS_GH_COST_LOG=0 writes no line`
  line). This is the exact "amendment-5 residue" shape the dispatch predicted, but it lives in a
  pm-owned file and a backlog row already exists for it — not re-raised as new.

## `task_verify`

n/a — this is a read-only review dispatch, not a PLAN task. No `verify:` command was given.

## Suite run (for `suite:` field — no PLAN task means no `verify:`, but a real result is owed)

Ran `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` after finishing the review (no
`HARNESS_GH_COST_LOG` set, default OFF). Exit 0, 175 `PASS` lines, 0 `FAIL` lines,
`test-gh-cost-log.py` reported `35/35 checks passed`. `.harness/logs/gh-cost-2026-08-19.jsonl`
confirmed byte-identical before and after (39504 bytes) — the default-OFF held, no live `gh`
call was made, `check-state.sh` was not run.
