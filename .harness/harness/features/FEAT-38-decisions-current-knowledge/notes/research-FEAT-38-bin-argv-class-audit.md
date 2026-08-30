# research — FEAT-38 — argv built from parsed text, across `bin/`

**BLUF: the class REQ-10 asserts is NOT empty. Eleven of seventy candidate scripts build a command
line out of a value they parsed from a document or a configuration file.** Ten are production
scripts; one is a test. None of the eleven is the deleted claims checker, and none executes a whole
command string lifted from text — the deleted mechanism's shape. What they share is the weaker
shape Q2 names: a repository slug, a default branch, a task's `files:` path, a pid, or a
BRIEF/plan-derived title flowing out of a parsed file and into `argv`. Each is recorded below with
its call site so an independent reader can check the verdict without re-deriving it.

## Enumeration

Verbatim, re-runnable:

    git grep -lE 'subprocess|shlex|shell=|Popen|os\.system|eval\(' -- .claude/skills/harness/bin

**It returns 70 files in the current tree** (post-T-24: `check-decision-claims.py` and
`test-check-decision-claims.py` are deleted, so this is two fewer than the 72 the plan's intent
recorded at 99bb52c). Every one of the 70 has a row.

## The filter, as applied

- **Q1 — is the executable a literal in this file's own source?** For `shell=True`, `os.system` or
  `eval`, the executable is the whole command string.
- **Q2 — provenance, not grammatical role.** Does any `argv` element's VALUE come from something
  this script reads and parses (`.md`, `.json`, `.yaml`, `.toml`, stdin) rather than from its own
  source, `sys.argv`, the environment, a `harness_boundary` resolution, or git output?

Verdict precedence within a multi-site file: TEXT-DERIVED-ARGV > FIXED-LITERAL-ARGV > NO-EXECUTION.

## The decisive case — a whole command string stored in configuration

`.harness/harness.json`'s `test_kinds.<kind>.cmd` holds a complete command line
(`.agents/skills/harness/bin/run-unit-tests.sh --kind integration`). Q1 catches any script that
reads that field and executes it. **Every reader of `test_kinds` under `bin/` was found and judged;
none executes a `cmd`:**

- `run-unit-tests.sh:108` reads `test_kinds.integration.detect` — a pipe-separated glob string, not
  `cmd` — and only set-compares it against its own two literal bash arrays (lines 30-31). The
  scripts it actually runs come from those arrays (`run-unit-tests.sh:149`,
  `python3 "$BIN_DIR/$s"`). Nothing parsed reaches `argv`.
- `test-run-unit-tests-kinds.py:61-66` writes a mutated `detect` into a fixture and drives
  `["bash", RUNNER, "--check-kinds"]` (line 47) — argv all literal.
- `check-state.sh:480` parses `harness.json` and consults `test_kinds` for INV checks only; no
  `cmd` is executed there.
- `upgrade-config.py:209-211` is the only script that touches `test_kinds.*.cmd` at all, and it
  formats the value into a diagnostic string. It is not even in the candidate set (it matches no
  enumeration token).

So the `cmd` field is a stored command line with **no in-tree executor**. That is a live latent
risk, not a current finding: the string is executed by whichever agent or CI step is told to run
it, outside `bin/`.

## Per-file verdicts

| bash-write-guard.sh | FIXED-LITERAL-ARGV | line 42 runs python3 -c with a literal bootstrap plus the PY heredoc from its own source; argv[1:3] are $_derived and $_selfdir, both derived from BASH_SOURCE. The agent JSON it parses arrives via the HOOK_PAYLOAD env var (line 41), and its shlex.split uses (239, 380, 486) only tokenize for inspection, never execute |
| board_lifecycle.py | TEXT-DERIVED-ARGV | line 1003 _ensure_abandoned_label runs [gh_bin, "label", "create", "abandoned", "--repo", repo_name]; repo_name comes from _resolve_board, which reads harness.json github.repo at lines 289-298 (json.load then github.get("repo")) |
| check-decision-anchors.py | FIXED-LITERAL-ARGV | line 111 git_tracked_basenames runs ["git", "ls-files"], both elements literal; the DECISIONS.md anchors it parses (line 46 regex, line 172 open) are only compared against that output, never executed |
| check-domain.sh | FIXED-LITERAL-ARGV | line 1478 _unmodified_since_commit runs ["git", "-C", _checkout] + _argv where _argv is one of two literal lists (1476-1477) and _checkout comes from the _sweep list built at 1417-1421 from the resolved root plus harness_boundary.linked_worktrees, both excluded provenances |
| check-omp-port.py | FIXED-LITERAL-ARGV | line 152 runs [sys.executable, str(sync), "--root", str(root), "--check"]; sync is a literal path join off root (line 150) and root is the CLI argument. The many yaml.safe_load reads (43, 60, 116) feed assertions only, never argv |
| check-plan-routes.py | TEXT-DERIVED-ARGV | line 74 resolve_agents runs [CHECK_DOMAIN, "--resolve", path]; path is a task files: entry, called at line 199 and line 356 over literal_entries and literals, which come from harness_yaml.load_plan(plan.yaml) at line 308 or the PLAN.md regex reader. A plan-authored string is the third argv element |
| check-state.sh | TEXT-DERIVED-ARGV | line 1633 runs [_gh_bin30, "api", "--paginate", "repos/%s/milestones..." % _repo30]; _repo30 is harness.json github.repo, read at line 1583 from the parsed config. The other sites (470, 1117, 1405, 1749) are literal git and gh argv |
| factory_gh.py | FIXED-LITERAL-ARGV | line 153 run_gh runs [gh] + list(args); gh is _gh_binary(), the FACTORY_GH env var or the literal "gh", and args arrive as a function parameter. This file itself parses nothing off disk — its json.loads calls (170, 420, 521, 805) consume gh stdout for return values and error text, not argv |
| factory_workspace.py | TEXT-DERIVED-ARGV | lines 103, 129 and 130 pass default_branch into git checkout and git reset --hard argv; default_branch is entry["default_branch"] read from the parsed fleet.yaml at lines 113-115 via factory_config.load_fleet and repo_entry |
| feature-worktree.py | TEXT-DERIVED-ARGV | _run_git at line 91 runs ["git"] + args; line 125 passes default_branch to git worktree add -b and line 289 embeds it in git rev-parse <default_branch>:<rel>. default_branch is entry["default_branch"] from the parsed fleet.yaml, returned by resolve_repo at line 87 |
| feature_schema.py | NO-EXECUTION | the three matches (lines 6, 9, 292) are prose in a docstring explaining that this module is imported rather than spawned; the file contains no subprocess, os.system or eval call at all |
| gh-close-gate.py | NO-EXECUTION | it uses shlex to LEX the agent-proposed command line for inspection (line 47 shlex.shlex, punctuation_chars=True) and decides allow or deny; there is no subprocess, os.system or eval call anywhere in the file |
| gh-close-gate.sh | FIXED-LITERAL-ARGV | line 73 runs python3 -I -c with a literal one-liner plus "$_selfbin" from BASH_SOURCE, and line 79 execs python3 "$(dirname "$0")/gh-close-gate.py" "$root" where root is a harness_boundary.resolve_root result, an explicitly excluded provenance |
| gh-sync.py | TEXT-DERIVED-ARGV | the clearest instance in the tree. Line 775 passes title and body built from brief['feat'], brief['phrase'], brief['problem'] and brief['goal'] into gh issue create argv, and line 789 passes task['title'] and task['body']; parse_brief reads BRIEF.md at line 289 and parse_tasks reads plan.yaml or PLAN.md at lines 305-355. Every gh call also carries --repo repo from harness.json github.repo, read at line 200 |
| gh_cost_log.py | FIXED-LITERAL-ARGV | line 82 _read_counter runs [_counter_binary()] + list(_COUNTER_ARGV); the binary is the FACTORY_GH env var or the literal "gh" (line 75) and _COUNTER_ARGV is a module constant. Its only file access is the append-only log write at line 142 |
| harness_boundary.py | NO-EXECUTION | the single match at line 122 is a comment stating that this resolver deliberately runs no git subprocess; the file spawns nothing |
| harness_yaml.py | NO-EXECUTION | the single match at line 231 is a comment about a hook subprocess exit code; the loader itself never spawns a process and never evaluates its input |
| inflight_registry.py | TEXT-DERIVED-ARGV | line 159 runs ["ps", "-o", "lstart=", "-p", str(pid)]; on the _omp_claim_live path pid is claim.get("supervisor_pid") read from the registry JSON parsed at line 54 (line 178, then _process_start_time at 182). The executable is literal and pid is int-validated at line 131, so the exposure is narrow, but the value's provenance is a parsed .json |
| post-merge-sweep.sh | TEXT-DERIVED-ARGV | line 215 runs feature-worktree.py remove --repo repo_arg --id wt_id; repo_arg comes from _repo_arg_for_segment (line 152), which returns either the literal "harness" or a name read out of the parsed fleet.yaml via factory_config.load_fleet at lines 110-118 |
| run-unit-tests.sh | FIXED-LITERAL-ARGV | line 149 runs python3 "$BIN_DIR/$s" where s iterates the two literal arrays at lines 30-31, and line 101 runs python3 -I - with the KINDCHECK heredoc from its own source. It parses test_kinds.integration.detect at line 108 but only set-compares it; no parsed value reaches argv |
| test-bash-write-guard.py | FIXED-LITERAL-ARGV | the harness at line 185 runs [GUARD] with the JSON payload on STDIN, never in argv; the isolated-tree variants (240, 445, 490, 495) build the executable path by os.path.join off a tempdir this file creates |
| test-board-lifecycle.py | FIXED-LITERAL-ARGV | line 398 runs [sys.executable, SCRIPT] + args and line 415 runs [sys.executable, "-c", code]; SCRIPT is a module constant, args are caller literals, and code is an f-string from this file's own source |
| test-board-station.py | FIXED-LITERAL-ARGV | line 120 runs [sys.executable, SCRIPT] + args with SCRIPT a module constant and args supplied literally by each case; the fake gh binary is injected through the FACTORY_GH and GH_SYNC_GH env vars, not argv |
| test-branch-create-gate.py | FIXED-LITERAL-ARGV | line 49 runs [GATE] with the hook payload on stdin; GATE is a module constant path and no argument is added |
| test-check-decision-anchors.py | FIXED-LITERAL-ARGV | line 50 runs the checker as a subprocess with argv assembled from module constants and fixture paths this file creates under its own tempdir |
| test-check-domain.py | FIXED-LITERAL-ARGV | the dominant harness (152, 349, 952, 2486) runs [HOOK] with the payload on STDIN; the --resolve cases (797, 822, 895, 1836) pass a path literal written in the case itself, and the argv variables at 1014 and 2166 are lists built one line earlier from HOOK plus a literal flag |
| test-check-expertise.py | FIXED-LITERAL-ARGV | line 55 runs [CHECK, p] where p is a fixture path this file wrote into its own tempdir, and the argv parameter at line 90 is assembled by the caller from those same constants |
| test-check-omp-port.py | FIXED-LITERAL-ARGV | line 17 runs [sys.executable, str(CHECK), str(root)]; CHECK is a module constant and root is the fixture tree this file builds |
| test-check-plan-routes.py | FIXED-LITERAL-ARGV | line 62 runs the checker with argv from module constants plus the fixture plan path the case created; the plan text under test is read by the CHILD, never spliced into this file's argv |
| test-check-state.py | TEXT-DERIVED-ARGV | line 2620-2628 imports shlex, regex-matches the backticked command out of short_line (check-state.sh's own captured STDOUT) and builds argv = [sys.executable] + shlex.split(m.group(1)), which line 2655 EXECUTES. This is the argv-from-parsed-text shape, deliberately: SC-17 of an earlier feature required the printed command to be run rather than read. It is mitigated but not eliminated — argv[1] is rewritten to the real script path (line 2635) and the resolver probe at 2644-2652 refuses to run unless the resolved root is the fixture. Its other ~25 sites are literal git and SCRIPT argv |
| test-context-watch-cli.py | FIXED-LITERAL-ARGV | line 56 _run_cli runs [sys.executable, CONTEXT_WATCH_PATH] + args; the transcript JSONL fixtures it writes (lines 50-52) are read by the child from a path, never expanded into argv |
| test-context-watch-hook.py | FIXED-LITERAL-ARGV | line 84 fire runs [hook] with the payload JSON on stdin; hook is the constant path resolved in the fixture builder |
| test-dispatch-guard.py | FIXED-LITERAL-ARGV | line 48 runs [GUARD] with the payload on stdin, line 302 builds the mutant path by os.path.join off this file's own tempdir, and the git fixture calls (347-358) are literal argv |
| test-expertise-merge.py | FIXED-LITERAL-ARGV | line 81 run_apply runs [sys.executable, CLI, "apply", "--file", file_path, "--entries", entries_path] where both paths are fixture files this file created; the Popen race at 140 and 146 reuses the same construction. The ast.literal_eval calls at 268-269 evaluate a cap tuple, not a command |
| test-factory-claim.py | NO-EXECUTION | in-process by design; the three matches (4, 393, 933) are docstring and comment prose stating that nothing here spawns a subprocess, and the file has no execution call site |
| test-factory-cli.py | NO-EXECUTION | the single match at line 9 is docstring prose about why run-unit-tests.sh classifies this file as unit; there is no execution call site |
| test-factory-config.py | NO-EXECUTION | the single match at line 10 is docstring prose stating nothing here spawns a subprocess; no execution call site exists |
| test-factory-decompose.py | NO-EXECUTION | the two matches (4, 33) are docstring and comment prose asserting this tool is exercised in-process; no execution call site exists |
| test-factory-gh.py | NO-EXECUTION | all 92 matches are ATTRIBUTE ASSIGNMENTS of the form fgh.subprocess.run = fake plus the saved original at line 64; a grep for subprocess.run( or subprocess.Popen( as a CALL returns zero hits, so this file never spawns anything |
| test-factory-integration.py | FIXED-LITERAL-ARGV | line 568 run_tool runs [sys.executable, TOOLS[tool_key]] + args, TOOLS being a module constant map and args caller literals; the python3 -c cases (1307, 1407, 1462, 1508, 1553, 1604) pass source strings written in this file |
| test-factory-land.py | NO-EXECUTION | the two matches (5, 242) are docstring and comment prose stating nothing here spawns a subprocess or touches a real repository; no execution call site exists |
| test-factory-workspace.py | NO-EXECUTION | the single match at line 11 is docstring prose stating nothing here spawns a subprocess; no execution call site exists |
| test-feature-worktree.py | FIXED-LITERAL-ARGV | line 52 run_cli runs [sys.executable, CLI] + args with args supplied literally per case, and _git at line 58 runs ["git"] + args; the fleet.yaml fixture it writes is parsed by the CHILD, so no parsed value enters this file's argv |
| test-gen-decisions-index.py | FIXED-LITERAL-ARGV | line 77 runs [sys.executable, GEN] + list(args or []) with GEN a module constant and args literal flags such as --stdout; the DECISIONS.md fixture reaches the child through cwd and HARNESS_PROJECT_DIR, not argv |
| test-gh-close-gate.py | FIXED-LITERAL-ARGV | line 49 runs ["bash", GATE] with the command under test on STDIN inside a JSON payload; the hostile command strings this file exercises are therefore data, never argv |
| test-gh-cost-log.py | NO-EXECUTION | all 13 matches are attribute rebinds of gh_cost_log.subprocess.run plus the saved original at line 41; a grep for subprocess.run( or subprocess.Popen( as a CALL returns zero hits, so no process is ever spawned |
| test-gh-sync.py | FIXED-LITERAL-ARGV | line 121 runs [SYNC] + args with SYNC a module constant and args literal subcommands; the fake gh binary is injected via the GH_SYNC_GH env var and the BRIEF and plan fixtures are parsed by the child |
| test-harness-yaml.py | FIXED-LITERAL-ARGV | line 309 runs [sys.executable, "-c", "import harness_yaml"], a literal source string, and line 376 uses the same construction; the malformed YAML fixtures are read by the child from disk |
| test-hooks-install.py | FIXED-LITERAL-ARGV | lines 218, 222, 223, 235 and 236 use shell=True, so the executable is the whole command string — and each is a module constant declared at lines 57-59 in this file's own source. Those constants are separately asserted to appear verbatim in SKILL.md, but the value executed is the literal, never a string read out of the document. Every other site is literal git argv |
| test-inflight-registry.py | FIXED-LITERAL-ARGV | line 368 runs [sys.executable, CLI, "list", "--root", root] with root a tempdir this file made, and the Popen sites (289, 545, 631) pass python source strings written here. Line 820 counts subprocess.run( occurrences in the module source as an assertion, which is a read, not an execution |
| test-inject-expertise.py | FIXED-LITERAL-ARGV | line 53 runs [SCRIPT] with the hook payload on stdin as bytes; SCRIPT is a module constant and no argument is appended |
| test-layout-migration.py | FIXED-LITERAL-ARGV | line 368 runs [_CHECK_STATE] with cwd set to the fixture tree; the executable is a module constant and argv carries nothing else |
| test-lead-stop-and-wake.py | NO-EXECUTION | the single match at line 24 is docstring prose stating this file is stdlib only with no subprocess; it reads the playbook text off disk and asserts on it |
| test-merge-gitignore.py | FIXED-LITERAL-ARGV | line 23 runs the command list built at lines 20-22 from str(SCRIPT), str(project) and an optional literal --check flag; project is the fixture directory this file created |
| test-merge-settings.py | FIXED-LITERAL-ARGV | lines 128 and 137 run [sys.executable, SCRIPT, tmp] and the same plus a literal --check; SCRIPT is a module constant and tmp is this file's own tempdir |
| test-no-distribution.py | FIXED-LITERAL-ARGV | line 39 runs ["git", "-C", ROOT, "ls-files"]; ROOT is derived from this file's own path and every other element is a literal |
| test-observations-merge.py | FIXED-LITERAL-ARGV | line 62 run_apply runs [sys.executable, CLI, "apply", "--file", file_path, "--entries", entries_path] over fixture paths this file wrote; the Popen race at 223 and 227 reuses that construction |
| test-omp-hooks.py | FIXED-LITERAL-ARGV | line 11 runs ["bun", "test", str(TEST)] where TEST is a module constant path; nothing is parsed into argv |
| test-orchestrator-playbook.py | NO-EXECUTION | the single match at line 10 is docstring prose stating stdlib only, no subprocess; the file reads PLAYBOOK_PATH and asserts on the text |
| test-plan-merge.py | FIXED-LITERAL-ARGV | line 120 run_apply runs [sys.executable, CLI, "apply", "--file", file_path, "--proposal", proposal_path] over fixture paths this file created; the Popen race at 218 and 222 reuses it. The plan text is read by the child |
| test-post-merge-sweep.py | FIXED-LITERAL-ARGV | the sweep is driven as ["bash", sweep] (232, 428, 471, 508, 545, 578, 661, 684) and ["bash", mutated_path] (443, 601, 708), both paths built by os.path.join off this file's own constants and tempdirs; the git fixture calls are literal argv |
| test-run-unit-tests-kinds.py | FIXED-LITERAL-ARGV | lines 47, 175 and 181 run ["bash", RUNNER, ...] with literal flags. It mutates test_kinds.integration.detect in a fixture harness.json at lines 61-66, but that value is read by the runner, never placed in this file's argv |
| test-sync-agent-adapters.py | FIXED-LITERAL-ARGV | line 34 runs [sys.executable, str(SCRIPT), "--root", str(root), *args]; SCRIPT is a module constant, root is the fixture tree and args are literal flags |
| test-upgrade-config.py | FIXED-LITERAL-ARGV | line 99 runs [sys.executable, SCRIPT, root, "--templates", os.path.join(root, "_templates"), *args] and line 182 the same shape with a literal missing-templates path; every element is a constant, a tempdir or a literal flag |
| test-validate-digest.py | FIXED-LITERAL-ARGV | line 73 runs [VALIDATE, "lead"] and the digest text — extracted from a template markdown by extract_fenced_block — travels on STDIN, not argv. Lines 902, 970, 1191 and 1675 follow the same pattern with a literal persona or --hook flag |
| test-validate-feature-json.py | FIXED-LITERAL-ARGV | lines 220, 230, 323, 347 and 359 run [VALIDATE_CLI] with at most one fixture path this file created; the malformed feature.json content is parsed by the child |
| test-worktree-terminal.py | FIXED-LITERAL-ARGV | lines 395 and 475 run [sys.executable, "-c", script] where script is a source string built in this file, and lines 271 and 281 run literal git argv against fixture repos this file created |
| verify-context-watch-live.py | FIXED-LITERAL-ARGV | line 221 runs [sys.executable, context_watch_path, "--projects-dir", projects_dir, agent_id]; projects_dir and agent_id are CLI arguments and context_watch_path is derived from this file's own location. The transcript JSONL it parses feeds the independent recomputation only |
| wayfind.py | TEXT-DERIVED-ARGV | line 66 gh_json runs [ghi.gh_bin()] + args, line 83 the same, and line 170 runs [ghi.gh_bin(), "issue", "edit", str(mapnum), "-R", repo, "--body-file", "-"]. repo is harness.json's github.repo, read and returned by the config loader at lines 55-62. The executable itself is env-or-literal, so it is Q2 and not Q1 that fires |
| worktree_terminal.py | TEXT-DERIVED-ARGV | line 150 runs git ls-tree --name-only <default_branch>:<features_rel> and line 160 git rev-parse <default_branch>:<rel>; default_branch comes from _resolve_default_branch at lines 132-144, which calls feature-worktree.py's resolve_repo and so reads the field out of the parsed fleet.yaml |

**Counts: 11 TEXT-DERIVED-ARGV, 45 FIXED-LITERAL-ARGV, 14 NO-EXECUTION. Total 70.**

## TEXT-DERIVED-ARGV

**Not EMPTY.** Listed as **remaining work**, in two groups, because they are two different risks.

**Group A — a configuration or fleet identifier flowing into a fixed executable's argv (9).** The
executable is always a literal or an env var, and the value is a repo slug, a branch name or a pid:

- `board_lifecycle.py:1003` — `harness.json` `github.repo` into `gh label create --repo`
- `check-state.sh:1633` — `harness.json` `github.repo` into a `gh api` path
- `wayfind.py:66,83,170` — `harness.json` `github.repo` into `gh ... -R`
- `check-plan-routes.py:74` — a `plan.yaml` `files:` path into `check-domain.sh --resolve`
- `factory_workspace.py:103,129,130` — `fleet.yaml` `default_branch` into `git checkout`/`reset`
- `feature-worktree.py:125,289` — `fleet.yaml` `default_branch` into `git worktree add`/`rev-parse`
- `worktree_terminal.py:150,160` — `fleet.yaml` `default_branch` into `git ls-tree`/`rev-parse`
- `post-merge-sweep.sh:215` — a `fleet.yaml` repo name into `feature-worktree.py --repo`
- `inflight_registry.py:159` — the registry JSON's `supervisor_pid` into `ps -p`

**Group B — document text becoming argv (2).** These are the shape closest to the mechanism T-24
deleted:

- `gh-sync.py:775,789,1180` — `brief['feat']`, `brief['phrase']`, `brief['problem']`,
  `brief['goal']`, `task['title']` and `task['body']`, parsed from `BRIEF.md`
  (`gh-sync.py:289`) and `plan.yaml`/`PLAN.md` (`gh-sync.py:305-355`), into `gh issue create`
  argv. This is argv assembled from approval-gated prose.
- `test-check-state.py:2620-2655` — a backticked command string regex-matched out of
  `check-state.sh`'s stdout, `shlex.split` into argv, and executed. A test, and guarded (the
  resolver probe at 2644 refuses unless the resolved root is the fixture), but structurally the
  same move.

### Why this is a finding and not an omission

The audit was run file by file with a provenance test, not a keyword sweep: 17 of the 70 candidates
matched the pattern only in prose or in an attribute rebind, and each was individually checked for
a real call site before being recorded NO-EXECUTION. Recording those as FIXED-LITERAL-ARGV would
have been false, which is why the third verdict exists.

### Recommendation

**Do nothing to Group A now.** Every member passes a list-form `argv` to a fixed executable, so
there is no shell to inject into and a hostile value can at most name a wrong repo or branch. The
identifiers are also already validated at their read sites (`gh-sync.py:201` rejects a `repo`
without a `/`; `inflight_registry.py:131` rejects a non-`int` pid). Recording the class is the
deliverable; hardening it is not this feature's scope.

**Group B deserves a ticket, not a task in FEAT-38.** `gh-sync.py` is the one production script
that puts document prose into a command line, and the mitigating facts are that the argv is a list
(no shell), the values land as `--title`/`--body` operands rather than as a program name, and
`BRIEF.md` is approval-gated. What is genuinely unproven is whether a `BRIEF.md` title containing a
leading `-` is taken by `gh` as a flag. That is one test case, and it belongs to whoever owns
`gh-sync.py`, not to this note.

### Open questions

- **Q-A (non-blocking):** `test_kinds.<kind>.cmd` is a whole command line in configuration with no
  executor under `bin/`. Its executor is an agent or a CI step. Whether that is acceptable is an
  operator question and is out of scope here.
- **Q-B (non-blocking):** the filter's exclusion list names "git output" but is silent on the
  captured stdout of a harness script. `test-check-state.py` was judged TEXT-DERIVED-ARGV on the
  strict reading. A reader who treats sibling-script stdout as an excluded provenance would score
  it FIXED-LITERAL-ARGV and Group B would hold one member.
