# Security Review — BUG-1507-ready-station-signature — c0

**Verdict: PASS, no security surface.** Diff at `review_sha=ac5e24e5` (base `4b5dbb23`, 5 files,
+38/-6 across the real diff, excluding the 21 feature-tree bookkeeping files that are pure
records, not code/instructions under review) is documentation/docstring text plus one new
stdlib-only test file. No auth, secrets, injection, or data-exposure surface is touched.

## Census (5 files, all read at the pin via `git show ac5e24e5:<path>` / `git diff 4b5dbb23 ac5e24e5`)

| # | File | What changed | Auth/secrets/injection/exposure? |
|---|---|---|---|
| 1 | `.claude/commands/harness-plan.md` | 2 lines: `Plan`→`plan`, `Ready`→`ready` in two documented command strings (`board-station.py <n> plan`, `gh-sync.py status <dir> ready`) | No — case-only spelling fix to a literal token in a fixed, non-interpolated command string. No new command, no new argument shape, no user-controlled substitution. |
| 2 | `.claude/skills/harness/references/github-mirror.md` | 2 lines: `Review`→`review` on :53/:55-56 (line-wrapped); Building/Ready/Review table rows rewritten to attribute writes correctly (`gh-sync.py start-task` for the task card, `plan-merge.py set-feature-station --station building` for the feature's own station) | No — same class of edit: case-fix on a literal argument, plus prose reattributing *which existing script* writes *which existing field*. No new script, no new write target, no argument built from input. |
| 3 | `.claude/skills/harness/SKILL.md` | +4 lines, build-phase segment 1: instructs the orchestrator to run `plan-merge.py set-feature-station --station building` at dispatch start | No — instructs invocation of an existing script with a fixed literal `--station building` argument. Not attacker-influenced; no new file target, no new write path. |
| 4 | `.claude/skills/harness/bin/gh-sync.py` | +16 lines, all inside `cmd_status`'s docstring (confirmed: diff hunk starts and ends entirely within triple-quoted doc text; the first executable line after the docstring, `if station not in STATION_VALUES:`, is unchanged, 0 deletions in the file) | No — docstring-only; zero executable lines touched. Verified the `_record_station`/branch logic it describes is unchanged by re-reading the function body immediately following the docstring at the pin. |
| 5 | `tests/integration/test-station-argument-spelling.py` | New file, 149 lines, stdlib-only (`glob, os, re, shutil, sys, tempfile` + in-repo `factory_config`) | No — see explicit checks below. |

## Explicit checks performed (not predicted)

- **Subprocess / shell-out:** grepped the full file text (read raw) for `subprocess`, `os.system`,
  `os.popen`, `eval`, `exec` — none present. The file never invokes `gh-sync.py` or
  `board-station.py`; it only regex-scans their *instruction text* in `.md` files. Zero process
  spawning anywhere in the diff's fifth file.
- **Execution of discovered content:** `TOKEN_PATTERN` extracts `(tool, token)` pairs from Markdown
  prose via `re.finditer` and only ever compares `token` against a set membership
  (`ACCEPTED_STATIONS`) or formats it into a print/assert string. Nothing extracted is ever
  passed to `open()`, `import`, `eval`, or a subprocess argv. No path is built from swept text.
- **Sweep scope and reads:** `scope_files()` globs only `.claude/commands/*.md` and
  `.claude/skills/**/*.md` under an explicit `root` argument (never a var/env override — confirmed
  by reading the whole file, no `os.environ` reference exists). `occurrences()` opens each matched
  path read-only (`open(path, encoding="utf-8")`, no write mode). The sweep cannot escape the
  repository tree it's rooted at, and it never writes.
- **Negative-control mutation (`case_reddens_on_a_reintroduced_capital`):** uses
  `tempfile.TemporaryDirectory()` — an OS-managed, auto-cleaned scratch directory outside the repo
  — copies exactly two named repo files into it with `shutil.copy`, then mutates **only the
  in-scratch copy** (`plan_copy`, a path under `tmp`) via `open(plan_copy, "w", ...)`. The
  real repo files (`REPO_ROOT`-rooted paths) are never opened in write mode anywhere in the file.
  Confirmed: the only `"w"`-mode `open()` call in the entire file targets `plan_copy`, computed
  from `os.path.join(tmp, rel)`, never from `REPO_ROOT`. No writes escape the scratch dir.
- **Path construction from data:** the only paths built from swept/extracted text are the
  glob results themselves (`os.path.join(root, ...)`, `root` always caller-supplied, never
  matched text) — `token`/`tool` values (the regex captures) are never used to build a path.
- **`gh-sync.py` executable-line check:** confirmed via `git diff` and adjacent `git show` read
  that all 16 inserted lines sit strictly between the existing docstring's `- Review:` bullet and
  the existing `- Plan, Done, Abandoned:` bullet, both unchanged; the function's first
  non-docstring statement (`if station not in STATION_VALUES:`) is byte-identical pre/post.
- **Instruction-text edits changing what an operator/agent is told to run:** the only *new*
  instruction is SKILL.md's addition telling the orchestrator to invoke
  `plan-merge.py set-feature-station --station building` at build-segment start. This is an
  existing, already-shipped script (not introduced by this diff) invoked with a fixed literal
  flag value (`building`) — no operator- or attacker-supplied data flows into the command. It
  writes to `plan.yaml`'s own `status` field, the same file/field class every other documented
  station write in this feature already writes to. Not a new write *target*, only a new *trigger
  timing* for an existing, already-reviewed write path.

## Already-adjudicated (info, not a gate — ruling R1)

Task-card Ready-column exclusivity (`gh_board.py` station-derivation: `_task_statuses` reads an
absent or already-`ready` task status as `ready`, so an ordinary reconcile can park a task card at
Ready with no signature) is a real authorization weakness — a task card's presence at Ready is
*not* proof of a signed plan, only the parent's is. This diff does not touch `gh_board.py` and the
issue's own scope line excludes station-derivation code work; `BRIEF.md`'s `## Constraints`
"Disclosed limit" paragraph names this exact gap and defers it to a scope-widening decision at
signature. Recording it here per R1, not re-opening it: severity `info`, `already-adjudicated`,
no action requested.

## Scope statement

**Scoped IN** (this review looked, not predicted): all 5 files enumerated above, read at the pin
via `git show`/`git diff` against base `4b5dbb23`; the new test file read in full raw text and
checked line-by-line for subprocess/exec/write-outside-scratch/path-from-data patterns as directed.
**Scoped OUT**: `gh_board.py` station-derivation code (R1, already adjudicated) and any file outside
the five named — none exist in the review_sha diff beyond bookkeeping records under
`.harness/harness/features/BUG-1507-ready-station-signature/` (BRIEF.md, STATE.md, feature.json,
plan.yaml, notes/*, observations/*), which are data/records the feature itself produced, not
instruction or code surface, and carry no injection/auth/secret content on inspection.

No `must_fix`. `severity_max: info` (the R1 already-adjudicated note only; the five in-scope files
themselves carry zero findings).
