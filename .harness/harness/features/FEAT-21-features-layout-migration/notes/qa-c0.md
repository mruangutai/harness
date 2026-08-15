# QA gate — FEAT-21 — cycle 0

Pin: HEAD = `5c39f8c1ea1da0b4ae9ffd5c8c5d035c1b5cd6a4`, matches `review_sha`. Range audited: `62fef85..5c39f8c`, measured via `git log --oneline` and `git diff --name-only` (not relayed from the dispatch, which undercounted). **Five commits, not the four the dispatch named**: `4b16f47` (sign), `5afa7e3` `[harness:t-01]`, `ea937b1` (bookkeeping), `d033b9d` `[harness:t-09]` cluster, plus `5c39f8c` itself — "FEAT-21 enters validation" — the harness bookkeeping commit that records entry into this gate and was not itself one of the four task-carrying commits the dispatch enumerated. This does not change SC-12: the plan's own SC-12 text counts *task* commits (T-01 alone, then the cluster), and both land exactly as required — `5afa7e3` carries T-01 alone, `d033b9d` carries T-02 through T-10. `git diff --name-only 62fef85..5c39f8c` also confirms zero `docs/harness/**` paths touched (SC-11).

## Verdict: PASS, with two findings routed up (neither a `must_fix`, both go to `open_questions` — see below)

- Suite: green at pin. unit exit 0 / 97 PASS; integration exit 0 / 89 PASS (verbatim commands below).
- `matrix_ok: true` — but only after **adding integration**, which the floor alone does not require. See Job 1.

## Phase 1 (pre-code) expected coverage, derived from BRIEF.md alone

Before reading any source: SC-01/03/05/08/09 → automated presence/absence checks with exit-status assertions (not line counts); SC-02/07/11/12 → inspection only (BRIEF says so itself, no runner covers the surface); SC-04 → full suite green including six named files; SC-06 → a resolve-both-shapes test; SC-10 → a parity test comparing CI vs session-entry renderings, reddening if either changes alone; SC-13 → one integration case (gh-sync) + one unit case (validate-feature-json) at migrated depth; SC-14 → two integration message-text assertions + one unit message-text assertion. **Delta against what was actually built:** none — Phase 2 confirmed every one of these exists, by name, in the diff (T-01, T-06, T-10). This is a **prescriptive-plan match** (O-05): the plan pins case labels verbatim (`parity`, `migrated_depth`, `not_onboarded`, `case_22a_...`), so the near-exact match is not independent-derivation evidence, it is compliance evidence.

## Job 1 — matrix derivation, and the floor is insufficient for this diff's shape

`harness.json` `test_matrix`: `logic` → `always: [unit]`. `config` → `always: []`. `scaffolding` → `always: []`.
Change types: T-01/T-03/T-04/T-05/T-06/T-09/T-10 = `logic` (→ requires `unit`); T-02/T-07 = `config` (→ nothing); T-08 = `scaffolding` (→ nothing).

`test_kinds.unit.cmd` = `run-unit-tests.sh --kind unit`, which runs only `UNIT_SCRIPTS` (`run-unit-tests.sh:17`). `test_kinds.integration.cmd` runs only `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`). Per-task binding table — the script that actually executes the changed file, and under which `--kind`:

| Task | change_type | Changed file(s) | Binding test | Array | Bound by floor (`unit`)? |
|---|---|---|---|---|---|
| T-01 | logic | test-layout-migration.py | itself | UNIT | yes |
| T-03 | logic | check-domain.sh | test-check-domain.py | INTEGRATION | **no** |
| T-04 | logic | check-plan-routes.py | test-check-plan-routes.py | INTEGRATION | **no** |
| T-05 | logic | check-state.sh | test-check-state.py | INTEGRATION | **no** |
| T-06 | logic | 8 test files | 6 of 8 in INTEGRATION (test-check-state/domain/plan-routes/bash-write-guard/harness-yaml/validate-digest), 2 in UNIT (test-no-distribution, test-factory-cli) | mixed | **no, for 6/8** |
| T-09 | logic | boundary note | task's own `verify:` runs `--kind unit` AND `--kind integration` directly | both | yes, but by the task's own verify, not by the matrix floor |
| T-10 | logic | gh-sync.py / validate-feature-json.py | test-gh-sync.py (INTEGRATION), test-validate-feature-json.py (UNIT) | split | gh-sync half: **no** |

**Finding: the floor (`logic` → `unit` only) does not execute the binding suite for T-03, T-04, T-05, 6 of T-06's 8 files, or T-10's gh-sync half.** Detection (the `unit.detect` glob matches `test-*.py` generally) is not execution — exactly the trap named in the dispatch. `integration` is the kind that actually binds these changes, and I added it as required and ran it:

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit    → exit 0, 97 PASS
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration → exit 0, 89 PASS
```
Named PASS lines for every task's binding file, confirmed in the raw output: `test-check-state.py`, `test-check-domain.py`, `test-check-plan-routes.py`, `test-bash-write-guard.py`, `test-harness-yaml.py`, `test-validate-digest.py`, `test-gh-sync.py` (integration); `test-layout-migration.py`, `test-no-distribution.py`, `test-factory-cli.py`, `test-validate-feature-json.py` (unit).

Additionally re-confirmed once each, exit codes only (all measured claims in the dispatch reproduced, not relayed): `layout_migration.py` → exit 0, `features: CLEAN — evidence migrated`, `docs: CLEAN — evidence legacy`, `0 mixed, 0 cannot-verify`; `check-state.sh` → exit 0, 0 INV-27 lines; `check-plan-routes.py` → exit 0, `0 violation(s)`, `examined 21 feature dir(s)` (non-zero — see Job 3).

**`matrix_ok: true` is honest only because I added `integration`.** Under the floor alone (`unit` only, as `logic` literally states), T-03/T-04/T-05 would report zero test-kind coverage. Kinds state: `unit` = satisfied (97 PASS, named); `integration` = satisfied, added beyond the floor and required for this change shape (89 PASS, named). No kind is missing, n/a, or blocked.

## Job 2 — D-08's two halves, mutation-probed on a scratch copy of `bin/` (never the main checkout)

Scratch copy: `/private/tmp/.../scratchpad/bin-probe/` (copied from `.claude/skills/harness/bin/`, outside the repo). Both probes run the **real, unmodified** `test-check-state.py` against the mutated `check-state.sh` via `CHECK_STATE_BIN` env override (the file's own documented escape hatch, `test-check-state.py:14-18`).

**(a) delivery half — neutered `fpath()` to bare basename.** Mutation diff confirmed applied (`diff` shown against the real file). Ran full suite: **exit 0, 0 FAIL lines** — every case still `ok`. **Finding: nothing in the suite asserts the label content `fpath()` produces.** Grepped `test-check-state.py` for any assertion naming a segment-qualified path (`.harness/harness/features/FEAT...`) — none exists outside the fixture-builder's own docstring comment (line 41), which is prose, not an assertion. Measured (not just reasoned) that the label is correct today: re-running `check-state.sh` over the live tree (`cs-out.txt`, captured earlier this run) shows the finding text `.harness/harness/features/FEAT-19-central-product-config/plan.yaml approval is pending — awaiting the user.` — segment-qualified, as D-08 intends. So the delivery half is measured-correct today but pinned by no test; a regression that reverts the label to a bare basename ships silently.

**(b) deferral half — qualified the `plan_docs` dict key with its segment, left the station-mirror lookup (`_feat = os.path.basename(_fp)`) unchanged.** Mutation diff confirmed applied. Ran full suite: **exit 1**, named cases went RED: `case (q/inv5)`, `(v.1)`, `(v.4)`, `(v.5)`, `(v.6)`, `(v.8)`, `(v.12)` — all INV-26 station-mirror cases. This is the correct, reassuring result: **the deferral half IS pinned** — qualifying the key the way D-08 forbids is caught, by name, by the existing suite. No finding here.

Net: one real finding — (a) is unpinned. **The no-authoring constraint, measured, not assumed:** `check-domain.sh --resolve` on `.claude/skills/harness/bin/check-state.sh` returns `harness-backend-dev harness-dev-ops` — not me; on my own artifact path it returns `harness-orchestrator harness-qa`. `tests/` does not exist in this repository (`ls tests` → No such file or directory). `run-unit-tests.sh`'s drift detector (lines 41-55) exits 2 on any `bin/test-*.py` not in its explicit `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays, so a file I could write under `tests/**` would match `unit`'s `detect` glob but run under no `cmd` — a green gate over a test that never executes. All findings below are therefore returned as precise specs, not code. Precise remedy for (a), since I hold no write to `bin/**`: add a case to `test-check-state.py` (joins `INTEGRATION_SCRIPTS`, already there) that stages two features under **different segment names** (e.g. `harness` and `other-repo`), runs `check-state.sh`, and asserts a finding line for each names its own **discovered** path prefix (`.harness/harness/features/FEAT-A/...` vs `.harness/other-repo/features/FEAT-B/...`), not a bare `.harness/features/FEAT-A/...`. Mutation that would prove it non-vacuous: exactly probe (a) above — revert `fpath()` to a bare basename; the new case must go RED where none does today. This subsumes Job 4's live-mechanism point (see below) — one fixture change serves both.

## Job 3 — the vacuity regression: does anything catch zero-discovery?

**`check-plan-routes.py`: bound.** `.github/workflows/tests.yml:165-172` carries a loud, active `examined -eq 0` guard on the real tree. Its *logic* is pre-existing (issue #133/DEC-183) and unchanged by this feature; its **error-string path text at line 171 is re-anchored by T-10** (`.harness/features/.` → `.harness/*/features/.`, confirmed as one of the three T-10 SC-14 substitutions, and confirmed present in the diff — `git diff --name-only 62fef85..5c39f8c` includes `.github/workflows/tests.yml`). Still live and correct post-move — confirmed by re-running `check-plan-routes.py`, which reports `examined 21 feature dir(s)`, non-zero. `test-check-plan-routes.py`'s own real-tree non-zero assertion was deliberately removed 2026-08-13 (documented in the file, lines 330-342) because it lost discriminating power once shipped features could legitimately zero out `plans`; its job moved to a fixture-based exact-count case (`case_19a3b`), which does bind and does discriminate — confirmed PASS in the integration run above.

**`check-state.sh`: NOT bound, by anything.** `check-state.sh` never prints an `examined N` count line at all (confirmed: `grep -n "examined" check-state.sh` → no hit; it either lists findings or prints `"  all state invariants hold."`). It is never invoked from `.github/workflows/tests.yml` (confirmed: only the comment at line 96 mentions it, no invocation). `test-check-state.py`'s docstring states plainly it never runs against the real repo state (line 4). **Named absence: nothing — no test, no CI step, no self-reported count — binds a non-zero discovery count for `check-state.sh` on the real tree.** The only thing that caught the mid-cluster zero-discovery incident described in the dispatch was a human comparing live output against the captured baseline in `layout-boundary-2026-08-14.md` — a one-time manual capture, not a standing assertion. This is a genuine gap with a spec'd remedy: add a case to `test-check-state.py` (INTEGRATION_SCRIPTS) that runs `check-state.sh` with `CLAUDE_PROJECT_DIR` pointed at a fixture holding N known feature directories and asserts the script's own note/warn output count is consistent with N staged features (or, more directly, stage a fixture engineered to trip a specific INV finding and assert the finding fires — which several existing cases already do implicitly, but none of them is framed as a discovery-count regression test, so a glob-pattern break that silently zeroes discovery for the REAL tree specifically is not independently caught). Routed as `open_question`, not `must_fix` — it is a standing-suite gap, not a defect in this diff's own tests.

## Job 4 — the two-segment adequacy question

Two classes, per the dispatch's own framing, confirmed against the file evidence:

1. **Cannot fire at one segment — key collision.** D-08's own reasoning (`plan.yaml` decisions block) states this explicitly and correctly: two repositories holding a same-named feature directory collapse last-write-wins in `plan_docs`, but it categorically cannot fire while one repository exists (there is no second segment to collide with). The deferral to unit 5/8 is on point and I re-affirm it — no finding here.

2. **Live today — the wildcard glob.** `check-state.sh`'s and `check-plan-routes.py`'s discovery globs (`os.path.join(H, "*", "features", "*")` / `os.path.join(root, ".harness", "*", "features")`) already discover **any** segment name, right now, at this landed commit — this needs no second onboarded repository, no `fleet.yaml` entry, nothing from unit 5/8. A two-segment fixture is two directories under `.harness/`, buildable in a tmp tree by any existing fixture builder in this suite. The prior panel's code-reviewer demonstrated a live defect (`check-plan-routes.py` silently swallowing an unreadable segment directory) this way, and that finding is already raised and routed as **ADV-1** — I do not re-file it. **My answer to the prior panel's open Q3: the readability-guard gap belongs to THIS feature's own test surface, not to the unit that lands segment two.** The distinguishing test is whether the defect requires two *repositories* (unit 5/8's job) or merely two *directories under different segment names* (buildable now, in this repo, by this feature's own suites). The readability guard is the latter. My Job 2 remedy above (a two-segment `test-check-state.py` case) is cut from the same cloth and should land alongside ADV-1's fix rather than as a separate ticket.

## SC evidence

| SC | Test |
|---|---|
| SC-01 | `layout_migration.py` re-run at pin: exit 0, `examined 21 feature dir(s)` (non-zero) |
| SC-02 | inspection — `notes/layout-boundary-2026-08-14.md`, both captures present with commit sha, verbatim, matches BRIEF wording exactly |
| SC-03 | `check-state.sh` re-run at pin: exit 0, 0 INV-27 lines |
| SC-04 | `run-unit-tests.sh --kind unit`/`--kind integration`, all six named suites PASS (shown above) |
| SC-05 | `test -e .harness/features` → absent (exit 1); `git ls-files .harness/features` → empty |
| SC-06 | `check-domain.sh --resolve` on post-move receipt path → `harness-backend-dev`/`harness-dev-ops`; pre-move shape → `NOBODY` (both re-run) |
| SC-07 | `git grep -l '\.harness/features/' -- .claude/agents .claude/commands .claude/skills` minus sanctioned exceptions → empty (re-run) |
| SC-08 | `test-branch-create-gate.py` (UNIT_SCRIPTS) — PASS |
| SC-09 | `.gitignore` grep, form-checked in T-07's own verify |
| SC-10 | `test-layout-migration.py`, case labelled `parity` — PASS, confirmed present in raw output |
| SC-11 | inspection — no `docs/harness/**` file in the diff range (T-01/T-06/T-08/T-09/T-10 file lists, none touch docs) |
| SC-12 | inspection — `git log --oneline 62fef85..5c39f8c` = 4 commits matching the plan's stated shape |
| SC-13 | `test-gh-sync.py` case `migrated_depth`/`not_onboarded` (integration, PASS); `test-validate-feature-json.py` case `case_migrated_depth_discovery_scans_the_segment_layout` (unit, PASS) |
| SC-14 | `test-check-plan-routes.py` `case_19a5...`/`case_22a...` (integration, PASS); `test-validate-feature-json.py` migrated_depth case's scanning-line conjunct (unit, PASS); workflow error string covered by T-10's own form-check verify only (BRIEF says so explicitly — no runner) |

## Coverage gaps (Phase 1 vs Phase 2 delta)

- None beyond the plan's own stated inspection-only SCs (SC-02/07/11/12) — matches Phase 1 expectation exactly.
- D-08 delivery-half label content: unpinned (Job 2a). New finding.
- `check-state.sh` zero-discovery regression: unbound on the real tree (Job 3). New finding.
- Two-segment fixture for the live wildcard mechanism: routed as belonging to this feature's own suite, alongside already-routed ADV-1 (Job 4).

## Test-first audit

T-01, T-06 and T-10 each land test edits in the same atomic commit (`d033b9d`) as the production code they cover — git history shows the whole cluster as one commit by design (D-02/D-03), so ordering within the commit is not separately checkable; the plan's own verify blocks (per-task, all read above) are what enforce shape before the commit lands. No violation found.
