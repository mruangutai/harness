# Receipt — T-10 — regenerate the decisions index

**PASS.** `docs/harness/DECISIONS-INDEX.md` now carries rows for DEC-190, DEC-191 and DEC-192 with
hand-written rulings. The verify clause produces no output and exits 0. The working-tree diff is a
single hunk of three added lines and nothing else.

## What was done

1. Confirmed T-10's `verify:` on disk matches the dispatched clause byte for byte (read from
   `plan.yaml` via `safe_load`, not by reading the plan whole).
2. Ran `gen-decisions-index.py` with no arguments. Three rows appeared carrying `⚠ RULING PENDING`
   at anchors `@5574`, `@5605`, `@5645` — matching the three `## DEC-19x` headings in
   `docs/harness/DECISIONS.md`.
3. Wrote the three rulings — the text right of ` :: ` only — from each entry's own body. Nothing
   left of ` :: ` was typed by hand.
4. Re-ran the generator. It preserved all three rulings (`build_index`'s `existing_rows` path,
   `gen-decisions-index.py:322`).

## The three rulings, as written

- **DEC-190** — ``jsonschema` is a required dependency, declared in `harness-init`'s prerequisite
  gate and CI rather than a manifest; a missing import is a loud error, never a quieter mode.`
- **DEC-191** — `A feature's execution state has a closed key set — eleven top-level keys,
  `additionalProperties: false`, eight required — enforced on `check-domain.sh`'s write path and in
  CI.`
- **DEC-192** — ``phase` and `status` collapse into one `status` field whose six case-sensitive
  values are the GitHub board's column names; no alias, no translation, and `blocked` is
  deliberately dropped.`

Each is drawn from its entry: DEC-190's "declared in exactly the two places PyYAML is" (the
`harness-init` prerequisite gate and `.github/workflows/tests.yml`) and its "no `requirements.txt`
and no `pyproject.toml`"; DEC-191's key counts and its enforcement point on `check-domain.sh`'s
write-payload path plus the required CI job; DEC-192's six board column names, its "case sensitive,
no lowercase alias", "no translation function, no alias table", and its explicit dropping of
`blocked`.

## Verification

| Check | Result |
|---|---|
| `gen-decisions-index.py --stdout \| diff - docs/harness/DECISIONS-INDEX.md` | no output, `exit=0` |
| `grep -c "RULING PENDING"` on the index | `0` (grep exit 1) |
| `git diff -U0` hunk count | `1` |
| `git diff --numstat` | `3	0	docs/harness/DECISIONS-INDEX.md` |
| `test-gen-decisions-index.py` | 9 tests ok, `exit=0` |
| index length | 210 lines, against the 260-line budget |

The unit test was run because the index's real constraints — the 260-line cap, the ≥20-character
prose floor, the 30-word ruling cap, and the `RULING PENDING` sentinel check — are asserted only in
`test-gen-decisions-index.py:394-455` and are invisible to the generator diff. A sentinel-bearing
row passes the verify clause; it fails that test.

## Attribution

Every changed line is attributable to DEC-190/191/192. No existing row's `@line` anchor moved, no
row gained a `— SUPERSEDED BY` clause, no tag set or refs graph changed, no amendment span changed.
The diff has zero deleted lines, which is the strongest form of that claim: no pre-existing row was
rewritten at all.

## Out of scope, seen but not touched

- Run by me at this checkout, not quoted from the dispatch: `check-plan-routes.py` prints
  `35 violation(s) across 16 plan(s)`, `exit=1`. `check-state.sh` exits 1 with 15 `VIOLATION` lines,
  every one of them `has runs/ but no feature.json`. Both close at T-08. Observed, not chased.
- The regenerated index still carries `feature.yaml` in historical rows. By design (rule 15, R-01).
  Not cleaned.

`files_touched`: `docs/harness/DECISIONS-INDEX.md` (plus this receipt).
