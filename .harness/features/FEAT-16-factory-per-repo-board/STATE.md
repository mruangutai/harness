# STATE

## Current

- feature: FEAT-16-factory-per-repo-board
- run: .harness/features/FEAT-16-factory-per-repo-board/runs/2026-08-12-4-product/state.yaml
- squad: product
- status: awaiting_user — 12 of 13 SCs met; SC-06 needs the operator's live run
- next: the operator's UAT (SC-06) — a live factory claim against a throwaway kaya-ai issue on board
  2, per `BRIEF.md ## Constraints`. Then the ship decision. No agent work is outstanding.

**All eleven tasks are done and every gate has run.** qa gate `matrix_ok: true` (unit exit 0,
integration exit 0). Reviewer panel `severity_max: med`, `must_fix: []` — below the `high` bar that
`gates.review: advisory_unless_high` makes blocking, so no fix cycle is owed. Goal-check: 12 met,
SC-06 `not_met` exactly as the BRIEF predicts.

**`review_sha` is pinned at `ec195ec`**, which contains all eleven tasks and both post-plan fixes.
Commits after it are bookkeeping and reviewer artifacts only, with nothing reviewable in them.

**Eight criteria are pinned by the suite; five are merely correct today.** SC-03, SC-06, SC-07,
SC-10 and SC-12 rest on live GitHub reads or one-off inspection that no runner ever re-executes.
Concretely: if anyone renames a station on board 2 or 3, or reorders the six options, the feature's
central promise breaks and **no gate anywhere will say so**. SC-05's static assertion catches the
board NUMBER drifting from its repository, never the station vocabulary drifting on the board. The
BRIEF predicted this in `## Verification gaps`; the goal-check confirms it survived into delivery.

**Two defects in the signed BRIEF, recorded and deliberately NOT repaired.** SC-10's base `a29ad06`
is stale — run literally it flags all four DEC-174 carve-out scripts, because FEAT-17 changed them
on main between plan time and this branch's start; the feature's own diff `a7c429c..ec195ec` touches
none of the four, so the criterion holds on intent and its base should read `a7c429c`. And SC-13's
rationale is falsified at source: `factory_claim.py:293` is the sole `no work available` call site
and it is an AGGREGATE check after the per-repository loop, so the mutant it names kills the
pre-existing case C1 too. The coverage is real and mutation-proved; only the justification is wrong.
Amending a signed BRIEF is the operator's.

**Three post-plan fixes landed that the plan never named**, each a falsehood this feature itself
created: `SPEC.md:426`'s onboarding sentence, `SPEC.md:415`'s table row, and — the one that mattered
— `factory_config.py`'s error message, which told a blocked operator to add three fields when
`_validate_board` requires four and checks the missing one first. Advisor-decided under the
operator's standing authorisation; `plan.yaml` was not amended.

**The panel's one finding worth acting on is a test that does not guard.**
`test-factory-claim.py`'s P5 is labelled as proving T-02's de-duplication, but the candidate loop
breaks on the first winner at `factory_claim.py:367`, so its assertions pass with the de-dup line
deleted. Live behaviour is correct; the guard is not. It is a hand-trace, not a killed mutant, so it
closes only with a fixture that fails before the change. Backlogged as B-1 rather than fixed here:
test code landing now would land after the pin and evade the panel entirely.

**Cycles 4 of 10, runs 11 of 20.** The single rework event was mine — I pinned a HEAD sha
(`5c46534`) that does not exist, having asserted it without running `rev-parse`; one lead halted on
it as instructed and the other proceeded on invariants. Both leads reported zero send-backs across
every run. Separately, validator-lead disclosed six spawns (~330k tokens) lost to its own dispatch
errors, one of which overwrote the first code review at its shared path — those findings now survive
only inside a gitignored run digest, which is why they are restated here.

## Open Questions

- Q1 (BLOCKING, operator only): SC-06's live factory claim run against a throwaway kaya-ai issue on
  board 2. It mutates a live board, so no agent may perform it and no gate can close it.
- Q2 (non-blocking): amend SC-10's base to `a7c429c`, or record the discrepancy as known?
- Q3 (non-blocking): amend SC-13's rationale, or record it as a known inaccuracy?
- Q4 (non-blocking, HARNESS DEFECT): `.claude/skills/harness/references/missions.md` was modified
  during the T-10 run — a path that resolves to NOBODY under `check-domain.sh --resolve`. I reverted
  and byte-verified it, and could not reproduce the channel: the hook denies every agent against
  Write, Edit, MultiEdit and NotebookEdit for that path, and `bash-write-guard.sh` is live enough to
  have blocked my own probe. The decision layer is sound and a write landed anyway.
- Q5 (non-blocking, HARNESS DEFECT): `bash-write-guard.sh` parses command TEXT rather than the
  shell-expanded path, so a redirect through a `$VAR` is denied while the identical literal path is
  allowed. I hit this myself twice.
- Q6 (non-blocking, ROUTING WALL): `harness-qa` holds no write grant over
  `.claude/skills/harness/bin/**`, so a qa segment asked to close a coverage gap in this
  repository's own suite is blocked by construction and must route to eng. Fifth recurrence of the
  class `team-config.yaml:224-230` already names.
- Q7 (non-blocking): the GitHub mirror never opened — `gh-sync.py open` was blocked by the
  permission classifier at the start of the build phase. The playbook makes it a SKIP and never a
  gate, so the feature proceeded, but FEAT-16 has no milestone and no mirrored issues.
