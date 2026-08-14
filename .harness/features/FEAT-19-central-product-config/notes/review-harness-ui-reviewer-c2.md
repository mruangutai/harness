# Review — harness-ui-reviewer — FEAT-19 — Mode A — c2 (confirmation pass)

**Verdict: FAIL.** One must_fix, narrower than c1's: Contract 3's row 6 (5b-ii, product config
present but malformed/not-a-mapping) has no `what` string anywhere — not in `plan.yaml`, not
supplied by `DESIGN.md`'s corrections — while every sibling raise site has one. `DESIGN.md` marks
row 6 "holds" and claims in the BLUF that "six of the seven now hold as the plan writes them." That
claim is false for row 6 on the `what` slot specifically.

**Note on the pin:** the dispatch cites `63b83c7`, but `DESIGN.md` and `plan.yaml` are untracked in
this working tree (`git status --short` shows `?? .harness/features/FEAT-19-central-product-config/`;
`git show 63b83c7:<path>` errors "exists on disk, but not in 63b83c7"). Everything below was read
directly off disk, not off that commit's git object. Not gating — pre-signature docs are often
uncommitted — but flagged as an open question below, since the operator would be signing text with
no commit backing it.

## 1. The branch count — seven, confirmed by reading the algorithm, not by grep

Counted `raise ProductConfigError` sites in T-01's `intent:` (`plan.yaml:93-241`) by walking the
algorithm rather than grepping the phrase (the dispatch's own warning about block-scalar wrapping
applies equally to a line count):

1. `plan.yaml:185` — step 4b, fleet absent
2. `plan.yaml:190` — step 4b, fleet present but does not load
3. `plan.yaml:196` — step 5a, inside neither root
4. `plan.yaml:214` — step 5b-i, checkout registered nowhere
5. `plan.yaml:222` — step 5b-ii, registered repo has no product config file
6. `plan.yaml:228` — step 5b-ii, product config file present but malformed/not-a-mapping
7. `plan.yaml:232` — step 6, harness's own `harness.json` missing/unparseable/not-a-mapping

Seven. `DESIGN.md`'s "seven" (scope line, BLUF, Contract 2, Contract 3's row count) is correct
against the current `plan.yaml`. c1's "five" was correct against the draft it read; both counts were
right about their respective inputs, as the dispatch anticipated.

## 2. Contract 3 against the plan, row by row — one gap, not zero

Checked each of Contract 3's seven rows (`DESIGN.md:59-67`) against the plan text it cites for
`what`/`value`/`next_step`:

| Row | `value` | `next_step` | `what` |
|---|---|---|---|
| 1 (4b absent) | matches (`plan.yaml:187`) | matches (`plan.yaml:188`) | plan supplies it (`plan.yaml:186`) |
| 2 (4b unloadable) | matches (`plan.yaml:191`) | matches (`plan.yaml:191`) | plan supplies it (`plan.yaml:191`) |
| 3 (5a) | matches (`plan.yaml:197`) | matches (`plan.yaml:198`) | plan supplies it (`plan.yaml:196`) |
| 4 (5b-i) | matches (`plan.yaml:215`) | matches (`plan.yaml:215`) | plan supplies it (`plan.yaml:214`) |
| 5 (5b-ii missing) | matches (`plan.yaml:223`) | matches (`plan.yaml:225`) | plan supplies it (`plan.yaml:222`) |
| 6 (5b-ii malformed) | matches (`plan.yaml:229`) | matches (`plan.yaml:229`) | **absent from the plan; not supplied by `DESIGN.md` either** |
| 7 (step 6) | `DESIGN.md` supplies it | `DESIGN.md` supplies it | `DESIGN.md` supplies it |

`plan.yaml:228-230` reads: *"If the file exists but is not valid JSON, or does not parse to a
mapping: raise ProductConfigError. value is the file path, next_step says to repair the file to a
JSON object."* No `what is "..."` phrase — unlike every other raise site in the algorithm, all six
of which state one explicitly. Contract 2 (`DESIGN.md:47`) fixes the grammar as `factory:
product-config: {what}: {value} — {next_step}`; `what` is not an optional slot.

The gap is invisible in Contract 3's table because the table has no `what` column at all (only `#`,
`Branch`, `value`, `next_step`, `Verdict`) — rows 1–5 are checkable only because the plan text itself
happens to supply `what` in prose next to each raise. Row 6 is the one place that prose is silent,
and nothing catches it.

**This also undercuts the document's own claim.** The BLUF states "Six of the seven now hold as the
plan writes them... The seventh, step 6... has no `what` string in the plan at all." That sentence is
false: row 6 also has no `what` string in the plan. `DESIGN.md`'s row-7 correction even leans on the
missing row-6 text to justify itself — "Rows 5 and 6 name a product's file in the same slot, and the
two must not read alike" (`DESIGN.md:78`) — asserting what row 6 says without anything having said it.

**must_fix:**
1. Add row 6's `what` text to `DESIGN.md`, the same way row 7's is supplied — distinguished from row
   5's "registered repository has no product config" (that text is false here; the file exists).
   Something on the order of "the product config file does not parse to a JSON object" would close
   it, parameterized to read distinctly from row 5.
2. Correct the BLUF's "Six of the seven now hold as the plan writes them" to five, and correct row
   6's "Verdict" cell from "holds" — it holds on `value`/`next_step` only.

Severity: `med`, not `high`, and narrower than c1's finding — that branch was wholly unwritten (no
row, no test case); this one already has a plan test case pinning it into existence ("product config
present but malformed JSON -> ProductConfigError naming the file", `plan.yaml:292`) and `value` is
pinned. Only the `what` slot is free. `must_fix` non-empty still gates FAIL regardless of severity.

## 3. Row 7 — sharpening, not a behaviour change

Confirmed against `plan.yaml:232-234`: the plan's own text for step 6 is "raises ProductConfigError
with value the file path and next_step **the repair**" — no `what`, and `next_step` is a bare noun,
not pinned prose. `DESIGN.md`'s "restore or repair `<path>` to a JSON object" fills that gap and
extends it to cover the missing-file cause alongside the unparseable one; it does not move when the
branch fires, what it returns, or its exit behaviour. This is the same fill-the-gap pattern c1
blessed for the old 3c/malformed-JSON corrections. No objection.

## 4. The renames — clean

Grepped both files for `resolve`, `--resolve`, `--which-config`, `product_config`:
- Every `--resolve` occurrence in `DESIGN.md` (lines 91, 93, 96, 99, 128, 129) is qualified as
  `check-domain.sh`'s flag, contrasted against the resolver's own `--which-config`. No bare mention
  of `--resolve` naming the new tool survives.
- `plan.yaml:116`'s bare `product_config.py` is contrastive — "A module named product_config.py
  would sit outside that enumeration permanently" — explaining why the name must NOT be that, not a
  dead reference to the old name.

No dead flag or dead module name survives in `DESIGN.md`.

## 5. Q1 (fleet-absent fallthrough) — closed, and enforced by a test

Confirmed: step 3 (`plan.yaml:167-169`) tests harness-root containment first and unconditionally
routes to step 6, before the fleet is ever loaded. Step 4b's fleet-absent branch
(`plan.yaml:185-189`) now raises directly rather than falling through. Step 5a explicitly forbids the
fallthrough in its own text: "DO NOT fall through to step 6: returning the harness config for a
session that is not in the harness checkout is a fall-back to another repository's config, which is
the exact failure this module exists to prevent" (`plan.yaml:201-203`).

Beyond the reordering itself, T-01's test-case list now has a case that makes the closure durable
rather than just textual: "session root outside the harness root and fleet ABSENT -> ProductConfigError,
never source harness. This is the case an earlier draft answered 'harness' for, and without it the
outside-both criterion passes over the hole" (`plan.yaml:295-297`). c1's Q1 is closed.

## 6. Checkability — otherwise sound

Contracts 1, 2, 4, 5 remain literal and pass/fail-checkable as in c1. Contract 3's rows 1–5 and 7 are
checkable; row 6 is not, until the must_fix above lands.

## Open questions

- Non-blocking, routed to the host: `DESIGN.md` and `plan.yaml` are untracked in the working tree at
  review time, not present in `63b83c7` as the dispatch's pin states (`git show
  63b83c7:.../DESIGN.md` errors "exists on disk, but not in 63b83c7"). This review read the files
  directly off disk. Recommend committing before signature so the artifact the operator signs has a
  commit to anchor to — otherwise the signed contract has no fixed reference the way `check-domain.sh`
  and `test-check-domain.py` citations do.
