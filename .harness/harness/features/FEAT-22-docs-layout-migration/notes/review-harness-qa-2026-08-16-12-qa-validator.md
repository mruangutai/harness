# QA gate — FEAT-22 · S-01-qa-matrix · pinned e26e628

**VERDICT: PASS.** All matrix-floor and SC-evidence kinds satisfied, both probes with reddening
proof, no defects found. No fix cycle spent.

## 0. Range confirmation

`git diff --name-only 0f12f14..e26e628 | wc -l` = **32**, `git rev-list --count 0f12f14..e26e628` =
**5**. Matches the claimed range exactly — no correction needed.

## 1. Matrix floor — re-derived, dispatch's correction confirmed correct

Grepped `plan.yaml` directly: T-01, T-06–T-11 (7 tasks) = `docs`; T-02 = `config`; **T-03, T-04, T-05
= `logic`**. `harness.json` `test_matrix.logic.always = ["unit"]`. So **unit is floor-mandatory**,
bound to 3/11 tasks (27%) — the dispatch's correction of the upstream "all docs, empty floor" claim
is right, confirmed independently from the plan, not just accepted.

`integration` is not floor-required by the matrix but is separately demanded by SC-05/06/08's own
`evidence: integration` — ran regardless, per the "floor is a floor, never a ceiling" rule.

## 2. Kinds run — exact configured `cmd`, both exit 0

| kind | cmd | exit | scripts | result |
|---|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | **0** | 15/15 `UNIT_SCRIPTS` | all PASS, 707 `ok` sub-assertions incl. `test-layout-migration.py` case 21 |
| integration | `run-unit-tests.sh --kind integration` | **0** | 12/12 `INTEGRATION_SCRIPTS` | all PASS, incl. `test-check-domain.py`, `test-gen-decisions-index.py` |

Confirmed BRIEF's claim that `run-unit-tests.sh:17-18`'s explicit arrays — not `harness.json`'s
`detect` glob — decide execution: `test-check-domain.py` and `test-gen-decisions-index.py` both
match the `unit` glob (`test-*.py`) but only run under `--kind integration`, because they're listed
in `INTEGRATION_SCRIPTS`, not `UNIT_SCRIPTS` (read directly at `run-unit-tests.sh:17-18`).

`component`, `ui`, `eval`, `typecheck` — all `cmd: null`/`status: unresolved`, none covers this
diff's surface (no UI, no LLM behaviour, no TypeScript). **Not applicable**, correctly per BRIEF's
own "Verification gaps" section.

**Discovery counts, not just exit codes:** unit ran 707 named sub-checks across 15 scripts (not a
vacuous 0-collected pass); integration ran 652+ named sub-checks across 12 scripts including a
106/106 explicit tally in `test-factory-integration.py`.

## 3. Three probes

**Probe 1 (`test-no-distribution.py` case4).**
- (a) files walked under the absence-assertion loop (`.harness/harness/docs` + `docs/`, both real
  dirs at HEAD): **8 files**, non-empty — instrumented directly with the same walk logic, not
  inferred from the test's own report.
- (b) `saw_decisions` control fires when perturbed: ran `case4()` in-process with the `endswith
  ("DECISIONS.md")` match swapped to a string that never matches (in-memory `exec`, never written to
  disk). Result: `FAIL case4_control_docs_walk_reached_decisions the walk never visited
  DECISIONS.md` — reddens correctly. Un-perturbed run passes all 8 assertions in case4, including
  the control. No source file was touched — `git status --porcelain` on
  `test-no-distribution.py` confirms clean.

**Probe 2 (`test-gen-decisions-index.py`, pre-existing asymmetry — not re-litigated).**
`DOCS_DIR`/`REAL_INDEX` now derive to `.harness/harness/docs/DECISIONS-INDEX.md`, which **exists**
post-move. So at HEAD, **neither** the `:361-363` FAIL branch nor the `:399-401` SKIP branch fires —
both hit the real-comparison path (`os.path.isfile(REAL_INDEX)` is `True`), and both ran as `ok` in
the live suite. T-04/`0140dce`'s "derive five sites from one local `DOCS_DIR`" change did not flip
which branch fires; it kept both on the substantive path, which is the outcome that matters.

**Probe 3 (em-dash literals, by polarity).**
Detector's `render()` emits `"%s: %s — evidence %s"` (`layout_migration.py`, confirmed via raw
byte read — genuine U+2014, not ASCII hyphen). Grepped every changed test/shell file in the diff for
negated assertions on `CLEAN`/`evidence`/dash literals:
- `test-layout-migration.py:399` — `"docs: CLEAN — evidence migrated" in docs_line` is a **positive**
  containment assertion (case 21) — self-catching, correct em-dash confirmed by byte inspection.
- `test-gen-decisions-index.py:721` — `after == before or "# DECISIONS — index" not in after` reads
  as `not in` but is semantically a **presence requirement** (FAILs when the marker is absent, not
  when present) — not a silent-miss risk despite the syntax.
- No other changed file in the diff asserts an em-dash-bearing literal under true negation/absence
  polarity. **No silent-miss risk found.**

## 4. Enforcement-layer files (DEC-174) — report only, no fix drafted

`check-domain.sh` and `check-state.sh` are both in the diff, each a single-line diagnostic-prose edit
(`docs/harness/DECISIONS.md` → `.harness/harness/docs/DECISIONS.md`, lines 953/676 named in the
plan). Grepped both files post-change for any remaining `docs/harness` mention outside the migrated
form — **none found**. No defect, nothing to route back.

## SC evidence

| SC | test | note |
|---|---|---|
| SC-01 | `git ls-files docs/harness/*` (0) + `git ls-files .harness/harness/docs/*` (5, exact names) | inspection, reproduced |
| SC-02 | `test-layout-migration.py::case 21` (`:398-399`) | unit |
| SC-03 | inspection — before/after capture, not re-derivable by qa | see gap below |
| SC-04 | `git show e6e74c8 --name-status`: 5× `R09x/R100` renames, one commit | inspection, reproduced |
| SC-05 | `test-check-domain.py:795-802` (live-tree `--resolve` case) | integration |
| SC-06 | `test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration` + header grep confirming `.harness/harness/docs/DECISIONS.md` literal at `gen-decisions-index.py:76` | integration |
| SC-07 | `run-unit-tests.sh --kind unit`, exit 0 | unit |
| SC-08 | `run-unit-tests.sh --kind integration`, exit 0 | integration |
| SC-09 | `test-layout-migration.py::case 1` — exit-0 half only, see finding below | unit (partial) |
| SC-10, SC-11, SC-12 | inspection-only per BRIEF; not qa's to verify | see gap below |

## Coverage gaps (Phase-1-derived, not closed)

- SC-03, SC-10, SC-11, SC-12 are inspection-only per the BRIEF's own "Verification gaps" section —
  no test kind in this repo answers them, and qa did not attempt to. This is not a suite gap; it is
  the six inspection-only SCs the BRIEF names up front (SC-01, 03, 04, 10, 11, 12). SC-01 and SC-04
  I additionally reproduced by direct inspection above (git ls-files / git show) since the commands
  are cheap; SC-03, 10, 11, 12 are prose/before-after judgements this gate cannot re-observe and are
  pm's to collect from the artifact, not qa's to test.

## Findings

**SC-09, `evidence: unit` — one literal not covered on the unit side (non-blocking).** SC-09 reads
"the checker exits 0 **and** reports a non-zero doc-root count." `test-layout-migration.py::case 1`
(`:129-134`) regex-captures three groups — feature-dir count (group 1), **doc-root count (group
2)**, reader-file count (group 3) — but only asserts `code == 0`, group(1) > 0, and group(3) > 0.
**Group(2), the doc-root count, is captured and never asserted anywhere in the unit suite** (grepped
`doc.root`/`doc_root` across the file; no other case names it). So:
- exit-0 is pinned by unit (`case 1`, `case 21`).
- non-zero doc-root evidence is *entailed*, not *literally asserted*, on the unit side: `case 21`
  requires `docs: CLEAN — evidence migrated`, and cases 11/16 prove CLEAN-with-migrated-evidence
  cannot fire on zero evidence (that path is CANNOT_VERIFY instead) — so the suite cannot currently
  go green with a zero doc-root count. But there is no assertion naming the count directly.
- The literal doc-root-count assertion SC-09 describes lives only in `.github/workflows/tests.yml:
  219-230` (CI Layout gate), per the BRIEF's own reading of that file — outside this gate's `unit`
  command.

This is intent-satisfied / text-unmet, not a suite defect — nothing here reddens, and adding one
`m.group(2) > 0` assertion to `case 1` is a one-line, low-risk addition, not worth the last fix
cycle for a non-blocking gap. Flagging by name per DEC-169 (an absence claim needs its own named
check) rather than closing it under the green run.

No blocking findings. No cycle spent.
