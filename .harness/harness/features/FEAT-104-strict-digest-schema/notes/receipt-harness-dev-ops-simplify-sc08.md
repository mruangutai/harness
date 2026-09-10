# Receipt — harness-dev-ops — simplify/efficiency — SC-08 assertion delta

**BLUF: the delta added zero work — it is the weakest sufficient form as written.** No new subprocess
invocation, no new fixture materialization, no new I/O; the two added clauses read an
already-captured attribute. `applied: none`, `would_have_applied: false`.

## Diff under review (168f875f..790023f0, verified via `git diff`)

`tests/integration/test-check-domain.py:82-90` (`_undeclared_cases()`), version-2 case only:
- Case name: `"...names it"` → `"...names it and gives its route"`.
- Added two `and`-clauses to the existing boolean: `"run-state-schema.json" in strict.stderr` and
  `` "`evidence`" in strict.stderr ``.

## 1. Subprocess / fixture count — before vs after

- `strict = _fire_new(...)` at `test-check-domain.py:80-81` is unchanged and appears **once**,
  identically at both revisions (confirmed by `git diff`, which touches only the return-list
  literal at lines 82-90, not the call above it).
- `strict` (a `subprocess.CompletedProcess`, per `check_domain_support.py:111-115`'s `fire()`) is
  bound **once** before the returned tuple is built. The two new clauses read `strict.stderr` —
  already-captured `str` from that one completed call — via plain `in` substring tests.
- Subprocess invocations per case: **1 before, 1 after.** Fixture materializations per case
  (`fixture(FIXTURE_MANIFEST)` inside `_fire_new`, `check_domain_support.py:30`, called once per
  `_fire_new` call): **1 before, 1 after.**
- No re-fire, no second `fire()`/`fixture()` call, no loop. This matches
  `_declared_shape_case()` (`test-check-domain.py:117-120`) doing genuine extra I/O — a fresh
  `open(...)` + `json.load` on `run-state-schema.json` for a *different purpose* (schema-key
  membership) — as a contrast: the SC-08 clauses do nothing structurally similar; they are two
  more `in` checks on a string already in memory.

## 2. Per-case I/O / re-read / extra fixture setup

None. The two new clauses do zero I/O. They assert that the *emitter's own output* mentions the
schema file's route (`run-state-schema.json`) and the `` `evidence` `` recovery field, both of
which `check-domain.sh:1653-1659` prints unconditionally from strings already built during the one
call. No schema file is opened by the test to construct the assertion.

## 3. Cost verdict

This is a one-shot build/validate case file (12 cases, ~1.2s wall for the whole file, measured via
`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py`, all 12 passing
including the target case), not a hot path or per-write gate. **Nothing to flag — no invented
cost.** Empty findings is the expected and accurate outcome for this angle.

## Carried forward, not re-raised

Standing Q7 (predicate-spelling residual across `check-domain.sh`/`check-state.sh`) — out of scope
for this delta, already open and accepted.

## Verification

- `git diff 168f875f..790023f0 -- tests/integration/test-check-domain.py` — read to confirm exact
  delta shape (shown above, verbatim).
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` — 12/12 passed,
  `ALL PASSED`.
- `git status --porcelain` after this run — empty, no tracked modifications.

```yaml
VERDICT: PASS
DIGEST:
  headline: SC-08 delta adds zero subprocess/fixture work — two added clauses read an already-captured stderr string; weakest sufficient form as written
  angle: efficiency
  findings: []
  applied: none
  would_have_applied: false
  subprocess_count_before: 1
  subprocess_count_after: 1
  fixture_materializations_before: 1
  fixture_materializations_after: 1
  weakest_sufficient_form: "yes — the assertion is the weakest sufficient form; no cost to trim"
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-dev-ops-simplify-sc08.md
```
