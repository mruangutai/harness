# Research — FEAT-26 PR linkage and source tickets

Measured at `ada8e99` (HEAD of `main` at the time of this note), issue #492.

## BLUF

Both halves are buildable, and the census that shapes the plan is bigger than the ticket says.
**All eleven** `Done` features carrying `pr: null` map to a merged PR — seven derive mechanically
from the branch already in `feature.json`, four need a number the operator supplies. So the
backfill is complete-able and the new invariant can be an honest predicate with **zero warns on
day one**. No grandfather boundary is needed and none is proposed.

The source ticket is recorded nowhere machine-readable, so `Closes #N` cannot be derived today. A
new key is required, and the schema is closed.

## 1. The seat that opens a PR is the user's, and it stays that way

`DEC-153` (`.harness/harness/docs/DECISIONS.md:3660-3662`, read directly): *"The commit pen is the
orchestrator's: it stages by explicit pathspec and commits the feature branch it owns; merge/PR/
deploy stay user-gated."* `.claude/skills/harness/SKILL.md:207` says the same from the other side:
*"the harness composes no issue-closing text into any pull request body"*.

Consequence for the goal constraint "stop depending on a human remembering": recording **at PR-open
time** cannot satisfy it, because the opening seat is the human. The only seat that removes memory
is one that **derives** the number after the fact.

Derivation is measured to work. `gh pr list --head <branch> --state merged --limit 10 --json number`
against every null feature's recorded branch:

| feature | branch | merged PRs on that head |
|---|---|---|
| FEAT-01 | `none` | [] |
| FEAT-02 | `feat/harness-native-foundation` | [15, 4] |
| FEAT-03-subissue-mirror | `feat/harness-native-foundation` | [15, 4] |
| FEAT-04-decisions-index | `feat/decisions-index` | [] |
| FEAT-05-pyyaml-file-parsers | `worktree-fix-harness-tooling-backlog` | [17] |
| FEAT-08-remove-cost-tracking | `feat/FEAT-08-remove-cost-tracking` | [131] |
| FEAT-10-software-factory | `feat/FEAT-10-software-factory` | [212] |
| FEAT-20-migration-detector | `feat/FEAT-20-migration-detector` | [376] |
| FEAT-21-features-layout-migration | `feat/FEAT-21-features-layout-migration` | [415] |
| FEAT-22-docs-layout-migration | `feat/FEAT-22-docs-layout-migration` | [451] |
| FEAT-23-ship-flow-fixes | `feat/FEAT-23-ship-flow-fixes` | [491] |

Seven resolve to exactly one. Two branches resolve to none (`none` is the unset placeholder;
`feat/decisions-index` never carried a PR — PR #15's title names FEAT-04 and it shipped from
`feat/harness-native-foundation`). One branch carries **two** merged PRs, which is why the rule must
be *exactly one*, not *first*.

Attribution for the four, from PR titles — judgement, not measurement, and therefore proposed for
the operator's signature rather than asserted: FEAT-01 -> #4, FEAT-02 -> #4 (PR #4 "Replace GSD with
the harness (foundation)"), FEAT-03 -> #15, FEAT-04 -> #15 (PR #15 "FEAT-04 (decisions index) +
FEAT-03 backlog disposition + briefing HTML").

Corrections to the ticket's own numbers: FEAT-19 is `status: Abandoned` and never built, so its
`pr: null` is correct and it is not a backfill candidate. The nulls are eleven of twenty-two `Done`
features, not "the recent five".

## 2. The source ticket has no home, and the seam is a timing seam

`feature.json`'s `github:` block holds exactly five keys, written verbatim at
`gh-sync.py:492-497`. None of them is the ticket the feature was planned from.

The operator names the ticket at **plan** time. `gh-sync.py open` runs later. So whatever the
ship-time code reads must already be durable at plan approval — which makes `plan.yaml` the natural
holder (pm authors it, the operator signs it) and `feature.json` the mirror.

**The clobber trap, and it is the concrete bug this design would otherwise ship.**
`save_recorded` (`:492-497`) rebuilds `doc["github"]` from five named keys, and `cmd_open` calls it
after *every* issue create in its loop (`:584`, `:595`, `:597`). A `source_issues` written once by a
separate statement is erased on the next save. The value must be threaded through the `rec` dict —
defaulted in `load_recorded`'s `rec` literal (`:355`), read from the loaded block, and written back
in `save_recorded`'s six-key block.

## 3. Issue #289 is answerable, and the two writers in this one file disagree

`save_recorded` starts from `doc = {}` on the absent-file path (`gh-sync.py:489-491`) and would then
write a document holding only `github` — missing all eight required keys of DEC-191's schema.

Reachability, the half #289 says must be answered first:
- `.claude/skills/harness/SKILL.md:22-24` has the orchestrator instantiate `feature.json` from
  `.claude/skills/harness/templates/feature.json` on its **first cycle ever**, which is mission
  plan. `gh-sync.py open` runs later.
- Every one of the 25 feature directories on disk carries a `feature.json`, including
  FEAT-24, which is still `status: Plan` and has never shipped.

So the path is **unreachable on the governed flow and reachable by hand** (`gh-sync.py` only
requires the directory to exist). The cheap correct fix is not a new guard but consistency:
`_record_status` already refuses to create a document, and `_atomic_write`'s docstring
(`:425-428`) argues exactly why — *"a fresh single-key document fails feature-schema.json's
additionalProperties: false (DEC-191)"*. `save_recorded`'s empty-start contradicts its own
neighbour. Make it refuse too, in the task that already edits the function.

## 4. `Closes #N` — rendered, never posted

DEC-138 amendment 6 (`DECISIONS.md:4220-4247`) bans "the mirror composing its own text at post
time" and makes the mechanism structural: any posting subcommand takes its body from a **file
path**. DEC-196 adds that the harness "closes only cards it created" — the source tickets are the
operator's.

Both are satisfied by a **renderer**: a subcommand that prints `Closes #N` lines to stdout from the
recorded `source_issues`, which the operator pastes into the PR body they open. The harness derives;
it does not post and does not close.

The rejected alternative worth naming: `cmd_ship` closing the source issues directly at acceptance.
Stronger automation, but it crosses DEC-196's boundary and changes who closes operator-authored
issues. That is the operator's call, raised as an open question rather than planned.

## 5. Surfaces, routes and runners

`check-domain.sh --resolve`, run per path:

| path | resolves to | plan route |
|---|---|---|
| `.claude/skills/harness/bin/gh-sync.py` | harness-backend-dev, harness-dev-ops | team |
| `.claude/skills/harness/bin/feature-schema.json` | harness-backend-dev, harness-dev-ops | team |
| `.claude/skills/harness/bin/test-*.py` (the three touched) | harness-backend-dev, harness-dev-ops | team |
| `.claude/skills/harness/bin/check-state.sh` | harness-backend-dev, harness-dev-ops | **main-session-direct** (DEC-174 carve-out) |
| `.claude/skills/harness/templates/plan.yaml` | NOBODY | main-session-direct |
| `.claude/skills/harness/SKILL.md` | NOBODY | main-session-direct |
| a feature's `feature.json` | harness-orchestrator | main-session-direct (no team lane holds it) |
| `.harness/harness/docs/DECISIONS*.md` | harness-documentor | team |

`check-plan-routes.py:366-370` reports `DEVIATION`, not a violation, when a granted path is declared
main-session-direct, so the carve-out and the orchestrator-owned files are legal declarations.

Runners: `unit` and `integration` are both active in `.harness/harness.json` `test_kinds`.
`test-validate-feature-json.py` is registered in `UNIT_SCRIPTS` and `test-gh-sync.py` /
`test-check-state.py` in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:17-18`). **No new test file is
needed**, so the drift detector at `run-unit-tests.sh:41-42` cannot be tripped. No surface this
feature touches is covered by a `cmd: null` kind, so the BRIEF records no verification gap.

Highest existing invariant in `check-state.sh` is **INV-27**, so the new one is **INV-28**. INV-21's
block (`check-state.sh:858-891`) is its shape model: per-feature glob loop, parse-guard that reports
rather than `continue`s silently, warn level because the GitHub mirror never gates.

Next free decision number is **DEC-197**.

## 6. Concurrency

`gh_board.load_board` is imported and called at `gh-sync.py:139`; that module belongs to #493 and is
**read-only** for this plan. Nothing here changes it, changes its signature, or adds a
`harness.json` key. Nothing here touches `fleet.yaml`, `factory_claim.py`, the expertise hooks, the
factory lane's use of `pr`, or any product repo.

## Open questions

1. Should the harness open its own PRs, as `factory_land.py:67` does for product repos? That
   contradicts DEC-153 and is the operator's to settle. This plan designs the recording seat only.
2. Should `gh-sync.py ship` close the source issues directly instead of rendering `Closes #N` for
   the operator's PR body? Changes who closes operator-authored issues (DEC-196).
3. The four PR numbers that cannot be derived (FEAT-01, 02, 03, 04) need the operator's confirmation
   at signature. Proposed values are in section 1.
