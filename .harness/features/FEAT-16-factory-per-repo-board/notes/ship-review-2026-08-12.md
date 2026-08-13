# FEAT-16 — a board per repository — ship review

Closes **#262**. Eleven tasks, 23 commits, four gates green, **12 of 13 success criteria met**.

## What breaks today, and what stops breaking

`fleet.yaml` declared **one board for the whole fleet**. Every product's stations were read off
whichever board the fleet happened to name, so the moment a second product is added, the factory
moves cards on the first product's board. With one product declared, that is invisible.

After this change each `repos:` entry carries its own `board:` block, and `factory_claim`,
`factory_decompose` and `factory_land` each address the board of the repository they are acting on.
A fleet carrying a leftover top-level `board:` is now **rejected**, so the old shape cannot survive
half-migrated.

## The change

| File | What |
|---|---|
| `factory_config.py` | `load_fleet` learns a per-repo board; `board_for` and a repo-scoped station lookup |
| `factory_claim.py` | reads a board only once it knows whose board it is |
| `factory_decompose.py`, `factory_land.py` | publish and land against the acted-on repository's board |
| `fleet.yaml` | top-level board removed; kaya-ai carries its own on board 2 |
| six test files | fixtures migrated; the repo-to-board pairing pinned where a unit gate sees it |
| `DECISIONS.md`, `SPEC.md` | DEC-174 amendment 2, and three falsehoods this feature created |

## Gates, run on the branch

| Gate | Result |
|---|---|
| `check-state.sh` | exit 0 |
| `check-plan-routes.py` | `0 violation(s) across 8 plan(s)` |
| `run-unit-tests.sh --kind unit` | 75 PASS, 0 FAIL |
| `run-unit-tests.sh --kind integration` | 80 PASS, 0 FAIL |
| qa gate (blocking) | `matrix_ok: true` |
| review panel | `severity_max: med`, `must_fix: []` — below the `high` bar, no fix cycle owed |

T-07's precondition was **read, not assumed**: both boards offer `Backlog, Plan, Ready, Building,
Review, Done` in that order, and board 2's distribution matched the signed figures exactly — 211
items, 118 Done, 82 Backlog, 11 Building, zero in each of Plan, Ready and Review. No board was
touched in either direction. The capture is `notes/board2-capture.md`.

## What this does NOT close, stated rather than left to be found

**SC-06 is `not_met`, and it is the only criterion that leaves the fixtures behind.** It requires a
live factory claim against a real kaya-ai issue on board 2, with the new station **read back off the
board** rather than inferred from an exit code. It is `verify: uat`, operator-owned, and it mutates
live product state, so no agent may perform it and no gate can close it.

It is also blocked by a prerequisite nobody wrote down: **board 2's `Ready` station is empty** — 0 of
211 items. A live claim run today would correctly report `no work available` and exit 1, proving
SC-13 rather than SC-06. An issue must first be promoted to `Ready`.

So the per-repo routing is proven **against fixtures and against the local declaration**, and is
unproven **against the live product board**. SC-04 and SC-05 are the fixture proofs; SC-06 is the
one that would settle it.

**Five criteria are correct today and guarded by nothing.** SC-03, SC-06, SC-07, SC-10 and SC-12 are
inspection-verified. If anyone renames a station on board 2 or 3, or reorders the six options, this
feature's central promise breaks and **no gate anywhere will say so**. SC-05 catches the board
*number* drifting from its repository; it cannot see the station *vocabulary* drifting on the board.

**Two defects in the signed BRIEF, recorded and not repaired.** SC-10's base `a29ad06` is stale —
run literally it false-positives on all four DEC-174 carve-out scripts, because FEAT-17 changed them
on `main` between plan time and this branch. The feature's own diff touches none of the four, so the
criterion holds on intent and its base should read `a7c429c`. And SC-13's *rationale* is falsified at
source: `factory_claim.py:293` is the sole `no work available` call site and is an aggregate check
after the per-repository loop, so the mutant it names also kills the pre-existing case. The coverage
is real and mutation-proved; only the justification is wrong. **Amending a signed BRIEF is a
re-signature, not a record correction, so both are left standing for the operator.**

**Three fixes the plan never named**, each a falsehood this feature itself created: `SPEC.md:426`'s
onboarding sentence, `SPEC.md:415`'s table row, and — the one that mattered —
`factory_config.py`'s error message told a blocked operator to add three fields when
`_validate_board` requires four and checks the missing one first. Following it could not succeed,
and `check-domain.sh` fails closed meanwhile, so the symptom was every agent write blocked.

**Eight backlog items** are recorded in the handoff, including one that closes only with a fixture
that fails pre-change, and two harness defects: a write that landed on a path resolving to `NOBODY`
and could not be reproduced, and `bash-write-guard.sh` parsing command *text* so a `$VAR` redirect
is denied while the identical literal path is allowed.

## The mirror

`gh-sync.py open` was **blocked by the permission classifier** for the whole build — not by the
environment — so FEAT-16 had no milestone and no mirrored issues while it was built. The playbook
makes that a SKIP and never a gate, so nothing stopped and nothing complained. The main session ran
it afterwards: milestone #9, parent #299, issues #300-#310, all eleven closed to match the work.

**That is issue #277 happening live during this feature.** A mirror that never ran and one that ran
cleanly were indistinguishable from outside.
