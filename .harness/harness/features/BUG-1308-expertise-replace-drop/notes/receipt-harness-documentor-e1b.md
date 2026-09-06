# Receipt — harness-documentor — BUG-1308 · E1b · SPEC §5.3 citation realignment

**All ten citations realigned; my independent measurement agreed with the lead on every range,
including the two where engineering's hand-off was wrong (`:242-250`, `:289-300`). `:157-167` was
checked and left unchanged. No prose correction was needed — the exit-12 description is still true
of the shipped mechanism, and §5.3 nowhere claims `section` is line-checked.**

One file edited: `.harness/harness/docs/SPEC.md`, §5.3 only — 8 physical lines, 10 citations.

## Citation table — measured against `expertise-merge.py` at HEAD `8a0121b`

| # | Site | Old | Measured (= written) | Matched lead? | Covers — first / last line |
|---|---|---|---|---|---|
| 1 | exit-12 row, cite 1 | `:153-225` | `:153-234` | yes | Step-A shape chain, `_malformed`..`_parse_op`: 153 `def _malformed(index, message):` / 234 `    return verb, op["target"], section, op.get("entry")` |
| 2 | exit-12 row, cite 2 | `:378-381` | `:387-390` | yes | `resolve_ops` payload-not-a-list: 387 `    if not isinstance(ops, list):` / 390 `        )` |
| 3 | exit-10 row | `:244-253` | `:253-262` | yes | `_resolve_replace_or_drop`: 253 `def _resolve_replace_or_drop(base_sections, section, target):` / 262 `    _check_base_ambiguity(matches, section, target)` |
| 4 | exit-11 row, cite 1 | `:233-241` | `:242-250` | yes (eng said `:242-251`) | `_check_base_ambiguity`: 242 `def _check_base_ambiguity(matches, section, target):` / 250 `        )`. 251 is blank; 250 is the last statement line |
| 5 | exit-11 row, cite 2 | `:280-291` | `:289-300` | yes (eng said `:289-301`) | `_check_proposal_ambiguity`: 289 `def _check_proposal_ambiguity(resolved):` / 300 `        seen.add(key)`. 301 is blank |
| 6 | prose | `:182-194` | `:191-203` | yes | `_validate_target_section`: 191 `def _validate_target_section(op, index):` / 203 `    return section` |
| 7 | prose | `:309-323` | `:318-332` | yes | `_rebuild_section`: 318 `def _rebuild_section(base_entries, section_ops, adds):` / 332 `    return rebuilt` |
| 8 | prose | `:294-306` | `:303-315` | yes | `_resolve_all`: 303 `def _resolve_all(base_sections, parsed_ops):` / 315 `    return resolved` |
| 9 | prose | `:350-357` | `:359-366` | yes | `_check_caps`: 359 `def _check_caps(merged):` / 366 `            )` |
| 10 | prose | `expertise-merge.py:524-573` | `:533-582` | yes | `cmd_ops`: 533 `def cmd_ops(args):` / 582 `    sys.exit(0)` |

**B — `_validate_verb` `:157-167` checked and left unchanged.** 157 `def _validate_verb(op, index):`
.. 167 `    return verb`. It sits above the cycle-2 insertion at :179 and is still exact
(SPEC.md:961-962).

## D — prose accuracy: no change made

**Exit-12 row, "...or gives an `entry` or `target` that is not a single-line string" — still true.**
My reasoning, not engineering's: the sentence asserts a *property of the value* (not a single-line
string), never a character set. The fix widened the mechanism from `\n`/`\r` to
`len(value.splitlines()) > 1` (`expertise-merge.py:187-188`), which strictly enlarges the refused
set. A wider refusal cannot falsify a claim of the form "X is refused"; it makes the sentence more
exactly right, because "a single line" now means what the parser means by it. The row also still
covers the non-string case (`:209`, `:196`). Verified by execution, not by reading: driving
`resolve_ops` directly, every one of `\n \r \v \f \x1c \x1d \x1e \x85 U+2028 U+2029` inside `entry`
returns exit 12 `entry must be a single line`; `target` with U+2028 returns the same for `target`;
`entry: 123` returns `entry must be a string, not int`; a plain single-line op is accepted.

**`section` is not line-checked, and §5.3 never says it is.** `_reject_multiline` is applied to
`target` (`:197`) and `entry` (`:211`) only; `section` is validated by closed-enum membership against
`CAPS` (`:201-202`). Executed: `section: "Patterns\u2028"` is refused exit 12 with the *enum*
message, not the single-line one. §5.3's only statements about `section` are the keying sentence
(SPEC.md:946-948) and the exit-12 row, neither of which claims a line check — so there is nothing
false to correct. §5.3 is **silent** on the enum refusal; per dispatch that is reported as advisory
and no clause was added. **Prose correction: none needed.**

## Git state — uncommitted, HEAD unmoved

- `git rev-parse HEAD` before: `8a0121b0b9799a42298040bb5b7731f26ae98b99`
- `git rev-parse HEAD` after: `8a0121b0b9799a42298040bb5b7731f26ae98b99` (equal)
- `git status --porcelain` after the edit: ` M .harness/harness/docs/SPEC.md` — plus this receipt and
  my observations log as untracked additions under `features/BUG-1308-expertise-replace-drop/`.
  Nothing committed; `git diff --stat` = 8 insertions, 8 deletions in one file.

## Advisory — citations I did NOT touch (dispatch §C), and a correction to §C itself

Dispatch §C states the `apply` paragraph's cites resolve into `harness_merge.py`. **They do not.**
Measured at HEAD: `compute_union` is `expertise-merge.py:114` (SPEC cites `:111-137`), `cmd_apply` is
`expertise-merge.py:451` (SPEC cites `:164-226`), `CAPS` is `expertise-merge.py:38` (SPEC cites
`:32`), and **no symbol named `acquire_lock` exists in either file** — `harness_merge.py` has
`acquire` (`:105`) and `locked_update` (`:121`). So §5.2/§5.3's `apply`-side citations are stale too,
by a different and older drift than the +9 shift. Reported, not edited, per dispatch. Note this means
one more realignment pass is already owed unless it is folded into the fix below.

## Backlog candidate

SPEC §5.3 pins behaviour to raw line ranges inside `expertise-merge.py`, a file this feature keeps
editing — this is the second realignment in one feature, and the `apply`-side cites above are a third
drift nobody has caught. Durable fix: cite **stable symbol names** (`_check_base_ambiguity`, no
range) and add a generated citation check — a script that resolves every `file:line` cite in
`docs/**` to the symbol the prose names and fails when they disagree, run in the same gate as
`check-expertise.sh`.
