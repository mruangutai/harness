# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: **ship phase — SC-10 fully itemised, briefing amended, awaiting the operator's ship
  instruction.** `runs/c19uatsteps-product` (product lead: pm, PASS, ONE send-back) now has its
  durable `digest.md`, `state.yaml`, and `.run-identity.json` restored from the original inline
  product-lead return. No validator run was dispatched or owed: this round wrote records only; the
  c19 code delta stays graded at the pin.
- **SC-10 = MET by the operator, and now itemised.** A SECOND main-session inline relay on
  2026-09-09 carried their verbatim instruction "flag uat pass for these four" against an execution
  report: Step 3b's six flagged merge forms all denied; Step 5's `open` setting
  `build_entry=opened`; Step 6 allowing plain merge and `--no-ff` silently; Step 7's
  `recover-terminal` creating no task issues, setting `recovered-terminal`, merge then allowed.
  Transcribed at `notes/uat-BUG-1309-mirror-build-entry.md:405-463`, append-only — **60 insertions /
  0 deletions by `git diff --numstat`**, so the script is byte-unchanged and no heading moved.
  **No step was executed or re-tested by any agent.**
- **Yesterday's fidelity gap is CLOSED, not inferred away.** The first relay carried an overall
  "pass" plus the Step 3 wording judgement and no per-step readout; the second answers it, so the
  script's five-step rule (3, 3b, 5, 6, 7) is itemised. **SC-10's verdict does not move** — met on
  the first relay, not re-graded or re-derived. Limit 2 (no answers file, none sought or authored,
  issue #671) stands. Steps 4, 8 and 1, 2, 9 were not itemised and are not asserted.
- **Goal-check: 11 of 11 met** — `notes/research-BUG-1309-c19-uat-sc10.md`; its two passages that
  presented the confirmation as outstanding now read closed, and its Non-modification paragraph was
  re-derived at HEAD `a826673` instead of overstating the tree's stillness. SC-04 met **by operator
  ruling**, not by new automated evidence; SC-09 is `verify: inspection`. **No BRIEF amendment or
  re-signature owed.**
- **Briefing amended and re-rendered:** `notes/ship-review-2026-09-09-shipdecision.md` (+ `.html`
  via `render-brief.py`). Decision item 3 — the optional UAT step confirmation — is struck as
  **CLOSED**, leaving **two** operator items: ship-or-not, and the backlog table, B-1..B-29. A
  dated amendment block names what moved; nothing was quietly deleted.
- station: **review** (`plan.yaml` unchanged — `done` belongs to the ship act). `review_sha`
  **unchanged at `4857818bb1408813c7a38311d9e4ffc20373427e`**: records only were written, and
  re-pinning would claim the panel reviewed a tree it never saw.
- budget: **`cycles_used` 18 of 17 — ONE OVER, recorded rather than rounded away.** The lead
  reported one send-back inside this round (pm's Non-modification paragraph returned for
  correction), and a reported send-back is a cycle (DEC-157). **The crossing forecloses fix work**:
  any "fix X" needs the operator to raise the cap first. No fix loop was running. `len(runs)` **57**
  of 20 — INFORMATIONAL (INV-22); read unchanged, in the briefing.
- mirror: unchanged — parent #1407 and nine sub-issues at review; no station moved, so no
  `gh-sync.py` write was owed. Nothing shipped, merged, pushed, committed or removed; `HEAD` stands
  at `a826673` and never moved.

### Evidence, measured rather than relayed

- `git diff --numstat`: UAT note `60 0`; goal-check note `39 14`; pm observations `1 0`. Plus the
  amended briefing, its HTML, `STATE.md`, `feature.json`, `notes/handoff-ship.md`, and the restored
  `runs/c19uatsteps-product/` artifact.
- New section extent `:405-463` (the note's last line); the FIRST relay's heading is at `:362`,
  which corrected the briefing's older `:360-403` citation.
- `feature.json` after the write: `cycles_used` 18, `max_total_cycles` 17, 57 runs, pin unchanged.
- The formerly missing product-run artifact is restored at `runs/c19uatsteps-product/`; the digest
  attributes its reconstruction to the original inline return and preserves that the original
  creation timestamp is unavailable. **B-30 is resolved.**

### Next, in order

1. **The operator's ship instruction** — the only open act; the briefing asks two things now: ship /
   fix / re-scope / stop, and struck backlog IDs. Nothing is dispatchable until it arrives.
2. On "ship": the main session runs `gh-sync.py ship` **from the main checkout** (it refuses a
   feature dir inside `.claude/worktrees/`) with the briefing as `--body-file`; unstruck rows become
   backlog issues; the PR merges under the operator's hand; the `post-merge` hook removes this
   worktree; distillation runs only after the merge (DEC-145).
3. On "fix X": **raise `max_total_cycles` first** — at 18 of 17 no cycle may be opened (DEC-157).

## Open Questions

- Q1 (resolved, 2026-09-08) — SC-04's two evidence gaps: **operator accepted both** on
  inspected-correct source (`notes/research-BUG-1309-c18-sc04-ruling.md`). MET by ruling, NOT by new
  automated evidence; c19 does not regress it. Its two remedies stay unscheduled — rows B-13, B-14.
- Q2 (resolved by delivery, 2026-09-09) — the `merge-gate: ` prefix was RETAINED and the ui reviewer
  confirmed every sibling message still shares that voice.
- Q3 (non-blocking, UAT coverage, pre-existing) — no UAT step exercises the duplicate-claimant
  ambiguity scenario. Row B-21.
- Q4 (non-blocking, harness defect, 5th and 6th sighting) — an agent returned a complete, well-formed
  fenced digest while the host recorded `failed (exit 1) — subagent called yield with null data`.
  Row B-26.
- Q5 (non-blocking, harness defect) — `bash-write-guard.sh` blocked `cp` and shell redirection for a
  read-only role but did not block `python3 -c "open(path,'w')"` run through bash. Row B-27.
- Q6 (non-blocking, backlog) — T-05's `verify:` grade assertion takes `min(grade)` over
  `git_merge`/`words`/`direct_merge`/`gh_merge` and never names `option_end`, `first_subcommand` or
  `merge_target`. Satisfied in fact (5/5/4); the remedy edits approval-gated `plan.yaml`. Row B-19.
- Q7 (non-blocking, backlog) — `merge_target` matches `--abort`/`--continue`/`--quit` by exact token
  equality while git accepts unambiguous abbreviation, so `git merge --abo` would be DENIED.
  Over-deny, never a bypass. Row B-18.
- Q8 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21 names
  while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration. Row B-20.
- Q9 (non-blocking, backlog) — no test can see the loss of the explicit feature name.
  `{command_line}` embeds `realpath(feat_dir)`, whose basename IS the feature id, so
  `"FEAT-9001-fixture-non-era" in reason` (`test-merge-gate.py:69`, `:102`) stays true with `{feat}`
  deleted. Behaviour is correct at the pin — the name appears twice — but the evidence is incidental.
  Remedy: assert on the region BEFORE `Run:`. Needs a cycle licensed to edit the D-11 carved-out
  test file. Row B-15.
- Q10 (non-blocking, backlog, med) — `merge-gate.py:188`, the repo-unpinned deny, still opens
  `{feat} records github.build_entry={value}` — the exact jargon the operator rejected for `:192` in
  this same cycle — and splices a bare `(D-09)` into operator-facing prose. Scoped out by ruling R-7
  §1/§3. The panel's one med. Row B-16.
- Q11 (non-blocking, low) — `merge-gate.py:180` leaks the raw constant name
  `feature_schema.BUILD_ENTRY_ERA_EXEMPT` into operator-facing stderr. Allow path, not deny path.
  Row B-17.
- Q12 (record honesty) — **test-first order for `4857818b` CANNOT be established from the repository
  record**, and qa reported it as such rather than assuming either way: source and both test hunks
  landed in one commit with no intermediate red. The pre-edit red observation was reported by the
  main session and is credible; it is not corroborated by the tree. PRINCIPLES rule 15 — not
  restated as verified. Policy question carried as row B-29.
- Q13 (documentation, trivial) — `notes/rulings-2026-09-08-c19-copy.md` §5.3 cites the
  `recover-terminal … --yes` / not-`open` expectation as "Step 6 (`:300`)"; it is Step 7 at `:303`.
  Stale anchor in the ruling note, not in the UAT. Row B-25.
- **Q14 (RESOLVED 2026-09-09 by the operator)** — raised because the first relay carried no per-step
  readout. Their second inline relay, "flag uat pass for these four", gives Steps 3b, 5, 6 and 7 an
  individual PASS (`notes/uat-BUG-1309-mirror-build-entry.md:405-463`). Never gated the ship; the
  briefing's item 3 is struck closed.
- **Q15 (non-blocking, operator decision)** — `cycles_used` is 18 of 17. Raising
  `max_total_cycles` is the operator's call and precedes ANY fix cycle; it is not needed to ship.
- **SC-10 is CLOSED and itemised (2026-09-09). The last open item is the operator's ship
  instruction — no agent work remains.**
