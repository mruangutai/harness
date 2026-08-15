# QA gate — FEAT-10, working tree vs f9488a2

## Verdict: BLOCKED

`test_kinds.functional.cmd` is `null` in `.harness/harness.json`, untouched by this diff
(`git diff HEAD -- .harness/harness.json` shows only the `integration` block changed), and
`tests/functional/**` matches zero files in the repo. The diff's own classification requires
`functional` (see table below), so this resolves to **misconfigured -> BLOCKED**, not FAIL and
not a soft skip: a soft "not applicable" is reserved for genuinely absent tooling (no browser
driver), not an unset `cmd` — the skill's rule is explicit that null `cmd` is always
misconfigured. Fix location: `.harness/harness.json`. The code under test is not the problem.

The BRIEF's own "Verification gaps" section asserts: "`functional`, `component`, `ui`, `eval`
and `typecheck` have `cmd: null`. This increment touches none of their surfaces... so nothing
here rests on a kind with no runner." That sentence is the finding this gate contradicts: five of
the seven new modules coordinate multiple internal modules and/or talk to an external system
(`gh`, `git` via subprocess), which is exactly `api`/`cross_module` territory, and both of those
change types put `functional` in `always`. The conclusion does not depend on picking `api` over
`cross_module` over a single coarse `feature` for the whole slice — all three floors include
`functional`. Only an all-`logic` classification would avoid it, and `factory_gh.py`'s
`subprocess.run([gh] + args)` forecloses that reading.

## Phase 1 — expected coverage, from BRIEF.md alone (before reading source)

Derived from REQ-01..08 and the 19 `verify: automated` SCs before opening any `.py` file:
unit tests per module (fleet loader, gh seam, publish/decompose, claim, workspace, land), one
forked-process integration test proving the whole publish->claim->workspace->land journey exits
0 with parseable stdout (SC-19), a separate integration proof that a fleet/state mismatch is
caught (SC-06), and inspection-only evidence for the two structural/negative claims (SC-03,
SC-09) since neither carries `evidence:`. No `functional`, `component`, `ui`, `eval`, or
`typecheck` evidence is named anywhere in the brief — the brief's own conclusion is that no kind
without a runner is needed. That expectation is exactly what this gate is now contradicting; see
"the finding" above.

## Phase 2 — classification, per logical change (from the diff)

| Group (module + its test file) | change_type | Why |
|---|---|---|
| `factory_cli.py` + `test-factory-cli.py` | **logic** | Pure library: message/exit-code formatting, JSON payload emission, an exception trap. No I/O, no other factory-module import, no external call. |
| `factory_config.py` + `test-factory-config.py` | **logic** | Reads and validates one local YAML file; imports `factory_cli` and `harness_yaml` for formatting/parsing only, no network. |
| `factory_gh.py` + `test-factory-gh.py` | **api** | The sole seam to GitHub: every function shells out via `subprocess.run([gh] + args)`. `touches_db_or_external` is true by construction — this module's entire job is the external call. |
| `factory_decompose.py` + `test-factory-decompose.py` | **cross_module** | Orchestrates `factory_config`, `factory_gh`, `harness_yaml`, `factory_cli` together to publish a plan (label ensure, parent adopt/create, issue create, board add, two-pass edge draw), plus an atomic file-splice write to `feature.yaml`. |
| `factory_claim.py` + `test-factory-claim.py` | **cross_module** | Orchestrates `factory_config`, `factory_gh`, `factory_cli`, `harness_yaml` for the candidate loop, blocker gate (reads a second feature's `plan.yaml`/`feature.yaml`), and the create-if-absent race. |
| `factory_workspace.py` + `test-factory-workspace.py` | **api** | External system seam to `git` via `subprocess.run`; single internal import (`factory_config`) for path derivation only. |
| `factory_land.py` + `test-factory-land.py` | **cross_module** | Orchestrates `factory_workspace.run_git`, `factory_gh`, `factory_config` to push, open a PR, and move the board station. |
| `test-factory-integration.py` (no paired new module) | — | Not classified on its own; it is the integration evidence for the five groups above (SC-19, SC-15, SC-10 fork-level cases) and, incidentally, keeps `test-check-state.py` (T-08, withheld) registered under `--kind integration`. |
| `run-unit-tests.sh` | **scaffolding** | Registers the seven new test files into `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`; the file's other hunk (CLAUDE_PROJECT_DIR root-resolution rewrite) is orthogonal held-dirt (omp support) bleeding into the same file, not re-litigated here since it does not change factory behavior and the suite ran green under it. |
| `.harness/harness.json` | **config** | Widens `integration.detect`, removes the stale `_reason` beside `integration.cmd` (cmd itself was already set). Leaves `functional.cmd` untouched — the fact this gate turns on. |
| `docs/harness/DECISIONS.md` + `docs/harness/DECISIONS-INDEX.md` | **docs** | Adds DEC-186 (SC-09's evidence) and its index row. |

**Union of floors actually bound by this diff:** `unit` (from every group), `functional` (from
`api` x2 and `cross_module` x3), `integration` (from `api`/`cross_module`'s "always", and
directly named by SC-06/SC-15/SC-19). `logic`, `scaffolding`, `config` and `docs` contribute no
kind beyond `unit`. Denominator: 5 of the 11 groups (`factory_gh`, `factory_workspace`,
`factory_decompose`, `factory_claim`, `factory_land`) are the ones binding `functional`; the
other 6 (cli, config, integration-test-file, scaffolding, config-file, docs) do not.

## Kind resolution table

| Kind | Required by | State | cmd | Exit | Named tests (own captured output) |
|---|---|---|---|---|---|
| unit | every group | **satisfied** | `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | `grep -E '^(PASS\|FAIL) test-.*\.py$'` on my own run: `test-factory-claim.py`, `test-factory-cli.py`, `test-factory-config.py`, `test-factory-decompose.py`, `test-factory-gh.py`, `test-factory-land.py`, `test-factory-workspace.py` all `PASS` (7/7 new files), plus 3 pre-existing unrelated files also `PASS`. Zero `FAIL` lines. |
| integration | api, cross_module groups; SC-06/15/19 named directly | **satisfied** | `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | `test-factory-integration.py` `PASS` (own captured output), `test-check-state.py` `PASS` (T-08 surface, withheld, left untouched and still green as instructed). 14/14 registered files `PASS`, zero `FAIL`. |
| functional | api, cross_module groups | **misconfigured -> BLOCKED** | `null` (unchanged by this diff) | n/a | n/a — `cmd` is null AND `tests/functional/**` matches zero files (`find . -type d -name functional` returns nothing). Both triggers named in the skill's misconfigured row are present. |
| component, ui, eval, typecheck | not required (no `frontend`, `ai_behavior` group; no `.ts`/`.tsx` in diff) | not applicable | null | n/a | Genuinely absent surfaces — no UI, no component substrate, no model-behaviour change in this diff. Soft skip, not a finding. |
| inspection (SC-03, SC-09) | required by those two SCs' `verify: inspection` | **satisfied by direct read** | n/a | n/a | SC-03: read `factory_decompose.py`, `factory_claim.py`, `factory_workspace.py`, `factory_land.py` — the only harness file any of them writes is `feature.yaml`'s `factory:` block (`factory_decompose.write_factory`); none opens `plan.yaml`/`BRIEF.md` for writing. SC-09: `docs/harness/DECISIONS.md` DEC-186 (added lines ~5421 on) states the three-purpose bound, names DEC-138 as the amended baseline, states `blocked_by` is never read back, states the per-blocker-per-candidate cost; `check-docs.sh` ran clean (`checked 62 superseded pattern(s) across 294 file(s). no stale statements found.`, exit 0). |

## Findings distinct from the blocking one

- **SC-06 has no evidence in this diff.** Its `evidence: integration` traces to `check-state.sh`
  INV-24, which is T-08 — explicitly withheld under the DEC-174 carve-out per this dispatch.
  `grep -n INV-24` on both `check-state.sh` and `test-check-state.py` returns nothing. This is
  not a defect of the diff under gate (T-08 correctly sits outside it), but it is a real
  coverage gap the operator should see stated rather than assumed: **SC-06 is unverified until
  the main session does T-08 directly.**
- **REQ-04/REQ-05 remain proven against test doubles only** (BRIEF's own qualification,
  confirmed by reading `test-factory-workspace.py`/`test-factory-land.py`: both use a recorded
  `FACTORY_GIT`/`FACTORY_GH`, never a real remote).
- **`sub_issues` re-post idempotence is unmeasured** — only the `blocked_by` 422 path was probed
  live (BRIEF's own statement, unchanged by this diff; `factory_decompose.py`'s edge pass treats
  a re-drawn `blocked_by` 422 as already-drawn but has no equivalent narrowing for
  `attach_sub_issue`).
- **The claim primitive's actual concurrent-creator serialization is exercised by no criterion**
  — inferred from the endpoint being create-only, per the BRIEF's own accepted residual.

## Test-first audit

Nothing is committed, so git history proves nothing about order — confirmed
(`git status --porcelain` on every new file under `bin/` shows `??`, no commits reference them).
What is establishable is what each receipt records as measured, not merely claimed:

- **T-02, T-03, T-04, T-05, T-06, T-07, T-11** (`receipt-harness-backend-dev-T-0{2..7,11}-c0.md`)
  each state a specific RED signature observed before the production module existed — e.g. T-02:
  "`ModuleNotFoundError: No module named 'factory_config'`"; T-05: "`ModuleNotFoundError`... "
  before `factory_claim.py` existed"; T-04 additionally discloses and corrects a self-inflicted
  incident (an edit script flipped two `open()` calls to write mode) rather than omitting it.
  These are concrete, falsifiable claims (a specific traceback message), which is stronger than
  a bare assertion, but they remain **self-reported and unverifiable from the tree** — I did not
  re-run a red/green perturbation myself (out of scope: I write no tests here).
- **T-12** (`receipt-harness-backend-dev-T-12-c0.md`) does not carry the same explicit
  RED-before-code phrasing; it reports "PASS. `test-factory-integration.py` written and
  registered (93/93 checks pass...)" without a captured pre-implementation failure signature.
  **Mark T-12's test-first claim unverifiable**, distinct from the other seven which at least
  self-report a specific RED artifact.
- Overall: **7 of 8 relevant build tasks self-report a specific RED signature; 1 does not; 0 are
  confirmed by anything this auditor can independently check** (no commits exist to diff).

## SC evidence (for pm's goal-check)

| SC | Test (path:section) |
|---|---|
| SC-16, SC-17, SC-01 | `.claude/skills/harness/bin/test-factory-decompose.py` (publish disposition/edge cases) |
| SC-20 | `.claude/skills/harness/bin/test-factory-decompose.py:745-768` (`(SC-20)` byte-identical hash checks) |
| SC-22 | `.claude/skills/harness/bin/test-factory-claim.py:500-639` (`B1`-`B7`, asserts the exact `create_ref` call, not exit status) |
| SC-13 | `.claude/skills/harness/bin/test-factory-claim.py` `R2`/`R3`/`B2` (clause a: skip-and-continue; clause b: `"no claimable work"` present, `"no work available"` absent, asserted against captured `err`) |
| SC-18, SC-08, SC-21 | `.claude/skills/harness/bin/test-factory-config.py` |
| SC-19 | `.claude/skills/harness/bin/test-factory-integration.py:574+` (Case F, forked subprocess chain) |
| SC-04 | `.claude/skills/harness/bin/test-factory-workspace.py` |
| SC-05 | `.claude/skills/harness/bin/test-factory-land.py` (M5/M6: no git call pushes default branch, no gh call is a merge) |
| SC-12 | `.claude/skills/harness/bin/test-factory-claim.py` (R4: `--issue` create_ref False -> exit 3, zero mutations) |
| SC-11 | `.claude/skills/harness/bin/test-factory-integration.py:406-542` (Case D, `json.loads(r.stdout)` per tool) |
| SC-10, SC-15 | `.claude/skills/harness/bin/test-factory-integration.py:333-400` (Cases A/B/C, real forked `r.returncode`) |
| SC-14 | `.claude/skills/harness/bin/test-factory-claim.py` (`mutating_calls() == []` over the full recorded list) |
| SC-03 | inspection (see table above) |
| SC-09 | inspection — `docs/harness/DECISIONS.md` DEC-186 |
| SC-06 | **none in this diff** — see Findings above |

## coverage_gaps

- `functional` kind: no runner (`cmd: null`), no files under `tests/functional/**` — this is the
  blocking finding.
- SC-06 — no evidence in this diff; sits behind the withheld T-08.
- REQ-04/REQ-05 proven only against test doubles (BRIEF's own accepted gap).
- `sub_issues` edge re-post idempotence — unmeasured, only `blocked_by`'s 422 was probed live.
- The claim primitive's real concurrent-creator serialization — exercised by nothing (accepted
  residual, `verify: uat` criterion that would have covered it was deleted 2026-08-08).
- T-12's test-first claim — unverifiable, no RED signature recorded (contrast with the other 7).
