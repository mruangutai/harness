# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: **ship phase — SC-10 recorded, briefing written, awaiting the operator's ship instruction.**
  `runs/2026-09-09-c19uat-product/` (product lead: pm, PASS, zero send-backs). No validator run was
  dispatched and none is owed: the c19 copy delta is fully graded at the pin.
- **SC-10 = MET, by the operator.** Their result reached the harness as a main-session inline relay
  on 2026-09-09 — the revised merge-gate refusal message judged CLEAR and ACTIONABLE, reported
  "pass" — and is transcribed at `notes/uat-BUG-1309-mirror-build-entry.md:360-403`, append-only,
  **45 insertions / 0 deletions verified with `git diff --numstat`**, so the script itself is
  byte-unchanged. Attributed to that channel throughout, never restated as an agent measurement.
  **Fidelity limit, recorded and NOT resolved by inference:** the relay carried an overall "pass"
  plus the Step 3 wording judgement, and no per-step readout of the note's own five-step verdict
  rule (Steps 3, 3b, 5, 6, 7). One optional confirmation line for the operator, not a downgrade,
  and the operator was not re-graded.
- **Goal-check: 11 of 11 criteria met — the goal is fully met.**
  `notes/research-BUG-1309-c19-uat-sc10.md`, one row per SC with a cited evidence path. SC-04 reads
  met **by operator ruling** on inspected-correct source, explicitly NOT by new automated evidence;
  SC-09 is `verify: inspection` by the brief's own declaration; SC-10 carries the relay as its
  provenance. pm re-read the SC-04 and SC-10 criterion texts: **no BRIEF amendment and no
  re-signature are owed** — no criterion text moves.
- **Briefing written and rendered:** `notes/ship-review-2026-09-09-shipdecision.md` (+ `.html` via
  `render-brief.py`, never hand-authored). It subsumes the undisposed B-1..B-13 of
  `notes/ship-review-2026-09-08-resume.md` into one fresh table **B-1..B-29** and names the three
  operator items: ship-or-not, strike backlog rows, optional UAT step confirmation.
- station: **review** (`plan.yaml` `status:`, unchanged — `done` belongs to the ship act, which has
  not happened). `review_sha` **unchanged at `4857818bb1408813c7a38311d9e4ffc20373427e`**: this
  phase wrote only feature-dir artifacts, and re-pinning would claim the panel reviewed a tree it
  never saw.
- budget: **`cycles_used` 17 of `max_total_cycles` 17 — UNCHANGED.** The product run reported zero
  send-backs and a clean first-pass run adds zero cycles (DEC-157). Any further fix work needs the
  operator to raise the cap, which is why every residual is a backlog row and not a fix cycle.
  `len(runs)` **56** of `max_total_runs` 20 — INFORMATIONAL (INV-22). My read, in the briefing too:
  honest but no longer cheap — the last four cycles closed evidence and wording rather than
  behaviour, which is what convergence looks like from the inside; a 57th run would not earn its
  place.
- mirror: unchanged — parent #1407 and nine sub-issues at review. No station moved, so no
  `gh-sync.py` write was owed. Nothing shipped, merged, pushed, or removed; `HEAD` never moved.
- quarantine: `quarantine.py list --feature BUG-1309-mirror-build-entry` → empty.

### Evidence for this phase, measured rather than relayed

- **Append-only shape of the UAT edit:** `git diff --numstat` → `45 0` on the UAT note; the only
  other working-tree changes are pm's new goal-check note and its observations bullet.
- **Both approval signatures, checked in both fragments (G-09):** `BRIEF.md ## Approval`
  `status: approved`, re-signed 2026-09-08 over SC-11; `plan.yaml approval` `status: approved`,
  `date: '2026-09-08'`. Walked the plan's commit history: the re-sign commit **`de04d841`** lands
  AFTER `d8f4dc49` (the D-13..D-15 amendment), so the plan signature covers those amendments. D-19
  was appended afterwards under ruling R-7 §4, which owes no re-signature. D-13 … D-19 are all
  present (`plan.yaml:203,225,244,263,291,308,330`).
- **Old backlog row struck on my own measurement:** the 2026-09-08 briefing's B-6 (module-scope
  `feature_schema` import costing ~50-60 ms per Bash call) is **resolved** — at the pin the import
  is deferred inside the deny path (`merge-gate.py:164`). Its sibling `feat = "this feature"`
  fallback **does** survive at `:163` and is carried as the new B-6.

### Next, in order

1. **The operator's ship instruction** — the only open act. The briefing asks for: ship / fix /
   re-scope / stop, struck backlog IDs, and optionally whether Steps 3b/5/6/7 also passed. Nothing
   is dispatchable until it arrives; no agent work remains.
2. On "ship": the main session runs `gh-sync.py ship` **from the main checkout** (it refuses a
   feature dir inside `.claude/worktrees/`) with the briefing as `--body-file`, unstruck rows become
   backlog issues, the PR merges under the operator's hand, the `post-merge` hook removes this
   worktree, and feature-close distillation runs only after the merge (DEC-145).

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
- **Q14 (NEW 2026-09-09, non-blocking, optional confirmation)** — the SC-10 relay carried no
  per-step readout. Whether Steps 3b, 5, 6 and 7 were each individually observed to PASS is not in
  the record and was not inferred. The briefing offers it as one line; it does not gate the ship.
- **SC-10 is CLOSED (2026-09-09). The last open item is the operator's ship instruction — no agent
  work remains on this feature.**
