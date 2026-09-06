# EFFICIENCY angle — BUG-1302 plan draft — harness-dev-ops

**BLUF:** No material waste. All five `verify:` commands are structurally estimated to be well
inside a 60s bound (unmeasured — see limitation below). One low-severity finding: T-01/T-02/T-03's
intent prose implies a shared `ast` parse ("the same … parse", "the ast parse already present") but
never directs the implementer to actually store one, so as worded each task most plausibly adds its
own independent `read_text()` + `ast.parse()` of the same ~565-line file. The four full-file
`verify:` reruns across T-01→T-04 are boundary evidence, not repetition — each is a distinct commit
step with its own red/then-green requirement, and SC-09 requires end-to-end passage anyway, so a
scoped run at T-02/T-03/T-04 could not substitute for it.

**Limitation, stated per the dispatch's constraint:** I did not run either test file or
`run-unit-tests.sh`. Every cost below is a structural estimate from reading the code (operation
counts, subprocess counts, file sizes), not a measurement. Where I say "within bound" that is an
estimate, never a timed result.

## Structural cost, read not run

`tests/unit/test-suite-layout.py` (565 lines) at HEAD, one full run:
- 1 `git ls-files -- *.py` (line 111) feeding `sole_implementations()`, which `read_text()`s every
  matched file (repo floor asserted `>= 90` tracked `.py` files, line 114).
- `_violations_callers(ROOT, SOURCE_EXTENSIONS)` (line 152) — its own `git ls-files` (unfiltered)
  plus a `read_text()` of every tracked file outside `tests/` with a `SOURCE_EXTENSIONS` suffix (7
  extensions) — **called twice**, once at line 174 for the equality check and again at line 176 as
  the `repr()` detail argument to the same `check()` call (Python evaluates both arguments
  eagerly). This is a pre-existing double full-repo sweep, not something any of T-01..T-05 adds.
- 8 fresh git fixtures: `base_git_fixture()` (cases 1,2,3,4,6,8,10 — 7 calls, each one `git init`)
  plus case 9's inline `git init` (1 more) = 8 `git init` invocations; 5 of those fixtures also run
  `git_commit()` (`git add -A` + `git commit`, 2 subprocess calls each). Plus 4 non-git
  `legal_tree()` builds (loop×2, line 91, line 286) and 3 bare `tempfile.TemporaryDirectory()`
  shape probes (lines 123–138).
- Net: on the order of 20+ subprocess spawns and 90+ file reads per run. This is the file's
  existing baseline, already inside the `run-unit-tests.sh --kind unit` CI gate today, per the
  dispatch's framing — not a cost this plan introduces.

`tests/integration/test-run-unit-tests-layout.py` (136 lines): ~10 fresh git-tree fixtures, each
`subprocess.run`-ing the real `run-unit-tests.sh` end to end (`timeout=60` per invocation, line
47) — each nested invocation itself pays the unit file's baseline above. Existing cost, unrelated
to T-05's one-clause edit.

## Marginal cost the plan adds

- **T-01:** one `B5_CORPUS` loop over 15 pure-string `_is_inside_tests()` calls (sub-millisecond)
  + one `ast.parse()` of the 565-line file (low single-digit ms). Not a hot-path add beyond the
  file's own existing per-CI-run cost; it runs once per `python3 test-suite-layout.py` invocation,
  same as everything else in the file.
- **T-02:** one `B4_CORPUS` loop over 13 calls (sub-millisecond) + a second independent
  `read_text()`/`ast.parse()` if the implementer does not reuse T-01's tree (see finding below).
- **T-03:** one dict construction (`CORPUS_BLIND_KINDS`) + one `select_control_candidate()` call
  (negligible) + a third independent `ast.parse()` under the same condition.
- **T-04:** one new git fixture (`git init` + `git add -A` + `git commit`, ~3 subprocess spawns)
  building a 2-file mini-repo, then one `_violations_callers()` call over it (2 files — trivial).
  This is new, deliberate coverage for a previously-unguarded exception path, not waste.
- **T-05:** a string-literal edit to one existing clause. Zero added operations.

None of this is material against the file's existing baseline (dominated by ~20 subprocess spawns
and ~90 file reads), and none of it is added to any per-write or per-session hot path — it only
runs inside the `run-unit-tests.sh --kind unit` CI gate, a one-shot-per-invocation boundary, not a
hook.

## Per-task 60-second bound (structural estimate, unmeasured)

- **T-01:** within bound (structural estimate, unmeasured) — marginal add is low-single-digit ms
  against an already-CI-budgeted baseline.
- **T-02:** within bound (structural estimate, unmeasured) — same reasoning; marginal add is a
  13-entry string-match loop plus at most one more `ast.parse()`.
- **T-03:** within bound (structural estimate, unmeasured) — marginal add is one dict literal and
  one function call.
- **T-04:** within bound (structural estimate, unmeasured) — marginal add is one small git fixture
  (~3 subprocess spawns over 2 files), an order of magnitude smaller than the file's other 8
  fixtures.
- **T-05:** within bound (structural estimate, unmeasured) — zero added operations; the file's
  existing ~10 nested `run-unit-tests.sh` invocations (each internally timeout-capped at 60s) are
  pre-existing cost this task does not touch.

## Findings

- **F-1** — task T-02/T-03, severity **low**, `tests/unit/test-suite-layout.py` (post-T-01 lines
  near the new `_is_inside_tests`/`_literal_key_present` checks, T-02 intent line ~121-122, T-03
  intent line ~172). T-02's intent says "Using the ast module imported by T-01 and the same
  `Path(__file__).read_text()` parse" and T-03's says "Using the ast parse already present in the
  file" — both phrasings gesture at reuse but neither directs the implementer to actually bind a
  shared parsed tree (e.g. a module-level `_MODULE_AST = ast.parse(Path(__file__).read_text())`
  computed once after the imports). Followed literally, the most natural per-task implementation
  is three independent `read_text()` + `ast.parse()` calls of the same 565-line file across
  T-01/T-02/T-03 — the same file read repeatedly across sequential tasks where one pass could feed
  several, the exact pattern this angle is asked to catch. **Honest cost:** each `read_text()` +
  `ast.parse()` of a <30KB, 565-line file is on the order of a few milliseconds; three redundant
  passes cost roughly 10-15ms against a baseline already dominated by ~20 subprocess spawns
  (each tens of ms) — not material to the 60s bound and not a hot-path risk, but real, avoidable,
  one-line-fixable duplication. **Recommended change:** amend T-01's intent to add, immediately
  after the `import ast` line, `_MODULE_AST = ast.parse(Path(__file__).read_text())` at module
  scope, and amend T-01/T-02/T-03's intents to each reference `_MODULE_AST` instead of re-invoking
  `ast.parse(Path(__file__).read_text())`.

No other findings. The four sequential full-file `verify:` reruns (T-01→T-04) are boundary
evidence for each task's own commit, not repetition — SC-09 requires end-to-end passage of the
whole file, so a scoped/narrowed run at any of T-02/T-03/T-04 could not stand in for it. The
pre-existing double invocation of `_violations_callers()` at lines 173/176 is real but is not a
finding against this plan: no task's intent touches those two lines, and T-04's own intent
explicitly says "Do not change the repository-wide caller check's expected set" — recommending a
fix there would be out of this plan's stated scope, and I am recording it as an observation, not a
finding.

## Confirmation

Wrote nothing under `tests/`. Did not touch `plan.yaml` or `BRIEF.md`. Ran no test suite, benchmark
or timer — every cost above is read, not measured.
