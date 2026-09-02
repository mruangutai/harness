# STATE

## Current

- feature: FEAT-52-factory-control-plane
- run: .harness/harness/features/FEAT-52-factory-control-plane/runs/2026-09-02-01-validator/state.yaml
- squad: none
- status: awaiting-user
- station: plan — SIGNED, and the build cannot be orchestrator-hosted. Both approvals landed on
  2026-09-01 (plan.yaml:3-6 `approved`/mruangutai, BRIEF.md:221-225 `approved`), which cleared the
  one FEAT-52 VIOLATION the previous seq carried; check-state.sh now reports ZERO for this feature
  and its remaining VIOLATIONs are all FEAT-51/BUG-1187, pre-existing and out of scope.
  The build mission then hit a hard authority boundary: **14 of the 15 tasks carry
  `execution_mode: main-session-direct`** — T-01..T-12, T-14, T-15 — and only T-13 is `team`
  (harness-documentor), which `depends_on: [T-12]` and so cannot start either. Per the operator's
  standing instruction the question went to the ADVISOR, not upward: `fable-advisor` was spawned,
  answered all four parts, and ruled **NO** — a spawned harness-orchestrator may not execute those
  tasks, under DEC-174 (DECISIONS.md:4305-4308) and, decisively,
  `.claude/skills/harness/references/github-mirror.md:32-34`, which excludes the orchestrator from
  the mode by name. The validator lead concurred, corrected one analogical citation, and added that
  the seven docs sweeps route main-session-direct under DEC-179 (NOBODY surface), not DEC-174.
  Re-routing them to a squad was ruled out twice over: the plan is signed, so routing is a pm
  re-plan needing a fresh signature, and NOBODY means no squad holds the grant anyway.
  Measured and reported rather than acted on: `HARNESS_AGENT_TYPE` is UNSET in this agent's bash
  env, so enforcement is INERT and the 14 tasks WOULD have written successfully — capability was
  never sanction (DEC-174).
  **FEAT-52 therefore advances zero tasks this run, and that is the correct outcome of a correct
  plan.** Deliverable is the dependency-ordered wave schedule in notes/handoff-build.md, recomputed
  here from the plan's own `depends_on` rather than inherited: W1 T-01,T-02 · W2 T-03,T-04,T-06,
  T-07,T-09 · W3 T-05,T-08,T-11,T-14 · W4 T-10 · W5 T-12 · W6 T-15 and T-13.
  cycles_used 7 of 10 — the one run this session reported 0 send-backs. runs 16 of an
  informational 20. review_sha stays `none`: no code exists to pin. The GitHub mirror was opened
  this run (milestone #41, parent #1220, sub-issues #1221-#1235) so the main session's `start-task`
  bookkeeping has cards to move; the executable list is notes/build-segments-c7.md.
  Handoff: notes/handoff-build.md

## Open Questions

- Q1 OPERATOR, blocking: FEAT-52 cannot advance inside any orchestrator-hosted run. The main
  session must execute the 14 main-session-direct tasks itself, in the wave order above, taking
  each task's `intent:` and `verify:` verbatim from plan.yaml. Confirm that hand-up, or direct pm
  to re-plan the routing under a fresh signature. Evidence:
  runs/2026-09-02-01-validator/digest.md.
- Q2 MAIN SESSION, non-blocking but outstanding: the `ready` seam act has never been made. The
  mirror's station table assigns Ready to the signature, and the plan write and the card write are
  ONE act: `plan-merge.py set-feature-station --station ready` then `gh-sync.py status <dir> ready`.
  It moves the sub-issues only, never the parent (D-18). The GitHub mirror itself is now OPEN — I
  ran `gh-sync.py open` this session: milestone #41, parent #1220, sub-issues #1221-#1235, one per
  task, all 15 attached and recorded in feature.json `github`.
- Q3 OPERATOR, non-blocking: parent #498's own body assigns its refresh to "the main session, at
  ship close", and FEAT-52 appears in none of its unit rows. Nothing about FEAT-52 was written to
  #498 this run. Whether FEAT-52 should be adopted as a unit of #498, or hang from #356 which is
  its only `source_issues` entry, is unrecorded anywhere.
- Q4 (harness owner, security): DEC-120's two enforcement layers were measured INERT under this
  OMP runtime — `HARNESS_AGENT_TYPE` is absent from a subagent's bash env and absence is read as
  the main session. Re-measured this run and unchanged. It means the DEC-174 carve-out is
  currently held by instruction alone, with no mechanism behind it.
- Q5 (harness owner, non-blocking): a member holds no write grant inside a lead run dir (#216);
  `check-domain.sh:1204` admits only a payload whose opening bytes are the prior file verbatim,
  so a recorded digest can be appended to, never prepended; `notes/review-*` is a reviewer path
  a lead cannot write.
- Q6 (harness owner, non-blocking): the feature directory is UNTRACKED — one bare `??` line in
  `git status --porcelain` — so `git show HEAD:<path>` exits 128 and `git diff` is empty for
  changed and unchanged files alike. Any gate proving BRIEF/plan integrity by clean diff on this
  tree is a FALSE GREEN.
- Q7 (record imprecision, deliberately unfixed): PF-4ea5b566's recorded summary says "no literal
  exit statement anywhere"; `inject-expertise.sh` has three (`exit 0` at :28, :49, :137). The
  operative claim survives. Correcting the text would change its content-hash id and invalidate
  any ruling on it, so it is flagged, not edited.
