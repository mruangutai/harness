# QA gate — BUG-240 workspace hard-reset guard — cycle 0

**matrix_ok: true.** Both required kinds ran green at the pin. GATE-ONLY: authored nothing.

## Pin identity

`git diff ed047fde93d367d52d09d665bac8c6957667ac0c HEAD -- .claude/skills/harness/bin/factory_workspace.py tests/unit/test-factory-workspace.py` → empty, exit 0. HEAD's two extra commits are feature.json-only bookkeeping; the two files under review are byte-identical at the pin and at HEAD. Exercised HEAD in the worktree as a faithful stand-in for the pin.

## Matrix derivation (change_type: bugfix, `.harness/harness.json` bugfix row)

- `always: []`.
- `unit if touches_runtime_code` → **true**: `.claude/skills/harness/bin/factory_workspace.py` is bin/ runtime code (not test/doc). **unit required.**
- `integration if fix_confined_to_tests_and_contract_docs` → **false**: the fix changes production code (`_main`'s refresh branch), not confined to tests/contract docs. **integration not required by this predicate.**
- `__bug_class__ if match_bug_class` → per this repo's own qa Expertise (G-08), `match_bug_class` is currently an unresolvable placeholder — no bug-class taxonomy entry fires for any diff yet. **no additional kind required.**
- Diff has no UI, API, or config-shape surface → no kind added above the floor.

**Required floor: `{unit}`.**

## Per-kind result

| kind | cmd | rc | ^FAIL count | result |
|---|---|---|---|---|
| unit (task verify, part 1) | `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py` | **0** | **0** | satisfied — `38/38 checks passed.` |
| unit (task verify, part 2 / standing kind cmd) | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | **0** | satisfied — 31/31 unit files PASS, including `test-factory-workspace.py` (exit 0, 38/38) inline in the run |

Both commands captured to files and their exit status read from `$?` into a variable, not inferred from tail output. `grep -c '^FAIL '` run independently over each full log; zero both times.

`integration`: not required (predicate false) — not run, not claimed.

## Adequacy audit: source-verified, not inherited

Read `git -C <worktree> show ed047fde:tests/unit/test-factory-workspace.py` directly. **Cases 2, 3 and 4 drive REAL git, not a monkeypatch** — settling the earlier dispatch's opposite claim as wrong:

- File's own docstring (pinned, lines 10-14): "Most cases here monkeypatch run_git with a recorder... the BUG-240 cases that exercise the hard-reset guard are the exception — they build a real local bare origin and checkout via `real_repo()` and drive real git, with no network."
- Case 2/3 fixture (line 358): `run_main(fw.run_git, ["--repo", REPO, "--issue", str(ISSUE)], wr)` — passes the module's real `run_git` function itself as the "recorder" argument; `run_main` assigns it straight back to `fw.run_git`, so nothing is faked.
- Case 4 (line 396): identical pattern, `run_main(fw.run_git, ...)`, plus real `git add`/`commit`/`push` via `subprocess.run` to build the ignored-dirt fixture.

There are **8 distinct `check("BUG-240 ...")` names** in the pinned file (not 9 — verified by grepping every `check("BUG-240` call site): the (B)-block order addition, plus cases 1, 2, 3, 4, 5, 6, 7. All 8 appear in the green run log at their expected `ok` lines.

Real-behaviour vs. seam, by name:
- **REAL git** (3): "dirty tracked: refusal line names the path and the uncommitted-work condition", "dirty tracked: the modified file survives byte-identical", "ignored-only dirt: not refused" — these three reproduce the actual defect end-to-end (a real `reset --hard` that would have destroyed `tracked.txt` absent the guard) and are the strongest evidence in the suite.
- **Seam-based** (5): "existing checkout: refresh order..." (Recorder), "dirty tracked: exits 2 before any fetch" (Recorder), "self checkout: refused when clean..." (Recorder + stubbed `_control_plane_root`), "other harness checkout: ... not refused" (Recorder + stubbed `_control_plane_root`), "no bypass: the parser rejects --force" (argparse + source-text grep). The two self/other-checkout cases necessarily stub `_control_plane_root` — driving the real control-plane path in-process is what the guard exists to forbid — so the seam here is the correct design, not a shortcut.

## Per-SC (SC-01..SC-05, `verify: automated`)

| SC | status | discharging check |
|---|---|---|
| SC-01 | satisfied | "BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition" (real git) + "...the modified file survives byte-identical" (real git) |
| SC-02 | satisfied | "BUG-240 ignored-only dirt: not refused" (real git) |
| SC-03 | satisfied | "BUG-240 self checkout: refused when clean, naming the self-checkout condition" (Recorder + stubbed `_control_plane_root`) |
| SC-04 | satisfied | "BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard" (Recorder, (B)-block) for the refresh-order half; pre-existing case (A) ("missing checkout: first call is clone") for the clone-still-works half |
| SC-05 | satisfied | `run-unit-tests.sh --kind unit` exit 0, captured above |

SC-06 is `verify: inspection` — that is the code reviewer's determination, not asserted here.

## Settled items — not re-raised

F-01 (ordering asserted only through the `run_git` seam), F-02 (no-bypass is a 3-literal source grep), ALT-5 (dirty check also refuses non-destructible untracked content) are on record as adjudicated at plan signature. Not raised again; not `must_fix`.

## Test-first

T-01 (tests, `status: done`) precedes T-02 (production guard, `status: done`, `depends_on: [T-01]`) in the plan's own task graph, and T-01's verify pins the pre-T-02 red state (4 of 8 FAIL). Order confirmed by plan structure, not re-derived from git history in this gate-only pass.
