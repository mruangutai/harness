# T-05 build evidence: caller policy, exit-2 correction, probe comments, DEC-138 amendment

Built main-session-direct (DEC-174) by `BuildD_T05` in this worktree from HEAD `3369f844`.
`HARNESS_AGENT_TYPE` and `CLAUDE_PROJECT_DIR` were unset. No git writes, no remote calls. Raw
outputs are in `t05-build/`, each ending with its `exit=` line. The GitHub issue, the live probe
and their two receipts are Main's.

## Edits

- **`.claude/skills/harness/references/github-mirror.md`**
  - The four-shapes bullet for a write failing while `gh` works overpromised continuation. It now
    says per-item writes (`gh_try`, board projection) continue, while a `gh()` failure is the
    mid-flight `SKIP` (exit 0) and the remaining writes do not run.
  - New `## Caller-to-failure-policy` section: FACTORY_GH as the only override, why policy sits
    at callers, and a three-column table (condition / outcome and exit / partial writes and
    recovery). Every row was read from the code at `3369f844`, not from the intent.
  - **Milestone row states the actual behaviour:** ordinary create looks the title up on ANY
    failure. It also says the 422 narrowing was cut (divergence (e), C5, see
    t02-red-green.md).
  - Notes: subprocess deadlines are a conscious non-goal, so a hung gh can hang every consolidated
    path. The enforcement executors keep their private `GH_BIN`/deadline semantics, and the backlog
    ticket is not their fix.
- **`.claude/skills/harness/bin/factory_cli.py`** (docstring only). Exit 2 is now refusal or
  failure, and it may follow irreversible remote writes. The examples are factory_land's push and
  PR create before a later board move, and factory_decompose's created issues and receipt before a
  later edge write. Exit 3 keeps its distinct lost-race "nothing mutated" claim. No code changed.
- **`tests/manual/probe-issue-types.py`**. Two comments now read "never honour a binary
  override" and "never an override", and the hardcoded no-fixture rationale is kept.
  `GH = "gh"` and all code are byte-identical, and `py_compile` passes.
- **`.harness/harness/docs/DECISIONS.md` DEC-138, "Shared code, and migration scope."** Only the
  implementation sentences were rewritten in place: the argv builders stay in gh_issues.py,
  `factory_gh` is the one shared transport (it resolves `FACTORY_GH` and launches gh for every
  caller), and failure policy stays at each caller, with the gh-sync/wayfind example kept. The
  write-only guard sentence's text is unchanged; it now starts on its own line. There is no
  gh_bin, no "keeps its own runner" and no provenance. DEC-146 is untouched.
- **`DECISIONS-INDEX.md`**. Regenerated (`01-gen-index.txt`, exit 0). Only `@line` anchors after
  DEC-138 shifted by +2, and every ruling tail is unchanged. `--stdout` matches the written file
  (`02-index-stdout-diff.txt`, exit 0).

## Verify

- `03-verify.txt`: the literal T-05 verify, **exit 1**. Main's two receipts already exist and their
  assertions passed. It fails at the retired-override sweep on `tests/unit/test-wayfind.py:417`
  (T-04-owned, outside T-05's edit list). case_13's absence assertion contains the literal
  `"GH_SYNC_GH"`.
- `04-verify-own-lines.txt`: the same assertions without the receipt lines, with the same single
  failure. The policy vocabulary assertions pass before the sweep. The exit-2 and DEC-138
  assertions after it pass on their own (`05-remaining-assertions.txt`, exit 0).
