# Handoff — FEAT-31, build phase, mid-flight — written at e5f88c4, run build-eng

## Next

**Collect run `build-eng` from disk — do NOT re-dispatch it.** `harness-eng-lead` was still running
T-02 when this was written; T-01/T-03/T-11 are `complete PASS` in `runs/build-eng/state.yaml`,
T-06/T-07/T-08/T-13 `pending`. Read that state.yaml first — it is the only record of the verdicts,
since the lead's digest was never collected.

Then: (1) route the two must-fix defects below to eng-lead as a fix cycle on T-01; (2) the four
`main-session-direct` tasks — **T-14 then T-10** (T-10 depends_on T-14), **T-04** (unblocks T-05 and
T-09), **T-12** (depends_on T-11, done); (3) T-05 + T-09 as team lanes; (4) qa `test_matrix` gate on
the whole diff; (5) SIMPLIFY; (6) pin `review_sha`; (7) review panel; (8) pm goal-check. The qa gate
was deliberately NOT run on a partial diff.

## Trust

- Both approval gates read `approved`/operator/2026-08-21; `approval:` sha256 `e4cc9491d96635a6…`
  identical in working tree and `git show e5f88c4:` — verified-at e5f88c4
- **DEFECT 1, must-fix: the tool finds ZERO orchestrators by default.**
  `discover_orchestrator_rows` scans `<root>/<session>/subagents`; the real layout is
  `<root>/<project>/<session>/subagents`. 0 matches at the coded depth vs 1999 real, 103 of them
  `agentType: harness-orchestrator`. Blocks SC-01 and SC-10's no-argument UAT.
  `notes/finding-discovery-depth-orchestrator.md` — verified-at e5f88c4
- **DEFECT 2, must-fix: `current` reports 0 for a loaded orchestrator.** `current = sizes[-1]` and
  `sizes` appends 0 for any line lacking `message.usage`. Agent `a7783f0ec41e6a8c6` reports
  `current=0` while holding **696,472** — its last line is a `user` message. 3 of 25 sampled rows
  show it. Defeats REQ-01 and SC-10 question 2 — verified-at e5f88c4
- **`entries` is ambiguous and will fail T-13**, which requires all three figures to agree: the tool
  counts ALL parsed lines (1046 for that agent), a usage-based count gives 669 — verified-at e5f88c4
- **The arithmetic is CORRECT.** Tool and an independent inline recomputation agree to the token on a
  live orchestrator: `current=peak=186,041`. Top-level == sum over non-advisor iterations in 409/418
  multi-iteration entries — verified-at e5f88c4
- **SC-07 and SC-13 have NO implementing task**, per `D-02`'s own "HALF-WRITTEN BY DESIGN". Needs the
  operator before the ship decision — `notes/finding-sc-coverage-orchestrator.md` — verified-at e5f88c4
- Backlog not gate: `iterations` mixes 395 foreign-context `advisor_message` entries and the plan's
  max-over-all rule picks them in 325/395 — but that changes peak and current in 0/74 — verified-at e5f88c4
- Mirror clean: milestone #20, sub-issues #642–#655 on parent #598, 8 cards `Building`, plan.yaml
  statuses written FIRST. `cycles_used` stays 3 — T-01/T-03/T-11 each `cycles: 0` — verified-at e5f88c4
- INV-17 checks heading PRESENCE only (`check-state.sh:509`, membership `:614`) and sits inside the
  `SEAM_NOTES` loop (`:592`) — T-10/T-14 premises hold — verified-at e5f88c4

## Dead ends

- Sending T-01 back for the `advisor_message` filter — faithful to the signed plan, changes no
  published figure — `notes/verify-arithmetic-orchestrator-build.md` — verified-at e5f88c4
- Treating T-02's `# expect NO ... MISCONFIGURED` as a hole. **I was wrong in the dispatch:**
  `run-unit-tests.sh:52-53` prints then `exit 2`, so the exit code carries it — verified-at e5f88c4
- Reproducing the BRIEF's headline figures — its cited transcript (1,497,025 -> 750,837) aged out of
  the 30-day window; `746878` matches nothing in all 76 files — verified-at e5f88c4
- Recording `phase` in feature.json — DEC-192 DELETED the field; the playbook line is stale
  doctrine, not a gap. Phase lives in STATE.md — verified-at e5f88c4
- A second `harness-pm` — issue #628 unfixed; 14 tasks became 1 in 63 seconds here — verified-at e5f88c4

## Working set

- .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/build-eng/state.yaml
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/finding-discovery-depth-orchestrator.md
- .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/finding-sc-coverage-orchestrator.md
- .claude/skills/harness/bin/context-watch.py
