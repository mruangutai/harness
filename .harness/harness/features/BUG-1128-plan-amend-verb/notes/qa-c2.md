# QA gate — BUG-1128-plan-amend-verb — panel c2 — review_sha `08dd66bb`

**BLUF: FAIL.** The evidence claims reproduce exactly (229/0, run-unit-tests.sh 0 FAIL,
check-state.sh 0 violations) and V1/V2/V4's mutation counts reproduce exactly (3/1/2). But the
panel's own headline remedy — `_verify_amend`'s value-comparison check, the thing that "demotes
V1, V2 and V6 to refusals" — has **zero regression coverage**: `case_amend_v3_identity_check_is_live`
is vacuous (H2 confirmed), and a syntax-valid mutant that deletes only that check trips **0 of
229 assertions**. Separately, a **new, live, silently-reproducible defect** exists that none of
the four remedies touch: amending any field on an item that has a comment or blank line between
fields **silently deletes it** at exit 0 with a clean `AMENDED` receipt (H1, reproduced twice).
The do-no-harm schema branch and its `reloaded` return value are provably dead in every test
(H7). H4/H5 (BLOCK_HEAD_RE gaps, nested-mapping mis-binding) reproduce as **`--show` lying about
content**, but the actual write is fail-closed thanks to V3 — real, but milder than V1. H3
(`|-`/`>` unusable under ordinary conventions) is fail-closed, a functional gap not a corruption.
Item 4's carried-over gap (`case_amend_refuses_an_unknown_key` non-discriminating) is unchanged.

## 1 — Author's evidence, verified by running it

| claim | author said | observed (this run, `08dd66bb` pin) |
|---|---|---|
| `test-plan-merge.py` | 229 PASS / 0 FAIL | **matches** — `python3 .claude/skills/harness/bin/test-plan-merge.py`, exit 0, 229 PASS lines, 0 FAIL lines |
| `run-unit-tests.sh` (full) | exit 0, 0 FAIL | **matches** — `bash .claude/skills/harness/bin/run-unit-tests.sh`, exit 0, `grep -c '^FAIL'` → 0 across 3814 lines. `test-plan-merge.py` confirmed present and PASS (line 3375-3376); still member of `INTEGRATION_SCRIPTS` only, never `UNIT_SCRIPTS` (`run-unit-tests.sh:31`) — the matrix-floor gap from cycle 0 (V8) is structurally unchanged, not a target of this cycle's remedies |
| `check-state.sh` | exit 0, 0 violations | **matches after my own cleanup** — first run showed exactly one `VIOLATION INV-29`, self-caused by a scratch worktree (`bug1128-qa-mutate-c2`) I created for mutation testing and then removed via `git worktree remove` (clean tree, no `--force` needed); re-run after removal: exit 0, 0 violation lines. Not attributable to this diff |

## 2 — Mutation re-derivation of V1–V4

Method: copy `plan-merge.py` to a scratch dir, mutate, run the **full** `test-plan-merge.py`
suite against it via `PLAN_MERGE_BIN=<mutant>` (the test file's own env-var override,
`test-plan-merge.py:24`) with `PYTHONPATH` pointed at the real `bin/` dir so sibling imports
(`factory_config`, `harness_merge`, etc.) resolve without copying them. Each mutant restored by
discarding the scratch copy; the tracked tree was never touched (confirmed via `git status
--porcelain` — clean throughout).

| finding | mutation | author claimed | observed |
|---|---|---|---|
| V1 | remove the `if head and ...: i = _block_scalar_end(...); continue` skip in `_field_block` (:1044-1046) | 3 assertions | **matches — exactly 3**: `V1: --show binds to the REAL verify…`, `V1: and does not return the intent body`, `V2: an identity replace of a block field SUCCEEDS` (collateral: V2's case also depends on the skip to find the real field first) |
| V2 | remove the block-scalar-form-preserving branch in `_render_field`, always route through `_field_lines` (:1077-1085) | 1 assertion | **matches — exactly 1**: `V2: an identity replace of a block field SUCCEEDS` |
| V4 | remove the `try/except yaml.YAMLError` around `base_doc = yaml.safe_load(raw)` (:1141-1147) | 2 assertions | **matches — exactly 2**: `V4: an unparseable base refuses rather than crashing`, `V4: and the refusal says the plan on disk does not parse` |
| V3 | **see §3 below — does not reproduce** | 3 assertions | **0 or 2, never 3; the identity check itself is caught by nothing** |

Self-disclosed V4-dummy-hash bug confirmed real: ran the same unparseable-base fixture with
`--expect-sha256 0*64` (dummy) against the V4 mutant — exits 6 (stale hash) before the guard is
ever reached, would leave the case vacuous. The suite's actual `_sha_of(...)` real-hash call
(`test-plan-merge.py:1362`) is what makes it non-vacuous. Confirmed by direct run, not inferred.

## 3 — H2: `case_amend_v3_identity_check_is_live` is vacuous — CONFIRMED

Command: replicated the case standalone (`test-plan-merge.py:1313-1345`'s own logic, executed
directly) to inspect what it actually measures:

```
sha 2c96e12055b5efe539ed93154d5084fb3dff7cb74f6535dd15eae3dd8dd52fc6
real rc 0
plan changed after real run? True
mut rc 1
mut stderr: File ".../mutant.py", line 1176
    reloaded = (lambda *a, **k: None)("utf-8"), args.key, args.id, args.field, want)
                                                                                   ^
SyntaxError: unmatched ')'
tautology read(plan)==read(plan): True
```

(a) **`read(plan) == read(plan)` is a syntactic tautology**, confirmed literally True — same
expression evaluated twice with nothing between, always equal regardless of what the mutant did.
(b) **`mut.returncode` is 1, not 6-from-a-stale-hash** as hypothesized — the string-replace the
case performs (`needle = "_verify_amend(spliced.encode("`) is **unbalanced**: it deletes an open
paren without deleting its matching close, so the "mutant" script never parses. The check
`not (real.returncode == mut.returncode == 0 and ...)` trivially passes because ANY crash makes
`mut.returncode != 0` — the case "discriminates" via a Python `SyntaxError`, never by exercising
the identity-check logic it names.
(c) Ran the **full suite** against this literal mutant: 90 of 229 assertions fail, but for the
wrong reason — every subprocess invocation crashes with the same `SyntaxError`, so this "proves"
nothing about `_verify_amend` specifically; it proves the file doesn't parse.

**The genuinely semantic mutant** (dispatch's own instruction: keep `_verify_amend` returning
`reloaded`, delete only its refusals, stay syntax-valid) — three variants, isolating the claim:

| mutant | removed | suite result |
|---|---|---|
| full removal (not-list check + duplicate-id check + value-mismatch check, `return reloaded` kept) | all 3 raises in `_verify_amend` | **2 FAIL**, both from `case_amend_duplicate_id_is_refused` (`a duplicate id is refused…`, `and the plan is unchanged`). `case_amend_v3_identity_check_is_live` does **not** fail |
| isolated: only `if got[0].get(field) != want: raise …` removed | just the value-comparison — **the actual identity check**, V3's whole point | **0 FAIL** |
| isolated: same removal, `return None` instead (author's warned-confounded variant) | same, but with the "return value feeds `_schema_error`" hazard the dispatch names | **0 FAIL** — because (§4/H7) that branch never runs on any fixture in the suite, so even the confounded variant can't get caught by it |

**Conclusion: the author's "3 assertions" claim for V3 does not reproduce under any
syntax-valid mutation of `_verify_amend`'s value check.** The only mutation that trips exactly
"3-ish" assertions (2, from a different check in the same function) is the duplicate-id guard,
not the value-comparison guard the panel actually named as the fix. **The specific line
`if got[0].get(field) != want:` — the comparison `_verify_amend`'s own docstring calls "the
discipline `_verify_signature` already held" — is exercised by zero tests in the 229-case
suite.** This is the panel's stated headline remedy, unprotected against regression.

## 4 — H7: the do-no-harm schema branch is dead — CONFIRMED by measurement

`REQUIRED_TASK_FIELDS` (`harness_yaml.py:288-289`) = `id, title, change_type, execution_mode,
files, verify, intent`. Checked both fixtures directly against `harness_yaml.validate_plan_doc`:

```
_amend_plan  schema_error = ...tasks[0] (T-01) is missing ['change_type', 'execution_mode', 'files', 'intent']
_block_plan  schema_error = ...tasks[0] (T-01) is missing ['title', 'change_type', 'execution_mode', 'files']
```

Both — and the inline fixture in `case_amend_duplicate_id_is_refused` (also missing these
fields) — always fail the schema. So `if _schema_error(base_doc) is None:`
(`plan-merge.py:1180`) is **never True in any case in the suite.** Confirmed by mutation:
replacing the whole branch (:1180-1184) with `pass` → **0 FAIL** across all 229 assertions.
The branch, and the `reloaded` value `_verify_amend` returns for it to consume (the author's
self-disclosed NameError fix), are exercised by nothing.

## 5 — H1: silent comment/blank-line deletion — REPRODUCED LIVE, twice, NOT one of V1-V4

Mechanism: `_field_block`'s **non**-block-scalar end-scan (`plan-merge.py:1052-1058`) stops only
at `ITEM_ID_RE` or a `SIBLING_KEY_RE` match at indent `<=` the field's own indent. A comment
(`#...`) or blank line matches neither `SIBLING_KEY_RE` (requires `[A-Za-z_]` at line start) nor
`ITEM_ID_RE` — so it is silently swept into the "field block" being replaced.

**Case A — mid-item comment.** Fixture:
```
tasks:
  - id: T-01
    title: original title
    # NOTE: keep this
    verify: run the thing
    status: ready
```
`amend --field title --show` block = `title:` line **plus** the comment line (confirmed via
`--show` output). Full replace: `--expect-sha256 <shown> --value-file <renamed>`:
```
AMENDED tasks:T-01.title
APPLIED /private/tmp/.../plan.yaml
rc=0
```
After:
```
tasks:
  - id: T-01
    title: renamed title
    verify: run the thing
    status: ready
```
`# NOTE: keep this` is **gone**. Clean `AMENDED`/`APPLIED` receipt, exit 0, no warning.

**Case B — last field of the last item, trailing comment before the next top-level key.**
Fixture:
```
tasks:
  - id: T-01
    title: only task
    status: ready
# TRAILING COMMENT before decisions, must survive
decisions:
  - id: D-01
    choice: something
```
`amend --field status --show`: block includes the comment (`SIBLING_KEY_RE` matches
`decisions:` at indent 0 <= the field's indent 4, so the scan stops there — but the intervening
comment line, indent-blind, is inside the swept range). Full replace of `status`:
```
AMENDED tasks:T-01.status
rc=0
```
After: `# TRAILING COMMENT before decisions, must survive` is gone; `decisions:` and its content
survive untouched.

**Why V3 cannot catch this and why the suite doesn't either.** `_verify_amend` compares only
`got[0][field]` — the amended field's own reloaded value, which is correct in both cases above
(the title/status field itself reads back exactly right). It asserts nothing about content
outside that one field, so a comment vanishing beside it is invisible to the check. And
`case_amend_preserves_comments_elsewhere` (cycle 0's finding, still true) places its comment in
the file **preamble**, which never intersects any field's scanned span — it cannot detect this
class at all. This is a **live, silent, reproducible defect** at exit 0 that none of V1–V4
addresses; it is the concrete second instance the dispatch's H6 asked me to find (the identity
check protects one field; damage elsewhere passes).

## 6 — H3: block-scalar form coverage — CONFIRMED, refined

Identity replace (write back the exact current value) succeeds for `|`, `|-`, `|+`, `|2`, and a
4-space-indented `|` body — all round-trip correctly, `rc=0`. **But identity replace is not
representative of how a caller actually writes a value file.** Testing a genuinely **new** value
written the way every fixture in this suite writes one (`f.write(newval + "\n")`):

| form | new single-line value | new multi-line value |
|---|---|---|
| `\|` (plain literal) | rc=0, correct | rc=0, correct — the motivating case |
| `\|2` (indicator) | — | rc=0, correct |
| `\|+` (keep) | — | rc=0, correct |
| `\|-` (strip/clip) | **rc=5, REFUSED** | (same defect, not retested) |
| `>` (folded) | rc=0 (coincidence — one line, folding is a no-op) | **rc=5, REFUSED** |

`\|-` refusal, reproduced: value file `'brand new content\n'` →
`REFUSED: ... asked for: 'brand new content\n' / reloads as: 'brand new content'`. `>` refusal,
reproduced: value file `'line one\nline two\n'` → `reloads as: 'line one line two\n'`. Root
cause (`plan-merge.py:1175`): `want = value_text if BLOCK_HEAD_RE.match(cur[f2]) else
value_text.strip("\n")` treats every block-scalar header as if it preserves the value file's
raw bytes, but YAML's own chomping (`-`) and folding (`>`) rules transform the reload regardless
of what was written. **Fail-closed — no corruption — but `\|-` and `>` fields are effectively
unusable via `amend` under the value-file convention this codebase itself uses everywhere else.**
Advisory, not blocking on its own: no `\|-` or `>` field exists in FEAT-46's real plan.yaml today
(spot-checked the fixture pattern against SPEC.md:1813's byte-exact `\|` contract, which is the
only form the spec actually requires).

## 7 — H4/H5: BLOCK_HEAD_RE gaps and nested-mapping mis-binding — CONFIRMED, fail-closed on write

`BLOCK_HEAD_RE = ^(\s*)([A-Za-z_][\w-]*):\s*([|>][+-]?\d*)\s*$` does not match `\|2-`
(indicator-before-chomp order — legal YAML, confirmed via `yaml.safe_load`) or a header with a
trailing comment (`verify: \|  # literal` — also legal, confirmed parses). Reproduced both live:
a fixture with `intent: \|2-` (or `intent: \|  # literal`) whose body contains a prose line
`verify: ...`, followed by the real `verify: \|` field:

```
$ amend --field verify --show
      verify: this line is PROSE inside a block scalar (indicator-then-chomp form)
      and must never be mistaken for a key.
sha256: 9305a05... / de82fd9...   # WRONG block, WRONG hash, exit 0
```

Same shape for a **nested mapping** (H5): `checks:\n  verify: nested value` preceding the real
`verify:` field — `SIBLING_KEY_RE` matches the nested key (only block-scalar bodies are skipped,
not arbitrary nested mappings) — `--show --field verify` returns the nested value, exit 0.

**But the actual replace is refused, not corrupting**, in all three variants — confirmed by
running the full write with a deliberately different value against the (wrong) hash `--show`
printed:
```
REFUSED: ... T-01.verify would not say what was asked for.
  asked for: 'corrupted'
  reloads as: 'python3 -c "print(\'the real verify\')"\n'   # (or 'real value\n' for H5)
rc=5
```
Plan confirmed byte-identical after each refusal (direct string comparison against the
pre-amend fixture). **V3's per-field identity check is why**: since the splice landed in a
different named field (`intent`/`checks`), the real `verify:` field's reloaded value is
untouched and can never equal the caller's intended new value — so V1's original *silent
corruption* mode is closed for this class specifically. What remains is narrower but still real:
**`--show` reports the wrong content and a wrong sha256 for these two legal header shapes and
for nested mappings**, which could mislead an operator (they'd see plausible-looking content,
compute a "correct" hash for it, and always get refused on write — confusing but not damaging).

## 8 — Item 4: vacuity audit of the other `case_amend_*` cases

`case_amend_refuses_an_unknown_key` — **still non-discriminating, unchanged from cycle 0.**
Mutation: disabled the `AMENDABLE_KEYS` gate entirely (`if False: ...` in place of the check at
`plan-merge.py:1091-1095`) — full suite: **0 FAIL**. `approval:` remains structurally
unreachable via `_item_range` regardless of the guard (no `- id:` line under a flat mapping), so
the case that names this defends nothing the guard itself provides. None of V1-V4 touched this
code path; it is carried over, not regressed.

`case_amend_v4_unparseable_base_refuses_cleanly` — confirmed non-vacuous with the real hash it
uses (§2); confirmed it WOULD be vacuous with a dummy hash (§2). Genuinely fixed.

The remaining cases (`show`, `replaces_a_multiline_decision_field`, `refuses_a_stale_hash`,
`requires_the_hash`, `refuses_absent_id...`, `refuses_absent_field`, `preserves_comments_elsewhere`,
`value_round_trips_through_yaml`, `value_yes_stays_a_string`, `duplicate_id_is_refused`) each
name a distinct, narrow behavior directly asserted by content (not substring/exit-code-only) —
consistent with cycle 0's adequacy table, unchanged by this diff, and cross-checked here via the
V1-V4 mutation runs (each of those mutants trips exactly the assertions belonging to its own
named case, never a neighboring one, which is itself evidence the other cases are not
accidentally masking each other).

## Open items for the panel

1. **H2 is the decisive finding.** The value-comparison check inside `_verify_amend` — what the
   cycle-0 digest called "the discipline `cmd_sign_approval` already held and `amend` did not
   inherit" — has no test that fails when it is removed. Recommend a **direct** case: mutate (or
   monkeypatch, if that's acceptable here unlike elsewhere in this file) `_verify_amend` to skip
   only its value comparison, run a REAL replace with a deliberately wrong value, and assert
   `rc == 0` is refused. `case_amend_v3_identity_check_is_live`'s subprocess-mutation approach
   needs its string-replace fixed to stay syntax-valid, or replaced with a case that runs the
   real function through a wrong-field fixture the way H4/H5 do above (those two ARE, in effect,
   a working identity-check regression test — just uncredited as one).
2. H1 (comment/blank-line loss) is new, live, and silent at exit 0. Recommend `_field_block`'s
   plain-field end-scan also stop before a comment or blank line immediately preceding the next
   sibling key/item, or exclude trailing comment/blank lines from the emitted-replacement range.
3. H7: the do-no-harm schema branch cannot be exercised by any fixture in this file without a
   full `REQUIRED_TASK_FIELDS`-satisfying fixture (`change_type`, `execution_mode`, `files`,
   `intent` all present) — worth a dedicated fixture rather than reusing `_amend_plan`/`_block_plan`.
4. H3 (`\|-`/`>` unusable) and H4/H5 (`--show` misreports content for two legal header shapes and
   nested mappings) are real but non-blocking on their own — fail-closed, not corrupting — unless
   the panel wants `\|-`/`>` support or `--show` accuracy in scope for this bug.
5. V8 (matrix floor `unit` unmet) persists unchanged; not this cycle's remedy target, still
   routes to pm/main session per cycle 0.
