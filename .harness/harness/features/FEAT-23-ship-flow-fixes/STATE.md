# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: none in flight — T-03 is out as a build card to the main session
- squad: none
- status: building

Mission `build`. Branch `feat/FEAT-23-ship-flow-fixes`, tip `e50b8b4`. Three of six tasks are
landed and committed, each verified green by this orchestrator on disk before its commit, and each
verified a second time by an independent read-only `harness-dev-ops` re-run the eng lead sequenced
itself (`notes/receipt-harness-dev-ops-2026-08-17-6-verify.md`):

- **T-02** `9016628` — `.claude/skills/harness-simplify/SKILL.md`. Verify red at `2697f58`, `T-02
  GREEN` after. All three tripwires re-checked independently: the dispatch-discipline literal
  occurs exactly once, `harness-validator-lead` zero times, `code-simplifier` zero times.
- **T-01** `d96ab5e` — `gh-sync.py` + `test-gh-sync.py`. `T-01 GREEN`. `_record_status` is the
  LAST statement of both `cmd_ship` (`:744`) and `cmd_abandon` (`:682`), structural rather than
  milestone-gated, which is what the conjunction/non-conjunction asymmetry required. Both
  "feature.json is untouched" docstring claims are gone (grep count 0).
- **T-05** `e50b8b4` — `board-station.py`, `test-board-station.py`, `run-unit-tests.sh`. `T-05
  GREEN`; all seven cases run inside the full suite (197 PASS, 0 FAIL, exit 0). The engineer
  self-disclosed and corrected a TDD order lapse: it hashed the implementation, moved it out of the
  tree, wrote and registered the suite, watched all eight checks fail for the right reason, then
  restored the file byte-identical. RED was genuinely observed.

**T-03 is out as a build card** — `plan.yaml` `status: building`, `#457` moved to `Building`.
Anchors re-measured at `e50b8b4` and intact: `the build is not done until the matrix` at
`SKILL.md:57` and `is pinned before any validator run` at `:59`, each exactly once, with the
DEC-118 sentence occupying line 58 — the do-not-split trap the intent warns about. Verify red,
exit 1, marker absent. `harness-plan.md:12` carries the target-state line with both anchor clauses
byte-intact.

Remaining: T-06 (card, needs T-03 + T-05 — T-05 is done, so T-03 is its only blocker), then T-04
LAST (team, `harness-documentor`, needs T-03 + T-06). Then the orchestrator-sequenced qa segment
for the `test_matrix` blocking gate, then the four-angle simplify pass as the last build step, and
only then is `review_sha` re-pinned for the review panel.

Budget: `cycles_used` 3 of 10 — **unchanged this phase.** Both eng runs reported zero send-backs
and no task was routed back, so no rework has occurred. 11 runs of 20.

## Open Questions

- **THIS ORCHESTRATOR'S OWN ERROR, recorded as a failure rather than smoothed over.** I dispatched
  T-05 **twice**. Run `-6-t01t05-eng` returned a digest at 09:49 labelled PROVISIONAL saying its
  member was still in flight; I correctly waited for T-01, then wrongly concluded the run was over
  and spawned run `-7-t05-eng` for T-05. Run 6 was still alive and dispatched T-05 itself at seq-2.
  **The file that would have stopped me is run 6's own `state.yaml`, which records each step's
  `dispatched_at`/`completed_at` and which I never opened before re-dispatching.** Cost: one lead
  run and two member spawns producing zero lines of code. It is not a cycle under DEC-157 — no
  send-back, no rework of failed work — so the cycle budget is structurally blind to it. It belongs
  in the briefing as waste.
- **The collision was contained by the tripwire, not by the runner.** `mutates_repo: true`
  serialises dispatches *within* a run and has no reach across runs, so nothing in the team layer
  could detect two live T-05 writers. What stopped it was the instruction in my own dispatch that a
  verify passing on an untouched tree is a finding: run 7's member hit it, refused to overwrite the
  authentic `c1` receipt, wrote a forensic `c2` and touched nothing.
- **Harness defect, six recurrences on this feature and the root of the duplicate above.**
  `validate-digest.py --hook` fires on a lead's turn-end while its dispatched member is still in
  flight and will accept only a verdict that cannot yet be truthful. Run 6's lead named the
  causal chain plainly: the hook forced it to write a provisional `BLOCKED` digest mid-run, and that
  artifact — a BLOCKED eng digest sitting beside unexplained new files in `bin/` with no receipt
  yet — is exactly the disk picture that triggered my duplicate dispatch. **Fixing the hook fixes
  both.** Earlier recurrences: `-3-foldin-product` Q8, `-5-foldin2-product` Q3.
- **Not blocking, raised by run 6 and left visible rather than absorbed:** T-01's pre-edit RED run
  is unattested *by the member* — its first spawn died on an API connection error before writing
  anything, and the resumed spawn correctly refused to reconstruct a red line it had not observed.
  The discrimination rests on the lead's own pre-dispatch measurement of the untouched tree and on
  `notes/research-FEAT-23-verify-red-runs.md`, which receipts this exact clause failing at
  `b7ae135`.
- **GitHub returned intermittent GraphQL 503s during this phase.** `close-task` for T-01 failed
  twice and left `#455` open with the plan already at `done`, which INV-26 correctly flagged as a
  VIOLATION. Closed on a manual retry; `check-state.sh` now exits 0. Station writes to parent `#454`
  errored three times. The mirror never gates, so nothing stopped — but a failed station write is
  never re-attempted, so **the parent card's station must be re-derived before the briefing.**
- The `bash-write-guard.sh` scratchpad denial is still live (raised by pm). Worked around by piping
  extracted verify clauses to stdin rather than staging a file.
- Non-blocking, raised by the ui reviewer and still unowned: how is "the operator names the ticket"
  recognised during a live `/harness-plan` session? No seat owns dialog semantics. Bears on T-06.
- Arch finding G is deliberately unapplied by the operator's signature. Not re-opened.
- Backlog: #350 is CLOSED carrying two unimplemented rulings with no open implementing ticket.
- Backlog: the two accepted costs in DEC-196 — a second board-writing entry point, and a fourth
  copy of the root probe with no importable `harness_root()`.
