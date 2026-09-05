# Plan-panel c8 — scope reader (code side) — BUG-1286-test-tree-enforcement

**BLUF: PASS with one LOW note.** Every hunt item I ran against actual `fnmatch`/`code_grade`/git-index
probes came back clean — the amendment closes what cycle-6 flagged and stays internally consistent. The
one new fact I found is that the ADVISOR CONSULTATION's stated impossibility (a) is technically
overbroad — a counterexample pattern exists — but it does not touch (b) soundness or (c) coverage, and
none of the four running kinds' actual `detect` values are of the exempted shape. No `must_fix`.

## ADVISOR CONSULTATION — required answers

**(a) Is pm's impossibility claim TRUE as stated? — FALSE AS STATED; TRUE for every pattern actually in
play.** Probe (`fnmatch`, run live):

```
pat1 = "**/test_*.py"; escape1 = "a/test_/b/random_unrelated_name.py"
fnmatch.fnmatch(escape1, pat1) -> True ; is_test_shaped(escape1) -> False   # confirms pm's mechanism

pat2 = "**/test_foo.py"   # a "**/"-prefixed pattern with NO wildcard after the leading "**/"
fnmatch.fnmatch("a/b/test_foo.py", pat2) -> True   -> basename is ALWAYS exactly "test_foo.py"
fnmatch.fnmatch("some/dir/evil.py", pat2)   -> False
fnmatch.fnmatch("some/dir/gen.py", pat2)    -> False
fnmatch.fnmatch("some/dir/test_food.py", pat2) -> False
```
`pat2` is `**/`-prefixed and *does* satisfy the universal form: every path it can match has the fixed
literal basename `test_foo.py`, which `is_test_shaped` always accepts, so there is no escaping path at
all. pm's argument ("a bare `*` always crosses `/`, so every `**/`-prefixed pattern can match some path
whose basename the guard never refuses") only holds for a pattern that carries a wildcard *after* the
leading `**/`; a pattern whose tail is pure literal has no such freedom. This is a real counterexample to
the sentence as literally written in D-01's `because` (`plan.yaml` ~line 88) and SC-19's HYGIENE
paragraph (`BRIEF.md` ~line 190), both of which say "no `**/`-prefixed fnmatch pattern satisfies that
property" with no qualifier.
**Consequence, checked and found benign:** none of the four running kinds' actual `detect` patterns are
of this literal-tail shape (`unit`: `**/*.test.*`, `**/*_test.*`, `**/test_*.py`, `tests/unit/**`;
`integration`: `tests/integration/**`; the two `locally_run` kinds are pure literals with no `**/`
prefix at all — `tests/manual/probe-omp-session-accessor.py`). Traced against the plan's own HYGIENE rule
for `pat2`: core after stripping `**/` = `"test_foo.py"`, contains **no** wildcard at all, so the
GUARD-COVERED clause's own "core contains a wildcard" test fails and the rule classifies it
UNCERTIFIED — i.e. the plan's chosen sufficient condition does **not** get fooled into certifying `pat2`
as safe; it just over-flags a pattern that happens to be safe. Fail-closed, not fail-open. **LOW**
severity: an overstated justification sentence in D-01/SC-19, zero operational consequence today.

**(b) Is the substitution SOUND? — YES, with one caveat already disclosed, worth restating precisely.**
The behavioural half re-derives `tracked_paths(ROOT)` at *test-run time*, not at plan- or commit-time, so
it is not blind to a future commit — the very next `python3 tests/unit/test-suite-layout.py` invocation
after such a file lands will see it and redden. But the mechanism that "carries" the residual is the
**unit test's own assertion**, not `suite_layout.violations()` itself: `is_test_shaped()` is
basename-only by construction (D-01), so it structurally can **never** flag `.harness/tools/test_dir/gen.py`
as a violation — the production guard lets it through silently, forever. REQ-09's word "refused by the
guard" is therefore true only in the sense of "the unit suite reddens on the next run", not in the sense
of "the runtime pre-check (`run-unit-tests.sh --check-layout`) refuses it before any test executes"
(REQ-01's stronger guarantee, which this residual class does not get). The plan's own text is honest
about this — BRIEF's residual bullet and case 11's closing sentence both say "reddens the unit suite",
never "refused by the guard" for this specific class — so I read this as accurately disclosed rather than
misrepresented. Still: it is a genuinely different (weaker) enforcement mode than the one REQ-01
promises for ordinary test-shaped files, and a reader skimming REQ-09's headline sentence alone could
believe the production guard closes it. Recorded as a clarity note, not a defect.

**(c) Any class of counted-but-unrefused path escaping BOTH halves? — NONE FOUND.** I checked whether the
directory-component escape is unique to `**/test_*.py` (the only example named in BRIEF's residual
bullet) or also afflicts the two AGNOSTIC patterns:
```
"a/x.test.sub/file.py"   vs "**/*.test.*"  -> True  | is_test_shaped(basename "file.py") -> False
"a/y_test.sub/file.py"   vs "**/*_test.*"  -> True  | is_test_shaped(basename "file.py") -> False
```
Same escape, all three wildcard-bearing running patterns. This is **not** a new gap: T-01 case 11's
positive-control corpus already requires all three directory-component shapes
(`.harness/tools/test_dir/gen.py`, `.harness/tools/a.test.d/gen.py`, `.harness/tools/a_test.d/gen.py`,
`plan.yaml` ~lines 553-556) — the behavioural half's `_is_test_path` call covers whichever pattern causes
the match, generically, not pattern-by-pattern. I also checked the INAPPLICABLE branch for a fail-open
hole (a broken `is_test_shaped` — e.g. bugged to always return `True` — would make every corpus candidate
fail to "qualify", forcing INAPPLICABLE instead of a hard fail): that specific regression is caught
anyway, on a different assertion — T-01 case 1's exact-equality list (SC-06) would gain spurious entries
the moment `is_test_shaped` starts over-matching legitimate `tests/manual`/`tests/unit` fixture files, so
the INAPPLICABLE escape hatch does not, in practice, hide an under-refusal. No escaping class found.

## Hunt — findings

None. Every item below is a genuine falsification attempt with a concrete probe/measurement, not an
unexamined assumption.

- **Union-vs-unit phrasing (D-01/REQ-09/SC-19/T-05 consistency).** Grepped every `unit.detect`/"unit
  kind" occurrence in `plan.yaml` and `BRIEF.md`. Three of four hits are: (1) the historical Problem
  statement (`BRIEF.md:12`, correctly describing the *original bug*, not a live obligation), (2) the
  superseded `panel:` block (out of scope per the dispatch), (3) a worked illustrative mutation example
  naming `unit.detect` specifically as *one instance* to mutate (`plan.yaml:645`, fine — the case's
  governing rule at `plan.yaml:529-530` explicitly says "Do NOT scope this case to the unit kind"). No
  surviving unit-only phrasing where the union was meant.
- **Amendment breakage.** SC-06's one-element exact-equality list (`BRIEF.md:88-103`) matches T-01 case
  1's fixture verbatim (no `*_test.*`/`*.test.*` planted there, case 10 owns that). T-03's `TOTAL 85 /
  OUTSIDE 9 / VIOLATIONS 0` matches BRIEF's Verification-gaps closing bullet. SC→REQ→AC traceability
  table: all 9 REQs trace from at least one task (`T-01`: REQ-01,02,03,04,05,08,09; `T-02`:
  REQ-01,02,03; `T-03`/`T-04`: REQ-06; `T-05`: REQ-07 — no orphan REQ, no task citing a nonexistent REQ).
  `depends_on` graph (`T-01:[]`, `T-02:[T-01]`, `T-03:[T-01]`, `T-04:[T-03]`, `T-05:[T-01,T-02]`) is a
  valid topological order, no cycle, nothing `verify:`s a predecessor's deletion (everything here is
  additive).
- **Positive control / INAPPLICABLE.** Re-derived the corpus-selection mechanism by hand against the
  live matcher (see (c) above): dropping `**/test_*.py` genuinely falls through to the next family
  rather than going INAPPLICABLE (matches the plan's own claimed measurement); INAPPLICABLE only fires
  on a benign narrowing or an `is_test_shaped` over-match, neither of which is a fail-open scenario this
  feature exists to catch.
- **`guard-covered bucket must be non-empty`.** Not a hardcoded value pin — it asserts non-emptiness only,
  which forces the guard-covered code path to actually execute today (since `**/*.test.*`, `**/*_test.*`,
  `**/test_*.py` all currently certify guard-covered) without pinning which or how many patterns land
  there. Earns its place; replaces a cardinality pin with a coverage-sanity check, correctly per F-03/F-04.
- **Disclosed blast radius.** Verified against live `.harness/harness.json`: `component.detect` = 3
  patterns (`**/*.spec.tsx`, `**/*.stories.tsx`, `**/*.stories.ts` — matches BRIEF exactly). `ui.detect` =
  3 patterns (`tests/e2e/**|e2e/**|**/*.e2e.spec.ts`); `tests/e2e/**` certifies inside-tests, leaving 2
  uncertified — matches BRIEF's "ui leaves 2". `typecheck.detect` = `**/*.ts|**/*.tsx`, both uncertified —
  matches "typecheck leaves 2". `git ls-files | grep -E '\.tsx?$'` returns exactly three tracked files:
  `tests/unit/omp-hooks.test.ts` (inside `tests/`, irrelevant), and the two BRIEF names —
  `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts` and
  `.omp/extensions/harness-hooks.ts` — no third file exists that BRIEF failed to count. The DEC-163
  route is not a dead end: T-05's amendment states the remedy explicitly (widen vocabulary or record
  scope in DEC-213), so activation is blocked-with-a-route, not blocked-with-no-route.
- **F-01 fix presence.** Confirmed the `..`-rejection-then-normalize text is present in T-01 case 11's
  HYGIENE section and traced it by hand against `tests/../evil/**`: `..` segment present → rejected
  outright regardless of normalization; separately, its core (whole string, since no leading `**/`)
  still contains `/` so it also fails GUARD-COVERED. Uncertified either way — the fix is present and
  correct, not merely present-but-inert.

## Independent measurement reproduced

`git rev-parse HEAD` = `cab6adb2` (same commit the plan cites). Ran my own probe (not copy-pasted from
any note): `tracked=2706`, `counted-outside-tests/=0`, running kinds =
`{handoff_comprehension, integration, omp_session_accessor, unit}` — matches every prior record exactly,
at the exact cited commit, not a later one.

## Scope-reader verdict on tasks

No task serves no requirement; nothing is missing a task. `T-01`/`T-02`/`T-03`/`T-04`/`T-05` map 1:1
onto REQ-01…09 with no gap and no orphan. Nothing here is scope creep — SC-19/REQ-09's breadth beyond the
ticket's literal ask was already ratified by the operator across three rulings (off the table per this
dispatch's constraints).
