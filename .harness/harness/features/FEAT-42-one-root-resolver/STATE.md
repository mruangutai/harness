# STATE

## Current

- feature: FEAT-42-one-root-resolver
- run: none. The main session executed the whole remaining lane directly under DEC-174; no
  orchestrator or squad ran after `2026-08-26-7-eng`.
- squad: none
- status: Building, ALL 21 TASKS `done`. Plan and BRIEF approved 2026-08-27.
- cycles_used: 5 of 10. runs: 7 of 20. Neither moved during the main-session lane, which spends
  neither.
- T-21 was ADDED during the build, main-session-direct, and is the only task not in the signed
  plan. It repairs the three `test-check-state.py` fixtures T-04 broke. Its number is high and
  its position is between T-06 and T-07, which is where it ran.

There is ONE resolver. `git ls-files` minus `test-*`, `harness_boundary.py`, `*.md` and the three
record-tree roots holds ZERO occurrences of the retired environment chain, down from 21 across 17
files at `3952814`. `test-no-distribution.py` case 6 asserts it over that derived set, never a
fixed list, and its mutation proof plants a chain line in `docs/invalid-states-audit.html` —
outside `bin/` on purpose, so a mutant only the repo-wide scan can see is what proves the
widening.

Verified BY ME at disk, 2026-08-27:

- `run-unit-tests.sh --kind all`: EXIT 0, 1040 verdict lines, ZERO failures. The
  baseline before this feature was 1013 lines and zero failures at `a1658c2`.
- `check-state.sh`: 0 violations.
- `check-plan-routes.py` over this plan: 0 violations.
- `.harness/.inflight-claims.json`: `{}`.
- Every task printed its own verify block's OK line.
- Cards #871 through #890 are at Done. T-21 has no card; see Q24.

WHAT THE PLAN DID NOT SAY, and had to. Recorded because the next feature of this shape will hit
all of it again:

- **Every gate's test steered its fixtures with the host-owned variable alone.** `resolve_root`
  reads one name and honours it only when `.harness/team-config.yaml` sits underneath, so after
  each cutover the cases pointed at the LIVE checkout. Eight test files needed both names set to
  one value and a marker written into each fixture root. Four of them were not in their task's
  `files:` at signature.
  The last one surfaced only in the FULL suite: `test-layout-migration.py` drives the REAL
  `check-state.sh` against a fixture to prove its INV-27 block and `layout_migration.render()`
  name the same readers. With one name set the gate resolved to the live checkout, reported
  nothing about the fixture, and seven parity comparisons saw an EMPTY gate side and called it
  a mismatch. Nine test files in total, not eight.
- **Three isolated-copy fixtures needed `harness_boundary.py` copied in beside the script under
  test.** Each exists to neutralise exactly one thing; without the resolver they died on
  ImportError instead, red for the wrong reason. An inconclusive red proof reads exactly like a
  surviving mutant.
- **Six parity proofs were vacuous.** They captured `^(PASS|FAIL)` while those suites print `ok`,
  so T-10's before-set held ONE line and satisfied its `test -s` check. All six now capture
  `^(ok|PASS|FAIL)` against a measured floor. The technique and its three traps are in
  `notes/verify-technique-2026-08-27.md`.
- **Two suites were writing into the LIVE claim registry.** Eight stranded claims accumulated
  during this work and then refused unrelated cases — issue #742 in miniature, from the same
  cause, during the fix for it. Written up in `notes/receipt-main-session-T-18.md`.
- **T-16's instruction contradicted a decision.** It said exit 2 on an unresolvable root;
  `DECISIONS.md:1503` records this hook as "always exits 0 so it can never block a spawn". The
  decision won; the failure still reaches stderr.
- **T-19's five documents are four generated adapters and one skill.** `.claude/agents/*.md` are
  regenerated from `.omp/agents/` by `sync-agent-adapters.py`, which silently deleted all four
  statements the first time. Found by running `check-state.sh` before committing.

## Open Questions

- Q10 (OPEN, non-blocking): `resolve_root` probes with `os.path.isfile`; the deleted
  `check-plan-routes.py` probe used `os.access(..., os.R_OK)`. An unreadable-but-present
  `team-config.yaml` now flips from "not a root" to "is a root". No site is known to reach it.
- Q15 (OPEN, non-blocking, harness defect): `bash-write-guard.sh` refuses a command whose PROSE
  body contains an angle-bracket placeholder or an ASCII arrow, parsing it as a redirect. Three
  occurrences on this feature. Needs its own ticket.
- Q16 (OPEN, non-blocking, harness defect): `gh-sync.py` has `start-task` and no per-task finish
  command, so only `cmd_ship` moves a card to Done and every intermediate move is a direct
  `board-station.py` call. Needs its own ticket.
- Q20 (OPEN, non-blocking, harness defect): `validate-digest.py` releases a returning agent's
  claim (step one) and THEN refuses the return on children-in-flight, so a blocked lead runs on
  unclaimed and is invisible to `dispatch-guard`. T-17 does NOT close it: the session filter
  ignores FOREIGN-session children, and this lead's are same-session and live. Needs its own
  ticket.
- Q24 (NEW, non-blocking, record fidelity): T-21 has no GitHub sub-issue. Every other task has
  one, and `gh-sync.py open` is the command that would create it. Creating an issue is
  outward-facing, so it waits on the operator.
- Q25 (NEW, non-blocking, decision hygiene): DEC-174 amendment 4 enumerates the enforcement layer
  by filename. This feature changed every file on that list and added none, but the list has gone
  stale before and nothing checks it. Ruled worth a ticket earlier and never filed.
