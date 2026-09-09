# Receipt — harness-dev-ops — T-09 — register harness-add-repo in MAIN_SESSION_ONLY

## Intent/verify cross-check

Pulled T-09 verbatim from `<feature-dir>/plan.yaml` (lines 1204-1241, tag as read).
`intent:` and `verify:` byte-match the two blocks quoted in the dispatch. No mismatch.

## Change made

Edited exactly `.claude/skills/harness/bin/check-instruction-paths.py`, lines 12-18
(comment block + tuple), nothing else:

```diff
diff --git a/.claude/skills/harness/bin/check-instruction-paths.py b/.claude/skills/harness/bin/check-instruction-paths.py
index f05f88c1..a33edf30 100755
--- a/.claude/skills/harness/bin/check-instruction-paths.py
+++ b/.claude/skills/harness/bin/check-instruction-paths.py
@@ -11,8 +11,11 @@ import harness_boundary
 
 # harness-init is excluded here because of the anchor rule, not because of ownership:
 # the anchor rule would rewrite its deliberately clone-relative core.hooksPath value.
+# harness-add-repo is excluded because it runs only in the main session, and its
+# content is deliberately clone-relative, so the anchor rule would rewrite it too.
 MAIN_SESSION_ONLY = (
     "harness-init",  # anchor rule would rewrite its clone-relative core.hooksPath; runs only in the main session
+    "harness-add-repo",  # runs only in the main session
     "harness-grilling",  # main session only
     "harness-wayfinding",  # main session only
 )
```

The trailing comment on the new entry says only "runs only in the main session" —
it does not restate harness-init's core.hooksPath reason, per the dispatch's
explicit instruction not to copy that neighbour's comment. The block comment above
the tuple now states both reasons: harness-init's clone-relative core.hooksPath,
and harness-add-repo's own clone-relative content that the anchor rule would also
rewrite.

## Pre-edit verify — RED

Command (run from worktree root, `HARNESS_AGENT_TYPE` cleared):

```
env -u HARNESS_AGENT_TYPE bash -c "grep -q '\"harness-add-repo\"' .claude/skills/harness/bin/check-instruction-paths.py && python3 .claude/skills/harness/bin/check-instruction-paths.py"
```

Output: (none — `grep -q` prints nothing)
Exit status: `1`

Failed at the grep, as required: `"harness-add-repo"` was absent from the file
before the edit, so `&&` short-circuited before `check-instruction-paths.py` ran.

## Post-edit verify — GREEN

Same command, after the edit:

```
env -u HARNESS_AGENT_TYPE bash -c "grep -q '\"harness-add-repo\"' .claude/skills/harness/bin/check-instruction-paths.py && python3 .claude/skills/harness/bin/check-instruction-paths.py"
```

Full output:
```
scanned 62 file(s), 0 violation(s)
```
Exit status: `0`

File count is 62, unchanged from the pre-edit description of the scanner's normal
run (62 files) — matches expectation since `.claude/skills/harness-add-repo/`
does not exist yet, so `_skill_docs`'s `os.listdir`-driven scan list is unaffected
by the new tuple entry (it is currently inert, as intended by T-09's ordering).

## Syntax check

```
env -u HARNESS_AGENT_TYPE python3 -c 'import ast;ast.parse(open(".claude/skills/harness/bin/check-instruction-paths.py").read())'
```
Exit status: `0` (no output).

## Diff scope

```
git diff --stat -- .claude/skills/harness/bin/check-instruction-paths.py
```
```
 .claude/skills/harness/bin/check-instruction-paths.py | 3 +++
 1 file changed, 3 insertions(+)
```

Full diff pasted above under "Change made" — confined to the block comment and the
tuple, exactly the scope the intent names.

## git status --porcelain (full, unfiltered)

```
 M .claude/skills/harness/bin/check-instruction-paths.py
 M .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-t09-eng.md
```

The two modified feature-tree files (`feature.json`, `plan.yaml`) were already
dirty before this dispatch's edit (pre-edit `git status --porcelain` run before
any change showed the identical two lines) — not touched by me. This dispatch's
own production edit is the single `check-instruction-paths.py` line-group; the
receipt file is my own new note. No `runs/` entry was attempted or needed for
this task (no run-dir bookkeeping instruction was given beyond the receipt).

## Prefix-predicate check

`_skill_docs`'s comprehension filters on `name.startswith("harness-")`. Measured
in this worktree at the pre-edit read (tag `59EB`): **line 31**, matching the
intent's own citation that it is line 31 at `12f74ea8` (not the dispatch-relay's
line 29). Exact text measured:

```
30:        candidate for name in os.listdir(base)
31:        if name.startswith("harness-") and name not in MAIN_SESSION_ONLY
```

`harness-add-repo` starts with `"harness-"`, so it is inside the globbed
directory-listing set that this predicate selects; the `MAIN_SESSION_ONLY` tuple
entry is what removes it from `_skill_docs`'s returned candidates. Confirmed by
the post-edit run above still scanning 62 files (the entry is a no-op today
because the directory does not exist, per T-09's stated ordering rationale).

## Skill directory existence check

```
test -d .claude/skills/harness-add-repo && echo EXISTS-BAD || echo ABSENT-OK
```
Output: `ABSENT-OK` — confirms the new tuple entry is currently inert, as T-09
requires. Creating this directory is T-10's job, not touched here.

## Non-goals confirmed untouched

`TOKEN`, `FEATURE_RE`, `FENCE`, `_skill_docs`'s body, `_markdown_under`, `scope`,
every other `MAIN_SESSION_ONLY` entry (`harness-init`'s comment left verbatim,
`harness-grilling`/`harness-wayfinding` untouched), and every other file in the
tree — confirmed by the diff above touching only lines 12-18 of one file.
