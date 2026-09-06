# Receipt — harness-dev-ops — BUG-1308 cycle-1 independent verification

BLUF: **All six rows CONFIRMED, independently re-derived.** Backend-dev's receipt numbers hold up.
One provenance nuance in row A worth flagging (unit-file override is new, not a defect) — noted below.
Read-only session: no edit, no commit, no staged file, HEAD unmoved (`721735e5`), `git status --porcelain`
unchanged before/after (diffed byte-for-byte, `NO DIFF`).

## A — `EXPERTISE_MERGE_BIN` provenance — CONFIRMED (mixed, reported precisely)
- `tests/integration/test-expertise-merge.py:9,35` — `pre-existing`. `git diff` on the file shows **no
  hunk touching either line**; `git show HEAD:tests/integration/test-expertise-merge.py` contains the
  identical `CLI = os.environ.get("EXPERTISE_MERGE_BIN") or …` at both locations verbatim.
- `tests/unit/test-expertise-ops.py:10` — `new-this-cycle`. `git diff` shows
  `-MODULE_PATH = os.path.join(BIN_DIR, "expertise-merge.py")` →
  `+MODULE_PATH = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(BIN_DIR, "expertise-merge.py")`;
  HEAD's copy has no such line at all (grep returns nothing). This is a real addition made this
  cycle — not called out in the receipt — but it mirrors the integration file's pre-existing pattern
  exactly and B below proves the suite is green with the var **unset**, so it does not gate.

## B — both suites, `EXPERTISE_MERGE_BIN` unset — CONFIRMED
- `env -u EXPERTISE_MERGE_BIN .agents/skills/harness/bin/run-unit-tests.sh --kind unit` → exit 0,
  `^FAIL ` count 0, 28 files (`pool: 8 workers, 28 files, 2.15s wall`).
- `env -u EXPERTISE_MERGE_BIN .agents/skills/harness/bin/run-unit-tests.sh --kind integration` → exit 0,
  `^FAIL ` count 0, 46 files (`pool: 8 workers, 46 files, 61.92s wall`).

## C — T-01/T-02 verify blocks, byte-matched against `plan.yaml` — CONFIRMED
Both blocks quoted in the dispatch matched `plan.yaml` lines 354-359 (T-01) and 540-545 (T-02)
verbatim (re-read directly, no paraphrase). Ran both:
- T-01: exit 0, 65/65 `PASS` lines, zero `FAIL`.
- T-02: exit 0, all `case1`..`case24` `PASS`, zero `FAIL` (includes `case21`-`case24` new regressions).

## D — code grade, working tree — CONFIRMED
- `tests/integration/test-expertise-merge.py`: **zero grade-1** functions. Six grade-2 functions —
  `case_concurrency_real` (:136, cyc12/cog21/ABC40.3), `case_destination_refusal` (:288,
  cyc2/cog1/ABC28.3), `case_missing_target` (:493, cyc1/cog0/ABC27.5), `case_ambiguous_target` (:525,
  cyc1/cog0/ABC41.6), `case_contract_drift` (:728, cyc9/cog2/ABC41.6), `case_multi_op_composition`
  (:913, cyc6/cog1/ABC27.2) — exactly the 4+2 set the receipt names, all grade 2 (never gating).
- `case_concurrent_writers` (:890): cyc2/cog0/ABC13.6, **GRADE 4** — matches receipt exactly.
- `case_malformed_ops_cli` (:1022): cyc2/cog0/ABC6.7, **GRADE 5** — matches receipt exactly.
- `tests/unit/test-expertise-ops.py`: zero functions at grade 1 or 2.
- `.claude/skills/harness/bin/expertise-merge.py` working tree: four sub-bar-4 functions —
  `parse_expertise` (cyc14/cog20/ABC25.5, grade 2), `compute_union` (cyc8/cog16/ABC18.5, grade 2),
  `cmd_apply` (cyc8/cog10/ABC24.7, grade 3), `cmd_apply.transform` (cyc12/cog22/ABC39.8, grade 2) —
  exactly the four named, no others.
- Pre-fix comparison: graded `git show HEAD:…expertise-merge.py` from a scratch copy inside the repo
  (code-grade.py refuses paths outside it) — all four functions' cyc/cog/ABC/grade are **identical**
  to the working-tree numbers above. Claim "pre-existing, unchanged by this fix" **CONFIRMED**.

## E — four exit-code fixes, reproduced from fresh `mktemp -d` fixtures — CONFIRMED
All against a `.harness/expertise/harness-test-agent*.md` fixture (path suffix required, else exit 9).
1. VL-01 entry (`\n` and `\r` separately, embedded via `replace`/`P-01`): both → exit **12**,
   `MALFORMED OPS op index=0: entry must be a single line`. sha256 unchanged both times.
2. VL-01 target (`\n` and `\r` separately, via `add`/forged `P-99\n- P-77: forged`): both → exit **12**,
   `MALFORMED OPS op index=0: target must be a single line`. sha256 unchanged both times.
3. VL-02 (`target: ["P-50","x"]` via `add`): exit **12**, `MALFORMED OPS op index=0: target must be a
   string, not list`; stderr captured separately, zero `Traceback` occurrences. sha256 unchanged.
4. VL-03 (fresh base, `Patterns` holds `P-07` twice — "four-a"/"four-b" — `add P-07` three ways):
   (a) neither-occurrence text → exit **11** `AMBIGUOUS TARGET … reason=the id appears 2 times`;
   (b) last-occurrence-matching text → exit **11**, same message; (c) first-occurrence-matching text
   → exit **11**, same message. All three sha256-unchanged. Matches receipt's claimed pre-fix→post-fix
   swing (7 / 0-PRESERVED / 7 → 11/11/11) exactly.

## F — REQ-07, apply path unchanged — CONFIRMED
- Structural: `git diff --numstat` → `+54/-14`. Three hunks, all inside `_validate_verb`,
  `_validate_target_section`, `_parse_op`, `_resolve_replace_or_drop`, `_resolve_add`. Four new
  functions added: `_reject_multiline`, `_validate_entry_shape`, `_base_matches`,
  `_check_base_ambiguity`. Grep of the diff for `cmd_apply|render(|compute_union|CAPS = |
  require_expertise_destination|parse_expertise` — **zero matches**.
- Behavioural: at-cap (15/15) `Gotchas` fixture, `apply --entries` proposal with a forged 16th
  markdown line → exit **8** `CAP EXCEEDED section=Gotchas cap=15 union_size=16`, file byte-identical
  (sha256 match). A separate ordinary add-only proposal on a fresh fixture → exit **0**, stdout
  `ADDED P-02` / `PRESERVED P-01` / `APPLIED …`, entry present on disk.

## Verification table

| Row | Verdict |
|---|---|
| A | CONFIRMED (integration: pre-existing; unit: new-this-cycle, non-gating) |
| B | CONFIRMED |
| C | CONFIRMED |
| D | CONFIRMED |
| E | CONFIRMED |
| F | CONFIRMED |

## Session hygiene
`git status --porcelain` before and after (unfiltered) are byte-identical (`diff` → no output).
No file edited, no commit made, nothing staged, HEAD unmoved at `721735e58124d274ad8e5009194f4a7de9a3f4c6`.
All scratch fixtures lived under `mktemp -d` and were `rm -rf`'d before this receipt was written.

## Open question
Not blocking, but worth the panel's attention: the unit suite's `EXPERTISE_MERGE_BIN` override
(`tests/unit/test-expertise-ops.py:10`) is a new addition this cycle, introduced without being called
out in the fix receipt. It does not currently mask anything — B above proves the suite is green with
the var unset — but it silently enables the same false-green mechanism the dispatch's row-A framing
warns about, and nothing pins it to stay unset in CI.
