# Cycle-2 code review — BUG-1308 expertise replace/drop

**Graded at `git show 48d2285be7770a7e630b0a11c8136a55b2d351e3:<path>` for every source/test file cited below —
never a plain file read.** `git status --porcelain` at end of run: two untracked notes from concurrent
siblings (`research-…goalcheck-sc-c2.md`, `review-harness-ui-reviewer-c2.md`) plus a modified
`observations/harness-pm.md` — none mine, none touched by me.

## BLUF
**FAIL.** VL-01/02/03/04 are genuinely CLOSED for the exact adversarial inputs cycle 1 used. But the
lead's P1 prediction **reproduces**: `_reject_multiline` (expertise-merge.py:170) narrowed its rejection
alphabet to `\n`/`\r` only, while the codebase's own line-boundary alphabet — `str.splitlines()`, used
by both `parse_expertise` (:63) and `check-expertise.sh`'s near-identical parser — is eight characters
wider. REQ-03 ("no operation can leave a section over its cap") is still **false as shipped**, via the
same root cause VL-01 had (validator alphabet narrower than parser alphabet), just a different fault
line. `must_fix` non-empty → FAIL.

## Stage 1 — spec compliance (REQ-01..09)
| REQ | Verdict | Citation |
|---|---|---|
| REQ-01 replace | Delivered | `_resolve_replace_or_drop` expertise-merge.py:244, `_rebuild_section` :309-323; confirmed live: `resolve_ops` → `REPLACED` |
| REQ-02 drop | Delivered | same functions; drop path omits the entry in `_rebuild_section` (:318-320) |
| REQ-03 caps preserved | **NOT delivered** | `_check_caps` (:350) counts only the in-memory merged list; see finding F1 below — reproduced live |
| REQ-04 missing target | Delivered | `_resolve_replace_or_drop` :247-253, exit 10; confirmed live |
| REQ-05 ambiguous target | Delivered | `_check_base_ambiguity` :233-241, `_check_proposal_ambiguity` :280-291, exit 11; confirmed live for VL-03's add case too |
| REQ-06 refusal ⇒ byte-identical | Delivered | `harness_merge.locked_update` (harness_merge.py:121-148): `transform` raises before any bytes are computed/written; every refusal path (7/8/10/11/12) is raised before `render()` runs in `cmd_ops` (:540 `transform`) |
| REQ-07a apply unchanged | Delivered (settled, signed) | 0 removed lines in `compute_union`/`cmd_apply` per context |
| REQ-07b SC-11 concurrency | Delivered | `case_concurrent_writers` (test-expertise-merge.py:897) genuinely calls `harness_merge.acquire(lock_path)` — the **same** primitive `locked_update` uses on `path + ".lock"` — no env var, no test-only flag; polls two real subprocess children every 0.05s over a 2.0s hold, asserts neither exits, then asserts both complete post-release with the correct census. Verified this is the real lock, not a double, by reading the call site directly. |
| REQ-08 contract/mechanism agree | Delivered | `harness-distill/SKILL.md:112,125-126` reads "add \| replace \| merge \| drop" / "replace on the surviving id … drop of the absorbed id", matching `_validate_verb`'s refusal text (:159-161) verbatim; `case_contract_drift` exercises both drift directions against 3 mutated copies |
| REQ-09 regression coverage | Delivered, but narrower than the defect class it names (see F1) | `case_replace_at_capacity`, `case_removal`, `case_missing_target`, `case_ambiguous_target`, `case_atomic_failure`, `case_multi_op_composition` (case19) all present in `_run_all_cases` (test-expertise-merge.py:1140-1162) |

No scope leakage: `git diff --stat origin/main..48d2285b` outside `.harness/harness/features/**` touches
exactly the 5 source files plus the 2 test files named in the batch context — nothing else.

## Cycle-1 findings — reproduced live, not read
All four run against the pinned code executed in-memory (fetched via `git show <sha>:<path>`, `exec`'d;
no disk writes — bash-write-guard blocks all writes for this persona, confirmed by testing).

- **VL-01 CLOSED.** `resolve_ops` on a `replace` whose `entry` embeds `\n## Gotchas (max 15)\n- G-16: forged additional entry` → `MergeRefusal(12, ["MALFORMED OPS op index=0: entry must be a single line"])`.
- **VL-02 CLOSED.** `resolve_ops` on an `add` whose `target=["P-50","x"]` → `MergeRefusal(12, ["MALFORMED OPS op index=0: target must be a string, not list"])`. No traceback.
- **VL-03 CLOSED.** `resolve_ops` on an `add` targeting a base id duplicated twice in-section → `MergeRefusal(11, ["AMBIGUOUS TARGET section=Patterns id=P-07 reason=the id appears 2 times in section Patterns"])`.
- **VL-04 CLOSED.** `code-grade.py --base $(git merge-base origin/main 48d2285b) --head 48d2285b`: `case_concurrent_writers` → CYCLOMATIC 2 / COGNITIVE 0 / ABC 13.6 → **GRADE 4, PASS** (bar 3). `case_malformed_ops_cli` → CYCLOMATIC 2 / COGNITIVE 0 / ABC 6.7 → **GRADE 5, PASS**. Both were grade 1 at cycle 1.

## P1 / P2 — the lead's falsifiable prediction

**P1 REPRODUCES.** Base `Gotchas` at cap (15 entries). `ops=[{"op":"replace","target":"G-08","section":"Gotchas","entry":"new text\u2028- G-16: forged entry"}]`. `resolve_ops` exits clean: `[('REPLACED','G-08')]`, `_check_caps` sees `len(merged['Gotchas'])==15` (at cap, passes). `render()` writes the entry verbatim (U+2028 is not `\n`/`\r`, so `_reject_multiline` never sees it). Re-parsing that same rendered text with the tool's own `parse_expertise` — the operation the tool itself, or the very next `apply`/`ops` invocation, or `check-expertise.sh`, would perform — yields **16** `Gotchas` entries (`G-01..G-08,G-16,G-09..G-15`), one over cap. Command and full output are the literal reproduction embedded in this run; re-runnable verbatim from the transcript. **Confirmed with all 8 gap characters**: TAB is correctly *not* a splitlines() boundary and is *not* rejected (fine); VT `\v`, FF `\f`, FS `\x1c`, GS `\x1d`, RS `\x1e`, NEL `\x85`, LS `U+2028`, PS `U+2029` **all** split via `str.splitlines()` and **none** are rejected by `_reject_multiline`.

**P2 CONFIRMED.** Same forged text placed in an `apply --entries` markdown proposal (not JSON): `parse_expertise` splits the proposal itself via `str.splitlines()` **before** `compute_union` ever runs, so the injected line is already a distinct parsed entry (`G-16`, `G-17`) at cap-check time — `compute_union` correctly reports 17 > 15 and `cmd_apply` would exit 8. The two paths are asymmetric exactly as predicted: JSON `entry` strings hide separators from the validator until render time; markdown proposals never do.

## Findings
- **F1 — high, GATING.** REQ-03 false: `_reject_multiline` (expertise-merge.py:170) checks only `"\n" in value or "\r" in value`, narrower than `str.splitlines()`'s boundary set that both `parse_expertise` (:63, the line calling `.splitlines()`) and `check-expertise.sh`'s parser (same call) use to count entries and enforce caps downstream. A `replace` whose `entry` embeds `\v`/`\f`/`\x1c`/`\x1d`/`\x1e`/`\x85`/U+2028/U+2029 passes Step A, reports success (`REPLACED`), and leaves a section one entry over its DEC-145 cap once re-parsed by any tool in this codebase that shares the parsing convention — this is VL-01's exact cause (validator alphabet narrower than parser alphabet), unclosed for 7 of 8 codepoints that split a Python string into lines. `case_ops_entry_injection`/`u17` only exercise `\n`/`\r`, so this gap is untested as well as unfixed. Fix: `_reject_multiline` should reject on `len(value.splitlines()) > 1` (or equivalent) rather than enumerating two characters by hand, so the validator's alphabet cannot silently drift from the parser's again.
- **F2 — low, advisory.** `_validate_target_section` (:182-186) and `_validate_entry_and_keys` report `"missing required key target"`/`"missing required key section"` for `target=0`, `target=[]`, `target=False`, `target=""` — the key is *present*, just falsy; the message misattributes cause. Never gates (exit 12 is still correct), but a caller debugging a malformed digest is told the wrong thing.
- **F3 — info, backlog, pre-existing (not introduced by this feature).** `render()` (:103) falls back to `f"## {name}"` with no `(max N)` annotation when a section name is valid but absent from `headers` (e.g., a first `add` into a section the file never had). `check-expertise.sh`'s `SECTION_RE` makes the annotation optional, so this still passes at exit 0 — cosmetic only. This fallback is unchanged from the pre-existing `apply` path; not something BUG-1308 introduced.
- **F4 — med, non-gating (skill-mandated report, not a defect).** `code-grade.py` at the pin reports 4 grade-2 test functions: `case_missing_target`, `case_ambiguous_target`, `case_contract_drift`, `case_multi_op_composition` — all ABC-driven by long flat sequences of independent `check(...)` assertion calls, not real nested complexity. Grade 2 never blocks per the grading skill; reasoned here as intentional assertion density in integration-test helpers, not a design smell.

## Docs — SPEC §5.3 / DEC-219 / DECISIONS-INDEX
Read all three at the pin. SPEC §5.3's new "Replace and drop are a second subcommand" block and DEC-219's
ruling both accurately describe the shipped mechanism: section+id keying (both required), resolution
against one base snapshot never an earlier op's result, order-independent per-section rebuild, caps
checked once on final state, `merge` refused with the exact instruction text, exits 10/11/12 as shipped.
Function-range citations (`_validate_target_section :182-194`, `_rebuild_section :309-323`,
`_resolve_all :294-306`, `_check_caps :350-357`, `cmd_ops :524-573`, etc.) are all within 0-2 lines of
the actual `def`/next-`def` boundaries at the pin — no material citation drift introduced by this feature.
DECISIONS-INDEX.md's DEC-219 row carries the literal ruling string. `harness-distill/SKILL.md:112-126`'s
vocabulary and rewrite-instruction text match `_validate_verb` verbatim (checked above under REQ-08). One
caveat, folded into F1 rather than filed separately: SPEC's exit-12 row promises rejection of an `entry`
or `target` "that is not a single-line string" — true of the code's narrow definition of "line" but not
of this codebase's own operational definition (`str.splitlines()`), so the guarantee the prose states is
not the guarantee the code delivers.

## Gating summary
`must_fix`: [F1]. `severity_max`: high. **VERDICT: FAIL.**
