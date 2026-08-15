# Receipt — harness-backend-dev — T-12 (FEAT-10-software-factory)

## Verdict

PASS. `test-factory-integration.py` written and registered (93/93 checks pass, ~5.6s). Both
untested T-06 live-git argv forms (`-b --track` and `-B --track`) exercised against real git and
found correct — outcome 1 of the three pre-decided outcomes.

## Task verify — verbatim

Command (character-exact from plan.yaml:1637, cross-checked against the dispatch — no mismatch):

```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration > /tmp/v-t12.txt 2>&1; s=$?; grep -q "^PASS test-factory-integration.py$" /tmp/v-t12.txt && [ "$s" -eq 0 ]
```

Result: **pass** (both the grep and `[ "$s" -eq 0 ]` succeeded; `$?` of the whole compound was 0).

## Measurement, as required

**BEFORE my append** — `run-unit-tests.sh --kind integration`:
- exit status: **0**
- files run (13): test-validate-digest.py, test-gh-sync.py, test-check-state.py,
  test-check-expertise.py, test-gen-decisions-index.py, test-bash-write-guard.py,
  test-check-domain.py, test-harness-yaml.py, test-upgrade-config.py, test-check-plan-routes.py,
  test-merge-settings.py, test-gen-omp-agents.py, test-omp-reviewer-guard.py

**AFTER my append** — `run-unit-tests.sh --kind integration`:
- exit status: **0**
- files run (14): the same 13, plus **test-factory-integration.py**

**`--kind unit` after finishing** (must stay 0, untouched):
- exit status: **0**
- files run (10, unchanged): test-harness-yaml-corpus.py, test-render-brief.py,
  test-team-catalog.py, test-factory-cli.py, test-factory-gh.py, test-factory-config.py,
  test-factory-workspace.py, test-factory-decompose.py, test-factory-claim.py,
  test-factory-land.py
- `UNIT_SCRIPTS` (line 58 of `run-unit-tests.sh`) is byte-identical before and after my edit —
  confirmed by re-reading the line post-edit against the pre-edit `Read` output.

No new red anywhere; nothing in `check-state.sh` / `test-check-state.py` / `validate-digest.py`
was touched.

**`--kind all` (union path, run twice for stability):** exit 0 both times, 24/24 `PASS test-*.py`
both times, `diff` of the two runs' `PASS`/`FAIL` lines is empty (no leaked state between runs).

**`test-factory-integration.py` run standalone, twice:** `93/93 checks passed.`, exit 0, both
times.

**`check-docs.sh`:** `checked 62 superseded pattern(s) across 294 file(s). no stale statements
found.`, exit 0 — run before this receipt was finalized.

## The three live-git outcomes — which one I hit

**Outcome 1: real git accepts both argv forms.** Git version exercised (measured on this
machine, printed by the test itself): `git version 2.50.1 (Apple Git-155)`, at `/usr/bin/git`.

- `factory_workspace.py:101` (`checkout -b <b> --track origin/<b>`) — a fresh clone whose local
  checkout carries no `factory/issue-<n>` yet, origin already carrying it. Asserted (not just
  exit 0): `HEAD` after the run equals origin's `factory/issue-1` sha, and the local branch's
  upstream is `origin/factory/issue-1`.
- `factory_workspace.py:97` (`checkout -B <b> --track origin/<b>`) — a local `factory/issue-<n>`
  cut from `default_branch` with no upstream, origin's ref pointing at a *different*, later
  commit. Asserted the local branch is force-aligned: `HEAD` afterward equals origin's tip, and
  the upstream is now `origin/factory/issue-2`. A fixture sanity check (before the run) confirms
  the pre-conditions actually diverged, so the assertion cannot pass vacuously via
  `checkout <branch>` alone.

Both cases use hermetic git (`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_SYSTEM=os.devnull`, a
private `HOME`) so `branch.autoSetupMerge` cannot silently give the `-B` fixture's local branch an
upstream before the tool runs (which would make that case exercise `checkout <branch>` instead of
`-B --track`, i.e. pass without ever reaching line 97).

## Findings surfaced (not fixed — every one lives on the LEAVE list)

1. **Two of the five tools never call `gh` at all.** `factory_config.py` and
   `factory_workspace.py` import neither `factory_gh` nor `gh_issues` (grep-verified). The
   intent's "for each of the five command-line tools ... a stub gh that exits non-zero on auth
   status makes the tool exit with process status exactly 2" is therefore authored only for
   `factory_decompose.py`, `factory_claim.py` and `factory_land.py` — the other two structurally
   cannot exhibit that failure mode. Not a defect; a narrower fact than the intent's phrasing
   states, reported so it isn't silently assumed covered.
2. **`factory_config.py`'s "no arguments" case does NOT trivially exit 2 the way the other four
   tools' argparse-driven refusal does** — it has zero required arguments, so with
   `CLAUDE_PROJECT_DIR` unset it would load this checkout's own committed
   `.harness/factory/fleet.yaml` and exit 0. This dissolves once `CLAUDE_PROJECT_DIR` is pointed
   at a fixture root with no `.harness/factory/fleet.yaml` present (as every case here does): the
   default `FLEET_PATH` then 404s, `harness_yaml.load_file` raises `YamlParseError` (an `OSError`
   subclass path), and `factory_cli.run`'s `BaseException` trap exits 2. Verified directly before
   writing the test (measured both ways). No fix needed; recorded so the reasoning is on record.
3. **`factory_claim.py:43`'s import-time `FEATURES_ROOT`** (already a carried, non-blocking
   finding per the dispatch) is why the SC-19 chain's fixture plan lives at exactly
   `<CLAUDE_PROJECT_DIR>/.harness/features/<feature>/plan.yaml` — there is no env-var override,
   only the `CLAUDE_PROJECT_DIR` redirect of `harness_root()` at import time. Confirmed this is
   the only working seam; not fixed (LEAVE list).

None of the three known non-blocking findings named in the dispatch (`YamlParseError` leaking
into operator output, the duplicated 422 phrase, `factory_claim.py:43`) were touched.

## A near-miss worth recording

While sanity-checking the mutant-catching power of the live-git assertions by hand, I typed
`git checkout -Bx bogus --track origin/nope` directly into Bash outside any fixture. It was
correctly blocked by `branch-create-gate.sh` (DEC-144) before anything happened. Per the
dispatch's explicit instruction, I stopped that manual-verification approach entirely rather than
finding a way around the gate — the G1/G2 assertions' non-vacuousness rests instead on the
outcome-based assertions (SHA/upstream, not just exit status) plus the fixture-sanity checks that
prove the `-B` pre-conditions were genuinely met before the tool ran.

## Files touched

- `.claude/skills/harness/bin/test-factory-integration.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (single-line append to `INTEGRATION_SCRIPTS`,
  line 59; `UNIT_SCRIPTS` at line 58 untouched)
