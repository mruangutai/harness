# Goal-check — FEAT-16 factory per-repo board (c0)

## BLUF

**Twelve of thirteen criteria met; SC-06 is `not_met` and that is the honest, expected state** — it is
`verify: uat`, needs a live board mutation, and only the operator may run it. No fix cycle is
recommended against it. All six REQs trace to done tasks. Two BRIEF-level defects are recorded, not
repaired: **SC-10's stated base `a29ad06` is stale** (its literal command now false-positives on all
four carve-out scripts because FEAT-17 changed them on main between plan time and this branch's
start), and **SC-13's stated rationale is falsified at source** (the mutant it claims C1 is blind to
kills C1 too). Both are the operator's to amend; the criteria themselves hold.

## Pin

- `git rev-parse HEAD` = `2e3b7bcf19b816292e83e31ad8020b57e772e60c` — matches the dispatch.
- `git rev-parse --abbrev-ref HEAD` = `feat/FEAT-16-factory-per-repo-board`.
- `git worktree list` = one entry, `/Users/molchairuangutai/GitHub/harness`. No sibling checkout.
- `ec195ec` (review_sha) and `a9558be` (T-07's capture sha) are both ancestors of HEAD
  (`git merge-base --is-ancestor`, exit 0). `a7c429c..HEAD` is 22 commits.
- `git status --porcelain` before writing this file: empty.

## Verdicts

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated | `test-factory-config.py` cases `(3) a repos entry has no board`, `(27)` asserting `repos[mruangutai/kaya-ai].board` in the error, `(28a-d)`; unit suite exit 0 (re-run) |
| SC-02 | met | automated | `test-factory-config.py:161,198` — `(8b) a leftover top-level board key raises FleetError` + `(8b) the next_step mentions repos[].board` |
| SC-03 | met | inspection | `notes/board2-capture.md` §2 (Done 118, Review 0, 211 total) and §3 (ids `f75ad846`, `51284156`, `8f8df98a`, `47fc9ee4`, `8c67edb9`, `98236657` — the three anchor ids all present) |
| SC-04 | met | automated | assertions on recorded call arguments, all three tools: `test-factory-claim.py:952` (P3 refusal names B's board), `test-factory-decompose.py:1148,1155`, `test-factory-land.py:461-466` (`b_markers` non-membership), `test-factory-integration.py:1078` |
| SC-05 | met | automated | `test-no-distribution.py:294` `kaya_ai_is_paired_with_board_2` (`kaya_board_number == 2`), plus `:264 board_lives_per_repo_not_fleet_level` and `:289 every_repo_declares_its_own_board` |
| SC-06 | **not_met** | uat | pending operator; live-run protocol is BRIEF `## Constraints`. Nobody but the operator may run it; a board write is parked. No agent work can close this |
| SC-07 | met | inspection | live read-only `gh project field-list N --owner mruangutai`, unsorted, both boards: board 2 → `Backlog,Plan,Ready,Building,Review,Done` count=6; board 3 → identical string, count=6 |
| SC-08 | met | automated | `run-unit-tests.sh --kind unit` re-run at HEAD → `UNIT_EXIT:0`, zero `^FAIL|^ERROR` lines |
| SC-09 | met | automated | `run-unit-tests.sh --kind integration` re-run at HEAD → `INTEGRATION_EXIT:0`, zero `^FAIL|^ERROR` lines |
| SC-10 | met **on intent**, base stale | inspection | `git diff --name-only a7c429c..ec195ec` ∩ four scripts → empty (exit 1); same for `a7c429c..HEAD`. The BRIEF's literal `a29ad06..HEAD` returns **all four**. See below |
| SC-11 | met | inspection | both greps return nothing at HEAD: the `fleet…["board"]`/`.get("board")` pattern over `.claude/skills/harness/bin/` (exit 1), and `grep -n 'def station(' factory_config.py` (exit 1) |
| SC-12 | met | inspection | re-run at HEAD after both post-T-10 SPEC edits: `DEC-174 amendment 2` count 1; `per repository served` count 2; `per-repository board` on the DEC-174 row (`DECISIONS-INDEX.md:192`) and the DEC-186 row (`:204`); `SPEC.md:416` now exposes `board_for`/`board_station`, and the `the \`board:\` the factory reads work from` sentence is absent. All four baselines confirmed 0/1 at `a29ad06` |
| SC-13 | met, rationale falsified | automated | `test-factory-claim.py:1000-1003` (P6: empty stdout, `no work available` on stderr, `EXIT_NOTHING`), mutation-proved non-vacuous by qa. See below |

## REQ coverage

Every REQ traces to a task recorded `done` in `plan.yaml`: REQ-01 → T-01,02,03,04,05,07; REQ-02 →
T-01,06,08,11; REQ-03 → T-08; REQ-04 → T-07; REQ-05 → T-09; REQ-06 → T-10. Nothing was dropped.

## The two BRIEF defects — reported, not repaired

**SC-10's base.** `a29ad06` is an ancestor of this branch, not its branch point (`a7c429c` is).
FEAT-17 changed all four carve-out scripts on main in between, so the criterion's stated premise —
"a non-empty intersection is this feature's doing and nobody else's" — is no longer true of the tree.
The feature's own diff touches none of the four. Amending the base to `a7c429c` is a re-signature and
therefore the operator's, not ours.

**SC-13's rationale.** `grep -n "no work available" factory_claim.py` returns exactly one hit,
`:293`, and it sits *after* the per-repository accumulation loop as an aggregate `if not candidates:`
check (`factory_claim.py:292-293`). So the "silent exit 0" mutant kills C1 and P6 together; the
BRIEF's "C1 passes on that mutant" is false of the code as it landed. qa reproduced this by mutation
(`notes/qa-c0.md`, Mutant 1: 7 of 113 failing, both C1 and P6 red). The criterion's *mechanical*
clause is fully satisfied and P6 is real coverage; only its justification is wrong.

## Pinned against regression vs. merely correct today

- **Pinned** (a suite re-checks them every run): SC-01, SC-02, SC-04, SC-05, SC-08, SC-09, SC-13, and
  SC-11's fleet-shape half (`test-factory-config.py` case 25 + `board_lives_per_repo_not_fleet_level`).
- **Merely correct today** (nothing will ever re-check them): SC-03, SC-06 and SC-07 — no runner
  reads a GitHub board, as the BRIEF's own `## Verification gaps` states, so a later board edit is
  caught only indirectly by SC-05's static pairing assertion; SC-10, a one-time diff fact; SC-12,
  since nothing re-greps the docs.

## Panel accounting — one note

`review-harness-security-reviewer-c0.md` is `PASS`, `severity_max: info`, `must_fix: []`;
`review-harness-code-reviewer-c0.md` is `PASS`, `severity_max: med`, `must_fix: []`. The
**UI-reviewer slot was filled by a code-reviewer spawn**: `review-harness-code-reviewer-c0-ui-scope.md`
records that the write-domain guard rejected the `harness-ui-reviewer` output path and that the
persona sign-off "remains unfilled". The scope-out conclusion (no rendered surface; 38 changed files,
all `.py`/`.yaml`/`.json`/`.md`) is unaffected. Orchestrator's call, not this check's.

## Open questions

- Q1 (non-blocking): SC-10's base `a29ad06` should read `a7c429c` — operator amendment.
- Q2 (non-blocking): SC-13's "C1 is blind to the mutant" rationale is falsified — operator amendment.
- Q3 (non-blocking): the ui-reviewer persona slot was covered by a code-reviewer spawn.
- Q4 (blocking for ship-complete only): SC-06 needs the operator's live run.
