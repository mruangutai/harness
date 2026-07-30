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

If `.harness/features/<FEAT>/review_sha` exists, diff `base..<review_sha>` instead — reviewing a pinned
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

### 3. Look up required kinds

Read `test_matrix` and `test_kinds` from `.harness/harness.json`. If it is absent, **stop and say so** —
do not invent a matrix.

The matrix is a **floor, not a ceiling**: you may add a requirement the diff clearly warrants. You may
never drop below it.

| Change type | Required |
|---|:---|
| `logic` | unit |
| `api` | unit + functional; integration **if it touches a DB or external service** |
| `cross_module` | unit + functional + integration |
| `frontend` | unit + component; ui **if there is an interaction flow** |
| `feature` | unit + functional + integration + ui |
| `bugfix` | a regression test that **reproduces the bug**, matching the bug's class |
| `ai_behavior` | eval |
| `config` / `scaffolding` / `docs` | exempt |

### 4. Check presence, then run

For each required kind, use its `detect` globs to confirm a test actually covering **this change**
exists. Then run its `cmd`.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because some
other endpoint has a test. Find the test that exercises the changed behavior, or the kind is missing.

### 5. Resolve each kind to exactly one of FOUR states

Collapsing these is how a hard gate silently becomes a no-op — or how it sends you hunting in the wrong
place.

**The discriminator is the FAILURE KIND, not the exit code and not the test count.** Ask: did a *named
test* run and fail its assertion, or did the runner fall over before it could run anything?

| State | Signals | Result |
|---|---|---|
| **satisfied** | at least one named test ran, none failed | contributes to `PASS` |
| **missing** | required kind, and no test covers this change (detect globs find nothing relevant) | **`FAIL`** — name the kind and what needs testing |
| **not applicable** | the tooling genuinely is not present in this project (e.g. `ui` with no Playwright installed) | **soft skip.** Report `ui: skipped (no browser target)` and do **not** FAIL |
| **misconfigured** | `cmd` is `null`/absent; **no test files matched**; or the failure is a **load / import / collection / syntax error** rather than an assertion failure | **`BLOCKED`** — never `FAIL` |

⚠️ **Do NOT use "zero tests collected" as the test for misconfiguration.** It looks like the obvious
signal and it is wrong: **some runners synthesize a failing test out of a load error.** Verified live —
`node --test src/` on Node 26 cannot resolve `src` as a module and reports:

```
Error: Cannot find module '.../src'   code: 'MODULE_NOT_FOUND'
ℹ tests 1      ℹ pass 0      ℹ fail 1
```

**`tests 1`, not `tests 0`.** A count-based rule classifies that as a genuine failure and sends the
reader hunting a bug that does not exist. The load error is the signal; the count is noise.

**Look for these, and treat any of them as `BLOCKED`:**

| Runner | Misconfiguration looks like |
|---|---|
| `node --test` | `MODULE_NOT_FOUND`, `Cannot find module`, `ERR_MODULE_NOT_FOUND`; a "test" whose name is a **path** rather than a description |
| `vitest` | `No test files found`, `Failed to load`, transform/resolve errors |
| `pytest` | `ERROR` (not `FAILED`) lines, `collection error`, `ImportError`, `no tests ran` |
| `jest` | `No tests found`, `Cannot find module`, `SyntaxError` during collection |

A genuine `FAIL` looks different: a **named** test with an assertion diff — *expected X, received Y*.

```
VERDICT: BLOCKED — test command misconfigured for kind 'unit'
  cmd:    node --test src/
  error:  Cannot find module '.../src'   (MODULE_NOT_FOUND, before any test ran)
  cause:  this runner treats `src` as a module, not a directory.
          Fix the cmd in .harness/harness.json — the code is not the problem.
```

**No test files matched, with exit 0, is also `BLOCKED`** — a runner that silently matched nothing has
told you the glob is wrong, and passing on it is exactly the no-op'd hard gate this section exists to
prevent.

Blocking legitimate non-web work on a missing browser would be a bug. Passing a hard gate because its
command was misconfigured is worse than halting.

### 6. Audit test-first discipline

Beyond presence: for each behavioral change, check that a test covers it. Where git history makes it
visible, check the test was written **before** the implementation. Report violations as findings — they
do not by themselves FAIL the gate.

## Output

```
VERDICT: FAIL

Tests for this change
  unit         PASS       14 named tests, all passed   pnpm -C web test
  component    MISSING                                the new filter control has no story test
  python       PASS       31 named tests, all passed   uv run pytest
  integration  BLOCKED    ImportError during collection — cmd misconfigured, not a code bug
  ui           skipped    no browser target in this project

What's needed
  A story test for the author-filter control covering the empty and
  single-author cases. Change type is `frontend`, so component tests are
  required by the matrix.
```

On success, `VERDICT: PASS`, and say which kinds ran and which were legitimately skipped — a PASS that
hides three skips is misleading.

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. It says nothing about whether *this change* is covered |
| "Playwright isn't installed, so I'll fail the ui kind" | Absent tooling is a soft skip, not a failure |
| "The test command errored, I'll skip that kind" | That is `BLOCKED`, loudly. A misconfigured hard gate is worse than a halt |
| "Non-zero exit, so the tests failed" | **Check the failure KIND first.** A load/import/collection error means your `cmd` is broken, not the code. Reporting FAIL sends the reader hunting a bug that does not exist |
| "Zero tests collected means misconfigured" | Not a reliable signal — `node --test` reports `tests 1` for a module-load error. Read the error, not the count |
| "It exited 0, so that kind is satisfied" | Not if no test files matched. A runner that matched nothing is telling you the glob is wrong |
| "There's already a test in that file" | Does it exercise the changed behavior? If not, the kind is missing |
| "This is a small change, the matrix is overkill" | The matrix is a floor. Size is not an exemption; `change_type` is |
| "I'll infer change type from what they asked for" | Infer it from the diff. The diff is the ground truth |
