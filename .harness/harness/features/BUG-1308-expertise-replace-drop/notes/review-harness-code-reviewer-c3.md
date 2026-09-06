# Code Review — BUG-1308 expertise-replace-drop — cycle 3 (final cycle)

Pin graded: `5942e34e82cf84fd127ff496fdb64202ad647ba6`. All source cited below was read with
`git show 5942e34e82cf84fd127ff496fdb64202ad647ba6:<path>` — never the worktree copy — except where
noted as a temp-copy reproduction under `$TMPDIR`. HEAD (`14a22b7c`) differs from the pin only by the
`feature.json` re-pin line, confirmed via `git diff --stat 48d2285b..pin` / `origin/main..pin`.

## VERDICT: FAIL — one new must_fix (NF-01), not one of VL-01..VL-05

Everything the cycle-2 fix (`8a0121b0`) closed **stays closed**: I rebuilt VL-01..VL-05 myself against
the pinned code, on temp-copy fixtures, not from the code's shape or from trusting the history. All
five are CLOSED. But item 4 of this dispatch ("attack the validator's completeness") found a real,
previously-unidentified hole: **`target` is never validated against the entry-id grammar**, and an
`add` op can plant a colliding id that neither the tool's own cap check nor `check-expertise.sh`
detects. See NF-01. This is new, verified by execution, not a false premise, and it is a fail-open
exactly in the shape this review is instructed to hunt.

## Stage 1 — REQ verdict table (file:line at the pin)

| REQ | Status | Evidence |
|---|---|---|
| REQ-01 replace | Delivered | `_rebuild_section` (`expertise-merge.py:318-332`), `_resolve_all` (`:303-315`), `cmd_ops` (`:533-582`). Executed myself: replace on P-07 in a 15-entry Patterns section → `REPLACED P-07`, re-parsed count 15, ordinal 7, text updated. |
| REQ-02 drop | Delivered | Same `_rebuild_section`. Executed myself: drop G-02 from a 3-entry Gotchas section → `DROPPED G-02`, exit 0, re-grepped file shows G-01/G-03 only. |
| REQ-03 cap preservation | **Delivered — reconfirmed FALSE in both prior cycles, now closed** | Executed myself against a 15/15 at-cap Patterns section: successful replace leaves count 15, ordinal 7 (positive case). Then re-ran the full 10-member `LINE_BREAKING_CHARS` alphabet (`\n \r \v \f \x1c \x1d \x1e \x85 U+2028 U+2029`) as a `replace` entry against the same file via direct CLI subprocess calls — **all 10 exit 12 MALFORMED OPS**, none reach `render`. Re-parsed the (unchanged) file with the tool's own `parse_expertise` each time. |
| REQ-04 missing target | Delivered | `_resolve_replace_or_drop` (`:253-262`), refusal 10. Executed myself: replace on a nonexistent `G-99` → `MISSING TARGET section=Gotchas id=G-99 reason=no entry with this id exists in this section`, exit 10, sha256 unchanged before/after. |
| REQ-05 ambiguous target | Delivered | `_check_base_ambiguity` (`:242-250`), `_check_proposal_ambiguity` (`:289-300`). Executed myself against a base file with `G-01` duplicated in one section → `AMBIGUOUS TARGET section=Gotchas id=G-01 reason=the id appears 2 times in section Gotchas`, exit 11, sha256 unchanged. |
| REQ-06 atomic refusal | Delivered | `harness_merge.locked_update` (`harness_merge.py:121-133`): docstring states plainly "If transform raises MergeRefusal, nothing is written at all... the file is left byte-identical" — `transform` (in `cmd_ops`) computes `resolve_ops` fully, including `_check_caps`, before `render` is ever called, so a refusal never reaches the write. Every refusal I forced above left sha256 unchanged. |
| REQ-07 add-only half | Delivered, reconfirmed | `git diff origin/main..pin -- expertise-merge.py \| grep -c '^-[^-]'` = 0 — the diff is purely additive; `compute_union`/`cmd_apply` byte-identical, confirmed by reading the diff hunks directly (new code inserted after `compute_union`'s closing line, `cmd_apply` untouched before the new `cmd_ops` insertion point). |
| REQ-07 concurrency half (SC-11) | Delivered | `case_concurrent_writers`/`_hold_lock_and_race_case18` (`tests/integration/test-expertise-merge.py:917-943, 851-880`) matches SC-11 verbatim: test takes `harness_merge.acquire(lock_path)` itself, launches an `apply` child and an `ops` child under `subprocess.Popen`, polls both every 0.05s across a 2.0s hold window asserting neither exits, then awaits each with a 20s timeout and checks the final Patterns census is the original 8 plus P-09/P-10, with P-07 carrying child B's replacement text. No env var, no injected sleep, no test-only flag, no edit to the two production files — read directly, not assumed. Part of the green integration run (see Verification). |
| REQ-08 contract/mechanism agree | Delivered | `git diff origin/main..pin -- .claude/skills/harness-distill/SKILL.md` shows the contract now says exactly "express it as a replace on the surviving id plus a drop of the absorbed id" and lists exit codes 7/8/9/10/11/12 with the `ops --file --ops` invocation — matches `_validate_verb`'s refusal text (`:159-161`) and the actual exit set verbatim. |
| REQ-09 regression coverage | Delivered | `case_replace_at_capacity`, `case_removal`, `case_missing_target`, `case_ambiguous_target`, `case_atomic_failure`, `case_multi_op_composition` (case19) all present and green (full suite run, 0 `^FAIL` across both files). |

SC-08/SC-10 spot-checked: a hand-crafted `add`-forged-duplicate file (see NF-01) still passes
`check-expertise.sh` at exit 0 — that is itself part of NF-01, not a violation of SC-08's own text
(SC-08 only requires replace/drop outputs pass the checker, which they do). DEC-219 row in
`DECISIONS-INDEX.md:219` carries the literal substring `replace and drop through the ops subcommand`,
required by SC-10; `test-gen-decisions-index.py` is part of the green integration run.

## VL-01..VL-05 — each closed by my own execution, not by reading the diff

- **VL-01 (embedded newline forging a header)**: CLOSED. `_reject_multiline`'s wide check
  (`len(value.splitlines()) > 1`) refuses it structurally; reconfirmed below under VL-05.
- **VL-02 (non-string target/entry → uncaught TypeError)**: CLOSED. `_validate_target_section`
  (`:191-204`) and `_validate_entry_shape` (`:206-211`) both `isinstance` guard before any use;
  `case_u19`/`case23` (non-string target) are green in the executed suite, exit 12 not 1, no traceback.
- **VL-03 (duplicated base id resolved against the last occurrence)**: CLOSED. `_resolve_add` calls
  `_check_base_ambiguity` before either PRESERVE/CONFLICT branch (`:265-278`); `case24` (green)
  exercises both duplicate-occurrence shapes and gets AMBIGUOUS TARGET(11), not a silent pick.
- **VL-04 (integration tests below grade bar)**: CLOSED, and unrelated to this cycle's touched code.
  `code-grade.py` at the pin (see Verification) reports the same 4 grade-2 test functions cycle-2
  already reported and reasoned (F4 in `review-harness-code-reviewer-c2.md`) — none are new, none are
  grade 1, none block.
- **VL-05 (`_reject_multiline` narrow-alphabet divergence from `parse_expertise`)**: CLOSED. This is
  the cycle-2 delta itself. I did not trust the docstring's claim — I ran all 10 members of the
  Python-derived `LINE_BREAKING_CHARS` set (the exact set `str.splitlines()` recognizes on this
  interpreter: `\n \r \v \f \x1c \x1d \x1e \x85 U+2028 U+2029`) through the live CLI as both a
  `replace` entry and (separately, via the shipped `u18`/`case22`) a forged `target`. All 10 exit 12
  MALFORMED OPS; none reach `render`. Also ran the shipped unit/integration suites directly
  (`python3 tests/unit/test-expertise-ops.py`, `python3 tests/integration/test-expertise-merge.py`):
  0 `^FAIL` in either, `u17/u18/case21/case22` all PASS, and `LINE_BREAKING_CHARS` is derived
  programmatically from `splitlines()` behavior at test-run time (`test-expertise-ops.py:29-34`), not
  a hand-copied literal — so it cannot silently fall behind a future Python's alphabet the way the
  pre-fix code did.

## Stage 2 — code quality of the cycle-2 delta

**The docstring's "strict subset, never fires alone" claim is false, but harmless — not dead code.**
`_reject_multiline` (`:170-188`) runs the narrow check (`"\n" in value or "\r" in value`) before the
wide check (`len(value.splitlines()) > 1`). I found a concrete counterexample: `value = "abc\n"` —
narrow fires (`"\n" in value` is True) while wide does **not** (`"abc\n".splitlines()` is `['abc']`,
length 1). Confirmed by direct execution. So the narrow check is not a subset of the wide one; it
catches a real case the wide one misses (any value ending in exactly one trailing `\n`/`\r` with
nothing after it). I checked whether this makes the narrow check dead/redundant — it is the opposite:
removing it would let a trailing-newline `entry` through, and `render`'s `"\n".join(out)` would then
embed a genuine extra blank physical line in the file (not multi-entry forgery, but real output
corruption `_check_caps` doesn't see either, since it counts parsed entries, not raw lines). So the
retained check is load-bearing, not vestigial — the docstring is simply wrong about the relationship,
which is worth fixing before someone "cleans up" the narrow check believing it. **Low, advisory,
chore** — reword the docstring; no behavior change needed.

**Code-risk grading**, `--base $(git merge-base origin/main pin) --head pin` (the full feature range,
since `pin` is not yet an ancestor of `origin/main`):
- `_reject_multiline`: cyclomatic 4, cognitive 4, ABC 7.2 → grade 4 (bar 4), PASS.
- `_validate_target_section`: cyclomatic 5, cognitive 4, ABC 12.2 → grade 4 (bar 4), PASS.
- `_validate_entry_shape`: cyclomatic 2, cognitive 1, ABC 4.5 → grade 5, PASS.
- All cycle-2/3-delta test functions (`case_u17`, `case_u18`, `_case21_full_alphabet`,
  `_case21_cap_bypass`, `_case21_cross_section`, `_case22_full_alphabet`) grade 4-5, PASS (test bar 3).
- 4 grade-2 functions reported (`case_missing_target`, `case_ambiguous_target`, `case_contract_drift`,
  `case_multi_op_composition`) — confirmed via `git diff 48d2285b..pin` that none of these four are
  touched by this cycle's delta; they are the same four cycle-2 already reported and reasoned (F4).
  Grade 2 never blocks; reported as `code_grade: grade_2`, not `fail`. No grade-1, no new SEVERITY
  high/critical anywhere in the run.

## NF-01 (new, high, must_fix) — `add`'s `target` is never checked against the id grammar it renders as

`_validate_target_section` (`:191-204`) requires `target` to be a truthy, single-line string, but
**never** checks it against `ENTRY_RE`'s id shape (`^[A-Za-z]{1,3}-\d+$`) or even that it excludes
`": "`. For `replace`/`drop` this is safe by construction — `_resolve_replace_or_drop` requires an
exact match against an already-well-formed base id, so a malformed target just gets refused as
MISSING TARGET. For `add`, no such backstop exists: any single-line string is accepted as a brand-new
id.

**Reproduced on a temp copy** (`$TMPDIR/.harness/expertise/harness-test-agent.md`, 14 legitimate
`Patterns` entries `P-01..P-14`, one short of the cap): an `add` op with
`target: "P-07: SNEAKY"`, `entry: "attacker text"` exits **0**, prints `ADDED P-07: SNEAKY`. The
in-memory cap check is not fooled (14 base + 1 new = 15 ≤ 15, correctly counted, because in memory
the new id is the full 15-character string `"P-07: SNEAKY"`, distinct from the real `"P-07"`). But
`render` writes the raw line `- P-07: SNEAKY: attacker text`, and when **the tool's own
`parse_expertise`** re-reads that file, `ENTRY_RE` matches on the *first* `": "` it finds — so this
line re-parses as **id `P-07`**, entry `"SNEAKY: attacker text"`. Id census before: 14 unique ids.
Census after re-parse: 15 raw entries, but `P-07` now appears **twice** with different text — a
genuine on-disk duplicate the cap check (`15 ≤ 15`) never saw, because it counted the in-memory
representation, not the round-tripped one. `check-expertise.sh` on the resulting file also exits 0 —
it does not check id uniqueness either, so nothing currently shipped catches this.

Consequence, not merely cosmetic: any future legitimate `replace`/`drop` targeting `P-07` on this file
now hits `_check_base_ambiguity` and is permanently refused as `AMBIGUOUS TARGET section=Patterns
id=P-07 reason=the id appears 2 times in section Patterns` until someone manually repairs the file —
a silent, self-inflicted lockout of that entry, caused by an `add` that itself reported success.

This is exactly the fail-open shape this review is instructed to hunt: a lookup (`_validate_target_section`)
that accepts a value it should refuse, and the acceptance is invisible until a *later*, unrelated
operation trips over it. **Severity: high** — realistic input (a stray colon in an LLM-authored
`target`, not an adversarial payload), silent corruption of the id-uniqueness invariant every other
part of this feature assumes, undetected by both gates that exist (`_check_caps`, `check-expertise.sh`).
Cheap, well-scoped fix: validate `target` against `ENTRY_RE`'s id pattern in
`_validate_target_section`, for all three verbs, the same place `_reject_multiline` already lives.

## Verification run (this session, at the pin's checked-out tree — worktree unmodified, see below)

- `python3 tests/unit/test-expertise-ops.py`: 0 `^FAIL`, ends `PASS test-expertise-ops.py`.
- `python3 tests/integration/test-expertise-merge.py`: 0 `^FAIL`, ends `PASS test-expertise-merge.py`.
- `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit`: 0 `^FAIL ` lines, 74 files.
- `bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration`
  (`run-integration-tests.sh` does not exist at this path): 0 `^FAIL ` lines, 46 files, 62.89s wall.
- `python3 .claude/skills/harness/bin/code-grade.py --base $(git merge-base origin/main pin) --head pin`:
  78 functions graded, 4 `RESULT: FAIL` (all `SEVERITY: med`, all `GRADE: 2`), 0 high/critical, 0
  grade-1.

## `git status --porcelain` (proves I changed nothing)

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c3.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-qa-c3.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c3.md
```

All three are concurrent sibling-agent output (pm/qa/ui-reviewer, same c3 panel) written after I
started reading the worktree — none are mine. I touched no source, test, plan, BRIEF, STATE, or
feature.json file; every reproduction above ran against a `$TMPDIR` copy, never this worktree.

## Open questions

None blocking. NF-01's fix is small and mechanical (one grammar check, same shape as the existing
`_reject_multiline` call site); whether to spend the last cycle on it or ship with it backlogged is
the orchestrator's call given the cycle budget, not mine to decide unilaterally — see DIGEST.
