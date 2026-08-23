# Receipt — harness-dev-ops — T-05 (FEAT-33)

BLUF: `audit` is built and wired into `board_lifecycle.py`, all five finding classes are covered
by their own case with its own fixture, the exit-code matrix (0/1/4) is observed and mutation-red-
proved, and the forking integration case (K) proves the process exit status. `run-unit-tests.sh
--kind all` is still finishing at the time this receipt is written (see below); every script this
task touches passes standalone.

## Files touched
- `.claude/skills/harness/bin/board_lifecycle.py` — added `cmd_audit`, `_audit_findings`,
  `_REQUIRED_WORKFLOWS`, and the AUDIT section of the module docstring. `provision` (T-04) is
  unchanged.
- `.claude/skills/harness/bin/test-board-lifecycle.py` — 15 new checks: clean board, one case per
  finding class (DECLARATION, STATION, REASON, LABEL, WORKFLOW×2: missing + disabled), the
  header-once check, and the GhError exit-4 case. Extended the fake `gh` and `run()` helper with
  `ISSUES_JSON`/`STATIONS_JSON`/`WORKFLOWS_JSON`/`FAIL_MATCH`.
- `.claude/skills/harness/bin/test-factory-integration.py` — case (K): one forking `audit` case
  against the stateful fake, plus the `issue list` and `fieldValueByName` (board-stations)
  branches that fake now needs to answer `audit`'s two calls it didn't serve before (`workflows`
  was already answered, for T-04's provision docstring section referencing it).

## The five finding classes and their case
1. **DECLARATION** — `test-board-lifecycle.py` "audit DECLARATION" (options missing `"Plan"`).
   Calls T-04's `_missing_options` verbatim; no re-authored comparison.
2. **STATION** — "audit STATION" (issue #10 closed, station `Building`, expected `Done`).
3. **REASON** — "audit REASON" (issue #20, `stateReason: null`). Also case (K)'s integration
   fixture (issue #900, one finding, real fork).
4. **LABEL** — "audit LABEL" (issue #30, `NOT_PLANNED`, no `abandoned` label) plus a sibling
   fixture (issue #31, same reason, WITH the label) proving the negative.
5. **WORKFLOW** — two cases: "audit WORKFLOW (renamed/absent)" (`Pull request merged` missing)
   and "audit WORKFLOW (disabled)" (`Auto-close issue` present, `enabled: false`). Both assert the
   per-line "no API can enable it ... web UI" suffix, and the header line
   `workflow detection matches by NAME only ...` (SC-09) is asserted to print exactly once.

## Exit-code matrix observed
| Case | Exit | Evidence |
|---|---|---|
| clean board | 0 | "audit clean board: exits 0" |
| DECLARATION/STATION/REASON/LABEL/WORKFLOW finding | 1 | each case's own "exits 1" check |
| forced `GhError` (fail on the first of the four calls) | 4 | "audit GhError: exits 4, never 0 or 1" |
| forking process, one REASON finding (case K) | 1 (real process exit) | "(K) ... forked process exits 1" |

`4` was reached by forcing the field-options call (the first of the four) to fail via a
`FAIL_MATCH` hook added to `test-board-lifecycle.py`'s fake `gh`; stdout carried nothing that
looked like a finding or a clean report, and stderr carried exactly one line.

## Network-call count vs docstring
Implementation makes exactly four: `factory_gh.project_field_options` (class 1),
`gh issue list --state closed --json number,stateReason,labels --limit 1000` (feeds classes 2/3/4),
`gh_board.board_stations` (class 2), `factory_gh.project_workflows` (class 5). The module docstring
states this count explicitly in a new AUDIT section and lists the four in order — it matches; no
fifth call exists.

## Mutation red-proofs (all restored byte-identical; confirmed via `grep` for the mutation marker
returning nothing after each restore)
- DECLARATION: `for value in _missing_options(...)` → `for value in []:` — reddened exactly the 2
  DECLARATION checks, nothing else.
- STATION: guarded the STATION `if` with `if False and ...` — reddened exactly the 2 STATION
  checks.
- REASON: same technique — reddened exactly the 2 REASON checks.
- LABEL: same technique on the `not in names` branch — reddened exactly the 2 LABEL checks (the
  sibling "carries the label -> no finding" case stayed green, since it asserts an absence that
  the mutation doesn't touch).
- WORKFLOW: guarded both the MISSING and disabled branches with `False and` — reddened both
  WORKFLOW cases (5 checks), nothing else.
- Header-once: deleted the `_out(_WORKFLOW_HEADER)` call — reddened exactly the header-once check.
- Exit-4: changed `sys.exit(4)` to `sys.exit(2)` in the `except GhError` handler — reddened
  exactly the "exits 4, never 0 or 1" check, with the real stderr text
  (`gh graphql call failed: ...`) proving the failure path is genuine, not fabricated.
- Case (K)'s discriminating power: renamed the `elif args.cmd == "audit":` dispatch arm so
  `audit` never runs — reddened exactly case (K)'s 2 checks (2 of 122), confirming the forking
  form is what catches a `__main__` block that forgets to dispatch, exactly as T-04's own sibling
  case was designed to and as this task's intent describes.

Every mutation was applied with `Edit`, verified reddened with a standalone run of
`test-board-lifecycle.py` (or `test-factory-integration.py` for case K), then reverted with
`Edit`, and the revert was confirmed by `grep` finding no trace of the mutation marker in the
restored file.

## Standalone results
- `python3 test-board-lifecycle.py` → `all checks passed.` (57 checks: 19 provision + 38 audit;
  see the file for exact counts.)
- `python3 test-factory-integration.py` → `122/122 checks passed.`

## `verify: .claude/skills/harness/bin/run-unit-tests.sh --kind all`
Ran to completion (`echo "EXIT:$?"` → `0`, confirmed by the background-task notification).
2,612-line log, `grep -n "FAIL\b\|MISCONFIGURED\|Traceback"` finds only benign substring matches
that are part of PASSING check names (e.g. `ok FAIL over an escalating member is rejected` — a
fixture literally named FAIL that a different task's own test expects to be rejected) — no real
failure or misconfiguration line anywhere in the run. `test-board-lifecycle.py` → PASS.
`test-factory-integration.py` → PASS, including case (K) at line 2228-2229:
`(K) board_lifecycle.py audit: forked process exits 1 ...` and `... the finding's text appears on
stdout`. `test-gh-sync.py` (T-08's sibling file, untouched by this task) → `ALL PASSED`. Log saved
at `/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/070b3f94-b495-4deb-b352-6896cfb60ad3/scratchpad/verify-t05.log`.

## Digest note (issue #778)
Plan's `change_type: feature` for T-05 is rejected by `validate-digest.py:158`'s dev-ops enum
`{config, scaffolding, infra, ci}`. Substituting `infra` — this is new infrastructure code (a CLI
subcommand talking to an external API), not CI config or scaffolding. Reporting the rejection per
the dispatch's instruction rather than silently working around it; #778 is the tracked defect.

## Open questions
- None blocking. The plan/harness.json `change_type` enum mismatch (#778) is a pre-existing,
  already-tracked issue, restated here per the dispatch's instruction, not a new finding.
