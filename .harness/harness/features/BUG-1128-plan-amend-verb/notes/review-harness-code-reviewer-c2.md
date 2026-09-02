# Review — harness-code-reviewer — BUG-1128 panel c2 (review_sha `08dd66bb`)

**VERDICT: FAIL.** V4 and V5 are genuinely closed (mutation-proven). V1, V2 and V3's own
mechanism hold for their literal motivating cases — but each remedy has a live, reproduced gap
just outside the scenario it was built for, and one of those gaps (a comment/blank-line silently
deleted at exit 0) is the exact defect class this whole review exists to stop. `code_grade: fail`
persists: `_item_range` is byte-for-byte unchanged from cycle 0 (Q3 never actually closed), and
the V3 remedy introduced a second blocking function, `_verify_amend`. Every claim below was run
live against `.claude/skills/harness/bin/plan-merge.py` at `08dd66bb` in the worktree; fixtures,
mutants and probes live under `/tmp/bug1128-c2/`, never in the worktree.

## must_fix (severity high)

**M1 — a comment or blank line trailing the amended field is silently deleted, exit 0.**
`_field_block`'s non-block forward scan (`plan-merge.py:1052-1057`) terminates only on
`ITEM_ID_RE` or a `SIBLING_KEY_RE` match at `indent <= field's own indent`. A comment or blank
line matches neither, so it is swept into the captured block and vanishes when the block is
spliced out. Reproduced live: a task with
`title: first\n    # NOTE: keep this comment...\n    verify: run the thing\n` — `--show`
already reports the comment as part of `title`'s block and hashes it in; amending `title`
succeeds at exit 0 and the comment is gone (`verify:` and everything else survives). `_verify_amend`
cannot see this: it only compares `got[0]["title"]` against `want`, and the amended field's own
value is exactly what was asked for — the *first* line of the captured range was located
correctly, only its *end* over-captured. This is a distinct mechanism from V1 (V1 is about the
locator binding to the **wrong field entirely**; this is the **correct field's range running
past its own end**), so it is not covered by the V1 fix and not caught by V3. Confirmed
`case_amend_preserves_comments_elsewhere` does not exercise this: its comment lives in the file
**preamble**, before `tasks:`, which never intersects any field's captured range.

**M2 — `case_amend_v3_identity_check_is_live` is vacuous; nothing in the suite would notice if
the load-bearing comparison in `_verify_amend` were deleted.** The test runs the REAL CLI first
(writing the plan), then runs a mutant CLI against the **same file** with the **same, now-stale**
`--expect-sha256`, and asserts `not (real.rc == mut.rc == 0 and read(plan) == read(plan))` — the
second clause is a literal tautology (identical expression on both sides). Reproduced with the
suite's own needle-replace mutant: the mutant string substitution actually raises a `SyntaxError`
(unbalanced parens), so `mut.rc` is 1 for a reason that has nothing to do with the identity
check. Built a clean, syntactically valid mutant instead — `plan-merge.py:340-347`'s
`if got[0].get(field) != want: raise ...` reduced to `return reloaded` — and ran the **entire**
`test-plan-merge.py` suite against it: **37/37 amend cases still PASS**, including
`V3: the check DISCRIMINATES`. The only thing that still catches a `_verify_amend` regression is
the unrelated duplicate-id case, and only because deleting the **whole function call** (a second,
cruder mutant) removes duplicate-id detection too — a targeted regression of the field-value
comparison alone is invisible to every test in the file. `_verify_amend`'s own logic is sound in
isolation (direct unit probe: refuses on a mismatched value, passes on a matching one) — the gap
is the suite's regression protection, not the check itself.

**M3 — `code_grade: fail`, `_item_range` unchanged from cycle 0.** `plan-merge.py:978`,
CYCLOMATIC 9, COGNITIVE 14, ABC 22.7, GRADE 3, DRIVER cyclomatic+cognitive+abc, BAR 4,
`SEVERITY: high` — identical numbers to cycle 0's F3. The duplicate-id fix (V5) landed inside
`_verify_amend`, not `_item_range`; cycle 0's own open question Q3 ("confirm the dev is expected
to land both together") was never actually answered by a code change to this function.

**M4 — `code_grade: fail`, `_verify_amend` is a second, NEW blocking function.**
`plan-merge.py:315`, CYCLOMATIC 9, COGNITIVE 6, ABC 18.5, GRADE 3, DRIVER cyclomatic, BAR 4,
`SEVERITY: high`. The V3 remedy itself now blocks the build it was meant to unblock.

Ran `python3 .claude/skills/harness/bin/code-grade.py --base $(git merge-base origin/main
08dd66bb) --head 08dd66bb` myself: exit 1, 2 functions at `SEVERITY: high` (M3, M4 above), 3 at
`SEVERITY: med` (`_field_block`, `cmd_amend`, `cmd_amend.transform` — see should_fix).

## should_fix (severity med)

**S1 — V1's fix is narrower than the defect class: `BLOCK_HEAD_RE` misses two legal block-header
forms, and `_field_block`'s *locate* loop (not just the body-skip) inherits the blind spot.**
`BLOCK_HEAD_RE = ^(\s*)([A-Za-z_][\w-]*):\s*([|>][+-]?\d*)\s*$` requires chomp-then-digit order
and nothing after the indicator. Two legal YAML forms don't match: an indentation-then-chomping
indicator (`|2-` — confirmed `yaml.safe_load` accepts it, `{'x': 'content here'}`), and a header
carrying a trailing comment (`verify: |  # note` — confirmed `yaml.safe_load` accepts it). For
both, `head = BLOCK_HEAD_RE.match(...)` is `None` in the locate loop
(`plan-merge.py:1039-1044`), so the block body is scanned line-by-line for `SIBLING_KEY_RE`
exactly as before the V1 fix. Reproduced live: a task with `intent: |2-` whose body contains a
prose line `verify: PROSE not a key`, followed by the real `verify: |` field —
`amend --show --field verify` returns the prose line, not the real block (same reproduction for
the trailing-comment header). On a full `--expect-sha256`+`--value-file` replace this is
**fail-closed, not corrupting**, but only *incidentally*: `_verify_amend` refuses because the
real top-level `verify` field it checks stays untouched by the wrong-location splice — nothing
in `_field_block` itself is aware of the miss. `--show` alone, though, silently returns and
hashes the wrong content for these two header shapes, which is misleading for any caller that
reads before deciding. Nested mappings reproduce the identical mechanism and the identical
fail-closed-by-accident outcome: a `checks:\n  verify: nested\n` sibling of the item's real
`verify:` field binds `--show` to the nested key (locate loop has no notion of mapping nesting,
only block-scalar opacity); a full replace is refused only because the true outer field stays
mismatched.

**S2 — form preservation (`_render_field`/`want`) assumes CLIP chomping for every block style,
not just `|`.** `want = value_text if BLOCK_HEAD_RE.match(cur[f2]) else value_text.strip("\n")`
(`plan-merge.py:1174`) uses the raw, unstripped value-file bytes for **every** block header,
regardless of its actual chomping/folding semantics. Confirmed live: an identity replace of a
`|-` (STRIP) field, using a value-file with the trailing newline a normal editor/tool would
write, **always refuses** (exit 5: `asked for: 'do the thing\n' / reloads as: 'do the thing'`) —
STRIP always drops the trailing newline on reload regardless of what was written, so `want`
(unstripped) can never match. A genuinely fresh multi-line value under `>` (FOLD) **always
refuses** for the same reason in the other direction (fold joins the lines PyYAML reloads,
`want` doesn't fold): `asked for: 'new line one\nnew line two\n' / reloads as: 'new line one new
line two\n'`. Both are fail-closed, not corrupting, and `>` is already outside SPEC.md:1813's
`|`-only contract — but `|-` is a legal chomping variant of the literal style V2 claims to fix,
and it is unconditionally unusable with normally-formed input. `_render_field` also silently
collapses any whitespace-only interior body line to fully empty
(`f"{body_indent}{ln}\n" if ln.strip() else "\n"`, `plan-merge.py:1073`), so a value containing
one always refuses too (confirmed live) — fail-closed, but the refusal message ("the wrong-field
write the content hash cannot see") misleadingly implies a location defect rather than the
renderer's own whitespace-stripping.

**S3 — V6 (`--show`/`--value-file` format mismatch) is still open for plain scalar fields.**
`--show` prints the full field **block**, including the `field: value` key line; `--value-file`
expects the bare **value**. Piping one into the other for a plain scalar field still nests
silently at **exit 0**: reproduced live, `title: first` piped through `--show` into
`--value-file` writes `title: '    title: first'`. `_verify_amend` cannot flag this — the caller
asked for exactly that string and got it. Block-scalar fields now happen to be refused on the
same naive pipe (exit 5), but only because the re-emitted header line duplicates and the
resulting value no longer matches `want` — an accidental side effect of V3's check, not a fix to
the format mismatch itself.

**S4 — the do-no-harm/schema branch, and `_verify_amend`'s only consumer, are exercised by zero
tests.** `REQUIRED_TASK_FIELDS` (`harness_yaml.py:288`) includes `change_type`,
`execution_mode`, `files`, `intent`; neither `_amend_plan()` nor `_block_plan()` supplies them.
Confirmed directly: `_schema_error(yaml.safe_load(_amend_plan()))` and the `_block_plan()`
equivalent are both non-`None` (both fixtures are already schema-invalid), so
`if _schema_error(base_doc) is None:` (`plan-merge.py:1181`) is `False` in every `case_amend_*`
case — the post-splice schema refusal (exit 8, "would not be legal") never fires, and `reloaded`
— `_verify_amend`'s return value, the thing the author's self-disclosed NameError fix touches —
is never read by anything the suite runs.

**S5 — exit 8 is one code for three unrelated meanings, undocumented for `amend`.** Within
`cmd_amend` alone it means "the base doesn't parse" (`plan-merge.py:1145-1147`) and "the spliced
result violates the schema" (`plan-merge.py:1183-1184`); the tool's top-of-file exit-code table
and `_register_amend`'s docstring document neither, and `apply` already uses 8 for a third,
unrelated meaning ("proposal's approval mapping parses differently from the base's"). Each
message is unambiguous to a human; a caller branching on exit code alone cannot distinguish
"the base needs repair first" from "your replacement value would break schema."

**S6 (unchanged from cycle 0's F5) — `cmd_amend` and `cmd_amend.transform` remain grade 2.**
`cmd_amend` (:1088, cyclomatic 11, ABC 43.3) and `cmd_amend.transform` (:1135, cyclomatic 7, ABC
29.6) both carry `SEVERITY: med`, `REASON REQUIRED`. Reasoned answer, same as cycle 0: both
duplicate the locate-then-verify sequence (fast pre-lock check, load-bearing under-lock
re-check) by design — V3 and V4's additions to `transform` grew it further without addressing
the underlying duplication a shared `_locate_and_verify` helper would remove.

## Verified clean — no finding

- **V4 (unreadable base) — CLOSED, mutation-proven.** Built a `revert_v4` mutant restoring the
  exact pre-fix shape (parse `base_bytes` unguarded, late, after the splice) and ran the suite:
  `case_amend_v4_unparseable_base_refuses_cleanly` correctly fails against it. The remedy and its
  test are both real.
- **V5 (duplicate id) — CLOSED, mutation-proven.** Deleting the entire `_verify_amend` call (not
  just the field check) makes `case_amend_duplicate_id_is_refused` fail — the uniqueness check
  lives solely inside `_verify_amend`, genuinely exercised.
- **`_verify_amend`'s comparison logic itself, in isolation** — direct unit probe: refuses when
  the reloaded field value differs from `want`, passes when it matches. Correct when reached;
  M2 is about the suite's failure to hold it there, not about the logic being wrong.

## Verdict per cycle-0 finding

| id | verdict | note |
|----|---------|------|
| V1 | **open** | narrowed, not closed — reproduces for `\|2-` and header+comment forms (S1) |
| V2 | **closed** (motivating case) | plain `\|` clip round-trips correctly; general mechanism has a residual gap, tracked as S2 |
| V3 | **closed** (mechanism) / **new must_fix** | check itself is correct; its own regression test is vacuous (M2) |
| V4 | **closed** | mutation-proven |
| V5 | **closed** | mutation-proven |
| V6 | **open** | plain-scalar naive pipe still nests silently at exit 0 (S3) |

## code_grade

`fail` — `_item_range` (:978, unchanged from cycle 0) and `_verify_amend` (:315, new) both
`SEVERITY: high`; `_field_block`, `cmd_amend`, `cmd_amend.transform` all `SEVERITY: med`.

**`_field_block` got MERELY LARGER, not simpler.** Cycle 0: cyclomatic 10, cognitive 15, ABC
20.0, GRADE 3 (`high`). Cycle 1: cyclomatic 13, cognitive 21, ABC 28.4, GRADE 2 (`med`) — every
metric increased; only the grade *bucket* moved, non-monotonically with complexity, off the
tool's own classification, not because the V1 remedy simplified anything.

## Scope note

CLI message wording is ui-reviewer's lens; I did not duplicate it beyond citing what a message
says when it bears directly on a correctness finding (S2, S5). Test-suite adequacy beyond what
bears on my own findings (M2, S4) is qa's lens.
