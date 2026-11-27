# Goal-check — FEAT-2452-gh-one-transport — validate cycle 1

Run r-20261123-5-validate-validator · pin `64102016cba259b96fcf7761b3f31ec685a65a8c` · base `b788e9dac342ee112106a3bc5aa7430d4467cbcb`.
All evidence below was read with `git show <pin>:<path>` or `git diff <base> <pin>`. No suites were re-run.

**BLUF: FAIL, one narrow gap.** The code maintainer perspective PASSES. The operator perspective is
PARTIAL, for one reason only: SC-05 requires QA to show the new abandon (#13) assertions failing
first, and the build recorded that they PASS on the old code (`notes/t02-red-green.md`, row
"#13 abandon regression on the old code"). Everything else in the operator's SCs is met. SC-04 is
**met with the cut**, not met as written. The one DEC amend row (DEC-138) is met.

The automated SCs (SC-01–SC-05) are graded from the build's red→green receipts and the tests at the
pin. QA's cycle-1 DIGEST was not yet available, because this reader runs concurrently with it; that
DIGEST is the run that confirms these verdicts. Between `943d2e79` (the last code commit) and the pin,
nothing changed outside the feature directory (`git diff --name-only 943d2e79 <pin>` lists only FD paths).

## Perspectives

| Perspective | Verdict | Carried by | Evidence |
|---|---|---|---|
| code maintainer | **pass** | SC-01, SC-02, SC-06 | Only `factory_gh.py` (the `launch_gh` body) calls `subprocess.run` with gh among the scoped modules. gh-sync's remaining `subprocess.run` calls launch plan-merge.py and git, not gh. `GH_SYNC_GH`, `D-11` and `dual-pin` have no match in `.claude/skills/harness/bin` or `tests` at the pin (git grep exit 1). The one assembled name is in test-wayfind.py:417 (disclosure 3). The policy table is in github-mirror.md. |
| operator | **partial** | SC-03, SC-04, SC-05, SC-07 | Fail-closed wayfind reads, typed failures, checked labels and ticket #2468 are delivered. The SC-05 abandon failing-first clause has no evidence (see SC-05). |

## SC verdicts

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated (unit) | Red: `t01-red-green/01-red-test-factory-gh.txt` (15/278 FAIL) and `01-red-test-gh-cost-log.txt` (5/49 FAIL). Green: 319/319 and 59/59. Tests: `tests/unit/test-factory-gh.py` t01_* (GhResult shape, try_gh launch failures and strict-JSON status-zero not-ok); `tests/unit/test-gh-cost-log.py` t01_counter_uses_launch_gh, t01_launch_gh_is_not_measured, t01_import_orders. |
| SC-02 | met | automated (integration) | Caller-level single-override red: `t02-red-green/01-red-confinement-open.txt` ("default gh binary was dispatched: 'auth status'"). Test: `tests/integration/test-gh-sync-open.py` single_override_case (sentinel unused, counter-bracketed telemetry). Shared confinement: `tests/offline_gh_support.py`. Absence at the pin: git grep, as in the maintainer row. |
| SC-03 | met | automated (unit) | Red: `t04-red-green/03-red-behaviour.txt` (every failed blocker/parent read is swallowed as absence). Tests: `tests/unit/test-wayfind.py` case_3, 4, 5, 7, 9, 10, 11, 12, 12b, 12c. The classifier is `wayfind.py` gh_json_or_absent, which requires an int nonzero status and `(HTTP 404)` in stderr. |
| SC-04 | **met with cut, not met as written** | automated (integration) | (c) red: `t02-red-green/04-red-behaviour-old-override.txt` (failed first label) and `t03-red-green/03-red-behaviour-lifecycle.txt` (13 FAIL). (d) red: `t02-red-green/03-red-behaviour-*.txt` (FileNotFoundError escapes gh and gh_try). Tests: test-gh-sync-open.py label_failure_case and launch_failure_cases; test-board-lifecycle.py reconcile case 4b. Live matcher tripwire: `c3-label-tripwire.txt` (gh 2.103.3). (e): see "Disclosure 1" below. |
| SC-05 | **partial** | automated (integration) | URL red: `t02-red-green/04-red-behaviour-old-override.txt` (parent, task, backlog CASE I FAIL). Tests: test-gh-sync-open.py malformed_url_cases; test-gh-backlog-issue-types.py case_i; test-gh-sync-abandon.py "#13 failing close API" ×3. **Gap:** `t02-red-green/05-red-abandon-old-override.txt` shows the #13 assertions PASS on the old code. The clause "QA demonstrates the new URL/abandon assertions failing first" has no abandon red. |
| SC-06 | met | inspection | See "SC-06" below. |
| SC-07 | met | inspection | See "SC-07" below. |

### SC-06 (graded at the pin)

- `.claude/skills/harness/references/github-mirror.md`, section `## Caller-to-failure-policy`,
  is a three-column table: condition / outcome and exit / partial writes and recovery. Its rows cover:
  - mirror `gh()` SKIP/0 and `gh_try` tuple/continue;
  - binding refusal/2, checked label create, ordinary milestone, replacement create (recovery), merged-PR list, issue-type downgrade;
  - gh-sync board projection, board-station (diagnostic/0), factory (GhError/2 after writes);
  - board_lifecycle audit/provision/reconcile, wayfind (fail-closed, exit 1) and gh_cost_log (None).

  Under **Notes**: "Deadlines are a conscious non-goal: `factory_gh` sets no subprocess deadlines".
  Spot-checked against the code: board-station.py catches `(gh_board.BoardError, factory_gh.GhError)`
  (line 167); the milestone else-branch looks up on any failure (gh-sync.py `_open_ensure_milestone`).
- `.claude/skills/harness/bin/factory_cli.py` Contract: exit 2 now reads "refused or failed … Exit 2
  does NOT mean nothing was mutated", with factory_land and factory_decompose examples. The exit-3
  lost-race claim is kept.
- No enforcement change. `git diff --name-only base..pin` names no branch-create-gate, merge-gate or
  check_state file. Its only `GH_BIN` lines are prose in github-mirror.md. This matches C4
  (`notes/c4-enforcement-diff.md`).

### SC-07 (graded at the pin)

`notes/enforcement-backlog.json` records:
- number 2468;
- url `https://github.com/mruangutai/harness/issues/2468`;
- state OPEN;
- title "Enforcement GitHub reads must not trust unverified state".

Its body is byte-identical to the signed body in T-05's intent (compared programmatically). The body
names branch-create-gate.py trusting nonempty stdout without checking the return code, and merge-gate.py
falling back to the local branch after a failed head read. Neither executor changed (SC-06).

## Disclosure 1 — divergence (e) under C5

SC-04 as written requires three things:
- a lookup only on 422 plus "already exists";
- a failing-first regression for (e);
- one lookup regression and one no-lookup regression.

**None of the three exists at the pin.** SC-04's own last clause ("is cut under the settled
first-to-cut lever if it needs more"), together with C5 ("second spelling … → cut it, record in the
ship record, no return required"), sanctions the cut. The trigger is that GitHub reports a duplicate
milestone as `already_exists` / `Validation Failed (HTTP 422)`, so the pinned phrase may be absent.
That trigger is `[INFERENCE]`, drawn from the documented API shape and not from a live probe
(`t02-red-green.md` § "Cut under C5"). The cut keeps the base behaviour, so it adds no regression.

Verdict: **met-with-cut.** Still outstanding: the ship record must carry the cut, which C5 requires. It
cannot be graded until ship.

## Decision dispositions

| Row | Verdict | Method | Evidence |
|---|---|---|---|
| DEC-138 amend (runner clause "each caller keeps its own runner, because"; successor D-01) | met | inspection | At the pin, `.harness/harness/docs/DECISIONS.md` line 3132 opens "Shared code, and migration scope." The rewrite names `factory_gh` as "the one shared transport", resolving `FACTORY_GH`, with "Failure policy stays at each caller". Neither "gh_bin" nor "keeps its own runner" appears anywhere in the file. `git diff base..pin` is one hunk (+6/−4), confined to that paragraph. The guard sentence's text ("imports only `internal_id_args` and `attach_sub_issue_args` … standing regression guard") is unchanged; only its line wrap moved. No policy clause and no DEC-146 line changed. DECISIONS-INDEX.md: after stripping `@line` anchors, every changed line is identical, so the edit was an anchor shift only. |

Keep rows are not graded. There are no strike rows.

## Findings

1. **substance · med · T-02.** SC-05's abandon failing-first clause is unevidenced.
   - Scenario: the #13 assertions already pass against the base gh-sync.py, so a regression that made abandon stop after a failed close would be caught, but no record shows the assertions can fail.
   - Route: qa, under P-05 and O-07. Show the three "#13 failing close API" checks reddening against a mutant whose abandon loop aborts on the first `gh_try` failure.
   - If qa's cycle-1 DIGEST already carries this, SC-05 and the operator perspective become met.
2. **form · low · T-05.** The github-mirror.md milestone row carries history ("A planned narrowing … was cut"). T-05's intent says to keep the reference to current policy rows, and keep closure history in the ship record (PF-3cf5ab12).
   - Scenario: an agent loading the reference treats a cut plan item as live context.
   - The row's current-behaviour statement is accurate.

## Open (non-blocking)

- The ship record must record the (e) cut (C5).
- QA's cycle-1 DIGEST is the confirming execution for SC-01–SC-05 at the pin.

## Principles applied

- P-05 (Expertise): SC verdicts are graded independently of gate status, which keeps SC-05 partial despite green suites.
- P-15/P-06 (Expertise): DEC-138 is checked against the pinned bytes, not against the builder's summary.
