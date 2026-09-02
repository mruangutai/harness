# Plan review — FEAT-47-tests-layout — plan-panel / scope — cycle 0

**BLUF.** No orphan requirements and no scope creep: every REQ-01..REQ-11 traces to at least one
task, every task's `traces:` cites a real REQ, and nothing in the nine tasks touches the explicitly
out-of-scope items (#979's mutation gate, the third own-product base, the `is_control_plane_target`
rename, change-based selection). The `depends_on` graph is acyclic and every edge I checked is
functionally required (T-05←T-07 for the unit-count math, T-08←T-07 for D-09's no-parallelism-before-
independence rule, T-05←T-04 for the empty-bin-of-probes invariant). File lists match their task
intents throughout. The count arithmetic (36 integration, 19 unit, 21 unit after T-05+T-07, 37
integration after T-05) is internally consistent and matches the research baseline. Five findings
below, none `must_fix`-blocking on their own, but finding 1 is exactly the `#979` defect class this
feature exists to close and should not ship unaddressed.

## Findings

**1. [high] SC-05's "a second copy would falsify this criterion" has no instrument that can catch a second copy.**
`plan.yaml` BRIEF SC-05: "The layout predicate is one function in one file... A second copy of the
predicate anywhere would falsify this criterion." T-05 (plan.yaml:~520-620) deletes the *old* bash
duplicate (`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/drift-detector/KIND-CROSS-CHECK) and T-06's verify
greps repo-wide for the literal strings `UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS`, `check-kinds`
(plan.yaml T-06 verify block). That only catches a *literal reintroduction of the old names*. Nothing
in any task's `verify:` or intent scans for a *new*, differently-named reimplementation of the
layout-violation logic (e.g. inline in `run-unit-tests.sh`, or a second `violations()`-shaped
function elsewhere). `tests/unit/test-suite-layout.py` (T-05 step 2) only exercises the behavior of
`suite_layout.violations()` itself — it can't detect a duplicate living beside it. Concrete
consequence: a future edit that adds a second, slightly different layout check (the exact failure
DEC-197 already recorded once) would leave SC-05 green forever, because the criterion asserts a
property no check in the plan actually measures.

**2. [med] T-02's rename-count check is a lower-bound count that fixture renames can pad.**
T-02 verify (plan.yaml ~T-02): `git diff -M --name-status ea6f51f... -- tests .claude/skills/harness/bin | grep -c "^R"`, asserted `-ge 36`. T-02's own intent also `git mv`s the 4 fixture files
(`bin/fixtures/*` → `tests/integration/fixtures/*`) in the same path scope. If, say, 4 of the 36 named
test files lost rename-tracking (effectively delete+add rather than `git mv`, e.g. because an editor
touched them mid-move) but the 4 fixture renames land cleanly, the total is still exactly 36 and the
`-ge 36` check passes — silently masking exactly the files whose history-preservation the check
exists to prove. The per-file `python3 "$f"` loop above it proves the *content* is correct
regardless, so this is a real but narrow gap: it only affects the "history followed the move" claim
in T-02's own intent, not functional correctness.

**3. [med] The default worker-count logic (`min(processors, 8)`, fallback-to-4-on-`getconf`-failure) has zero verify coverage.**
T-08 intent step 2 (plan.yaml ~T-08): "if it returns empty or non-numeric, fall back to 4 and say so
on stderr. Never fall back silently: a pool that quietly became one worker turns a 47-second gate
into a 247-second one and nothing reports why." Neither T-08's own inline verify nor the new cases
listed for `tests/integration/test-run-unit-tests-layout.py` (T-08 step 7) exercise this fallback
path or assert the `min(nproc,8)` cap arithmetic. On any host with ≤8 cores (plausible for CI), the
cap is never exercised either. The one behavior the intent explicitly calls "never silent" ships with
no automated check that it stays that way.

**4. [med] REQ-03's classification correctness is a one-time inspection, not an ongoing CI gate — and this gap is undisclosed.**
REQ-03 ("every test file's kind matches the [in-process vs. cross-process] property... rather than
the kind it historically sat under") is verified by SC-09, `verify: inspection`, graded by manually
running `tests/manual/suite-census.py children`. `suite_layout.violations()` (T-05), the only check
that runs on every future CI invocation, tests directory *shape* only — non-empty, no duplicate
basename, no test-shaped file in `bin/` — never the child-process property that actually defines
`unit` vs `integration`. So a future test misplaced in `tests/unit/` because it forks a child is
caught by nothing automated. BRIEF's own "Verification gaps" section discloses the analogous SC-12/
SC-13 (stability/speed) gap explicitly and in detail, but says nothing about this one for SC-09/
REQ-03 — it's the same shape of gap, left unstated.

**5. [low] T-05's intent miscounts the number of new no-baseline test files by one.**
T-05 intent (plan.yaml, `suite-census.py verdict-lines` description): "A file on disk with no
baseline row is printed as new and does NOT fail — this feature adds two such tests." By the time
T-05's own verify runs `suite-census.py verdict-lines` (T-05 depends on T-07), three files exist
with no baseline row: `tests/unit/test-suite-layout.py` (T-05 step 2), `tests/unit/test-suite-independence.py` (T-07 step 5, lands first per the depends_on edge), and
`tests/integration/test-run-unit-tests-layout.py` (T-05 step 3). No operational impact — the tool's
spec doesn't fail on "new" regardless of count — but it's a factual slip in a plan whose whole thesis
is measured-not-assumed counts.

## Checked and clean

- REQ↔task tracing: all REQ-01..REQ-11 have ≥1 task; every task's `traces:` cites an existing REQ. No
  orphans either direction.
- Out-of-scope items respected: no touch to #979's mutation gate/host kind/fixture provenance, no
  third own-product base, no rename of `is_control_plane_target` (only its docstring text, per T-01
  step 3), no change-based selection logic anywhere (D-11 correctly left as rejected-and-recorded).
- `depends_on` graph: acyclic; T-05←[T-03,T-04,T-07] and T-08←[T-05,T-07] are each functionally
  required, not just declared — verified against what each task's verify/intent actually reads.
  T-05's declaration-order position (before T-06/T-07 in the YAML list) does not match its true
  topological position (after T-07); this is consistent with D-09's explicit statement that the
  constraint lives in `depends_on`, not list order, so I did not file it as a finding.
- T-07 (identify #1053 partner): its verify runs files directly with `python3`, never through
  `run-unit-tests.sh` — correct, since the runner is explicitly unusable between T-02 and T-05 (stated
  in T-02's and T-07's own intent) and T-07 doesn't depend on T-05.
- File-count arithmetic: 36 (T-02) + 19 (T-03) + 1 probe (T-04) = 56, matches BRIEF's baseline; 10
  reassigned unit→integration files matches D-04's list exactly; unit 19+1(T-05)+1(T-07)=21 and
  integration 36+1(T-05)=37 match both T-05's and T-08's verify counts.
- `files:` vs. `intent:` cross-check: every file listed by T-01, T-02, T-03, T-04, T-05, T-06, T-07,
  T-08, T-09 is addressed by a step in that task's own intent; no orphaned file entries, no intent
  step touching a file absent from the list.
- SC↔instrument coverage: every SC-01..SC-14 has a task that builds its evidence (census, layout
  guard, domain assertions, bisect/confirm, stability); every instrument built (`suite-census.py`,
  `suite_layout.py`, `suite-bisect.py`, `suite-stability.py`) is read by ≥1 SC. No orphan instruments.
- Fail-open scan on `verify:` blocks: all `set -e` scripts, `if grep ...; then exit 1; fi` idioms
  correctly fail *closed* (absence of a match ≠ pipeline failure); exact-count assertions (`= 21`,
  `= 37`, `= 36`) are paired with explicit no-FAIL-lines checks, not counts alone. Only the T-02
  rename count (finding 2) uses a loose bound.

## Severity legend (mine, not reassignable)
high / med / med / med / low, per finding above.
