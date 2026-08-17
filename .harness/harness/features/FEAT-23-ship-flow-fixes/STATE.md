# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: none — main-session-direct segment (T-02); no lead run in flight
- squad: none
- status: building

Mission `build`, phase entered 2026-08-17 after the operator signed BRIEF and plan as one (both
approval blocks read `approved`). Branch `feat/FEAT-23-ship-flow-fixes` at `2697f58`; the signed
plan is committed on it; `gh-sync.py open` recorded milestone 14, parent #454, tasks #455–#460.

**T-02 is out as a build card to the main session** — `status: building` in `plan.yaml`,
`gh-sync.py start-task` moved #456 and parent #454 to `Building` (exit 0, both writes landed).
T-02 is `main-session-direct` because `check-domain.sh --resolve` returns NOBODY for
`.claude/skills/**`; the same reason covers T-03 and T-06.

Verified by this orchestrator at HEAD `2697f58`, not inherited: T-02's `verify` clause, extracted
by `yaml.safe_load` and never retyped, exits 1 with `T-02: .claude/skills/harness-simplify/SKILL.md
does not exist`. A green here would have been a finding.

Sequencing from here (dependency order, not plan order): T-02 (card, out now) → T-01 + T-05 as ONE
eng build team run, both dependency-free and both resolving to `harness-backend-dev` → T-03 (card,
needs T-02) → T-06 (card, needs T-03 + T-05) → T-04 LAST (team, `harness-documentor`, needs T-03 +
T-06). Then the orchestrator-sequenced qa segment (`test_matrix`, the only blocking gate), then the
four-angle simplify pass as the last build step, and only then is `review_sha` re-pinned for the
review panel.

Budget: `cycles_used` 3 of 10, carried from the plan phase. 8 runs of 20.

## Open Questions

- Harness defect, carried from the plan phase: **lead spawns are intermittently provisioned without
  the `Agent` tool their agent files grant.** Retries succeeded every time. Budget retries in the
  T-01/T-05 and T-04 team runs; do not treat a first failure as a blocker.
- Harness defect, carried: **lead returns went false about the disk four times** —
  `validate-digest.py --hook` fires on a lead's turn-end while its dispatched member is still in
  flight and extracts a premature verdict. Cause named in
  `runs/2026-08-17-5-foldin2-product/digest.md` Q3. **Disk is authoritative over any lead return on
  this feature**; verify `files_touched` against the artifacts before recording a verdict.
- Arch finding G is deliberately unapplied by the operator's signature note. Do not re-open it.
- Non-blocking, raised by pm: `bash-write-guard.sh` denies writes to the session scratchpad the
  harness itself designates for temp files. Worked around by extracting verify clauses to stdin
  rather than to a file.
- Non-blocking, raised by the ui reviewer: how is "the operator names the ticket" recognised during
  a live `/harness-plan` session? No seat owns dialog semantics. Bears on T-06.
- Backlog: #350 is CLOSED carrying two unimplemented rulings with no open implementing ticket.
- Backlog: the two accepted costs in DEC-196 — a second board-writing entry point, and a fourth
  copy of the root probe with no importable `harness_root()`.
