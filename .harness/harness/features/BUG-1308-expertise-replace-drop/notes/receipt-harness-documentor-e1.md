# Receipt — harness-documentor — BUG-1308 escalation E1 — SPEC §5.3 citation realignment

**Nine `ops`-path citations in §5.3 now match the post-fix file; VL-05 is closed. Four of
engineering's five handed-down ranges overshot by one blank line and were corrected. The
apply-path citations are broken but PRE-EXISTING — measured, reported, not touched.**

Only file changed: `.harness/harness/docs/SPEC.md`, lines 942–968 (all inside §5.3, 866–978).
Reference: `.claude/skills/harness/bin/expertise-merge.py` (601 lines), `harness_merge.py` (171).

## 1. Citations rewritten — measured, first/last line verbatim

| § line | Symbol / branch | OLD | NEW | first line of new range | last line of new range |
|---|---|---|---|---|---|
| 968 | exit **12** shape gate `_malformed`→`_parse_op` | `:153-200` | `:153-225` | `def _malformed(index, message):` | `    return verb, op["target"], section, op.get("entry")` |
| 968 | exit **12** payload-not-a-list, in `resolve_ops` | — | `:378-381` | `    if not isinstance(ops, list):` | `        )` |
| 966 | exit **10** `_resolve_replace_or_drop` | `:203-212` | `:244-253` | `def _resolve_replace_or_drop(base_sections, section, target):` | `    _check_base_ambiguity(matches, section, target)` |
| 967 | exit **11** `_check_base_ambiguity` | `:213-251` | `:233-241` | `def _check_base_ambiguity(matches, section, target):` | `        )` |
| 967 | exit **11** `_check_proposal_ambiguity` | — | `:280-291` | `def _check_proposal_ambiguity(resolved):` | `        seen.add(key)` |
| 956 | `_resolve_all` | `:254-266` | `:294-306` | `def _resolve_all(base_sections, parsed_ops):` | `    return resolved` |
| 957 | `_check_caps` | `:310-317` | `:350-357` | `def _check_caps(merged):` | `            )` |
| 948 | `_validate_target_section` | `:170-178` | `:182-194` | `def _validate_target_section(op, index):` | `    return section` |
| 952 | `_rebuild_section` | `:269-283` | `:309-323` | `def _rebuild_section(base_entries, section_ops, adds):` | `    return rebuilt` |
| 942 | `cmd_ops` | `:484-533` | `:524-573` | `def cmd_ops(args):` | `    sys.exit(0)` |

Re-measured, asserted still correct: **`_validate_verb` `:157-167` — CONFIRMED** (`def` 157,
last body line `    return verb` 167).

## 2. VL-05 closed — the exit-12 row now covers every cause it names

Row 968 names five causes; each is inside a cited range:
1. **payload is not a JSON list** — `resolve_ops`, `:378-381` (the branch the OLD `:153-200`
   excluded; this is the VL-05 finding).
2. **omits a required key** — `_validate_target_section` `:184-185`, `:190-191`;
   `_validate_entry_and_keys` `:206-207` — all inside `:153-225`.
3. **carries a forbidden key** — `_validate_entry_and_keys` `:208-209`, `:212-214`.
4. **unknown verb** — `_validate_verb` `:165-166` (and the `merge` refusal `:159-164`).
5. **`entry`/`target` not a single line** (added, see §5) — `_reject_multiline` `:170-179`,
   `_validate_entry_shape` `:197-201`.

## 3. Corrections to engineering's handoff (4 of 5 differed)

Each overshot by exactly one line, landing on the blank line after the last body line:
`:244-254`→**`:244-253`**, `:233-242`→**`:233-241`**, `:280-292`→**`:280-291`**,
`:350-358`→**`:350-357`**. Correct as handed: `:153-225`, `:378-381`, `:294-306`.

## 4. PRE-EXISTING breakage — measured, NOT rewritten (open questions)

None of these moved in cycle 1 (`git show 3488ca38 -U0` touches nothing above line 169), so they
were already wrong when the panel reviewed §5.3:

| §5.3 cite | Line | Measured truth |
|---|---|---|
| `CAPS`, `:32` | 925 | `expertise-merge.py:38` (also 38 pre-fix) |
| `cmd_apply`, `:164-226` | 920 | `expertise-merge.py:442-521` |
| CONFLICT report `:186-192` | 924 | `expertise-merge.py:471-477` |
| CAP EXCEEDED `:194-200` | 925 | `expertise-merge.py:479-485` |
| atomic write `:219-226` | 916 | **left this file** in the `harness_merge` extraction — now `harness_merge.py:142-153`, inside `locked_update` (`:121-153`) |
| `acquire_lock`, `:140-153` | 926 | **symbol does not exist** in either module. The lock is `harness_merge.acquire` (`:105-118`); the 10s budget is `LOCK_TIMEOUT_SECONDS` `harness_merge.py:36` |
| `compute_union`, `:111-137` | 914 | `expertise-merge.py:114-140`. Engineering asserted this one still correct — **REFUTED**, but off by 3 at `origin/main` too, so pre-existing, not cycle-caused |
| `test-expertise-merge.py:70-250` | 930 | path is `tests/integration/test-expertise-merge.py`; the cap-drift detector the sentence claims is covered sits at `:261` (`:259` at `origin/main`), outside the range |

## 5. Prose

- **Part 4a — no change needed, stated explicitly.** Row 967 already reads "The id appears twice
  in that section, or two ops in one proposal name the same target" — verb-agnostic, so cycle 1's
  `_resolve_add`→`_check_base_ambiguity` (`:263-264`) alignment is already covered. Empty result.
- **Part 4b — one addition, row 968.** Before: `… carries a forbidden one, or names an unknown
  verb |`. After: `… carries a forbidden one, names an unknown verb, or gives an `entry` or
  `target` that is not a single-line string |`. Justification: `_reject_multiline` (`:170-179`)
  refuses both fields at exit 12 and the row omitted it.
- No other §5.3 sentence was found factually wrong about behaviour. The exit **7** CONFLICT row
  (924) is still true of `add` as well as `apply` (`_resolve_add` `:270-277`).

## 6. Git state

`git status --porcelain`, verbatim, three lines and no others:

```
 M .harness/harness/docs/SPEC.md
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-documentor.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/receipt-harness-documentor-e1.md
```

SPEC.md is the only product file modified; the other two are my own log and this receipt. All
three are UNCOMMITTED. SPEC diff hunks: `942`, `948`, `952`, `956,2`, `966,3` — all inside §5.3.
**No commit made, nothing staged, HEAD unmoved at `3488ca38`.**
