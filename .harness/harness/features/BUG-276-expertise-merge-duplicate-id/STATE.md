# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-2-validator/state.yaml
- squad: validator
- status: in_review

VALIDATE ENTERED, PANEL RUN, PANEL RETURNED **FAIL** ON ONE MECHANICAL BLOCKER. Nothing about the
FIX ITSELF is in doubt: spec compliance passed in full and all six SCs re-graded PASS. The blocker
is a complexity-bar violation in one NEW TEST function. This section IS the validate handoff; a
`notes/handoff-*.md` remains unwritable from a worktree (Q8).

- SEAM (both preconditions in one act, in the skill's order): `review_sha` pinned, then
  `gh-sync.py status <feature-dir> review` (lowercase), which called `plan-merge.py
  set-feature-station` and moved plan.yaml `status: building -> review`. The pin is
  `ef8efd99a28cdabce9ac867c21b895e6cb0ea584` — the SEAM COMMIT, not the build tip `8d0aabeb`.
  Deliberate: the station write lands in plan.yaml and INV-33 compares plan.yaml's BYTES at the pin
  against disk, so a pin one commit below the station write is stale on arrival. `git diff
  --name-only 8d0aabeb ef8efd99` is exactly feature.json + plan.yaml — no code path moved, so the
  panel reviewed the tree the build produced.
- PANEL (2026-09-07-2-validator, FAIL, recorded in feature.json). All FOUR steps RAN, none skipped:
  code-reviewer FAIL; qa PASS (gate-only, `matrix_ok: true`, unit 520/0 exit 0, integration 1636/0
  exit 0, both task `verify:` blocks exit 0); security-reviewer PASS (STRIDE Tampering traced as the
  live axis, guard closes it, no partial-write window); ui-reviewer PASS (no rendered surface,
  scoped out after looking, file census as its evidence). Notes:
  `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c0.md` (tracked). Collated
  digest `runs/2026-09-07-2-validator/digest.md` — **the runs tree is gitignored, so that digest
  dies with this worktree; the four notes and this section are the durable record.**
- THE ONE must_fix (high, gating) — **I re-measured it at my own tier, do not re-derive it**:
  `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/code-grade.py --base 6d969ed3 --head
  ef8efd99...` reports `tests/integration/test-expertise-merge.py:1310`
  `case_duplicate_proposal_ids` at cyclomatic 7 / cognitive 2 / **ABC 47.9**, driver abc, **GRADE 1**
  against the test-code bar of 3 — and grade 1 anywhere is a high finding that fails review under
  `harness-code-risk-grading`. Cause: the three sub-cases each inline their own
  write → hash → propose → run → assert sequence (~13 lines x3).
  REMEDY, and its two traps: extract a **SIBLING** helper *in the shape of*
  `_assert_case24_ambiguous` (`:1192-1209`) — that helper is **bound to the ops path**
  (`write_ops`/`run_ops`) and is **NOT directly reusable** here; the reviewer read it and says so.
  And **all three sub-cases must survive**: dropping `case27b` is signed-REJECTED (PF-d6fb0ad9), so
  a "fix" that shrinks the function by deleting a case is a spec violation, not a remedy.
  Owner: T-02's dev, via harness-eng-lead — that file is in T-02's declared set.
- NOT a second finding, already correctly disposed: `tests/unit/test-expertise-ops.py:361`
  `case_u23` grades **2** (cyc 10 / cog 9 / ABC 32.6), same grader run. The skill admits grade 2
  with a written reason naming the function; the reviewer supplied one (three independently
  load-bearing sub-case assertions) and the lead concurred. **Non-gating — do not reopen it, and do
  not let a fix-cycle dev "helpfully" refactor it.**
- `cycles_used` stays **2** of 10, DELIBERATELY not yet incremented: the lead reported 0 send-backs
  inside the run, and the panel FAIL's rework increments when the FIX IS DISPATCHED. **The successor
  increments to 3 in the same act as dispatching the fix** — once, there or here, never both.
  `len(runs)` is 10 of an informational 20.

NEXT, in this order, for the validate successor:
  1. Fix cycle to **harness-eng-lead** (not the validator lead) for the one must_fix, with the LEAVE
     list stated: leave `case_u23` alone, leave `expertise-merge.py` alone (grade 4, PASS,
     behaviourally clean), keep all three case27 sub-cases. Increment `cycles_used` to 3 in that act.
  2. Re-measure at your own tier: re-run `code-grade.py` over the same range, require
     `case_duplicate_proposal_ids` at grade 3 or better, and re-run both suites. Two live hazards —
     `run-unit-tests.sh` ends with the last script's own `N/N checks passed`, so count `^FAIL ` lines
     and capture the exit status in a variable rather than reading the tail; and clear
     `HARNESS_AGENT_TYPE` with `env -u` or the leaked value reddens the plan-merge approval checks
     as a phantom regression.
  3. Commit, then **RE-PIN `review_sha` at the new tip** — the old pin no longer contains the fix.
  4. Re-review: this is a test refactor, so the risk is assertion loss, not behaviour. A targeted
     code-reviewer re-run over the changed file suffices; a full four-step panel does not earn its
     cost, since qa/security/ui graded a diff this fix does not touch. Do not accept an
     exclusion-style proof over the file's OTHER lines — read the rewritten assertions themselves.
  5. Only then the goal-check and the ship briefing. **This run did not ship and did not attempt to.**

TRUST, verified at `ef8efd99` unless noted: approval `approved` on BRIEF and plan with NO
`approval.rulings` (plan.yaml:3-7,176,286); the grade-1 and grade-2 numbers (I ran the grader, not
the reviewer's word); all four reviewer notes and the run digest exist on disk (`ls`, this run);
worktree clean at the build tip before the seam. UNVERIFIED, inherited and flagged by the lead
itself: the authoring segment's MUTATION PROOF (that the six new checks CAN redden) was measured at
`6d969ed3`, **not re-measured at the pin** — mitigated but not closed by the code-reviewer's
independent finding that all six assertions bind observable behaviour rather than check names.

DEAD ENDS for validate, all signed, and **no reviewer re-raised any of them**: D-07 (the
`parse_expertise`/`render` silent drop stays unfixed — separate defect), D-09 (no exit-11 row in
`harness-distill/SKILL.md`; lane NOBODY), D-04 (`check-expertise.sh` untouched), D-05 (no codes 10
or 12 in the docstring — adding them FAILS SC-06), and `case27b` stays.
WORKING SET: `tests/integration/test-expertise-merge.py` (fix target, plus `:1192-1209` for the
helper shape), `notes/review-harness-code-reviewer-c0.md`, plan.yaml, BRIEF.md, feature.json.

## Open Questions

None blocking. The panel added three non-gating items; the earlier five stand.

- Q11 (harness defect, for the harness owner): the `harness-security-reviewer` job exited NON-ZERO
  (exit 1) while returning a valid PASS block twice, having already written its note. The step ran
  and its artifact is on disk — a turn-end/contract interaction, not a review failure.
- Q10 (harness defect): `harness-ui-reviewer` returned `severity_max: "n/a"`, outside the
  `info|low|med|high|critical` enum, and the `SubagentStop` validator ACCEPTED it. A hole in digest
  validation; harmless here only because that member reported zero findings.
- Q12 (adequacy, briefing row): `matrix_ok: true` rests on a required floor of `{unit}` alone —
  integration ran voluntarily — while SC-01/02/04/05 all declare `evidence: integration`. Pooled
  integration PASS also moved 1513 -> 1636 between cycles at FAIL 0 (siblings run concurrently), so
  a pooled repo-wide count is no cross-cycle baseline; the two changed files re-measured exactly.
- Q9 (mirror, briefing row): this feature has no GitHub parent, milestone or sub-issues —
  `gh-sync.py open` has never run — so `status ... review` recorded the plan station and printed
  `no parent recorded`, with no cards to move. Never a gate, but the ship path must run `open`
  before `ship` or nothing can reach Done.
- Q8 (harness defect, MEASURED — do not re-diagnose): a handoff note cannot be written from inside a
  worktree. `check-domain`'s handoff-shape check resolves every authority pointer against the MAIN
  checkout — `brief-sc:SC-06`/`SC-03` came back ENOENT because the feature dir exists only in the
  worktree, so no pointer set can pass. STATE.md `## Current` carries the handoff (DEC-159).
- Q5 (harness defect): `check-domain.sh`'s worktree-claim guard matches a live claim by agent-type
  STRING alone, never by session or feature, so a concurrent unrelated harness-qa gate for BUG-240
  became this qa session's entire allowed claim set. For the harness owner; not Expertise.
- Q6 (re-confirmed by the panel's qa step): `test_matrix`'s `__bug_class__`/`match_bug_class`
  predicate is an unresolvable placeholder with no taxonomy, so that leg can never fire or be
  audited. Remove it, or give it a taxonomy?
- Q7 (briefing rows): simplify's F4 and F5 — one invariant in four implementations, and the
  exit-code contract stated in three homes with no cross-check test. The panel re-confirmed a
  third: exit 11's precedence over exits 7 and 8 is pinned by NO test.
- Q2 (residual, briefing backlog): D-07's `parse_expertise`/`render` silent drop
  (expertise-merge.py:73-95, :103-111, exit 0, both routes) is a known separate defect left
  unfixed. File it as its own ticket. PF-59b9da56871cca170a7f66678c292035, med.
