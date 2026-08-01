# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-08-01-19-validator/state.yaml (last complete)
- squad: none — nothing is dispatchable
- status: awaiting-user
- phase: **ship**, unchanged. The feature still sits at its user gate; this run moved no gate.
- note: **THE BRIEFING IS WRITTEN AND THE FEATURE AWAITS THE USER.**
  `notes/ship-review-2026-07-31-16.md` — the one artifact addressed to a human. Three things come back
  from the user and from no agent: the **ship / fix / re-scope / stop** decision; the **SC-13 edit** to
  `.claude/skills/harness/SKILL.md:137,144`, which no agent domain covers; and a **judgement on the
  half-applied `abandon`** (a mid-flight `gh()` failure in the reason-comment step calls `skip()`, which
  is `sys.exit(0)`, so the command can exit 0 having closed nothing — emergent, not a defect against
  anything approved; pm recommends a follow-on BRIEF item and I endorse it). On `ship`, the unstruck
  B-1..B-12 become issues; anything struck dies silently.
  **THE LEAD DISTILLATION DEADLOCK IS CLEARED — runs 17-19, all 13 ops applied by their own owners.**
  This is the one thing this session did. `harness-eng-lead.md` (4 ops: Patterns 3, Gotchas 1),
  `harness-product-lead.md` (6: Patterns 3, Gotchas 2, Outcomes 1) and `harness-validator-lead.md`
  (3: Patterns 2, Open 1) **did not exist at all** and now do. **Nothing was dropped and nothing was
  re-adjudicated** — each lead applied its own recorded judgments verbatim, assigning ids only.
  `check-expertise.sh .harness/expertise/` is **OK on all 11 files, exit 0**, run by me, including the
  title rule added at `99dd80a` after every one of those leads' runs.
  **The defect this repaired was mine.** My close-out dispatch told the leads not to self-apply, reading
  my own G-01 too widely: the domain hook blocks the ORCHESTRATOR from writing another agent's Expertise
  file, but `team-config.yaml` grants each lead its own with `upsert: true`. That left 13 ops with no
  owner. G-01 is corrected, and each lead was told plainly this run that its own file is its own domain.
  **My dispatch also prescribed an illegal digest encoding, and two leads needed a send-back for it.**
  I specified `steps_run: 1` with `members: []`; `validate-digest.py:493-497` rejects that pair. Both
  eng-lead's and product-lead's digest FILES failed my own file-level check (DEC-156) while their returns
  had been accepted — the retry path passes through unvalidated, which is how it got past the hook.
  validator-lead caught it unprompted and encoded correctly the first time. **All three files now return
  `digest ok`**, verified by me after the fix, in two different legal encodings: eng-lead and
  validator-lead as `steps_run: 0` with `members: []`, product-lead as `steps_run: 0` with itself named
  in `members:` to keep the roll-up granular.
  **One blemish left unrepaired, deliberately:** `runs/2026-08-01-18-product/digest.md` still argues in
  prose against the `steps_run: 0` its own block now carries. It is contained in an archived digest and
  does not affect the gate, and at 3x the cost budget I judged another spawn not worth it — recorded here
  rather than fixed, which is the honest trade and not an oversight.
  **Distillation across the whole feature is now closed:** 23 member entries at runs 14-16 plus these 13
  lead entries, and every one of the 11 Expertise files passes its validator.
  **Skips, all recorded rather than silent:** all three GitHub mirror sync points (`github.sync` false,
  `repo` null); the `ui` panel step and visual-designer (no visual surface, no DESIGN.md); ship-refresh
  (no `INDEX.md` and no map dir exists anywhere in the repo).
  **Budgets: cost ~$358 of $120 (3.0x); `cycles_used` 6 of 10, UNCHANGED.** Cost never gates (DEC-134).
  This run added ~$17 measured (eng-lead +5.22, product-lead +5.71, validator-lead +6.21 as snapshot
  deltas) plus my own orchestrator share, which is **not derivable**: no orchestrator cumulative has been
  recorded in a run state file since run 04, so the ~$358 total carries an estimate for my tier and is
  honest-approximate, not precise. `cycles_used` stays 6 deliberately: this repaired a botched close-out
  step of my own, and neither send-back rejected any member's product.

## Open Questions

- **SC-13 (for the user, PRE-SHIP, blocking the feature's completeness)** — the only criterion no agent
  can satisfy. `grep -c 'closes its issue and everything it absorbs' .claude/skills/harness/SKILL.md`
  reads **1** and must read **0**; `:144`'s ship row must name the parent **and** name it conditional on
  recorded origin — a row asserting an unconditional close does not satisfy it. Nothing mechanical
  detects this **by design**: a staleness marker for still-live wording turns `check-docs.sh` red and
  gates every `/harness` entry on an edit no agent may make, so T-08 declared none. Carried in the
  briefing as a named pre-ship step with its exact grep.
- **`abandon` can half-apply (for the user, judgement)** — see the phase note. Emergent, not a defect;
  pm recommends a follow-on BRIEF item and I endorse it. Not adopted as an SC by me — that is not mine.
- **B-13 CANDIDATE, new and NOT in the signed briefing** — `validate-digest.py:493-497` rejects
  `members: []` alongside a non-zero `steps_run`, so a lead's self-executed step (self-distillation is
  the one step a lead performs rather than routes) has no truthful encoding: report `steps_run: 0` and
  the step vanishes from the count, or name yourself in `members:` and the host folds into the roll-up it
  exists to police. Raised independently by product-lead and validator-lead; product-lead proposes either
  allowing `members: []` when host-executed steps account for the count, or a separate `host_steps:`
  counter. Non-blocking. Related second finding: a subagent's re-return after a hook rejection passes
  through unvalidated, so the hook did not catch the bad pair on either lead's retry.
- Backlog candidates B-1..B-12 are enumerated with natures in the briefing and are **not** repeated here
  — the briefing is their single home, and only what survives the user's strike-through becomes an issue.
  Six of the twelve are harness-tooling defects rather than anything this feature built, including the
  bash write-guard's `>` misparse, which blocked me twice more this run.
- Q1..Q8 (pm and eng-lead, from planning) — unowned-domain prose (`SKILL.md`, `harness-brief/SKILL.md`),
  the frozen adopted-parent body, the prototype gate judged not required, the `attached:` receipt schema
  (landed; the suite asserts both survival cases), and the slug judged narrower than the feature
  (immutable under DEC-133). Q8 CLOSED in execution — T-08 routed to product-lead as run 11 (DEC-118).
