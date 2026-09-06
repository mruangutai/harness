# QA gate — BUG-1308, cycle 2, pin 48d2285b

## BLUF: FAIL. VL-01's cause survived its own fix under a wider input alphabet than the validator checks. Everything else (VL-02/03/04, the 8 new regression cases, SC-11 concurrency, both suites) is genuinely closed/green.

## Suites at the pin (`env -u HARNESS_AGENT_TYPE`, `EXPERTISE_MERGE_BIN` unset)
- unit: exit 0, `^FAIL ` count 0, 28 files — matches orchestrator measurement.
- integration (`run-unit-tests.sh --kind integration`, no separate integration runner exists): exit 0, `^FAIL ` count 0, 46 files — matches orchestrator measurement. slowest: test-check-state.py 61.6s.

## Cycle-1 findings, reproduced at the pin (sandbox: disposable worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-sandbox-c2` removed after use; probes ran from `/tmp/qasb` against copies of `git show 48d2285b:.claude/skills/harness/bin/{expertise-merge,harness_merge}.py`)
- **VL-01 CLOSED (as originally scoped):** `add`/`replace` entry with literal `\n`/`\r` + forged `## Gotchas`/`- G-16:` → exit 12 `MALFORMED OPS ... entry must be a single line`, file sha unchanged. Confirmed both in my own sandbox and via the suite's own case21/u17.
- **VL-02 CLOSED:** non-string `target` (`12345`, and a JSON array in case23/u19) → exit 12 `MALFORMED OPS ... target must be a string, not int/list`, no traceback.
- **VL-03 CLOSED:** `add` against a base holding `G-01`/`P-07` twice in one section → exit 11 `AMBIGUOUS TARGET ... the id appears 2 times`.
- **VL-04 CLOSED:** `code-grade.py tests/integration/test-expertise-merge.py` — `case_concurrent_writers` GRADE 4 (ABC 13.6), `case_malformed_ops_cli` GRADE 5 (cyclomatic+cognitive+abc). Both clear the grade-3 bar.

## P1/P2 — the lead's falsifiable prediction: **P1 CONFIRMED, live finding**
`_reject_multiline` (expertise-merge.py:170-179 at pin) checks only `"\n" in value or "\r" in value`. `parse_expertise`'s `text.splitlines()` (line 62) also splits on `\v \f \x1c \x1d \x1e \x85 U+2028 U+2029`.
- Repro: `ops` payload `[{"op":"replace","section":"Gotchas","target":"G-01","entry":"new text\u2028- G-16: forged entry"}]` against a 15-entry (at-cap) `Gotchas` section → **`REPLACED G-01` / `APPLIED ...` / exit 0**. Re-parsing the written file with the tool's own `parse_expertise` yields **16 entries** in a section capped at 15 (`G-01: new text`, `G-16: forged entry`, plus the original 14 survivors). REQ-03 ("the entry/target validator narrower than the parser's own split alphabet cannot forge a section") is still false for `ops`, via U+2028/U+2029/`\v`/`\f`/`\x1c`-`\x1e`/`\x85` instead of `\n`/`\r`.
- Severity **high** — same shape as the original cycle-1 VL-01 (symptom changed, cause survived), and it gates.
- **P2 CONFIRMED not exploitable:** the pre-existing `apply` path parses the whole proposal file with `parse_expertise` (same `splitlines()`) *before* any cap check, so a `\u2028`-forged entry in a proposal is already split into two real entries at parse time and correctly trips `CAP EXCEEDED` (exit 8) rather than writing. Verified: `## Gotchas (max 15)\n- G-99: new text\u2028- G-16: forged entry\n` as an `apply --entries` proposal against the same 15-at-cap base → `CAP EXCEEDED section=Gotchas cap=15 union_size=17`, exit 8, file untouched. Fix belongs in `_reject_multiline`'s character set (or in `render`/cap-check ordering for `ops`), not in `apply`.

## Eight new regression cases — mutation-graded, 8/8 reddened
Cases: integration `case_ops_entry_injection`(21), `case_ops_target_injection`(22), `case_ops_non_string_target`(23), `case_ops_add_duplicated_base`(24); unit `case_u17`, `case_u18`, `case_u19`, `case_u20`. For each, mutated exactly the line(s) the case's own docstring names (via a sandbox copy, `EXPERTISE_MERGE_BIN` pointed at the mutant), reran both suites unmodified:

| mutation (line, pin) | case pinning it | unit result | integration result |
|---|---|---|---|
| `_validate_entry_shape`: drop `_reject_multiline(entry,...)` (L201) | u17 / case21 | u17 (a)(b) FAIL — reddened | case21 all 8 assertions FAIL, forged header written — reddened |
| `_validate_target_section`: drop `_reject_multiline(target,...)` (L188) | u18 / case22 | u18 (a)(b) FAIL — reddened | case22 all 7 assertions FAIL — reddened |
| `_validate_target_section`: drop `isinstance(target,str)` (L186-187) | u19 / case23 | u19 FAIL — reddened | case23's 3 shape assertions FAIL (sha-unchanged check alone survives, since the mutant coincidentally still doesn't write) — reddened |
| `_resolve_add`: drop `_check_base_ambiguity` call (L264) | u20 / case24 | u20 (a)(b) FAIL — reddened | case24(a) reverts to CONFLICT/exit 7, case24(b) reverts to silent PRESERVED/exit 0 and writes — reddened |

8/8 reddened under their own named mutant. None of the eight is vacuous.

## SC-11 / REQ-07 concurrency half — genuinely deterministic, no bypass
`case_concurrent_writers` (test-expertise-merge.py:890-910): the TEST process itself calls `harness_merge.acquire(path+".lock")` — the identical production primitive `locked_update` uses — holds it for a fixed 2.0s window, launches both CLI children (`apply`, `ops`) as real subprocesses under that hold, and asserts neither exits before the hold is released. No env var, no injected sleep, no test-only flag, no edit to `expertise-merge.py`/`harness_merge.py` anywhere in this call chain (confirmed by reading `_hold_lock_and_race_case18` at pin).
- Timed at the pin with real locking: **2.05s observed hold, all 5 case18 assertions PASS.**
- Negative control: copied `harness_merge.py`, replaced the single `fcntl.flock(...)` call in `_acquire_flock` with `pass` (no real lock), reran the identical case unmodified → **child A exited after 0.06s** (would-be regression correctly reddens: "it did not take the lock the core defines; this is the D-09 regression"), and the final-state assertion also failed (only 8 ids present, child B's write lost). Children would NOT complete during the 2s hold window for any reason other than correct locking — the negative control demonstrates the opposite failure mode concretely.

## SC evidence (SC-01..SC-12, BRIEF.md)
| id | verdict | method | evidence |
|---|---|---|---|
| SC-01 | satisfied | reasoned (existing case, unchanged by this feature's diff) | `case_replace_at_capacity`, test-expertise-merge.py:426 |
| SC-02 | satisfied | reasoned | `case_removal`, :465 |
| SC-03 | satisfied | reasoned | `case_missing_target`, :493 |
| SC-04 | satisfied | measured (u5/u6, case_ambiguous_target; VL-03 half via case24/u20 above) | :525, test-expertise-ops.py u5/u6 |
| SC-05 | satisfied | reasoned | `case_atomic_failure`, :571 |
| SC-06 | satisfied | measured (full integration suite green, 0 FAIL) | run above |
| SC-07 | satisfied | reasoned (permanent red case present, unmodified) | test-expertise-ops.py u10 ("THE PERMANENT RED CASE") |
| SC-08 | satisfied | reasoned | check-expertise.sh invoked at :457 (case11, replace) and :485 (case12, drop), both asserted exit-0-accept |
| SC-09 | satisfied | reasoned | `case_contract_drift`, :728, both directions asserted (case17) |
| SC-10 | satisfied | measured | DECISIONS-INDEX.md:219 carries the literal string; test-gen-decisions-index.py ran green in the 46-file integration suite |
| SC-11 | satisfied | measured (mutation-proven above) | `case_concurrent_writers`, :890 |
| SC-12 | satisfied | reasoned | `case_multi_op_composition` (case19), :913; u11 covers order-independence |

## Findings register
- **F-QA-01 (high, gating):** `ops`'s entry/target shape validator (`_reject_multiline`, expertise-merge.py:170-179) checks only `\n`/`\r`, but `parse_expertise`'s `str.splitlines()` (line 62) also splits on `\v \f \x1c \x1d \x1e \x85 U+2028 U+2029`. A `replace`/`add` entry embedding any of these forges a real physical line the same way the original VL-01 newline did, bypassing `_check_caps` exactly as before — reproduced live (P1 above), exit 0/`REPLACED`, 16 entries in a 15-cap section. Fix: broaden `_reject_multiline`'s check to the same set `str.splitlines()` recognizes (or drive it directly off `"x".splitlines(keepends=True)` producing more than one element), not just `\n`/`\r`. Gates the ship.

## Source reading discipline
Every claim above is grounded in `git show 48d2285be7770a7e630b0a11c8136a55b2d351e3:<path>` reads (expertise-merge.py, harness_merge.py, tests/integration/test-expertise-merge.py, tests/unit/test-expertise-ops.py), never a plain working-tree read for source-of-truth claims.

## git status --porcelain (worktree root), verbatim
```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c2.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-c2.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-security-reviewer-c2.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c2.md
```
(All four other cycle-2 panelists' concurrent writes plus pm's observations log — none of them mine. This note itself is untracked and not yet reflected in this snapshot.) A disposable worktree was created at `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-sandbox-c2` for the P1/P2/mutation probes and removed cleanly before this snapshot; `git worktree list` confirms it is gone.
