# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-01-eng/state.yaml
- squad: eng
- status: in_progress

BUILD PHASE COMPLETE — every build segment has landed and the worktree is clean at the branch tip.
The Building → Review seam is the next act and is deliberately NOT taken in this run: `review_sha`
is still `none`, and nothing has been pinned or synced. This section IS the build→validate handoff:
`notes/handoff-build.md` could not be written from a worktree (Q8 below), so the successor's
working memory lives here.

- Eng segment (2026-09-07-06-eng, PASS): T-01 at 88a627da, T-02 at 97e715d1, both tasks at station
  `done` in plan.yaml. The interrupted predecessor had committed the code but never recorded the
  run; that was reconciled at 2e1f7142 after the orchestrator re-ran both suites green at HEAD.
- QA segment (2026-09-07-1-validator, PASS) — the project's one blocking gate, green on
  measurement rather than on a receipt's word: both required matrix kinds satisfied (unit, plus
  integration added above the floor for the CLI-boundary SCs), unit 520 PASS / 0 FAIL, integration
  1513 PASS / 0 FAIL, both task `verify:` blocks verbatim at exit 0, and all six new checks proven
  to redden under a live mutation of the guard's call site in a disposable copy — which closes
  D-08's stated risk that a well-named check can pass on a weak assertion. All six SCs graded PASS
  by qa (SC-06 by inspection, as the BRIEF declares). Artifact: notes/qa-BUG-276-c0.md.
- SIMPLIFY (2026-09-07-01-eng, PASS): an EMPTY pass — four independent readers, zero applies, so
  the tip is unmoved and `review_sha` may pin at it. Reuse settled both questions the diff raised
  at source: `_check_proposal_duplicate_ids` walks raw proposal 2-tuples pre-resolution while
  `_check_proposal_ambiguity` walks resolved 5-tuples that exist only after base comparison, so
  they are different properties and D-02/D-03's separation stands; and the new cases already use
  the files' existing fixture helpers. Efficiency measured the guard as O(n≤15) on a
  once-per-distillation path. Seven findings reported-not-applied, all low or info.

Both segments reported 0 send-backs, so `cycles_used` stays 2 of 10. `len(runs)` is 9 of an
informational 20.

NEXT, for the validate successor (one act at a time, in this order): pin `review_sha` in
feature.json at the branch TIP via `feature-json-merge.py set-key` — not at the end of the code
range 6d969ed3..97e715d1, because bookkeeping commits sit above it and a pin must CONTAIN the work
— then `gh-sync.py status <feature-dir> review` with a LOWERCASE station, and only then dispatch
the review panel to harness-validator-lead over that code range, spec compliance before code
quality. Trust, all verified at 76066fbc unless noted: both tasks committed and at station `done`
with approval `approved` and no rulings (plan.yaml:3-7,176,286); qa's tallies and its mutation
proof (runs/2026-09-07-1-validator/digest.md); simplify empty (runs/2026-09-07-01-eng/digest.md);
the defect is FIRST-wins, not the last-wins the ticket asserts (PF-15e24dab70b6caca5bf5ba4837356157).
Dead ends for validate, all signed: D-07 (parse_expertise/render drop stays unfixed), D-09 (no
exit-11 row in harness-distill/SKILL.md, lane NOBODY), D-04 (check-expertise.sh untouched), D-05
(no codes 10 or 12 in the docstring — adding them FAILS SC-06). Working set: plan.yaml, BRIEF.md,
notes/qa-BUG-276-c0.md, .claude/skills/harness/bin/expertise-merge.py, feature.json.

## Open Questions

None blocking. The qa and simplify runs added four non-gating items; the signature-time four are
settled or residual as recorded.

- Q8 (harness defect, non-blocking, MEASURED this run — do not re-diagnose): a handoff note cannot
  be written from inside a worktree. `check-domain`'s handoff-shape check resolves every authority
  pointer against the MAIN checkout — it reported `brief-sc:SC-06` and `brief-sc:SC-03` unresolved
  in `/Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-276-.../BRIEF.md`,
  ENOENT, because the feature directory exists only in the worktree. Every legal authority type
  resolves under that same directory, so no pointer set can pass and the note is unwritable here.
  STATE.md `## Current` carries the handoff instead, which DEC-159 permits as the disk-only path.
- Q5 (harness defect, non-blocking): `check-domain.sh`'s worktree-claim guard matches a live claim
  by agent-type STRING alone (`inflight_registry.live_claims` / `claim_worktrees`), never by
  session or feature. A concurrent unrelated harness-qa gate for BUG-240 became the qa session's
  entire allowed claim set and blocked a write into BUG-276's own tree until qa registered its own
  claim by hand. For the harness owner; not Expertise.
- Q6 (non-blocking): `test_matrix`'s `__bug_class__` / `match_bug_class` predicate is an
  unresolvable placeholder with no taxonomy entries, so that leg can never fire and never be
  audited. Remove it, or give it a taxonomy?
- Q7 (non-blocking, briefing rows): simplify's F4 and F5 — one invariant carried in four
  implementations, and the exit-code contract stated in three homes with no cross-check test — are
  real structural residuals this ticket correctly declined. Candidate backlog rows alongside D-07.
  qa's own advisory adds a third: exit 11's precedence over the pre-existing exits 7 and 8 is
  pinned by no test.
- Q2 (residual, for the ship briefing backlog): D-07 records the `parse_expertise`/`render` silent
  drop (expertise-merge.py:73-95 plus :103-111, exit 0, both routes) as a known separate defect
  left unfixed. Recommend filing it as its own ticket. PF-59b9da56871cca170a7f66678c292035, med.
- Q1, Q3, Q4 (settled by the signature at a29450a1, which carries no `approval.rulings`): D-09's
  exclusion of the exit-11 row from `harness-distill/SKILL.md` stands (that file resolves to lane
  NOBODY); T-02's case27b was kept and the panel's proposal to drop it stays REJECTED with the
  reason in the plan; and the record correction stands — the merge is FIRST-wins, not last-wins as
  the ticket says, and BRIEF, plan and the landed fix all follow the measurement.
- Not a question, an observation for whoever retires this tree: `git stash list` shows one
  pre-existing `stash@{0}: autostash`. Inspected — it holds BUG-1081's feature.json and two
  `.harness/logs/` days, nothing of BUG-276. The stash is repo-level, shared across worktrees, and
  is not this feature's to drop.
