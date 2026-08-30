# Security review — FEAT-38-decisions-current-knowledge — ship panel

**Verdict: PASS.** The deletion closes a real, well-guarded but structurally unsound hole
(document-driven `git`/`grep` execution) and I found no surviving path for `DECISIONS.md` text, or
any parsed document/config, to reach a subprocess argv, `eval`, or shell in the reviewed tree. All 11
`TEXT-DERIVED-ARGV` rows I own are correctly labelled. No must-fix findings.

All work below is measured against `635cd3ba` via `git show <sha>:<path>` / `git ls-tree -r`; no file
read from the worktree directly, no HEAD move, no source touched.

## 1. The 11 `TEXT-DERIVED-ARGV` rows — independently re-derived

Every row: **CORRECT**. All 11 pass a value from a parsed document/config into a **list-form**
`subprocess.run`/`_run_git` call (never `shell=True`), so there is no shell to inject into — the
residual is argument-content, not command-injection.

| # | Site | Provenance | Argv shape | Exposure |
|---|---|---|---|---|
| 1 | `board_lifecycle.py:1003` `_ensure_abandoned_label` | `harness.json` `github.repo` via `_own_repo`/`_resolve_board`; CLI override validated against fleet.yaml's known-repo list at `_resolve_board:314` before use | `[gh_bin, "label", "create", ..., "--repo", repo_name, ...]` | real but low — value is config-derived and, on the override path, allowlist-checked before reaching argv |
| 2 | `check-plan-routes.py:74` `resolve_agents` | `plan.yaml` task `files:` entries | `[CHECK_DOMAIN, "--resolve", path]` — becomes `HARNESS_RESOLVE_PATH` **env var**, never re-parsed as argv (`check-domain.sh:71`) | read-only route lookup, no execution downstream |
| 3 | `check-state.sh:1633` INV-30 | `harness.json` `github.repo`, **no shape validation before use** (unlike `wayfind.py`/`gh-sync.py`, which check the value contains `/`) | `%s`-formatted into a REST **path string**: `"repos/%s/milestones?..." % _repo30`, still one list argv element | see finding F-1 below — worst-shaped of the 11 |
| 4 | `factory_workspace.py:103,129,130` | `fleet.yaml` `default_branch` | `["checkout", default_branch]`, `f"origin/{default_branch}"` | operator-config only |
| 5 | `feature-worktree.py:125,289` | `fleet.yaml` `default_branch` | `["worktree","add","-b",branch,dest,default_branch]`, `f"{default_branch}:{rel}"` | operator-config only |
| 6 | `gh-sync.py:775,789` (current line numbers 773/790) | `BRIEF.md`/`plan.yaml` prose (`brief['phrase']`,`brief['problem']`,`brief['goal']`,`task['title']`,`task['body']`) | `["issue","create","--repo",repo,"--title",title,"--body",body,...]` | see finding F-2 — closest in shape to the deleted mechanism, but this file's diff here is **comment-only** (DEC-number fixes), pre-existing and out of FEAT-38's scope |
| 7 | `inflight_registry.py:159` | registry JSON `supervisor_pid` | `["ps","-o","lstart=","-p",str(pid)]` | narrow — `pid` is int/positive-validated at `:131` before use, matches the row's own note |
| 8 | `post-merge-sweep.sh:215` | `fleet.yaml` repo name, or literal `"harness"` | `["python3",...,"feature-worktree.py","remove","--repo",repo_arg,"--id",wt_id]` | operator-config only |
| 9 | `test-check-state.py:2620-2655` | `check-state.sh`'s own stdout (backticked command), `shlex.split` then executed | `[sys.executable] + shlex.split(...)` | test-only, guarded by a resolver probe that refuses unless the resolved root is the fixture (`:2644`) — matches the row's "mitigated but not eliminated" framing exactly |
| 10 | `wayfind.py:66,83,170` | `harness.json` `github.repo`, via `cfg()` | `[ghi.gh_bin()] + args`, `[...,"-R",repo,"--body-file","-"]` (body itself travels on **stdin**, not argv) | operator-config only |
| 11 | `worktree_terminal.py:150,160` | `fleet.yaml` `default_branch` (via `feature-worktree.py`'s own `resolve_repo`) | `["ls-tree","--name-only",f"{default_branch}:{features_rel}"]`, `["rev-parse",f"{default_branch}:{rel}"]` | operator-config only |

**F-1 (severity: low)** — `check-state.sh:1633` is the one row of the 11 that embeds the
config-derived value into a **formatted URL-path string** rather than binding it as a discrete
flag value, and it is the only one of the config-repo sites with **no shape check** at the read site
(contrast `wayfind.py:cfg()`'s truthy check and `gh-sync.py:201`'s `/`-required check, both cited by
the research note itself). Concrete scenario: an actor who can already write `.harness/harness.json`
(same trust tier the value's owner already holds — not an escalation) could set `github.repo` to a
string containing `/../` or a stray `&`/`#`, redirecting the `gh api` request to a different path or
appending query parameters within whatever scope the invoking `gh` session's token already has.
Because the token holder is already the actor who could set the value, this is **not** privilege
escalation — it is a data-integrity nicety, not a gate-blocking defect. **Not must-fix.**

**F-2 (severity: info)** — the research note's own line citations for `gh-sync.py` (`775,789,1180`)
are incomplete and one is mismatched:
- Line **741** (`gh api ... -f title={brief['feat']} -f description={desc}`) and line **751**
  (`f'[.[] | select(.title == "{brief["feat"]}") | .number] | first'`, passed as `-q <filter>`) are
  two more genuine `brief['feat']`-into-argv sites the table never enumerates. I checked whether
  line 751's f-string, which interpolates `brief['feat']` **inside a double-quoted jq string
  literal**, is quote-breakable: it is not — `parse_brief` sets `brief['feat'] =
  os.path.basename(feat_dir)`, and every feature directory name this codebase creates is
  slug-constrained by `feature-worktree.py`'s `_ID_RE = r"^(FEAT|BUG)-[0-9]+[a-z0-9-]*$"`
  (alnum/hyphen only — no `"`, no backtick, no `$`). So the theoretically-worse "break out of the
  jq string" shape is not reachable given that provenance; only `--title`/`--body`'s genuinely-free
  BRIEF prose (`brief['phrase']`, `brief['problem']`, `brief['goal']`) carries residual risk, and
  that is already the row the table cites.
- The `1180` citation does **not** support the "brief/task text into argv" claim it is attached to:
  that line is inside `cmd_backlog`, where `title` comes from `item.partition(":")` over a CLI
  argument the **main session** supplies at the briefing step (`sys.argv`) — a provenance the
  audit's own Q2 filter explicitly **excludes** from `TEXT-DERIVED-ARGV`. This is a citation
  accuracy defect in the research note, not a security defect in the code; it does not change the
  file's verdict (already correctly `TEXT-DERIVED-ARGV` on the strength of lines 773/790).
- `gh-sync.py`'s diff at this pin is **comment-only** (DEC-number renumbering after the fold — `git
  diff 7ebfc9eb..635cd3ba` shows 12 lines, all inside docstrings/comments). This file's behavior is
  untouched by FEAT-38 and is correctly out of this feature's remediation scope per the contract.

### Backlog recommendation — worst first, by real exploitability

1. **`gh-sync.py` `--title`/`--body`** (Group B, rows 6 above): the one production site where BRIEF
   prose reaches an external service's argv. Add the one test case the research note already
   identifies — a `BRIEF.md` H1 phrase or SC body beginning with `-` — and confirm `gh`'s flag
   parser cannot mis-consume it. Mitigating facts already in place: list-form argv (no shell),
   values land as flag *values* not flag names, `BRIEF.md` is approval-gated. Estimate: low
   severity, but the highest-value backlog item of the eleven because it is genuinely
   free-text-shaped, not slug-shaped.
2. **`check-state.sh:1633`** (F-1): switch the `%s`-into-URL-path pattern to a bound `gh api`
   template placeholder (`gh api repos/{owner}/{repo}/milestones...` uses its own `-f`/`{}`
   substitution) or add the same `/`-shape check `wayfind.py`/`gh-sync.py` already apply to
   `github.repo` before formatting it into a path. Severity: low, no escalation path, defense in
   depth only.
3. **Correct the research note's `gh-sync.py` citation set** (F-2): drop line `1180`, add `741` and
   `751`, and record the `os.path.basename(feat_dir)` provenance of `brief['feat']` so a future
   reader does not have to re-derive that the jq-quote-breaking shape is closed by slug validation.
   Severity: info — documentation-of-the-audit accuracy, not a code defect.
4. Every remaining Group-A site (rows 1,2,4,5,7,8,10,11 above): **no action.** Config write access
   (`fleet.yaml`, `harness.json`) is already the same trust tier the values would need to abuse, and
   the two most narrowable inputs (`pid`, plan-route paths) are already type/shape-checked at their
   read sites.

**REQ-10's residual is correctly characterised as non-empty, mitigated, out of this feature's scope.**
None of the above is a must-fix for this ship.

## `test_kinds.<kind>.cmd` — independently re-derived (SC-17's decisive case)

I re-ran the sweep myself rather than trusting the research note's claim, searching every `.py`/`.sh`
under `.claude/skills/harness/bin/` at the pin for `test_kinds` and for `"cmd"`/`'cmd'`/`.cmd`
substrings (Python string search, not shell grep), and separately checked `.github/workflows/tests.yml`
and the `.claude`/`.github` hook surfaces:

- **`run-unit-tests.sh:108`** reads only `test_kinds.integration.detect` (a pipe-separated glob),
  set-compares it against its own two literal bash arrays, and runs only what those arrays name
  (`python3 "$BIN_DIR/$s"`, `:149`). Nothing parsed from `detect` reaches argv.
- **`check-state.sh`** reads `cj` (parsed `harness.json`) for `test_kinds`-scoped INV checks; zero
  hits for `"cmd"`/`'cmd'`/`.cmd` anywhere in the file.
- **`upgrade-config.py:209-211`** is the only script that reads `test_kinds.*.cmd` at all, and only
  to format it into a preserved-value diagnostic string (`f"test_kinds.{k}.cmd = {v.get('cmd')!r}"`)
  — never executed.
- **`.github/workflows/tests.yml`** mentions `test_kinds` once, in a comment, and contains no
  `"cmd"` reference at all.
- No other `bin/` script references `test_kinds` or a `cmd` key sourced from `harness.json` (the
  `dest="cmd"` hits found are unrelated `argparse` subparser names in `board_lifecycle.py`,
  `feature-worktree.py`, `expertise-merge.py`, `observations-merge.py`, `plan-merge.py`).

**Conclusion, independently confirmed: `test_kinds.<kind>.cmd` has no in-tree executor.** It is a
complete command line at rest in configuration, whose only reader in this tree treats it as opaque
text. **The trust boundary is external**: whatever agent, human, or CI step is told to run the printed
`cmd` string is the actual execution boundary, and it sits entirely outside `.claude/skills/harness/bin/`
— not a defect in this diff, and Contract point 8 / Q-A already marks this as a non-blocking operator
question, correctly not gated here.

## 2. Deletion verification — the hole is actually closed

- `git ls-tree -r --name-only 635cd3ba` (1819 entries, counted in Python): **zero** entries containing
  `check-decision-claims`. Both `check-decision-claims.py` and `test-check-decision-claims.py` are
  absent from the reviewed tree.
- Read the pre-change script at `99bb52c` to characterise exactly what was removed: a well-guarded
  but structurally-unsound mechanism — `<!-- claim: <cmd> :: <expected> -->` markers executed via
  `shlex.split` + list-form `subprocess.run`, gated by an allowlist (`git`/`grep` only, read-only git
  subcommands, no pager-launch option, isolated `GIT_CONFIG_*`, no grep file/device reads). The
  guard was real, but the design itself — build-and-run a command sourced from prose — is exactly
  the class this feature exists to eliminate; a future marker or a bug in the allowlist logic would
  have been a documentation-triggered execution path. Deleting it removes that class outright rather
  than trusting the guard to hold forever.
- Scanned every tracked `.py/.sh/.md/.json/.yaml/.yml` file (1744 candidates, all read via `git show`,
  all counting done in Python — the documented `/usr/bin/grep` hazard was avoided throughout) for
  `check-decision-claims`/`check_decision_claims` and for `<!-- claim:` markers. Hits outside the
  feature's own `notes/` directory: only `.harness/notes/grilling-remove-executable-claims-2026-08-29.md`
  (the planning record of the removal decision itself — prose, not live code).
- `.harness/harness/docs/DECISIONS.md` and `DECISIONS-INDEX.md`: **zero** `<!-- claim:` markers,
  **zero** `check-decision-claims` references, and **zero** `ALLOWED_FIRST_TOKENS`/
  `ALLOWED_GIT_SUBCOMMANDS` self-references (the grilling note's own pre-flight fact — verified
  independently, not taken on trust).
- `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` bash arrays: no
  `test-check-decision-claims.py` entry in either. `.harness/harness.json`'s `test_kinds.integration.detect`
  gained exactly one entry (`test-check-decision-anchors.py`) and lost none — consistent with T-25's
  scope.
- **No surviving path found** by which `DECISIONS.md` text, or any other parsed document, reaches a
  subprocess argv, `eval`, or a shell — directly, via the index generator, via `run-unit-tests.sh`,
  via a hook, or via CI.

## 3. Sweep of the shared file set — explicit verdict per area

| Area | Verdict | What I measured |
|---|---|---|
| `run-unit-tests.sh` (T-24, array entry) | **Nothing to report.** | Confirmed no claims-test entry remains in either bash array; `detect` string is set-compared only, never executed (re-derived above). |
| `check-decision-claims.py` + test (T-24, deleted) | **Deletion verified complete** (§2). | Accepted, signed cost per Contract 3 — not re-reported as a gap. |
| `gen-decisions-index.py` (T-06/T-10 + SIMPLIFY) | **Nothing to report.** | Read the full 311-line file at the pin: pure regex text transform over `DECISIONS.md` (heading/ref/tag extraction), writes only to the fixed literal `INDEX_PATH` or stdout. No `subprocess`/`eval`/`os.system`/`shell=` anywhere — it is correctly absent from the 70-file candidate enumeration. The diff (`164` lines changed) removes the amendment/supersession regex machinery (`AMEND_HEADING_RE`, `SUPERSESSION_VERB_RE`, `compute_amendments`) to match DECISIONS.md's new no-amendment shape; no new parsing surface introduced. |
| `check-decision-anchors.py` + test (RETAINED, frozen) | **Frozen and verified byte-identical to `99bb52c`** — sha256 `adb9a648cf…` and `7a4e0ba1af…`, both match the dispatch's pinned hashes exactly (measured, not assumed). Per Contract 2, not re-reviewed for content or re-reported for its stale docstring reference. |
| `.harness/harness.json` (T-25, one `detect` entry) | **Nothing to report.** | Diff is exactly the one array-append shown above; `test_kinds.*.cmd` re-derived independently in §"decisive case" — no executor. |
| `board_lifecycle.py` (earlier tasks) | **Nothing to report.** | 6-line diff is entirely comment text (`DEC-186`→`DEC-203` renumbering after the fold). The `_ensure_abandoned_label` argv site (row 1) is unchanged behavior; `repo_name` is allowlist-checked on the override path before reaching argv. |
| `check-domain.sh` (earlier tasks) | **Nothing to report.** | 1-line diff is a comment fix (`DEC-171 am.1`→`DEC-171`). No behavioral change; `--resolve <path>` binds the path to an env var, never re-parsed as argv, so no argument-injection surface. |
| `.github/workflows/tests.yml` (earlier tasks) | **Nothing to report.** | 2-line diff is comment-only (`DEC-171 am.1`→`DEC-171`, `DEC-192`→`DEC-203`). Trigger config (`pull_request` + `push`, never `pull_request_target`) is unchanged and safe; pre-existing, not this feature's surface. |
| `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md` (T-27/T-28, fold) | **Nothing to report** beyond §2's marker sweep. | Scanned the full rewritten text for secret-shaped strings (AWS keys, `api_key=`/`secret=`/`password=` patterns, GitHub PATs, PEM private-key headers) — zero hits. Also ran the same four patterns across the **entire** `7ebfc9eb..635cd3ba` diff (1.5 MB) per my own Expertise P-14 — zero hits. |

## STRIDE — what deleting the checker does to tampering detection

**Tampering (documentation integrity): unmitigated, accepted, signed.** The claims checker was the
only mechanism that re-verified a decision's *semantic* claim ("this constant equals this value",
"this file still says X") against live repository state on every run. Its removal means a citation
that was true when written can go silently false as the code changes — semantic citation rot has no
detector after this feature. This is **exactly** the Contract-3 accepted cost (`.harness/notes/
grilling-remove-executable-claims-2026-08-29.md`, "Facts I verified", plus the BRIEF's Q1 ruling) —
recorded here as required by my own dispatch, not raised as a finding, and not added to `must_fix`.

**What is *not* lost:** `check-decision-anchors.py` (frozen, retained) still catches *structural* rot
— a citation naming a deleted file or an out-of-range line — with a fixed, self-sourced `["git",
"ls-files"]` argv that the document never touches. The residual gap is specifically: file exists,
line exists, content at that line no longer supports the claim. Precisely that gap, and no more, is
now unverified.

**Everything else the fold touches** (STRIDE across the rest of the diff): no new trust boundary is
crossed. `DECISIONS.md`/`DECISIONS-INDEX.md` remain read by humans and by `gen-decisions-index.py`'s
pure-text-transform path; no new writer, no new network call, no new credential, no new elevation of
privilege was introduced by this feature.

## Summary

No must-fix findings. `severity_max` is `low` (F-1, the `check-state.sh` URL-path formatting gap —
defense-in-depth only, requires an actor already privileged to write `harness.json`). Everything else
is `info` or a correctly-accepted, signed cost. The class-sweep commissioned by this feature (T-29)
did its job: it found a genuinely non-empty `TEXT-DERIVED-ARGV` residual, every row of my eleven is
correctly labelled, and the one decisive `cmd`-in-configuration case (SC-17) has no in-tree executor,
independently confirmed.
