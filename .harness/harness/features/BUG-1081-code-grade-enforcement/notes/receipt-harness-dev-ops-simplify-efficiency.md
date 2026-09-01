# EFFICIENCY angle — BUG-1081 code-grade enforcement

## Verdict

One real finding: a measured ~59 ms (~13%) of redundant `git rev-parse --verify` calls
inside the enforcement path, re-verifying commit OIDs the same invocation already
resolved. Everything else the dispatch specifically asked about came back clean —
recorded below with numbers, not assumed.

## Method

Measured directly against this worktree, not estimated. Monkeypatched `subprocess.run`
to log every `git` invocation, then ran the real code path
(`code_grade_bound_to_review` + `code_grade_enforcement_error`) against a scratch
feature dir (`review_sha` = current HEAD, deleted before I finished — see Cleanup). Timed
with `time.perf_counter()`. Individual subprocess costs measured with 20-iteration
averages of the same command run standalone.

## Findings

### 1. Redundant re-verification of already-resolved commit OIDs — chore

**File**: `.claude/skills/harness/bin/validate-digest.py`, functions
`_canonical_review_range` (:648-683), `_mechanical_code_grade` (:734-758, via its call
to `reviewed_python_change` at :749), and `.claude/skills/harness/bin/code_grade.py`'s
`gated_set` (:419-430, via its two `commit_oid` calls at :423-424).

**Line**: `validate-digest.py:749` and `code_grade.py:423-424` are the concrete re-verify
sites; the OIDs they re-verify were already produced, in the same call, by
`validate-digest.py:665` (`resolve_reviewed_commit` for `review_sha`) and
`validate-digest.py:671` (`_merge_base_or_none` for `base_oid`).

**Summary**: `review_sha`'s OID gets resolved via a `git rev-parse --verify` subprocess
4 times in one hook invocation, and the merge-base-derived `base_oid` gets re-verified
2 times, even though both are already-trusted 40-hex commit OIDs the moment `git`
itself produced them (`merge-base`'s stdout, or a prior successful `rev-parse`).

**Cost, measured**: I traced the real call sequence `validate()` takes for a
`harness-code-reviewer` digest (`code_grade_bound_to_review` then
`code_grade_enforcement_error`) against this worktree's own diff (5 changed `.py`
files). Total: 27 `git` subprocesses, 467 ms wall (33 ms + 434 ms). Of those 27, 6 are
re-verifications of an OID this exact invocation had already established as valid one
call earlier:
  - `HEAD`'s OID resolved twice (once in `code_grade_bound_to_review`, again in
    `code_grade_enforcement_error`'s `reviewed_python_change` shape check).
  - `review_sha`'s OID resolved 4 times total (bound_to_review's `pin_oid`, the shape
    check's head, `_canonical_review_range`'s `resolve_reviewed_commit`, and
    `gated_set`'s `commit_oid(head_ref)`).
  - the merge-base-derived `base_oid` resolved 2 times (`reviewed_python_change` on the
    canonical range, then `gated_set`'s `commit_oid(base_ref)`).

  A standalone `git rev-parse --verify --end-of-options HEAD^{commit}` averages 9.8 ms
  over 20 runs in this checkout. 6 redundant calls × ~9.8 ms ≈ **59 ms, ~13% of the
  467 ms this path spends** on a return that changes nothing about the accept/reject
  decision — every one of the 6 calls re-verifies a value already known good.

**This runs once per code-review digest**, not on every `SubagentStop` (see clean
result #1 below) — so it is not "every write" money, but it is real, avoidable
per-review latency, and it compounds across a review cycle's revisions.

**Alternative**: thread the already-resolved OIDs through instead of re-deriving them.
Concretely: (a) have `_mechanical_code_grade` pass its own `base_oid`/`head_oid`
directly into a diff-only helper for the "does this range touch Python" check, instead
of routing back through `reviewed_python_change` (which exists to validate *untrusted*
input, not the output of `merge-base`/`rev-parse` `_mechanical_code_grade` just
produced); (b) give `gated_set` a path that accepts pre-verified OIDs directly (or has
`_classify_canonical_range` call the file-diff/grade step without going through
`commit_oid` a second and third time); (c) have `code_grade_bound_to_review` pass its
already-resolved `pin_oid` into `code_grade_enforcement_error` rather than the two
functions each re-deriving `review_sha`'s OID independently. None of this touches
D-03's seam boundary or the batch contract — it only removes repeat verification of a
value one `git` call in the same process already proved valid.

**Nature**: chore.

## Clean results (measured, not flagged)

1. **Gating runs before, not after, the git work.** `code_grade_enforcement_error`
   (and its sibling `code_grade_bound_to_review`) is called only inside
   `if raw_persona == "harness-code-reviewer"` (`validate-digest.py:1304`), and the
   grading call additionally requires `code_grade in CODE_GRADE_VALUES and not
   _is_plan_review(reviewed)` (`:1314`) before `code_grade_enforcement_error` runs at
   all. A `dev`, `qa`, `pm`, or any non-code-reviewer return does zero git work on this
   path — confirmed by reading the branch, not inferred.

2. **`_load_test_kinds` does not re-read a file already read in the same invocation.**
   It is the only reader of `test_kinds` in this call chain; `review_config_path()` /
   `load_policy()` (called earlier in `validate()` for `review_policy`, line 1137) reads
   the *same file* (`harness.json`) for a *different* key (`review`, not `test_kinds`).
   Measured cost of that second read+parse of `harness.json` (11,198 bytes) in this
   checkout: **0.04 ms** average over 200 iterations — not worth avoiding even if it
   were literally duplicated, which it is not.

3. **`code_grade.py`'s module import adds nothing new to hook startup.**
   `origin/main`'s `validate-digest.py` already carries
   `from code_grade import commit_oid` at module level — this diff only adds two more
   names (`classify`, `gated_set`) to that *already-existing* import, paying zero
   incremental import cost. Measured full `code_grade.py` cold import (via
   `python3 -X importtime`): 12.7 ms cumulative (mostly `dataclasses` → `inspect` →
   `dis`/`tokenize`, and `decimal`), all of which was already being paid pre-BUG-1081
   on every hook invocation via the pre-existing `commit_oid` import. Full
   `validate-digest.py` module import: 20.7 ms wall, unchanged in composition by this
   diff.

## Deliberate boundary work — not flagged

The ~434 ms `code_grade_enforcement_error` itself spends (10 `git show` calls to
pull both sides of every changed function, plus AST grading) is the mechanical
enforcement BUG-1081 exists to add — recomputing the grade rather than trusting the
reviewer's claim (D-05). That is the evidence the gate is real, not waste, and it fires
once per code review, not on every agent's every write.

## Cleanup confirmation

Scratch measurement used a temporary `.harness/harness/features/__scratch_efficiency__/`
directory (a synthetic `feature.json` with `review_sha` = this worktree's own HEAD, to
exercise the real code path against a real range). Deleted with `rm -rf` before writing
this receipt; `git status --porcelain` afterward shows only pre-existing sibling-agent
changes (`feature.json` modified, three `notes/*.md` untracked from other concurrent
agents) — no trace of my scratch directory remains, and I created no other files. No
source file was edited.

## DIGEST (for the record)

```yaml
VERDICT: PASS
DIGEST:
  headline: one measured chore-grade finding (~59ms/13% redundant git rev-parse re-verification per code review); every other efficiency question the dispatch raised comes back clean, with numbers
  task: none
  open_questions: []
  files_touched: [.harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-dev-ops-simplify-efficiency.md]
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-dev-ops-simplify-efficiency.md
```
