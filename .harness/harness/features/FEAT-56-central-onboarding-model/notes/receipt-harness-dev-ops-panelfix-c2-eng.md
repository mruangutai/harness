# Receipt — harness-dev-ops — panelfix-c2-eng

BLUF: F1, F3, F4 closed in cycle 1; the lead REJECTED cycle 1's tolerance carve-out in
`case_live_tree_passes`, and cycle 2 removed it (see "Cycle 2" below — that section is now the
accurate description of `case_live_tree_passes` and of the `--kind integration` baseline).
`test-sync-command-adapters.py:main()` (was grade 1, ABC 50.2) is decomposed into six `case_*`
functions + a thin aggregator, matching the file's own convention; nothing in the file is below
grade 4. `sync-command-adapters.py` gained a `REQUIRED_DOORS` module constant and a hard
fail-closed check for an absent required canonical door (F3), proven before/after against a real
scratch tree. The banner now names the real script path (F4); this makes `--check` legitimately
red against the live `.claude/commands/**` tree until the main session regenerates those four
adapters — expected, documented, not fixed here (out of lane), and as of cycle 2 the test suite
is left honestly red on that basis rather than tolerating it. Nothing committed; nothing touched
outside the three source files, this receipt, and pre-existing panel notes.

## F1 — `test-sync-command-adapters.py:main()` was code grade 1

Split into 6 `case_*()` functions (matches the file's own 5-independent-scenario shape, adopting
`test-onboarding-split.py`'s `case_*`/results-list convention — `test-sync-agent-adapters.py`'s
single continuous-narrative shape didn't fit 5 independent tempdir scenarios) plus a thin `main()`
that aggregates and prints. All 12 original assertions preserved verbatim, plus 3 new ones for the
F3 case (2d/2e below); total is honestly derived as `len(results)`, not hardcoded.

**BEFORE** (panel note, confirmed identically by my own pre-edit run):
| Qualname | Cyclo | Cog | ABC | Grade | Bar | Result |
|---|---:|---:|---:|---:|---:|---|
| `main` | 1 | 1 | 50.2 | **1** | 3 | **FAIL** |

**AFTER**:
| Qualname | Cyclo | Cog | ABC | Grade | Bar | Result |
|---|---:|---:|---:|---:|---:|---|
| `run` | 1 | 1 | 3.0 | 5 | 3 | PASS |
| `banner` | 1 | 0 | 0.0 | 5 | 3 | PASS |
| `seed` | 2 | 1 | 7.3 | 5 | 3 | PASS |
| `case_well_formed_tree_passes_check` | 1 | 0 | 5.1 | 5 | 3 | PASS |
| `case_edited_adapter_body_fails` | 1 | 0 | 7.5 | 5 | 3 | PASS |
| `case_missing_banner_fails` | 1 | 0 | 6.7 | 5 | 3 | PASS |
| `case_orphan_door_fails` | 1 | 0 | 6.7 | 5 | 3 | PASS |
| `case_missing_adapter_apply_workflow` | 2 | 2 | 17.3 | 4 | 3 | PASS |
| `case_missing_required_door_fails` (new, F3) | 1 | 0 | 9.9 | 4 | 3 | PASS |
| `main` | 4 | 9 | 11.1 | 4 | 3 | PASS |

No function grade 1 or 2 anywhere in the file.

## F3 — `--check` structurally blind to an ABSENT required door

Added `REQUIRED_DOORS = ("harness.md", "harness-plan.md", "harness-ship.md",
"harness-grilling.md")` and `missing_required_doors()` to `sync-command-adapters.py`. `sync()` now
checks it first and returns a hard exit 1 (both `--check` and `--apply`) naming the missing
door(s), before ever computing `expected_adapters()` — distinct from the existing stale-adapter
drift message. Glob-discovered non-required doors still sync as before.

**BEFORE (verbatim, real doors copied into `/tmp` scratch, UNMODIFIED script, `harness-ship.md`
deleted from both `.omp/commands` and `.claude/commands`):**
```
$ python3 orig-sync-command-adapters.py --root <scratch> --check
EXIT=0
```
(no stdout/stderr at all — false-clean, exactly the F3 defect.)

**AFTER (same scratch scenario, fixed script):**
```
$ python3 sync-command-adapters.py --root <scratch> --check
sync-command-adapters: required canonical door missing from .omp/commands/: harness-ship.md
EXIT=1
$ python3 sync-command-adapters.py --root <scratch> --apply
sync-command-adapters: required canonical door missing from .omp/commands/: harness-ship.md
EXIT=1
```
Scratch dir removed immediately after; `git status --porcelain` confirmed clean of it (see below).

`sync()` grade: was 2 (10/15/27.9, accepted reason on file), now 2 (12/18/31.2, cyclomatic+
cognitive+abc-driven) — moved, not worsened past grade 2; same accepted-reason class (four
responsibilities sharing local state, now five). Not decomposed further: still exempt per the
panel's existing MED/grade-2 reason.

`seed()` in the test file now lays down all four required doors + adapters (previously only
`harness.md`/`harness-ship.md`), so every pre-existing case still exercises the real required set.
Added `case_missing_required_door_fails` (2d) asserting `--check` fails naming the door and
`--apply` also fails.

**F3 second-source-of-truth (2e):** `check-omp-port.py:169`'s inline door tuple is pinned to
`sync-command-adapters.py`'s new `REQUIRED_DOORS` **behaviourally**, not by grepping source text —
`test-check-omp-port.py` now `importlib`-loads `sync-command-adapters.py` at runtime
(`_sync_command_adapters_module()`) and, for each of its four `REQUIRED_DOORS`, builds a fixture
missing exactly that door and asserts `check-omp-port.py` also reports it missing (8 new cases).

## F4 — banner named an unreachable `bin/` path

`BANNER` (and the test file's mirrored `banner()` helper) now reads, exactly:
```
<!-- Generated from .omp/commands/{name}; do not edit. Run .claude/skills/harness/bin/sync-command-adapters.py --apply. -->
```
(single line, trailing newline, as before).

**Consequence, not swallowed:** `sync-command-adapters.py --check` against the REAL tree is now
**RED**, because all four `.claude/commands/*.md` adapters still carry the old banner byte-for-
byte and I did not run `--apply` against `.claude/commands/**` (main-session-owned):
```
$ python3 .claude/skills/harness/bin/sync-command-adapters.py --root . --check
sync-command-adapters: Claude command adapters are stale: harness-grilling.md, harness-plan.md,
harness-ship.md, harness.md
exit 1
```
**Action needed from the main session:** run `--apply` to regenerate those four adapters with the
new banner bytes quoted above.

**Side effect, cycle 1 (superseded by cycle 2 below):** `check-omp-port.py` shells out to
`sync-command-adapters.py --check` against the live tree in its own `test-check-omp-port.py` "live
provider-neutral tree passes" case, so this became newly red the moment the banner changed. Cycle 1
added a tolerance carve-out to that case accepting either a clean run or exactly the four-adapter
banner-staleness message. The lead REJECTED that carve-out (it converts a permanent-hole risk — a
real future stale-adapter regression reading as pass — into the resolution). Cycle 2 removed it
entirely; see "Cycle 2" below for the current, correct state of this case and the suite.

## Unplanned: `test-check-omp-port.py:main()` was ALSO pre-existing code grade 1

Discovered while re-grading after the F3/F4 edits: `main()` in this file was **already** grade 1
(ABC 98.9, confirmed against the pre-edit working-tree copy via `git stash`) — unrelated to this
feature's diff, never flagged by the C2 panel because it wasn't part of that pin's graded set.
Since my F3/F4 edits touch this same function (pushing ABC to 110.0) and leaving a grade-1
function in a file I materially edited would gate the next review pass, I decomposed it too, same
`case_*` convention as F1 (13 case functions + thin `main()`). All pre-existing labels, fixture
shapes, and the `finally: td.cleanup()` pattern preserved verbatim; only shape changed.
AFTER: no function below grade 4 (two land at exactly grade 4 on ABC, everything else grade 5).

## Verification (verbatim exit codes / summaries)

1. `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-sync-command-adapters.py` → **EXIT=0**, `15/15 cases passed`. (Superseded by cycle 2, item 2 below, for `test-check-omp-port.py`.)
2. `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-omp-port.py` → cycle 1 reported EXIT=0/31/31; **this number is invalidated by cycle 2's carve-out removal** — see cycle 2 for the current EXIT=1/30/31 result.
3. `--kind unit` → **EXIT=0**. Four `FAIL` lines, all `BUG-1290 5a/5b/5c/5b(dup)` inside
   `----- test-factory-claim-mutation.py (exit 0, 0.46s) -----`, file itself reports `PASS`
   (its own suite treats these as intentional negative-proof lines) — matches the by-design baseline.
4. `--kind integration` → cycle 1 reported EXIT=1 with exactly the six D-14 `test-check-plan-routes.py`
   cases; **this count is invalidated by cycle 2**, which adds a seventh expected failure
   (`case_live_tree_passes`) — see cycle 2 for the current SEVEN-failure result.
5. `git status --porcelain` → only `.claude/skills/harness/bin/sync-command-adapters.py`,
   `tests/integration/test-check-omp-port.py`, `tests/integration/test-sync-command-adapters.py`
   (all modified), this receipt, and the four pre-existing panel-note files that were already
   untracked before this dispatch started (`review-harness-{code-reviewer,qa,security-reviewer,
   ui-reviewer}-c2.md`). Nothing under `.omp/commands/**` or `.claude/commands/**` touched —
   confirmed untouched, left for the main session's concurrent work.

## Open questions

None blocking. Cycle 1's advisory about removing the carve-out is now resolved — see "Cycle 2"
below.

## Cycle 2 — carve-out removed

The lead rejected cycle 1's tolerance carve-out: it traded a transient condition for a permanent
hole in the gate (a real future four-adapter staleness would read as pass forever, not just during
the pending regen window). `case_live_tree_passes` (`tests/integration/test-check-omp-port.py:64`)
is now a single unconditional assertion again — `clean.returncode == 0`, `clean.stderr` as the
failure detail — with the case label restored to its pre-cycle-1 text (`"live provider-neutral
tree passes"`). `known_pending_banner_regen` and its four-line justification comment are gone,
replaced by a two-line comment recording that the case is expected to fail until the main session
runs `sync-command-adapters.py --apply` to regenerate `.claude/commands/**`. No conditional on
`returncode`, `stderr`, or a door-name list remains.

**1. `test-check-omp-port.py` against the real tree — now honestly RED:**
```
$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-omp-port.py
FAIL  live provider-neutral tree passes — OMP-PORT: Claude command adapters are stale: harness-grilling.md, harness-plan.md, harness-ship.md, harness.md
30/31 cases passed
EXIT=1
```
Every other case in the file still passes — `case_live_tree_passes` is the ONLY failure.

**2. `test-sync-command-adapters.py` — unaffected, still EXIT=0:**
```
$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-sync-command-adapters.py
15/15 cases passed
EXIT=0
```

**3. Scratch-root proof that the red is exactly the pending regeneration and nothing else.**
Seeded a `/tmp` scratch root with `fixture()`'s own shape (copy `.omp`, `.agents`, `.claude`
with `symlinks=True`, plus `AGENTS.md`/`CLAUDE.md`) from the real tree, ran `check-omp-port.py`
against it (RED, identical message), then ran `sync-command-adapters.py --root <scratch> --apply`
**in the scratch only** and re-ran `check-omp-port.py` against the same scratch root (CLEAN):
```
$ python3 .../check-omp-port.py /tmp/omp-port-scratch.LhQeZ5
OMP-PORT: Claude command adapters are stale: harness-grilling.md, harness-plan.md, harness-ship.md, harness.md
EXIT=1

$ python3 .../sync-command-adapters.py --root /tmp/omp-port-scratch.LhQeZ5 --apply
Updated Claude command adapters: harness-grilling.md, harness-plan.md, harness-ship.md, harness.md
APPLY_EXIT=0

$ python3 .../check-omp-port.py /tmp/omp-port-scratch.LhQeZ5
OMP port surface: ok
EXIT=0
```
Scratch dir deleted immediately after (`rm -rf`); confirmed gone (`git status --porcelain` below
carries no scratch reference — it was never tracked, and the directory no longer exists on disk).
`.claude/commands/**` and `.omp/commands/**` in the real tree were never touched.

**4. `--kind unit` — unchanged: EXIT=0**, same four by-design `FAIL` lines in
`test-factory-claim-mutation.py` (BUG-1290 5a/5b/5c/5b-dup), file reports `PASS`.

**5. `--kind integration` — now SEVEN failures, all previously accepted or newly expected:**
the six D-14 baseline cases in `test-check-plan-routes.py` (`case_04_all_granted_exits_0`,
`case_05_ungranted_declared_main_session_exits_0`, `case_15_deviation_plan_still_exits_0`,
`case_17_midpattern_wildcard_grant_exits_0`, `case_19d_explicit_path_unaffected_by_the_root_guard`,
`case_19d2_explicit_path_with_no_tasks_still_exits_0`), confirmed name-for-name by an isolated run
of that file, plus `test-check-omp-port.py`'s `case_live_tree_passes` — no eighth failure.
`run-unit-tests.sh --kind integration` → **EXIT=1**.

**6. `git status --porcelain`** → only `.claude/skills/harness/bin/sync-command-adapters.py`,
`tests/integration/test-check-omp-port.py`, `tests/integration/test-sync-command-adapters.py`
(all modified from cycle 1, unchanged by cycle 2 except the target file), this receipt, and the
four pre-existing untracked panel notes. No scratch dir; `.omp/commands/**` / `.claude/commands/**`
untouched.

**7. Re-grade of `test-check-omp-port.py`** — `case_live_tree_passes` is now grade 5 (down from a
larger body in cycle 1, simpler again). No function in the file is grade 1 or 2.

**Remediation for the main session:** run `.claude/skills/harness/bin/sync-command-adapters.py
--apply` against the real tree to regenerate the four stale `.claude/commands/*.md` adapters with
the corrected banner. `case_live_tree_passes` will then pass unconditionally, with no code change
needed on this side.
