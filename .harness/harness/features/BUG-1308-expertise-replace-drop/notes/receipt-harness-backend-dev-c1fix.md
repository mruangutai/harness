# Receipt — harness-backend-dev — BUG-1308 cycle-1 fix

All four gating findings closed. Both suites re-run green. `apply` path behaviourally unchanged
(REQ-07). Nothing committed/staged; HEAD unmoved at `721735e5`.

## 1. VL-04 — two grade-1 test functions, fixed FIRST as instructed

Invocation used to grade the WORKING TREE (uncommitted): explicit file-path args, never
`--base/--head` (that mode reads `git show <ref>:<path>`, which would grade the old committed
code, not this diff) — `code-grade.py`'s `_paths_report` reads `(root / path).read_text()`
directly off disk.

```
python3 .claude/skills/harness/bin/code-grade.py tests/integration/test-expertise-merge.py
```

| Function | Before | After |
|---|---|---|
| `case_concurrent_writers` (:811) | cyc 9, cog 12, ABC 47.0, **GRADE 1** | cyc 2, cog 0, ABC 13.6, **GRADE 4** |
| `case_malformed_ops_cli` (:943) | cyc 2, cog 0, ABC 60.8, **GRADE 1** | cyc 2, cog 0, ABC 6.7, **GRADE 5** |

Both refactored by extracting the repeated call/assign sequences (ABC-driven, per the panel's
own `DRIVER: abc`) into named helpers — no branch removed, no assertion reworded beyond a
`case18:`/`case20:` label prefix every `check()` still carries (T-02's verify greps the id, not
the exact sentence). `case_concurrent_writers` still: takes `harness_merge.acquire` itself,
polls both children every 0.05s for 2.0s with no premature exit, awaits each up to 20s, checks
the id census + P-07 marker — zero env vars/sleeps/flags/edits added. `case_malformed_ops_cli`
still: 3 sub-cases (missing/empty section key, digest-shaped mapping), each byte-identity
asserted. Every new helper graded independently, all grade 4–5. The 4 pre-existing grade-2s
(`case_missing_target`, `case_ambiguous_target`, `case_multi_op_composition`, `case_contract_drift`)
and 2 more (`case_concurrency_real`, `case_destination_refusal`) are confirmed, by hashing the
committed HEAD content, unchanged by me and non-gating (grade 2 never blocks). One new grade-2
appeared transiently (`case_ops_add_duplicated_base`, ABC 38.0) and was extracted into
`_assert_case24_ambiguous`, landing both at grade 4/5 — no written-reason waiver needed.
Production file: every function I touched or added (`_reject_multiline`,
`_validate_target_section`, `_validate_entry_shape`, `_validate_entry_and_keys`, `_base_matches`,
`_check_base_ambiguity`, `_resolve_replace_or_drop`, `_resolve_add`) grades 4–5. Four apply-path
functions (`parse_expertise`, `compute_union`, `cmd_apply`, `cmd_apply.transform`) grade below
bar 4 — confirmed via the byte-identical pre-fix module that these failures **predate** this
fix and this feature entirely; out of scope per REQ-07/the dispatch's explicit do-not-touch list.

## 2/3/4. VL-01, VL-02, VL-03 — one Step A validator, `expertise-merge.py:170-224`

Fix: `_reject_multiline` (new) + `isinstance(str)` checks in `_validate_target_section` and the
new `_validate_entry_shape`, called from `_validate_entry_and_keys` — single site, never touches
`render`/`_rebuild_section`/`cmd_apply`. VL-03: `_base_matches`/`_check_base_ambiguity` extracted
and shared by `_resolve_replace_or_drop` and `_resolve_add`; the ambiguity check now runs before
`_resolve_add`'s PRESERVED/CONFLICT comparison.

| Finding | Before | After |
|---|---|---|
| VL-01 entry (`replace` on at-cap `Gotchas`, embedded `\n`) | exit 0 `REPLACED`/`APPLIED`, file gains a real 16th physical entry | exit 12 `MALFORMED OPS op index=0: entry must be a single line` |
| VL-01 target (`add`, embedded `\n`) | exit 8 (this particular add happened to overflow cap honestly) | exit 12 `MALFORMED OPS op index=0: target must be a single line` |
| VL-02 (`add`, `target: ["P-50","x"]`) | exit **1** + Python traceback to stderr | exit 12 `MALFORMED OPS op index=0: target must be a string, not list` |
| VL-03 (i) neither-occurrence `add` on duplicated `P-07` | exit 7 `CONFLICT` | exit 11 `AMBIGUOUS TARGET ... reason=the id appears 2 times` |
| VL-03 (ii) last-occurrence-matching `add` | exit 0 `PRESERVED` | exit 11 `AMBIGUOUS TARGET ...` (same line) |

All five reproduced live, before AND after, via direct CLI invocations against throwaway
`/tmp` fixtures (cleaned up); commands and full output captured in-session, not paraphrased.

## 5. New regression cases — proven RED pre-fix, GREEN post-fix

Integration: `case_ops_entry_injection`(21), `case_ops_target_injection`(22),
`case_ops_non_string_target`(23), `case_ops_add_duplicated_base`(24) — registered in `main()`.
Unit: `case_u17`..`case_u20`. Every one of the 21 new integration checks and 8 new unit checks
FAILED when pointed (`EXPERTISE_MERGE_BIN=<pre-fix scratch copy>` / same env var wired into the
unit loader) at a byte-identical copy of the pre-fix module (hash-verified against `git show
HEAD:<path>` before use, deleted after) — captured output showed the exact `FAIL case21: (a)...`
etc. lines. u19's guard (`_assert_malformed`) added a bare `except Exception` arm after the
pre-fix `TypeError` was observed to abort the whole unit run past `case_u19` silently (P-04) —
fixed before relying on it as RED evidence.

## Verify — carried verbatim, cross-checked against `plan.yaml` T-01/T-02

Both match `plan.yaml` exactly (lines 354/540). Both ran clean:
- T-01 (`test-expertise-ops.py`, all u1..u16 present): exit 0, 65/65 checks PASS.
- T-02 (`test-expertise-merge.py`, all case11..case20 present): exit 0, all checks PASS.

Both suites, verbatim commands:
```
.agents/skills/harness/bin/run-unit-tests.sh --kind unit          # exit 0, 28 files, 0 ^FAIL
.agents/skills/harness/bin/run-unit-tests.sh --kind integration   # exit 0, 46 files, 0 ^FAIL
```

## REQ-07 — `apply` path unchanged

`git diff -- .claude/skills/harness/bin/expertise-merge.py` touches only
`_validate_target_section`/`_validate_entry_and_keys`(+new `_validate_entry_shape`)/
`_resolve_replace_or_drop`/`_resolve_add` and adds `_reject_multiline`/`_base_matches`/
`_check_base_ambiguity` — grep of the diff for `cmd_apply|render(|compute_union|CAPS =
|require_expertise_destination|parse_expertise` returns zero matches. `case16` (add-only/
conflict/over-cap through `apply`) PASS. The VL-01 payload through `apply --entries` still
exits 8 `CAP EXCEEDED` (re-probed live, unchanged from qa's original finding).

## Final state

`git status --porcelain`: `expertise-merge.py`, `tests/integration/test-expertise-merge.py`,
`tests/unit/test-expertise-ops.py` — all `M`, all uncommitted. `git rev-parse HEAD` ==
`721735e58124d274ad8e5009194f4a7de9a3f4c6` (unmoved). Nothing staged. No commit made.
