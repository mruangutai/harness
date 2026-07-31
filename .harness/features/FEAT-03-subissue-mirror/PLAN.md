# PLAN — FEAT-03-subissue-mirror

Eight tasks. T-01 makes the `unit` gate able to see `gh-sync.py` at all (it cannot today), T-02
extracts the shared GitHub primitives, T-03–T-06 rewrite the four mirror commands around one
sub-issue per `T-NN`, T-07 adds the missing-parent invariant, T-08 records the reversed contract.

Order: T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08. T-01 and T-02 are independent of each
other; every later task's `verify:` runs through T-01's runner, and T-03–T-06 all edit
`gh-sync.py`, so they are serial.

## Decisions

- **D-01 — the parent is adopted-or-created by `open`, and its number is recorded, never
  discovered.** Precedence, first match wins: (1) `feature.yaml github.parent` already holds a
  number (the orchestrator recorded an adopted wayfinding map issue or absorbed backlog issue — the
  grilling's origins 1 and 2); (2) `--parent <n>` passed on the command line; (3) no parent recorded
  → `open` creates one, titled `<feature-dir-basename> — <human phrase from BRIEF's H1>`, body =
  BRIEF `## Problem` + `## Goal`. Rejected: calling the parent endpoint to find it. That is a READ,
  and DEC-138 makes the mirror write-only; idempotency comes from local receipts, so a discovery
  path would be a second, contradictory source of truth. Consequence a future scan will re-suggest
  and must not: `gh-sync.py` importing `parent_of` is a defect, not a convenience.
- **D-02 — `absorbs:` stops closing anything.** It becomes citation-only: the absorbed numbers stay
  in the task's issue body (already the behaviour at create) and `close-task` closes exactly one
  issue. This **reverses DEC-138 am.1's "they close with it"** and inverts two live assertions
  (`test-gh-sync.py:177-178`). Trade-off, accepted: watchers of an absorbed issue no longer see it
  close automatically, so the only route from "the feature covered this" to "this is closed" is a
  human signature — the same briefing-gated route DEC-138 am.4 uses for residual findings, chosen
  because absorption is normally *partial* (kaya's #315/#209/#309/#312/#305 were each only partly
  covered) and a script must not infer that a partly-covered issue is done.
- **D-03 — one new module `gh_issues.py`, exposing argv builders plus one lookup, not executors.**
  The two callers have deliberately different failure semantics — `gh-sync.py` skips and exits 0 on
  an environmental failure, `wayfind.py` dies exit 1, and `wayfind.py` is dry-run by default. A
  shared executor would have to pick one and would silently give `gh-sync.py` a gate. So the module
  owns the *knowledge* (endpoint shapes, the id-not-number trap, the `GH_SYNC_GH` binary override)
  and each caller keeps its own runner. Underscored filename because it must be importable.
- **D-04 — the `unit` kind becomes a runner (remedy (a)), rather than pinning the mirror SCs to
  inspection.** `unit.cmd` is one script today and `unit.detect` matches zero files here, so an SC
  claiming `evidence: unit` would be proven by a test that never touches `gh-sync.py` — DEC-163's
  gate-that-looks-real-and-does-nothing. Cost: `.harness/harness.json` is dev-ops's domain, so T-01
  is a dev-ops task. Rejected: BRIEF-recorded gap + `verify: inspection` on eight SCs — cheaper to
  write, permanently weaker, and it leaves the next feature with the same blind gate.
- **D-05 — the missing-parent invariant is INV-21 at warn level.** Warn, not violation: the mirror is
  never a gate, and an unrecorded parent is a per-feature bookkeeping gap that a re-run of `open`
  fixes. INV-20 is the warn-level precedent (flows still run). Contrast INV-13, which *is*
  violation-level, because `sync: true` with `repo: null` is a config contradiction that makes every
  sync silently skip.
- **D-06 — every task is `change_type: logic | bugfix | config | docs`.** Those rows of `test_matrix`
  resolve to `unit` only (or `[]`). `feature` and `api` would pull in `functional` and `integration`,
  both `cmd: null`, reintroducing DEC-163's invisible gate through a field value. The work genuinely
  is script logic behind an existing CLI, so this is honest, not gaming — but it is recorded because
  "this adds a subcommand, so it is `feature`" is the obvious wrong call.

## Tasks

### T-01 — make the `unit` gate actually run the bin test scripts
- owner: harness-dev-ops
- change_type: config
- traces: REQ-08, D-04
- files:
  - create `.claude/skills/harness/bin/run-unit-tests.sh`
  - edit `.harness/harness.json` (`test_kinds.unit.cmd`, `test_kinds.unit.detect`)
- intent: `run-unit-tests.sh` is `set -uo pipefail`, `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`, and holds
  an **explicit list** of test scripts to run in order — `test-validate-digest.py`, `test-gh-sync.py`
  — executing each and collecting failures rather than stopping at the first. Before running any, it
  globs `.claude/skills/harness/bin/test-*.py` and **exits 1 naming any script not in the list**, so
  a future test file cannot be silently orphaned by the gate (the failure this task exists to fix,
  one level up). Prints one `PASS`/`FAIL` line per script and a final summary; exit 0 only if all
  passed. In `.harness/harness.json`: set `test_kinds.unit.cmd` to
  `.claude/skills/harness/bin/run-unit-tests.sh`, and append
  `|.claude/skills/harness/bin/test-*.py` to `test_kinds.unit.detect` — the existing globs
  (`tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py`) match zero files in this repo because both
  scripts are hyphenated and live under the hidden `.claude/` tree, so qa's detect step resolves
  `unit` to *missing* and would FAIL. Leave `exclude` unchanged. Do not touch any other key.
- verify:
  - `chmod +x` applied, then `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0, output names
    both scripts as PASS.
  - `python3 -c "import json,glob;p=json.load(open('.harness/harness.json'))['test_kinds']['unit'];print(sorted({f for g in p['detect'].split('|') for f in glob.glob(g,recursive=True)}))"`
    → prints both `test-validate-digest.py` and `test-gh-sync.py`.
  - temporarily `touch .claude/skills/harness/bin/test-orphan.py`, re-run the runner → exit 1 naming
    `test-orphan.py`; delete the file and confirm `git status --porcelain` is clean of it.

### T-02 — extract the three GitHub primitives into one shared module
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-06, D-03
- files:
  - create `.claude/skills/harness/bin/gh_issues.py`
  - edit `.claude/skills/harness/bin/wayfind.py`
- intent: the new module is stdlib-only and holds, with the trap documented **once** in its
  docstring ("the sub-issue and dependency endpoints take an issue's internal `id`, never its
  `number`"):
  - `gh_bin()` → `os.environ.get("GH_SYNC_GH", "gh")`. Both callers route through it, so the fake
    `gh` in `test-gh-sync.py` intercepts helper-built calls too; today `wayfind.py` hardcodes
    `"gh"` in every `subprocess.run`.
  - `internal_id_args(repo, num)` → `["api", f"repos/{repo}/issues/{num}", "--jq", ".id"]`
  - `attach_sub_issue_args(repo, parent, child_id)` →
    `["api", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={child_id}"]`
  - `parent_args(repo, num)` → `["api", f"repos/{repo}/issues/{num}/parent"]`
  - `blocked_by_args(repo, num, blocker_id)` →
    `["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by", "-F", f"issue_id={blocker_id}"]`
  Argv builders only — no `subprocess` execution in the module beyond nothing at all; each caller
  executes with its own runner, because `wayfind.py` dies exit 1 and is dry-run by default while
  `gh-sync.py` skips exit 0 (D-03). `wayfind.py` then: imports the module (prepend
  `os.path.dirname(os.path.abspath(__file__))` to `sys.path`, since the file is invoked as a
  script), and builds **no** endpoint strings itself — `sub_issues()`, `blockers()`, `parent_of()`,
  the `ticket` attach and the `block` edge all pass helper-built argv into the existing `gh_json()`
  / `do()`. Behaviour must be byte-identical: same endpoints, same `-F` forms, same dry-run output.
  `wayfind.py`'s `gh_json()`/`do()` switch from literal `"gh"` to `gh_issues.gh_bin()`.
- verify:
  - `python3 -c "import sys;sys.path.insert(0,'.claude/skills/harness/bin');import gh_issues as g;print(g.gh_bin(),g.internal_id_args('o/r',5),g.attach_sub_issue_args('o/r',1,999),g.parent_args('o/r',5),g.blocked_by_args('o/r',5,7))"`
    → exit 0, prints the five forms above.
  - `! grep -qE 'sub_issues|dependencies/blocked_by|issues/\{num\}/parent|/parent"' .claude/skills/harness/bin/wayfind.py`
    → exit 0 (every endpoint string now lives in the module).
  - `! grep -q '"gh"' .claude/skills/harness/bin/wayfind.py` → exit 0.
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0.

### T-03 — `open` creates one sub-issue per `T-NN` under one recorded parent
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-05, SC-01, SC-05, SC-12, D-01
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent:
  - `parse_brief` also returns `phrase`: the H1's trailing segment — from
    `# BRIEF — <feat-id> — <human phrase>`, take what follows the second em-dash; empty if absent.
  - `load_recorded` reads `parent` from the `github:` block (`^\s*parent:\s*(\d+)`; `none`/absent →
    `None`) plus an `attached:` list of `T-NN` ids (see below), and `save_recorded` writes `parent:`
    and `attached:` alongside `milestone:` and `issues:`. **Both extend — today `save_recorded`
    regexes out the whole `github:` block and rewrites it as milestone+issues, which would delete
    the `parent: none` line this feature's own `feature.yaml` already carries.**
  - `main()` accepts an optional `--parent <n>` for `open`, stripped from argv before dispatch.
  - `cmd_open`: after the milestone step, resolve the parent by D-01's precedence. Adopted (recorded
    or `--parent`) → record it and print `parent #<n> adopted`; none → create the issue with
    `--title "<feat-id> — <phrase or feat-id>"`, `--body` = BRIEF `## Problem` + `\n\n**Goal:** ` +
    `## Goal`, `--label harness`, no milestone; record it **immediately** (DEC-131 crash discipline,
    as the milestone already does) and print `parent #<n> created`.
  - Per task, unchanged: create the issue exactly as today (title, body, `absorbs:` citation,
    derived labels, milestone), record, save. Then **attach it to the parent**: look up the child's
    internal id via `internal_id_args`, then POST `attach_sub_issue_args`. Both calls go through the
    existing `gh()` helper, so a failure is a SKIP exit 0, never a gate. **The attach carries its own
    receipt:** on success append the `T-NN` to `rec["attached"]` and `save_recorded` immediately.
    The idempotency test is per-step, not per-task — a task in `rec["issues"]` skips the *create*, a
    task in `rec["attached"]` skips the *attach*. Without the second receipt, a crash between
    recording and attaching (the failure `gh-sync.py:204-208` memorialises for the milestone) would
    leave a recorded-but-unattached, permanently unreachable sub-issue that no re-run repairs and
    INV-21 cannot see, because the parent *is* recorded. Re-attaching an already-attached child would
    422, which is why the receipt is what gates it rather than a lookup.
  - Do **not** import or call `parent_args`/`blocked_by_args` (BRIEF `## Out of scope`, D-01).
  - In `test-gh-sync.py`, extend the fake `gh` to answer the two new API shapes: a GET of
    `repos/*/issues/<n>` (with `--jq .id`) echoes a **distinct** internal id derived from the
    number, `9000<n>`; a POST to `repos/*/issues/<n>/sub_issues` echoes `{}`. Without this both
    calls fall through to bare `exit 0` with empty stdout and the attach would post an empty
    `sub_issue_id`. Add assertions: parent created and recorded in `feature.yaml`; three sub-issues
    created (unchanged count) and **three** attach POSTs to the parent's `/sub_issues`; every attach
    carries `sub_issue_id=9000…`, i.e. the internal id and **not** the issue number; `--parent 55`
    adopts instead of creating; a re-run creates and attaches nothing. Two more:
    **crash resume** — pre-seed a `feature.yaml` whose `github:` block has `issues: {T-01: 41}` and
    no `attached:` entry for it, run `open`, assert exactly one attach POST for T-01 and no `issue
    create` for it; **round trip both ways** — a `feature.yaml` that already carries `parent: 40`
    still carries it after the per-task `save_recorded` calls, and the issue map survives writing
    the parent.
- verify: `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0, with `ok` lines for
  "parent created and recorded", "three sub-issues attached to the parent", "attach uses internal id
  not number", "--parent adopts", "re-run open creates nothing", "recorded-not-attached task is
  attached on re-run", "pre-existing parent survives per-task saves".

### T-04 — `close-task` closes exactly one issue; `absorbs:` stops closing
- owner: harness-backend-dev
- change_type: bugfix
- traces: REQ-02, REQ-03, D-02
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: delete the `for n in tasks.get(tid, {}).get("absorbs", [])` loop and its two `gh issue
  close` calls from `cmd_close_task` (`gh-sync.py:240-242`). The function closes `rec["issues"][tid]`
  and nothing else; the `parse_tasks` call it only needed for `absorbs` goes away with it. Print,
  after the close, one line naming any absorbed numbers as **left open for the ship briefing** so the
  operator sees where they went. In `test-gh-sync.py`, this is an **inversion of two existing
  assertions, not an addition**: line 177's `close-task closes issue + 2 absorbed` /
  `len(closes) == 3` becomes `len(closes) == 1`, and line 178's `absorbed #12 #14 closed` becomes the
  positive regression guard **`absorbed #12 #14 NOT closed`** — neither number appears anywhere in
  the close log. Do not delete either assertion; a dropped assertion loses the guard.
- verify:
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for "close-task closes
    exactly one issue" and "absorbed #12 #14 NOT closed".
  - `! grep -qE 'len\(closes\) == 3|absorbed #12 #14 closed' .claude/skills/harness/bin/test-gh-sync.py`
    → exit 0.

### T-05 — `cmd_abandon --reason-file`: the second terminal state
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-04, SC-12
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: a **new** subcommand (`gh-sync.py abandon <feature-dir> --reason-file <path>`) wired into
  `main()`'s dispatch and the module docstring's usage block. Missing `--reason-file`, or a path
  that is not a file → `die` (caller error, exit 1). No recorded milestone **and** no recorded
  issues → `skip`. Sequence, all through `gh()` so environmental failure is one SKIP line exit 0:
  1. Post the reason on the parent, verbatim from the path:
     `gh issue comment <parent> --repo <repo> --body-file <path>` — a file path, never an assembled
     string (DEC-138 am.6). No parent recorded → print one line saying the reason was not posted, and
     continue.
  2. Close each `rec["issues"]` value with `state_reason: not_planned`:
     `gh api -X PATCH repos/<repo>/issues/<n> -f state=closed -f state_reason=not_planned`. The enum
     is exactly `completed`/`not_planned`/`duplicate` — `not_doing` is a 422 (DEC-138 am.5), so do
     not invent a value or a label.
  3. Close the milestone: `gh api -X PATCH repos/<repo>/milestones/<n> -f state=closed` (milestones
     take no `state_reason`).
  4. **Leave the parent open.** An adopted parent is someone else's live backlog item, and a fresh
     one is the container the sub-issues' `not_planned` state already explains.
  Do not read or assert on `sub_issues_summary` (eventually consistent, DEC-168). Tests: fake `gh`
  needs a case for `api -X PATCH repos/*/issues/*` echoing `{}`. Assert — one PATCH per recorded
  task issue, each carrying `state_reason=not_planned`; the milestone PATCHed closed; **no** close
  call naming the parent; the comment call uses `--body-file` and the log contains none of the file's
  text; missing `--reason-file` → exit 1; `sync: false` → SKIP exit 0.
- verify: `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for "abandon closes
  3 subs not_planned", "abandon closes the milestone", "abandon leaves the parent open", "abandon
  posts via --body-file", "abandon without --reason-file exits 1".

### T-06 — `ship` closes the parent as well as the milestone
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-04, SC-12
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: `cmd_ship` gains an optional `--body-file <path>` (stripped in `main()`; a non-file path →
  `die`). Order: if `--body-file` is given and a parent is recorded, `gh issue comment <parent>
  --repo <repo> --body-file <path>` (the signed ship review, verbatim — DEC-138 am.6); then close the
  parent (`gh issue close <parent> --repo <repo>`, i.e. `state_reason: completed`, the default —
  distinct from abandonment's icon); then PATCH the milestone closed exactly as today. No recorded
  parent → close the milestone only and print one line saying so; no recorded milestone → `skip`, as
  today. Tests: assert ship closes the parent **and** PATCHes the milestone, in that order; that
  `--body-file` posts once via `--body-file`; and that ship without `--body-file` posts nothing.
- verify: `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for "ship closes
  parent then milestone", "ship --body-file posts once", "ship without --body-file posts nothing".

### T-07 — INV-21: a mirrored feature with no recorded parent
- owner: harness-dev-ops
- change_type: logic
- traces: REQ-07, SC-08, D-05
- files:
  - edit `.claude/skills/harness/bin/check-state.sh`
  - create `.claude/skills/harness/bin/test-check-state.py`
  - edit `.claude/skills/harness/bin/run-unit-tests.sh` (add the new script to the explicit list)
- intent: in `check-state.sh`, after the INV-20 block and before INV-13, add **INV-21 at warn level**
  (`warn.append`, never `bad`): when `harness.json` `github.sync` is true, then for each
  `.harness/features/*/feature.yaml` whose `github:` block has a non-empty `issues:` map and no
  numeric `parent:`, warn naming the feature — the mirror's tasks exist but their container is
  unrecorded, so `ship` and `abandon` cannot close it and `open` will not re-derive it (the mirror is
  write-only, DEC-138). Parse with the same regex-on-text style the file already uses; no YAML
  dependency. It must stay **vacuous when `github.sync` is false**, which is the case in this repo,
  so the check costs nothing here. `test-check-state.py` builds temp dirs and runs
  `check-state.sh` with `CLAUDE_PROJECT_DIR` pointed at each (the script already honours it,
  `check-state.sh:14`), asserting: (a) `sync: true` + `issues: {T-01: 41}` + no `parent` → the INV-21
  note appears and the exit code is unchanged by it; (b) same fixture with `parent: 40` → no INV-21
  note; (c) `sync: false` + issues + no parent → no INV-21 note. Fixtures need whatever minimal
  `.harness/` shape the earlier invariants require to avoid unrelated violations; assert on the
  INV-21 substring, not on the whole output.
- verify:
  - `python3 .claude/skills/harness/bin/test-check-state.py` → exit 0, three cases pass.
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 (the new script is listed, so the
    orphan check passes).
  - `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh` → exit 0 in this repo, no
    INV-21 note (`github.sync` is false).

### T-08 — record the reversed contract in DECISIONS.md
- owner: harness-documentor
- change_type: docs
- traces: REQ-09, SC-11, D-02
- files: edit `docs/harness/DECISIONS.md`
- intent: append **DEC-138 amendment 7** (next free amendment number — am.6 is the last; confirm
  before writing) recording, in the file's existing voice: one sub-issue per `T-NN` under one parent
  per feature; the parent adopted-or-created and **recorded** at `feature.yaml github.parent`, never
  discovered; `close-task` closes exactly one issue and **`absorbs:` no longer closes anything** —
  explicitly superseding am.1's "they close with it", with the reason (partial absorption is the
  norm; a work item changes state through a human signature); `ship` closes parent + milestone,
  `abandon` closes the feature's sub-issues `not_planned` and leaves the parent open; the three
  primitives now live in `bin/gh_issues.py`; migration is new features only. Note that Feature B
  (`depends_on:`, `blocked_by` edges) is sequenced separately and that no `blocked_by` edge is
  emitted by the mirror yet. **Constraint on the `<!-- stale: … -->` markers:** `check-docs.sh`
  scans `.claude/skills/**/*.md` as well as `docs/`, and `.claude/skills/harness/SKILL.md:137` still
  reads "closes its issue and everything it absorbs" — a file **no agent domain covers**. So declare
  no marker whose wording appears outside `docs/**`; instead record the required main-session edits
  (`SKILL.md:136-137`, the mirror table) in the amendment's prose as an explicit follow-up. Also add
  the `abandon` row's existence to the amendment so a reader is not left with three sync points.
- verify:
  - `.claude/skills/harness/bin/check-docs.sh` → exit 0, "no stale statements found".
  - `grep -n "amendment 7" docs/harness/DECISIONS.md` → one heading.
  - `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh` → exit 0 (INV-10 clean).

## Approval

status: pending
