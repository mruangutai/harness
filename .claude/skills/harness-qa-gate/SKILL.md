---
name: harness-qa-gate
description: Enforce the test matrix against a diff — infer change type, determine required test kinds, verify they exist, run them, and PASS or FAIL. Use before shipping, before merging, when asked whether a change is adequately tested, or when asked to run the tests for a change.
user-invocable: false
---

# Harness: QA Gate

Decide whether a change is adequately tested, **against the diff — never against a self-report**.

This is a **gate**, not advice. It returns `PASS`, `FAIL`, or `BLOCKED`. A missing required test kind is
a `FAIL` even when the suite that does exist is green — and a test command that cannot run is `BLOCKED`,
never a pass and never a `FAIL`.

## Process

### 1. Establish the diff

```bash
git merge-base HEAD <base>            # base is usually main/master
git diff --stat <merge-base>..HEAD
git diff <merge-base>..HEAD
```

If `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/review_sha` exists, diff `base..<review_sha>` instead — reviewing a pinned
SHA, not a moving `HEAD`.

### 2. Classify each changed path

Assign **one** change type per logical change. Judge from the diff, not from a task description.

| Change type | Looks like |
|---|---|
| `logic` | pure functions, utilities, algorithms, transforms |
| `api` | endpoints, services, handlers, business logic |
| `cross_module` | changes crossing module or process boundaries |
| `frontend` | components, styling, client state |
| `feature` | UI **and** API together |
| `bugfix` | a defect repair, whatever layer |
| `ai_behavior` | prompts, model calls, agent definitions, tool definitions |
| `config` / `scaffolding` / `docs` | build config, deps, generated scaffolding, documentation |

**A `config` change that alters a value's SHAPE — a key's container type, required-ness, or
structural nesting in `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json` or `fleet.yaml`, or any config a gate script reads — is
still `config`, but trips the `touches_config_shape` predicate (DEC-212).** Changing `stations` from
a mapping to a list is shape; bumping `max_total_runs` from 20 to 25 is not. A shape change has a
consumer blast radius no test scoped to the producing module can see — issue #1033 shipped exactly
this, unit-green, while `check-state.py`'s own INV-26 block and `board_lifecycle.py` threw a
`TypeError` against it.

### 3. Look up required kinds

Read `test_matrix` and `test_kinds` from `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`. If it is absent, **stop and say so** —
do not invent a matrix.

The matrix is a **floor, not a ceiling**: you may add a requirement the diff clearly warrants. You may
never drop below it.

The matrix in `harness.json` is the authority — apply it as read, never restate or paraphrase it
(a hardcoded copy here has already drifted from the config once). For `bugfix`, the required test
is a regression test that **reproduces the bug**, matching its class.

### 4. Check presence, then run

For each required kind, use its `detect` globs to confirm a test actually covering **this change**
exists. Then run its `cmd`.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because some
other endpoint has a test. Find the test that exercises the changed behavior, or the kind is missing.

**The `ui` kind is an evidence gate, not a test count (FEAT-1821 SC-10/SC-11).** Its runner writes
`<feature>/runs/<run-id>/ui/results.json` and WebP screenshots; you never trust that reporter on its
own. For every `ui` obligation:

1. Bind the feature id and the validate run id you are grading, and take the pinned `review_sha` —
   that is the served-bundle commit the evidence must name.
2. Run the configured `cmd` with `HARNESS_UI_FEATURE=<feature> HARNESS_UI_RUN_ID=<run-id>` so the
   bundle lands under that run.
3. Independently judge the bundle against the **committed** `DESIGN.md`:
   `python3 <HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/ui_contract.py gate --design <feature>/DESIGN.md --results <feature>/runs/<run-id>/ui/results.json --feature <feature> --run-id <run-id> --served-bundle-commit <review_sha> --client-package <HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/dashboard/client --changed <path>…`
   with one `--changed` per path in the diff. It re-parses the `## Checks` table itself — a results
   file never supplies its own list of checks — and prints `UI GATE: PASS|FAIL` with every reason.

`FAIL` from the gate is the kind's result, verbatim: a missing runner, a contract-parser refusal, a
listed check with no record or two records at an applicable project, a spec title that is not
byte-identical to its Checks row, absent or empty or non-WebP evidence, a stale
`served_bundle_commit`, incomplete `listed/applicable/observed/missing` accounting, an inspection row
reported `passed` instead of `evidence`, or a summary that hides a failed record. **Any change under
the dashboard client package requires the package's whole Checks table and every spec title present
in its e2e specs** — a shared component is never classified by route, so it cannot evade coverage
(D-04). No `## Checks` table for a `has_interaction_flow` change is `FAIL`, never a skip.

### 5. Resolve each kind to exactly one of FIVE states

Collapsing these is how a hard gate silently becomes a no-op — or how it sends you hunting in the wrong
place.

**The discriminator is the FAILURE KIND, not the exit code and not the test count.** Ask: did a *named
test* run and fail its assertion, or did the runner fall over before it could run anything?

| State | Signals | Result |
|---|---|---|
| **satisfied** | at least one named test ran, none failed | contributes to `PASS` |
| **missing** | required kind, and no test covers this change (detect globs find nothing relevant) | **`FAIL`** — name the kind and what needs testing |
| **not applicable** | the tooling genuinely is not present in this project **and the kind is not `ui`** (e.g. an `eval` kind in a project with no model calls) | **soft skip.** Report `<kind>: skipped (<reason>)` and do **not** FAIL. **`ui` never soft-skips:** a `has_interaction_flow` change with no browser runner, no `## Checks` table or no evidence bundle is `FAIL` (FEAT-1821 SC-10) |
| **locally-run** | the kind's `test_kinds` entry carries `status: "locally_run"` (issue #1187) — a real, working `cmd`, but one that structurally cannot run in CI (needs a host and live credentials the checkout does not have) | **not FAIL, not a soft skip.** Confirm the change actually touched this kind's `detect` surface, then require a recorded run: a note under the feature's `notes/` naming who ran it, when, and the result. No note for an in-scope surface is `BLOCKED — locally-run kind '<kind>' has no recorded run`, never silently PASS |
| **misconfigured** | `cmd` is `null`/absent; **no test files matched**; or the failure is a **load / import / collection / syntax error** rather than an assertion failure | **`BLOCKED`** — never `FAIL` |

A `locally-run` kind is never `missing` (that would FAIL the gate for something CI is structurally
unable to run) and never `not applicable` (that would mean no obligation exists at all, when one does —
it is just discharged by a human on a credentialled host rather than by CI). It is its own state because
neither of those two is honest about what actually happened.


⚠️ **Do NOT use "zero tests collected" as the test for misconfiguration** — some runners synthesize
a failing test out of a load error (`node --test` reports `tests 1 / fail 1` on `MODULE_NOT_FOUND`).
The failure kind is the signal; the count is noise.

**Look for these, and treat any of them as `BLOCKED`:**

| Runner | Misconfiguration looks like |
|---|---|
| `node --test` | `MODULE_NOT_FOUND`, `Cannot find module`, `ERR_MODULE_NOT_FOUND`; a "test" whose name is a **path** rather than a description |
| `vitest` | `No test files found`, `Failed to load`, transform/resolve errors |
| `pytest` | `ERROR` (not `FAILED`) lines, `collection error`, `ImportError`, `no tests ran` |
| `jest` | `No tests found`, `Cannot find module`, `SyntaxError` during collection |

A genuine `FAIL` looks different: a **named** test with an assertion diff — *expected X, received Y*.

A misconfigured cmd returns `VERDICT: BLOCKED — test command misconfigured for kind '<kind>'`,
naming the cmd, the error, and the fix location (`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`) — the code is not the problem.

**No test files matched, with exit 0, is also `BLOCKED`** — a runner that silently matched nothing has
told you the glob is wrong, and passing on it is exactly the no-op'd hard gate this section exists to
prevent.

Blocking legitimate non-web work on a missing browser would be a bug — which is why the `ui` obligation
only exists on a `has_interaction_flow` change. Once it exists, it is discharged by evidence or it
fails. Passing a hard gate because its command was misconfigured is worse than halting.

### 6. Audit test-first discipline

Beyond presence: for each behavioral change, check that a test covers it. Where git history makes it
visible, check the test was written **before** the implementation. Report violations as findings — they
do not by themselves FAIL the gate.

### 7. Collect fail-first evidence — this one gates

For every SC marked `verify: automated`, name the test that discharges it **and the evidence that it
failed before the fix**: the path of the captured failing run, or the receipt line that records it
(`tests/unit/test-foo.py: 1 failed at 3f2a9c1~1`). Where the fix and its test landed in one commit,
reproduce the red state in a worktree — revert the production change, run the test, capture the
output, restore — and cite that capture.

**A green suite with no fail-first evidence is `FAIL`, not `PASS` (FEAT-59 SC-17).** Passing proves
the tests pass today; only a recorded red run proves they constrain anything. The digest carries this
as `fail_first`, and `validate-digest.py` rejects `VERDICT: PASS` with `matrix_ok: true` and an empty
`fail_first`. Only `matrix_ok: n/a` — no gate ran — may carry `[]` truthfully.

## Output

```
VERDICT: FAIL

Tests for this change
  unit         PASS       14 named tests, all passed   pnpm -C web test
  component    MISSING                                the new filter control has no story test
  python       PASS       31 named tests, all passed   uv run pytest
  integration  BLOCKED    ImportError during collection — cmd misconfigured, not a code bug
  ui           FAIL       UI GATE: FAIL — no record for C1-HEADER-GEOMETRY at desktop-1920
  omp_session_accessor  locally-run   not on this diff's touched surface — no run required

What's needed
  A story test for the author-filter control covering the empty and
  single-author cases. Change type is `frontend`, so component tests are
  required by the matrix.
```

On success, `VERDICT: PASS`, and say which kinds ran and which were legitimately skipped — a PASS that
hides three skips is misleading.

The DIGEST block that travels with the verdict is specified in `harness-verification-rules`; the field
this gate adds is:

```yaml
fail_first: [{ sc: SC-01, evidence: "<path or receipt line>" }]   # one per `verify: automated` SC
```

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. It says nothing about whether *this change* is covered |
| "Playwright isn't installed, so I'll skip the ui kind" | On a `has_interaction_flow` change, `ui` never skips: no runner, no `## Checks` table or no evidence bundle is `FAIL` (SC-10) |
| "results.json says every check passed, so ui is satisfied" | The reporter is not the gate. Run `ui_contract.py gate`; it re-reads DESIGN.md and checks the WebPs and the bundle pin |
| "Only one tile component changed, I'll require just that surface's checks" | Any change under the client package requires the whole Checks table (D-04). Shared components are why |
| "The test command errored, I'll skip that kind" | That is `BLOCKED`, loudly. A misconfigured hard gate is worse than a halt |
| "Non-zero exit, so the tests failed" | **Check the failure KIND first.** A load/import/collection error means your `cmd` is broken, not the code. Reporting FAIL sends the reader hunting a bug that does not exist |
| "Zero tests collected means misconfigured" | Not a reliable signal — `node --test` reports `tests 1` for a module-load error. Read the error, not the count |
| "It exited 0, so that kind is satisfied" | Not if no test files matched. A runner that matched nothing is telling you the glob is wrong |
| "There's already a test in that file" | Does it exercise the changed behavior? If not, the kind is missing |
| "This is a small change, the matrix is overkill" | The matrix is a floor. Size is not an exemption; `change_type` is |
| "I'll infer change type from what they asked for" | Infer it from the diff. The diff is the ground truth |
| "I can't run it in CI, so I'll skip that kind" | Check `test_kinds.<kind>.status` first. `locally_run` is not `not applicable` — it needs a recorded run, not silence |
| "The suite is green and the tests exist, so PASS" | Green with no recorded red run is `FAIL`. `fail_first` names, per automated SC, the evidence the test failed before the fix |
