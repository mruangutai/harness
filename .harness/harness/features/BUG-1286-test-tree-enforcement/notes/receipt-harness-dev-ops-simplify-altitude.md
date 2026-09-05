# ALTITUDE angle — BUG-1286-test-tree-enforcement plan draft

**BLUF:** The plan fully closes cost (a) — tracked test-shaped files outside `tests/**` are refused,
with strong REQ/SC coverage. Cost (b) — `harness.json`'s `test_kinds.unit.detect` claiming
repository-wide discovery no runner performs — is only narrowed to practical vacuity by T-01's guard;
the literal false claim in `harness.json` stays, frozen by SC-11/Constraints, and the compensating
reasoning (nothing can exist outside `tests/**` for the glob to over-claim about) is never written
down anywhere in BRIEF.md or plan.yaml. Two smaller drift risks: the test-shaped vocabulary and the
FEAT-44 exception's reason text are each hand-restated in prose across D-01/T-01/T-05 and
D-05/T-01/T-04/T-05 instead of citing the code registry as the single authority.

## Q1 — stated problem vs. neighbouring one

**finding.** Cost (a) is fully traced: REQ-01–05, REQ-08 and SC-01–08, SC-12 all bind the tracked-file
refusal (T-01/T-02). Cost (b) has **no REQ or SC that binds it** — `Constraints` (BRIEF.md:53-54) and
SC-11 (BRIEF.md:97-100) explicitly freeze `.harness/harness.json` `test_kinds`/`test_matrix` as
unchanged, so `unit.detect`'s `**/*.test.*|**/*_test.*|**/test_*.py` text still literally claims
repository-wide discovery after this ships.
- artifact: BRIEF.md Problem, lines 10-14 (states cost b) vs. Constraints lines 53-54 / SC-11 (freezes
  the file cost b) lives in)
- cost: cost (b) is **narrowed, not closed** — once T-01 lands, no tracked test-shaped file can exist
  outside `tests/**` except the one documented exception, so the over-broad glob has nothing left
  outside `tests/` to falsely claim discovery over. That is a real compensating argument, but it
  appears **nowhere** in the artifacts: BRIEF's own "Verification gaps" section (lines 106-114) covers
  only null/excluded kinds, never revisits the detect-glob claim its own Problem section raised. A
  future reader re-litigating "why didn't this fix the detect lie" has nothing to point to.
- alternative: add one line to BRIEF.md's `## Verification gaps`:
  `"harness.json's unit.detect glob still literally claims repository-wide discovery; T-01's guard
  makes the claim vacuous rather than accurate — no tracked test-shaped file can exist outside
  tests/** for it to over-match. The text itself is not corrected (frozen by SC-11); accepted here as
  BUG-1286's scope is the guard, not the config wording."`
- **briefing-row** — worth pm recording so review doesn't independently rediscover cost (b) as
  unaddressed; not a fold-in because it doesn't change any task, only names an already-made trade.

## Q2 — one authoritative vocabulary statement, or several

**finding.** Four independent statements of the same test-shaped vocabulary: D-01's prose
(plan.yaml:36-39), the runtime authority `NAME_PATTERNS`/`SOURCE_EXTENSIONS` in `suite_layout.py`
(T-01 intent, plan.yaml:114-116), T-03's census tool (plan.yaml:242-244, correctly imports rather than
restates), and T-05's DEC-213 amendment paragraph (plan.yaml:316-319, hand-restates the same five
patterns and seven extensions in prose for "the current contract").
- artifact: plan.yaml T-05 intent, lines 316-319, vs. T-01 intent lines 114-116
- cost: `suite_layout.py`'s constants are the only place values can actually change; DEC-213's amendment
  is a **living "current contract" claim** with no mechanism forcing re-sync — if a future feature adds
  an extension to `SOURCE_EXTENSIONS`, DEC-213 goes stale exactly the way DEC-213's own bin-only
  enumeration went stale, which is what this feature exists to fix.
- alternative: T-05 intent should read, in place of restating the five patterns and extensions: "state
  the predicate's reach as: refuses every tracked test-shaped file outside tests/, per the
  NAME_PATTERNS/SOURCE_EXTENSIONS vocabulary defined in suite_layout.py (see that module for the exact
  list, which is authoritative)." T-03 already does this correctly for the census tool; T-05 should
  match it.
- authority belongs in `suite_layout.py`'s constants (already true in code); prose descriptions should
  point at it by name, never re-enumerate it.
- **fold-in** — a wording-only change to T-05's intent; low risk, pm can apply directly.

## Q3 — capability at caller vs. callee

**no finding requiring a change, one testability cost worth naming.** `run-unit-tests.sh:33` stays a
pure one-line delegation (`suite_layout.violations(root)`) — the plan correctly keeps git enumeration
(`tracked_paths()`) inside the module `violations()` calls, not bolted onto the caller. That is the
right home for the capability itself.
- artifact: plan.yaml T-01 intent lines 126-133 (git enumeration lives in `suite_layout.py`) vs.
  `tests/unit/test-suite-layout.py`'s existing single-arg call `violations(ROOT)`
- cost: because `violations()` performs the git call itself rather than accepting a caller-supplied
  tracked-path set, 5 of T-01's 8 new unit cases (plan.yaml:159-181, cases 1,2,3,4,6/7) must build real
  `git init` fixtures — mkdtemp, `git init -b main`, `git add -A`, commit — purely to exercise branches
  (registry policing, vocabulary boundary) that do not need real git behaviour, only a tracked-path
  set. A `violations(root, tracked_paths_fn=tracked_paths)` injection point would let those cases pass
  a plain list instead of standing up a repository, at the cost of widening `violations()`'s signature.
- this is a real, measured cost (five real subprocess-backed fixtures per unit run) but reshaping it
  now touches the already fully-specified shape of 5-of-8 test cases in a task the plan has pinned in
  unusual detail — not a wording fix.
- **briefing-row** — record the injection-point alternative for pm to weigh against T-01's already-fixed
  test design; not a fold-in because applying it silently would rewrite cases the plan pinned exactly.

## Q4 — accepted residuals and their compensating controls

- **BRIEF "Verification gaps" (component/ui/typecheck null, functional/eval excluded, FEAT-44 `.ts`
  never type-checked)** — compensating control named: DEC-187, and the explicit statement that no SC
  rests on a null kind. No deeper fix available without reopening DEC-187 repo-wide. **leave.**
- **D-05 (FEAT-44 probe stays at its current path, not relocated)** — compensating control named:
  relocating would rewrite a landed feature's shipped evidence/review record, and keeping it live makes
  the registry entry load-bearing (real coverage). No deeper fix that doesn't reopen a settled,
  shipped feature. **leave.**
- **D-04 (filesystem bin clause retained beside the index clause, dedup't)** — compensating control
  named: the bin clause catches untracked plants an index scan cannot see; dedup logic is specified
  (plan.yaml:69, 143). **leave.**
- **Cost (b), residual from Q1** — this is the one residual with **no compensating control named in the
  artifacts** (see Q1). Same finding, cross-referenced here rather than duplicated. **briefing-row**
  (already filed under Q1).

## Q5 — a rule stated in several task intents where one authority should carry it

Two instances, both variants of the same drift pattern as Q2:
- **Test-shaped vocabulary** — D-01 (plan.yaml:36-39), T-01 (plan.yaml:114-116, the real authority),
  T-05 (plan.yaml:316-319, hand-restated). Authority: `suite_layout.py`'s constants. Covered under Q2.
- **FEAT-44 exception's reason text** — independently worded in D-05 (plan.yaml:76-82), T-01's registry
  seed reason (plan.yaml:120-122, this is the actual stored string), T-04's audit note instruction
  (plan.yaml:289-291, "in your own words"), and T-05's DEC-213 amendment (plan.yaml:332-333). Four
  independent phrasings of one fact (why this one path is exempt). Authority should be the literal
  reason string stored in `suite_layout.DOCUMENTED_EXCEPTIONS` (T-01); T-04 and T-05 should quote it
  rather than re-derive it, so a future edit to the registry's reason can't leave DEC-213 or the audit
  note describing a superseded justification.
- artifact: plan.yaml T-04 intent line 289 ("the reason in your own words") vs. T-01 intent lines
  120-122 (the actual stored reason string)
- cost: three independent prose renderings of one exemption's justification can drift from the code's
  own stored reason and from each other with nothing to catch it.
- alternative: T-04 intent, replace "the reason in your own words" with: "the reason, quoting
  suite_layout.DOCUMENTED_EXCEPTIONS' stored text for that path verbatim." T-05's amendment paragraph
  (plan.yaml:332-333) should do the same.
- **briefing-row** — worth pm's attention alongside Q2, but touches wording in two already-detailed
  task intents (T-04, T-05); bundling with the Q2 fold-in risks pm treating two independent findings
  as one edit.
