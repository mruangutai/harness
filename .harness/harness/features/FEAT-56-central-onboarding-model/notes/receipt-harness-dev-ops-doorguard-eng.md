# Receipt — harness-dev-ops — doorguard-eng

Advisory validate-phase hardening item (no T-NN, no plan verify). Guards finding F2's defect
class: a canonical door under `.omp/commands/` whose body delegates to `.claude/commands/`
(its own generated output), which two pre-existing checks — `check-omp-port.py:169-171`
(existence only) and `sync-command-adapters.py --check` (byte parity only) — both miss silently.

## Change 1 — new case

Added `case_no_canonical_door_delegates_to_adapter` to
`tests/integration/test-check-omp-port.py` (registered in `CASES`), following the file's
existing convention: a function returning `list[(label, bool, detail)]`.

- Discovers `.omp/commands/*.md` on the REAL tree (module-level `ROOT`, same anchor as
  `case_symlink_topology`/`case_live_tree_passes`).
- Guards the empty case: asserts the discovered set is non-empty AND covers the required set
  loaded at runtime from `sync-command-adapters.REQUIRED_DOORS` (not a hardcoded literal) —
  a zero-match glob now fails this assertion instead of vacuously passing.
- Per-file, one assertion per door: iterates every discovered door and asserts, individually,
  `".claude/commands" not in text`, with the door's own path in both label and failure detail.
  A directory-wide `any()` was explicitly rejected per the dispatch — it would pass on three
  conforming doors and stay blind to the fourth (exactly F2).

One bug caught and fixed during development: `REQUIRED_DOORS` entries already carry the `.md`
suffix (`"harness.md"`, not `"harness"`), so an initial `f"{name}.md"` comprehension produced
`"harness.md.md"` and falsely reddened the coverage assertion on the live tree. Fixed to
`set(_sync_command_adapters_module().REQUIRED_DOORS)` directly; reran clean.

## Change 1 — RED proof (disposable copy)

Copy made via `git archive HEAD | tar -x -C "$TMPDIR"` (mktemp -d), with the uncommitted new
test file copied in over the archived one (archive is HEAD-only and does not carry working-tree
edits). Ran the COPY's own `tests/integration/test-check-omp-port.py` with its own `__file__`-
relative `ROOT`/`_anchor_root`, so both resolved inside `$TMPDIR` — no override needed, the
existing anchor mechanism worked unmodified.

**Pre-mutation control, same copy:** 36/36 cases passed, exit 0 (confirms the copy's baseline
is clean before mutating — the delta below is caused only by the mutation).

**Mutation:** appended a delegation line to the copy's `.omp/commands/harness.md`:
```
See .claude/commands/harness.md for the generated adapter copy.
```

**Post-mutation run, verbatim (relevant lines):**
```
FAIL  live provider-neutral tree passes — OMP-PORT: Claude command adapters are stale: harness.md
...
FAIL  .omp/commands/harness.md does not delegate to .claude/commands — .omp/commands/harness.md references .claude/commands

34/36 cases passed
```
The target case reddened and NAMED the offending door (`.omp/commands/harness.md`) in both
label and detail. The collateral `live provider-neutral tree passes` failure is expected and
separate: appending text also changed the canonical file's bytes, which `sync-command-adapters
--check` (a different, pre-existing mechanism) independently flags as adapter drift — it is not
evidence for or against the new case, which reddened for its own, distinct, correctly-named
reason. All other 32 cases stayed green, i.e. the mutation-caused delta is exactly the two lines
above — no other case regressed.

Copy deleted (`rm -rf "$TMPDIR"`) immediately after. `git status --porcelain` on the real tree
confirmed no leftover run dir (see full listing at the end of this receipt).

## Change 2 — REQUIRED_DOORS composition measurement (no fix)

Second disposable copy, same `git archive` method, deleted immediately after measuring.

1. Shrunk `REQUIRED_DOORS` in the copy's `sync-command-adapters.py` from four entries to three
   (dropped `"harness-grilling.md"`).
2. Deleted the copy's `.omp/commands/harness-grilling.md` and
   `.claude/commands/harness-grilling.md`.
3. Ran both tools against the copy with their root arguments, verbatim:

```
$ python3 sync-command-adapters.py --root "$TMPDIR" --check
(no output)
SYNC_EXIT=0

$ python3 check-omp-port.py "$TMPDIR"
OMP-PORT: .omp/commands/harness-grilling.md is missing; harness-grilling has no provider-neutral door
CHECK_EXIT=1
```

**Prediction HELD.** With `REQUIRED_DOORS` shrunk to three and the fourth door plus its adapter
both deleted, `sync-command-adapters.py --check` is satisfied (exit 0, silent) — its own
required-door list no longer mentions the deleted door, and adapter parity holds trivially since
neither side has it. `check-omp-port.py` still independently catches the same deletion (exit 1,
naming `harness-grilling.md` by name) because its four-door tuple at line 169 is a separate,
hardcoded literal that a `sync-command-adapters.py` edit cannot touch. No fix applied to
`sync-command-adapters.py` in the real tree; this is measurement only, per the dispatch's
explicit instruction not to act on the result.

## Acceptance — item by item

1. New case exists, per-file, guards the empty case, RED-capability demonstrated with the door
   NAMED — see above. ✅
2. `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-omp-port.py` → exit 0,
   **36/36 cases passed** (was 35 cases before this change; +1 new case contributing 2 sub-
   assertions: coverage guard + per-door delegation check for the 4 live doors = the count grew
   by 5 result-tuples but 1 CASES-tuple function). ✅
3. `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-sync-command-adapters.py` → exit 0,
   **15/15 cases passed**, unchanged by this work (proof it was not disturbed). ✅
4. Real tree: `check-omp-port.py` → `OMP port surface: ok`, exit 0.
   `sync-command-adapters.py --check` → exit 0, no output. ✅
5. Both project suites re-run on the real tree via
   `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind <kind>`:
   - **unit**: exit 0. Exactly FOUR `^FAIL ` lines, all in `tests/unit/test-factory-claim-mutation.py`
     (BUG-1290 5a / 5b / 5b-dup / 5c):
     - `FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan`
     - `FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed`
     - `FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path`
     - `FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed` (dup)
     That file itself reports PASS (the runner's per-file rollup is separate from its internal
     by-design cases; matches the D-14 contract, unchanged).
   - **integration**: exit 1. Grep of `^FAIL ` returns 7 lines, of which 6 are case names and 1
     is `run_pool.py`'s per-FILE rollup line (`FAIL test-check-plan-routes.py`, printed
     unconditionally whenever any case in that file fails — confirmed at
     `.claude/skills/harness/bin/run_pool.py:105`, not a 7th distinct case). The 6 case-level
     failures, ALL in `tests/integration/test-check-plan-routes.py`, name-for-name match the
     pinned D-14 set:
     - `case_04_all_granted_exits_0`
     - `case_05_ungranted_declared_main_session_exits_0`
     - `case_15_deviation_plan_still_exits_0`
     - `case_17_midpattern_wildcard_grant_exits_0`
     - `case_19d_explicit_path_unaffected_by_the_root_guard`
     - `case_19d2_explicit_path_with_no_tasks_still_exits_0`
     No seventh case-level failure of any kind. ✅
6. `git status --porcelain` on the real tree, full/unfiltered, after all experiments and both
   disposable copies were deleted:
   ```
    M tests/integration/test-check-omp-port.py
   ?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-doorguard-eng.md
   ?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-code-reviewer-c3.md
   ?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-qa-c3.md
   ?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-security-reviewer-c3.md
   ?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-ui-reviewer-c3.md
   ```
   The four `review-*-c3.md` files are pre-existing untracked notes from sibling review-panel
   agents (present at session start, not written by this task — see `?? ` for reviewer notes
   already in the working tree before any of my edits). No temp artefacts, no `.orig`/`.bak`,
   no leftover run directories from either disposable copy. ✅
7. REQUIRED_DOORS composition measurement reported above with actual tool output; prediction
   HELD. ✅
8. Nothing committed. ✅

## Non-goals honored

Did not write `.omp/commands/**`, `.claude/commands/**`, `bin/**`, or `sync-command-adapters.py`
in the real tree. Did not fix the `REQUIRED_DOORS` hardcoded-literal duplication in
`check-omp-port.py` — measured only, per instruction.
