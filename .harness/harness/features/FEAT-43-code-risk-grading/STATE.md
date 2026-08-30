# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/2026-08-29-validate-delta-c26-validator/state.yaml
- squad: validator
- status: Review — COMPLETE and RECOMMENDED FOR SHIP. 20 of 20 criteria met, every gate green, the
  engine crash class closed. Nothing shipped, merged, deployed or closed; the worktree stands and
  PR #978's lifecycle is the operator's.
- review_sha: `baa96b7ee1cfbc7fcbea8873692cc91751a0c171`
- cycles: **28 of 28 — exhausted** (`answers/Q10-b21-hold-and-fix.md` authorized the last one, singly
  and narrowly). No repair capacity remains.
- briefing: `notes/ship-review-c28.md` (supersedes `ship-review-c27.md`)

Seven defects closed across cycles 14–26, each verified by the orchestrator's own run rather than
accepted on report.

- **CR-01** — the tool rejected its own change (exit 1, six grade-3 production functions). Now
  **exit 0**: 198 gated records, zero blocking, 12 grade-2 all reasoned. Two rounds: the first closed
  the six named functions; my post-commit check then caught `test-code-grade.py:main` at grade 1,
  invisible because the self-grading guard enumerated three hardcoded production files. The second
  closed the class.
- **CR-02 + UI-01** — severity derived from blocking-ness, not the grade literal; one spelling across
  tool, JSON, guidance and enum.
- **SEC-01** — closed as a class (`answers/Q8`). Both remedies QA ranked were refused: `base == head`
  blacklists one shape that `~1` walks around, and the schema change was unnecessary because
  `git merge-base` already returns the reviewed base. **The range a digest names no longer changes
  the answer.**
- **ENUM-01** — found by the goal-check *after* the panel passed: the severity ladder was narrowed
  and only one of four consuming templates followed. Fixed in both trees and guarded.
- **REQ-11 prose** — glossary and shipped skill still taught the old vocabulary, one heading naming
  the failing side of the bar as the target. Four sentences corrected.
- **T-01** — deviation refused by the operator (`answers/Q9` §2). Both grade-2 engine functions
  reached grade 4 and **both allowlist entries were deleted rather than re-pointed**. Engine is 53
  functions, zero below grade 4. Behaviour proven unchanged by three mutations from two agents.
- **B21** — the operator chose HOLD AND FIX (`answers/Q10`). `_strip_docstring` (D-03, underwriting
  D-02) and `_qualname`'s class-prefix join are now bound by named behavioural tests that fail under
  the exact mutations that previously left suite and self-grade at exit 0. I re-ran one mutation
  myself; the delta review re-ran both and proved the docstring test binds *for the right reason* —
  a no-rename control returns bit-identical results mutated and unmutated, so the rename is
  load-bearing.

**Gates at the ship pin:** full independent panel PASS at `17106762`; three delta reviews PASS
(`6752597`, `e12d53b1`, `cd8dae47`), all `must_fix: []`, the last at `severity_max: low` — down from
`med` because the untested-branch driver is closed; test matrix PASS; `check-state.sh` exit 0;
canonical suite 957 results with one failing suite (`test-hooks-install.py (e-green) SC-14`,
untouched by this diff, reproduces on main, B8); SIMPLIFY an empty pass.

**Goal-check: 20 of 20 met, 0 `not_met`, 0 open.** SC-11 — the feature's central claim — was
executed by the operator at this pin and **PASSED**: a1=6, a2=5, b1=16, b2=14, so worst_A 6 <
worst_B 16 and gap 10 > max spread 2, both conditions of the frozen MAXIMA rule, with the gap five
times the larger within-arm spread. `notes/uat-sc11-c21.md` is `status: passed` and committed; pm
re-derived the arithmetic and reproduced all four values by regrading the surviving outputs
(`notes/research-goalcheck-final.md`).

Two caveats carried into the briefing rather than dropped: an initial dispatch was **discarded before
any number was recorded** because shared context revealed the arms to the controls — a void on
procedure, disclosed, not a selection between draws; and it cannot be verified by inspection that the
surviving `/tmp` outputs are the neutral run's rather than the discarded one's, so that one link is
testimonial. SC-11 is strongly evidenced, not end-to-end machine-verified.

`runs` is 39 against an informational 20-run budget (INV-22) — surfaced in the briefing with the read.

## Cycle 28 — the crash class, CLOSED

Three `None` guards in `_Counter` — `visit_AnnAssign/node.value`, `visit_With/item.optional_vars`,
`visit_Try/handler.type` — matching the pattern `visit_Assert` already used in the same class. My own
sweep over `bin/*.py`: **99 graded, 0 crash**, up from 83/16; `harness_merge.py` and
`harness_boundary.py` now grade. Range gate exit 0 at 201 records, engine 53 functions zero below
grade 4, five suites exit 0, `check-state.sh` exit 0.

**The class is closed structurally, not patched three times.** `ast.NodeVisitor.generic_visit` skips
`None` behind an `isinstance(value, AST)` check, so only a custom `visit_*` override calling
`self.visit()` directly can crash. The delta review enumerated all 18 optional fields `_Counter`
reaches and ran 30 construct probes: 30/30 clean here, the same three raising at the prior pin. Each
guard binds under isolated mutation to a NAMED test failure, and the tests assert literal metrics
re-derived term by term — correctly NOT asserting bare-`with` and `with`-`as` identity (`abc_a`
differs by 1). `answers/Q12-cycle-28-crash-class.md`.

**SC-11 carries across the change without an argument:** pm re-graded the four surviving arm outputs
at this pin and reproduced 6/5/16/14 exactly.

## Cycle 27 — the CI blocker, and what fixing it uncovered

The PR #978 CI failure is CLOSED. `check_prior_validator` ran `git show df63193:<file>`, absent in a
shallow checkout. The operator's own patch deleted the check; **I refused** — it is the sole
implementation of SC-20's fourth clause (`BRIEF.md:210-218`, verbatim). The two files are now
byte-identical `.fixture` data with a non-`.py` suffix, so they stay out of the graded set. Proven in
a real `git clone --depth 1` where `df63193` is absent: suite exit 0. The delta review corrupted the
fixture and confirmed the named failure still fires. Two further history dependencies in the same
file were fixed with it; the scope call was reported and ratified. `answers/Q11-ci-hermeticity-cycle-27.md`.

**BLOCKING, for the operator.** `code_grade._Counter` visits three ASDL-optional AST fields without a
`None` guard — `visit_With`/`optional_vars`, `visit_Try`/`handler.type`, `visit_AnnAssign`/`node.value`.
`with lock:`, `except:` and `x: int` each raise `AttributeError`. I reproduced all three.
**16 of the harness's 99 `bin/*.py` crash**, including production `harness_merge.py` and
`harness_boundary.py`; CLI-reachable; always a loud raise, never a silent mis-grade; zero
intersection with the 200-record gated set; **introduced by `1ac1bd0`, this feature's first commit**.
`visit_Assert` guards `node.msg` correctly in the same class, so the pattern was omitted three times.

The verification apparatus was **structurally incapable** of finding it: self-grading measures
complexity, not correctness, and the gated set has no overlap with the crash list. Third time in this
feature that a green suite concealed a missing control.

Recommendation: authorize cycle 28 — three one-line guards plus six assertions, spec at
`notes/qa-delta-c27.md`. Note `with lock:` and `with lock as _discard:` are NOT metric-identical
(`abc_a` differs by 1); an earlier draft spec would have written a failing test.

## Open Questions

- Q1 (settled): a read-only engineering assessment had no legal way to report its suite; it RUNS the
  suite and reports the real value. Harness wart, backlog B7.
- Q2 (ANSWERED, `answers/Q6`): remediate, do not exempt.
- Q3 (ANSWERED, `answers/Q8`): the repository-derived range closes SEC-01 as a class.
- Q4 (ANSWERED, `answers/Q9` §1): SC-11 is decided on arm **MAXIMA**, recorded before the run.
- Q5 (ANSWERED, `answers/Q9` §2): T-01's deviation refused and fixed at the root.
- Q6 (ANSWERED, `answers/Q10`): B21 held and fixed in one narrowly scoped cycle.
- Q7 (ANSWERED, operator-executed 2026-08-29): the SC-11 UAT **passed**; recorded in
  `notes/uat-sc11-c21.md` and closed in the goal-check at 20 of 20.
- Q8 (FOR THE OPERATOR, the only thing left): the ship decision, and which of backlog B1–B20, B22,
  B23, B24 survive. Recommendation: **ship**.
- Q10 (correction on the record): pm reported B22 stale after a glob check. I verified with
  `git status` and `find` — the stray untracked directory DOES exist in the main checkout, two
  files. **B22 stays.**
- Q9 (disclosed, non-blocking): the collision test binds a *derived symptom*, not a direct
  cross-attachment, because `grade_source` keys its name map with `_child_qualname` and never
  `_qualname` — direct discrimination is impossible given the engine's shape. The validator lead
  ruled the operator's literal bar met. Three neighbouring branches remain unbound (B23).
