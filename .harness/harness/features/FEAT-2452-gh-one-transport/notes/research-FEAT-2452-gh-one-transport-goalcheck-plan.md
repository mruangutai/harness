# FEAT-2452 plan goal-check: the applied plan delivers the operator's stated intent (operator pass, code maintainer pass)

**Asked verbatim: does this plan deliver the operator's stated intent? Yes.** I graded against the grilling note as the primary source (`.harness/notes/grilling-gh-adapters-d-2026-11-23.md`, Destination, Settled, Out of scope), then against the applied `BRIEF.md` and `plan.yaml`. Every Destination item and every Settled ruling Q1–Q8 maps to at least one SC and one task. Both perspectives pass.

Two items remain open, and neither is an implementation failure:
- **OQ-1**, the DEC-138 implementation sentence. Only the operator can rule on it.
- **The external four-angle simplify pass**, which must happen before signature.

The plan stays `status: plan` with `approval.status: pending`. All five tasks are `main-session-direct`.

## Perspective grades

| Perspective | Grade | Supporting SCs | Tasks |
|---|---|---|---|
| operator | **pass** | SC-03, SC-04, SC-05, SC-07 | T-01, T-02, T-03, T-04, T-05 |
| code maintainer | **pass** | SC-01, SC-02, SC-06 | T-01, T-02, T-03, T-04, T-05 |

Every SC has at least one tracing task (`plan.yaml tasks[].traces`):

| SC | Tasks |
|---|---|
| SC-01 | T-01, T-02, T-03, T-04 |
| SC-02 | T-01, T-02, T-03, T-04, T-05 |
| SC-03 | T-04 |
| SC-04 | T-02, T-03 |
| SC-05 | T-01, T-02, T-03 |
| SC-06 | T-05 |
| SC-07 | T-05 |

No perspective lacks a task.

## Intent coverage (grilling → plan)

- **Destination 1, one transport (Q1, Q3).**
  - T-01 adds `factory_gh.try_gh`/`GhResult`, `launch_gh`, and the `gh_cost_log._read_counter` move onto the non-measured primitive.
  - T-02 covers gh-sync `gh`/`gh_try` plus the auth, label, type, milestone, PR-list and replacement-create paths.
  - T-03 covers the board_lifecycle label path. T-04 covers wayfind `gh_json`/`do`/`append_gist`.
  - FACTORY_GH-only cutover and D-11 prose deletion: `factory_gh` warning (T-01), `gh-sync`/`gh_sync_support` (T-02), `gh_board`/`board_lifecycle`/board test headers (T-03), `gh_issues.gh_bin` (T-04), probe comments (T-05). This closes #893 (D-02).
- **Destination 2, five divergences.**

  | Divergence | Task |
  |---|---|
  | (a) fail-closed reads with typed 404 | T-04 |
  | (b) typed JSON | T-04 |
  | (c) checked label creates | T-02 for the mirror, T-03 for lifecycle |
  | (d) typed launch errors | T-02 |
  | (e) 422 milestone, trimmed to the first-to-cut inline conjunction | T-02 |

  Each has a failing-first regression in its task intent. #1542 is handled by T-01's parser and T-02/T-04, and #13 by T-02.
- **Destination 3, recorded policy (Q5 keep, Q6).** T-05 owns the caller-to-failure-policy table and the `factory_cli` exit-2 correction. SC-05 carries the regression controls for the kept policies.
- **Destination 4, enforcement untouched (Q2, Q4).** The ticket is a named deliverable, with T-05 filing it and SC-07 checking it. D-01 rejects `issue://`, `pr://` and `run_watch`. BRIEF Constraints mark DEC-100/144 as BLOCKS. No instruction changes are made.
- **Out of scope.**
  - Subprocess deadlines are a recorded non-goal: T-05's verify asserts the phrase "subprocess deadlines".
  - The probe's unchecked cleanup is unchanged by T-05.
- **Q8.** Every task is main-session-direct, with `execution_reason` DEC-174.

**Additions beyond the grilling** stay within DEC-132's room for what done also requires:
- the issue_types_live receipt (T-05, PF-f10c24fc);
- the DEC-220 keep rows;
- the offline sentinel confinement.

None widens the settled scope.

## Panel dispositions (cycle 1)

These are taken from `notes/research-FEAT-2452-gh-one-transport-apply-plan.md`. I did not re-review them independently. Severities and kinds match the recorded `plan.yaml panel.findings`, and I changed none.

| PF | Kind/sev | Reader | Apply disposition | Goal-check read |
|---|---|---|---|---|
| PF-3bfe1e6fa1d390a01608f9f4691e5d27 | substance/high | scope | Applied: confinement first, plus a caller-level single-override red run | Consistent: T-02/T-03/T-04 intents carry the sentinel and the FACTORY_GH-only setup |
| PF-500b6edeb3f44a1077e3d17823d19094 | substance/med | scope | Applied: absence requires nonzero int status AND HTTP 404; a status-zero JSON failure raises | Consistent: T-04 intent, SC-03 |
| PF-1d616c71fa78e2127146432752890b56 | substance/med | scope | Applied: recovery patches move to FACTORY_GH; telemetry is bound to T-02's verify pool | Consistent: T-02 verify includes tests/unit/test-gh-cost-log.py |
| PF-264d65c0b4c11c8fc335feb5240c3635 | form/med | scope | Applied: keep rows added for DEC-167 and DEC-220 (x2), plus a DEC-138 runner-clause keep row; OQ-1 raised | Consistent: `decisions_affected` |
| PF-f10c24fc64326826c94b4b2326fd8010 | form/low | scope | Applied: T-05 owns the probe receipt; SKIP fails | Consistent: T-05 files and verify |
| PF-e4b1875dab5b26b1e625b00544388f1e | proportionality/low | should-not-exist | Trimmed: inline 422 + already-exists conjunction, two regressions | Consistent: T-02 intent, SC-04 |
| PF-3cf5ab1247b91727827d2acdc2d6b56a | proportionality/info | should-not-exist | Trimmed: reference holds current policy only | Consistent: T-05 intent |

`plan.yaml panel.findings[].disposition` still reads `open` for all seven. That is the record-panel state, and the dispositions live in the apply note. Main records the fourth reader (goalcheck) from the lead digest. I edited no panel or plan file.

## Decision dispositions

`decisions_affected` has 11 rows, all `keep`:
- DEC-138 ×2
- DEC-146, DEC-174, DEC-144, DEC-166, DEC-200, DEC-203, DEC-167
- DEC-220 ×2

There are no amend or strike rows, so there are no disposition verdicts to grade. This is plan-time, so no review_sha exists.

## Open items, stated honestly

- **OQ-1 (operator-only, non-blocking for the plan step).** DEC-138's shared-code clause says, in the present tense, that `gh_bin()` lives in `gh_issues.py` and that each caller keeps its own runner. After T-02 and T-04, that implementation sentence is literally stale, though the policy it serves still holds.
  - The grilling settled "DEC amendments: none required". Its escape hatch, "only if the table would otherwise contradict the index rows", does not fire. DEC-205 (current-truth) points toward amending.
  - The choice is **keep**: accept the stale sentence until a later sweep, as the plan does now. Or **amend**: add an amend row and give DECISIONS.md an owning task, either T-05 or a new one. That would reopen settled scope and reset the task set.
  - The apply pm recommends amend. Choosing between them is the operator's ruling at signature, not a defect in this plan's delivery of the stated intent. The plan is faithful to the settled "no DEC amendments".
- **Four-angle simplify pass (pre-signature dependency).** This was escalated outside the product team and has not been done. Nothing here claims it. It gates signature, not this goal-check. If it changes tasks, it triggers `APPROVAL-RESET` handling under the normal rules.

## Writer receipt for `apply --proposal -` (task-changing)

**The full stdout is unavailable.** The apply agent's command (from its session transcript, `Feat2452Plan.BiologicalDolphin.EnthusiasticHyena`) redirected stdout to `/tmp/feat2452/apply1.out` and printed it as `cut -c1-300`. That temp directory no longer exists, so the full REPLACED old→new strings cannot be recovered without rerunning a writer, which I did not do.

Below is the only extant capture, preserved verbatim from that tool result. Each REPLACED line was cut at 300 characters by the agent's own command. The leading five lines are that command's proposal-size printout, and stderr was cut at 400 characters.

The capture contains no `APPROVAL-RESET:` line. Every stdout line is visible at its start, so an APPROVAL-RESET line would have appeared. No gh-sync call was due.

```text
T-01 {'id': 4, 'intent': 4419}
T-02 {'id': 4, 'intent': 6629, 'verify': 561}
T-03 {'id': 4, 'intent': 2591}
T-04 {'id': 4, 'intent': 3570}
T-05 {'id': 4, 'intent': 5261, 'files': 5, 'verify': 1620}
exit=0
REPLACED T-01.intent: "Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult its AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/
REPLACED T-02.intent: "Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/146/
REPLACED T-02.verify: 'python3 .claude/skills/harness/bin/run_pool.py --workers 4 tests/unit/test-gh-sync-build-entry.py tests/integration/test-gh-sync-open.py tests/integration/test-gh-sync-start-task.py tests/integration/test-gh-sync-record.py tests/integration/test-gh-sync-abandon.py tests/integr
REPLACED T-03.intent: "Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/146/
REPLACED T-04.intent: "Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/166/
REPLACED T-05.intent: "Work directly in PRODUCT Harness checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport; never delegate execution. Consult AGENTS.md, .harness/harness/docs/SPEC.md sections 3.3 and 9, .harness/harness/docs/DECISIONS.md DEC-138/146/
REPLACED T-05.files: [{'path': '.claude/skills/harness/references/github-mirror.md', 'quote': '## Failure has four shapes, not one'}, {'path': '.claude/skills/harness/bin/factory_cli.py', 'quote': 'Contract:'}, 'tests/manual/probe-issue-types.py#main', {'path': '.harness/harness/features/FEAT-2452-g
REPLACED T-05.verify: "python3 - <<'PY'\nimport json, pathlib\nroot = pathlib.Path.cwd()\nref = (root / '.claude/skills/harness/references/github-mirror.md').read_text()\nassert 'Caller-to-failure-policy' in ref\nassert all(word in ref for word in ('gh_try', 'SKIP', 'board-station', 'reconcile', 'fa
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
---stderr
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2452-gh-one-transport: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport.
  note       .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2452-gh-one-transport: run r-20261123-1-plan-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2452-gh-one-transport (not gating).
```

The `set-key decisions_affected`, `record-panel` and `check` outputs are complete in the apply note and are not repeated here. I ran no writer, check, test, build, lint or formatter.
