# UI Review (Mode B) — CLI/hook text surface — cycle 7

`review_sha 894adc0f08c71c108ef8432f1f7a3cc8a2a763c0`. c6 interrupted before a lead verdict (ABSENT);
its note read only as a hypothesis set, everything below re-derived from source and live execution
at the pin, in a fresh `/tmp/mgc7` fixture tree (`/tmp/mgc6*` fixtures from c6 no longer exist).

**Visual/dark-light/rendered-a11y axes: N/A.** No `DESIGN.md`, no rendered markup, no colour, no
theme anywhere in this diff — the entire surface is stdout/stderr text from Python/Bash CLIs and a
JSON `permissionDecisionReason` string a hook host reads programmatically, never rendered as UI.
Decided, not skipped.

## Headline

**New this cycle, not found by c0–c6:** `gh-sync.py:_build_entry_recovery_notice`'s non-era branch
unconditionally tells the operator the merge is cleared by `gh-sync.py open`, but for a real,
reachable feature state the actual merge gate requires `recover-terminal` instead — the two
messages contradict each other for the identical feature, proven by running both live. Following
the wrong advice creates spurious GitHub sub-issues on already-completed work, which is exactly the
harm `recover-terminal` exists to prevent. **`must_fix`, severity high.**

Item 3 (the row-11 placeholder-naming DENY): reachable, confirmed **pre-existing**, not introduced
by 894adc0f. Non-gating, consistent with c6 and with `harness-code-reviewer`'s independent c7 trace
(`agent://` note `review-harness-code-reviewer-c7.md`, which dates the pattern to `4338ee44`).

## merge-gate.py message table — every row captured live (`ROOT=/tmp/mgc7`)

| # | Trigger | Rendered literal | Names subject? | Remedy correct? |
|---|---|---|---|---|
| 1 | non-merge command, sync true | *(silent, exit 0)* | n/a | n/a |
| 2 | merge command, sync false | *(silent, exit 0)* | n/a | n/a |
| 3 | unreadable/malformed `harness.json` | *(silent, exit 0)* | n/a | n/a |
| 4 | sync true, no record matches resolved branch | *(silent — ALLOW)* | n/a | n/a |
| 5 | matched record, `build_entry="opened"` | *(silent — ALLOW)* | n/a | n/a |
| 6 | `GH_BIN=/nonexistent/gh`, `gh pr merge 123`, no record | stderr: `merge-gate: could not verify this merge - the head branch could not be resolved through gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch main owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).` | names the gh error + local branch | n/a, ALLOW |
| 7 | matched record, feature basename `BUG-1030-stale-anchor-write-hazard` in `BUILD_ENTRY_ERA_EXEMPT` | stderr: `merge-gate: BUG-1030-stale-anchor-write-hazard predates the build-entry receipt (feature_schema.BUILD_ENTRY_ERA_EXEMPT), so this merge is allowed. Its terminal receipt is created only by an explicit operator-approved gh-sync.py recover-terminal /private/tmp/mgc7/root_exempt/.harness/repo-a/features/BUG-1030-stale-anchor-write-hazard --yes.` | yes | yes — full realpath + `--yes` |
| 8 | owing record, `plan.yaml status: review` → `recovery_command_for`="recover-terminal" | stdout DENY: `merge-gate: FEAT-200-owing records github.build_entry=absent, so no Build entry receipt exists for it. This merge is denied until python3 .claude/skills/harness/bin/gh-sync.py recover-terminal /private/tmp/mgc7/root_owing_terminal/.harness/repo-a/features/FEAT-200-owing --yes records one.` | yes | yes |
| 9 | owing record, `plan.yaml status: planning`, no done tasks → "open" | stdout DENY: `merge-gate: FEAT-500-open-recovery records github.build_entry=absent, so no Build entry receipt exists for it. This merge is denied until python3 .claude/skills/harness/bin/gh-sync.py open /private/tmp/mgc7/root_owing_open/.harness/repo-a/features/FEAT-500-open-recovery records one.` | yes | yes — correctly omits `--yes` |
| 10 | owing record, `github.repo: ""` (unpinned) | stdout DENY: `merge-gate: FEAT-200-owing records github.build_entry=absent, and this project has github.sync true with github.repo NOT pinned, so the mirror records nothing here and no receipt can ever be written for it (D-09). NO COMMAND CLEARS THIS BY ITSELF. Pin github.repo in /tmp/mgc7/root_unpinned/.harness/harness.json to the value of gh repo view --json nameWithOwner -q .nameWithOwner, or set github.sync to false, and then re-run the Build entry.` | yes | yes — both remedies real |
| 11 | internal exception before `feat_dir` resolved | stdout DENY: `merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge.` | **NO** — literal placeholder seed | NO command at all |

Fixture provenance: rows 1–5, 7–10 built via the `Write` tool under `/tmp/mgc7/root_*` (`bash`
output-redirects are blocked for this read-only role — confirmed by the `bash-write-guard`, so
fixtures went through `Write`, execution through `bash` stdin-redirect, which is unblocked) —
`.harness/harness.json` + `.harness/repo-a/features/<id>/{feature.json,plan.yaml}`, `branch` set to
`feature-branch` to match `git merge feature-branch`'s resolved head. Row 6 used `gh pr merge 123`
+ `GH_BIN=/nonexistent/gh`. Row 8/9's recovery commands checked against `gh-sync.py --help`'s usage
line (`open|start-task|abandon|ship|backlog|record-pr|status|recover-terminal <feature-dir> ...
[--yes]`) — both printed forms are real, runnable invocations. Row 11: two independent executed
triggers, below.

## Item 3 — the row-11 placeholder DENY, re-derived myself

**(a) Reachable at the pin — yes, TWO independent live reproductions:**
1. `driver_exc.py`: `os.chdir()` into a directory, `os.rmdir()` it out from under the process, then
   `runpy.run_path` the gate in-process — `os.getcwd()` raises `FileNotFoundError` inside
   `main()`'s `head_branch(command, os.getcwd(), ...)` argument evaluation, before `feature_for` is
   ever called. Captured live: the exact placeholder DENY above.
2. **New, more realistic trigger:** `PATH=/opt/homebrew/bin python3 merge-gate.py ... ` (excludes
   `/usr/bin`, where `git` lives on this host) with stdin `{"command": "gh pr merge abc"}` (no
   digit → `head_branch` calls `local_branch(cwd)` directly). `local_branch`'s
   `subprocess.run(["git", ...])` has no `try/except` (unlike `gh_head`, which catches `OSError`
   explicitly), so a `git` binary unresolvable via `PATH` raises before `feat_dir` is set. Captured
   live: the identical placeholder DENY. This shows the asymmetry is structural — `gh_head` is
   defended against a missing `gh`, `local_branch` is not defended against a missing `git`, in the
   same function.

**(b) Present at the parent — yes.** `git show 894adc0f^:.claude/skills/harness/bin/merge-gate.py`:
`local_branch`, `head_branch`, `feat = "this feature"`, and the terminal
`except Exception: deny(f"...{feat}'s...")` are present and byte-identical to the pin (confirmed by
full-file diff: `git diff 894adc0f^..894adc0f -- merge-gate.py` touches only `feature_for` and
`main`'s `document is None` branch — the exception-fallback block is outside every changed hunk).

**(c) Therefore pre-existing, not introduced by 894adc0f.** Non-gating for this pin's diff.
`harness-code-reviewer`'s independent c7 note traces the pattern back further, to `4338ee44`
("[harness:t-05] gate merges on Build-entry receipt") — this feature's own first cycle, not legacy
code from outside BUG-1309. Advisory only: fails closed (deny, not allow), and an environment
missing `git` on `PATH` while still running Bash-gated PreToolUse hooks is a badly broken host by
itself. Carried forward, not re-opened as a fresh gate.

## New finding — `_build_entry_recovery_notice` names the wrong remedy (severity: HIGH, must_fix)

`gh-sync.py:1379-1389`, the **non-era** branch (reached from `_build_entry_preflight` on every
`start-task` when `entry == "recovery-required"` and the feature is not era-exempt) is a static
string with no call to `feature_schema.recovery_command_for` — unlike every sibling site in this
same feature (the era branch three lines above it, `_build_entry_preflight`'s own `refuse()`
branches, `merge-gate.py`'s deny, `check-state.sh`'s INV-37):

```
print(f"gh-sync: build entry is recovery-required for {realpath(feat_dir)}; "
      f"Build proceeds, the MERGE is refused until gh-sync.py open records opened", file=sys.stderr)
```

**Executed proof of the mismatch.** Built a feature at `plan.yaml status: building` with one task
already `status: done` (T-01) and `build_entry: recovery-required`, not era-exempt:
- `gh-sync.py._build_entry_recovery_notice(feat_dir, feat)` prints (captured live, stderr):
  `"gh-sync: build entry is recovery-required for /private/tmp/mgc7/gs_recovery_notice_repro; Build
  proceeds, the MERGE is refused until gh-sync.py open records opened"`.
- `feature_schema.recovery_command_for(feat_dir)` — the SAME classifier `merge-gate.py`'s own deny
  uses — returns `'recover-terminal'` for the identical directory (task-done triggers it, per
  `feature_schema.py`'s own docstring).
- Built the identical feature/state as a merge-gate.py fixture and ran it: DENY reads `"...This
  merge is denied until python3 .claude/skills/harness/bin/gh-sync.py recover-terminal
  /private/tmp/mgc7/root_mismatch/.harness/repo-a/features/FEAT-9200-inflight-recovery --yes
  records one."` — **the two operator-facing messages name opposite commands for the same feature
  in the same state.**

**Concrete harm if followed.** `cmd_open`'s `_open_sync_task` (gh-sync.py:1171-1181) only skips a
task that is `abandoned` or already has a recorded issue (`task["id"] in rec["issues"]`) — a `done`
task with no recorded issue (exactly this state, since the earlier `open` run that set
`recovery-required` stopped before completing) gets a **real GitHub sub-issue created for already-
finished work** — precisely the outcome `recover-terminal`'s docstring says it exists to avoid
("Creates ZERO task sub-issues"). This is not a refusal-blocking message (Build proceeds either
way), but it is the operator's only advance signal for what will clear the merge gate, and it is
wrong for a realistic and reachable subset of `recovery-required` states.

**Coverage.** `tests/integration/test-gh-sync.py` has exactly one case touching this branch, `"T-04
era recovery-required does not claim a refusal"` — the **era** arm only. No case exercises the
non-era arm's wording against a task-done/late-station fixture; confirmed by grep
(`recovery-required` appears at :3440, :3624 only). Prior UI-1 (c0/c2, LOW, still open — the
non-era command lacks the `feat_dir` path argument, cosmetic) audited this exact line for
copy-pasteability but never checked the command *choice* against `recovery_command_for`; fixing
UI-1 by making this branch call the same classifier every sibling site already uses would resolve
both findings together.

## Silent-success paths (item 4)

Rows 1–3: gate disabled/misconfigured, fail-open-and-silent — matches this feature's own DEC-138
framing. Rows 4–5: the ordinary passing-merge case (no record owed, or receipt already held) —
correctly silent; printing on every clean merge would be pure noise. Not a gap.

## Terminology consistency (item 5)

Same concept ("a Build-entry receipt exists/is owed") renders in three surface forms across
`merge-gate.py` alone: `build-entry receipt` (rows 6, 7), `Build entry receipt`/`Build entry` (rows
8–10), `Build-entry receipt` (row 11, matching the module docstring). Cosmetic — no message is
ambiguous — but a real grep-fragility nit, not gating. `harness-code-reviewer`'s c7 note independently
carries the same-shape finding for the DEC-138 stderr string ("owes no build-entry receipt" wrongly
worded at the compliant-record call site) as `[low]`, consistent with this reading.

## gh-sync.py / check-state.sh / post-merge-sweep.sh — operator text the diff changes

- `check-state.sh` INV-37 (new at this pin, confirmed absent at `894adc0f^`): both branches call
  `feature_schema.recovery_command_for(_fp37)` and name `gh-sync.py open <path>` or `gh-sync.py
  recover-terminal <path> --yes` correctly discriminated. No live gap found by source read.
- `post-merge-sweep.sh`'s retention SKIP message (`:222-232`) hardcodes `recover-terminal ... --yes`
  with **no** call to `recovery_command_for` — looked like the same class of bug as the finding
  above, so I checked it live rather than filing on the pattern alone. **Disproven by execution:**
  ran the real sweep (via the integration test's own fixture helpers, imported by path) against a
  non-era, non-terminal-station (`planning`) feature with an owed receipt — the retention branch
  **never fires** (the worktree isn't removal-eligible yet, so the receipt check is never reached).
  Ran it again with the plan at a terminal station (`Done`) — the branch fires, and
  `recovery_command_for` independently agrees the answer is `recover-terminal` for that state, since
  reaching this code path already requires the plan to be at a station that makes `recovery_command_for`
  return exactly that. The hardcoding is safe by construction here, unlike `gh-sync.py`'s notice
  above (reachable from *any* station via `start-task`). No finding.

## Verdict rationale

One new `must_fix` (severity high): `gh-sync.py:_build_entry_recovery_notice`'s non-era branch names
the wrong recovery command for a reachable, executable feature state, contradicting `merge-gate.py`'s
own gate and risking spurious GitHub sub-issue creation on completed work if followed. Item 3's
placeholder-naming DENY is reachable (two independent live triggers) but confirmed pre-existing —
advisory, carried forward. Silent-ALLOW paths are the correct shape. Terminology drift is cosmetic.
`post-merge-sweep.sh`'s look-alike hardcoding was checked live and found safe by construction — not
a finding.
