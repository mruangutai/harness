# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/validate-regate-c21-validator/state.yaml
- squad: validator
- status: Review — all four terminal blockers closed and QA-gated. `review_sha` re-pinned to
  `17106762c588b3d1c0df45efbcb6128604efb185`. Next act: the fresh independent validator panel.
- cycles: 21 of 25 (`answers/Q6-cycle-20-remediation-authorization.md`,
  `answers/Q7-cycle-25-preemptive-authorization.md`)

The operator chose **remediate, not exempt**. All four cycle-13 panel blockers are closed, each one
verified by the orchestrator's own measurement rather than accepted on a squad's report.

**Three source commits**, each committed by explicit pathspec:

- `a643e44f97285c5388fcd1bc7287cdd6d79a103b` — CR-01 core (the six grade-3 production functions
  behind new helpers), CR-02 + UI-01 (severity derived from the bar rather than a grade literal, one
  spelling across tool, JSON and guidance), SEC-01 attempt 1.
- `34a49c4b78c74cac6676ec91d7cb7f262abf19e7` — CR-01 as a class. `check_self_grading` enumerated a
  hardcoded three production files, so `test-code-grade.py:main` degrading to grade 1 (ABC 45.7
  against a test bar of 3) was invisible to the very suite that exists to prove CR-01. The guard now
  covers every changed file at a derived per-file bar; `main` is decomposed to grade 5.
- `17106762c588b3d1c0df45efbcb6128604efb185` — SEC-01 as a class, per the ruling in
  `answers/Q8-sec01-remedy-ruling.md`.

**The four closures, with the measurement behind each:**

- **CR-01 — closed.** `code-grade.py --base 7ccfae8d --head 17106762` exits **0**: 178 gated
  records, **zero blocking below-bar**, 14 grade-2 records (the designed non-blocking carve-out) all
  reporting severity `med`. It exited 1 with six grade-3 production failures at the cycle-13 pin.
  Note the closure rests on the tool, not on the test-side `SELF_GRADING_ALLOWLIST` — `code-grade.py`
  never reads that allowlist.
- **CR-02 + UI-01 — closed.** Severity is bar-relative, so every blocking record carries `high` in
  both text and JSON where a grade-3 previously printed nothing and reported `"severity": null`.
  `.claude/skills/harness-code-review/SKILL.md` names the state and the `fail` spelling; SC-14 and
  SC-17 hold unchanged.
- **SEC-01 — closed as a class, not as a shape.** The first fix bound only the reviewed *head*, so
  `<review_sha>..<review_sha>` still bought `n_a` at exit 0 — QA reproduced that live and FAILED the
  cycle-18 gate. Q8 rejected both remedies QA ranked: `base == head` blacklists one shape that
  `<review_sha>~1..<review_sha>` walks around, and the `feature.json` schema change was unnecessary
  because `git merge-base main <pin>` already returns `7ccfae8d`, exactly the base the panel
  reviewed. The `n_a` decision now diffs a repository-derived
  `merge-base(default branch, review_sha)..review_sha` range. **The tell that the class is closed is
  that the range the digest names no longer changes the answer**: all three of `<pin>..<pin>`,
  `<pin>~1..<pin>` and the honest `7ccfae8d..<pin>` now refuse `n_a` at exit 1, while a
  `code_grade: fail` digest over the same forged range still validates at exit 0. `pass`/`fail`/
  `grade_2` are deliberately not gated on base derivation, so a repository without a resolvable
  default branch cannot brick reviewer validation.

**Gates since:** SIMPLIFY ran four read-only angles and applied nothing — an empty pass, HEAD
unmoved (`runs/validate-final-simplify-c21-eng/digest.md`). The QA re-gate PASSED at the baseline
(unit 29/29, integration 28/28), drove all four new fail-closed branches live, and bound the derived
range with two named mutations (`runs/validate-regate-c21-validator/digest.md`).

**Not yet run:** the canonical repository suite and `check-state.sh` (both deliberately deferred to
one final checkpoint), `gh-sync.py status Review` for the new pin, the fresh independent validator
panel, the product goal-check, documentation, and the SC-11 UAT. Ship, merge, PR, deploy, issue
closure and worktree removal remain prohibited pending the operator's decision.

## Open Questions

- Q1 (settled): a read-only engineering assessment had no legal way to report its suite —
  `dev` + `suite: n/a` + PASS is rejected while `dev-ops` is allowed. An assessment-only member RUNS
  the suite and reports the real value. The asymmetry is a harness wart, backlog row B7.
- Q2 (ANSWERED, `answers/Q6-cycle-20-remediation-authorization.md`): remediate, do not exempt.
- Q3 (ANSWERED, `answers/Q8-sec01-remedy-ruling.md`): SEC-01's remedy is the repository-derived
  range; the `~1` variant is closed by it rather than backlogged; a non-empty intersection between
  the self-grading allowlist and the gated set is the designed steady state.
- Q4 (open, non-gating): the duplicated binding-error line. With `artifact: none` and
  `code_grade: n_a`, one producing site is reached by two call paths in a single run and the output
  is not de-duplicated, so the same error prints twice. QA first refuted it; the validator lead
  overturned that refutation on source evidence. Backlog candidate, severity info.
- Q5 (open, non-gating, for the panel to weigh): a checkout whose branch maps to more than one
  `feature.json` can still name any of those features in its `artifact:` line. The forgeable set is
  narrowed from 42 features to those sharing the checkout's branch — for a normal feature branch,
  exactly one. Does the panel accept the narrowed guarantee?
