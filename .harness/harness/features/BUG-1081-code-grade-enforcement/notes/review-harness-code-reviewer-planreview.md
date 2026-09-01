# Architecture/plan review — BUG-1081 code-grade enforcement (D-01..D-07, T-01..T-04)

Scope: `plan.yaml`'s decisions and tasks against `code_grade.py`, `code-grade.py`, `validate-digest.py`
and their existing tests, as they exist today (no implementation diff to review). Read-only, no edits,
no tests run.

## Verdict

**FAIL** — one `high` finding (F1): two of the plan's four tasks cite verify commands that are
guaranteed to fail as written, one against a script deleted under a signed decision. The core design
(shared result API, canonical range derivation, error contract, grade precedence, DEC-207 isolation)
is sound and well specified; F1 blocks purely on the build-mechanics of T-03/T-04, not the grading fix
itself.

## What the plan gets right

- **D-04's mixed-result precedence** (`fail` > `grade_2` > `pass`) matches `code-grade.py`'s existing
  `_blocks`/`_severity` semantics exactly (`grade < bar and grade != 2` blocks; `grade == 2` is always
  reasoned, never blocking, regardless of bar) — T-01 does not need to invent new classification rules,
  only expose the existing ones.
- **The `n_a` boundary is correctly placed outside the seam.** T-01's classification API is scoped to
  never decide `n_a` ("an empty pair from `gated_set()` cannot distinguish no Python change from a
  changed Python file with no gated function"), and T-02 keeps the `n_a` decision on the existing
  `reviewed_python_change`/`_derived_reviewed_python_change` machinery (`validate-digest.py:549-682`).
  This is the right seam placement — one adapter (the seam) for "what does this range grade to," a
  separate one for "did Python change at all."
- **DEC-207 preservation is structurally sound.** `code_grade_bound_to_review` already short-circuits
  plan reviews to `_pending_plan_review_error`, which requires `code_grade == "n_a"`
  (`validate-digest.py:908-914`) before any grading logic runs — a plan review claiming a graded value
  is rejected by this existing gate independent of whatever T-02 adds.
- **D-02's range derivation reuses, rather than duplicates, SEC-01 wave 4's existing fail-closed OID
  derivation** (`_default_branch_or_none`/`_merge_base_or_none`/degenerate-range check,
  `validate-digest.py:637-682`) — refactoring it into a shared path for both n_a and the seam call is
  the correct "one implementation" move D-07 asks for.

## Findings

### F1 (high) — T-03 and T-04's `verify:` commands cannot pass; one cites a script deleted by a signed decision

**Evidence.** T-03's verify block is `.agents/skills/harness/bin/check-docs.sh`. T-04's is:
```
python3 .agents/skills/harness/bin/gen-decisions-index.py --check
.agents/skills/harness/bin/check-docs.sh
```
`check-docs.sh` does not exist anywhere in the repository (confirmed by a full-repo glob against both
`.agents/skills/harness/bin/` and `.claude/skills/harness/bin/`). It was deliberately deleted:
`DECISIONS.md` **DEC-188** ("A contradicted decision is struck, not marked: detection is replaced by
deletion") states plainly "`bin/check-docs.sh` is deleted, the INV-10 block is out of
`check-state.sh`... and there is no replacement mechanism — 'the repo loses the only mechanism' that
detected stale cross-references." `check-state.sh` itself confirms at its own INV-10 removal comment:
"It ran check-docs.sh, the propagation checker, which no longer exists."

Separately, `gen-decisions-index.py --check` is also broken on its own terms: the script's module
docstring states outright "There is no --check: to check for drift without writing, pipe the read-only
mode into diff." Its `parse_argv` (`gen-decisions-index.py:240-259`) treats any argument other than
`--stdout`/`--help` as a hard error and calls `sys.exit(2)` with "unrecognized argument(s): --check.
Wrote nothing." — so this line fails for a second, independent reason.

**Failure scenario.** T-03's executor runs its stated verify command and gets a shell "No such file or
directory." T-04's executor runs the first line and gets "unrecognized argument(s): --check" (exit 2)
before even reaching the second, equally broken, line. Neither docs task has a working automated verify
path as specified; both would have to be re-derived ad hoc by whoever executes them, which is exactly
the ambiguity a plan's `verify:` field exists to remove.

**Required correction.** Drop the `check-docs.sh` line from both T-03 and T-04 (there is no replacement
per DEC-188 — the BRIEF already correctly scopes SC-09 to `verify: inspection`, which is the only
verification these docs changes get). If T-04 wants a mechanical drift check on the generated index,
use the script's own documented invocation: `gen-decisions-index.py --stdout | diff -
.harness/harness/docs/DECISIONS-INDEX.md`.

### F2 (med) — No fixture pins the deletion-only-Python-file boundary, where the plan's two "did Python change" mechanisms disagree

**Evidence.** T-02 decides `n_a` from "the canonical diff" and otherwise calls T-01's seam. Today these
are two *different* enumerations of "what changed": `reviewed_python_change` (`validate-digest.py:558-
568`) runs `git diff --name-only` with no `--diff-filter`, so a **deleted** `.py` path still appears in
its output and counts toward `python_changed = True`. `code_grade.gated_set()`'s own file selector,
`_changed_python_files` (`code_grade.py`), explicitly excludes any path whose status starts with `D`
before grading — by design, since a deleted function cannot regress. D-01/D-07 push toward "one
importable grading API" and reusing rather than duplicating range-derivation; if an implementer
consolidates the n_a "has Python changed" answer through `gated_set`'s (or `_changed_python_files`'s)
deletion-excluding logic instead of preserving `reviewed_python_change`'s inclusive one, a
deletion-only canonical range would be misclassified as `n_a` when the correct classification (per
D-04's own text — deletions are changed `.py` files, just never gated ones) is `pass`.

**Failure scenario.** A reviewer's canonical range deletes a `.py` file and touches nothing else. The
honest claim is `code_grade: pass` (Python changed, nothing gated). If the n_a decision is
implemented on the deletion-excluding path, the validator's expected value is `n_a`, and the honest
`pass` digest is rejected as a mismatch — a false rejection of a legitimate review, not a security hole,
but exactly the kind of correctness gap T-02's own fixture list should pin and currently does not: the
listed fixtures cover "no-Python n_a" but nothing that isolates the deletion-only case from that.

**Required correction.** Add a fixture to T-02: canonical range whose only Python-touching change is a
file deletion, asserting the mechanical result is `pass`, not `n_a`. State in T-02's intent which
helper answers "did Python change" (the inclusive name-only diff) versus "what needs grading"
(`gated_set`'s deletion-excluding selection), so the two are not accidentally merged into one.

### F3 (med) — The plan does not name which checkout root backs the seam call, and this file already has two disagreeing conventions for that question

**Evidence.** T-01's seam and `code_grade.gated_set(repo_root, base, head)` both take `repo_root`
explicitly; and — one level down — `code-grade.py`'s `_is_test(root, relative)` opens `root /
".harness" / "harness.json"` to pick the bar (3 vs 4). T-02 must supply this `repo_root` when it calls
the seam, but the plan does not say from where, and `validate-digest.py` already contains two live,
disagreeing patterns for "which checkout is this review in":
1. `_root_or_none()` / `review_config_path()` — `harness_boundary.resolve_root`, script-location/
   environment-derived, used for the review-policy gate config.
2. Deriving the root directly from `feature_dir` (`os.path.join(feature_dir, "..", "..", "..", "..")`)
   — the pattern `_current_branch_or_none` already uses for branch corroboration
   (`validate-digest.py:775-782`).

`test-validate-digest.py`'s own `check_hook_feature_dir` demonstrates these two can legitimately
differ: it stubs `_root_or_none()` to an `owner_root` distinct from the resolved worktree
`feature_root`. This repository's own layout is exactly that topology —
`.claude/worktrees/<owner>/<FEAT>` worktrees share one git object store but **not** one working tree,
so a `.harness/harness.json` read from the wrong root can silently differ from the reviewed checkout's.

**Failure scenario.** If T-02 passes `_root_or_none()`'s value into the seam instead of deriving
`repo_root` from `feature_dir` (the pattern two functions away already establishes for the identical
"which checkout" question), mechanical grading in the installed-hook/fleet path reads the **owner**
checkout's `.harness/harness.json` `test_kinds` instead of the reviewed worktree's. If the two diverge
(a plausible, in-flight-feature scenario — this very feature's worktree could itself change test-kind
detection), a path is silently graded against the wrong bar (3 vs 4) with no exception raised — a
silent wrong mechanical result, in the exact class of defect this feature exists to close.

**Required correction.** State explicitly in T-02 that `repo_root` for the grading/seam call is derived
from `feature_dir` the same way `_current_branch_or_none` already does, not from `_root_or_none()`.

### F4 (low) — `test-code-grade-cli.py`'s hardcoded self-grading qualname list will need updating, not merely shrinking, when T-01 moves functions out of `code-grade.py`

**Evidence.** `test_diff_paths_complexity` (`test-code-grade-cli.py:305-312`) asserts a fixed tuple of
qualnames — including `_record`, `_severity`, `_blocks` — are present in, and grade well against,
`code-grade.py`'s **own** source. T-01's intent is to move exactly these functions ("the CLI's
path-to-bar and blocking rules") into the new shared seam in `code_grade.py`. Once moved, this
assertion fails loudly (good), but the easy fix under time pressure is to drop the now-absent names
from the tuple rather than confirm they are still graded at their new home. This is mitigated, not
eliminated: `test-code-grade.py`'s CR-01 self-grading sweep (`SELF_GRADED_FILES`) already includes both
`code-grade.py` and `code_grade.py` and grades every function each file *currently contains* (not a
fixed list), so coverage of the relocated logic reattaches automatically there. `test_diff_paths_
complexity`'s list is the narrower, redundant one.

**Required correction.** Note in T-01 (or leave to the code-quality pass) that this tuple should track
the functions' new location rather than simply be shortened; not a build blocker given CR-01's
independent coverage.

### F5 (low) — DEC-207 plan-review isolation would benefit from an explicit second guard, for error-message clarity only

**Evidence.** The existing `n_a` mechanical-check branch is explicitly gated
`if code_grade == "n_a" and not _is_plan_review(reviewed):` (`validate-digest.py:1232`). T-02's new
"otherwise call the seam" branch is not described as carrying the same `not _is_plan_review(reviewed)`
guard. In practice a plan review is already rejected upstream by `_pending_plan_review_error` if
`code_grade != "n_a"` (`validate-digest.py:913-914`), so D-06's outcome (plan reviews never call
grading, always rejected on a non-`n_a` claim) holds either way — but without the explicit guard, a
malformed `reviewed: "plan:...", code_grade: "pass"` digest would also fall through into the new
grading branch and attempt to resolve a `review_sha` that, per DEC-207, must not exist yet for a
pending plan, producing a second, confusing, review_sha-flavored error alongside the correct one
instead of one clean message.

**Required correction.** Mirror the existing pattern: gate the new branch on `not
_is_plan_review(reviewed)` as well, for a single clear error rather than a redundant one. Not a
correctness gap.

## Not findings (assessed and dismissed)

- Duplicated grading implementation risk (D-07): the plan is explicit and consistent about reusing
  `gated_set()` as the sole implementation; no second grader is proposed anywhere in T-01/T-02.
- Grade-2/blocking conflation: `_blocks` already excludes `grade == 2` from blocking regardless of bar,
  so D-04's stated precedence requires no new logic, only exposure — confirmed against
  `code-grade.py:55-62`.
- Empty-but-present `.py` files (added or truncated to zero bytes, not deleted): `grade_source("")`
  returns no records either way; the seam's "pass" default for an empty gated set is the same,
  correct, answer whether the file is new-empty or truncated-empty — no divergence like F2's deletion
  case, since both diff mechanisms agree these are changed `.py` files.
