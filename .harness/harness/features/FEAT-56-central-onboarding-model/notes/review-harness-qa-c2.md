# QA Review C2 — FEAT-56 — pin 9768681c2e290072ce4af7d25c4115603ce4e1ec

BLUF: **PASS.** Matrix confirmed at exact baseline (unit exit 0/4 by-design FAILs; integration
exit 1/exactly 6 failing cases, all `test-check-plan-routes.py`, all the D-14 owner-manifest
deviation — no seventh failure, no different cause). All three red-capability probes fired
correctly: the door-port gate is not vacuous, the CLI-floor guard reddens per token (14/14
probed), and the ordering-predicate fixture independently discriminates on all 6 permutations,
not just full reversal. All ten assigned SCs graded MET, each with per-file/per-command evidence
as their text demands. One `info`-severity finding on message clarity in
`sync-command-adapters.py`; not gating.

## 1. Matrix gate

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit`
  → **EXIT 0**, exactly 4 `^FAIL ` lines, all `tests/unit/test-factory-claim-mutation.py`
  (BUG-1290 5a/5b/5b-dup/5c) — this is the by-design negative-case suite; script itself PASSes.
  Matches baseline exactly.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration`
  → **EXIT 1**. Grep of `^FAIL ` returns 7 lines; 6 are per-case failures
  (`case_04_all_granted_exits_0`, `case_05_ungranted_declared_main_session_exits_0`,
  `case_15_deviation_plan_still_exits_0`, `case_17_midpattern_wildcard_grant_exits_0`,
  `case_19d_explicit_path_unaffected_by_the_root_guard`,
  `case_19d2_explicit_path_with_no_tasks_still_exits_0`), the 7th is the run-unit-tests.sh
  one-line-per-failed-script summary (`FAIL test-check-plan-routes.py`, per Expertise G-04). The
  runner's own tally line reads `6 FAILURE(S): [...]` naming exactly those six. All six cite the
  same `.harness/team-config.yaml` owner-manifest deviation vs the main checkout (D-14, expires at
  merge). **Exactly six failing cases, one file, one cause — no seventh, no different cause.**
- change_type for this feature's tasks is `docs`/`config` per plan.yaml; both ACTIVE matrix kinds
  (`unit`, `integration`) ran. `matrix_ok: true`.

## 2. Red-capability probes

**Note on method:** `.omp/commands/**` and `.claude/skills/harness-init|harness-add-repo/**` are
main-session-direct (NOBODY for harness-qa) even inside a disposable `git worktree add` under
`.claude/worktrees/` — the domain guard blocked direct file mutation there
(`bash-write-guard: ... outside your domain`). I did **not** route around it via a different tool
(that is the exact DEC-151 violation the guard names). Instead: (a) for the door-port probe, both
`sync-command-adapters.py` and `check-omp-port.py` accept an explicit `--root`/positional root
argument, so I built a fully synthetic, non-worktree sandbox at `/tmp/synth_door` (never
`git worktree add`, never inside any harness checkout, so the domain guard's path-matching never
fires) and pointed the scripts at it directly — no repo file touched. (b) for the token-guard and
ordering-fixture probes, `test-onboarding-split.py`'s checking functions
(`_harness_init_token_cases`, `_cli_probe_absence_cases`, `_central_model_marker_cases`) take
`text` as a plain argument, so I called them directly on the real file content with tokens
appended in memory — again no file touched, no domain issue. Both sandboxes were deleted after
use; no receipt needed since nothing was written into any tracked tree.

### a. Door-port gate vs its own bug (Lead 2)

Reconstructed the original defect (`.claude/commands/` populated with the four doors,
`.omp/commands/` absent) in `/tmp/synth_door`:

- `sync-command-adapters.py --root /tmp/synth_door --check` → **exit 1**,
  `Claude command adapters are stale: harness-grilling.md, harness-plan.md, harness-ship.md, harness.md`.
  Also tested `.omp/commands/` present but **empty** → same exit 1, same message. Neither state is
  vacuous.
  - **Finding (info, `.claude/skills/harness/bin/sync-command-adapters.py`, T-13, squad-writable):**
    the message frames the four Claude-only doors as *"stale adapters"* to be deleted on `--apply`,
    not as *"canonical files missing, doors need promotion"*. The exit code is correct and
    non-zero either way, so this does not gate — but an operator reading only the message could
    run `--apply` and delete the four doors' content rather than noticing they are the canonical
    source that needs to move to `.omp/commands/`. Advisory only; not required by any SC's wording.
- `check-omp-port.py /tmp/synth_door` → **exit 1**, and specifically among its 15 errors:
  `.omp/commands/harness.md is missing; harness has no provider-neutral door` (and the same for
  `harness-plan`, `harness-ship`, `harness-grilling`), each printed individually and by name. This
  assertion (`check-omp-port.py:168-171`) is a direct `is_file()` check per door, independent of
  the `sync-command-adapters.py --check` subprocess call it also runs — it does **not** merely
  prove four files exist at a new path; it explicitly names the canonical-root-missing case.
  **Conclusion: this gate would have caught the original bug, and does not merely validate a
  relocated no-op.**
- Root resolution is not overridable in production use: `check-omp-port.py`'s default root
  (`main()` line 187, `Path(__file__).resolve().parents[4]`) resolves to the real repo root when
  invoked with no args, which is how the standing suite calls it — so "wrong canonical root"
  is not a live risk in the shipped invocation.

### b. `test-onboarding-split.py` permanent guard (Lead 4)

Re-added each banned token in memory to the real `harness-init/SKILL.md` and
`harness-add-repo/SKILL.md` text and re-ran the exact case functions — **14/14 reddened**, each
naming its own token:
- `INIT_MUST_NOT_MATCH` (7): `Track A`, `Track B`, `factory/fleet.yaml`, `The approval gate`,
  `then the BRIEF`, `Design pass`, `harness-visual-designer` — all reddened against
  `harness-init/SKILL.md`.
- CLI-probe guard (2): `claude --version`, `2.1.217` — both reddened against
  `harness-init/SKILL.md`.
- `ADD_REPO_MUST_NOT_MATCH` (4): `The approval gate`, `then the BRIEF`, `Design pass`,
  `harness-visual-designer` — all reddened against `harness-add-repo/SKILL.md`.
- CLI-probe guard (1): `claude --version` — reddened against `harness-add-repo/SKILL.md`.

**Ordering-predicate fixture, verified independently of the simplify pass's own claim:** ran
`_central_model_marker_cases` over all 6 permutations of
(`default_branch`, `factory/fleet.yaml`, `<control-plane>/.harness/<segment>`), not just the
suite's own two synthetic cases (correct order / full reversal). All 6 permutations matched the
expected ordered/not-ordered verdict — the predicate discriminates on every partial
mis-ordering (e.g. `FL, DB, SG` and `DB, SG, FL`), not merely on total reversal. The suite's own
`case_central_model_marker_order_regression` synthetic fixture is a valid — if partial — proof;
my independent 6-permutation sweep confirms it generalizes.

### c. Orphan-door case (T-14 intent, `test-sync-command-adapters.py`)

Built a synthetic root with all four valid doors plus one extra
`.claude/commands/harness-orphan.md` with no `.omp/commands/harness-orphan.md` counterpart:
`sync-command-adapters.py --root ... --check` → **exit 1**,
`Claude command adapters are stale: harness-orphan.md`. Matches the suite's own
`ok orphan Claude-only door fails --check` / `ok orphan failure names the file` cases
(12/12 passed at pin). Confirmed independently, not merely trusted from the suite's own report.

## 3. SC grades (assigned: SC-01, 02, 05, 06, 07, 08, 10, 13, 14, 16)

- **SC-01 — MET.** Ran T-10's `verify` block verbatim against
  `.claude/skills/harness-add-repo/SKILL.md` at pin: every clause passed (Preflight heading, no
  `claude --version`, no `templates/team-config.yaml`, no `instantiate its own`/`from the
  templates`/`the only place a`, no `into the control plane's`, has `anywhere but the control
  plane` and `IS a grilling`, no control-plane-grilling clause, no red-flag-row leakage, no
  approval/BRIEF/Design-pass/visual-designer strings, has `--check-product-configs`, exactly
  `### 1.`/`### 2.`/`### 3.` headings and no `### 4.`-`### 9.`, no stale step-number phrases, and
  the default_branch/fleet.yaml/segment markers appear in that line-number order), plus
  `check-instruction-paths.py` exits 0 (`scanned 62 file(s), 0 violation(s)`).
- **SC-02 — MET.** `git show 9768681c:.claude/skills/harness-init/SKILL.md` verified via the
  standing suite's own hook check; `env -u HARNESS_AGENT_TYPE python3
  tests/integration/test-hooks-install.py` exits 0 (ran as part of the green `--kind integration`
  run: file is discovered by that suite and passed with the other 12/12-style suites — no skip
  reported).
- **SC-05 — MET.** `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py` →
  **18/18 checks passed**, exit 0. Matches the BRIEF's 12f74ea8 baseline; no `factory_config.py`
  or the test file touched by this revision's tasks, re-take reproduces as expected.
- **SC-06 — MET.** `--kind unit` exits 0 (see §1). By-design FAILs are the four
  `test-factory-claim-mutation.py` cases, script itself PASS.
- **SC-07 — MET, per criterion's own carve-out.** `--kind integration` exits 1, but the criterion
  is graded jointly with the BRIEF's own `## Verification gaps` D-14 acceptance: "the qa gate may
  pass with it outstanding while citing D-14; it clears at merge... every per-task route line
  still reports OK, and a second violation of any kind is a failure." No case reports a skip for a
  missing skill anchor (checked the full log: zero `SKIP` tokens). No second violation observed —
  exactly the 6 D-14 cases, nothing else red.
- **SC-08 — MET.** `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-instruction-paths.py`
  → `scanned 62 file(s), 0 violation(s)`, exit 0. `env -u HARNESS_AGENT_TYPE python3
  .claude/skills/harness/bin/check-omp-port.py` → prints exactly `OMP port surface: ok`, exit 0 —
  confirmed via §2a that this is not a check that "looks at nothing": it explicitly asserts each
  door's existence and delegates to `sync-command-adapters.py --check`.
- **SC-10 — MET.** `env -u HARNESS_AGENT_TYPE python3 -c "import
  yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"` → exit 0.
- **SC-13 — MET, all four assertions independently.**
  1. `sync-command-adapters.py --check` (real repo, real root) → exit 0.
  2. Per-file existence, not count: `.omp/commands/harness.md` PASS,
     `.omp/commands/harness-plan.md` PASS, `.omp/commands/harness-ship.md` PASS,
     `.omp/commands/harness-grilling.md` PASS (each `git cat-file -e 9768681c:...` individually).
  3. `tests/integration/test-sync-command-adapters.py` → exit 0, 12/12, including
     `ok well-formed tree passes --check`, `ok orphan Claude-only door fails --check` (re-verified
     independently in §2c), and `ok orphan failure names the file`.
  4. `tests/integration/test-check-omp-port.py` → exit 0, 23/23, including
     `ok missing command door fails` / `ok missing door is named` and
     `ok absent canonical command root fails` / `ok absent canonical root names all four doors` —
     the criterion's stated "teeth" cases are present and green, and independently re-verified
     live in §2a (not merely trusted from the suite's own report).
- **SC-14 — MET.** `tests/integration/test-onboarding-split.py` → exit 0, all 24 named assertions
  PASS (7 init-token, 2 CLI-probe-init, 1 add-repo-exists, 4 add-repo-token, 3 add-repo
  central-model-marker presence, 1 add-repo ordering, 2 command-door-no-init-citation, 1
  add-repo Preflight heading, 1 add-repo no-claude-version, 2 more CLI-probe checks — see full
  output; plus the 2 synthetic-ordering-regression cases). Independently re-verified the
  token-guard and ordering-fixture discrimination in §2b, not merely trusted from the pass count.
- **SC-16 — MET, all clauses, per-file (never a global grep).**
  - `.harness/harness.json`: `json.load` parses OK, `cli_min_version` NOT in mapping.
  - `.claude/skills/harness/templates/harness.json`: parses OK, key absent.
  - `.claude/skills/harness/templates/examples/harness.kaya-ai.json`: parses OK, key absent.
  - `.harness/team-config.yaml`: `yaml.safe_load` parses OK, key absent from mapping, content
    matches neither `cli_min_version` nor `floor for the spawn env vars`.
  - `.claude/skills/harness/templates/team-config.yaml`: same, all clauses pass.
  - `.harness/harness/docs/BUILD.md`: content does NOT match `cli_min_version` anywhere.
  - `.harness/harness/docs/DECISIONS.md`: content DOES match `cli_min_version` (DEC-83's
    amendment names the key) AND DOES match `2.1.172` (the band row survives).
  All checked individually at `git show 9768681c:<path>`, never by one global grep.

## Findings summary

| File | Task | Severity | Lane | Note |
|---|---|---|---|---|
| `.claude/skills/harness/bin/sync-command-adapters.py` | T-13 | info | squad-writable | `--check` on a missing/empty canonical root reports the Claude-only doors as "stale, to be deleted" rather than "canonical missing, needs promotion" — exit code is correct (non-zero) either way, not gating, advisory on operator-facing clarity only. |

No SETTLED items re-raised. D-14's six-case integration red not reported as a finding (contract).

## Coverage vs Phase-1 (no-source) expectations

Before reading the diff I expected: (1) a positive existence+order test for the new skill's
central-model statement, (2) a negative test that stale onboarding-combined markers don't return,
(3) a mechanical (not inspection-only) door-reachability gate with a demonstrated red state, (4) a
per-file (not aggregate) cli_min_version absence check, (5) unit/integration suites both green
modulo the known D-14 exception. All five are present and match what T-10/T-13/T-14/T-16/T-19
built; no gap between Phase-1 expectation and delivered coverage.
