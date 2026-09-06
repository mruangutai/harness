# Goal check — BUG-440-digest-verdict-reconciliation — post-review, pin `442e0d24`

## BLUF

**PASS. All seven success criteria are MET, each on its own declared method, graded at the pinned
sha.** REQ-01..REQ-04 are all traced by T-01 (`plan.yaml` T-01 `traces`). `must_fix` is empty:
V-04 (med, order-blindness) is a real strictness gap in the six-token assertion but SC-01 does not
quantify over assertion strength, so it does not defeat the criterion — ruling and reasoning below.
No product gap blocks the ship decision. Three process-record inconsistencies are reported ungraded
in the last section.

## Pin discipline

`git rev-parse HEAD` = `442e0d24b25b92b1223eb18b7d16b3a0ff5b3280`. `git status --porcelain` shows
only `feature.json`/`plan.yaml` modified and peer `notes/*-c[123].md` untracked. md5 of the working
tree `check-state.sh` and `test-check-state.py` each equal `git show <pin>:<path>` — the working
tree **is** the pinned blob for both graded files, so line anchors below are valid at the pin.

## Per-SC grading

| SC | method | verdict | evidence |
|---|---|---|---|
|SC-01|automated|**MET**|`test-check-state.py:4693-4695` — `code == 1`, `len(lines) == 1`, and `all(token in line for token in expected)` over the six-tuple at `:4691`. Six separate substring tests, one per item, not one match: `FEAT-TEST`=feature, `M`=run id, `FAIL`=digest verdict, `PASS`=feature.json verdict, `feature.json`=path, `digest.md`=path. Counted at source, not taken from a note. Suite line 215 `ok`|
|SC-02|automated|**MET**|A separate all-agree fixture exists: `_bug440_clean_case` `:4709-4714` builds `entries=("E",)` with a lead-hosted complete run whose digest says `PASS` and asserts `code == 0 and "INV-37" not in out`. Distinct fixture from the mismatch case at `:4701-4706`, so the FAILS-IF does not fire|
|SC-03|automated|**MET**|Each of REQ-03's five has its own test: (a) non-lead host `("N","omp",...)` `:4680`; (b) non-complete `("I",...,"active",...)` `:4681`; (e) unclaimed dir `O` present in `runs` `:4684` but absent from `entries` `:4688` — all three individually named in `silent` `:4692` and each tested independently by `not any(...)` `:4696`; (c) `G` `:4682` pinned by `out.count("runs/G: run is complete but digest.md is missing") == 1` `:4697`; (d) `X` `:4683` pinned by `out.count("runs/X/digest.md: does not satisfy the lead digest") == 1` `:4698` (the `== 1` is the "no second line" clause)|
|SC-04|automated|**MET**|The fixture hashes on **both** sides: `before` at `:4660`, `run(tmp)` at `:4661`, `after` at `:4662`, compared at `:4663`, over `feature.json` plus every `digest.md` collected at `:4657-4659`. The result is bound as the `unchanged` conjunct at `:4694`, not discarded|
|SC-05|inspection|**MET**|`git show <pin>:.harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/redproof-BUG-440.md` exits 0. The note exists at the sha, pins the pre-change source `772790be5277`, records the invocation (fenced `sh` block) and the verbatim failing output (`FAIL - BUG-440 INV-37 reconciles digest verdicts without mutation`, `mixed=False`), and closes `RESULT: RED`. No pass is recorded|
|SC-06|automated|**MET**|`python3 tests/integration/test-check-state.py` from the worktree root: **exit 0, 217 output lines, 0 lines beginning `FAIL`**, and `grep -n FAIL` over the whole output returns nothing (checked, per the runner-accounting gotcha). 73.3s wall. Judged on the literal wording; the 216→217 delta versus the `772790be` baseline is the one added `ok - BUG-440 …` case line at output line 215 — expected, not a failure|
|SC-07|inspection|**MET**|Four independent checks, all at the pin: **(i)** regexes byte-identical — `grep -o 'r"[^"]*"'` over `check-state.sh:1546,1548` and `validate-digest.py:1155,1160` `diff`s empty; both files carry `r"^\s*VERDICT:"` and `r"^\s*VERDICT:\s*(\S+)"`. `validate-digest.py:1155` is the `anchors = list(...)` line and `:1160` the `m = re.search(...)` line, so the cited span is accurate. **(ii)** comment at `check-state.sh:1545`: `# Keep validate-digest.py:1155-1160's tail-anchor semantics byte-for-byte.` **(iii)** reuse: the region operates on `_dtext`, read once by INV-15 at `:1532`; no `open(` anywhere in `1536-1560`. **(iv)** `grep -cE "PASS\|FAIL\|BLOCKED\|ESCALATE"` over `1536-1560` = **0**|

## The V-04 ruling — it does not defeat SC-01

**Ruled: SC-01 MET.** SC-01's four clauses are exit non-zero, exactly one new finding for that run,
the text contains each of six items, and those six are asserted separately rather than as one match.
Each is independently pinned above. SC-01 says nothing about the assertions *discriminating* which
verdict is which, so an order-blind check satisfies its literal text.

The gap is nonetheless real and worth the operator's eye: the run-id token is the single character
`M`, and `FAIL`/`PASS` are checked only for presence — transposing the two `!r` fields in the INV-37
message at `check-state.sh:1550-1553` would ship green. The code reviewer's c3 addendum
(`notes/review-harness-code-reviewer-c3.md:58-68`) adds that c3 dropped c2's `"runs/M"` line filter,
leaving the six-token check as the only tie to run M. This is a criterion-authoring weakness, not a
code defect: a stronger SC-01 would have demanded the assertion distinguish the two verdict fields.
Recording it rather than rewriting the criterion to match, and rather than failing on a demand the
criterion never made.

## Divergence from the review record

None substantive. QA c3 (`notes/qa-bug440-c3.md:14,55`) measured exit 0 / 217 / 0 FAIL — I reproduce
it exactly. QA carried SC-01..SC-07 forward "by name" from cycle 2 rather than re-deriving; I
re-derived SC-01's six-count, SC-03's five legs, SC-04's both-sides hashing and all four SC-07 sub-
claims at source and reach the same verdicts. QA's standing low "SC-05 note staleness" finding is
accurate as a fact — the note's recorded output shows a `mixed=False; clean=True` diagnostic line
that the c3 case at `:4725` no longer prints — but SC-05 demands only existence at the sha, the
invocation, the verbatim failing output, and no recorded pass. All four hold. **Ruled MET; the
staleness is advisory.**

## Process-record inconsistencies — reported, NOT graded, NOT repaired

1. `STATE.md` still describes the plan phase: `status: awaiting-user`, `run:
   runs/plan-record-fix-product/state.yaml`, and a BLOCKING Q1 asking the operator for the A/B/C
   ruling. Three review cycles have since run.
2. `feature.json` `runs[]` holds only the five plan-phase entries (`plan-draft-product` …
   `plan-record-fix-product`) while `cycles_used: 1` and c1/c2/c3 notes exist for QA and three
   reviewers. `review_sha` is correctly the graded pin.
3. The BRIEF's A/B/C disclosure ruling (`BRIEF.md:101-121`) has no recorded resolution:
   `approval.status` is `approved` (2026-09-06, operator) but `approval.rulings` is absent from
   `plan.yaml`. The 4 live mismatches become blocking findings at `/harness` entry on merge, so
   whether A or B was chosen is a live sequencing question for the ship decision.

## Open questions

- **Q1 (blocking the ship decision, not any SC):** which A/B/C ruling applies? Nothing on disk
  records it, and it decides whether `/harness` entry goes red on merge.
- **Q2 (non-blocking):** should V-04 be filed as a follow-up hardening ticket? It is a genuine
  strictness loss that no criterion in this brief covers.
