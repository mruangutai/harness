# Code review — BUG-1306, cycle 0, pinned `review_sha` da05ea28

## Verdict: PASS. severity_max: none. must_fix: none.

Stage 1 (spec compliance) passes cleanly, including both `verify: inspection` criteria I own.
Stage 2 (code quality) finds nothing above `info` on the changed hunks. `code-grade.py` reports
`PASSING: 0` / exit 0 over `merge-base(main, da05ea28)..da05ea28` — no gated Python record.

## Stage 1 — spec compliance

### SC-04 — PASS

Cited against `git show da05ea28:tests/integration/test-plan-merge.py` (NOT the on-disk path,
per G-01 — the on-disk path under the wrong cwd resolved to the *main checkout's* pre-fix copy
on my first attempt and gave stale line numbers; re-run against the absolute worktree path
matched `git show` exactly):

- Pop: `os.environ.pop("HARNESS_AGENT_TYPE", None)` — **line 41**, module scope, immediately
  after the six-line comment, before `RESULTS = []` (line 43).
- It is `.pop(..., None)`, not `del os.environ[...]` — confirmed by reading the line itself.
  `del` would raise `KeyError` on every CI run (`.github/workflows/tests.yml` runs this suite
  with no `HARNESS_AGENT_TYPE` set); `.pop(..., None)` degrades to a no-op instead. Correct
  choice, matches D-02.
- First case-function definition: **line 165** (`def case_proposal_indent_differs_from_base`) —
  the pop at line 41 lexically precedes every case body, no exceptions (confirmed by listing
  every `def case_*`/`run_apply`/`run_verb` def line from 137 through 2013; none precede 41).
- The two raw `Popen` call sites are at **lines 315 and 319** (inside `case_concurrency_real`),
  both after line 41.

One documentation drift, not a defect: BRIEF/plan text says "near lines 305/309" for the Popens.
At `review_sha` they are actually at 315/319 — a +10 shift caused by the fix's own 8-line
comment/pop block plus the 2-line net growth of the `run_verb` docstring edit, both of which sit
*before* the Popens in the file. Order is unaffected (41 < 315 < 319); flagging only because a
future reader diffing against the BRIEF's literal numbers might be confused. Not gating.

### SC-05 — PASS

`git diff --name-only $(git merge-base main da05ea28) da05ea28` — verbatim:

```
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/STATE.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/handoff-build.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/handoff-plan.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/qa-BUG-1306-integration.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-backend-dev-T-01-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-backend-dev-simplify-reuse-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-backend-dev-simplify-simplification-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-dev-ops-simplify-altitude-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-dev-ops-simplify-efficiency-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/research-BUG-1306-goalcheck-plan-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-code-reviewer-planpanel-c0.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/observations/harness-orchestrator.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/observations/harness-pm.md
.harness/harness/features/BUG-1306-agent-type-hermetic-tests/plan.yaml
tests/integration/test-plan-merge.py
```

Every path is either `tests/integration/test-plan-merge.py` or under this feature's own
`.harness/harness/features/BUG-1306-agent-type-hermetic-tests/`. No path under
`.claude/skills/harness/bin/` or `.agents/skills/harness/bin/`. No second test file.

### REQ-03 — PASS

`.claude/skills/harness/bin/plan-merge.py` is absent from the changed-path list above (proved
from the diff, not from reading the file's current text). Read the cited line for accuracy only:
`plan-merge.py:1188` is `_signing_agent = os.environ.get("HARNESS_AGENT_TYPE") or ""` — the
comment's line citation is correct, and no test-mode bypass exists anywhere in that file's diff
(there is no diff — the file is untouched).

### REQ-01/REQ-02 — PASS (judged from diff + qa-BUG-1306-integration.md, execution not duplicated)

Diff is exactly the two hunks shown below (`git diff -U0 bfb77f23 da05ea28`): a module-level
pop with comment (pre-image line 34) and a three-line docstring addendum to `run_verb` (pre-image
line 141). qa's independently-measured record (both endpoints: pre-fix `bfb77f23`-content in an
isolated worktree at 14 FAIL/exit 1; post-fix at `7e38d0ae` — same test-file bytes as `da05ea28`
— governed run 0 FAIL/exit 0 with both #1103 PASS lines present, clean-env run 0 FAIL/exit 0)
satisfies SC-01/02/03, hence REQ-01/REQ-02. Not re-run here per dispatch instruction.

### Plan-decision compliance

- **D-01** — no shared helper, no second test file: confirmed by the SC-05 path list above.
- **D-02** — pop at module import (line 41), comment names `plan-merge.py:1188` correctly (verified
  against the actual line), `run_verb` docstring gained the specified sentence: confirmed.
- **D-03** — `plan-merge.py` untouched: confirmed (absent from changed-path list).
- **D-05** — no new case added: confirmed. `git diff -U0 bfb77f23 da05ea28 -- tests/integration/test-plan-merge.py`
  shows exactly two hunks, both outside every `def case_*` body; the `CASES`/dispatch list is
  untouched.

### PF-15e50cd4137f8309fac4057506bd40a5 — byte-identity confirmation (standing gap, T-01's
reviewer-confirmation remedy)

**Confirmed identical.** Method, independently reproduced (not inferred from the green suite, not
from unchanged `check()` name strings, and not from trusting the sha1 the build handoff cited
without stating its own derivation):

1. **Hunk-range analysis.** `git diff -U0 bfb77f23 da05ea28 -- tests/integration/test-plan-merge.py`
   produces exactly two hunks: `@@ -34,0 +35,8 @@` and `@@ -141 +149,3 @@`. Both pre-image anchors
   (34, 141) are well before the pre-image `case_1103_` region (1097-1140); neither hunk's range
   intersects it. This independently confirms the build handoff's claim of "exactly 2 hunks, at
   pre-image lines 34 and 141" — I did not take that claim on faith, I re-derived it.
2. **Direct byte diff of the extracted region**, accounting for the cumulative +10 line shift the
   two hunks impose on everything after them (+8 from hunk 1, net +2 from hunk 2's 1-line-for-3
   replacement): `diff <(git show bfb77f23:… | sed -n '1097,1140p') <(git show da05ea28:… | sed -n '1107,1150p')`
   — empty diff. Both `case_1103_` bodies (`case_1103_sign_approval_refuses_a_governed_agent` at
   pre-image 1097/post-image 1107, `case_1103_sign_approval_negative_control_absent_is_main_session`
   at pre-image 1120/post-image 1130) are byte-identical.
3. Read both bodies at `review_sha` directly: the positive case still explicitly sets
   `env=dict(os.environ, HARNESS_AGENT_TYPE="harness-pm")` and asserts `rc == 10`; the negative
   control still filters `HARNESS_AGENT_TYPE` out of its own explicit env dict and asserts
   `rc == 0` plus the signature landing. Both are semantically live, not merely byte-preserved.

## Stage 2 — code quality (changed hunks only)

No `must_fix`. No fail-open branches introduced — the diff adds one unconditional module-level
statement and prose; it introduces no new conditional, no new error path, and no new lookup that
could miss.

- **`run_pool.py` isolation, confirmed by reading the file, not assumed:** `run_one()`
  (`.agents/skills/harness/bin/run_pool.py:59-63`) calls
  `subprocess.run([sys.executable, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)`
  once per test file, with no `env=` argument — each test file is its own OS process inheriting a
  snapshot of `run_pool.py`'s own environment at spawn time. An `os.environ.pop(...)` executed
  inside `test-plan-merge.py`'s own process can only mutate that process's private environ; it has
  no channel back into `run_pool.py`'s environ or into any sibling test file's already-spawned (or
  not-yet-spawned) process. DEC-211's parallel-suite contract holds.
- **In-process imports of production code, checked, not assumed:** `test-plan-merge.py` loads
  `plan-merge.py` in-process twice via `importlib.util` — `case_amend_v3_identity_check_is_live`
  (~line 1671) and the `_load_pm()` helper (~line 1923, used by `case_amend_f2_under_lock_hash_is_pinned`).
  Read both call sites: they exercise `_verify_amend` and `_require_locked_hash` respectively,
  neither of which reads `HARNESS_AGENT_TYPE` or calls `cmd_sign_approval`. The module-level pop
  in the test file's own process is therefore inert for these two paths — consistent with the
  plan panel's already-recorded dismissal ("neither reaches cmd_sign_approval").
- `code-grade.py --base $(git merge-base main da05ea28) --head da05ea28` → `PASSING: 0`, exit 0.
  The diff touches no function body whose complexity moved; `code_grade: pass` (a Python file did
  change, so this is not `n_a`).

## Findings

- id: F-INFO-01, severity: info, summary: BRIEF/plan cite the raw-Popen call sites as "near lines
  305/309"; at `review_sha` they are 315/319 (a +10 shift from the fix's own inserted lines,
  which sit textually before them). Failure scenario: none — order is unaffected and SC-04 does
  not depend on the exact absolute number, only on lexical precedence, which holds. Recorded so a
  future reader diffing against the BRIEF's literal numbers isn't puzzled; not gating, no
  must_fix.

## code_grade

`pass` — `code-grade.py` ran clean (`PASSING: 0`, exit 0) over `merge-base(main, da05ea28)..da05ea28`;
no gated record, no `SEVERITY:` line.
