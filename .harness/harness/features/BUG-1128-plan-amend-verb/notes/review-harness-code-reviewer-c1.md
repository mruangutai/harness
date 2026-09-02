# Review — harness-code-reviewer — BUG-1128 panel c1

**VERDICT: FAIL.** Four high-severity findings, two of them crashes/silent-corruption on
scenarios issue #1128 explicitly names as required fail-closed cases, plus a mechanical
`code_grade: fail`. Test claim (218 PASS / 0 FAIL) is confirmed accurate. Scope owned: items
1, 2, 3, 5, 6, 7 (item 4 — security/reachability of `approval:` — belongs to SecRev).

All experiments run against `.claude/skills/harness/bin/plan-merge.py` at `fe5c5b57` in the
worktree, plus scratch fixtures under `/tmp/bug1128-review/`. Real corpus scans ran against the
main checkout's `.harness/*/features/*/plan.yaml` (725 tasks+decisions items) and FEAT-46's own
plan.yaml, copied from its own worktree `.claude/worktrees/harness/FEAT-46-decision-standard/`.

## must_fix (severity high)

**F1 — duplicate/ambiguous id silently resolves to the FIRST match, not refused.**
`plan-merge.py:939 _item_range`. Issue #1128 names this exactly: *"Fail closed on ambiguity:
more than one match…"* — zero implementation, zero test coverage (none of the ten
`case_amend_*` cases uses a duplicate id). The loop's `if m.group(2) == iid and start is None`
only ever records the first occurrence; any later line with the SAME id lands in the
`elif start is not None and len(...) <= len(indent)` branch, which is the "next sibling item"
terminator — it silently closes the first item's range with no signal that a second match
existed. Verified live: a fixture with two `id: T-01` tasks, `amend --show` and a full
`--expect-sha256`+`--value-file` REPLACE both exit 0 against the first copy only, leaving the
duplicate second copy untouched and the caller told nothing about it.

**F2 — an unreadable base document crashes instead of refusing.**
`plan-merge.py:1078`, inside `cmd_amend.transform`:
`if _schema_error(yaml.safe_load(base_bytes.decode("utf-8"))) is None:` — this call is OUTSIDE
the `try/except yaml.YAMLError` that guards the sibling `yaml.safe_load(spliced)` three lines
above. Issue #1128 names *"an unreadable document"* as a required fail-closed case. The gap is
reachable in a realistic shape: the function's own "DO NO HARM" comment anticipates amending a
plan that legitimately doesn't parse yet ("useless exactly where it is needed most" — i.e. using
`amend` to REPAIR a broken plan.yaml). Built exactly that fixture — a task whose own `verify:`
line is the sole thing breaking the base's YAML (`verify: [unclosed`) — and replaced it with a
value that fixes the break. `spliced` now parses fine, so the guarded call passes; the SECOND,
unguarded call re-parses the still-broken `base_bytes` and raises an uncaught
`yaml.parser.ParserError`. Result: exit code **1**, a raw Python traceback on stderr, not one of
the tool's documented codes (0/3/4/5/6/7/8/9). No data is written (verified byte-identical —
`locked_update`'s `except BaseException` still protects the file), but the caller gets a crash
instead of a coherent refusal on a scenario the issue names by name.

**F3 — `code_grade: fail`.** Ran `code-grade.py --base $(git merge-base origin/main fe5c5b57)
--head fe5c5b57` myself (exit 1):
- `_item_range` (`plan-merge.py:939`) — CYCLOMATIC 9, COGNITIVE 14, ABC 22.7, GRADE 3, DRIVER
  cyclomatic+cognitive+abc, BAR 4, `SEVERITY: high`.
- `_field_block` (`plan-merge.py:965`) — CYCLOMATIC 10, COGNITIVE 15, ABC 20.0, GRADE 3, DRIVER
  cyclomatic+cognitive, BAR 4, `SEVERITY: high`.

Both are production write-path functions below the grade-4 bar. Not a coincidence that F1 lives
inside `_item_range`: the tangle the grader flags is the same tangle that let the ambiguity
branch go unwritten.

**F4 — every multi-line field amend violates SPEC.md's documented byte-exact contract, and
silently changes the field's value.** `SPEC.md:1813` gives the canonical `plan.yaml` task shape
and is explicit: `` verify: |  # literal `|`, never folded `>` — a byte-exact contract ``.
`_field_lines` (`plan-merge.py:246`) renders every replacement through
`yaml.safe_dump(..., default_flow_style=False, ...)`, which — confirmed empirically for every
multi-line string tried, with or without special characters — NEVER selects `|` style; it always
produces a quoted, escaped-newline scalar. Verified against the real motivating file
(`FEAT-46-decision-standard/plan.yaml`, copied from its own worktree, `T-23.verify` — the exact
field this feature's own build handoff cites as smoke-tested): an IDENTITY replace — read the
field's current value with `yaml.safe_load`, write it unchanged to `--value-file`, `amend` it
back — produces a DIFFERENT stored value (`yaml.safe_load` before ≠ after) and different raw
bytes. The only difference is the field's trailing `\n`, unconditionally stripped by
`_render_field`'s `value_text.strip("\n")` — real content for every `|`-block field in this repo
(YAML's default clip chomping always keeps exactly one). None of the ten new tests catches this:
every test value is either single-line or has a throwaway `+ "\n"` the test itself expects
stripped, so no test asserts a value's OWN trailing newline survives. `harness_yaml.load_plan`
accepts the mutated file without complaint (checked directly) — nothing downstream notices.
`D-05`/`D-14`, this bug's originally-named motivating fields, happen to be plain single-line
scalars and dodge this (verified: identity replace on D-05 leaves bytes unchanged) — but
`--field verify` is exactly what the diff's own tests exercise, and it is not scoped away from
this defect by anything in the code.

## should_fix (severity med)

**F5 — code_grade grade_2, REASON REQUIRED.** `cmd_amend` (`plan-merge.py:1006`, cyclomatic 11,
ABC 43.3) and `cmd_amend.transform` (`plan-merge.py:1053`, cyclomatic 7, ABC 26.2) are both grade
2 against bar 4 (does not block the build by itself). Reasoned answer: both duplicate the same
locate-then-hash-compare sequence — once unlocked (F-item-1's fast refusal) and once again
inside `transform` (the load-bearing recheck) — which is a deliberate design (see item 1 below),
but the duplication is exactly what drives both functions' scores up. A shared
`_locate_and_verify(lines, key, iid, field, expect_sha)` helper called from both sites would
remove the duplicated branching and likely bring both under grade 4 — genuine simplification,
not just a metric dodge.

**F6 — `_field_block` can bind to a field-name-shaped line inside a PRECEDING field's literal
body.** Demonstrated live: a task with `intent: |` before `verify: |`, whose `intent:` prose
contains a line starting `verify: something` at deeper indent than the item — `--field verify`
binds to that line inside `intent`'s body, not the real `verify:` sibling that comes after.
Scanned the entire real corpus with the actual `_field_block` function — every `tasks:`/
`decisions:` item across every `plan.yaml` under `.harness/*/features/*/` (725 items, run
directly against the worktree's own `pm._field_block`): **zero real instances today.** Per this
review's own scoping instruction, a hazard with no live instance is advisory, not gating — so
this is should_fix, not must_fix. Flagged because `intent:` conventionally precedes `verify:`
on every task in this repo and `verify:` bodies routinely quote shell/Python that could itself
contain a field-name-shaped line as the corpus grows.

## Verified clean — no finding

- **Item 1, pre-lock hash check:** not dead weight. It is a fast, cheap, precise refusal before
  the lock is ever taken. The under-lock recheck in `transform` re-reads `base_bytes` FRESH
  inside `harness_merge.locked_update` (`harness_merge.py:121-152` reads the file AFTER
  `acquire()`, not before) and is independently sufficient to close the TOCTOU window — confirmed
  by reading the lock implementation, not assumed.
- **Item 2, one renderer:** confirmed — no second quoting/rendering grammar exists anywhere in
  the diff; `_render_field` is the sole call site and always routes through
  `_field_lines` → `yaml.safe_dump`. Killed a hand-built naive-f-string mutant live via
  `PLAN_MERGE_BIN=<monkeypatched copy>`: both `case_amend_value_round_trips_through_yaml` and
  `case_amend_value_yes_stays_a_string` go red under the mutant (one on `rc=8` unparseable
  splice, the other on `got=True type=bool`) — genuine `yaml.safe_load` round-trip discrimination,
  not a substring check.
- **Item 5, registration:** `_register_amend(sub)` is called from `main()` right after the
  `VERBS` loop (`plan-merge.py:1162`); reading the table's own documented instruction as licence
  for separate registration is correct, and the verb works end-to-end through the real CLI.
- **Item 7, no half-applied FEAT-46 blocks:** diff touches only `plan-merge.py` and
  `test-plan-merge.py` (confirmed via `git diff --stat`); FEAT-46's `plan.yaml`, in its own
  worktree, is untouched by this diff.

## Test claim verification

`python3 .claude/skills/harness/bin/test-plan-merge.py` in the worktree: **218 PASS / 0 FAIL** —
matches the build handoff's claim exactly.

## code_grade

`code_grade: fail` (mechanical, reproduced myself; base = `2e2e45d2`, computed via
`git merge-base origin/main fe5c5b57`). See F3/F5 above for the specific records.

## Scope note

Item 4 (reachability of `approval:`, `--key approval`, and any other route into the approval
mapping) is SecRev's lens per the shared dispatch, not mine — I did not duplicate it; F1's
duplicate-id gap is a different mechanism from item 4 and does not touch `approval:` (`--key`
stays validated against `AMENDABLE_KEYS` regardless of id ambiguity).
