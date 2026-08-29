# Observations - harness-backend-dev

- 2026-08-29: T-06 (gen-decisions-index.py supersession removal). The `edit` tool resolved a relative path (`.claude/skills/harness/bin/...`) against the MAIN repo checkout, not the active worktree, even though prior `read` calls on the same session used the worktree's absolute path — a domain-hook success on the relative path silently modified the wrong checkout. Fix: always pass edit tool paths as the same absolute worktree path `read` returned in its `[path#tag]` header, never a repo-relative shorthand, when working inside a `.claude/worktrees/...` session. Caught it only by re-reading immediately after the edit and finding the worktree file unchanged; `git status --porcelain` in the main repo confirmed the stray diff, which I reverted with `git checkout --` before redoing the edit against the correct absolute path.
- 2026-08-29: T-17 anchor-rot checker — regex `` `([\w./-]+\.(py|sh|md|json|yaml|yml|ts|toml)):(\d+)(?:-\d+)?` `` applied to `git show 7ebfc9e:.harness/harness/docs/DECISIONS.md` extracts exactly 32 anchors, of which exactly 3 fail basename-in-`git ls-files` existence (all `feature.yaml`/`FEAT-03-subissue-mirror/feature.yaml`) — matches the dispatch's expected "exactly three feature.yaml anchors" without any tuning; useful reference point if a future task touches this checker's grammar.
- 2026-08-29: gen-decisions-index.py's default-path resolution is `harness_boundary.resolve_root(_BIN_DIR)` + `os.path.join(".harness","harness","docs","DECISIONS.md")`, called inside `main()` (call-time, post-chdir) — not at module import. Any sibling checker needing the same default should call `resolve_root` directly rather than importing `DECISIONS_PATH`, since that constant is relative and assumes the generator's own `os.chdir(project_dir)` already ran.
- 2026-08-29 (T-10): the mutation-proof step for a generator test that reads the LIVE .harness/harness/docs/DECISIONS.md required a temporary write to that file, but DECISIONS.md is documentor's domain (.harness/*/docs/**), not backend-dev's — check-domain and bash-write-guard both correctly refused it. Dispatches that ask backend-dev to mutate DECISIONS.md for a proof need to route the actual write through documentor or grant a scoped exception; backend-dev cannot self-serve it.
- 2026-08-29 (T-10): test_root_resolves_through_harness_boundary_not_the_retired_variable (test-gen-decisions-index.py) went from `ok` at T-06 (see receipt-harness-backend-dev-2026-08-29-03-eng.md) to `FAIL` by T-10, with zero code changes to that test path — root cause is the same orphan-row exit(1) the two by-construction-red cases hit, caused by T-04/T-05/T-07's DECISIONS.md deletions landing before T-11 regenerates DECISIONS-INDEX.md. Any T-10-era verify script's FAIL exclusion list that only names the two committed-index cases will be one short until T-11 lands.
- 2026-08-29 (T-12): CRITICAL environment defect — the `edit`/`write` tool family resolved
  relative worktree paths against the MAIN checkout (/Users/molchairuangutai/GitHub/harness),
  not the assigned worktree, even though the `read` tool and path echoes showed the worktree
  path. `edit` reported success and showed correct-looking diffs, and a repeat `edit` call
  reported "byte-identical" (already applied) — but `bash`/`git status` in the worktree showed
  zero change, while `git status` in the MAIN checkout showed my edits landed there instead.
  Confirmed via a `write`-tool probe file that resolved under the main checkout's absolute path.
  Recovered by: diffing the main checkout to confirm the accidental changes were exactly my
  intended edits (nothing else touched), restoring those 9 files from `git show HEAD:<path>`
  content via plain `cp` (no git command against the main checkout), deleting the stray probe
  file, then redoing every edit via `bash`/`python3 -c` (inline, not heredoc — heredocs
  targeting scratch paths outside the domain manifest tripped `bash-write-guard`) directly
  against the worktree, verified by `git status`/`git diff` inside the worktree after every
  batch. Lesson for future tasks in this environment: after the FIRST `edit`/`write` call in a
  worktree session, verify with `bash`/`git status` in the SAME worktree before trusting the
  tool's own "success" report — do not assume `edit`/`write` and `bash` share a filesystem view.
