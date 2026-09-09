# STATE

## Current

- feature: BUG-276-expertise-merge-duplicate-id
- run: .harness/harness/features/BUG-276-expertise-merge-duplicate-id/runs/2026-09-07-04-validator/digest.md
- squad: validator
- status: in_review

VALIDATE IS CLEAN. The panel's one gating must_fix is fixed, re-measured, committed, re-pinned and
re-reviewed **PASS with `must_fix: []`**. Nothing gates validate any more. This section IS the
validate handoff (a `notes/handoff-*.md` stays unwritable from a worktree — Q8). **This run
deliberately stopped after the panel returned and did NOT run ship.**

- THE FIX (commit `a641a5b8`, one file: `tests/integration/test-expertise-merge.py`). New SIBLING
  helper `_assert_case27_ambiguous(root, stem, exit_check_name, message_check_name, texts,
  base_sections=None)` at `:1310-1340`, on the APPLY path (`write_entries`/`run_apply`) — NOT a
  generalisation of `_assert_case24_ambiguous`, which is bound to the ops path and stays
  byte-identical at `:1190`. `base_sections=None` is the absent-destination seam: `write_file` and
  the before-hash sit strictly inside `if base_sections is not None`, so case27c still proves
  nothing is created. The exit-11 check at `:1327` is UNCONDITIONAL, before the branch, so it fires
  for all three sub-cases. Call sites `:1345`, `:1354`, `:1363`. Receipt:
  `notes/receipt-harness-backend-dev-t02-fix-grade1.md`.
- GRADES, re-measured at my own tier (`code-grade.py --base 6d969ed3 --head a641a5b8`, `env -u
  HARNESS_AGENT_TYPE`): **`case_duplicate_proposal_ids` GRADE 5** (cyc 1 / cog 0 / ABC 3.0 — was
  GRADE 1 at ABC 47.9); **`_assert_case27_ambiguous` GRADE 3** (cyc 6 / cog 5 / ABC 25.2, bar 3);
  `_check_proposal_duplicate_ids` GRADE 4 (bar 4, production, untouched). `PASSING: 3`.
  **No grade-1 function remains in the graded range.**
- SUITES: `run-unit-tests.sh` bare is `--kind all`, so BOTH trees ran: **exit 0, `^FAIL ` count 0**,
  80 files, 86.6s; `test-expertise-merge.py (exit 0, 11.02s)` inside it. Standalone the file reports
  219 PASS / 0 FAIL — the SAME 219 as before the refactor, so no check was dropped.
- **MUTATION PROOF — THE INHERITED `UNVERIFIED` IS NOW CLOSED for case27.** c0 measured
  redden-ability only at `6d969ed3`, and the c1 lead correctly flagged that a green run proves
  execution, not sensitivity. Measured instead of carried: `cp -R` the bin dir to a temp dir,
  replaced the `_check_proposal_duplicate_ids(...)` call in `compute_union` with `pass` (exactly the
  pre-fix behaviour), re-ran the file through the test's own `EXPERTISE_MERGE_BIN` override — **no
  tracked file was ever edited.** Result: **9 FAIL / 0 PASS across case27, exit 1.** All three
  sub-cases redden INDEPENDENTLY, including case27b (identical ALPHA/ALPHA) and case27c's existence
  check. The rewritten assertions bind observable behaviour, not check names. Probe dir deleted;
  `git diff --stat HEAD` empty and `git status --porcelain` clean before the commit.
- RE-REVIEW (`runs/2026-09-07-04-validator`, **PASS**, `must_fix: []`, `severity_max: med`,
  `code_grade: grade_2` for the whole-branch range). NARROW BY MY DECISION: the code-reviewer step
  only. qa / security-reviewer / ui-reviewer were **NOT dispatched** at this pin — they graded a
  diff this fix does not touch and all three PASSed at `ef8efd99`; their c0 notes stand as that
  evidence, and the lead recorded the non-dispatch rather than presenting them as clean. Note:
  `notes/review-harness-code-reviewer-c1.md` (tracked) — per-proposition, line-anchored, explicitly
  NOT an exclusion proof. All NINE case27 propositions survive; the four-token message assertion
  (`AMBIGUOUS TARGET` + `section=Patterns` + `id=P-02` + `reason=`) is intact and unweakened for
  BOTH (a) and (b). `case27b` present — its deletion is signed-REJECTED, PF-d6fb0ad9.
- `review_sha` RE-PINNED to **`a641a5b8`**; the old `ef8efd99` no longer contains the work under
  review. plan.yaml is unchanged since `ef8efd99`, still `status: review` / `approval: approved`, so
  the pin contains the station write and INV-33 compares equal.
- `cycles_used` **3** of 10 (incremented once, in the act of dispatching the fix; both leads reported
  0 send-backs). `len(runs)` is 12 of an informational 20 — a long feature, but every run resolved a
  named finding and the last two closed the only gating one.
- NOT REOPENED: `tests/unit/test-expertise-ops.py:361` `case_u23` still grades **2** (cyc 10 / cog 9
  / ABC 32.6) and still prints `REASON REQUIRED`. c0 disposed of it with a written reason (three
  independently load-bearing sub-case assertions); c1 carried that reason forward rather than
  re-litigating. Grade 2 is admissible WITH a reason; it has one. In range only because the range
  spans the whole branch. `expertise-merge.py` untouched.

NEXT, for the successor:
  1. The pm goal-check over the six SCs (through `harness-product-lead`), then the ship briefing.
     Nothing in validate blocks it.
  2. Q9 gates the SHIP path, not this one: no GitHub parent, milestone or sub-issues exist —
     `gh-sync.py open` has never run — so `ship` cannot reach Done until `open` does. Run
     `gh-sync.py` from the MAIN checkout; it refuses at exit 1 from inside `.claude/worktrees/`.
  3. The briefing's backlog table must carry Q2, Q6, Q7, Q9, Q10, Q11, Q12 as rows — anything not
     listed dies silently.

TRUST, verified at `a641a5b8` unless noted: the three grades and the whole-suite result (I ran the
grader and the runner myself, not the dev's or the lead's word); the nine case27 checks (read in the
file, observed PASSing by name, AND observed reddening 9/9 under mutation); the tree clean and
untouched by the probe; approval `approved` on BRIEF and plan with NO `approval.rulings`.
UNVERIFIED, still: redden-ability of the new checks OUTSIDE case27 — the probe covers case27's nine
only, and the c0 measurement at `6d969ed3` remains the sole evidence for the rest, mitigated by the
code-reviewer's finding that all six assertions bind observable behaviour rather than check names.

DEAD ENDS for validate, all signed, none re-raised: D-07 (the `parse_expertise`/`render` silent drop
stays unfixed — separate defect), D-09 (no exit-11 row in `harness-distill/SKILL.md`; lane NOBODY),
D-04 (`check-expertise.sh` untouched), D-05 (no codes 10 or 12 in the docstring — adding them FAILS
SC-06), and `case27b` stays.
WORKING SET: `tests/integration/test-expertise-merge.py` (`:1310-1371`),
`notes/review-harness-code-reviewer-c1.md`, `notes/receipt-harness-backend-dev-t02-fix-grade1.md`,
plan.yaml, BRIEF.md, feature.json.

## Open Questions

None blocking. The eight standing items are unchanged by this fix cycle; all are briefing rows.

- Q11 (harness defect): `harness-security-reviewer` exited NON-ZERO (exit 1) while returning a valid
  PASS block twice, having already written its note. A turn-end/contract interaction, not a review
  failure.
- Q10 (harness defect): `harness-ui-reviewer` returned `severity_max: "n/a"`, outside the
  `info|low|med|high|critical` enum, and the `SubagentStop` validator ACCEPTED it. A hole in digest
  validation; harmless here only because that member reported zero findings.
- Q12 (adequacy): `matrix_ok: true` rests on a required floor of `{unit}` alone — integration ran
  voluntarily — while SC-01/02/04/05 all declare `evidence: integration`. Pooled integration also
  moved 1513 -> 1636 between cycles at FAIL 0 (siblings run concurrently), so a pooled repo-wide
  count is no cross-cycle baseline; the two changed files re-measured exactly.
- Q9 (mirror): no GitHub parent, milestone or sub-issues — `gh-sync.py open` has never run — so
  `status ... review` recorded the plan station and printed `no parent recorded`. Never a gate, but
  the ship path must run `open` before `ship` or nothing can reach Done.
- Q8 (harness defect, MEASURED — do not re-diagnose): a handoff note cannot be written from inside a
  worktree. `check-domain`'s handoff-shape check resolves every authority pointer against the MAIN
  checkout — `brief-sc:SC-06`/`SC-03` came back ENOENT because the feature dir exists only in the
  worktree, so no pointer set can pass. STATE.md `## Current` carries the handoff (DEC-159).
- Q5 (harness defect): `check-domain.sh`'s worktree-claim guard matches a live claim by agent-type
  STRING alone, never by session or feature, so a concurrent unrelated harness-qa gate for BUG-240
  became this qa session's entire allowed claim set.
- Q6: `test_matrix`'s `__bug_class__`/`match_bug_class` predicate is an unresolvable placeholder with
  no taxonomy, so that leg can never fire or be audited. Remove it, or give it a taxonomy?
- Q7: simplify's F4 and F5 — one invariant in four implementations, and the exit-code contract
  stated in three homes with no cross-check test. The panel confirmed a third: exit 11's precedence
  over exits 7 and 8 is pinned by NO test.
- Q2 (residual): D-07's `parse_expertise`/`render` silent drop (expertise-merge.py:73-95, :103-111,
  exit 0, both routes) is a known separate defect left unfixed. File it as its own ticket.
  PF-59b9da56871cca170a7f66678c292035, med.
