# Receipt — harness-backend-dev — BUG-1308 cycle 3 (final) — VL-06

## Headline

VL-06 is closed. `_validate_target_section` now anchors `target` against `ENTRY_RE`'s id grammar
for all three verbs, via a pure insertion (`_validate_target_grammar`, `expertise-merge.py:191-203`)
called at line 213. Both panel-measured exploits are reproduced RED against the pin, confirmed
GREEN (exit 12) after the fix, and the panel's stated lockout consequence is proven gone.

## 1. Pre-fix reproduction (verbatim)

Copied the pinned `expertise-merge.py`+`harness_merge.py` into `/tmp/prefixbin/` (sha256
`6915b7e3e20317b60a27a6d800896f9b9e4bb4ce66c22b34de3655db2de46e3a` for `expertise-merge.py`,
byte-identical to `git show HEAD:...`), invoked directly against fresh `$TMPDIR` fixtures. No
tracked file was touched for this step.

**Exploit A** (`add target="PPPP-1"`, base `Gotchas: [G-01]`):
```
ADDED PPPP-1
APPLIED /tmp/.../harness-test-agent.md
exit=0
```
Re-parse with the tool's own `parse_expertise`: `Gotchas entries: [('G-01', 'existing gotcha one.')]`
— the added entry is invisible. A following, unrelated `replace P-01` then silently drops the
`PPPP-1` line from the file entirely (`grep -c PPPP-1` → `0` after).

**Exploit B** (`add target="P-01: fake prefix"`, base `Patterns: [P-01]`):
```
ADDED P-01: fake prefix
APPLIED /tmp/.../harness-test-agent2.md
exit=0
```
Re-parse: `Patterns entries: [('P-01', 'existing pattern one.'), ('P-01', 'fake prefix: attacker text')]`,
`P-01 count: 2`. A following legitimate `replace target=P-01` then hits the pre-existing
lockout: `AMBIGUOUS TARGET section=Patterns id=P-01 reason=the id appears 2 times in section
Patterns`, exit **11**.

## 2. Fix

`_validate_target_grammar(target, index)` inserted at `expertise-merge.py:191-203`, called from
`_validate_target_section` at line 213 (right after the existing `_reject_multiline` call, the
same Step-A gate). Mechanism, one sentence (`derivation_mechanism` in DIGEST): it round-trips
`target` through `ENTRY_RE` itself via the exact synthetic line `render` would write
(`ENTRY_RE.match(f"- {target}: x")`) and requires the anchored match's captured id equal `target`
verbatim — `"PPPP-1"` fails to match at all, `"P-01: fake prefix"` matches but captures
`"P-01" != target`, so both exploits are refused by the SAME equality, never a hand-rolled anchor.

**Derived, not re-typed**, evidence:
```
$ grep -n '\[A-Za-z\]{1,3}' .claude/skills/harness/bin/expertise-merge.py
43:ENTRY_RE = re.compile(r"^- ([A-Za-z]{1,3}-\d+): (.*)$")
196:    hand-copied `[A-Za-z]{1,3}-\\d+` literal (REQ-07 forbids editing `ENTRY_RE`, and duplicating
```
Line 43 is the sole regex literal (`ENTRY_RE` itself, untouched, REQ-07 forbids editing it); line
196 is prose inside the new function's docstring, not a second pattern object.

## 3. Post-fix reproduction of both exploits, plus the lockout-cleared proof

Exploit A, post-fix, fresh fixture: `MALFORMED OPS op index=0: target 'PPPP-1' does not match the
entry id grammar`, exit **12**. sha256 before/after: `495f78b8...86aea7` == `495f78b8...86aea7`
(unchanged). Re-parse: `Gotchas entries: [('G-01', 'existing gotcha one.')]` — no new entry.

Exploit B, post-fix, fresh fixture: `MALFORMED OPS op index=0: target 'P-01: fake prefix' does not
match the entry id grammar`, exit **12**. sha256 before/after:
`703b1f59...b86aea` == `703b1f59...b86aea` (unchanged — full values in section 5). Re-parse:
`Patterns entries: [('P-01', 'existing pattern one.')]`, `P-01 count: 1`.

**Lockout proof**: immediately following the refused Exploit B, a legitimate
`replace target=P-01` on the SAME file now exits:
```
REPLACED P-01
APPLIED ...
exit=0
```
— not the pre-fix `exit 11`. The refused `add` never planted the second `P-01`, so nothing is
locked out.

**Positive control** (well-formed target still succeeds): `add target=P-02` on a fresh fixture
→ `ADDED P-02`, exit 0. The check does not reject everything.

## 4. Permanent regression tests

Unit (`tests/unit/test-expertise-ops.py`), pure `resolve_ops`, no filesystem:
- `case_u21` — malformed-target grammar, all 3 verbs: `add "PPPP-1"`, `add "P-01: fake prefix"`,
  `replace "PPPP-1"`, `drop "PPPP-1"` — each asserts `MergeRefusal(12)` starting `MALFORMED OPS`.
- `case_u22` — positive control: well-formed `add target="P-02"` still succeeds
  (`("ADDED", "P-02")` in outcomes, entry present in merged Patterns).

Integration (`tests/integration/test-expertise-merge.py`), full CLI subprocess + file:
- `case_ops_target_grammar` (case 25) — (a) too-long id `PPPP-1`: exit 12, sha256 unchanged,
  re-parsed `Gotchas` holds no new entry. (b) id-embedding target `"P-01: fake prefix"`: exit 12,
  sha256 unchanged, re-parsed `Patterns` holds exactly one `P-01`, **and** a following legitimate
  `replace target=P-01` exits 0 (the lockout-is-gone assertion).
- `case_ops_target_grammar_well_formed` (case 26) — positive control: well-formed `add target=P-02`
  exits 0, rendered file contains the new entry.

**RED demonstration.** Ran both test files with `EXPERTISE_MERGE_BIN=/tmp/prefixbin/expertise-merge.py`
(a copy of the pinned, pre-fix source plus its unmodified `harness_merge.py` sibling, so the
local `import harness_merge` resolves) against the *new* test code:

Unit, pre-fix module: exit 1, 6 `FAIL` lines, all under `u21` (u22 stayed green — the positive
control does not manufacture a false red):
```
FAIL  u21: add too-long id: raises MergeRefusal | no exception raised
FAIL  u21: add embeds valid id: raises MergeRefusal | no exception raised
FAIL  u21: replace too-long id: code is 12 | 10
FAIL  u21: replace too-long id: line starts MALFORMED OPS | ['MISSING TARGET section=Patterns id=PPPP-1 ...']
FAIL  u21: drop too-long id: code is 12 | 10
FAIL  u21: drop too-long id: line starts MALFORMED OPS | ['MISSING TARGET section=Patterns id=PPPP-1 ...']
```
Integration, pre-fix module: exit 1, 8 `FAIL` lines, all under `case25` (case26 stayed green):
```
FAIL  case25: (too-long id vanishes on reparse) exits 12
FAIL  case25: (too-long id vanishes on reparse) combined output carries MALFORMED OPS
FAIL  case25: (too-long id vanishes on reparse) file sha256 is unchanged
FAIL  case25: (id-embedding target refused, not aliased) exits 12
FAIL  case25: (id-embedding target refused, not aliased) combined output carries MALFORMED OPS
FAIL  case25: (id-embedding target refused, not aliased) file sha256 is unchanged
FAIL  case25: (b) re-parsed Patterns holds exactly one P-01
FAIL  case25: (b) a following legitimate replace of P-01 exits 0, not 11
```
Both, run against the working-tree (post-fix) module: exit 0, 0 `FAIL`.

## 5. Atomicity (sha256 before/after, both refusal paths)

- Exploit A: before `495f78b8858aff549b86192d51d5bbf24c9ff83082b1accbbc78a5326b86aea7`, after
  `495f78b8858aff549b86192d51d5bbf24c9ff83082b1accbbc78a5326b86aea7` — identical.
- Exploit B: before `703b1f59c6ace96ca7e49678b60cea3447bc65b7dceb075bb29f08a96342eb5e`, after
  `703b1f59c6ace96ca7e49678b60cea3447bc65b7dceb075bb29f08a96342eb5e` — identical.
- `case25`'s own sha256 assertions (both sub-cases, in-process via subprocess CLI calls) are part
  of the green integration run above.

## 6. Code grade, before/after, every touched test function

New functions did not exist pre-fix, so "before" is N/A for them; "after" (graded against the
working tree via `code-grade.py`'s positional-path mode, since `--head HEAD` reads the committed,
pre-fix tree only):

| function | file | cyclomatic | cognitive | ABC | grade | bar | result |
|---|---|---|---|---|---|---|---|
| `_validate_target_grammar` (production) | expertise-merge.py:191 | 3 | 3 | 5.1 | 5 | 4 | PASS |
| `_assert_case25_malformed` | test-expertise-merge.py:1231 | 2 | 1 | 19.4 | 4 | 3 | PASS |
| `case_ops_target_grammar` | test-expertise-merge.py:1250 | 3 | 0 | 24.0 | 3 | 3 | PASS |
| `case_ops_target_grammar_well_formed` | test-expertise-merge.py:1294 | 1 | 0 | 10.0 | 4 | 3 | PASS |
| `case_u21` | test-expertise-ops.py:335 | 1 | 0 | 9.2 | 4 | 3 | PASS |
| `case_u22` | test-expertise-ops.py:352 | 1 | 0 | 7.3 | 5 | 3 | PASS |

Full run: `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/expertise-merge.py tests/unit/test-expertise-ops.py tests/integration/test-expertise-merge.py`
→ `PASSING: 101`, plus 10 pre-existing grade-2 `RESULT: FAIL` rows, all confirmed (by function
identity, not just count) to be the same four the code-reviewer's c3 review already reported and
reasoned (`case_missing_target`, `case_ambiguous_target`, `case_contract_drift`,
`case_multi_op_composition`) plus their sub-blocks from the file's own multi-block grading —
none touched by this diff, none grade 1, none new.

## 7. REQ-07 / scope confirmation

```
$ git diff origin/main -- .claude/skills/harness/bin/expertise-merge.py | grep -c '^-[^-]'
0
```
Pure insertion confirmed. `git diff origin/main -- .claude/skills/harness/bin/expertise-merge.py`
shows only new `+def ...` blocks (`_validate_target_grammar` plus the one new call-site line);
`apply`, `compute_union`, `cmd_apply` bodies carry zero changed/removed lines — grepped their
diff hunks directly (see hunk headers `@@ -139,6 +140,277 @@ def compute_union(...)` and
`@@ -274,6 +546,58 @@ def cmd_apply(...)`, both `+`-only after the anchor line).

## 8. Both suites

```
$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit
exit=0, ^FAIL  count=0, pool: 8 workers, 28 files, 3.81s wall
$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
exit=0, ^FAIL  count=0, pool: 8 workers, 46 files, 62.60s wall
```
Both match baseline (28 unit files / 46 integration files).

## 9. git status / HEAD

```
$ git status --porcelain
 M .claude/skills/harness/bin/expertise-merge.py
 M tests/integration/test-expertise-merge.py
 M tests/unit/test-expertise-ops.py
$ git rev-parse HEAD
5464cb971727d1c619d9df5e5e1a725f1532d0cb
```
No commit made. HEAD unchanged (`5464cb97`). Only the three in-scope files touched.

## 10. SPEC wording (not applied — `.claude/skills/harness-documentor` owns SPEC.md)

At `SPEC.md:970`'s `12 MALFORMED OPS` row, append (or add an adjacent row with the same "The
payload is..." lead-in) exactly:

> ", or gives a `target` that does not match `ENTRY_RE`'s entry-id grammar — anchored via the
> synthetic line `render` would write for it (`_validate_target_grammar`,
> `.claude/skills/harness/bin/expertise-merge.py:191-203`)"

## Open questions

None blocking.
