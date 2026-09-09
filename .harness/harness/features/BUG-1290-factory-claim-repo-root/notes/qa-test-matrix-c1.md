# QA test-matrix gate — BUG-1290 — cycle 1

**VERDICT: PASS.** Diff `4e52d2e3..419614e5` clears the `bugfix` matrix floor (unit + integration, both
resolved to `active`, both run, all suites and both kind commands green), test-first holds for T-01/T-02,
and every SC has named, run evidence. Two hard-look items (step 5) both check out on direct inspection,
not exit code alone.

## Change type & matrix resolution

Inferred type: **bugfix** (matches plan's `change_type` on all 5 tasks — a source-derivation resolution
rule, no cache/state migration, no new endpoint/UI). `bugfix` row (`harness.json:203-219`), each `when`
resolved against the diff itself:

| predicate | resolution | kind pulled |
|---|---|---|
| `touches_runtime_code` | **true** — `factory_config.py`, `factory_claim.py`, `feature-worktree.py`, `layout_migration.py`, `layout_fixtures.py` are all production | `unit` |
| `fix_confined_to_tests_and_contract_docs` | **false** — 5 production files changed, not test/doc-only | `integration` not pulled by this leg |
| `match_bug_class` | unresolvable — no bug-class taxonomy entry fires for any diff yet (repo Expertise G-08); placeholder, contributes nothing | none |

Floor from `bugfix` alone: `unit` only. **QA adds `integration`** (floor is a floor, not a ceiling):
REQ-07/SC-07/SC-09 explicitly require `tests/integration/test-factory-integration.py` and
`test-layout-migration.py`, and `test-feature-worktree.py` drives `resolve_repo` through the CLI as a
subprocess — behavior a source scan cannot see. All three are `tests/integration/**`, which the
`integration` kind's `detect` already covers and `run-unit-tests.sh --kind integration` already lists
(confirmed by running it, see below) — no gap between "should run" and "kind command runs it."

## Required kinds — resolved states

| kind | state | evidence |
|---|---|---|
| `unit` | **satisfied** | `run-unit-tests.sh --kind unit` exit 0; `test-factory-claim.py` 124/124 ok, `test-factory-claim-mutation.py` both markers present (its 3 `FAIL` lines are the mutation proof's *own* expected reddening, not real failures — verified in raw output at `/tmp/qa_kind_unit.out:751-756`) |
| `integration` | **satisfied** | `run-unit-tests.sh --kind integration` exit 0, zero `^FAIL ` lines, 46 files, 65.4s wall |
| `component`/`ui`/`typecheck` | not applicable | `unresolved` in `test_kinds`, not in the `bugfix` floor, diff touches no `.tsx`/e2e/component surface |
| `functional`/`eval` | not applicable | `status: excluded`, signed `DEC-187`; not in `bugfix` floor either |
| `omp_session_accessor`/`handoff_comprehension` | not applicable | `locally_run`; diff does not touch `inflight_registry.py` session-file resolution or the handoff contract — outside their `detect` surface |

`matrix_ok: true`.

## Exact commands + real output (trimmed)

```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py
... BUG-1290 5a..5f all "ok"
124/124 checks passed.

$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a / 5b / 5c
MUTATION PROOF: 3/3 cases reddened

$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-factory-integration.py
... (F) claim/workspace/land all ok, (H) all three legs ok
131/131 checks passed.

$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-layout-migration.py
... case 1..22 all ok, EXIT=0

$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-feature-worktree.py
... all PASS lines, ends "PASS test-feature-worktree.py"

$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit
EXIT=0; grep -c '^FAIL ' = 3 (all three are the mutation proof's own reddening, confirmed by line context)

$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
EXIT=0; grep -c '^FAIL ' = 0; 46 files, 65.7s wall
```

## Test-first audit (commit order + reconstructed RED)

Order: `0054108d` (T-01 tests) → `dd7b664b` (T-02 fixtures) → `cd6d843d` (T-03 production) →
`c0959c6c` (T-04) → `61b62343` (T-05). Tests precede the production fix. Reconstructed rather than
trusted:

- Disposable worktree at `0054108d` (`.claude/worktrees/qa-bug1290-t01check`, added via
  `git worktree add --detach` per DEC-153 — bash-write-guard refuses a worktree outside
  `.claude/worktrees/`, confirmed) running `tests/unit/test-factory-claim.py` against **pre-T03**
  production: all six `BUG-1290 5a..5f` cases print `FAIL`. Genuine RED, not a vacuous 5d/5e/5f pass.
- Disposable worktree at `dd7b664b` (`.claude/worktrees/qa-bug1290-t02check`) running
  `tests/integration/test-factory-integration.py`: `12 of 125 FAILING`, including every `(F)` claim/
  workspace/land line and both `(H)` claim/land lines — exactly the markers T-02's `verify:` names.

**Test-first HOLDS** for both T-01 and T-02; not partial.

*(Two disposable worktrees remain at `.claude/worktrees/qa-bug1290-t01check` and
`.../qa-bug1290-t02check` for the orchestrator/main session to remove from outside them — not my act
per the handoff contract.)*

## SC cross-check

| SC | evidence |
|---|---|
| SC-01 | `test-factory-claim.py` case `BUG-1290 5a` — ok |
| SC-02 | case `5b` — ok |
| SC-03 | case `5c` — ok |
| SC-04 | case `5d` — ok |
| SC-05 | case `5e` — ok |
| SC-06 | case `5f` — ok |
| SC-07 | `test-factory-integration.py` `(F)` claim/workspace/land + `(H)` legs — all ok |
| SC-08 | `test-factory-claim-mutation.py` — `BASELINE 3/3 ok` + `MUTATION PROOF: 3/3 cases reddened`, mutant confirmed reached (see hard-look below) |
| SC-09 | `test-layout-migration.py` case 22 (CLEAN, migrated) **plus** T-04's own reader-row probe, run directly by me: `READER ROW PROBE: ok 5 {...factory_config.py: 'migrated'...}`, exit 0 — 5 rows, `factory_claim.py` absent, `factory_config.py` migrated, legacy pattern matches legacy control and not migrated control, migrated pattern matches migrated control |

## Hard-look findings (step 5)

1. **`test-factory-integration.py` has one global `FAILS` counter, no case selection.** Verified by
   grep: single `FAILS = 0` / one `sys.exit(1 if FAILS else 0)`. Did NOT rely on exit code — read the
   named `(F)` and `(H)` `ok` lines directly (12 distinct lines, listed above) confirming both claim
   cases individually pass, not merely that the file as a whole exited 0.
2. **`test-factory-claim-mutation.py` mutation seam.** Read the file directly: `_MutantFactoryConfig`
   wraps the real `factory_config` module, intercepting only `features_root` and discarding
   `repo_name` in favor of a fixed fleet name (`real.features_root(FIXED_FLEET_NAME)`) — exactly the
   `factory_config.features_root` seam, discarding the repo argument, the "post-change equivalent of
   the deleted hardcode" the brief names. `reached()` is asserted (`if not reached: MUTANT NEVER
   REACHED`), and my own run printed `MUTANT ACTIVE` before the three `FAIL` lines, confirming the
   mutant actually entered the seam rather than being bypassed. Baseline and mutated runs differ only
   in that one patched attribute (monkeypatch/restore around `_run_suite()`), so the three reddened
   cases (`5a`/`5b`/`5c`) are attributable to the mutation, not an unrelated import/fixture fault.

## Matrix gaps

None. Nothing to route back to a task.
