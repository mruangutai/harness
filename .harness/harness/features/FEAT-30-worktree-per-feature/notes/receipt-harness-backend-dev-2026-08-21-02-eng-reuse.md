# REUSE angle — FEAT-30 `49c528a..fbb3bc0` — read-only

## Finding 1 (med, apply-candidate) — `feature-worktree.py` re-derives what `harness_boundary.linked_worktrees` already answers, via a git subprocess instead of the no-subprocess pointer read

- **File/line:** `.claude/skills/harness/bin/feature-worktree.py:184-190` (`_linked_worktree_paths`), consumed at `:210` (`cmd_remove` GATE 1).
- **The existing thing:** `.claude/skills/harness/bin/harness_boundary.py:71-115`, `linked_worktrees(owner_root)` — "Absolute checkout directories of `owner_root`'s linked worktrees, sorted. Standard library only... NO GIT SUBPROCESS" — reads each `.git/worktrees/<id>/gitdir` pointer file directly and is already the function `check-domain.sh`'s post-write sweep calls to answer exactly this question. `feature-worktree.py` already imports this module (`_harness_boundary()`, used for `WORKTREES_SEGMENT` at `:59`/`:160`), so the import cost is already paid.
- **What `feature-worktree.py` does instead:** `_linked_worktree_paths` (`:184-190`) shells out to `git worktree list --porcelain` and reparses the text with its own `_parse_worktree_porcelain` (`:136-154`) to get the same set of realpaths. `cmd_list` (`:157-176`) does the same subprocess call plus its own `commonpath` filter against `worktrees_root` to decide which entries count as belonging to this owner_root.
- **Concrete cost:** two independent answers to "what are this repo's linked worktrees" now have to be kept in lockstep by hand — one reads git's on-disk pointer files with no subprocess (the sweep's source of truth, and the one DEC-193's no-subprocess-on-the-governed-write-path framing was written for), the other trusts `git worktree list --porcelain`'s parsed text. A worktree whose pointer is present but that porcelain omits (or the reverse — e.g. a stale/prunable entry) makes `cmd_remove`'s GATE 1 and `check-domain.sh`'s sweep disagree about whether the same path is a legitimate linked worktree, and nothing detects the disagreement because the two call sites never call the same function. No test in `test-feature-worktree.py` exercises that divergence (it is a missing-case finding on its own, not bundled into this apply).
- **Alternative:** `cmd_remove`'s GATE 1 can call `hb.linked_worktrees(owner_root)` directly and test `os.path.realpath(dest) in {...}` against that set, dropping `_linked_worktree_paths` entirely. `cmd_list` still needs branch names from the porcelain output (which `linked_worktrees` does not carry), but it can use `hb.linked_worktrees(owner_root)` as the authoritative membership set and only read porcelain for the branch field, instead of re-deriving membership from `commonpath` against `worktrees_root` itself.
- **Apply-candidate:** `.claude/skills/harness/bin/feature-worktree.py` (permitted). No change to `harness_boundary.py` needed — pure consumption of an already-imported, already-exported function.

## Finding 2 (info, flag-only) — `expertise-merge.py` re-spells three more of `check-expertise.sh`'s format constants than the already-settled A-2 names

- **File/line:** `.claude/skills/harness/bin/expertise-merge.py:36-37` (`SECTION_RE`, `ENTRY_RE`) and `:157-161` (`default_title`).
- **The existing thing:** `.claude/skills/harness/bin/check-expertise.sh:43-44` (`SECTION_RE = re.compile(r"^## (\w+)(?: \(max (\d+)\))?\s*$")` — byte-identical string; `ENTRY_RE` — same anchor idiom, narrower character class) and `:86` (`expected = f"# Expertise — {os.path.basename(path)[:-3]}"` — the exact same title format `expertise-merge.py`'s `default_title` reproduces).
- **A-2 (already settled) named only the four DEC-145 caps.** This finding is the same non-appliable category — `check-expertise.sh`'s copy lives inside a `python3 - <<'PY'` heredoc at `:36`, so it is not importable, same as the settled CAPS case — but the section/entry parsing regex and the title-format string are additional spellings A-2's citation did not name. Confirmed the drift detector A-2 asks about is present: `test-expertise-merge.py:226` `case_cap_drift_detector` compares this file's `CAPS` against `check-expertise.sh`'s text.
- **Concrete cost:** none actionable today — same as A-2, a heredoc genuinely cannot be imported by a plain script. Recorded so a future consolidation (e.g. lifting the heredoc into an importable module) is known to have four spellings to collapse, not one.
- **Apply-candidate:** none. `check-expertise.sh` is flag-only/DEC-174 (enforcement layer); `expertise-merge.py`'s side is a mirror of an unimportable heredoc, so there is nothing to apply on either side.

## Not flagged (checked and clean)

- `feature-worktree.py`'s `resolve_repo`/`dest_for` `repo.split("/", 1)[-1]` duplication of `factory_config.workspace_path`'s identical rule is A-5, already settled — not re-reported.
- `test-check-domain.py:109` `make_linked_worktree` (fabricates worktree pointer files, no subprocess) is a different testing need than `test-feature-worktree.py`'s real-git fixtures: `test-feature-worktree.py` exercises the actual CLI, which itself shells out to real `git worktree add`/`remove`, so a fabricated pointer pair would not exercise the code under test. Not a reuse violation.
- `test-expertise-merge.py`'s `write_file`/`write_entries`/`run_apply` are local to this file and match no existing shared fixture module (`layout_fixtures.py` is a different, unrelated fixture domain — layout-migration reader stubs, not Expertise files).
- No existing file-locking helper exists anywhere under `bin/` for `expertise-merge.py`'s `acquire_lock` to have re-implemented — genuinely new.

## Summary for DIGEST

Two findings, one apply-candidate (med), one flag-only/info (no apply available on either side).
