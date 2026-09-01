# QA Gate — FEAT-51 — 2026-09-01 run 03

**VERDICT: FAIL.** `run-unit-tests.sh --kind integration` exits **1** with **9** `^FAIL ` lines at
this diff's HEAD (`6db25ba2`). Unit kind is clean. Root causes below are both attributable to files
this diff touched; neither is a misconfiguration (both are named tests with real assertion diffs).

## Required kinds (floor, re-derived from plan.yaml against harness.json's test_matrix)

| task | change_type | required |
|---|---|---|
| T-01 | api | unit (always). `when: integration if touches_db_or_external` — diff of `validate-digest.py` adds no DB/socket/subprocess/HTTP call, predicate resolves **false**, integration not owed via this clause. `test-validate-digest.py` still lives in `INTEGRATION_SCRIPTS`/`test_kinds.integration.detect` per D-09 ("enforcement-layer test files land in the existing integration array regardless of change_type; unit floor satisfied by the unchanged unit array running green") — floor is met, not violated. |
| T-02 | logic | unit |
| T-03 | cross_module | unit + integration |
| T-04 | feature | unit + integration |
| T-05 | docs | none owed |
| T-06 | docs | none owed |
| T-07 | cross_module | unit + integration |
| T-08 | scaffolding | none owed |
| T-10 | cross_module | unit + integration |

**Floor = {unit, integration}.** Both active in `test_kinds`.

## Kind resolution

| kind | cmd | exit | `^FAIL ` | `^ok /^PASS ` | state |
|---|---|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | **0** | 948 ok / 519 PASS | **satisfied** |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | **1** | **9** | 1351 ok / 741 PASS | **FAIL** |

Full logs: `/tmp/qa51/unit.log` (1532 lines), `/tmp/qa51/integration.log` (2339 lines). Captured `$?`
into a variable immediately after each run (not read from a tail — the dispatch's warned hazard is
real: `unit.log:1501` reads `28/28 checks passed.` but the file continues to line 1532).

`--check-kinds`: **exit 0** — "the script arrays and test_kinds.integration.detect agree."
`test-quarantine.py` registration confirmed in **both** surfaces with the `.claude/skills/harness/bin/`
prefix `run-unit-tests.sh:115` actually uses: `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:31`) and
`test_kinds.integration.detect` (`.harness/harness.json`, confirmed via direct parse). Note:
`PREFIX` at `run-unit-tests.sh:115` is literally `.claude/skills/harness/bin/`, not `.agents/...` as
T-04's own `intent:` claimed — T-04's receipt (`receipt-harness-dev-ops-T-04-c1.md`) already caught
and corrected this; re-confirmed here independently, not a new finding.

## Integration FAIL — two distinct root causes, both real

**A (8 of 9 FAILs) — `.harness/team-config.yaml` (T-03), self-heals at merge, not a code defect.**
`check-plan-routes.py`'s `_manifest_deviation` (:102-140) compares this worktree's
`.harness/team-config.yaml` against the **owner (main) checkout's** copy — `harness_boundary`
resolves the "owner" root for governed manifests, not the worktree. T-03 added one line to the
worktree's copy (`- { path: .harness/*/features/*/quarantine/** }`, confirmed via
`diff .harness/team-config.yaml <worktree>/.harness/team-config.yaml`); main's copy is byte-identical
to the base sha `0bc57c88` (confirmed, zero drift). Six `test-check-plan-routes.py` cases
(`case_04_all_granted_exits_0`, `case_05_ungranted_declared_main_session_exits_0`,
`case_15_deviation_plan_still_exits_0`, `case_17_midpattern_wildcard_grant_exits_0`,
`case_19d_explicit_path_unaffected_by_the_root_guard`, `case_19d2_explicit_path_with_no_tasks_still_exits_0`)
run against the **live** manifest pair and see the DEVIATION every unmerged team-config.yaml edit
produces — the file's own doc-comment says as much ("Any feature that so much as re-words a comment
here inherited that"). `_manifest_deviation`'s fast path returns `None` on byte-equal content
(:128-130), so this clears once the branch merges and main's copy matches. Not a defect in T-03's
logic; it is the true, reproducible state of the standing gate command **today**, in this worktree,
and the gate cannot be told to look past it.

**B (1 of 9 FAILs) — genuine, unresolved regression. Owner: T-03 (`.harness/team-config.yaml`), fix
lands in `test-harness-yaml.py` (not in T-03's declared files).**
`test-harness-yaml.py:183 test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` reads
the **worktree's own** live manifest (not the owner-root comparison A uses) and asserts
`hy.manifest_domains(MANIFEST_PATH, agent)` against a hardcoded `COLLECT_FIXTURE`. For
`harness-backend-dev` the assertion now fails:
```
got:      ['.harness/*/features/*/quarantine/**', 'package.json', ...]
expected: [                                        'package.json', ...]
```
T-03's new shared glob is real, live, additive content in the manifest `manifest_domains()` correctly
walks — `COLLECT_FIXTURE` in `test-harness-yaml.py` was never updated to expect it. This file is not
in T-03's `files:` list and was not exercised by T-03's own `verify:` (which only runs
`test-check-domain.py`). **This is a genuine gap the broader integration command catches that the
task-scoped verify could not** — exactly the class of finding this gate exists for. Requires an
actual fix (update `COLLECT_FIXTURE`), not a merge.

## Three attention items

**1. `quarantine.py adopt` → `plan-merge.py` delegation: real subprocess, not a stand-in.**
`test-quarantine.py:32` drives `quarantine.py` itself via `subprocess.run([sys.executable, CLI, ...])`
(real CLI, real process). `quarantine.py:124-130` (`adopt`, plan.yaml branch) itself
`subprocess.run`s the real `plan-merge.py apply` — no monkeypatch, no stub. `test-quarantine.py:131`
("case1: canonical carries all fifteen task ids") asserts the merged id set from that real delegation.
Verified green in the integration run (`case1...` passes). **Genuinely end-to-end.**

**2. `orphan_write` consulted by both gates: each drives its own gate end-to-end with a real registry
fixture, not the predicate in isolation.** `test-check-domain.py:149` `fire()` and
`test-plan-sign-gate.py:462` `qgate()` both `subprocess.run` the real hook/gate script with a payload
built against a throwaway root whose `.harness/.inflight-claims.json` is populated via
`inflight_registry.claim_with_receipt` (real registry writes, not mocked). Confirmed passing:
`an orphan canonical write is quarantined` (check-domain.sh) and
`an orphan agent plan-merge apply on plan.yaml is quarantined` (plan-sign-gate.py). T-10 additionally
covers the **union** the two authors could not see individually — both surfaces' fail-open (raising
call, unimportable module) plus a negative control per surface, all 6 confirmed `ok` in the run
(lines 1094-1096, 2295-2297 of the integration log).

**3. T-05's `BOUND_SITES` reduction — measured, not a silent coverage drop.**
Before: `BOUND_SITES = [DECISIONS_PATH, INFLIGHT_REGISTRY_PATH]` — 2 sites, 4 `ONCE_RE` occurrences
total (3 in `DECISIONS.md`, 1 in `inflight_registry.py`), 6 assertions (2 `case_floor_*` + 4
`case_occurrence_*`), all passing at `0bc57c88`. After: `BOUND_SITES = [DECISIONS_PATH]` — 1 site, 3
occurrences (all in `DECISIONS.md`), 4 assertions, all passing (`python3 test-lead-stop-and-wake.py`
run directly: `PASS case_floor_DECISIONS.md`, 3 `PASS case_occurrence_DECISIONS.md_*`). Confirmed
`inflight_registry.py`'s post-T-02 source contains **zero** occurrences of the once-only phrase family
(grepped directly — T-02 replaced the line entirely, not just qualified it), so leaving the site in
`BOUND_SITES` would have produced a false `case_floor` failure on legitimately-changed content, not a
real gap. **The narrow claim ("once-only phrasing carries a per-stop-sequence qualifier") is not
under-asserted anywhere it still applies.**

However: **a related, unguarded staleness was found and is NOT caught by any test in this diff.**
`DECISIONS.md` DEC-199 (untouched by this diff — confirmed via `git diff` on that file) still states,
present tense: *"Only the dispatch cause of issue #551 is closed... [the two reporting consequences]
are NOT closed"* and *"`inflight_registry.py`'s refusal message states the same [once-only] bound."*
Both clauses are now false: T-01/T-02 close exactly those reporting consequences via the SUSPENDED
mechanism, and `inflight_registry.py`'s refusal message no longer states any once-only bound (T-02
replaced it outright — confirmed by direct read of `children_refusal_lines`, :568-583). No task in
this plan amends DEC-199, and `bound_site_cases`' qualifier check only asserts DEC-199's own sentence
is internally self-qualified (it is, trivially, since it's unedited) — it asserts nothing about
whether DEC-199's claim is still true of current source. This is a **coverage gap**, not something
`test-lead-stop-and-wake.py` was ever built to catch, and not attributable as a regression to any one
task — flagged for `pm`'s goal-check / a documentation follow-up, not gating this build's kind
resolution.

## Test-first audit, per task

| task | lane | evidence |
|---|---|---|
| T-01 | main-session-direct | commit `741804ad`, no message body, no receipt (lane convention). Checked STATE.md and both persisted observations logs (`harness-eng-lead.md`, `harness-pm.md`) for a recorded RED — **none found**. No evidence recorded, not distinguishable from "not done first" by anything I can read. |
| T-02 | main-session-direct | commit `af5c7136`, same — **no RED evidence recorded** in any artifact I can reach. |
| T-03 | main-session-direct | commit `94f7f2eb`, same — **no RED evidence recorded**. |
| T-04 | team / harness-dev-ops | **RED recorded**: `receipt-harness-dev-ops-T-04-c1.md` §"Step 1 — RED, recorded verbatim" shows 11 genuine failing assertions against the absent `quarantine.py`, then full 25/25 GREEN after. Test-first confirmed. |
| T-05 | main-session-direct | commit `f260b5fb`, no receipt (lane convention) — **no RED evidence recorded**, though plan intent explicitly demanded "record the failing exit code" against the pre-change file. |
| T-06 | team / harness-documentor | `receipt-harness-documentor-T-06-c1.md` states "Baseline before any edit: clause 1 matched 0 times, clause 3 matched 0 times... The task was not pre-landed" — a baseline record, weaker than T-04's full RED transcript but a genuine before/after measurement. Test-first evidenced. |
| T-07 | main-session-direct | commit `72ec341d` — **no RED evidence recorded**. |
| T-08 | team / harness-dev-ops | **RED recorded** via 4 mutation probes (A-D) in `receipt-harness-dev-ops-T-08-c1.md`, each showing the targeted clause going red and unrelated clauses staying green — the strongest evidence of the nine tasks. |
| T-10 | main-session-direct | commit `a033793a` — plan intent explicitly demanded "PROVE THE GROUP DISCRIMINATES and record the failing output," and STATE.md documents the group as landed with `verify:` passing, but **no RED/discrimination transcript is recorded** in any artifact I can reach. |

**Six of nine tasks (T-01, T-02, T-03, T-05, T-07, T-10) carry no discoverable RED evidence** — all
`main-session-direct`, which write no receipt by lane convention, and each landed as a single commit
(test+production together), so commit order cannot show test-before-code either. This is a **finding**
for the routing tier, not something I can resolve from the repository: main-session-direct execution
leaves no artifact trail this gate can audit, structurally, regardless of whether the discipline was
actually followed.

## SC evidence

Not in this dispatch's scope — no `plan.yaml` `verify: automated` SC list was handed to me to map;
`pm`'s goal-check is a separate dispatch. Flagging only what I directly measured against the matrix
and the diff.

## Must-fix, routed by task/file

1. **T-03 / `test-harness-yaml.py` (`COLLECT_FIXTURE`)** — update the `harness-backend-dev` expected
   `shared` list to include `.harness/*/features/*/quarantine/**`. Real, standing regression;
   independent of merge state.
2. **T-03 / `.harness/team-config.yaml`** — the 8-case DEVIATION failure family is expected to clear
   on merge to main; no action needed inside this worktree, but do not treat the integration suite as
   green here until it is re-run post-merge (or against main directly).
3. **Routing tier decision needed**: six main-session-direct tasks carry no RED evidence artifact.
   Not a code defect, but a process gap this qa segment cannot resolve or waive on its own.
