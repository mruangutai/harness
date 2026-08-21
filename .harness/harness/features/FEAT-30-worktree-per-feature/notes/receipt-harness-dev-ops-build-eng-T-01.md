# Receipt — harness-dev-ops — build-eng — T-01

## Result

PASS. T-01's `verify:` (byte-diffed against plan.yaml lines 288-295 before running — matches
exactly) exits 0. Both new files written, nothing else touched, no stray worktree or branch
created in this checkout (`git worktree list` still shows only the pre-existing FEAT-31
worktree; `git branch --list | grep FEAT-9` empty).

## Files written

- `.claude/skills/harness/bin/feature-worktree.py` — new, executable. `create`/`list`/`path`
  subcommands. `remove` deliberately absent (T-02).
- `.claude/skills/harness/bin/test-feature-worktree.py` — new. 55 cases, house shape
  `(name, ok, detail)`, subprocess-only invocation of the CLI with `CLAUDE_PROJECT_DIR` pointed
  at a `tempfile.mkdtemp()` fixture.

Idempotence precondition checked before writing: neither file existed at start (`ls` on both
paths → "No such file or directory"), so nothing here overwrote another writer's work.

## Verify — verbatim command and its verbatim output

Command (byte-diffed against plan.yaml T-01 `verify:` before running — identical):

```
set -u
FEATURE_WORKTREE_BIN=/nonexistent/feature-worktree.py \
  python3 .claude/skills/harness/bin/test-feature-worktree.py >/dev/null 2>&1 \
  && { echo "RED PROOF FAILED: the suite passes with no CLI under test"; exit 1; }
git show eeabc59:.claude/skills/harness/bin/feature-worktree.py >/dev/null 2>&1 \
  && { echo "RED PROOF INVALID: the CLI already existed at eeabc59"; exit 1; }
python3 .claude/skills/harness/bin/test-feature-worktree.py || exit 1
exit 0
```

Combined run: exit 0, no `RED PROOF` line printed on stdout — confirming both guard branches
did not trip. Run again with each branch surfaced individually for the record:

**RED PROOF branch 1** (`FEATURE_WORKTREE_BIN=/nonexistent/feature-worktree.py`, without the
`>/dev/null` suppression, to show the suite actually reddens):

```
GUARD FAILED — refusing to create anything; skipping remaining cases
FAIL  GUARD: path --repo harness --id FEAT-90 resolves inside the fixture directory
      | rc=2 stdout='' stderr="...Python: can't open file '/nonexistent/feature-worktree.py': [Errno 2] No such file or directory\n"
FAIL test-feature-worktree.py
exit: 1
```

**RED PROOF branch 2** (`git show eeabc59:.claude/skills/harness/bin/feature-worktree.py`):

```
fatal: path '.claude/skills/harness/bin/feature-worktree.py' exists on disk, but not in 'eeabc59'
exit: 128
```

**Final suite run** (`python3 .claude/skills/harness/bin/test-feature-worktree.py`): all 55
cases `PASS`, ending `PASS test-feature-worktree.py`, exit 0.

## Design notes for the reviewer

- `--repo` resolution, `dest_for`, and the two module constants (`REFUSE_ON_DIRTY`,
  `REQUIRE_LANDED`) match the intent's literal names and signature.
- `harness_boundary.WORKTREES_SEGMENT` is read via one lazy-import helper in
  `feature-worktree.py`; the segment string `.claude/worktrees` is not spelled a second time
  anywhere in that file. The test file (not under that constraint) imports `harness_boundary`
  directly to build its own expected-path assertions.
- `list`'s membership filter uses `os.path.commonpath` over `os.path.realpath` of both sides,
  never string-prefix, per the conflation-guard requirement.
- One environment-specific wrinkle, recorded because it shaped a test assertion rather than the
  CLI: on this machine `/var` is a symlink to `/private/var`, and `git worktree add` records the
  worktree's canonicalized path internally, so `git worktree list --porcelain`'s path differs
  byte-for-byte from `create`'s own literal `dest_for()` output even though both name the same
  location. The `list` case (case 8) compares via `os.path.realpath` on both sides rather than
  literal string equality for this reason — `create`'s own case (case 1, layout) is still
  asserted on the literal, unresolved `dest_for()` join, per its own wording.

## Not done here (by design)

T-02 (`remove`), T-04 (`WORKTREE_REL_RE` cutover), and every `run-unit-tests.sh` registration
(D-06 — no task before T-08 may invoke the runner). Nothing was staged or committed.
