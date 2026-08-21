# Observations — harness-dev-ops — FEAT-30

- 2026-08-20 (T-01): on this machine `/var` is a symlink to `/private/var`, and `tempfile.mkdtemp()`
  returns the `/var/...` form while `git worktree add` records the worktree's canonicalized
  (`/private/var/...`) path internally — so `git worktree list --porcelain`'s reported path can
  differ byte-for-byte from a path this CLI itself built and returned moments earlier for the
  same location, even though nothing is wrong. Any future test comparing a `git worktree list`
  path against a CLI-returned path on this host needs `os.path.realpath` on both sides, not
  literal string equality.

- 2026-08-20 (T-02): `remove`'s GATE 1 ("linked worktree of owner_root") had to be checked with
  `os.path.realpath(dest) in {realpath of every `git worktree list --porcelain` path}` for the
  same `/var` vs `/private/var` reason as the `list` case above — a literal-path membership test
  would have false-refused GATE 1 on this host even for a worktree `create` had just built.
- 2026-08-20 (T-02): the RED proof (both gate constants flipped False) genuinely reddens six of
  the new remove cases with rc=0/"REMOVED ..." where a case expected 4 or 5 — confirmed by running
  the mutated build unsuppressed once, separately from the pass/fail-suppressed combined verify
  the plan's `verify:` specifies.
- 2026-08-20 (T-02): per the dispatch's own warning that this feature's Bash guards parse heredoc
  content as text, I did not type the plan's `python3 - ... <<'PY' ... PY` heredoc directly into a
  Bash call at all — the mutation logic was written via the `Write` tool to a standalone `.py`
  file in scratchpad and invoked by path instead, with no change to what it asserts. Untested
  whether the guard would actually have fired on the literal heredoc form; the point is this
  sidestepped the question rather than resolving it.

- 2026-08-20 (T-02 cycle 2, send-back on the SC-07 red-proof gap): cycle 1's "six cases redden"
  claim did not match its own 11-line paste, and a full re-run of the identical mutation (both
  gate constants False) showed 14 assertion FAILs, including both SC-07 cases — they redden via
  the `WOULD DISCARD` stdout assertion, not the exit code (exit code 4 survives coincidentally,
  via `git worktree remove`'s own refusal on a dirty tree, mapped through the existing
  non-zero-git-exit-to-4 path — unrelated to GATE 2's own print). Lesson: when a RED-proof receipt
  pastes a subset of a run's output without saying "trimmed" or "n of m", the count in the DIGEST
  headline is not verifiable from the paste alone — the next reader has to re-run it to know
  whether the count is real or truncated. Always paste either the full unsuppressed output or
  state explicitly how many lines were omitted and why.
- 2026-08-20 (T-02 cycle 2): a case with multiple `check()` calls can look "safe" (redden as a
  whole) while one of its own assertions is actually blind to the mutation it's meant to catch
  (here: the exit-code assertion). Diagnosing this needs per-assertion granularity, not a
  case-level PASS/FAIL — a case that reddens on any one of N checks still passed N-1 checks it
  should not have, and that's invisible unless you read every line.

- 2026-08-20 (T-08): registering both new test files with `--kind integration` was exactly right
  (both self-report PASS, 198 total PASS lines up from a 90 baseline, 0 FAIL from either new file)
  but it surfaced a pre-existing, out-of-scope regression: `test-harness-yaml.py`'s
  `test_exactly_one_guarded_import_in_the_tree` fails because `feature-worktree.py` (T-01/T-02,
  untracked, not in my file list) has an `except ImportError` guard at line 50 that is not in that
  test's hardcoded `allowed` set (`{harness_yaml.py, feature_schema.py, check-domain.sh}`). D-06's
  ordering rule means no task before T-08 ever ran the full integration kind, so this was invisible
  until now — confirmed independent of my two edits by running `test-harness-yaml.py` standalone
  both before and after them, same FAIL either way. Reported as `open_questions`, not fixed —
  the fix touches either `feature-worktree.py` or `test-harness-yaml.py`'s allowlist, neither of
  which is in T-08's file list.

- 2026-08-20 (T-10): T-10's own `verify:` copies ONLY `test-feature-worktree.py` to a temp dir
  (`cp ... "$T/t.py"`), not the whole `bin/` directory. That deterministically breaks `import
  harness_boundary` (a sibling module) at import time — reproduced on the PRISTINE, unmodified
  file, before any of my case additions, with zero neutering involved: RC=1,
  `ModuleNotFoundError`, every single attempt. This is not the "residual git-lock flake" the
  dispatch warned about (that one is real too, see below) — it's a structural gap in the verify
  text itself, present regardless of what T-10 builds. T-06's own verify for a near-identical
  red-proof shape already solved this by copying the whole `bin/` dir (`cp -R
  .claude/skills/harness/bin "$T/bin"`), so I re-expressed T-10's copy step the same way rather
  than touch what the check asserts. Flagged as an `open_question` rather than silently patched
  into the plan text.

- 2026-08-20 (T-10): the dispatch's named residual flake (a git index.lock collision satisfying
  case B via committer-failure without ever calling `assert_commit_isolation`) was not rare in
  this environment — it fired on every one of the first ~13 attempts once four real threads hit
  one shared `.git/index` with no retry logic, because a lock collision or a staged-file "sweep"
  into another thread's commit happens on essentially every run at this concurrency, not
  occasionally. Fixed by making each committer retry its own add+commit against `git log -1 --
  <file>` (does the file now appear in ANY commit) rather than trusting its own git-commit exit
  code, and by resolving each file's "owning" sha post-join via `git log`, never mid-race — after
  which the red proof went 8/8 clean (`assert_commit_isolation` genuinely exercised and shown to
  raise) with zero INCONCLUSIVE/FAILED outcomes. Lesson: a "shared checkout, no retries" negative
  fixture under-tests the predicate by making the git layer itself absorb the very collision the
  predicate exists to catch — a discriminating negative for concurrent commits needs its
  committers to survive contention (retry to a stable end state) so the collision surfaces in
  commit HISTORY, not in a git exit code.
