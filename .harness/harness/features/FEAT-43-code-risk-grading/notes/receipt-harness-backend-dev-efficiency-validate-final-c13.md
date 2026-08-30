# EFFICIENCY receipt — FinalFeat43Cycle.IcyBadger.SimplifyEfficiency — validate-final-c13

BLUF: The `code_grade` import cost is small and, more importantly, **not comparable to
anything before it** — the committed baseline shells `git diff` on unvalidated
`base`/`head` strings with zero revision resolution. R-01 didn't relocate duplicated
work; it added new, forced validation work at a seam that previously had none. One real
finding: the import is paid on *every* `validate-digest.py` invocation (all personas) though
`commit_oid` is only reachable on one narrow branch. Nothing here rises to `must_fix`.

## 1. Import-cost measurement (required deliverable)

**Command** (mirrors validate-digest.py's real load order — `subprocess` is already
imported at its own line 25 before `harness_boundary`/`harness_yaml`/`code_grade` load, so
`subprocess`'s own transitive cost, ~4.2ms, is *not* new and is excluded):

```
python3 -X importtime -c "
import sys, re, os, json, subprocess
import harness_boundary
import harness_yaml
import code_grade
from gate_policy import GatePolicyError
"
```
Cumulative `code_grade` line, 3 runs: **8265us, 8199us, 8326us → ~8.3ms**.

**Baseline, one full hook invocation** (`code_grade.py:1-388` structural check
`.claude/skills/harness/bin/validate-digest.py`):
```
python3 -c "import subprocess,time; ...
subprocess.run(['python3','validate-digest.py','harness-backend-dev'], input=b'nothing', capture_output=True)"
```
10 reps, avg **42.5ms** per full process (`validate-digest.py:1-1122`).

**Verdict: material relative to the hook's own budget (~20% of 42.5ms), not material in
absolute human-perceptible terms.** `code_grade`'s self-time (ast/hashlib/math parsing) is
only ~700-760us; the rest (dataclasses→inspect→dis→tokenize ~3.4ms, decimal→_decimal
~1.1ms) is stdlib weight pulled in by `@dataclass` and the ABC-metric `Decimal` rounding —
present because `code_grade.py` is one module serving both grading (needs `dataclass`,
`Decimal`) and now `commit_oid` (validate-digest.py's only actual need). That's the true
cost of the consolidation: `commit_oid`'s importer inherits weight it doesn't use.

## 2. stdlib-only / no import-time side effects — verified by execution, not just reading

`code_grade.py:5-10` imports only `ast, hashlib, subprocess, dataclasses, decimal, math` —
all stdlib. Confirmed by reading the whole file (no other import statements exist,
`code_grade.py:1-388` structural pass) and, separately, by execution: `code_grade`'s
**self** import time (688-756us across 3 runs) is consistent with pure bytecode
compilation/class-body execution and nowhere near the ~11ms a subprocess spawn costs
(measured directly, §3) — if `import code_grade` shelled out at load time it would show up
in that self-time. `@dataclass(frozen=True)` on `FunctionGrade` (`code_grade.py:13-26`)
runs at import time but only builds `__init__`/`__eq__` etc. — no I/O. No module-level
statement outside `import`/`def`/`class` exists (verified via full-file structural read).
**Conclusion: stdlib-only, no import-time side effect, confirmed by execution.**

## 3. Other wasted work

- `commit_oid` invoked **twice** per `reviewed_python_change` call
  (`validate-digest.py:556-557`, `resolve_reviewed_commit` at 541-546) — **forced, not
  waste**: base and head are two distinct, independently-untrusted revisions; each needs
  its own `git rev-parse --verify` (`code_grade.py:284-289`). Measured each `git rev-parse`
  subprocess spawn directly: `python3 -c "subprocess.run(['git','-C','.','rev-parse',
  '--verify','--end-of-options','HEAD^{commit}'],...)"`, 10 reps → avg **11.0ms/spawn**
  (range 9.6-13.4ms). Two spawns ≈ 22ms — this **dwarfs** the 8.3ms import cost and is the
  actual dominant per-call-site cost of the new seam, but it is *gated*: it only executes
  inside `if code_grade == "n_a":` (`validate-digest.py:766-767`), i.e. only for
  `harness-code-reviewer` digests claiming `code_grade: n_a`, not every hook invocation.
  **Enhancement, not bug**: `git rev-parse` accepts multiple revisions in one invocation
  (`git rev-parse --verify --end-of-options a^{commit} --verify --end-of-options
  b^{commit}`), which would collapse 2 spawns into 1 (~11ms saved per n_a-claim
  validation) — but it changes `commit_oid`'s per-revision error attribution and is a
  seam-signature change, out of scope for this pass.
- **The eager import is the real finding.** `from code_grade import commit_oid`
  (`validate-digest.py:32`) is unconditional at module top, so its ~8.3ms is paid on
  **every** invocation of `validate-digest.py` — every persona, every `SubagentStop` — even
  though `commit_oid` is reachable only through `resolve_reviewed_commit`
  (`validate-digest.py:541-546`), itself reached only when `code_grade == "n_a"`
  (`validate-digest.py:766-767`), a `harness-code-reviewer`-only branch. Most invocations
  (`harness-backend-dev`, `harness-qa`, leads, etc.) never touch it and still pay the tax.
  **[enhancement]** `validate-digest.py:32` — summary: eager top-level import of
  `code_grade` costs ~8.3ms on every hook run though used on one narrow branch — cost:
  ~8.3ms × every `SubagentStop` across every persona in a session (dozens of spawns is not
  unusual, so tens to ~100ms/session, not "minutes") — alternative: move
  `from code_grade import commit_oid` inside `resolve_reviewed_commit`
  (`validate-digest.py:541`), making the cost conditional on the branch that needs it.
  Below the material bar on its own (absolute per-call cost is single-digit ms); flagging
  because it is easy, safe, and free of behavior change — not because it is urgent.
- No repeated file reads, no re-parsing of the same source, no closures holding scope alive
  found in the seven-file diff.

## 4. Reduce vs. relocate (R-01 from the efficiency angle)

**Neither — R-01 ADDS new, forced work; there was nothing to relocate.** Checked the
committed baseline directly: `git show HEAD:.claude/skills/harness/bin/validate-digest.py`
had `reviewed_python_change` running `git diff --name-only -z base head` on the **raw,
unvalidated** `base`/`head` strings — no `commit_oid`, no resolver, no import of
`code_grade` at all. Same check on committed `code-grade.py` (`main`) and `code_grade.py`
(`gated_set`/`_changed_python_files`): neither validated revisions before shelling out
either. So there were not three duplicate *validating* implementations being consolidated
— there were **zero** validating implementations, plus two call sites passing untrusted
strings straight to `subprocess`. R-01 introduces `commit_oid` as new logic and gives all
three call sites (`code-grade.py:162-163`, `code_grade.py:369` inside `gated_set`,
`validate-digest.py:541-546`) the same validation for the first time, via one seam instead
of three copies of a fix. Runtime-wise this is a forced *addition* (2 subprocess spawns +
one shared import per validating call site), not removed duplication — but it does prevent
the alternative (three inline copies, which would have paid the same subprocess cost with
none of the shared-fix benefit and a live drift risk). **Correct trade for correctness; not
free, and honestly costed above.**

## Findings summary

| # | label | file:line | cost | alternative |
|---|---|---|---|---|
| 1 | enhancement | `validate-digest.py:32` | ~8.3ms on every hook invocation regardless of persona/branch | lazy-import `commit_oid` inside `resolve_reviewed_commit` (`validate-digest.py:541`) |
| 2 | enhancement | `code_grade.py:281-292`, called from `validate-digest.py:556-557` | 2×~11ms `git rev-parse` spawns per `n_a`-claim validation, collapsible to 1 | single `git rev-parse` call with two `--verify` args (changes seam signature — out of scope here) |

Neither finding is `must_fix`. Deliberate full-suite runs at the qa-gate/ship boundary are
not flagged — none observed added by this diff; the three suites below are the appropriate
targeted+full runs for this scope, not redundant re-runs.

## Suites

```
python3 .claude/skills/harness/bin/test-code-grade.py        -> PASS test-code-grade (exit 0)
python3 .claude/skills/harness/bin/test-code-grade-cli.py     -> PASS test-code-grade-cli (exit 0)
python3 .claude/skills/harness/bin/test-validate-digest.py    -> ALL PASSED (exit 0) — 65/65 + 14/14 + 24/24 + 2/2
```

## git status --short (last action)

```
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-check-plan-routes.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .claude/skills/harness/bin/test-validate-digest.py
 M .claude/skills/harness/bin/validate-digest.py
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-validate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q2-cycle-11-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q3-cycle-13-overrun.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q4-simplify-routing.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q5-simplify-apply-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-fix-c13-qa-validator.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-efficiency-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c11.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.md
```
(No source/test file under the seven-file scope was touched by this run — all modifications
predate this assessment; this receipt itself is the only new untracked file this run adds,
alongside sibling receipts written concurrently by peer angle readers.)
