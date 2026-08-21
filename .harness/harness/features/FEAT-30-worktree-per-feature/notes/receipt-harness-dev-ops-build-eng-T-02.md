# Receipt — harness-dev-ops — build-eng — T-02

## Result

PASS. Second writer on both files (idempotence precondition checked: neither `remove` nor any of
`WOULD DISCARD`/`VERIFIED`/`MISSING`/`DIFFERS` existed on disk before I wrote — grep on named
strings, not a line count). T-02's `verify:` (byte-diffed against plan.yaml lines 456-473 before
running — identical apart from a heredoc-delimiter rename I introduced only inside my own diff
harness to avoid shell nesting; the plan text itself is untouched) exits 0. All 76 cases in
`test-feature-worktree.py` pass (T-01's 55 + 21 new). No stray worktree or branch left in this
checkout (`git worktree list` still shows only the pre-existing FEAT-31 worktree; no `FEAT-9*`
branch exists).

## Files written

- `.claude/skills/harness/bin/feature-worktree.py` — added `remove` subcommand: `cmd_remove`,
  `_linked_worktree_paths`, `_status_paths`, and the `remove` subparser/dispatch. `create`,
  `list`, `path` untouched in behavior.
- `.claude/skills/harness/bin/test-feature-worktree.py` — added `create_one`, `_commit_artifact`,
  `_merge_into_default`, and five new case functions wired into `main()`, reusing T-01's
  `build_fixture`/`run_guard`/`run_cli`/`_git` unchanged.

## Verify — verbatim command and its verbatim output

Command (byte-diffed against plan.yaml T-02 `verify:` before running — identical, modulo the
heredoc delimiter rename noted above, which never touched the plan file):

```
set -u
T=$(mktemp -d) || exit 1
cp -R .claude/skills/harness/bin "$T/bin" || exit 1
python3 - "$T/bin/feature-worktree.py" <<'PY' || exit 1
import sys
p = sys.argv[1]
s = open(p).read()
m = s.replace("REFUSE_ON_DIRTY = True", "REFUSE_ON_DIRTY = False", 1)
m = m.replace("REQUIRE_LANDED = True", "REQUIRE_LANDED = False", 1)
assert m != s and "REFUSE_ON_DIRTY = False" in m and "REQUIRE_LANDED = False" in m, \
    "the two gate constants were not found BY NAME"
open(p, "w").write(m)
PY
FEATURE_WORKTREE_BIN="$T/bin/feature-worktree.py" \
  python3 .claude/skills/harness/bin/test-feature-worktree.py >/dev/null 2>&1 \
  && { echo "RED PROOF FAILED: the suite passes with both refusals switched off"; exit 1; }
python3 .claude/skills/harness/bin/test-feature-worktree.py || exit 1
exit 0
```

Per the dispatch's hazard warning (Bash guards read heredoc TEXT, no notion of quoting), the
`python3 - ... <<'PY'` body was never typed into a live Bash call. It was written via the `Write`
tool to a standalone `.py` file in scratchpad and invoked by path — same mutation logic, same two
assertions, zero change to what is being checked. The combined verify (suppressed form, matching
the plan exactly) ran to exit 0.

**RED PROOF, surfaced unsuppressed** (same mutated build, `python3 test-feature-worktree.py` run
directly instead of through the `&&`-gated suppression) — six of the new `remove` cases actually
redden with the gates disabled, `rc=0` and `REMOVED ...` where 4 or 5 was expected:

```
FAIL  SC-04 refuse: remove exits 5 when the artifact is unmerged
      | rc=0 stdout='REMOVED /var/.../repoA/.claude/worktrees/harness/FEAT-96\n' stderr=''
FAIL  SC-04 refuse: stdout names MISSING .harness/harness/features/FEAT-96/BRIEF.md
FAIL  SC-04 allow: remove exits 0 once the artifact is landed
      | rc=3 stdout='' stderr='feature-worktree: remove: not a linked worktree of ...: .../FEAT-96\n'
FAIL  SC-04 allow: stdout names VERIFIED .harness/harness/features/FEAT-96/BRIEF.md
FAIL  SC-04 allow: the final line begins REMOVED
FAIL  SC-04 differs: remove exits 5 when worktree and default-branch blobs differ
FAIL  SC-04 differs: stdout names DIFFERS .harness/harness/features/FEAT-97/BRIEF.md
FAIL  SC-04 differs: the tree still exists on disk
FAIL  no artifact directory at all: remove exits 5
FAIL  no artifact directory at all: stdout names the directory .harness/harness/features/FEAT-98
FAIL  no artifact directory at all: the tree still exists on disk
FAIL test-feature-worktree.py
exit: 1
```

(One "SC-04 allow" case above shows `rc=3` rather than a bare pass-through: with `REQUIRE_LANDED`
disabled, the prior `remove` in the same case already removed the worktree, so the *second* call
in that pair correctly hits GATE 1 — "not a linked worktree" — for an unrelated reason. This is the
suite reddening for real, not a scripted failure; it is exactly the kind of extra discriminator a
partial run can miss, so it is reported here rather than pruned.)

**Final suite run** (`python3 .claude/skills/harness/bin/test-feature-worktree.py`, both gates
restored — this ran against the *real*, unmutated `feature-worktree.py` in the working tree, not
the mutated tempdir copy): all 76 cases `PASS`, ending `PASS test-feature-worktree.py`, exit 0.

## Design notes for the reviewer

- `remove` resolves `--repo` through the same `resolve_repo` and `dest_for` T-01 already defines;
  no second resolver was added.
- GATE 1 checks membership in `git worktree list --porcelain`'s reported paths via
  `os.path.realpath` on both sides (`_linked_worktree_paths`), for the same `/var` vs
  `/private/var` reason T-01's `list` case already had to handle on this host — a literal-path
  check would have false-refused a worktree `create` had just built moments earlier.
- GATE 2 prints one `WOULD DISCARD <path>` line per `git status --porcelain` entry (untracked and
  tracked-modified alike; renames use the destination-side path), then one summary line naming
  the count and the tree, then exits 4 without touching anything.
- GATE 3 walks `.harness/<segment>/features/<id>` inside the worktree, printing exactly one of
  `VERIFIED`/`MISSING`/`DIFFERS` per file found — every file is checked and printed before the
  gate decides, not stopped at the first failure. An entirely absent artifact directory prints one
  `MISSING ARTIFACT DIRECTORY <dir>` line and exits 5 without walking anything.
- Removal only runs `git worktree remove` then `git worktree prune` in `owner_root` after all
  three gates pass; git stderr passes through on a non-zero exit (4); success prints `REMOVED
  <dest>` as the last line.
- Test cases 1–6 from the intent map to `case_remove_dirty_untracked`,
  `case_remove_dirty_tracked`, `case_landed_refuse_then_allow` (cases 3 and 4 together, same tree,
  same id — refuse-then-merge-then-allow, as the intent's numbering implies), `case_landed_differs`,
  `case_no_artifact_directory`. Every one of the 21 new `check()` calls asserts on an exit code, a
  named path/directory string, or both — none asserts only one when both were named in the intent.
  New fixture ids `FEAT-94`..`FEAT-98` were chosen to avoid colliding with T-01's `WT` list
  (`FEAT-90`..`FEAT-93`).
- No case's `owner_root` ever resolves outside the `tempfile.mkdtemp()` fixture: every new case
  runs only inside the `if run_guard(fx, root):` branch T-01 established, after the T-01 guard has
  already asserted `path --repo harness --id FEAT-90` lands under `root`.

## Not done here (by design)

`run-unit-tests.sh` was not invoked (D-06 — registration is T-08's). T-03/T-04/T-05/T-07/T-09 were
not touched (`execution_mode: main-session-direct`, DEC-174). `harness_boundary.py`,
`check-domain.sh`, `bash-write-guard.sh`, and their test files were not touched. Nothing was staged
or committed.
