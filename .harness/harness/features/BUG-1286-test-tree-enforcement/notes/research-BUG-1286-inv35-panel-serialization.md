# INV-35 on plan.yaml was a serialization false positive — cleared, value untouched

**BLUF.** `PF-d33300cef5eb898cfa0a971c791c8107`'s `summary` is now a **literal block scalar (`|-`)
on one physical body line**. Its decoded value is byte-identical (sha256
`2d1be049b94bc7d78a666697c1cddbdaae2f8d73b947a97d6d362ccb6afd0faf` before and after). INV-35 no
longer fires for this plan. The plan is otherwise unchanged and remains unsigned.

## Why it fired, and why the block form is the fix

`check-state.sh` INV-35 (`.claude/skills/harness/bin/check-state.sh:192-199`) documents its one
known gap: the scanner tracks block scalars and skips their bodies, but does **not** track a
multi-line **flow-quoted** scalar, on the stated premise that this corpus uses block scalars
exclusively for multi-line prose. `plan-merge.py set-panel` (`plan-merge.py:1048`) dumps the panel
with `yaml.safe_dump(..., width=80)`; the summary contains ` #` so PyYAML chose single-quoted style
and wrapped it so that plan.yaml:196 began `issue #1286 ...`. `_line_value` read that continuation
as a plain scalar and `_unquoted_hash_digit` hit ` #1`. The data always parsed correctly.

**Form chosen: literal block `|-`, not a single-line quoted scalar.** The value contains no
newlines and no trailing whitespace, so `|-` round-trips it exactly, PyYAML never wraps a block
scalar body, and `summary: |-` is precisely the shape `_BLOCK_SCALAR_VALUE` skips. The single-line
quoted fallback was unnecessary.

**Sibling `PF-ae6d643363371bf038d536934837962a` was NOT touched** — confirmed: its `#1286` sits on
the scalar's first physical line, which opens with `'`, so `_unquoted_hash_digit` returns None. A
scan of the whole `panel:` mapping (lines 113-233) found no other space-`#`-digit line start.

## Route

Written through `plan-merge.py set-panel` — its lock, its splice, its reload-equality check. The
verb has no style control, so a throwaway driver (`/tmp/inv35_fix.py`, outside the tree) registered
a `SafeRepresenter` override for that one string value before calling `main()`. No harness file was
modified.

## The five checks

1. `yaml.safe_load` summary sha256 before == after == `2d1be049b9…` — **equal True**.
2. `check-state.sh` — **0 lines** matching `INV-35` (was 1, naming plan.yaml:196).
3. `approval: {status: pending}`, no `rulings` key; top-level `status: plan`.
4. Panel: **9 findings**, same 9 ids, `{med:1, low:3, info:5}`, `disposition: open` on all 9.
5. `check-plan-routes.py` — `0 violation(s) across 1 plan(s)`, exit 0; all 5 tasks carry 11 keys.

## The diff

**`git diff` has no baseline here** — the whole feature directory is untracked (`?? .harness/harness/features/BUG-1286-test-tree-enforcement/`), so the diff is against a reconstruction of the pre-change bytes: the same file with `panel:` re-emitted by the *unpatched* dumper (`/tmp/inv35_reconstruct.py`). Its removed lines reproduce the pre-change file's lines 195-197 verbatim.

**1 hunk, 3 lines out, 2 lines in, touching exactly one key**: `panel.findings[PF-d333…].summary`.
No other key, decision, task, requirement or criterion differs.

## Open question — for the harness owner, not for this feature

`plan-merge.py set-panel` can emit a shape `check-state.sh` INV-35 misreads: the emitter and the
invariant disagree. The gap is documented in the scanner as unreached; `set-panel` reaches it
whenever a panel scalar containing ` #<digit>` wraps so the hash lands after a line break. **The fix
applied here is not stable** — any later `set-panel` run re-emits the flow form and INV-35 fires
again. Fixing that means changing the emitter or the scanner, both out of scope here and deliberately
not worked around anywhere in this plan.
