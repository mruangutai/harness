# QA test-matrix gate — BUG-1290 — re-scoped to the FEATURE diff — 2026-09-06-03-validator

**VERDICT: PASS.** `matrix_ok: true`. `MATRIX-01` from `qa-2026-09-06-02-validator.md` is
**WITHDRAWN**: it was raised against the wrong diff object (the fix cycle's uncommitted delta
only). Re-scoped to the feature's own diff (`merge-base main HEAD` .. `HEAD` + working tree), the
`integration` leg does not even fire — and separately, were it to fire, its presence check is
satisfied outright.

## 1. Corrected diff object, independently re-measured

`git diff --name-only $(git merge-base main HEAD) HEAD` (37 files) plus `git status --porcelain`
(4 modified + 4 untracked, all `.harness/` bookkeeping and this note's siblings). Production
files in the corrected diff:
`.claude/skills/harness/bin/{factory_claim.py,factory_config.py,feature-worktree.py,layout_fixtures.py,layout_migration.py}`
(mirrored byte-identically under `.agents/skills/harness/bin/` — same size/mtime, not a
distinction that matters here). Test files, confirmed present with `--stat`, **matching the
orchestrator's assertion exactly, nothing false**:

```
tests/integration/test-factory-integration.py |  13 +-
tests/integration/test-layout-migration.py    |   9 +-
tests/unit/test-factory-claim-mutation.py     | 151 ++++++++++++++++
tests/unit/test-factory-claim.py              | 238 ++++++++++++++++++++------
```

## 2. `bugfix` predicates resolved against the corrected scope (`harness.json:203-218`)

| predicate | resolution | reason |
|---|---|---|
| `touches_runtime_code` | **true** (flips from the prior run's `false`) | 5 production `bin/*.py` files are in the corrected diff |
| `fix_confined_to_tests_and_contract_docs` | **false** | production code changed; the diff is not confined to tests/docs |
| `match_bug_class` | unresolvable, contributes nothing | no bug-class taxonomy entry fires (repo Expertise G-08), unchanged |

**Floor: `unit` only**, via `touches_runtime_code`. The `integration` leg's own precondition is
false this cycle — it does not fire, full stop.

## 3. `MATRIX-01` disposition — withdrawn, with the measurement, and the two dispositions kept distinct

Per dispatch instruction not to conflate "leg unfired" with "leg satisfied": **the leg does not
fire** under the corrected scope (`fix_confined_to_tests_and_contract_docs = false`), so there is no
`integration` requirement to test presence against at all — this is why `MATRIX-01` is moot, not
"passed."

Separately, and only as additional confirmation: **had** the leg fired, its presence check
(`test_kinds.integration.detect = tests/integration/**`) is unambiguously satisfied — both
`tests/integration/test-factory-integration.py` and `tests/integration/test-layout-migration.py`
are in the corrected diff, and (§4) both are discovered, executed, and pass under
`--kind integration`. Either disposition clears `MATRIX-01`; I report both so the record doesn't
read as "found satisfied" when the truer statement is "leg didn't fire."

**`MATRIX-01`: WITHDRAWN.**

## 4. Required kinds — resolved states, corrected scope

| kind | state | cmd | exit | discovery | tally |
|---|---|---|---|---|---|
| `unit` (required, `touches_runtime_code`) | **satisfied** | `run-unit-tests.sh --kind unit` | 0 | 28 files | `grep -c '^FAIL '` = 3, all inside `test-factory-claim-mutation.py`'s own `MUTANT ACTIVE` block (`BASELINE 3/3 ok` → `MUTATION PROOF: 3/3 cases reddened`) — expected reddening, not a real failure |
| `integration` (not required this cycle; run anyway) | satisfied | `run-unit-tests.sh --kind integration` | 0 | 46 files | `grep -c '^FAIL '` = 0; both changed files present and executed: `----- test-factory-integration.py (exit 0, 15.08s) -----` / `PASS`, `----- test-layout-migration.py (exit 0, 1.68s) -----` / `PASS` |

```
$ env -u HARNESS_AGENT_TYPE run-unit-tests.sh --kind unit
...
----- test-factory-claim-mutation.py (exit 0, 0.49s) -----
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
MUTATION PROOF: 3/3 cases reddened
PASS test-factory-claim-mutation.py
pool: 8 workers, 28 files, 4.46s wall
EXIT=0
```

```
$ env -u HARNESS_AGENT_TYPE run-unit-tests.sh --kind integration
...
----- test-factory-integration.py (exit 0, 15.08s) -----
...PASS test-factory-integration.py
----- test-layout-migration.py (exit 0, 1.68s) -----
...PASS test-layout-migration.py
pool: 8 workers, 46 files, 70.84s wall
EXIT=0
```

`component`/`ui`/`typecheck` — not in the `bugfix` floor, diff touches no such surface: not
applicable. `functional`/`eval` — `status: excluded` (DEC-187): not applicable.
`omp_session_accessor`/`handoff_comprehension` — `locally_run`, diff touches neither surface: not
applicable.

## 5. Carried forward, unchanged — the re-scope does not touch either

- **Test-first compliance** (`qa-2026-09-06-02-validator.md` §4): reasoned finding — the `issues`
  mutant reddens case 5b under the post-edit fixture and does not under the pre-edit fixture,
  the applicable "RED under target mutant, GREEN before the edit" form. This was reasoned from
  mutation adequacy directly, not from diff scope, so the scope correction does not change it.
  **Holds; no violation.**
- **T-01's `verify:`** (`plan.yaml:274-281`): exits 1 with all six `5x` cases `MISSING RED` on both
  this tree and a detached `HEAD` worktree — because T-03 (an earlier cycle) already landed the
  seam, so every case reports `ok`, never a fresh `FAIL`. This is a task-level, ref-pinned check
  independent of how the gate scopes "the diff," so the scope correction **does not move it**.
  Per dispatch instruction, not gated as a failure this cycle.
- Mutation adequacy for REQ-02's issue-map clause (prior run §3): **not re-derived**, per
  instruction — that measurement stands.

## 6. Q2, restated as non-gating (operator backlog, not a finding against this diff)

`test_kinds.integration.detect` keys the required `integration` kind on a directory label
(`tests/integration/**`) rather than on the changed surface. Under the corrected scope this gates
nothing — the leg doesn't fire, and even where it might, both changed files happen to sit under
that directory. But the label-vs-surface mismatch is real and will bite the next fix-only cycle
that touches unit-resident fixtures without touching `tests/integration/**`. Non-gating; for the
operator's harness-config backlog.

## 7. Verdict

`matrix_ok: true`. Floor (`unit`, via `touches_runtime_code`) is satisfied. `integration`'s own
predicate does not fire this cycle; run anyway as supplementary evidence and green regardless.
**VERDICT: PASS.**
