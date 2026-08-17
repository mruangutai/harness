# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: none in flight — T-06 is out as a build card to the main session
- squad: none
- status: building

Mission `build`. Branch `feat/FEAT-23-ship-flow-fixes`, tip `17b7a9d`. **Four of six tasks landed
and committed**, each verified green by this orchestrator on disk before its commit:

- **T-02** `9016628` — `harness-simplify/SKILL.md`. All three tripwires re-checked: dispatch
  literal once, `harness-validator-lead` zero, `code-simplifier` zero.
- **T-01** `d96ab5e` — `gh-sync.py` + `test-gh-sync.py`. `_record_status` is the LAST statement of
  both `cmd_ship` (`:744`) and `cmd_abandon` (`:682`), structural not milestone-gated. Both
  "feature.json is untouched" docstring claims gone.
- **T-05** `e50b8b4` — `board-station.py` + suite + registration. Seven cases run inside the full
  suite; 197 PASS, 0 FAIL, exit 0. Engineer self-disclosed and corrected a TDD order lapse.
- **T-03** `17b7a9d` — the simplify step is sequenced into both playbooks. Verified beyond the
  clause: both anchors still occur exactly once and are byte-unchanged, the DEC-118 sentence on
  line 58 was NOT split, and all seven substantive points are present on a whitespace-normalised
  search (a flat grep gave a false zero on "may not delete or weaken an assertion" purely because
  the line wraps between "may" and "not" — line-wrapping defeats `grep -F` on prose).

**T-06 is out as a build card** — `plan.yaml` `status: building`, `#460` moved to `Building`. Both
its dependencies (T-03, T-05) are done. Measured at `17b7a9d`: verify red, exit 1, marker absent;
`squad plans,` occurs exactly once; T-03's collision conjunct still matches, so the two edits to
`harness-plan.md` have not collided; `board-station.py` and `no ticket is named` both absent as
expected. The insertion window is between `harness-plan.md:5` (step-zero grilling) and `:10`
(Target state). `board-station.py`'s own usage line confirms the intent's claim: the issue number
resolves against `harness.json` `github.repo` (`mruangutai/harness`) and is not a parameter.

Remaining: **T-04 LAST** (team, `harness-documentor`, needs T-03 + T-06 — T-06 is its only
remaining blocker). Then the orchestrator-sequenced qa segment for the `test_matrix` blocking gate,
then the four-angle simplify pass as the last build step — now a RULED step in the playbook this
feature just edited — and only then is `review_sha` re-pinned for the review panel.

Budget: `cycles_used` 3 of 10 — **unchanged this phase.** No task has been routed back and both eng
runs reported zero send-backs. 10 runs of 20.

## Open Questions

- **THIS ORCHESTRATOR'S OWN ERROR, recorded as a failure rather than smoothed over.** I dispatched
  T-05 **twice**. Run `-6-t01t05-eng` returned a digest labelled PROVISIONAL while its member was
  still in flight; I waited out T-01 correctly, then wrongly read the run as finished and spawned
  run `-7-t05-eng` for a task run 6 went on to dispatch itself. **The file that would have stopped
  me is run 6's own `state.yaml`, which records `dispatched_at`/`completed_at` per step and which I
  never opened before re-dispatching.** Cost: one lead run and two member spawns, ~146k subagent
  tokens, zero lines of code. Not a cycle under DEC-157 — no send-back, no rework — so the budget
  is structurally blind to it. It belongs in the briefing as waste.
- **The collision was contained by a tripwire, not by the runner.** `mutates_repo: true` serialises
  within a run and has no reach across runs, so nothing in the team layer could see two live T-05
  writers. What stopped it was one sentence in both dispatches — *a verify that passes on an
  untouched tree is a finding*. Run 7's member hit it, refused to overwrite the authentic `c1`
  receipt, wrote a forensic `c2`, and touched nothing.
- **Harness defect, six recurrences on this feature, and the root of that duplicate.**
  `validate-digest.py --hook` fires on a lead's turn-end while its dispatched member is still in
  flight and will accept only a verdict that cannot yet be truthful. It does not merely produce
  false returns — **it manufactures the disk state that causes duplicate dispatches**: a BLOCKED eng
  digest sitting beside unreceipted new files is exactly the picture that triggered mine. It is a
  DEC-174 enforcement surface, so only the operator may edit it. Earlier recurrences:
  `-3-foldin-product` Q8, `-5-foldin2-product` Q3.
- **Not blocking, left visible rather than absorbed:** T-01's pre-edit RED run is unattested *by the
  member* — its first spawn died on an API connection error before writing anything, and the
  resumed spawn correctly refused to reconstruct a red line it had not observed. Discrimination
  rests on the lead's own pre-dispatch measurement and on `notes/research-FEAT-23-verify-red-runs.md`.
- **GitHub GraphQL returned intermittent 503s all phase.** `close-task` for T-01 failed twice,
  leaving `#455` open with the plan at `done` — INV-26 correctly flagged it; a manual retry closed
  it. Station writes to parent `#454` have now failed five times and are never re-attempted.
  `check-state.sh` exits 0, but **the parent card's station must be re-derived before the briefing.**
- The `bash-write-guard.sh` scratchpad denial is still live (raised by pm). Worked around by piping
  extracted verify clauses to stdin rather than staging a file.
- Non-blocking, raised by the ui reviewer and now partly answered by T-06's intent: how is "the
  operator names the ticket" recognised during a live `/harness-plan` session? T-06 pins it to the
  opening ask or the step-zero grilling answer, with no separate question. No seat owns dialog
  semantics more generally.
- Arch finding G is deliberately unapplied by the operator's signature. Not re-opened.
- Backlog: #350 is CLOSED carrying two unimplemented rulings with no open implementing ticket.
- Backlog: the two accepted costs in DEC-196 — a second board-writing entry point, and a fourth
  copy of the root probe with no importable `harness_root()`.
