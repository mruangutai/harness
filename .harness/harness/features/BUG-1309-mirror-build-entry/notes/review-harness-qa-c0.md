# QA gate re-verification — review-c0 — BUG-1309-mirror-build-entry

Pinned at `6f64a21c5df24f8dd17c4f1bcf2c93e10563cf24`. Independent re-run of the test_matrix gate;
authoring qa segment's own PASS (`notes/qa-matrix-gate-BUG-1309-rerun.md`) not reused as evidence —
every number below is freshly measured in this session.

## VERDICT: matrix_ok = true

**Change type & required kinds.** Plan carries 5 change types across 13 tasks: `config` (T-01),
`bugfix` (T-02, T-04, T-06, T-07, T-10, T-12), `feature` (T-03, T-05), `docs` (T-08, T-09),
`scaffolding` (T-11, T-13, disposed by D-10/D-12). Resolving the matrix (`.harness/harness.json:156-240`):
- `bugfix` → `unit` fires (`touches_runtime_code`: all six bugfix tasks touch runtime code).
  `match_bug_class` is the repo's known unresolvable placeholder (no taxonomy entry fires for any
  diff yet) — contributes nothing, per this checkout's own Expertise.
- `feature` (T-03, T-05) → `always: [unit, integration]`, no `ui` (no interaction flow, this is a CLI).
- `config` (T-01) → `github.build_entry` is a brand-new closed enum key nested under `github` in
  `feature-schema.json`, read by three gate scripts (`check-state.sh`, `merge-gate.py`, `gh-sync.py`
  itself) — a structural-nesting change to a config a gate script reads, tripping
  `touches_config_shape` (DEC-212) → `integration` required.
- Combined floor: **{unit, integration}**. Both `active` in `test_kinds` with real `cmd`s.

**Per-kind results, run fresh in this session:**

| kind | cmd | exit | discovered |
|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` (env -u HARNESS_AGENT_TYPE) | 0 | 33 files, 531 `PASS`/`ok` lines, 0 `FAIL` |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 50 files, 3611 `ok`/`PASS` lines, 0 `FAIL`/`not ok` |

Both non-zero discovery, both green. `matrix_ok: true`.

## The three gates' live discovery counts (not just exit code)

- **`check-state.sh` INV-37**: ran live against this checkout (`github.sync: true` in
  `.harness/harness.json`, so the invariant's own guard is open). Direct corpus scan: **75 of 75**
  plan-carrying feature directories in this repo are inside `feature_schema.BUILD_ENTRY_ERA_EXEMPT`
  — **0 objects discovered as violations**, and 0 non-exempt candidates existed to check in the first
  place. `check-state.sh` itself exits 1 (pre-existing, unrelated INV-17/INV-23/INV-28 notes on other
  features — none is INV-37; confirmed by grep, 0 hits).
- **`merge-gate.sh`**: ran live (`git merge feat/BUG-1309-mirror-build-entry`) from inside this exact
  worktree — genuine non-fixture invocation. Result: `allowed... predates the build-entry receipt`,
  correctly resolving this feature by branch and reading it as era-exempt, exit 0. Same corpus fact as
  above: all 75 live features are era-exempt, so **no live "deny" is currently reachable** — the deny
  path is proven only by the fixtures in `test-merge-gate.py`.
- **`post-merge-sweep.sh`**: NOT run live (it mutates/removes worktrees on a real merge — out of
  scope for a read-only audit and explicitly forbidden). Its retention branch is confirmed via
  `tests/integration/test-post-merge-sweep.py`'s 8 T-07 cases + T-13, all `ok`, inside the 50-file/
  exit-0 integration run above.

This 75/75 era-exempt fact is a **verification-scope limitation, not a defect** — BRIEF.md's own
"Verification gaps" section already discloses it (17 sync-enabled legacy features knowingly
unrecovered, forward-only guarantee). Recorded here because it means every "fires"/"denies" behaviour
this gate re-confirms today is proven by synthetic fixtures, never by a live positive discovery in
this tree — worth knowing next time someone treats a clean `check-state.sh` run as proof INV-37 works.

## Adequacy — each named behaviour, and what binds it

- **Build-entry recorder in `open`**: MEASURED, both sides. `test-gh-sync.py`: "T-02 open records
  opened", "T-02 sync false records not-applicable", "T-02 unpinned repo records nothing", "T-02
  first-call failure records recovery-required", "T-02 partial remote write records nothing", "T-02
  second open stays opened / opened never downgrades", "T-02 contract error records nothing".
- **`recover-terminal` idempotency, zero task sub-issues on re-run**: MEASURED directly.
  `test-gh-sync.py:3547-3554` ("T-03 second run is idempotent") asserts
  `len(create_calls(logR4)) == 0` on the SECOND invocation and an unchanged `github.issues` map — an
  exact call-count assertion, not a substring check.
- **`cmd_start_task` Build refusal**: MEASURED for absent/era/recovery-required states (T-04 cases,
  `test-gh-sync.py`). The unpinned-repo variant has no dedicated fixture, but is REASONED-bound, not
  independently measured: `_build_entry_preflight` (`gh-sync.py:1357-1359`) branches only on
  `rec.get("build_entry")`, which D-09 makes ABSENT for an unpinned repo — the identical state "T-04
  non-era absent refuses" already exercises. No separate code path exists for "unpinned" inside the
  preflight, so this is sound inference from source, flagged here per this checkout's own
  observation about reasoned-vs-measured evidence.
- **Closed 5-state enum**: MEASURED. `test-validate-feature-json.py` rejects `'opened '`, `'reopened'`
  and the hyphen misspelling, and accepts all four legal values plus a `github` block without the key.
- **Merge-gate GitHub-read fallback**: MEASURED both branches in `test-merge-gate.py` — gh outage +
  no local-branch match → allow with "could not verify" (:102-103); gh outage + local branch resolves
  to a feature owing a receipt → deny (:107-108). This is the exact D-07 fail-open/local-fallback
  contract, mutated in both directions.
- **Recovery while GitHub unavailable → non-terminal, worktree retained**: bound by COMPOSING two
  independently measured tests across two files rather than one chained scenario: `test-gh-sync.py`
  "T-02 first-call failure records recovery-required" produces the state, `test-post-merge-sweep.py`
  "T-07 recovery-required keeps the worktree" consumes it. No single test drives gh-failure-during-open
  straight into a sweep run in one process. REASONED composition (valid, since both halves are pinned
  to the same `github.build_entry` field contract), not directly measured as one flow.
- **Unpinned repo + `github.sync: true` blocks BOTH halves, records nothing**: MEASURED on both
  halves independently — "T-02 unpinned repo records nothing" (recording half) and "T-05 unpinned
  repo absent build_entry denies naming the configuration fix" (`test-merge-gate.py:68-69`, merge
  half). The Build-block half is the same REASONED inference noted above (absence state is shared).

No behaviour in the signed policy list is fully unbound. The softest spots, in order: (1) INV-37's
"open"-branch message text (`check-state.sh:2012-2016`) is exercised only through the pure
`recovery_command_for() == "open"` unit assertion, never through a captured `check-state.sh` stdout
containing that exact message — a mutation dropping "gh-sync.py open" or the feature path from that
f-string would pass the whole suite; the sibling recover-terminal message IS asserted against captured
stdout (`test-check-state.py:4658-4663`). Severity: low — it is the friendlier, non-blocking half of
the invariant, and the routing decision itself (`recovery_command_for`) is pinned. (2) the two
composed-not-chained bindings above (unpinned-Build-refusal, GitHub-unavailable-retention) — reasoned
sound, not independently reproduced end-to-end.

## SC evidence (verify: automated only; SC-09 is inspection, SC-10 is uat — not qa's)

| SC | test |
|---|---|
| SC-01 | test-gh-sync.py "T-02 second open stays opened" / "opened never downgrades" |
| SC-02 | test-gh-sync.py "T-02 first-call failure records recovery-required", "partial remote write records nothing", "contract error records nothing" |
| SC-03 | test-gh-sync.py T-04 cases ("non-era absent refuses", "BUG-named non-era absent refuses", "station discriminator", "era-exempt continues") |
| SC-04 | test-merge-gate.py denial/allow cases (lines 64-92) |
| SC-05 | test-gh-sync.py:3524 "T-03 recover-terminal creates milestone and parent only", :3551 "T-03 second run is idempotent" |
| SC-06 | test-post-merge-sweep.py T-07/T-13 cases (lines 887-906) |
| SC-07 | test-check-state.py `case_t06_build_entry_invariant` |
| SC-08 | test-validate-feature-json.py enum accept/reject cases |

## Findings (concrete scenario required)

1. **[low]** `check-state.sh`'s INV-37 "open"-branch message (:2012-2016) is untested at the
   integration level — mutating that f-string to drop "gh-sync.py open" or the feature path would
   pass every test in this suite. Scenario: a future edit that renames the remedy verb or truncates
   the path in that one branch ships silently; an operator reading the message gets a broken or
   misleading remedy for a non-terminal feature missing its Build entry. Fix is cheap: one more
   `case_t06_build_entry_invariant` fixture with `station != done/review` and no done tasks, asserting
   the captured line contains `"gh-sync.py open"` and the feature path, mirroring the existing
   recover-terminal-branch assertion.
2. **[info]** All 75 live feature directories in this repo are `BUILD_ENTRY_ERA_EXEMPT`, so INV-37
   and merge-gate's real "deny"/"fires" paths have zero live discovery today — proven only by
   synthetic fixtures. Deliberate per D-08 and already disclosed in BRIEF.md's own "Verification
   gaps"; recorded here as a fact I measured directly (corpus scan + a live, non-fixture
   `merge-gate.sh` invocation against this feature's own branch), not a new gap.

Neither finding gates the matrix; both are advisory.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Matrix satisfied at the pin — unit (33 files) and integration (50 files) both exit 0, non-zero discovery; every signed-policy behaviour is bound (one pair by sound composition rather than a single chained test); one low-severity coverage gap on INV-37's happy-path message text."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 33 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 50 }
  coverage_gaps:
    - "check-state.sh INV-37's 'open' remedy message (the non-terminal, no-done-task branch) is asserted only through the pure recovery_command_for() unit check, never through captured check-state.sh stdout — the recover-terminal sibling branch IS asserted against captured output"
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-gh-sync.py: T-02 second open stays opened / opened never downgrades" }
    - { id: SC-02, test: "tests/integration/test-gh-sync.py: T-02 first-call failure records recovery-required / partial remote write records nothing / contract error records nothing" }
    - { id: SC-03, test: "tests/integration/test-gh-sync.py: T-04 non-era absent refuses / station discriminator / era-exempt continues" }
    - { id: SC-04, test: "tests/integration/test-merge-gate.py:64-92" }
    - { id: SC-05, test: "tests/integration/test-gh-sync.py:3524 T-03 recover-terminal creates milestone and parent only; :3551 T-03 second run is idempotent" }
    - { id: SC-06, test: "tests/integration/test-post-merge-sweep.py:887-906 T-07/T-13 cases" }
    - { id: SC-07, test: "tests/integration/test-check-state.py case_t06_build_entry_invariant" }
    - { id: SC-08, test: "tests/integration/test-validate-feature-json.py enum accept/reject cases" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-qa-c0.md
```
