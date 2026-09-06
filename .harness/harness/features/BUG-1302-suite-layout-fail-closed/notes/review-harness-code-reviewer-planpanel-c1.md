# Review — plan-panel scope reader — BUG-1302-suite-layout-fail-closed — cycle 1

**Conclusion: PASS.** No orphan traces, no unfalsifiable criterion that a correct fix could fail, no
dependency-chain hazard. Three independent re-derivations (mine, plus the two prior readers) of every
AST count and every code-grade number agree exactly with what the plan pins — I ran `code_grade.py`
and hand-built `ast.walk` counts directly against the file at HEAD (not the test suite) and got zero
mismatches. One low-severity completeness gap (SC-09 has no task-level owner) and a set of
already-closed items carried forward for the record.

## Traceability (REQ ↔ task ↔ SC), both directions

REQ-01..REQ-06 each have exactly one delivering task (REQ-01→T-02, REQ-02→T-01, REQ-03→T-03,
REQ-04→T-04, REQ-05→T-05, REQ-06→ all five). Every task's `traces:` cites REQs that exist in the
BRIEF. SC-01..SC-10 (BRIEF contains exactly ten — **no eleventh SC exists**, contra the upstream
dispatch's "SC-01..SC-11" framing; this is a framing artifact, not a plan gap) each map to a REQ and
a task, except:

- **SC-09 (REQ-06 regression safety) has no task whose `verify:` executes SC-09's own command.**
  Severity: **low**. Concrete consequence: T-01..T-04's `verify:` blocks do gate on the *whole
  file's* exit code (`out=$(python3 …)` — a nonzero exit from `SystemExit(1 if failures else 0)`
  short-circuits the `&&` chain before any grep runs), so a REGRESSION that makes an existing check
  FAIL is caught incidentally by every task after it. But SC-09's actual bar is stricter — "exit 0
  alone does NOT discharge this criterion" — and requires each *named* pre-existing check
  (`real layout is valid`, `sole implementation sweep`, `case 11 hygiene…`, `case 1`..`case 10`, and
  the eight integration names) to appear by name in the output. No task's `verify:` greps for any of
  those names. If a task accidentally *deleted* one of those pre-existing `check(...)` calls (rather
  than breaking it), the run would still exit 0 with no FAIL line, and nothing in T-01..T-05 would
  catch it — only a separate, later execution of SC-09's own literal command would. SC-10 has the
  same shape (no task owns it) but is explicitly `verify: inspection`, so the absence is disclosed;
  SC-09 is `verify: automated` with no disclosed owner. Recommend the plan (or the build/ship gate
  that consumes it) name who runs SC-09's command before the feature ships — it is not fatal, since
  `harness-qa-gate` at build time is the natural place, but the plan itself does not say so.

No task traces a REQ that does not exist; no REQ is undelivered.

## Criteria that cannot report red — none found

Walked SC-01 through SC-10 against (a) fix absent, (b) fix wrong, (c) fix present-but-not-executing.
All ten are falsifiable as written; none is a SOURCE-TEXT grep standing in for run-output. SC-05/SC-06
(B-6) are the interesting case: because the live `test_kinds` config makes `control_candidate`
non-`None` today, case 11's `else` branch is genuinely unexecuted at runtime in a live-repo run — the
plan compensates with a reachability check (`select_control_candidate(CORPUS_BLIND_KINDS) is None`,
which I independently confirmed returns `None`) plus a purely-structural AST check on the literal
`orelse` body of the one `ast.If` comparing `control_candidate` to `None`. This is the same residual
risk the BRIEF's own "Residual risk and its owner" section already discloses and the Advisor's R2
already dispositioned — **rediscovery, not new**, and I find the compensating pair (reachability +
AST shape, with the AST clause explicitly requiring the literal `False` constant so a truthy-rewrite
can't sneak past both phrase checks) adequate.

## Dependency-chain hazard — none found

T-01→T-02→T-03→T-04 all touch `tests/unit/test-suite-layout.py`; T-05 is correctly independent
(different file). Checked every earlier task's `verify:` against what every later task edits:

- T-01's two greps (`b5 corpus`, `b5 structural`) test `_is_inside_tests`/`B5_CORPUS`. T-02 touches
  `_literal_key_present`, T-03 touches case 11, T-04 touches `_violations_callers` — none touch
  `_is_inside_tests`. Re-running T-01's verify after T-02..T-04 land still passes.
- T-02's three clauses (`b4 corpus`, `b4 structural`, `code_grade` grade-3 assert) test
  `_literal_key_present`. T-03/T-04 don't touch it. Still passes after re-run.
- T-03's three clauses (`b6 reachability`, `b6 message`, no-`INAPPLICABLE`) test case 11. T-04 adds
  an unrelated case after case 11 touching only `_violations_callers`, and its intent never mentions
  the word `INAPPLICABLE`. Still passes after re-run.

The chain exists to serialize edits to one shared file (T-04's own goalcheck-noted "reason
unstated" — cosmetic, not a defect), not because of verify entanglement. Confirms prior "task order:
PASS" — rediscovery.

## Measured values — independently re-derived, not assumed (three-way agreement)

Ran directly against `tests/unit/test-suite-layout.py` at HEAD (`code_grade.grade_source`, `ast.walk`
— not the test suite):

| Measurement | value |
|---|---|
| `any`-Name `ast.Call` count inside `_literal_key_present` (pre-fix) | **2** ✓ |
| `ast.Constant` `"*?["` count inside `_literal_key_present` (pre-fix) | **2** ✓ |
| `ast.Constant` `".."` count inside `_is_inside_tests` (pre-fix) | **2** ✓ |
| `_literal_key_present` code-grade, pre-fix | cyc **12**, cog **13**, abc **18.4**, grade **2** ✓ |
| `_literal_key_present` code-grade, post-fix (conjunct removed, simulated in memory) | cyc **10**, cog **13**, abc **15.1**, grade **3** ✓ |
| `select_control_candidate(live test_kinds_cfg)` | `.harness/tools/test_dir/gen.py` ✓ |
| `select_control_candidate(CORPUS_BLIND_KINDS)` | `None` ✓ |

All match the plan's pinned values exactly. Hand-traced all 15 `B5_CORPUS` pairs and all 13
`B4_CORPUS` pairs against the live function bodies (`_is_inside_tests`, `_literal_key_present`) —
zero mismatches. Also independently confirmed T-05's grep targets: line 93 today reads exactly
`"PASS test-unit.py" not in p.stdout`; line 121 (case 4) already reads `"PASS test-" not in
p.stdout`; no other line in the file contains either exact substring (line 22's f-string
`"PASS test-{kind}.py")` does not match `'"PASS test-" not in p.stdout'`). Post-fix count is exactly
2 as T-05's verify requires. This is the third independent confirmation (two prior readers plus
mine); I looked specifically for a disagreement per the dispatch's instruction and found none.

## Specification completeness

No placeholders. Every `verify:` is a literal shell block runnable from repo root, consistent with
the file's own `TESTS_DIR`/`ROOT`/`BIN` conventions. `code_grade.grade_source(source_text, path)`
signature and `FunctionGrade.qualname`/`.grade` fields used in T-02's verify are correct against
`.claude/skills/harness/bin/code_grade.py:281,15-19` — confirmed by running it, not assumed.

## Already-assessed items, confirmed closed (rediscovery, not new)

Cross-referenced the cycle-1 goalcheck note's F-1..F-4 against the current BRIEF/plan text:
- **F-1** (BRIEF falsely disclaimed the code-grade clearance) — closed: current Non-goals section
  explicitly states the clearance IS delivered and disambiguates which grade-2 record it means.
- **F-2** (SC-09 not falsifiable) — the exit-0-is-not-enough language and named-check list are now
  present in SC-09's `verify:`. Note the residual gap above (low) is narrower than F-2 was: SC-09 is
  now falsifiable *if run*, it just isn't run by any task.
- **F-3** (SC-10 wrong evidence kind) — closed: `evidence`/`verify` now read `inspection` with
  reasoning.
- **F-4** (D-02/D-03 had `dec: none`) — closed: both now cite "Advisor RECOMMENDATION Q2 (a),
  runs/2026-09-05-2-validator/digest.md".

No re-litigation of AR-01, AL-01, AR-08, or R1/R2 — none of my findings touch their subject matter.

## What the feature needs to ship

Nothing blocking. The plan is internally consistent, every number checks out against three
independent derivations, and the dependency chain has no self-invalidating hazard. Recommend the
operator/lead confirm who executes SC-09's literal verify command (build-time qa gate, presumably)
before signing, since no plan task does.

plan.yaml and BRIEF.md are unmodified by this review.
