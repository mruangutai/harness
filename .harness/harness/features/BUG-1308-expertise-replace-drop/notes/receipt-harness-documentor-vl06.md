# Receipt — harness-documentor — BUG-1308 · SPEC §5.3 target-grammar gate

**SPEC §5.3 now documents the VL-06 grammar gate, and all six ops-side citations the `a737eb9d`
insertion displaced are re-measured and corrected.** 8 lines changed in one file. Two
engineering-relayed values were wrong; two were right. No commit, HEAD unmoved at `a737eb9d`.

## Why every ops-side citation moved, exactly

`a737eb9d` is two hunks in `expertise-merge.py`, not one: `@@ -190,0 +191,15 @@` (the new
`_validate_target_grammar`) **and** `@@ -197,0 +213 @@` (its call site inside
`_validate_target_section`). So the shift below line 191 is **+16**, not the +15 the insertion size
suggests — which is why every relayed number derived from "15 lines" was off. `_validate_target_section`
is the one symbol split across both hunks: its `def` moved +15 (191→206), its tail +16 (203→219).

## Edits — measured ranges, first and last source line verbatim

| SPEC line | Old citation | New | Symbol now covered | First line | Last line |
|---|---|---|---|---|---|
| 942 | `cmd_ops`, `:533-582` | `:549-598` | `cmd_ops` | `def cmd_ops(args):` | `    sys.exit(0)` |
| 948 | `_validate_target_section`, `:191-203` | `:206-219` | `_validate_target_section` | `def _validate_target_section(op, index):` | `    return section` |
| 952 | `_rebuild_section`, `:318-332` | `:334-348` | `_rebuild_section` | `def _rebuild_section(base_entries, section_ops, adds):` | `    return rebuilt` |
| 956 | `_resolve_all`, `:303-315` | `:319-331` | `_resolve_all` | `def _resolve_all(base_sections, parsed_ops):` | `    return resolved` |
| 957 | `_check_caps`, `:359-366` | `:375-382` | `_check_caps` | `def _check_caps(merged):` | `            )` |
| 966 | `:253-262` | `:269-278` | `_resolve_replace_or_drop` (raises 10) | `def _resolve_replace_or_drop(base_sections, section, target):` | `    _check_base_ambiguity(matches, section, target)` |
| 967 | `:242-250` plus `:289-300` | `:258-266` plus `:305-316` | `_check_base_ambiguity`; `_check_proposal_ambiguity` | `def _check_base_ambiguity(matches, section, target):` / `def _check_proposal_ambiguity(resolved):` | `        )` / `        seen.add(key)` |
| 968 | condition cell, no grammar clause | condition cell gains the grammar clause citing `_validate_target_grammar`, `:191-203` | `_validate_target_grammar` | `def _validate_target_grammar(target, index):` | `        _malformed(index, f"target {target!r} does not match the entry id grammar")` |
| 968 | report cell `:153-234` | `:153-250` | Step A shape-gate block, `_malformed` → `_parse_op` | `def _malformed(index, message):` | `    return verb, op["target"], section, op.get("entry")` |
| 968 | report cell `:387-390` | `:403-406` | `resolve_ops`' payload-is-a-list check | `    if not isinstance(ops, list):` | `        )` |

Two of row 968's report citations are **not** single-symbol ranges and never were: `:153-250` spans
`_malformed` through `_parse_op` (start unmoved, end = `_parse_op`'s last code line, old 234 +16), and
`:403-406` is a four-line statement inside `resolve_ops`. Both endpoints map onto determinate
constructs at exactly +16, so these are re-measurements, not guesses. **Unresolved citations: none.**

## Engineering-relayed values, judged

| Relayed | Verdict |
|---|---|
| `SPEC.md:968` = the `12 MALFORMED OPS` row | **correct** |
| `SPEC.md:948` = the `_validate_target_section` citation | **correct** |
| `_validate_target_grammar` at `:191-203` | **correct** (last code line 203) |
| `_validate_target_section` at `:206-220` | **WRONG, one line too long** — 220 is blank; last code line is 219, `    return section` |

Engineering also flagged only *one* displaced citation. **Five more were displaced** (942, 952, 956,
957, 966, 967) — all found by the end-to-end sweep, none by the relay.

## Prose verdict — accurate post-fix, with one advisory

**The grammar gate applies to all three verbs, so the un-verb-scoped condition cell I wrote is right.**
Traced, not taken from the digest: `resolve_ops:407` calls `_parse_op` for every op; `_parse_op:248`
calls `_validate_target_section` unconditionally, before any verb branch; `_validate_target_section:213`
calls `_validate_target_grammar` unconditionally. Confirmed by execution against pure `resolve_ops`
(no IO) — `add`, `replace` and `drop` each returned `exit 12 MALFORMED OPS op index=0: target
'PPPP-1' does not match the entry id grammar`, and the containment vector `"P-01: fake"` was refused
identically. §5.3 nowhere scopes the gate to `add`; no correction was needed there.

The rest of §5.3's ops-side prose is true of the shipped code: verbs (`_OP_KEYS:146-150`), replace-in-place
(`_rebuild_section`), one-base-snapshot ordering (`_resolve_all`), caps once on the merged state
(`_check_caps`), `merge` refused with the rewrite instruction (`_validate_verb`), and the four success
verbs (`_build_outcomes`). `_validate_verb`'s `:157-167` was already correct — it sits above the
insertion point. **No further edit was warranted, and none was manufactured.**

*Advisory, not edited (pre-existing, not displaced by this cycle):* row 966 reads as though exit 10
covers every verb; `_resolve_add:290` returns `False` for a missing target rather than refusing, so 10
is replace/drop only.

## Boundary held

**Apply-side citation drift left untouched, by name:** `compute_union` (`:111-137`), the atomic write
(`:219-226`), `cmd_apply` (`:164-226`), `CAPS` (`:32`), the `CONFLICT` (`:186-192`) and `CAP EXCEEDED`
(`:194-200`) cells, the dead `acquire_lock` (`:140-153`), and `test-expertise-merge.py:70-250`. All
sit at SPEC lines 914-930; the diff's hunk headers (`942`, `948`, `952`, `956,2`, `966,3`) prove none
was touched.

## Tree state

```
$ git status --porcelain     # from the worktree root
 M .harness/harness/docs/SPEC.md
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-documentor.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/receipt-harness-documentor-vl06.md
```

`SPEC.md` is the only modified product file; the other two paths are this receipt and my own
observations log (appended via `observations-merge.py`, never rewritten). **Everything is
uncommitted — I made no commit and did not move HEAD, which is still `a737eb9d`.**
