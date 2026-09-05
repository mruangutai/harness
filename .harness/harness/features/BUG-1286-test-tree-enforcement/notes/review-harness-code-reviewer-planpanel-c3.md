# Scope review — BUG-1286-test-tree-enforcement — plan-panel cycle 3

**BLUF: the plan is internally consistent — no orphan REQs, no reversed dependencies, no
verify clause proven ungradable at its own task's completion, and every task earns its keep.
One low-severity spec ambiguity in T-03/T-04 worth tightening before dispatch; two judgment
calls ((b), (c) below) I accept as disclosed and correctly scoped rather than gating; no
must_fix.**

## Checks run, and what each returned

1. **Orphan/invalid REQ citations.** REQ-01..REQ-08 (BRIEF.md) each traced by >=1 task
   (`plan.yaml` T-01..T-05 `traces:`); no task cites a REQ absent from BRIEF.md. Clean.
2. **`depends_on` topology.** T-01 `[]`; T-02 `[T-01]`; T-03 `[T-01]`; T-04 `[T-03]`; T-05
   `[T-01, T-02]`. Listed order T-01..T-05 is a valid topological sort — every dependency
   precedes its dependent in file order. Clean.
3. **Verify clauses vs. task-completion file state**, all five re-read against the pinned code:
   - T-01 `python3 tests/unit/test-suite-layout.py && run-unit-tests.sh --check-layout` —
     `--check-layout` already exists at HEAD (`run-unit-tests.sh:16-17,40`), non-vacuous (it
     invokes the real `violations(ROOT)` against the real checkout, which must clear the new
     clause after T-01 seeds `DOCUMENTED_EXCEPTIONS` with the one live FEAT-44 entry — the other
     8 outside-tree matches are Markdown/JSONL, excluded by `SOURCE_EXTENSIONS`). The pre-existing
     `check("real layout is valid", ...)` at `tests/unit/test-suite-layout.py:20-21` already wires
     SC-08 through this same call, so T-01 does not need its own separate case for it. Clean.
   - T-02, `python3 tests/integration/test-run-unit-tests-layout.py` — self-contained, runs after
     T-01 lands (`depends_on: [T-01]`), non-vacuous per its own case 2's third assertion. Clean.
   - T-03 verify greps the `tree-audit --ref HEAD` output for the FEAT-44 row; depends on T-01's
     registry seed, correctly ordered (`depends_on: [T-01]`). Clean.
   - T-04 verify re-runs `tree-audit --ref HEAD --against <own just-written note>` — see Finding 1.
   - T-05 verify chains four checks (`grep` x2, `gen-decisions-index.py --stdout | diff`,
     `check-decision-anchors.py`); confirmed the DEC-213 heading (`DECISIONS.md:6651`), the
     amendable paragraph "One predicate guards the shape" (`DECISIONS.md:~6674-6680`), the "Amended
     by …" house style precedent (`DECISIONS.md:4908` under DEC-182), and that
     `grep -c "tracked test-shaped file outside" DECISIONS-INDEX.md` is currently 0
     (`DECISIONS-INDEX.md:213`), so the verify's non-vacuousness precondition holds. Clean.
4. **SC gradability / live anchors.** Opened all three named:
   - SC-07 → `tests/unit/test-suite-layout.py:104-105` — `active = […]` / `check("manual tests are
     not actively detected", …)` — resolves exactly.
   - SC-09 → `tests/integration/test-layout-migration.py:62` — `import layout_fixtures as lf` —
     resolves exactly.
   - SC-15 → `run-unit-tests.sh:47` — `exec python3 "$BIN_DIR/run_pool.py" --mutation-check
     "$BIN_DIR" -- …` — resolves exactly, file is 47 lines total, sole `run_pool.py` invocation.
   All three anchors are live at the pinned tip; none rotted. Every other SC's `verify:`/`evidence:`
   pairing matches a task deliverable that actually produces that evidence (unit SCs → T-01 cases,
   integration SCs → T-02 cases, inspection SCs → SC-02/12/13/14/15/16 all name a concrete grading
   procedure or citation, not a bare "looks right").
5. **Tasks/content with no live requirement.** T-03's `--against` note-comparison mode is not
   directly requested by any REQ/SC — SC-12 is graded by inspection (a human `git show` + re-run
   diff), which does not strictly need an automated comparator. I traced it anyway: T-04's own
   `verify:` calls `--against`, so it is load-bearing for that task's mechanical gate, not
   decorative, and its design took a specific defensive step (the explicit "do NOT call
   `baseline()`" warning, because that function's regex would silently diff against an empty set).
   I accept it — it earns its keep by making T-04 a real machine-checked criterion instead of a
   pure eyeball SC-12. (Same finding already surfaced in the c2 goal-check §6 as "for the panel to
   accept or strike" — this panel accepts it.)

## Finding 1 — T-03/T-04: `--against` output contract is underspecified (low, should_fix)

`plan.yaml` T-03 intent describes two paragraphs: "print the rows … then TOTAL … exit 1/0" and,
separately, "With `--against`, … compare … print MISSING/EXTRA … exit 1 on any difference." It
never states whether the first paragraph's output (the fenced row block + TOTAL line) still prints
when `--against` is supplied. T-04's `verify:` clause depends on it doing so: it re-runs
`tree-audit --ref HEAD --against qa-tree-audit.md` and greps the combined stdout for
`probe-session-accessors\.ts.*documented-exception` — a string that only appears in the *row*
output, never in a MISSING/EXTRA line (which fires only on a mismatch, and by construction the
note and the live measurement should be identical at write time, so no MISSING/EXTRA line for that
path exists either way).

Concrete consequence: if backend-dev reads "With `--against`, …" as replacing rather than
augmenting the normal output — a common "diff tool" convention, silent on match — a fully
spec-compliant `--against` implementation makes T-04's own `verify:` fail on a correct note,
forcing a re-read/rework cycle. The file's own precedent (`verdict()`, `suite-census.py:33-42`)
favors the augmenting reading (it always prints one line per test plus any mismatch lines), which
is why I rate this low rather than med — a careful implementer following in-file convention lands
on the right answer — but the plan's own text does not say so explicitly, and it is cheap to fix:
add one clause to T-03's intent stating the row block and TOTAL line print unconditionally, and the
MISSING/EXTRA/exit-code behavior is additive under `--against`.

## Judgment (a) — SC-06 exact-equality assertion: acceptable, not brittle in the way asked

The one-element list `["tracked test-shaped file outside tests/: .harness/tools/test_rogue.py"]`
is pinned by equality specifically to close the c2 goal-check gap (membership/containment cannot
prove the valid `tests/{unit,integration,manual}` files and the copied `bin/` module contributed
nothing). I traced the fixture by hand against T-01's own clause spec and confirm the one-element
result is correct given the described implementation (`tests/manual/probe-fixture.py` starts with
`tests/` so is excluded by the new clause; `test-unit.py`/`test-integration.py` sit in their own
correct kind dirs so the pre-existing clause emits nothing; the copied `bin/suite_layout.py` matches
none of the bin clause's globs). The string this test pins is introduced BY this same task (T-01),
not an "unrelated message-text" the task doesn't own — so a future wording change to that exact
message is normal coupling (the person changing the message also owns this test), not
cross-feature brittleness. I judge this an acceptable, deliberate cost for real falsifiability, not
a defect.

## Judgment (b) — D-05's archival landmine: real, disclosed, accepted — advisory only

D-05 deliberately keeps FEAT-44's `evidence/probe-session-accessors.ts` as the registry's one live
entry rather than adding a synthetic exception, and the plan states the consequence plainly: if
that evidence file is ever archived/removed, `DOCUMENTED_EXCEPTIONS`' self-policing clause
("documented exception is no longer tracked") fires on **every** `run-unit-tests.sh` invocation
repo-wide (`--check-layout` and the full run both go through `violations()` first), and only
`harness-backend-dev`/`harness-dev-ops` can edit `suite_layout.py` to clear it — not whoever
performed the archival. That is a broad, blocking blast radius (every test run, every kind) from a
narrow, unrelated housekeeping action (archiving a landed feature's evidence directory) gated to a
role that has no natural reason to be watching for it. I do not treat this as a must_fix: the trade
is explicit, reasoned (avoids rewriting a shipped feature's evidence README/review note to satisfy
a layout rule), and is exactly the kind of decision `plan.yaml`'s `decisions:` block exists to
surface for operator sign-off — the coupling is legitimate, not a plan defect, but it is worth the
operator/CEO explicitly seeing this consequence at approval rather than only backend-dev and QA.
Rated **med** as a disclosed-risk flag, not a defect in the plan's construction.

## Judgment (c) — `harness.json` extension-agnostic `detect` residual: disclosure is sufficient, does not gate

The residual BRIEF records — `unit.detect`'s `**/*.test.*`/`**/*_test.*` globs are extension-
agnostic while D-01's new vocabulary is restricted to source extensions, so a tracked `*_test.md`
outside `tests/**` would pass the new guard, be counted as a `unit` test by the kind map, and be
run by no runner — reproduces, in miniature, the exact defect class the BRIEF's own "Problem"
section names as the motivating bug. I judge disclosure sufficient for this plan cycle rather than
gating, for three reasons together: (1) REQ-01 is scoped to "test-shaped" as **this plan's own**
D-01 definition, which deliberately excludes non-source extensions with a stated reason (8 of 9
current outside-tree matches are exactly this shape, and refusing them would fight the evidence
trail); the plan is internally consistent about what it promises. (2) The class is empirically
empty at the pinned tip (T-03's audit selects *without* the extension filter specifically so this
class is measured, not blind). (3) Correcting `detect` reopens `harness.json` and DEC-197, both
explicitly frozen by this plan's own constraints (SC-14) and out of scope per the grilling note.
None of that makes the residual free, however — it is not something the grilling note or the
operator explicitly signed off on by name — so I raise it as an `open_question`, non-blocking,
rather than a finding.

## Findings summary (my own severities — nobody may reassign)

| # | Severity | Summary | Concrete consequence |
|---|---|---|---|
| 1 | low | T-03's `--against` output contract doesn't state whether the row/TOTAL block still prints under comparison mode | A spec-compliant "diff-only" reading of the same text makes T-04's own `verify:` fail on a correct note, forcing rework |
| 2 | med | D-05's accepted archival landmine (judgment b) | Archiving FEAT-44's evidence file reddens every `run-unit-tests.sh` invocation repo-wide until a backend-dev/dev-ops edit, though the archiver need not hold that grant |
| 3 | info | SC-06 exact-equality (judgment a) | None — verified correct and appropriately scoped, recorded for the record |
| 4 | info | `harness.json` detect residual (judgment c) | None gating — disclosed, measured, empty today; flagged as an open question for explicit operator awareness |

No must_fix. `severity_max` is `med` (Finding 2), which is a disclosure/visibility flag on an
already-accepted decision, not a broken plan mechanism — I do not read this plan-panel role's gate
as failing on it, since D-05 is a decision correctly routed through `plan.yaml`'s `decisions:`
block for operator sign-off, not a defect I found in the plan's construction. Recommend `PASS`.
