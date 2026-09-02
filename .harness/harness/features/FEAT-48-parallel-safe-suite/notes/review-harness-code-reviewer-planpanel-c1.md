# Scope review — FEAT-48 plan.yaml, cycle 1 (discharge audit)

## BLUF

**Do not sign yet.** Of the ten cycle-0 items, nine are genuinely FIXED or DISSOLVED at source —
this is a real, verified re-plan, not a relabeling. But testing D-09's own "shipping first removes
the dependency" claim against the actual sibling plan (as directed) surfaces a **new high-severity
cross-plan defect no one has caught**: FEAT-47's plan.yaml T-03 (the task that will `git mv`
`test-suite-independence.py` into `tests/unit/`) still believes the file resolves its root by a
hardcoded "four levels up" climb and instructs a builder to "repoint that climb to the two-level
form" (`FEAT-47/plan.yaml:391-395`). That is false of the file FEAT-48 actually ships — T-03's own
plan text here calls `root_above`, a pure marker walk with **no climb to repoint**
(`plan.yaml:396-413`). FEAT-47's plan was evidently drafted against FEAT-48's pre-fix draft (the
one cycle-0 F-01 was filed against) and never picked up the fix. BRIEF's own claim that the file
"survives the move with no edit" (`BRIEF.md:161`) is therefore not true of the plan that will do
the moving, today. This is exactly the defect class both features exist to kill: a claim that
reads clean in isolation and is false the moment the two plans are read together.

One second finding, lower stakes: T-06's new automated check over
`notes/measurements-parallel-suite.md` (fixing F-07) verifies shape, not authenticity — a
hand-typed note with fabricated but well-formed numbers passes it. The plan's own intent
discloses this limitation and leans on human inspection of the fenced verbatim output, consistent
with how SC-02/05/06 are already scoped `verify: inspection`; I record it as a residual gap, not a
regression.

## Discharge audit

| id | disposition | evidence |
|---|---|---|
| F-01 | **FIXED** | T-03 now calls `harness_boundary.root_above(...)`, a marker walk with zero depth arithmetic, and gives the correct reason for rejecting both alternatives (`plan.yaml:396-413`); verified against `harness_boundary.py:44-50` (`root_from_script`, pure arithmetic), `:53-79` (`resolve_root`, env-read + MARKER check), `:84-98` (`root_above`, pure marker walk) — the reasoning matches the code exactly |
| F-02 | **DISSOLVED** | D-09 now ships all of FEAT-48, including T-04, whole and before FEAT-47 (`plan.yaml:102-134`); T-04's `files:`/`verify:` hard-code `.claude/skills/harness/bin/test-run-pool.py`, which is correct because T-04 never runs after the move — the premise that made the old path wrong no longer holds |
| F-03 | **FIXED** | T-03 verify now asserts the exact named set of ten historical sites (`want - sites` must be empty, `plan.yaml:379-386`) rather than `len(lines) >= 8` — a scanner that drops any one of the ten now fails |
| F-04 | **FIXED** | T-03 verify now asserts `disc[0] >= 50` and `len(disc) == 1` at the plan level (`plan.yaml:388-390`), reading the `discovered <n>` line the intent declares a stated contract, not debug output (`plan.yaml:420-424`) |
| F-05 | **FIXED** | T-04 verify independently reconstructs attribution (`att = all(...)`), failure propagation (`fails == ["FAIL bad.py"]`), reported worker count (`"pool: 3 workers, 3 files" in w3.stdout`) and the mutation check (`m.returncode==1`, `"tracked.txt" in mo`) rather than trusting only `pool.returncode==0` (`plan.yaml:518-536`) |
| F-06 | **DISSOLVED** | The constraint F-06 says is unenforced ("T-04 lands only after FEAT-47 merges") no longer exists — D-09 removes the dependency direction entirely; nothing in FEAT-48 waits on FEAT-47 |
| F-07 | **FIXED, with a residual gap (see New Findings G-02)** | New T-06 verify parses `notes/measurements-parallel-suite.md` for existence and required shape (`plan.yaml:686-696`) — the prior total absence of a check is closed; content authenticity is not, and the plan says so |
| F-08 | **FIXED** | BRIEF SC-09 now states correctly there is no `--check` flag and cites the real mechanism (`BRIEF.md:108-117`) |
| F-09 | **FIXED** | T-05 verify now requires 14 specific phrases/numbers inside the located `## DEC-NN` section plus a 300-word floor (`plan.yaml:766-777`), not four substrings over the whole file |
| VL-01 | **DISSOLVED, but see G-01** | FEAT-47's plan no longer asserts exact equality (main-session-confirmed: floors `-ge 37`/`-ge 20`) and explicitly reconciles the two-file census against FEAT-48's D-09 by name (`FEAT-47/plan.yaml:117-134, 267-268, 382-384`) — the census deadlock is genuinely gone, not relocated. The mechanism, however, is not: see G-01 |

## New findings from the re-plan

**G-01** [severity: **high**] — anchor: `FEAT-47/plan.yaml:391-395` vs `FEAT-48/plan.yaml:396-413`,
`BRIEF.md:161`. D-09/BRIEF's claim that `test-suite-independence.py` "survives the move with no
edit" because it resolves its root "by marker walk rather than by counting directory levels" is
false of the sibling plan that performs the move: FEAT-47 T-03's intent describes the file as
deriving its root by "four levels up while it sits in bin, two levels up from tests/unit" and
instructs "Repoint that climb to the two-level form." That description matches FEAT-48's *pre-fix*
draft (what cycle-0 F-01 was filed against), not the shipped `root_above` call, which has no climb
of any kind to repoint. Concrete consequence: a builder executing FEAT-47 T-03 who follows the
written instruction rather than reading the actual file risks introducing depth-counting arithmetic
into `test-suite-independence.py` where none exists today — regressing exactly the hazard F-01 was
raised, and fixed, to remove. FEAT-47's own T-03 verify block would not catch this: it only runs
`python3 "$f"` for each moved file and checks exit 0 (`FEAT-47/plan.yaml:358-366`), and
`root_above` returns a correct root regardless of directory depth, so a spurious "repoint" edit
that keeps the file syntactically valid could pass silently either way. This is FEAT-48's own
D-09/BRIEF claim failing verification against the very sibling plan it is a claim about — not a
FEAT-47 code defect, a cross-plan text staleness defect that undermines D-09's "no edit" framing
until someone updates FEAT-47's T-03 intent to name `root_above`.

**G-02** [severity: **med**] — anchor: `plan.yaml:686-696` (T-06 verify), intent at `:726-736`.
T-06's new automated check on `notes/measurements-parallel-suite.md` is a set of regexes against
line shape (`run \d+ exit \d+ ...`, `control broken reads \d+`, etc.) with numeric range checks,
not an authenticity check. Concrete consequence: an operator under time pressure could hand-type
ten `run N exit 0 45.0s` lines, `control broken reads 1`, `post-fix broken reads 0`, and a
`pool: 8 workers, 56 files, 50.0s wall` line without running anything, and T-06's verify passes.
The plan discloses this itself ("What that still cannot prove is that the numbers were measured
rather than typed; the fenced verbatim command output beside them is what a reviewer reads for
that," `plan.yaml:736`) and SC-02/05/06 remain `verify: inspection` in BRIEF precisely because of
this — so this is a disclosed, partially-mitigated gap consistent with how the rest of the plan
treats unmeasurable claims, not a hidden one. Recording it as a finding because the dispatch asked
directly whether a hand-typed note satisfies the gate: it does, for the numeric shape; only human
reading of the fenced verbatim blocks catches fabrication.

**G-03** [severity: **low**] — anchor: `plan.yaml:503` (T-04 files) vs `plan.yaml:659,` step 2 of
T-06 intent (`:737-742`, registration). `test-run-pool.py` is created by T-04 but registered into
`INTEGRATION_SCRIPTS` / `test_kinds.integration.detect` only in T-06, the very next task in
sequence. `run-unit-tests.sh`'s own drift detector (`run-unit-tests.sh:60-74`) exits 2
`MISCONFIGURED` for any `test-*.py` in `bin/` absent from both arrays. If CI re-runs on the
intermediate commit after T-04 lands but before T-06 does (a common GitHub Actions default: rerun
on every push to an open PR), that intermediate state is red. T-03's own file
(`test-suite-independence.py`) avoids this by self-registering in the same task it is added
(`plan.yaml:415-419`); T-04 does not follow that pattern. Likely harmless if only the branch's
final HEAD gates the merge, which is the typical setup here — recorded as a low-severity
consistency gap, not a blocker.

## SC-01 .. SC-10 — reddening change, and which task produces the graded artifact

- **SC-01**: reddens if T-01's live-mtime/bytes-unchanged assertions fail, or the crashing-case
  stops emitting `CRASHED`/exit 2. Produced by T-01's own verify block. Clean.
- **SC-02**: reddens if a post-fix poll sees a broken read, or the `ea6f51f` control poll sees zero.
  `verify: inspection`; T-06's note supplies `control broken reads <n>` / `post-fix broken reads 0`,
  parsed by T-06's verify for shape (G-02 notes the authenticity gap).
- **SC-03**: reddens if the live scan reports >0, discovers <50 files, resolves the wrong root, or
  misses any of the ten named historical sites. Produced by T-03's own verify block. Clean.
- **SC-04**: reddens if `test-suite-independence.py` is unregistered or the `PASS` line is absent
  from a real `--kind unit` CI run. Registration is T-03's; the evidentiary `PASS` line is recorded
  in T-06's note; the actual CI gate is the existing (out-of-plan) `--kind unit` workflow step.
- **SC-05**: reddens if any of ten `--kind all` runs fails or fewer than ten ran. T-06's note,
  parsed for `len(runs)==10` and `set(runs)=={"0"}`.
- **SC-06**: reddens if the printed wall time exceeds 120s or is absent. T-06's note, parsed for
  the `wall` regex against `<= 120`.
- **SC-07**: reddens if `--check-kinds`, the PASS/FAIL contract, or the unknown-kind exit-2 path
  regress. Produced by T-06's verify block (`ck.returncode==0`, `not ran`, `bad.returncode==2`).
  The discriminating half (real unit/integration runs) is carried by the untouched, pre-existing
  `test-run-unit-tests-kinds.py` — unchanged from cycle 0's reasoning.
- **SC-08**: reddens if completion order matches input order on a set built to scramble, or if the
  verdict set changes at 1 worker vs. 4. Produced *only* inside `test-run-pool.py` case (e) — T-04's
  plan-level verify does not independently reconstruct order-scrambling the way it does attribution
  and propagation, so this one property is still exit-code-only trust of the newly authored suite
  (a narrower, residual instance of the pattern F-05 used to name broadly). Not raised as a separate
  G-id: the mechanism it is checking (thread-pool scheduling from a shared queue) is simple enough,
  and every *other* REQ-07-adjacent property in this task now has an independent check, that I judge
  this below the bar for a new finding — recorded here per the sweep's own instruction to name it.
- **SC-09**: reddens if the required phrases/word floor are missing from the DEC section or the
  index drifts. Produced by T-05's verify block. Clean.
- **SC-10**: reddens if the mutating fixture exits 0, no `MUTATED` line names the path, the
  subprocess-vector fixture is missed, a non-checkout directory reports clean, or
  `run-unit-tests.sh` invokes the pool without `--mutation-check`. Direct-write and non-checkout
  cases are reconstructed at T-04's plan level; the subprocess-vector leg lives in
  `test-run-pool.py` case (g) only — but the mechanism (a before/after snapshot of on-disk
  size/mtime) is vector-agnostic by construction, so this is a belt-and-suspenders redundancy
  rather than a real coverage hole. `--mutation-check` always being on is bound by T-06's verify
  (`len(inv)==1 and "--mutation-check" in inv[0]`). Clean.

## Assessed and dismissed, with reasons

- **T-04/T-06 registration split (G-03) escalated to a blocker?** No — typical CI gates on final
  PR HEAD, not intermediate pushes; recorded as low severity above rather than a blocker.
- **SC-08's residual exit-code trust** — not filed as its own G-id; explained inline in the SC
  sweep above rather than duplicated.
- **REQ-06 traced only to T-06, not T-04**, despite T-04's intent substantively discussing the
  `PASS`/`FAIL` spelling contract REQ-06 protects. Not filed: REQ-06 does have a task (T-06) whose
  verify block (`--check-kinds`, unknown-kind) is the actual discriminating check; the trace list
  is accurate about where the check lives even if T-04's intent text also touches the concern.
- **`depends_on` topology looks out of file order** (T-06 appears before T-05 in the file). Checked
  the edges, not the position: `T-05.depends_on: [T-06]`, so T-06 correctly precedes T-05 — the
  graph is a valid linear chain (`T-01→T-02→T-03→T-04→T-06→T-05`), the file order matches it, and
  the dispatch's suspicion does not materialize.
- **Orphan/missing REQ traces**: REQ-01..REQ-08 each trace to at least one task; no task cites a
  REQ absent from BRIEF. Unchanged from cycle 0, still clean with the new T-06 task folded in.
- **`<cmd> | grep .` masked-exit idiom**: absent from all of T-01..T-06's verify blocks, which are
  single `python3 -` heredocs (or, for T-06's bash-level checks in FEAT-47, not this plan's
  concern). Confirmed clean, consistent with cycle 0.
- **T-04's subprocess-vector fixture not independently reconstructed at plan level**: the
  mutation-check mechanism snapshots filesystem state before/after the whole run and cannot
  distinguish a Python-level write from a shelled-out one — the property doesn't depend on vector,
  so trusting the suite for that one leg carries little incremental risk.
- **BRIEF SC-09 marked `verify: inspection` while T-05's actual mechanism is fully automated**:
  labeling is more conservative than the mechanism, not less — not a hazard, just an
  under-claim.

## Open questions

- { id: Q1, question: "G-01: who updates FEAT-47's T-03 intent to name `root_above` instead of
  'repoint the climb to two-level form'? This is a plan-text edit on FEAT-47's side that FEAT-48's
  signature cannot force, but D-09's 'no edit' framing rests on it being made before FEAT-47's T-03
  executes.", blocking: true }
- { id: Q2, question: "Does this repository's CI configuration re-run checks on every push to an
  open PR, or only at merge time? That fact determines whether G-03's registration-order gap is a
  real transient CI break or purely theoretical.", blocking: false }

```yaml
VERDICT: FAIL
DIGEST:
  headline: >-
    Nine of ten cycle-0 findings are genuinely fixed or dissolved — but testing D-09's own
    "ships first, no edit needed" claim against the sibling plan (as directed) turns up a new
    high-severity cross-plan defect: FEAT-47's T-03 still instructs repointing a hardcoded
    root-depth climb in test-suite-independence.py that no longer exists in the file FEAT-48
    actually ships, which risks a builder reintroducing the exact hazard F-01 was fixed to remove.
  severity_max: high
  findings: 3
  must_fix:
    - "G-01 (high): FEAT-47/plan.yaml:391-395 instructs repointing a four/two-level directory
      climb in test-suite-independence.py; the file FEAT-48 ships (plan.yaml:396-413) calls
      root_above with no climb at all. BRIEF.md:161's 'survives the move with no edit' claim does
      not hold against the sibling plan as currently written."
  spec_violations: []
  reviewed: "unsigned plan.yaml at HEAD of FEAT-48-parallel-safe-suite worktree"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Who updates FEAT-47's T-03 intent to name root_above so it stops instructing a repoint that doesn't apply?", blocking: true }
    - { id: Q2, question: "Does CI re-run on every PR push (making G-03's registration-order gap a live transient break) or only at merge (making it theoretical)?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-planpanel-c1.md
```
