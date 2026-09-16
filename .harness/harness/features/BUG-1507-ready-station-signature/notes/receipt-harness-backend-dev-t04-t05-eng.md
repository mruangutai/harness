# Receipt — harness-backend-dev — T-04 + T-05 — BUG-1507-ready-station-signature

## T-04 — cmd_status docstring, Building bullet

Edit: added one bullet + one decision paragraph to `cmd_status`'s docstring in
`.claude/skills/harness/bin/gh-sync.py`, immediately after the existing `Review` bullet and
before the existing `Plan, Done, Abandoned` bullet. No executable line touched. Line 1347's
early-return tuple (`if board is None or station in ("plan", "done",
factory_config.TERMINAL_MARKER):`) is byte-identical to the pre-edit text.

Command (verbatim from plan.yaml T-04 `verify:`), run from the worktree root:

```
python3 -c "import ast,re,sys; p='.claude/skills/harness/bin/gh-sync.py'; t=open(p,encoding='utf-8').read(); ast.parse(t); d=t.split('def cmd_status(')[1].split('\"\"\"')[1]; sys.exit(0 if re.search(r'^    - Building[:,] ',d,re.M) else 1)" &&
grep -qF 'if board is None or station in ("plan", "done", factory_config.TERMINAL_MARKER):' .claude/skills/harness/bin/gh-sync.py
```

Exit code: **0**

### SC-08 diff (only the docstring changed)

```diff
diff --git a/.claude/skills/harness/bin/gh-sync.py b/.claude/skills/harness/bin/gh-sync.py
index 4b80ef74..8f27bb77 100755
--- a/.claude/skills/harness/bin/gh-sync.py
+++ b/.claude/skills/harness/bin/gh-sync.py
@@ -1309,6 +1309,22 @@ def cmd_status(feat_dir, station, repo, board):
       the lowercase `"review"` (operator ruling, D-23) — one `gh_board.set_station` call
       each. A parent that is not recorded prints one stderr line and the sub-issue writes
       still proceed; this does not raise and does not restate INV-21's finding.
+    - Building: `_record_station` records plan.yaml's own station as `building`, and the
+      early-return guard just below (unchanged) does not list `building`, so control falls
+      through it; neither the ready branch nor the review branch fires, so NO CARD IS WRITTEN
+      by this subcommand for building — the parent card reaches the board's Building column
+      by derivation from the task statuses `gh-sync.py start-task` writes. Nothing calls this
+      subcommand for building today: the orchestrator records the feature's building station
+      through `plan-merge.py set-feature-station --station building` (BUG-1507's addition to
+      SKILL.md's build phase, already landed on this branch), so this path is a stated
+      contract, not a live caller.
+
+      This is intentional (D-02), not a fallthrough left unstated: recording the station and
+      writing no card is the INTENDED behaviour for building, and building is deliberately not
+      added to the tuple below, because `load_recorded` — which the fallthrough reaches — raises
+      SystemExit on an unparseable or non-mapping feature.json, so short-circuiting building past
+      it would change observable behaviour in exactly the case the tuple is meant to be neutral
+      about (BUG-1507).
     - Plan, Done, Abandoned: no station write at all (Plan is board-station.py's own write;
       Done is written by `ship` alone, which is the only writer of the done station, so a
       Done feature's cards are already there by the time this runs; Abandoned has no column
```

`git diff --stat` confirms exactly one file, 16 insertions, 0 deletions.

## T-05 — tests/integration/test-station-argument-spelling.py (new file)

Module-level helpers `scope_files(root)`, `occurrences(root)`, `offenders(root)` are pure
functions of an explicit `root`, called in-process; no subprocess self-reinvocation, no env
override, no module-level scope state, no recursion guard, no conditionally-skipped row.
Accepted station sets are derived: `set(factory_config.MANDATED_STATIONS) |
{factory_config.TERMINAL_MARKER}` for `gh-sync.py status`, `set(factory_config.MANDATED_STATIONS)`
alone for `board-station.py`.

Command (verbatim from plan.yaml T-05 `verify:`), run from the worktree root:

```
python3 tests/integration/test-station-argument-spelling.py &&
python3 tests/integration/test-station-argument-spelling.py | grep -q '^PASS - every station argument in the instruction scope is an accepted station$' &&
python3 tests/integration/test-station-argument-spelling.py | grep -q '^PASS - the sweep reddens on a reintroduced capital$'
```

Exit code: **0** (chain exits 0; a `BrokenPipeError` traceback appears on the second/third legs
because `grep -q` closes stdin early once it finds its match — that traceback is a byproduct of
`grep -q`'s early exit against a `print`-heavy producer, not a test failure, and does not affect
the `$?` of the `&&` chain, which is 0 all the way through).

Direct run output:

```
PASS - the instruction scope is non-empty
PASS - at least the measured number of station-argument occurrences are found
PASS - harness-plan.md is among the swept occurrence files
PASS - github-mirror.md is among the swept occurrence files
PASS - SKILL.md is among the swept occurrence files
PASS - every station argument in the instruction scope is an accepted station
PASS - the unmutated scratch copy reports no offender
PASS - the sweep reddens on a reintroduced capital
```

### Regression guard (SC-09)

```
python3 tests/integration/test-gh-sync.py
```
Exit code: **0** (`ALL PASSED`, plus every additional block through the trailing "all pass"
section — full run visible in the tool transcript, no FAIL lines).

```
python3 tests/integration/test-board-station.py
```
Exit code: **0** (`all pass`, no FAIL lines).

### Step 8 — one-off RED evidence (recorded, not asserted in the committed file)

Staged the pre-fix copies with `git -C <worktree> show 4b5dbb23:<path>` for
`.claude/commands/harness-plan.md` and `.claude/skills/harness/references/github-mirror.md` into
a scratch root (written via Python `open(..., "w")`, not shell redirection), imported
`test-station-argument-spelling.py` as a module in-process, and printed
`offenders(<scratch root>)`:

```
[('<scratch>/.claude/commands/harness-plan.md', 'board-station.py', 'Plan'),
 ('<scratch>/.claude/commands/harness-plan.md', 'gh-sync.py status', 'Ready'),
 ('<scratch>/.claude/skills/harness/references/github-mirror.md', 'gh-sync.py status', 'Review'),
 ('<scratch>/.claude/skills/harness/references/github-mirror.md', 'gh-sync.py status', 'Ready'),
 ('<scratch>/.claude/skills/harness/references/github-mirror.md', 'gh-sync.py status', 'Review')]
```

(`<scratch>` stands in for the mktemp path; full literal tuples as printed carried the real
`/var/folders/.../tmp.../` prefix.) This confirms the pre-fix instruction text actually
reintroduces the capitalised spelling the sweep exists to catch — five offending occurrences
across the two files, none of which appear in the current (post-fix) tree, where
`case_every_argument_is_accepted` passes with zero offenders. No pinned sha appears as an
assertion inside the committed test file; this evidence is one-off and lives only here.

## git status --porcelain (worktree root)

```
 M .claude/skills/harness/bin/gh-sync.py
 M .harness/harness/features/BUG-1507-ready-station-signature/plan.yaml
?? tests/integration/test-station-argument-spelling.py
```

The `gh-sync.py` modification and the new test file are this task's own work (plus this receipt
and its parent `notes/` directory, not separately listed by porcelain since it is untracked
alongside the test file's sibling entry). The `plan.yaml` modification (2 lines changed) was
**not** made by this dispatch — no `plan.yaml` write occurred in this session — and is observed
here as concurrent orchestrator/tooling activity outside this task's scope (O-06), not
investigated or reverted. Nothing is staged; nothing is committed.
