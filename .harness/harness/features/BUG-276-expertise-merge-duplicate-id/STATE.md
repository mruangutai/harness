# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-2-validator/state.yaml
- squad: validator
- status: in_review

BUILDING → REVIEW SEAM IS TAKEN. Both preconditions were performed in one act before any panel
dispatch, in the order the harness skill fixes: `review_sha` pinned, then
`gh-sync.py status <feature-dir> review` (lowercase station), which called
`plan-merge.py set-feature-station` and moved plan.yaml `status: building -> review`. This section
IS the build→validate handoff; a `notes/handoff-*.md` remains unwritable from a worktree (Q8).

- The pin is `ef8efd99a28cdabce9ac867c21b895e6cb0ea584`, the seam commit itself, NOT the build tip
  `8d0aabeb`. Deliberate: the station write lands in plan.yaml, and INV-33 compares plan.yaml's
  BYTES at the pin against disk, so a pin one commit below the station write is STALE the moment it
  is taken. `git diff --name-only 8d0aabeb ef8efd99` is exactly feature.json + plan.yaml — no code
  path moved between the build tip and the pin, so the panel reviews the same tree the build
  produced.
- Mirror, non-gating: `gh-sync.py status` recorded the plan station and then printed
  `no parent recorded for BUG-276-...` — this flow has never run `gh-sync.py open`, so it holds no
  milestone, parent issue or sub-issues, and there were no cards to move to Review. `open` is a
  ship-mission act (github-mirror.md), so the omission is on the ship path, not a defect here. The
  mirror is never a gate.
- Panel dispatched over the pin: the `review` team (code-reviewer, qa gate-only, security-reviewer,
  ui-reviewer, four in one turn) to harness-validator-lead, run dir `2026-09-07-2-validator`. The
  code under review is three files in `6d969ed3..ef8efd99`:
  `.claude/skills/harness/bin/expertise-merge.py` (+24/-1), `tests/unit/test-expertise-ops.py`
  (+54), `tests/integration/test-expertise-merge.py` (+53). Everything else in that range is
  feature-directory bookkeeping.

Build phase, all complete and unchanged by the seam: eng (2026-09-07-06-eng, PASS) — T-01 at
88a627da, T-02 at 97e715d1, both at station `done`; qa (2026-09-07-1-validator, PASS) — the one
blocking gate, unit 520/0 and integration 1513/0, both task `verify:` blocks at exit 0, all six new
checks proven to redden under a live mutation of the guard's call site, all six SCs PASS
(notes/qa-BUG-276-c0.md); SIMPLIFY (2026-09-07-01-eng, PASS) — an EMPTY pass, four readers, zero
applies, which is why the tip was pinnable unmoved. Zero send-backs reported, so `cycles_used`
stays 2 of 10; `len(runs)` is 9 of an informational 20.

NEXT, after the panel returns: record its verdict as a run in feature.json, route any `must_fix` to
the owning lead as a fix cycle (increment `cycles_used`), and only on a clean panel proceed to the
goal-check/ship phase — this dispatch stops at the panel and does not ship. Trust, verified at
ef8efd99 unless noted: approval `approved` on both BRIEF and plan with no rulings
(plan.yaml:3-7,176,286 — read at 76066fbc, unchanged since); the worktree was clean at the build
tip before the seam (`git status --porcelain` empty at 8d0aabeb); the defect is FIRST-wins, not the
last-wins the ticket asserts. Dead ends for validate, all signed and NOT to be re-litigated: D-07
(the parse_expertise/render silent drop stays unfixed — separate defect), D-09 (no exit-11 row in
harness-distill/SKILL.md; that file resolves to lane NOBODY), D-04 (check-expertise.sh untouched),
D-05 (no codes 10 or 12 in the docstring — adding them FAILS SC-06). Working set: plan.yaml,
BRIEF.md, notes/qa-BUG-276-c0.md, .claude/skills/harness/bin/expertise-merge.py, feature.json.

## Open Questions

None blocking. The qa and simplify runs added four non-gating items; the signature-time four are
settled or residual as recorded.

- Q9 (mirror, non-blocking, briefing row): this feature has no GitHub parent, milestone or
  sub-issues because `gh-sync.py open` never ran for it. Nothing gates on that, but the ship path
  must run `open` before `ship` or the mirror will hold nothing to move to Done.
- Q8 (harness defect, non-blocking, MEASURED — do not re-diagnose): a handoff note cannot be
  written from inside a worktree. `check-domain`'s handoff-shape check resolves every authority
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
