# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: (build phase opening — first run dir is 2026-07-31-09-eng)
- squad: eng
- status: in-progress
- phase: **build** (was plan). Exit predicate (DEC-148): every T-01..T-08 carries a PASS run in
  `feature.yaml runs:`.
- note: **The approval gate PASSED and was verified first-hand, not trusted from the dispatch.**
  BRIEF:233 and PLAN:653 both read `status: approved` / `approved-by: Mike Ruangutai` /
  `date: 2026-07-31`, signed at `4d00dbc`; `check-state.sh` exits 0 ("all state invariants hold"),
  which also retires Q10's symptom. The plan-phase handoff note (seq-4) said "wait for the
  signature" — that `## Next` is now satisfied, which is why the build starts rather than blocks.
  **All three GitHub mirror sync points are SKIPPED for the whole feature** — `harness.json`
  `github.sync: false`, `github.repo: null`, so `gh-sync.py open`, `close-task` and `ship` post
  nothing (DEC-138: environmental failure is a SKIP, never a gate). Recorded in
  `skipped_segments`. Every GitHub Issues invariant this feature builds is therefore proven against
  `test-gh-sync.py`'s fake `gh` only — BRIEF `## Verification gaps` already states this and DEC-168's
  measured probe carries the live API behaviour.
  **Build dispatch shape — three runs, because no `build` team yaml exists (Q9).** Step lists are
  passed inline; naming a nonexistent team would make the lead list-and-stop per `harness-team` §1.
  - **09-eng: T-01 ALONE, as a real boundary.** T-01 is `change_type: config`, whose `test_matrix`
    row is `always: []` — no qa gate will ever cover it, so its own `verify:` block is the only
    check that exists. Eight SCs claim `evidence: unit`, and `unit` is not a runner until T-01
    lands. The load-bearing property is STREAMING (PLAN:144-151): a runner that captured child
    output would satisfy "one PASS/FAIL line per script" and silently void five downstream verifies.
    Gate on the `ALL PASSED` line emitted by `test-gh-sync.py` **itself**, re-checked by the
    orchestrator before T-02 dispatches.
  - **10-eng: T-02..T-07 sequential.** T-03..T-06 all edit `gh-sync.py` + `test-gh-sync.py`, so
    `mutates_repo: true` serializes them however the DAG is drawn; one lead spawn beats five.
  - **11-product: T-08** — the lateral hop (Q8). `harness-documentor` is a product-squad member
    (`team-config.yaml:112`), so eng-lead cannot spawn it; the orchestrator routes it (DEC-118).
    After eng, not parallel: SC-11 reads `check-docs.sh` and `check-state.sh` INV-10 across the repo.
  **Goal-check will be scoped SC-01..SC-12, with SC-13 carved out in the dispatch text.** Not a
  waiver: PLAN `## Preconditions and hand-offs` records SC-13 as a **main-session** pre-ship step
  and no agent domain covers `.claude/skills/harness/SKILL.md`. Handing all 13 to pm returns SC-13
  unmet, FAILs the roll-up, and demands a fix cycle routable to no lead — precisely the
  BLOCKED-on-an-unowned-criterion outcome Q13 predicts. It rides up as an `open_question` and a
  named pre-ship step in the briefing instead, carrying its exact grep and fix cycle 3's raised bar
  (the `:144` ship row must name the parent **and** name it conditional on recorded origin).
  **Cost is OVER budget before the build's first dispatch: ~$162 of $120, by ~$42.** Reported, never
  gated (DEC-134). Expect the 10-eng run to exceed `per_run_usd: 15.0` as well — six tasks, one
  lead, member spawns each. Neither figure stops work.
  Tree state at build start: one held-dirt file, `.harness/logs/2026-07-31.md` (the main session's),
  which must never be staged. Commits go by explicit pathspec with `git commit -F` (Q14).

## Open Questions

- Q17 (eng-lead, non-blocking, cosmetic) — **four PLAN sites cite `feature.yaml:41` for
  `parent: none` and the line keeps moving** (`:54`, then `:61`, and again this cycle when the phase
  transition was recorded — proof the anchor class is inherently unstable, not that one number is
  stale). Sites: PLAN `:88`, `:464`, `:479`, `:529`. The asserted FACT is true in every case, so
  nothing is falsified. Fix by citing the field (`feature.yaml github.parent`) rather than a line,
  in one pass, only if a cycle opens anyway. Proposed for the ship backlog as a chore.
- Q13 (for the user, pre-ship) — **SC-13 is a success criterion only the main session can satisfy.**
  Its subject (`.claude/skills/harness/SKILL.md:137,144`) is covered by no agent domain; MF-5's
  remedy rests entirely on that edit, eng-lead having accepted a softening of its run-02 wording
  (the `<!-- stale: -->` marker became optional, with SC-13's ship-gate grep substituted as the
  detection mechanism). T-08 must declare **no** marker for still-live wording — a marker whose
  phrase is still present turns `check-docs.sh` red and gates every `/harness` entry on an edit no
  agent may make. Carved out of the agent goal-check; returned to the main session as a named
  pre-ship step.
- Q14 (orchestrator, harness defect) — `bash-write-guard.sh` scans the WHOLE bash command string,
  including quoted and heredoc CONTENT, and reads any `>` in it as a shell redirect. **Reproduced
  again this run:** a read-only `python3 -c` printing `test_matrix` rows was BLOCKED because the
  literal `->` inside a print argument parsed as a redirect target. Four distinct hit classes now:
  the mandated `Co-Authored-By: … <noreply@anthropic.com>` trailer, an arrow in heredoc prose, a
  heredoc that "targets GitHub", and now an arrow in a `-c` string. The workaround is "avoid `>` in
  ANY bash prose": commit messages via `git commit -F <file>`. A rule backfiring on content it
  should not parse — a bug to file, never a workaround to keep.
- Q11 (orchestrator, harness defect) — the playbook's
  `cost-report.py --yaml >> <run_dir>/state.yaml` append produces a duplicate top-level `cost:` key
  beside the lead's `cost: pending_orchestrator`, which `check-state.sh` rejects per DEC-156. The
  obvious fix (renaming the placeholder) is ALSO rejected: `CHECKPOINT_KEYS`
  (`check-state.sh:258-268`) admits only `cost`, so the metered figure must nest as `cost.run_usd`.
  Hand-resolved that way in all eight prior run dirs; the playbook instruction and the invariant
  still disagree.
- Q10 (orchestrator, harness defect) — `check-state.sh` infers a cycle from any FAIL run, so it
  fired a VIOLATION on the legitimate "FAIL held at the user gate" state DEC-157 defines as zero
  cycles. Symptom retired now that both artifacts are approved and it exits 0; the
  over-approximation is still a defect. Also asymmetric: a pending PLAN is a `note`, a pending BRIEF
  a VIOLATION — yet a plan mission ends with both pending.
- Q9 (eng-lead, harness gap) — **no `build` team yaml exists** (only `gate-probe.yaml`,
  `review.yaml`). Worked around this run by passing inline step lists; the gap is real and reaches
  every future build phase. Proposed for the ship backlog as a chore.
- Q1 / Q2 (pm) — `.claude/skills/harness/SKILL.md:137,144` and
  `.claude/skills/harness-brief/SKILL.md` (the BRIEF-H1 parent-title contract) both state contracts
  this feature changes, and no agent domain covers either file. Q1 is ANSWERED IN PLAN, not closed
  (see Q13). Q2 is unowned and out of this BRIEF.
- Q3 (pm) — freezing an adopted wayfinding map issue's body at hand-off is settled in the grilling
  but scoped out of this BRIEF; nobody owns it.
- Q4 (pm) — prototype gate: pm judged NO prototype required (re-confirmed at cycle 1), substituting
  for visual-designer, which never ran. Overridable.
- Q5 (pm) — PLAN adds an `attached:` receipt list to `feature.yaml github:`, a local-state schema
  addition the grilling did not name. eng-lead judged it safely writable under the regex constraint,
  with one sharp edge: the issues reader `^\s{4}(T-\d+):\s*(\d+)` would misread a nested form. Fix
  cycle 2's `parent_origin` key rides the same constraint and was shaped to clear it.
- Q6 (pm) — pm judges the slug `subissue-mirror` narrower than the feature; id not renamed, and
  DEC-133 makes it immutable now.
- Q8 (eng-lead) — RESOLVED IN SHAPE: T-08's owner `harness-documentor` is product squad, so the
  orchestrator routes it to product-lead as run 11 (DEC-118). Kept for the record.
