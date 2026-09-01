# Goal-check — BUG-1081 at review_sha 676940ce (cycle 2)

**Eleven of twelve criteria are MET. SC-11 is UNMET and it is a TEST-only gap: the behaviour is
correct, the committed suite under-fixtures it.** No CODE gap found. Every content criterion was
read with `git -C <worktree> show 676940ce:<path>`; every automated criterion was traced to a named
test function in the suites I ran (`test-validate-digest.py` exit 0, `test-code-grade.py` exit 0 —
"ALL PASSED" / "PASS test-code-grade", no `FAIL ` lines).

| SC | Method | Verdict | Evidence |
|---|---|---|---|
| 01 | automated | MET | `check_hook_rejects_false_pass` — real `[VALIDATE, "--hook"]`, exit 2, asserts `expected 'fail'`, asserts no `Traceback`. Pre-fix half reproduced by me: base validator from `9f2a0702` run over the same fixture with cwd inside it → **exit 0, empty stderr** |
| 02 | automated | MET | same function, second half: honest `fail` + `VERDICT: FAIL` in the same repo accepted at exit 0 — so the suite discriminates, not blanket-refuses |
| 03 | automated | MET | `check_mechanical_result_discrimination` over `GRADE_FIXTURES` (4 results). For `pass`/`grade_2`/`n_a`: accept-matching (3) + reject-one-wrong (3) + `f"expected {expected!r}"` named in the rejection (3) = **9/9 obligations fixtured**, each with its own purpose-built range |
| 04 | automated | MET | `check_committed_syntax_error` — exit 2, `"does not parse"`, no `Traceback`. Pre-fix half reproduced by me: base validator → **exit 0, empty stderr** |
| 05 | automated | MET | `check_digest_base_cannot_move_result` — bases A and B both yield `expected 'fail'`; a non-`review_sha` head still refused on `review_sha` |
| 06 | automated (unit) | MET | `check_classify_bars` (production bar 4, active-test bar 3), `check_classify_precedence` (grade 1 beats a simultaneous grade 2 → `fail`), grade-2 reason requirement in `check_code_grade_state`. *Advisory:* the reason rule lives in `validate-digest.py`, so its assertion sits in the **integration** script — the criterion's `evidence: unit` is imprecise, the clause is still proven at the pin |
| 07 | automated | MET | `check_plan_review_never_grades` (monkeypatched `gated_set` records **zero** calls; module-global lookup, so the patch is real) + `_check_plan_approval_states` rejecting a non-`n_a` plan review |
| 08 | automated | MET | `check_judgment_outranks_clean_grade` — clean range, `must_fix` and `severity_max: high` each still fail on `review policy` |
| 09 | inspection | MET | `show 676940ce:.claude/skills/harness-code-review/SKILL.md` L63-101: reviewer owns findings + grade-2 reasoning; `validate-digest.py recomputes … independently`; "No changed Python path … means `n_a`"; "A mismatch refusal names the value the repository expected" |
| 10 | inspection | MET | `show 676940ce:…/test-validate-digest.py` L2223-2243: RED block names **both** intended cases — blocking production fn and committed syntax error — each with `validate() errors=[]`, `--hook exit 0`. Cases drive `validator.validate()` and the real `--hook` subprocess, no stub |
| 11 | automated | **UNMET — TEST-only** | see below |
| 12 | inspection | MET | `show 676940ce:.harness/harness/docs/DECISIONS.md` DEC-209 (§ from L6362): enforcement ownership, canonical-range derivation, availability trade (reverses FEAT-43's carve-out), fail-closed/no-traceback, retained human-judgment boundary — all five present |

## SC-11 — the one finding

The criterion binds **"For an ordinary `pass`, `fail`, or `grade_2` claim"** over three conditions.

- unresolvable default branch — `check_unresolvable_default_branch` loops all four grades, asserts
  `"default branch"`, plus `"repair origin/HEAD"`. **Covered.**
- missing merge base — `check_no_merge_base` loops all four grades, asserts `"no merge base"`.
  **Covered** (remediation text not asserted).
- degenerate range — only `check_derived_base_range`'s degenerate case, and
  `_assert_derived_rejects` hardcodes `reviewer_digest("n_a", …)`. **No ordinary claim is ever
  fixtured against it**, and the remediation is not asserted either.

Behaviour is correct: `_canonical_review_range` returns the degenerate error before any grade
comparison, and `validate()` calls enforcement for every non-plan `code_grade`. Measured directly
against the committed validator with the suite's own fixture — `pass`, `fail`, `grade_2` each
refused with `already an ancestor` **and** `Re-pin review_sha`. So: add fixtures, change no code.

This contradicts two claims on disk that I checked rather than trusted: `notes/qa-test-matrix-c1.md`
L148 ("not under-fixtured") and `notes/review-harness-code-reviewer-c1.md` L44 both credit the
degenerate clause to `check_derived_base_range` without noticing its `n_a`-only digest.

## Definition of Done

Satisfied at this pin for everything the DoD asserts about behaviour — a false `pass` cannot buy a
green review, an honest claim is accepted, and an ungradable range refuses by name. The only
shortfall is regression cover for one of SC-11's three conditions. GitHub #1081's board card
reaching `Done` is a **post-merge** step owned by the ship/close gate and, per the BRIEF itself, not
a pre-merge criterion — not graded here.

## Open

- Q1 (non-blocking): fixture SC-11's degenerate range for `pass`/`fail`/`grade_2`, and assert the
  remediation substring for the merge-base and degenerate conditions as
  `check_unresolvable_default_branch` already does. Test-only, `test-validate-digest.py`, which
  DEC-174 makes main-session-direct.
