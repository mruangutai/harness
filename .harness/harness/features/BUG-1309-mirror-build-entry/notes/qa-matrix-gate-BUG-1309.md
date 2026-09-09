# QA test-matrix gate — BUG-1309-mirror-build-entry

## Verdict: FAIL

Three independent reasons, any one of which fails the matrix on its own:

1. **A real regression in the standing suite.** `tests/integration/test-hooks-install.py`
   case `case_sc14_end_to_end_and_red_proof`, sub-case `(e-green) SC-14: the terminal
   feature's worktree is gone after a real merge...` is RED. Command:
   `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind
   integration` → exit 1; this is the only `FAIL` line in a 3941-line run. Root cause traced
   to source, not inferred: T-07's diff to `post-merge-sweep.sh` (git diff shown below)
   retains a merged worktree whenever `github.sync` is true and `feature.json` lacks
   `github.build_entry`, unless the feature directory is in the frozen
   `BUILD_ENTRY_ERA_EXEMPT` set. The pre-existing fixture in `test-hooks-install.py`
   commits a feature under the synthetic name `FEAT-90-e-green-thing` with
   `github={"milestone": 9001}` and no `build_entry`, against an origin whose
   `harness.json` has `github.sync: true` — exactly the new "no receipt" branch, and the
   synthetic name can never be era-exempt (that set is frozen from real feature directories
   only). The sweep now prints `post-merge-sweep: SKIP removal of ... — FEAT-90-e-green-thing
   records github.build_entry=absent` and returns without removing, so the test's
   `not os.path.isdir(dest)` assertion fails.
   - **Owning task: T-07.** **Fault: COVERAGE, not code.** `post-merge-sweep.sh` is doing
     exactly what the signed D-08 policy requires — an already-merged, sync-enabled feature
     with no Build-entry receipt is supposed to be retained. The fixture is what's stale: it
     was written before `build_entry` existed and jumps straight to a `Done`-station merge
     without ever simulating a completed Build entry (e.g. via the fake-`gh` stub the file
     already sets up). It needs updating to record `build_entry: "opened"` (or route through
     the fake-gh open flow) before the merge, so SC-14's green case still tests what it was
     meant to test. This file is not in any BUG-1309 task's declared `files:` list — T-07
     changed `post-merge-sweep.sh` without re-running the fuller integration bucket, which is
     exactly how this leaked through (T-07's own `verify:` only runs
     `test-post-merge-sweep.py`).

2. **`feature`'s unconditional `unit` requirement is unmet for T-03.** `test_matrix.feature.always`
   is `[unit, integration]`, unconditional — no predicate gates it. T-05 satisfies both
   (`integration`: `tests/integration/test-merge-gate.py`, 14 named cases, all `ok`;
   `unit`: `tests/unit/omp-hooks.test.ts` changed +3 lines, run via `tests/unit/test-omp-hooks.py`,
   56/56 pass — confirmed part of the diff). **T-03 (`gh-sync.py recover-terminal`) satisfies
   only `integration`** (`tests/integration/test-gh-sync.py`, 7 named T-03 cases, all `ok`) —
   no unit-kind file (`tests/unit/test-*.py`) was added or changed for T-03 at all.
   - **Owning task: T-03. Fault: COVERAGE** — the feature (recover-terminal's four-adoption-state
     logic) is correctly implemented and well covered at the integration/subprocess level; the
     unconditional unit floor is simply unaddressed.

3. **`bugfix`'s conditional `unit` requirement is unmet for T-02, T-04, T-06, T-07.**
   `test_matrix.bugfix.when` fires `unit` on `touches_runtime_code` (DEC-217: "modifies at
   least one file that is not under `tests/**`, is not `*.md`, and is not under `.harness/`").
   True for all four: `gh-sync.py` (T-02, T-04), `check-state.sh` + `feature_schema.py` (T-06),
   `post-merge-sweep.sh` (T-07). No `tests/unit/test-*.py` file was added or changed by any of
   the four; every one of their tests lives in `tests/integration/`. `fix_confined_to_tests_and_
   contract_docs` is false for all four (real runtime code changed), so `integration` is not
   independently required by that leg — though it is present anyway (all named cases for T-02,
   T-04, T-06, T-07 pass; see below). `match_bug_class`/`__bug_class__` never fires — confirmed
   unresolvable placeholder (repo Expertise G-08: no bug-class taxonomy entry exists for any
   diff yet), treated as not-applicable.
   - **I flag this with real but not total confidence**, because DEC-217's own "Over" clause
     explicitly rejects "copying an already mutation-proven integration contract guard into
     `tests/unit/**` solely to satisfy a directory label," and this repository's own established
     precedent for the *identical* shape of change — `feature_schema.RUNS_AGENT_EXEMPT` and
     BUG-1071's INV-32 era guard, both cited by this plan as the pattern T-06 follows — carry
     **zero** `tests/unit/` coverage of their own, tested entirely from `tests/integration/`.
     Taken literally, the same predicate would already have been unsatisfiable for BUG-1071.
     I resolve this as **MISSING** per the floor's literal text (repo Expertise P-04: "a firing
     predicate is floor, not optional"), but this specific tension — whether `touches_runtime_
     code → unit` was ever meant to bind CLI-shell-script bugfixes tested exclusively via
     subprocess harnesses under `tests/integration/` — is itself worth a decision, not a
     silent normalize-away by me.
   - **Owning tasks: T-02, T-04, T-06, T-07 collectively. Fault: ambiguous between COVERAGE
     (add unit tests) and a matrix-predicate gap (amend DEC-217 with a carve-out) — needs a
     call above QA.**

## Per-cell table

| change kind | task(s) | required kind | predicate evaluation | covering file:case | state |
|---|---|---|---|---|---|
| config | T-01 | integration (when `touches_config_shape`) | fires: adds a new enum-typed key to `feature-schema.json`, a schema the `validate-feature-json.py` gate reads — a structural/type addition | `tests/integration/test-validate-feature-json.py::accepted_github_build_entry_{opened,recovery-required,not-applicable,recovered-terminal}`, `rejected_github_build_entry_illegal_value_*`, `rejected_github_build_entry_hyphen_misspelling`, `accepted_github_block_without_build_entry` (8 cases, all `PASS`) | **satisfied** |
| bugfix | T-02,T-04,T-06,T-07 | unit (when `touches_runtime_code`) | fires: all four touch non-test/non-md/non-`.harness` code | none | **MISSING** (see §3 above) |
| bugfix | T-02,T-04,T-06,T-07 | integration (when `fix_confined_to_tests_and_contract_docs`) | does not fire: real runtime code changed | n/a (present anyway, see below) | not required; present as an add-on |
| bugfix | T-02,T-04,T-06,T-07 | `__bug_class__` (when `match_bug_class`) | never fires: unresolvable placeholder, no taxonomy entry exists (repo Expertise G-08) | — | not applicable |
| feature | T-03 | unit + integration (`always`, unconditional) | both fire unconditionally | integration: `tests/integration/test-gh-sync.py::"T-03 ..."` (7 cases, all `ok`). unit: **none** | integration **satisfied**; unit **MISSING** (see §2) |
| feature | T-05 | unit + integration (`always`, unconditional) | both fire unconditionally | integration: `tests/integration/test-merge-gate.py` (14 named cases, all `ok`) + `python3 .../merge-settings.py --check` (9 prerequisites present). unit: `tests/unit/test-omp-hooks.py` running `tests/unit/omp-hooks.test.ts` (changed, 56/56 `bun test` pass) | **satisfied** |
| docs | T-08, T-09 | none (`always: []`) | n/a | T-09's own verify re-run: `gen-decisions-index.py --stdout \| diff` clean, `DEC-220` present, `test-check-decision-anchors.py` 8/8 `ok`, `VERIFY-PASS`. T-08 verify (`grep -q "Build entry" ...`) not independently re-run but is a trivial string-presence check already gated at task verify | **satisfied** (no floor) |

## Every test run, named, with counts

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` → **exit 0**, pool: 8 workers, 31 files, all `PASS`, including `test-omp-hooks.py` (56 pass / 0 fail via `bun test`) and `test-config-shape-matrix.py` (19/19, unaffected by this feature's schema change — it self-tests the harness.json matrix declaration, not per-feature schemas).
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` → **exit 1**, pool: 8 workers, 50 files, wall 74.9s. Exactly one `FAIL`: `test-hooks-install.py` (see §1). Every other file `PASS`, including the full set of named contract cases:
  - `test-validate-feature-json.py`: T-01's 8 new cases, `ALL PASS`.
  - `test-gh-sync.py`: 316 `ok` / 0 `FAIL`, all 8 T-02 cases, all 7 T-03 cases, all 5 T-04 cases present as `ok`.
  - `test-merge-gate.py`: `exit 0`, all 14 T-05 cases `ok`, `ALL PASSED`.
  - `test-check-state.py`: all 9 T-06 cases (`INV-37`/`recovery_command_for`) present as `ok -`.
  - `test-post-merge-sweep.py`: `exit 0`, all 8 T-07 cases `PASS:`.
  - `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && grep -q "DEC-220" ... && python3 tests/integration/test-check-decision-anchors.py` → `VERIFY-PASS` (T-09, re-run independently).

No new test was written by me — the matrix's per-task presence requirements are otherwise met by tests already in the diff; the gap is absence (§1–§3), not a kind I can fabricate coverage for.

## Case non-vacuity — spot-checked, not exhaustive

I did not re-run mutation proofs for all ~40 new named cases; volume made that impractical inside
this gate. I relied on: (a) the plan's own intent text, which repeatedly specifies exact-value
assertions designed against known vacuity traps ("assert absence of the key, not a falsy value",
"count the create lines... == 0, never a substring absence", "assert both... because the first
alone passes on a message that merely omits the .py"); (b) backend-dev's T-02/T-03 receipts, which
show red-before-green per case and, for two strengthened T-03 assertions, an explicit non-vacuity
proof (`receipt-harness-backend-dev-T-03-c1.md`); (c) the live discovery in §1, which is itself a
mutation-style proof that T-07's retention code is load-bearing (a real, previously-green fixture
went red the moment the guarding logic engaged). I did not independently re-derive red states for
T-04's or T-06's era-gate cases; those are **reasoned**, not measured, from the code (confirmed
`BUILD_ENTRY_ERA_EXEMPT` and `recovery_command_for` exist exactly as specified,
`feature_schema.py:226-328`) plus their exact-string/exact-exit-code assertions passing.

## Test-first audit, per task

- **T-01**: COMPLIANT. Receipt shows 6 of 8 new cases genuinely RED before the schema edit
  (`FAIL accepted_github_build_entry_opened` etc.), GREEN after; the other 2 pre-edit-green cases
  are explicitly justified as non-new-schema-dependent, not silently accepted.
- **T-02**: COMPLIANT, with an honest partial disclosure. 5 of 8 cases genuinely RED before the
  production edit. 3 cases (`unpinned repo records nothing`, `partial remote write records
  nothing`, `opened never downgrades`, `contract error records nothing` — receipt lists these as
  "GREEN pre-change, honestly") were pre-existing-green for a **vacuous** reason (nothing wrote the
  field yet, so absence held by accident) and the receipt states this plainly rather than hiding
  it, then explains why each now holds by construction post-change. This is very likely the
  dispatch's "one whose red-before-green was a partial red reported as such."
  I could not find a second task with a fully post-hoc test order — the other receipted tasks
  (T-01, T-03) show clean red-before-green; T-03's cycle 1 receipt goes further, adding explicit
  mutant-discrimination proofs for two strengthened assertions.
- **T-03**: COMPLIANT (see above); independently re-verified by dev-ops
  (`receipt-harness-dev-ops-T-03-c1.md`, byte-identical verify string, 316 ok / 0 FAIL,
  all 7 cases present).
- **T-04, T-05, T-06, T-07, T-08**: **could not establish.** These are `execution_mode:
  main-session-direct` (DEC-174 enforcement carve-out); the main session does not write
  receipts, and I found no observations-log entry from any team member establishing red-before-
  green for these five tasks specifically. All of their named `verify:` cases pass at HEAD, which
  proves presence and passing, not ordering. I am not upgrading this silence into compliance.
- **T-09**: no red/green cycle applicable (pure documentation append); receipt shows the intent's
  factual claims were checked against landed code (`gh-sync.py:625-626`, `:1357-1389`, `:289`,
  `:1277-1323`; `check-state.sh:1983-2018`; `.claude/settings.json:48`) before being written, and
  one factual correction was made and disclosed (the era-exempt set bounds three call sites, not
  the one the intent named).

## A file changed with no task attribution (not a QA-owned defect, flagging for the record)

`.harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml` (`status: review` →
`status: done`) is in the merge-base..HEAD diff but is not in any BUG-1309 task's `files:` list.
Traced to commit `4e8f5ea1` ("FEAT-55-issue-types-created-work: station done at ship"), which is on
this branch's own line (not an ancestor of `merge-base`) — i.e. an unrelated feature's own ship
commit landed inside the BUG-1309 branch history. `plan.yaml`'s own `lanes.resolved_at` is pinned
to this exact same commit hash, so the lane resolution itself is anchored past this contamination
point. This is a branch-hygiene question for the orchestrator, not a test-matrix defect; I did not
attempt to unwind it.

## Coverage gaps (Phase-1 expectations against what exists)

Reading BRIEF.md/plan.yaml cold, before touching code, I expected test coverage for: the five
`build_entry` states and their schema validation (found, T-01); Build refusing on an absent
receipt with FEAT-*/BUG-* parity (found, T-04); the merge gate's allow/deny matrix (found, T-05);
INV-37's terminal-with-no-receipt detection (found, T-06); worktree retention keyed on the
recorded value (found, T-07 — and per §1, retention IS wired in and takes effect, just not
reconciled against a sibling fixture); `recover-terminal`'s four adoption states (found, T-03).
The one gap Phase 1 would not have predicted, because it's a cross-cutting side effect rather than
a stated requirement, is §1's fixture staleness.

## SC evidence pointers (for pm's goal-check)

- Build-entry states + schema (REQ-03/04/05): `test-validate-feature-json.py::accepted_github_
  build_entry_*` / `rejected_github_build_entry_*`.
- REQ-01 (Build refuses absent, FEAT/BUG parity): `test-gh-sync.py::"T-04 non-era absent refuses"`
  + `"T-04 BUG-named non-era absent refuses"` (the pair).
- REQ-02/09 (recover-terminal, ship message): `test-gh-sync.py::"T-03 recover-terminal creates
  milestone and parent only"`, `"T-03 ship names recover-terminal"`.
- REQ-07 (merge refused while recovery owed): `test-merge-gate.py::"T-05 recovery-required
  denies"`.
- REQ-10 (INV-37): `test-check-state.py::"T-06 INV-37 fires at a done station with no task
  statuses"` + `"T-06 INV-37 silent on an era-exempt feature"` (the pair).

## files_touched
None — read-only gate. I wrote no new test file: the matrix's presence requirements are met where
they are met by tests already in the diff, and the gaps found (§1–§3) are either not mine to fix
(stale fixture in another task's non-owned file, §1) or a floor whose remedy (add unit tests, or
amend DEC-217) is a decision for the owning tasks / product-lead, not a QA-authored patch.
