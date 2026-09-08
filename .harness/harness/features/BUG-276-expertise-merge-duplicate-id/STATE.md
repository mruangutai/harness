# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-02-eng/digest.md
- squad: eng
- status: in_review

THE ONE GATING must_fix IS CLOSED. The validate panel's only blocker — `case_duplicate_proposal_ids`
at GRADE 1 — is fixed, re-measured at the orchestrator's own tier, committed and re-pinned. This
section IS the validate handoff; a `notes/handoff-*.md` remains unwritable from a worktree (Q8).

- THE FIX (commit `a641a5b8`, one file: `tests/integration/test-expertise-merge.py`). New SIBLING
  helper `_assert_case27_ambiguous(root, stem, exit_check_name, message_check_name, texts,
  base_sections=None)` at `:1310-1338`, written against the APPLY path (`write_entries`/`run_apply`)
  — NOT a generalisation of `_assert_case24_ambiguous`, which is bound to the ops path and stays
  byte-identical at `:1190`. `base_sections=None` is the absent-destination seam: it skips both the
  base write and the before-hash, so case27c still proves nothing is created. Three call sites at
  `:1347`, `:1357`, `:1366`. Receipt: `notes/receipt-harness-backend-dev-t02-fix-grade1.md`.
- RE-MEASURED AT MY OWN TIER — I ran the grader and the suites, I did not take the dev's numbers:
  - `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/code-grade.py --base 6d969ed3
    --head a641a5b8` → **`case_duplicate_proposal_ids` GRADE 5** (cyc 1 / cog 0 / ABC 3.0, was
    grade 1 at ABC 47.9); **`_assert_case27_ambiguous` GRADE 3** (cyc 6 / cog 5 / ABC 25.2, bar 3);
    `_check_proposal_duplicate_ids` GRADE 4 (bar 4, unchanged, production untouched).
    **`PASSING: 3` — NO grade-1 function remains in the graded range.**
  - Suites, `bash .claude/skills/harness/bin/run-unit-tests.sh` (bare = `--kind all`, so BOTH trees
    ran): **exit 0, `^FAIL ` line count 0**, 80 files, 8-worker pool, 86.6s.
    `test-expertise-merge.py (exit 0, 11.02s)` in that pool; standalone it reports 219 PASS / 0 FAIL,
    exit 0 — the SAME 219 as before the refactor, so the check count did not drop.
  - ASSERTION SURVIVAL read from the rewritten lines themselves, not from an exclusion proof: all
    **nine** case27 checks pass under their ORIGINAL names (`case27{a,b,c}` exit / message / bytes
    or existence). The four-token message assertion (`AMBIGUOUS TARGET` + `section=Patterns` +
    `id=P-02` + `reason=`) is intact for (a) and (b); `case27b` (identical ALPHA/ALPHA texts) is
    intact — its deletion is signed-REJECTED, PF-d6fb0ad9.
- `review_sha` RE-PINNED to **`a641a5b8`**, the fix commit; the old `ef8efd99` no longer contains
  the work under review. plan.yaml is unchanged since `ef8efd99` and still reads `status: review`
  with `approval: approved`, so the pin contains the station write and INV-33 compares equal.
- `cycles_used` incremented **2 → 3** of 10, once, in the act of dispatching the fix. `len(runs)` is
  11 of an informational 20 — a long feature, but each run resolved a named finding.
- NOT REOPENED, and must stay that way: `tests/unit/test-expertise-ops.py:361` `case_u23` still
  grades **2** (cyc 10 / cog 9 / ABC 32.6) and still prints `REASON REQUIRED`. The panel disposed of
  it with a written reason (three independently load-bearing sub-case assertions) and the lead
  concurred. Grade 2 is admissible WITH a reason; it has one. `expertise-merge.py` untouched.

NEXT, for the successor:
  1. The narrow re-review has been dispatched (see the run above / the validator run recorded in
     feature.json). A test refactor's risk is assertion loss, not behaviour, so a targeted
     code-reviewer over the changed file is the proportionate gate; qa/security/ui graded a diff
     this fix does not touch.
  2. On re-review PASS: the pm goal-check over the six SCs, then the ship briefing.
  3. Q9 stands and gates the SHIP path, not this one: this feature has no GitHub parent, milestone
     or sub-issues — `gh-sync.py open` has never run — so `ship` cannot reach Done until `open` does.
     Run `gh-sync.py` from the MAIN checkout; it refuses at exit 1 from inside `.claude/worktrees/`.

TRUST, verified at `a641a5b8` unless noted: the two grades and the suite result (I ran both);
the nine surviving case27 checks (read in the file AND observed passing by name); approval `approved`
on BRIEF and plan with NO `approval.rulings`. UNVERIFIED, inherited and still flagged: the authoring
segment's MUTATION PROOF (that the six new checks CAN redden) was measured at `6d969ed3` and never
re-measured at a pin — mitigated, not closed, by the code-reviewer's finding that all six assertions
bind observable behaviour rather than check names.

DEAD ENDS for validate, all signed, none re-raised by any reviewer: D-07 (the
`parse_expertise`/`render` silent drop stays unfixed — separate defect), D-09 (no exit-11 row in
`harness-distill/SKILL.md`; lane NOBODY), D-04 (`check-expertise.sh` untouched), D-05 (no codes 10
or 12 in the docstring — adding them FAILS SC-06), and `case27b` stays.
WORKING SET: `tests/integration/test-expertise-merge.py` (`:1310-1371`), `notes/receipt-harness-backend-dev-t02-fix-grade1.md`,
`notes/review-harness-code-reviewer-c0.md`, plan.yaml, BRIEF.md, feature.json.

## Open Questions

None blocking. The panel's three non-gating items and the earlier five stand, unchanged by this
fix cycle.

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
