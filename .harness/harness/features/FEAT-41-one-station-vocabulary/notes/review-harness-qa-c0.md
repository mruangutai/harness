# QA gate — FEAT-41-one-station-vocabulary, review_sha 7c02ea4

BLUF: **FAIL.** Not because of this feature's own code — every T-09/T-08/T-14/T-03 case I audited
is solid, red-first, negative-controlled. It fails because SC-11 ("the whole suite is green") is
measured **false** at the pin: `run-unit-tests.sh --kind integration` exits **1**, reproducibly
(2/2), on a case in a file this feature never touches. Two real coverage gaps also confirmed in
the areas the build itself flagged thin (worktree-deletion fallback, plan-write splice guard).

## Baseline reproduction (exit codes, not grep)

| check | expected | observed |
|---|---|---|
| `run-unit-tests.sh --kind unit` | exit 0, 493 PASS, 0 FAIL | **matches**: exit 0, 493 PASS, 0 FAIL |
| `run-unit-tests.sh --kind integration` | exit 0, 797 PASS, 0 FAIL | **disagrees**: exit 1, 1 FAIL script (`test-bash-write-guard.py`), reproduced 2/2 full-suite runs |
| `check-state.sh` | exit 0, 0 VIOLATION, 0 tracebacks | **matches**: exit 0, 0 VIOLATION, 0 tracebacks (only pre-existing INV-23 notes for FEAT-05/FEAT-43, correctly out of scope) |

**F-1 (blocks ship as measured, HIGH, but not attributable to this diff).**
`test-bash-write-guard.py`'s `"ONE IMPLEMENTATION: mutating WORKTREES_SEGMENT flips BOTH routes
0 -> 2"` case (source line 524) fails deterministically inside the full `--kind integration` run
(`bash=0, write=0`, wanted `(2,2)`) but passes 4/4 when run standalone. Neither
`harness_boundary.py`, `bash-write-guard.sh`, nor `test-bash-write-guard.py` are touched by this
diff (`git diff --name-only base..review_sha` — confirmed absent); the test file's last edit
(`66e9a9d`) is an ancestor of `base`, i.e. pre-existing. `check-domain.sh`, which this feature
does touch, is one of the two routes this case exercises, but the untouched `bash-write-guard.sh`
route fails identically, pointing at shared/timing infrastructure (the file's own comment already
documents a `.pyc`-staleness hazard it tried to work around) rather than at FEAT-41's code. Still:
**SC-11 literally requires the whole suite green, and it is not, at this pin, as measured twice.**
Recommend: main session reproduces once more on a quiet machine before re-pinning; if it
reproduces there too, this is a standing defect in `test-bash-write-guard.py` to file separately,
not a FEAT-41 regression.

**Correction to dispatch framing (not a finding, informational):** no "per-task mutant table"
exists in `.harness/logs/2026-08-31.md` (grepped `mutant` — zero hits). The log is prose
observations; the test-first evidence (assertion counts, red-first proofs, negative-control
mutants) lives in the **commit messages**, exactly where item 3 of my dispatch also pointed.

## Test-matrix gate

Change types present (from `plan.yaml`): config, cross_module, api, docs, bugfix, logic — matches
dispatch. Resolved against `.harness/harness.json`'s matrix:

| kind | required by | state | evidence |
|---|---|---|---|
| unit | logic, api, cross_module, bugfix (`always`) | **satisfied** | `run-unit-tests.sh --kind unit`, active cmd, 493 PASS |
| integration | cross_module (`always`) | **satisfied for this diff's coverage** (named cases for T-03/T-08/T-09/T-14/T-16/T-17 all pass) but **suite: fail** overall — see F-1 | `run-unit-tests.sh --kind integration` |
| api's `integration` (`touches_db_or_external`) | not triggered — T-03 (plan-merge.py) touches no DB/external service | n/a | — |
| bugfix's `__bug_class__` (`match_bug_class`) | not triggered — no `bug_class` field on T-10/T-14 | n/a | — |
| component / ui / eval | not required (config/docs/scaffolding carry `always: []`; frontend/`ai_behavior` absent from this diff) | **not applicable** | confirmed by grep: zero files in the 163-file diff match the `component` (`*.spec.tsx`/`*.stories.tsx|ts`), `ui` (`tests/e2e/**`, `*.e2e.spec.ts`) or `eval` (`evals/**`) detect globs. BRIEF's claim holds — verified, not accepted on faith |
| typecheck | not in matrix, no `.ts`/`.tsx` in diff | not applicable | confirmed by grep |

`matrix_ok: true` — every required kind is present with an active, run, executed command; no
required kind carries a null `cmd`.

## Test-first audit (commit-message evidence, `base..review_sha`)

| task | change_type | commit | verdict |
|---|---|---|---|
| T-09 | config | `b72e93e` | **holds** — "21 assertions, all shown failing first"; `test-check-domain.py` bundled in the same commit |
| T-08 | config | `dedaadf` | **holds** — 16 assertions; explicit weak-red repair: two deliberately-wrong mutants scored (7 FAIL / 1 FAIL) to prove discrimination before trusting the real red |
| T-14 | bugfix | `a1dc932` | **holds** — "THE RED CAME FIRST AND IS RECORDED": (inv32.a) FAILS pre-fix, (b)(c)(d) demonstrated PASSING VACUOUSLY against an intentionally incomplete implementation, so the fixtures are shown to discriminate, not just to exist |
| T-03 | api | `b974830` | **holds** — "39 new assertions written failing first," exercised against the real 1500-line `plan.yaml`, not only fixtures |
| T-16 | logic | `9c95d85` | **partial / different shape** — this is fixture-debt repair (`test-gh-sync.py` 84→0), not new-test-before-new-code in the literal sense: the fixtures were already broken by T-01/T-02 four commits earlier (log lines 16-21) and sat red, undetected, because no task verify named `test-gh-sync.py`/`test-factory-integration.py`. T-16 does show real red-proof discipline within itself ("MY FIRST INVERSION ASSERTED THE WRONG MECHANISM... measured", "it took two attempts: the first passed T-99 ... so the case was green while proving nothing") but the framing is regression repair, not literal TDD for new behavior. Not a blocking finding — the session log already surfaces this window explicitly — but worth naming since the dispatch's "test-first for every new case" claim doesn't cleanly cover it. |

## Adequacy judged, not just green

- **check-domain.sh T-09 route denial (`test-check-domain.py:2529-2621`, `run_t09`).** Case 1
  (agent_type present) asserts denial + `set-task-station` name + **the reason** (`"one writer"`
  and `"validate"` both in stderr) + correct basename + absence of an unrelated routing sentence.
  Case 2 (agent=None, i.e. the main session) asserts **only the exit code**, not the reason text.
  **PB-07's disclosed gap is confirmed still real**: nothing asserts the reason is stated for the
  no-`agent_type` payload — not new, but independently verified rather than taken on faith.
- **plan-sign-gate.py (SC-07).** Fully satisfied: a payload WITH `agent_type` is denied (exit 2,
  case names literal `sign-approval` and states the rule), WITHOUT/empty `agent_type` is allowed,
  and the refusal names `awaiting_user` as the sanctioned route.
- **`worktree_terminal.py:classify` PyYAML-absent fallback — HIGH finding.** The pure text-scan
  helper `_scan_top_level_status` is thoroughly unit-tested
  (`test-worktree-terminal.py:868-916`, `case_plan_station_scan_without_pyyaml`). But the actual
  **wiring** in `_read_landed_plan_yaml` — `except Exception as exc: if
  type(exc).__name__ != "MissingDependency": ... else: doc = _scan_top_level_status(...)`
  (`worktree_terminal.py:213-221`) — has no deterministic, environment-independent test. The only
  thing that exercises it is `test-post-merge-sweep.py` invoking the real `-I`-isolated
  `post-merge-sweep.sh` as a subprocess, and that only actually raises `ImportError` **on this
  machine**, because PyYAML happens to live in user site-packages here (confirmed:
  `python3 -I -c "import yaml"` → `ModuleNotFoundError`). A machine with PyYAML in system or venv
  site-packages would silently skip this path with zero test failure to flag the gap. **Failure
  direction is the safe one on the observed code path**: an unrecognised exception type or a
  scan miss both resolve to `"unresolved"`/omitted-from-terminal, never to a wrongly-deleted
  worktree — but that safety is a property of the code, unverified by any test that forces the
  branch.
- **`plan-merge.py` `_verify_spliced` (STEP 9, `plan-merge.py:232`) — HIGH finding.** Added after
  a real production incident (a signed plan corrupted to 1541 unparseable lines, exit 0). Grep for
  `_verify_spliced` in `test-plan-merge.py` returns **zero** hits. The one related case,
  `case_proposal_indent_differs_from_base` (`test-plan-merge.py:145`), proves the **fix**
  (re-indentation) avoids ever needing the guard — it never constructs a splice that still
  produces unparseable output or a dropped/mismatched task id to prove the guard's own two
  refusal branches (`yaml.YAMLError` catch, and the `got != want` id-list mismatch that catches a
  silently dropped task) actually fire. If `_verify_spliced` were disabled or its comparison
  broken, no test would notice, and the exact incident it exists to prevent could recur.
- **`check-plan-routes.py` manifest deviation, byte→parsed.** Solid: `case_41_t09_a_ROUTE_
  difference_still_deviates` proves a real deviation still trips the parsed comparison, and
  `case_41_t09_comment_only_manifest_difference_is_NOT_a_deviation` proves the parsed form
  correctly stops flagging what the old byte comparison over-reported. No gap.
- **SC-09 / INV-26.** Confirmed directly: `git show 7c02ea4:...FEAT-40.../plan.yaml` carries
  top-level `status: done`; `check-state.sh`'s full run emits zero `INV-26` lines for any feature.
- **SC-01..SC-04, SC-14 — ran each criterion's own stated command verbatim:**
  - SC-01: no code in `.claude/skills/harness/bin` (or anywhere outside `__pycache__`/feature
    history docs) defines `_STATION_KEYS`. **Caveat (info, not blocking):** the literal wording
    "no longer exists anywhere in the tracked tree" is not literally true — three *other*,
    already-shipped features' notes/`plan.yaml` (FEAT-16, FEAT-24, FEAT-33) and this feature's own
    grilling note still name the retired constant as historical record, which is expected and
    correct; the criterion's clear intent (no live code definition) is met.
  - SC-02: the criterion's own grep, run verbatim, returns **0** lines (was 27 at `0d4845b`). Holds.
  - SC-03: the criterion's own anchored Python assertion exits 0. Holds.
  - SC-04: `set_station(` call sites outside tests, whole tree: exactly 4 (`board_lifecycle.py`
    ×2, `board-station.py` ×1, `gh-sync.py` ×1 — the policy site). Matches exactly. Holds.
  - SC-14: T-15's own verify script, run verbatim, exits 0 — three amendment markers present, one
    each in DEC-182/DEC-191/DEC-203, all three original clauses still standing. Holds.

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: Baseline does not reproduce — integration suite exits 1 (SC-11 unmet as measured), reproducibly, on a case in a file untouched by this diff; two HIGH coverage gaps confirmed in the areas the build flagged thin (worktree-deletion fallback wiring, plan-splice refusal guard).
  suite: fail
  failures: 1
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 493 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 797 }
    - { kind: component, state: not_applicable, cmd: null }
    - { kind: ui, state: not_applicable, cmd: null }
    - { kind: eval, state: not_applicable, cmd: null }
    - { kind: typecheck, state: not_applicable, cmd: null }
  coverage_gaps:
    - "worktree_terminal.py:_read_landed_plan_yaml's MissingDependency exception-dispatch wiring (lines ~213-221) has no deterministic unit test; only the pure _scan_top_level_status helper is unit-tested, and end-to-end coverage is incidental to this machine's PyYAML install location"
    - "plan-merge.py:_verify_spliced (STEP 9) has zero test forcing either refusal branch (unparseable reload, dropped/mismatched task id) — only the fix that avoids needing it is tested"
    - "T-09's own test-check-domain.py case 2 (no agent_type) asserts exit code only, not the denial's reason text — PB-07's disclosed gap, confirmed still real, not new"
  sc_evidence:
    - { id: SC-01, test: "manual grep, .claude/skills/harness/bin/**, verbatim per BRIEF.md:118-121 — 0 hits outside __pycache__/feature-history docs" }
    - { id: SC-02, test: "manual grep, BRIEF.md:124-125 verbatim — 0 lines (was 27 pre-feature)" }
    - { id: SC-03, test: "BRIEF.md:145 verbatim python3 -c assertion — exit 0" }
    - { id: SC-04, test: "manual grep set_station( outside tests — exactly 4 call sites" }
    - { id: SC-06, test: ".claude/skills/harness/bin/test-check-domain.py run_t09 cases T-09 5/6" }
    - { id: SC-07, test: ".claude/skills/harness/bin/test-plan-sign-gate.py" }
    - { id: SC-08, test: ".claude/skills/harness/bin/test-factory-integration.py, test-check-plan-routes.py (both PASS; not independently re-derived reader-count this pass)" }
    - { id: SC-09, test: "git show 7c02ea4:.../FEAT-40.../plan.yaml + check-state.sh full run — 0 INV-26 lines, verified directly" }
    - { id: SC-10, test: ".claude/skills/harness/bin/test-gh-sync.py (PASS; not independently re-derived this pass)" }
    - { id: SC-11, test: "run-unit-tests.sh both kinds + check-plan-routes.py — MEASURED FALSE: integration exits 1 (F-1)" }
    - { id: SC-13, test: ".claude/skills/harness/bin/test-check-state.py case_24/case_25 series (PASS; not independently re-derived this pass)" }
    - { id: SC-14, test: "T-15's own verify script (plan.yaml), run verbatim — exit 0" }
  open_questions:
    - { id: Q1, question: "Is test-bash-write-guard.py's ONE-IMPLEMENTATION mutation case (line 524) a known pre-existing flake, or does it need filing as a new defect? It reproduces 2/2 in the full suite and 0/4 standalone on this machine, in files this feature does not touch.", blocking: true }
    - { id: Q2, question: "Should worktree_terminal.py's MissingDependency wiring and plan-merge.py's _verify_spliced refusal branches get dedicated tests before ship, given both sit in the five areas the build itself flagged as thin?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-qa-c0.md
```
