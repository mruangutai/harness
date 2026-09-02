# QA gate — BUG-1128-plan-amend-verb — panel c1 — review_sha fe5c5b57

**BLUF: FAIL.** Two live, reproducible defects, both unbound by any of the ten `case_amend_*`
cases: (1) `_field_block` mis-binds when a field name appears as a false sibling-key-shaped line
inside a preceding literal-block field's BODY — reproduced live, causes a *silent wrong-field
write reported as success* (item 3); (2) the UNDER-LOCK hash re-check, exit-8 unparseable, exit-8
illegal-schema, and the do-no-harm branch are **entirely unexercised** — deleting all of them
leaves the suite at 0 FAIL (item 1 in part, plus the exit-8/do-no-harm items from the adequacy
list). The matrix's own `unit` floor is also not met by anything in this diff. Scoped out: none
of items 1–7; all seven addressed below. Items 2, 5, 6, 7 check out clean.

## Trust claims — verified, not accepted

| claim | author said | observed (this run, fe5c5b57 pin) |
|---|---|---|
| `test-plan-merge.py` | 218 PASS / 0 FAIL | **matches** — exit 0, 218 PASS, 0 FAIL |
| `run-unit-tests.sh --kind unit` | exit 0, 0 FAIL | **exit 0, 517 PASS, 0 FAIL — but `test-plan-merge.py` is not a member of `UNIT_SCRIPTS` and never ran** (see Matrix below) |
| `run-unit-tests.sh --kind integration` | (not separately claimed) | exit 0, 850 PASS, 0 FAIL, `test-plan-merge.py` present |
| `check-state.sh`: exactly one violation, `INV-26` on `BUG-1081` | — | **exit 0, zero `violation`-severity lines at all** (script's own legend: "Exit 0 = all invariants hold"). All 737 printed lines are `note`-level, informational; zero `INV-26` hits. This is repo-wide state that moves independently of this diff (other sessions landed commits since the build's 58742037 measurement) — not attributable to this diff, but the specific count/id the author cited does not reproduce now |
| red-first: 204 PASS / 9 failing before the verb existed | — | **cannot be established from the record.** `git log --oneline -- test-plan-merge.py` shows the entire BUG-1128 diff (both files) landed in **one commit**, `fe5c5b57`. No earlier commit in this range shows a pre-verb red state. The claim rests on the author's own narrative, not on anything the repository records |

## Matrix — `unit` is the real gap here

`plan.yaml` is `station_only: true`, `tasks: []` (main-session-direct, DEC-174) — change_type is
`bugfix` by the issue's own framing. `test_matrix.bugfix`: `always: [unit]`; `when:
{__bug_class__, match_bug_class}` — does not fire, no `bug_class` field anywhere (consistent with
every prior feature's gate in this repo).

**Floor: `unit`, required, always.** The diff touches exactly two files:
`plan-merge.py` and `test-plan-merge.py`. `test-plan-merge.py` matches `unit`'s `detect` glob
(`.claude/skills/harness/bin/test-*.py`) — but glob match is not the same as running. Checked
`run-unit-tests.sh`'s explicit script arrays directly: `test-plan-merge.py` is a member of
**`INTEGRATION_SCRIPTS` only** (line 31), never `UNIT_SCRIPTS` (line 30) — by design, per the
suite's own stated principle (`test_kinds.functional.excluded_because`): in-process vs.
forking-subprocess is the unit/integration split, and `test-plan-merge.py` is explicitly
subprocess-driven throughout, including a documented refusal to monkeypatch
(`test-plan-merge.py:847-848`, "FORCED THROUGH THE FRONT DOOR, NOT BY PATCHING THE MODULE").
Confirmed by running `--kind unit` directly and grepping for any `plan-merge` mention: **zero
hits**.

So: **nothing in this diff is exercised by the `unit` kind.** `unit` is `bugfix.always`,
required, and unsatisfied — **state: missing**. Not a matrix design flaw I can wave past under
"qa may add, never drop below" — the floor itself is unmet. `integration` (present, satisfied)
is not a substitute for a required kind; it is the natural home for this file, which is itself
the finding: `bugfix.always: [unit]` cannot be met by any change confined to a CLI script this
project's own convention tests only via subprocess.

```
kinds:
  - { kind: unit, state: missing, cmd: ".../run-unit-tests.sh --kind unit", named_tests: 0 }
  - { kind: integration, state: satisfied (not required by matrix), cmd: ".../run-unit-tests.sh --kind integration", named_tests: 1 }
```

## Adequacy — code paths vs. the ten cases

`cmd_amend` / `transform`, `plan-merge.py:1006-1093`:

| path | case | state |
|---|---|---|
| `--key` not in `AMENDABLE_KEYS` → exit 2 | `case_amend_refuses_an_unknown_key` | **weak, see item 4 below** |
| `_item_range` returns id absent → exit 3, lists present ids, scoped to `--key` | `case_amend_refuses_absent_id_and_lists_what_is_there` | bound |
| `_field_block` returns `None` (field absent) → exit 4 | `case_amend_refuses_absent_field` | bound |
| `--show` path | `case_amend_show_reports_block_and_hash` | bound |
| missing `--expect-sha256`/`--value-file` → exit 2 | `case_amend_requires_the_hash` | bound |
| **pre-lock** hash mismatch → exit 6 | `case_amend_refuses_a_stale_hash` | bound (pre-lock only, see item 1) |
| **under-lock** hash re-check → exit 6 (distinct code path, `plan-merge.py:1066-1068`) | none | **UNBOUND — confirmed by mutation** |
| `transform`: id vanished under lock → exit 3 | none | not exercised (no concurrency case for `amend` at all — `case_concurrency_real` covers `apply` only) |
| `transform`: field vanished under lock → exit 4 | none | not exercised, same reason |
| spliced doc fails `yaml.safe_load` → exit 8 (unparseable) | none | **UNBOUND — confirmed by mutation** |
| do-no-harm: skip schema enforcement when BASE already fails schema | none | **UNBOUND — confirmed by mutation** |
| reloaded doc fails `_schema_error` when base was legal → exit 8 (illegal schema) | none | **UNBOUND — confirmed by mutation, same probe as do-no-harm (both removed together)** |
| successful splice, single-line field | `case_amend_preserves_comments_elsewhere` | bound |
| successful splice, multi-line field | `case_amend_replaces_a_multiline_decision_field` | bound |
| value round-trips through YAML (colon/dash/hash) | `case_amend_value_round_trips_through_yaml` | bound, content-asserted (not substring) |
| value that is a YAML boolean word | `case_amend_value_yes_stays_a_string` | bound, content-asserted |
| a `verify: \|` literal field whose emitted FORM changes | none | not characterized by any case (see item 3 note below — real, but not a defect on its own) |

**Coverage gaps, named:** the under-lock re-check, both exit-8 branches, and the do-no-harm
branch are unexercised by anything in `test-plan-merge.py`. Mutation-proven (below), not inferred
from reading.

## Mutation proofs — worktree `.claude/worktrees/bug1128-qa-mutate` (`fe5c5b57`), each restored via `git checkout --`, confirmed clean via `git status --porcelain` after every step

1. **Positive control**, `AMENDABLE_KEYS` gate disabled (`if False:`): suite still exit 0, 0 FAIL
   — see item 4, this one does NOT redden either, for a structural reason, not because the guard
   is dead code in general.
2. **Under-lock hash re-check** (`plan-merge.py:1066`) replaced with `if False:`: **exit 0, 0
   FAIL.** The check the author's own commit message calls "the check that is actually
   load-bearing" has zero test coverage. A regression here (e.g. reverting to
   pre-lock-only trust, exactly the dead end the handoff says it rejected) would ship green.
3. **Exit-8 unparseable branch** (`plan-merge.py:1070-1074`) bypassed (`except` swallows and
   sets `reloaded = {}`): **exit 0, 0 FAIL.**
4. **Do-no-harm + illegal-schema branch** (`plan-merge.py:1078-1082`) replaced with `pass`:
   **exit 0, 0 FAIL.**

None of 2–4 is reachable by any case in the diff. All three are dead as far as this suite proves.

## Item 4 — `--key approval`, re-examined by mutation, not by reading

`case_amend_refuses_an_unknown_key` asserts only `returncode != 0` and the plan unchanged. With
`AMENDABLE_KEYS` disabled entirely (mutation 1 above), the suite **still passes** — because the
fixture plan carries no `approval:` top-level mapping with `- id:` items at all, so `_item_range`
returns "not found" (exit 3) regardless of whether the `--key` allowlist exists. The test is not
discriminating the allowlist; it is coincidentally passing via a different refusal.

Checked whether `approval:` is reachable for a REAL reason instead: `cmd_sign_approval`'s own
writer (`plan-merge.py:888`) shows `approval:` is authored as a **flat mapping**
(`status:`/`approved_by:`/`date:`), never a `- id:` list. `_item_range`'s `ITEM_ID_RE` only
matches `^(\s*)-\s+id:\s*(\S+)\s*$` lines. So `approval:` is structurally unreachable via this
code path independent of the `AMENDABLE_KEYS` check — there is no `- id:` line under it to match,
in any real plan. **Not a live defect: `approval:` cannot be amended, by document shape, with or
without the guard.** But the case that claims to prove this proves something else instead — name
it as a coverage gap: nothing in the suite exercises `AMENDABLE_KEYS` against a plan that actually
HAS an `- id:`-shaped item under a disallowed key.

## Item 3 — field-block mis-binding: REAL, REPRODUCED LIVE, not a hypothesis

Built a fixture task whose `intent: |` body contains a line shaped like a sibling key
(`      verify: this is NOT the real verify field...`) followed by the item's real `verify: |`
field. `_field_block` scans from the item's start for the FIRST line matching
`^(\s*)(field):` at deeper-than-item indent — it does not know it is inside a preceding field's
literal-block body, because `SIBLING_KEY_RE` is a plain regex over physical lines, blind to YAML
block-scalar context.

```
$ plan-merge.py amend --field verify --show
      verify: this is NOT the real verify field, it is prose inside intent's body
      continue after.
sha256: 74df276e...
```

Ran it through to a full **replace**: reported `AMENDED tasks:T-23.verify`, exit 0 — but the
resulting document shows the splice landed **inside `intent:`'s body**, silently corrupting it,
while the REAL `verify:` field was **never touched**. The tool claims success and names the field
it claims to have amended; it amended a different one. This is silent data corruption disguised
as a successful, auditable write — the exact failure mode the compare-and-swap hash exists to
prevent, except the hash correctly matched the (wrong) block it hashed, so the CAS gives no
protection against mis-*location*, only against mis-*content*.

**Not a live incident on FEAT-46's actual plan.yaml today** — checked T-23's real `intent:` body
directly (`.claude/worktrees/harness/FEAT-46-decision-standard/.../plan.yaml:1129-1183`): no line
in it starts with `verify:` at any indent, so `--field verify` correctly finds the real field
there (confirmed below). But the mechanism is general and the fixture shape (a literal-block
`intent:` whose prose contains a colon-terminated word at line start) is unremarkable — plan
authors write imperative prose routinely, and nothing in the schema or the tool refuses a body
line that happens to start `word:`. This is a HIGH-severity, mutation-proof-independent, directly
reproduced defect: `_field_block` needs to bound scan to the ACTUAL first-level fields of the
item (e.g. stop scanning once inside a block scalar already opened, or require the matched key's
indent to equal a specific first-seen field indent rather than any deeper indent), not "first
textual match at any deeper indent."

## Item 6 — the decisive experiment, run against the real file

Copied `FEAT-46-decision-standard/plan.yaml` (2490 lines) to `/tmp/feat46_real/` under a legal
`.harness/harness/features/FEAT-46-decision-standard/` path (never touched the tracked worktree).
`--show` reproduced the author's own claims exactly: `D-14.because` sha
`48219d6c...`, `T-23.verify` full multi-line body with zero false sibling-key matches (consistent
with the item-3 finding above — this specific file happens not to trigger it).

Ran a REAL replace: `amend --key decisions --id D-14 --field because --expect-sha256 <shown>
--value-file <new prose>`. **Exit 0.** Reloaded document parses; `D-14.because` reads back exactly
the new text; `diff` against the pre-amend copy shows **exactly one hunk**, the targeted field,
nothing else moved. First real, end-to-end replace against FEAT-46's actual content — the author's
own evidence stopped at `--show`. **The verb works for its motivating case.**

One side effect worth naming, not gating: the FORM changed from a bare plain scalar to a
single-quoted folded scalar with blank lines between logical lines (`_field_lines` routes
everything through `yaml.safe_dump`, which folds multi-line values this way — see item 3
docstring's own account of why a hand-rolled quoting rule was rejected). Checked whether anything
depends on the pre-amend form: `check-plan-routes.py`'s `BUDGETED_FIELDS` line-count gate
(`DEC-182`, 30 lines/task) counts `len(value.splitlines())` on the **parsed** string, not on raw
file text, so the extra blank lines the folded style inserts do **not** inflate the budget.
Nothing else in this repo reads `plan.yaml` by raw regex per DEC-182 (`check-state.sh`'s old
regex readers were removed by that decision). **Cosmetic only — a human diffing the PR will see a
noisier hunk than the logical change warrants, but no gate is fooled.** No case in the suite
asserts anything about emitted form either way — a real but non-blocking adequacy gap.

## Items 2, 5, 7 — checked, no findings

- **Item 2 (one renderer):** confirmed at source — `_render_field` is the only call site
  constructing replacement text and it delegates entirely to `_field_lines`
  (`yaml.safe_dump`-backed); no second quoting path exists anywhere in the +206-line diff. The two
  guard cases assert via `yaml.safe_load` round-trip against the parsed document (`got == hostile`,
  `got == "yes" and isinstance(str)`), not substring — genuinely discriminating.
- **Item 5 (registration):** `VERBS`' own header comment (`plan-merge.py:1101-1104`) states the
  rule `_register_amend` invokes: an optional-argument verb "gets its own registration — do not
  add a `required` column." `amend` has three optional args (`--show`, `--expect-sha256`,
  `--value-file`). Correct application of the table's own stated instruction.
- **Item 7 (nothing half-applied):** `git show fe5c5b57 --stat` confirms exactly two files
  changed, `plan-merge.py` and `test-plan-merge.py`. Nothing under
  `FEAT-46-decision-standard/` is touched by this commit or by `2b5b3536`/`abe59b3f` (the two
  records-only commits after the pin).

## Open questions for the panel/lead

1. Item 3's mis-binding is the highest-severity finding — recommend it block ship until
   `_field_block` is bounded correctly (e.g., require the matched sibling to be the first field
   line seen with indent exactly equal to the FIRST field's own indent — the current "any deeper
   indent" test is what lets a nested body line qualify).
2. The `unit` matrix floor being structurally unsatisfiable for a change confined to
   `plan-merge.py` (a CLI script this project only tests via subprocess) recurs for every future
   bugfix to this file — worth a `_matrix_provenance` entry carving `plan-merge.py`-only bugfixes
   toward `integration` instead of `unit`, rather than re-litigating this every cycle.
