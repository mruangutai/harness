# SC-03/SC-07 amendment + goal-check at 894adc0f — BUG-1309

**BLUF. SC-01..SC-09 are all `met` at `review_sha 894adc0f`; SC-10 is `cannot-verify (user-gated)`.**
The two amended clauses are no longer claims about conduct — I ran the discrimination each new
clause demands and observed red-then-green for both. **The BRIEF has changed, so its `## Approval`
signature (Mike Ruangutai, 2026-09-06) no longer covers the text on disk: the main session must
re-sign. I did not and cannot touch that block.** The UAT script is accurate against the pinned
code (all 8 steps executed, zero drift) and **no UAT step touches PANEL-3's contradiction** — §5.

## 1. Verbatim before / after

**SC-03 — trailing sentence only. BEFORE:**
> The refusing assertion must be demonstrated failing against the pre-change copy of the script
> before the fix is accepted.

**SC-03 AFTER (`BRIEF.md:102-106`):**
> The refusing assertion is DISCRIMINATING at `review_sha`: run against the pre-change copy of the
> script recovered with `git show <base>:.claude/skills/harness/bin/gh-sync.py`, or against a
> mutation of that production path, the refusal case FAILS — and an assertion that cannot be made
> to redden is reported as non-discriminating rather than kept.

**SC-07 — trailing sentence only. BEFORE:**
> The violating fixture must be shown passing `check-state.sh` before the invariant lands.

**SC-07 AFTER (`BRIEF.md:133-137`):**
> The violating fixture is DISCRIMINATING at `review_sha`: pointed at the pre-change copy of the
> script recovered with `git show <base>:.claude/skills/harness/bin/check-state.sh` (the
> `CHECK_STATE_BIN` escape), or at a mutation of that production path, the violation case FAILS —
> and a case that cannot be made to redden is reported as non-discriminating rather than kept.

`git diff -- BRIEF.md` = **9 insertions, 3 deletions, two hunks at 102 and 131.** Every other line,
including `## Approval` and both `verify:`/`evidence:` lines, is byte-unchanged. `HEAD` unmoved
(`5d672120`).

The ordering requirement was converted, not deleted: what the sequencing clause bought was
*discrimination*, and discrimination is observable at the pin. The gate is not weaker — it is now
executable, and it names the report obligation when a case cannot redden.

## 2. Executed discrimination evidence

Trees: `git archive 894adc0f | tar -x` into `/tmp/b1309/pin`, `/tmp/b1309/red-gh`, `/tmp/b1309/red-cs`;
the pre-change script laid over the red trees with `git archive 6ad7233f <path> | tar -x`
(`6ad7233f` = `git merge-base origin/main 894adc0f`, re-derived). **The worktree's own sources were
never touched.** All runs `env -u HARNESS_AGENT_TYPE`.

**SC-03 — `tests/integration/test-gh-sync.py`, pre-change `gh-sync.py`**
- GREEN (`/tmp/b1309/pin`): exit 0, 322 ok / 0 FAIL. `ok T-04 non-era absent refuses`,
  `ok T-04 BUG-named non-era absent refuses`, `ok T-04 station discriminator`,
  `ok T-04 era-exempt continues`, `ok T-04 era recovery-required does not claim a refusal`.
- RED (`/tmp/b1309/red-gh`): **exit 1, 302 ok / 20 FAIL**, and all five of those cases FAIL —
  `FAIL T-04 non-era absent refuses`, `FAIL T-04 BUG-named non-era absent refuses`,
  `FAIL T-04 station discriminator`, `FAIL T-04 era-exempt continues`,
  `FAIL T-04 era recovery-required does not claim a refusal`.
- **Failure shape checked, not just the status** (guard against a red-for-the-wrong-reason): the
  refusal cases print `gh-sync: issue #41 -> building (T-01)` / `#40 -> building (parent)` — i.e.
  `start-task` proceeded normally and no refusal was emitted. Not a crash, not an argument error.

**SC-07 — `tests/integration/test-check-state.py`, pre-change `check-state.sh` via `CHECK_STATE_BIN`**
- GREEN (`/tmp/b1309/pin`, default `SCRIPT`): exit 0, 225 ok / 0 FAIL; all nine `T-06` cases `ok`.
- RED (`CHECK_STATE_BIN=/tmp/b1309/red-cs/.claude/skills/harness/bin/check-state.sh`): **exit 1,
  224 ok / 1 FAIL — exactly one case, and it is the violation case:**
  `FAIL - T-06 INV-37 fires at a done station with no task statuses`.
- Advisory (not a downgrade): its sibling `T-06 INV-37 message discriminator names recover-terminal
  only` stays green under the reverted script because it asserts `"open" not in line` and `line` is
  `""` when INV-37 never fires — **vacuously green, i.e. non-discriminating on its own.** The
  criterion's discrimination is carried by the `fires` case, which does redden. Backlog chore: bind
  that case to a non-empty line.

## 3. Grades at `review_sha 894adc0f` (SC-01..SC-09)

Provenance: `git diff --name-only d80a7b12 894adc0f -- .claude tests .omp` → **only**
`merge-gate.py`, `test-merge-gate.py`, `test-hooks-install.py`. Every other suite's evidence is
therefore valid at this pin unchanged; SC-04 is re-derived at the pin.

| SC | Method | Verdict | Evidence at the pin |
|---|---|---|---|
| SC-01 | automated/integration | **met** | my run, `/tmp/b1309/pin` exit 0: `T-02 open records opened`, `T-02 sync false records not-applicable`, `T-02 unpinned repo records nothing`, `T-02 first-call failure records recovery-required`, `T-02 second open stays opened`, `T-02 opened never downgrades` — all `ok` |
| SC-02 | automated/integration | **met** | same run: `ok T-02 partial remote write records nothing`, `ok T-02 contract error records nothing` |
| SC-03 | automated/integration | **met** (amended text) | five `T-04` cases `ok` at the pin; the amended discrimination clause executed — §2, red 20 FAIL / green 0 FAIL |
| SC-04 | automated/integration | **met** | qa c7 at this pin: `test-merge-gate.py` **19/19 ok, exit 0**, integration kind 50 files exit 0 (`notes/review-harness-qa-c7.md:10,26-27`). Plus my own four direct observations through `merge-gate.sh` at the pin's code: deny naming `open` (recovery-required/building), deny naming `recover-terminal --yes` (absent/done), allow silent exit 0 after `opened`, allow silent exit 0 after `recovered-terminal`. Remedy is derived, not hardcoded: `merge-gate.py:152` calls `feature_schema.recovery_command_for` |
| SC-05 | automated/integration | **met** | `ok T-03 recover-terminal creates milestone and parent only`, `ok T-03 FEAT-55 shape adopts and creates nothing`, `ok T-03 second run is idempotent`; and I observed `build_entry = recovered-terminal \| task issues = {}` with only `milestone #7` + `parent #41` created |
| SC-06 | automated/integration | **met** | `post-merge-sweep.sh` and `test-post-merge-sweep.py` are **unchanged** in `d80a7b12..894adc0f`, so the named cases `T-07 era-exempt recovery-required keeps the worktree` / `T-07 era-exempt absent build_entry is swept` (61 PASS / 0 FAIL, `notes/research-…-goalcheck-delivery.md:23`) hold at this pin; re-confirmed green by qa c7's integration run (50 files, exit 0). **I did not re-run it** — outside my two permitted files |
| SC-07 | automated/integration | **met** (amended text) | nine `T-06` cases `ok` at the pin incl. `T-06 INV-37 fires at a done station with no task statuses` (fixture: station `done`, no task `status` key, sync true, repo pinned) and the four silent cases; amended discrimination clause executed — §2, red 1 FAIL |
| SC-08 | automated/integration | **met** | `test-validate-feature-json.py` unchanged in the range; the four `accepted_github_build_entry_*` and three `rejected_*` cases as recorded, re-confirmed green inside qa c7's integration run (exit 0) |
| SC-09 | inspection | **met** | `git show 894adc0f:.claude/skills/harness/references/github-mirror.md` → `:41` "Build entry — immediately after the plan's signed approval, before the first task starts \| **orchestrator** \| `gh-sync.py open <feature-dir>`", `:51-52` the four values + "its absence means no Build entry completed". `git show 894adc0f:.claude/skills/harness/SKILL.md` → `:141-142` build-phase item 1, "**Build entry.** Immediately after signed approval and before dispatching any task, run `gh-sync.py open <feature-dir>`". Grep for `at ship` in both at the sha: **zero hits** |

No criterion grades `unmet`, so there is no work-undone / criterion-unmeetable split to report.

## 4. SC-10 — `cannot-verify (user-gated)`

Script: `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`.
Only the operator can grade it; recording it met or unmet would falsify the record.

**Accuracy against the pinned code — I executed all eight steps (step 9 cleanup skipped, `rm -rf`
is guard-denied for me). Zero drifted steps.** Step 1: 83 lines, "near 80" ✓. Step 2:
`git show 894adc0f:.claude/settings.json` names `merge-gate.sh:48` ✓. Step 3: deny reads
`records github.build_entry=recovery-required … denied until python3 …gh-sync.py open
/private/tmp/…` — matches the note's stated text incl. its `/private/tmp` macOS caveat ✓. Step 4:
usage line carries both `open` and `recover-terminal` ✓ (it prints prefixed `gh-sync: ERROR —
usage:`, which the note's "a usage line" covers). Step 5: prints exactly `opened`, plus the two
expected board/issue-type notices ✓. Step 6: no output, `exit=0` ✓. Step 7: all four observations
hold — deny names `recover-terminal … --yes` not `open`; only milestone + parent created;
`build_entry = recovered-terminal | task issues = {}`; then silence at exit 0 ✓. Step 8: deny says
`NO COMMAND CLEARS THIS BY ITSELF` and names both configuration fixes plus the `gh repo view` command ✓.

One standing caveat, not drift: `UAT_CHECKOUT` names the worktree
`/Users/…/.claude/worktrees/harness/BUG-1309-mirror-build-entry`, whose on-disk scripts are
byte-identical to the pin (`894adc0f..HEAD` touches `feature.json` alone). It must be run **before**
the worktree is released.

## 5. PANEL-3 vs the UAT — checked step by step

**No UAT step lands on PANEL-3's contradiction. Spending the operator's ten minutes does not
require PANEL-3 to be ruled on first, and running the UAT will not produce evidence about it.**

PANEL-3 concerns `gh-sync.py:1387-1389`, the non-era arm of `_build_entry_recovery_notice`, which is
reached **only from `_build_entry_preflight` → `cmd_start_task`** (`gh-sync.py:1452`). Step by step,
the code path each exercises:

- Steps 3, 6, 7, 8 — `merge-gate.sh` → `merge-gate.py`. Its remedy string is derived at
  `merge-gate.py:152-153` from `feature_schema.recovery_command_for`, so it cannot disagree with
  that function by construction; measured, it named `open` for recovery-required/building (step 3)
  and `recover-terminal --yes` for absent/done (step 7).
- Step 4 — `gh-sync.py` with no arguments: the `die()` usage branch.
- Step 5 — `gh-sync.py open` → `cmd_open`.
- Step 7 (middle command) — `gh-sync.py recover-terminal --yes` → `cmd_recover_terminal`.
- Step 1 — the fixture builder; Step 2 — a grep of `settings.json`; Step 9 — cleanup.

**`grep -n "start-task" <the UAT note>` exits 1: zero matches in the whole script**, so no step
invokes the only entry point that reaches the contested message. Step 3 is the closest, and its
fixture is `recovery-required` + station `building`, for which `recovery_command_for` returns `open`
— the *consistent* combination. The contradiction needs `recovery-required` **and** a
station/task-status that makes `recovery_command_for` return `recover-terminal` **and** the
`start-task` path; no step has that shape.
