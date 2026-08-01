# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-16-validator/state.yaml (last complete)
- squad: none — nothing is dispatchable
- status: awaiting-user
- phase: **ship** (was validate). Validate EXITED at panel PASS with `must_fix: []`; the goal-check then
  returned **12 of 12 in-scope SCs met**. Ship ends at a user gate, which is where this now sits.
- note: **THE BRIEFING IS WRITTEN AND THE FEATURE AWAITS THE USER.**
  `notes/ship-review-2026-07-31-16.md` — the one artifact addressed to a human. Three things come back
  from the user and from no agent: the **ship / fix / re-scope / stop** decision; the **SC-13 edit** to
  `.claude/skills/harness/SKILL.md:137,144`, which no agent domain covers; and a **judgement on the
  half-applied `abandon`** (a mid-flight `gh()` failure in the reason-comment step calls `skip()`, which
  is `sys.exit(0)`, so the command can exit 0 having closed nothing — it satisfies SC-12 literally, so it
  is emergent, not a defect against anything approved; pm recommends a follow-on BRIEF item, and I
  endorse that). On `ship`, the unstruck B-1..B-12 become issues; anything struck dies silently.
  **Five commits, all on `feat/harness-native-foundation`, nothing merged and no PR:** `2897b09` T-01,
  `ae728e8` T-02..T-07, `e68ba00` T-08, `4d4c3af` validation bookkeeping, plus this close-out.
  `git log 4d00dbc..HEAD` shows only mine — validator-lead's Q5 (files modified at its spawn) is
  resolved: the two `harness-*/SKILL.md` files were last touched by pre-existing `9a1f638`/`e4a07fb`.
  **Every load-bearing receipt was re-run by me, never taken from a digest.** `run-unit-tests.sh` exit 0
  over three scripts; `check-docs.sh` exit 0; `check-state.sh` all invariants hold; all four SC-06
  payload/lookup absences clean while both carve-out list GETs still count 1; `parent_args|
  blocked_by_args` in `gh-sync.py` = 0; `absorbed #12 #14 NOT closed` present.
  **SC-12's reported evidence gap was a FALSE PREMISE and is closed.** validator-lead read `ship` as a
  new subcommand; `BRIEF:19-20` names it pre-existing, and at the approval commit `cmd_ship` was defined
  while `cmd_abandon` was not. `abandon` is the only new verb and `test-gh-sync.py:529` covers it. **What
  seeded the error is real and is B-2:** `:353`'s label claims "for the new subcommand too (SC-12)" while
  `:351` invokes `open`. A lying test label travelled two tiers as though it were a measurement. Routing
  it to pm rather than adjudicating it myself is what caught it, at the cost of no cycle.
  **Distillation done — and two Expertise files were REPAIRED, not merely extended.**
  All eight `.harness/expertise/*.md` now pass `check-expertise.sh`. `harness-security-reviewer.md` had
  **four pre-existing violations** its member fixed; **my own had eleven** (six entries over the 50-word
  cap, five carrying feature ids), distilled this run — the spawn hook had been injecting a file its own
  validator rejects. Four files were created from absent (documentor, pm, qa, code-reviewer). 23 member
  entries accepted; the digest-skim sourced a majority, so it earned its cycle — though validator-lead
  rightly flags that 8-of-8 acceptance cannot distinguish good sourcing from relay-as-dictation in one
  sample, now `OQ-01` in my own Expertise.
  **13 lead Expertise ops ride up UNAPPLIED in my digest** (eng 4, product 6, validator 3). My dispatch
  told the leads not to self-apply, on an over-generalized reading of my own G-01: the domain hook blocks
  **me** from writing another agent's file, but `team-config.yaml:259` grants each lead its own with
  `upsert: true`. product-lead caught the error and complied anyway. G-01 is now corrected.
  **Skips, all recorded rather than silent:** all three GitHub mirror sync points (`github.sync` false,
  `repo` null — so the mirror posts nothing and every invariant is proven against the fake `gh`); the
  `ui` panel step and visual-designer (no visual surface, no DESIGN.md); ship-refresh (no `INDEX.md` and
  no map dir exists anywhere in the repo).
  **Budgets: cost ~$341 of $120 (2.8x); `cycles_used` 6 of 10.** Cost never gates (DEC-134). ~$162
  predates the build; build ~$74, validation ~$53, close-out ~$49; the six-task build run alone was ~$54
  against `per_run_usd: 15.0`. Three of the six cycles were **prose-only** send-backs — no implementation
  was rejected once — which is why 6 reads heavier than the work was. Both bounds are the user's to
  raise; neither was edited.

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
- **13 unapplied lead Expertise ops** — need an owner. Each lead holds its own file with `upsert: true`,
  so a one-line re-dispatch per lead would apply them; otherwise the main session applies them verbatim.
  If nobody acts, three leads' lessons from this feature are lost, since observations are never injected.
- Backlog candidates B-1..B-12 are enumerated with natures in the briefing and are **not** repeated here
  — the briefing is their single home, and only what survives the user's strike-through becomes an issue.
  Six of the twelve are harness-tooling defects rather than anything this feature built: the bash
  write-guard's `>` misparse (five hits this run), `check-state.sh:109`'s run parser dropping any entry
  with a trailing comment on its `squad:` line, the missing `build` team plus `review.yaml`'s absent `qa`
  step under a **blocking** `qa_gate`, the cost reporter's per-run gap, `validate-digest.py`'s
  `change_type` vocabulary collision, and `check-expertise.sh`'s blind spots.
- Q1..Q8 (pm and eng-lead, from planning) — unowned-domain prose (`SKILL.md`, `harness-brief/SKILL.md`),
  the frozen adopted-parent body, the prototype gate judged not required, the `attached:` receipt schema
  (landed; the suite asserts both survival cases), and the slug judged narrower than the feature
  (immutable under DEC-133). Q8 CLOSED in execution — T-08 routed to product-lead as run 11 (DEC-118).
