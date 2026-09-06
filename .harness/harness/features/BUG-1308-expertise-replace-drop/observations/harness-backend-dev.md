# Observations - harness-backend-dev

- 2026-09-05: BUG-1308 T-01 — the plan's Step A "missing required key" refusal lines needed a
  concrete wire format not fully pinned by the intent prose (which key literal + which index
  spelling). Chose `MALFORMED OPS op index=<i>: <message>` naming the literal token `section` (or
  `target`/`entry`) inline; both unit test and implementation authored together so the format is
  self-consistent, but a sibling reading only the plan intent would need to re-derive it — worth
  flagging in T-02/T-03 if they independently assert on refusal line shape beyond code+prefix.
- 2026-09-05: the `read` tool's structural-summary numbering for `expertise-merge.py` (a 561-line file with docstrings spanning multiple functions) silently truncated at ~293 lines and renumbered subsequent content as if the file ended there — `grep`'s line numbers against the same cached read matched the wrong physical lines entirely (off by ~230). Cross-checked against `wc -l` and `sed -n` (bash) which gave correct content/counts throughout. When a `read` summary's line count disagrees with `wc -l` for the same path, trust `sed`/`wc` and treat the read-tool numbering as unusable for that file rather than debugging further.
- 2026-09-05: `code-grade.py --base REF --head REF` reads file content via `git show <ref>:<path>`, so it can only ever grade committed code — to grade UNCOMMITTED working-tree changes, pass explicit file paths as positional args instead (`_paths_report` reads `(root/path).read_text()` off disk). Positional-path mode also surfaces every function in the file, not just the ones changed in a diff — this exposed pre-existing sub-bar functions in `expertise-merge.py`'s untouched `apply` path (`parse_expertise`, `compute_union`, `cmd_apply`) that no prior review had seen because they only ever ran the diff-scoped `--base/--head` mode.
