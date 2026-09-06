# QA Premise Verification — BUG-1308 review panel, review_sha 4c76f0f5

All commands run from the worktree root against files confirmed byte-identical to the pinned
`review_sha` (`git diff --quiet 4c76f0f5 -- .claude/skills/harness/bin/{expertise-merge,harness_merge}.py
tests/integration/test-expertise-merge.py tests/unit/test-expertise-ops.py .claude/skills/harness/bin/check-expertise.sh`
→ no output, identical). All fixtures live under a `mktemp -d` scratch dir (created and removed
via the Write tool / `rm -rf`, since bash-write-guard denies `cp`/redirect writes outside domain);
no tracked file was ever opened for write. `HARNESS_AGENT_TYPE` unset per Expertise G-07.

## Probe A — complexity census

Command:
```
python3 .claude/skills/harness/bin/code-grade.py \
  --base "$(git merge-base origin/main 4c76f0f51a7e8eddc871f5a721d92602762ac103)" \
  --head 4c76f0f51a7e8eddc871f5a721d92602762ac103
```
Exit: `1`. Full per-function output (58 changed functions) is reproduced verbatim in this run's
tool transcript; `PASSING: 48` is the tool's own tail line. Key rows, copied exactly:

- `tests/integration/test-expertise-merge.py:811 case_concurrent_writers` — CYCLOMATIC 9,
  COGNITIVE 12, ABC 47.0, GRADE 1, DRIVER abc, BAR 3, RESULT FAIL, SEVERITY high.
- `tests/integration/test-expertise-merge.py:943 case_malformed_ops_cli` — CYCLOMATIC 2,
  COGNITIVE 0, ABC 60.8, GRADE 1, DRIVER abc, BAR 3, RESULT FAIL, SEVERITY high.

**Both number sets CONFIRMED exactly** as claimed (cyclomatic/cognitive/ABC and grade 1 for both).

(a) Grade-1 functions (2 total): `case_concurrent_writers`, `case_malformed_ops_cli` — both in
`tests/integration/test-expertise-merge.py`.

(b) Grade-2 functions (4 total, all `tests/integration/test-expertise-merge.py`): `case_missing_target`
(L493, ABC 27.5), `case_ambiguous_target` (L525, ABC 41.6), `case_contract_drift` (L728, cyc 9,
ABC 41.6), `case_multi_op_composition` (L900, cyc 6, ABC 27.2). All FAIL, SEVERITY med.

(c) **No function in `expertise-merge.py` itself falls below the production bar of grade 4.**
Every one of its 17 changed functions (`_malformed` through `cmd_ops.transform`) graded 4 or 5,
BAR 4, RESULT PASS. All sub-4 grades belong exclusively to the two test files (BAR 3, the test bar).

(d) For each grade-1 function, the sole driver recorded is **`abc`** (both `DRIVER: abc`) — ABC
alone pins the grade in both cases; cyclomatic and cognitive are within their own thresholds.

## Probe B — entry-text injection vs. the cap guarantee

Fixture: `.harness/expertise/harness-backend-dev.md`, `Gotchas` with exactly 15 entries (G-01..G-15).

**Step 2 — `ops` with an embedded-newline `entry`:**
```
echo '[{"op":"replace","target":"G-08","section":"Gotchas",
  "entry":"text eight\n## Gotchas (max 15)\n- G-16: forged additional entry","why":"..."}]' \
  | python3 .claude/skills/harness/bin/expertise-merge.py ops --file <fixture> --ops -
```
Output: `REPLACED G-08` / `APPLIED <fixture>`. **Exit 0.** The written file now contains a second
literal `## Gotchas (max 15)` header and a forged `- G-16: forged additional entry` line, spliced
mid-section. Line-count of `^- [A-Za-z]{1,3}-[0-9]+: ` (how `check-expertise.sh` counts) rose from
15 → **16**, over cap, with the tool having reported success.

`bash .claude/skills/harness/bin/check-expertise.sh <fixture>` on the resulting file:
```
FAIL <fixture>
  - section Gotchas: 16 entries — cap is 15
EXIT:1
```
So the two tools disagree: `expertise-merge.py ops` exits 0 on a file `check-expertise.sh` rejects.

**Step 3 — discriminator, same payload through `apply --entries`:** fresh 15-entry fixture, proposal
file containing the *same* forged header+entry as real (non-indented) lines:
```
## Gotchas
- G-08: text eight
## Gotchas (max 15)
- G-16: forged additional entry
```
`apply` parses this proposal file structurally (`parse_expertise`) **before** computing the union,
so the forged line becomes its own counted entry. Result:
```
CAP EXCEEDED section=Gotchas cap=15 union_size=16
EXIT:8
```
File left byte-identical to before (refusal precedes the write). **`apply` refuses where `ops`
accepts — CONFIRMED. This is a NEW hole opened by `ops`**, not a pre-existing property of the
tool: `ops`'s `entry` arrives as an opaque JSON string that `_check_caps` only ever measures by
list length, never re-parsed for embedded structure before the render step; `apply`'s proposal is
markdown re-parsed line-by-line up front, so an injected line is a real, counted entry by the time
caps are checked.

**Step 4 — `target` field, embedded newline, on `drop` and `replace`:** payload
`"target": "G-08\n- G-17: forged via target"` against a fresh 15-entry fixture, both verbs:
```
drop:    MISSING TARGET section=Gotchas id=G-08
         - G-17: forged via target reason=no entry with this id exists in this section
         EXIT:10
replace: MISSING TARGET section=Gotchas id=G-08
         - G-17: forged via target reason=no entry with this id exists in this section
         EXIT:10
```
The forged `- G-17: ...` text appears as a literal extra line **inside the refusal's stdout**, but
the fixture's on-disk bytes are unchanged in both cases (refusal precedes write; confirmed by
`cat`). No file-content injection via `target` — only a cosmetic forged line in the refusal
transcript.

**Step 5 — existing coverage:** `grep -niE '\\n|embedded|newline|multi-?line|injection'` over both
`tests/integration/test-expertise-merge.py` and `tests/unit/test-expertise-ops.py` returns **zero
matches**. Neither suite feeds a multi-line/embedded-newline `entry` or `target` through `ops`.
**No existing case would have caught the accepted-injection result.**

## Probe C — `add` against a base id already duplicated

Fixture: `Patterns` section containing `- P-07: first occurrence text` and, later in the same
section, `- P-07: second occurrence text DIFFERENT` (two different texts, same id).

`_resolve_add`'s `existing = dict(base_sections.get(section, []))` collapses the duplicate to its
**last** occurrence before any comparison runs — so behaviour depends only on whether the proposed
text matches that surviving (second) copy:

- (i) `add` P-07, entry == **first** occurrence's text → `CONFLICT ... existing text: second
  occurrence text DIFFERENT ... proposed text: first occurrence text`. **Exit 7.**
- (ii) `add` P-07, entry matching **neither** occurrence → `CONFLICT ... existing text: second
  occurrence text DIFFERENT ... proposed text: third totally different text`. **Exit 7.**
- (iii) `replace` P-07 (same base) → `AMBIGUOUS TARGET section=Patterns id=P-07 reason=the id
  appears 2 times in section Patterns`. **Exit 11.**

So on this exact base, neither (i) nor (ii) reports PRESERVED — both hit CONFLICT because the
chosen texts didn't match the dict's surviving (last) value. **Refuting the literal "PRESERVED or
CONFLICT" pairing for these two specific inputs** — but a bonus 4th run (entry == the **second**
occurrence's text exactly) does reach `PRESERVED P-07` / exit 0, and the file is written with the
duplicate left in place, untouched, still counted as two entries. So the general claim — `add`
never detects the duplicate and instead silently resolves against whichever single occurrence
`dict()` keeps last, landing on PRESERVED or CONFLICT depending on match, while `replace`/`drop`
correctly refuse exit 11 AMBIGUOUS on the identical base — is **CONFIRMED**; only the specific
(i)/(ii) outcome pairing needed correcting to CONFLICT/CONFLICT rather than PRESERVED/CONFLICT.

In all three add/replace cases the file's `Patterns` section was left with the duplicate intact
(2 entries under P-07) whenever the op didn't succeed (cases i, ii — no write occurs on refusal);
in the bonus PRESERVED case the file is also left unchanged, duplicate still present — **the
duplicate is never collapsed or resolved by an `add`, silently or otherwise; it just never gets
flagged.**

Suite coverage: `grep -n '"op": "add"'` in `tests/integration/test-expertise-merge.py` → **zero
matches** (that suite's only `add`-shaped case, `case_add_only_compatibility`/case16, goes through
`apply`, not `ops`). `tests/unit/test-expertise-ops.py`'s two `add` calls (`op("add", "Patterns",
"P-16", ...)`, lines 114/123) target a fresh id, not a duplicated one. The only duplicated-base-id
case in either suite is `case_ambiguous_target`/case14(b) (`tests/integration/test-expertise-merge.py:531-547`),
and it exercises `replace`, never `add`. **CONFIRMED: no case in either suite exercises `add`
against a duplicated base id.**

## Final state

```
$ git status --porcelain
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/qa-mutation-c1.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-c1.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-security-reviewer-c1.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c1.md
```
(Sibling reviewers' untracked notes only — identical to the state before this session started;
this file itself will appear as a fifth untracked entry once written. No tracked file touched.)
