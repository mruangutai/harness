# Receipt — harness-backend-dev — SIMPLIFY apply (S-01) — run c1

**BLUF: applied.** The single authorised fold-in (`type_for_nature` → delegates to `_resolve`) is
in place, byte-for-byte behaviour-preserving as pre-verified before editing. 8 of 9 required runs
are exit 0 / FAIL 0. The 9th (the unit driver) surfaces 2 pre-existing `^FAIL ` lines that are
proven, by reading the failing test's own source, to be independent of this edit and of the
working tree entirely — no revert is warranted or possible to fix them.

## Pre-edit verification (required before editing)

Read `type_for_nature` (lines 66-76) and `_resolve` (lines 49-59) side by side at commit
`7dc0ee92`, pre-edit:
1. Membership test — both `name not in table` (`nature not in DEFAULT_TYPE_BY_NATURE` vs
   `name not in table`, with `table = DEFAULT_TYPE_BY_NATURE` at the call site). Identical.
2. Exception type — both raise `UnknownWorkNature`. Identical.
3. Message — both f-strings read `f"{X!r} is not a known change_type, so no issue type is mapped
   for it - add it to DEFAULT_TYPE_BY_CHANGE_TYPE or fix the plan"`. Byte-identical wording in both
   functions, including the (arguably wrong) "change_type"/"DEFAULT_TYPE_BY_CHANGE_TYPE" nouns even
   inside `type_for_nature`. Confirms the "message becomes more correct" claim from one angle
   reader is **wrong** — delegating changes nothing about the message. Did not touch the message.
4. Override lookup — both `overrides.get(default)`, accepted only if `isinstance(override, str)
   and override`. Identical.

All four steps agreed with the lead's claim. Proceeded to edit.

## Diff (verbatim, full and only hunk)

```diff
diff --git a/.claude/skills/harness/bin/gh_issue_types.py b/.claude/skills/harness/bin/gh_issue_types.py
index 9ab6a026..7f750a92 100644
--- a/.claude/skills/harness/bin/gh_issue_types.py
+++ b/.claude/skills/harness/bin/gh_issue_types.py
@@ -64,16 +64,7 @@ def type_for_change_type(change_type, overrides):
 
 
 def type_for_nature(nature, overrides):
-    if nature not in DEFAULT_TYPE_BY_NATURE:
-        raise UnknownWorkNature(
-            f"{nature!r} is not a known change_type, so no issue type is mapped for it - "
-            "add it to DEFAULT_TYPE_BY_CHANGE_TYPE or fix the plan"
-        )
-    default = DEFAULT_TYPE_BY_NATURE[nature]
-    override = overrides.get(default)
-    if isinstance(override, str) and override:
-        return override
-    return default
+    return _resolve(nature, DEFAULT_TYPE_BY_NATURE, overrides)
 
 
 def type_for_parent(overrides):
```

No other hunk. `_resolve`, `type_for_change_type`, `type_for_parent`, the tables, and the
docstring are all untouched.

## Nine-run result table

| # | Suite | RC | `^FAIL ` count |
|---|---|---|---|
| 1 | tests/integration/test-gh-issue-types.py | 0 | 0 |
| 2 | tests/integration/test-gh-sync.py | 0 | 0 |
| 3 | tests/integration/test-gh-backlog-issue-types.py | 0 | 0 |
| 4 | tests/integration/test-factory-issue-types.py | 0 | 0 |
| 5 | tests/integration/test-factory-decompose.py | 0 | 0 |
| 6 | tests/unit/test-factory-gh.py | 0 | 0 |
| 7 | tests/integration/test-factory-integration.py | 0 | 0 |
| 8 | tests/unit/test-issue-types.py | 0 | 0 |
| 9 | `.claude/skills/harness/bin/run-unit-tests.sh` (absolute path under this worktree) | 1 | 2 |

All nine commands were run with `env -u HARNESS_AGENT_TYPE`, `rc=$?` captured immediately after
each run, and `^FAIL ` counted with `grep -c '^FAIL '` against that run's own captured output (not
the driver's own tail line).

## Row 9 in detail — proven pre-existing, unrelated to this apply

The 2 `^FAIL ` lines both come from one sub-script, `tests/integration/test-anchor-directions.py`
(exit 1, run inside the driver's pool):

```
FAIL - reviewed-sha whole scope
VIOLATION .claude/skills/harness/references/github-mirror.md:19: unanchored instruction path: .claude/skills/harness/bin/gh_issue_types.py
VIOLATION .claude/skills/harness/references/github-mirror.md:24: unanchored instruction path: .harness/harness.json
scanned 62 file(s), 2 violation(s)
FAIL test-anchor-directions.py
```

Read the test's source (`tests/integration/test-anchor-directions.py`): `REF =
os.environ.get("HARNESS_REVIEW_SHA") or "HEAD"` (unset in this run, so `REF = HEAD` =
`7dc0ee92`), and every path it scans is fetched with `git show <REF>:<path>` (see `show()` and
`_whole_scope_ok()`) — **committed content, never the working tree.** I confirmed the violation is
already present in the committed blob:

```
$ git show HEAD:.claude/skills/harness/references/github-mirror.md | sed -n '19p;24p' (paraphrased above)
```

shows the same two unanchored mentions of `.claude/skills/harness/bin/gh_issue_types.py` and
`.harness/harness.json` already committed at `7dc0ee92`, in prose inside `github-mirror.md` — a
file this dispatch explicitly forbids me from touching (NOBODY-owned, concurrently being edited by
the main session; it shows ` M` in `git status --porcelain` right now, consistent with the main
session actively fixing exactly this anchoring gap).

Because the check reads `git show HEAD:...` and not the working tree, this failure is:
- **Invariant to my edit** — my working-tree change to `gh_issue_types.py`'s body is never read by
  this check; the check only reads the byte string `.claude/skills/harness/bin/gh_issue_types.py`
  as it appears inside `github-mirror.md`'s committed prose.
- **Invariant to a revert** — `git checkout -- .claude/skills/harness/bin/gh_issue_types.py` would
  not change `HEAD`'s content of `github-mirror.md` and would not restore green.
- **Out of my repair authority** — the only file that could clear it (`github-mirror.md`) is
  explicitly off-limits to me this run.

No repair attempt was applicable (nothing in my one authorised file could fix a check that reads a
different, off-limits file at a fixed commit), and no revert was performed because reverting would
not have changed the outcome and would have discarded a verified-correct, in-scope fix for an
unrelated, pre-existing, already-being-fixed-by-someone-else defect.

## `git status --porcelain` (final, verbatim)

```
 M .claude/skills/harness/bin/gh_issue_types.py
 M .claude/skills/harness/references/github-mirror.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/qa-2026-09-05-01-validator.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-backend-dev-simplify-efficiency-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-data-engineer-simplify-altitude-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-dev-ops-simplify-simplification-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-data-engineer.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
```

Only ` M .claude/skills/harness/bin/gh_issue_types.py` is mine. Everything else is other agents'
and the main session's concurrent activity, left untouched as instructed.
