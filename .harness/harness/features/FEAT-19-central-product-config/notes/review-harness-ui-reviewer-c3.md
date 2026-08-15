# Review — harness-ui-reviewer — FEAT-19 — Mode A — c3 (confirmation pass, narrow)

**Verdict: PASS.** c2's must_fix is closed. Row 6 now has a `what` string, distinct from row 5's,
in the same subject-verb-clause grammar as the plan's own `what` texts, and every restatement of
the seven-branch count in `DESIGN.md` is now internally consistent — no stale "six" or "only one"
survives anywhere in the file.

## 1. Row 6's `what` — closed

`DESIGN.md:79-85` supplies **"the product config does not parse to a JSON object"**, marked
contract-supplied (not plan-quoted — confirmed `plan.yaml:228-230` still carries no `what` for this
branch, only `value`/`next_step`, unchanged since c2).

- **Reads distinctly from row 5.** Row 5's `what` (`plan.yaml:222-225`, "registered repository has
  no product config") describes absence; row 6's describes presence-but-unparseable. `DESIGN.md`
  states this distinction explicitly and correctly: "on this branch the file **exists**... 'does not
  parse' states the file is there and the contents are the fault" (`DESIGN.md:80-83`).
- **Follows the established grammar.** Contract 2's slot is a subject-verb clause (compare row 2's
  plan-native "the fleet declaration does not load"); row 6's contract-supplied text matches that
  shape rather than introducing a new one.
- **Distinct from row 7 too**, by design intent stated in the text itself (`DESIGN.md:84-85`, "must
  not read like row 7's harness-side text: the word *product* is what tells the operator whose file
  to open") — checked against row 7's actual text ("the harness's own config does not load",
  `DESIGN.md:92-93`); the two do not collide.

## 2. The count — checked every restatement, not just the five named

Grepped the whole file for `six`, `seven`, `five`, `only one` (`DESIGN.md`, all lines). Every
occurrence:

| Line | Text | Verdict |
|---|---|---|
| 6, 20, 47 | "seven refusal lines" / "seven refusals" / "seven failing branches" | total count, unchanged, correct |
| 22 | "Five of the seven now hold" | matches designer's edit 1 |
| 23-25 | "Two do not: row 6 ... and row 7 ..." | consistent with line 22 (5+2=7) |
| 68 | row 6 Verdict cell: "`value`/`next_step` hold — `what` gap in plan, text supplied below" | matches edit 2 |
| 69 | row 7 Verdict cell: "gap in plan — text supplied below" | consistent, no stale claim |
| 71-72 | "Rows 1–5 satisfy both slot rules... Rows 6 and 7 satisfy them on `value` and `next_step`... missing `what` entirely" | matches edit 4 — was "Rows 1–6" before |
| 104 | "one of the two the plan leaves without a `what`" | matches edit 5 — was "the only one" before |

No `six` survives anywhere in the file (`grep -in '\bsix\b'` — zero matches). No `only one` /
`no specified text` phrasing survives (`grep -in` — zero matches). Five distinct restatements,
all consistent with "five hold, two (rows 6 and 7) do not." No sixth, stale instance found.

## 3. Provenance sentence — present and does the job

`DESIGN.md:73-74`: "Everything in those two blocks marked 'contract-supplied' is written here, not
quoted from `plan.yaml`; every other cell in the table is the plan's own text." Correctly scopes the
contract-supplied/plan-quoted distinction to exactly the two blocks (rows 6 and 7) it applies to.

## 4. Nothing else moved

Rows 1-5, Contract 4, and Contract 5 read identically to what c2 confirmed — same `value`/`next_step`
text, same citations, same renamed-flag guarantees. Row 7's own text (lines 88-101) is unchanged from
c2 except the one closing-sentence edit at line 104 already covered above.

## 5. `plan.yaml`'s T-02 changes — confirmed out of the refusal-message contract's path

T-02 (`plan.yaml:349-434`) writes `.harness/products/kaya-ai/harness.json`, a product's runtime
config — unrelated to T-01's `factory_product_config.py` resolver that Contract 2/3 govern. The four
`main()` CLI test cases and the `select_base` agreement case live in T-01's test-case list
(`plan.yaml:316-334`), not T-02; none of the four assert on `what`-slot text — they check the success
payload's key set, the `product: null` case, relative-path resolution, and one refusal branch's
exit-code/stream contract (row 4, already-approved text, unchanged). None touch rows 6 or 7's wording.
No effect on this verdict.

## Not gating, carried forward from c2

The uncommitted-working-tree open question from c2 stands — `DESIGN.md` and `plan.yaml` are still
untracked (`git status --short` unchanged). Not re-raised as a new question since it was already
routed to the host; noting it stays true at this pass too.

## Open questions

None new. c2's open question (commit before signature) still applies if not already acted on.
