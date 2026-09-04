# Final code review — FEAT-52 factory control-plane, pinned to 1d93c727

Range reviewed: `merge-base(origin/main, 1d93c727)..1d93c727` = `0ec44965..1d93c727` (95 files,
+6895/-238). `52375c9c` (HEAD) only rewrites `feature.json.review_sha`; no diff beyond that commit
is in scope. No `[harness:human]` commits since the pin touch reviewable source.

## Verdict: PASS

## Stage 1 — spec compliance

Walked BRIEF.md's REQ-01..06 and all 15 SCs against plan.yaml's 15 tasks (all `status: done`) and
the diff. No scope creep found: every changed file traces to a T-NN task, and every task traces to a
REQ. No requirement is missing a corresponding change.

Independently re-ran every SC that has an automated carrier, rather than trusting the recorded runs:

- `HARNESS_REVIEW_SHA=1d93c727 tests/integration/test-anchor-directions.py` → 7/7 PASS (SC-04 S1-S5
  + SC-11 S2, plus whole-scope-at-pin), exit 0.
- `python3 .claude/skills/harness/bin/check-instruction-paths.py` (live tree) → `scanned 62 file(s),
  0 violation(s)`, exit 0 (SC-04 whole-scope half).
- `tests/integration/test-check-instruction-paths.py` → 13/13 PASS, including all five named
  `scope contains <S1..S5>` assertions (SC-03) and the fenced+inline red proof (SC-05).
- `tests/unit/test-instruction-workflow-gate.py` → 3/3 PASS: the CI wiring assertion and both its
  mutants (deleted step, neutered `exit "$rc"`) go red as required (SC-08).
- `tests/integration/test-inject-expertise.py` → 21/21 PASS: unconditional control-plane block
  (SC-01), UNRESOLVED+BLOCKED branch and the exit-grep positive control (SC-02), HARNESS_PATH_DRIFT
  none/count branches (SC-12).
- `tests/integration/test-dispatch-guard.py` → 48/48 PASS, including all six case-17 assertions for
  the shell-less feature-tree-root refusal/allow/mismatch matrix (SC-13).
- Read `.omp/agents/harness-{product-lead,eng-lead,validator-lead,orchestrator}.md` and
  `harness-handoff/SKILL.md` at `1d93c727` directly: all five state the shell-less route, the
  `HARNESS-FEATURE-TREE-ROOT:` line, the `VERDICT: BLOCKED` refusal and the emit duty exactly where
  BRIEF SC-14/SC-09 requires (`harness-handoff/SKILL.md:60-67` carries both placeholders).
- `DEC-214` is present in `DECISIONS.md` with a `DECISIONS-INDEX.md` row (SC-09).
- `git diff <base>..1d93c727 -- .harness/team-config.yaml` is 0 lines; `grep` for changed `- bash`
  `- write` `- edit` tool lines across `.omp/agents` and `.claude/agents` is 0 (SC-07).
- `check-domain.sh` itself is untouched (0 lines in the diff); SC-15 is proved by a new paired
  fixture (`test-check-domain.py::_feat52_foreign_cwd_receipt_pair`) run from a foreign product cwd,
  asserting the feature-worktree receipt path allows (exit 0) and its product-tree twin refuses
  (exit 2) — read and confirmed inline, matches the SC-15 text exactly.

All of the above are inspection or automated verify kinds named by their SCs; none required a kind
this reviewer is not permitted to check.

## Stage 2 — code quality

Ran `code-grade.py --base 0ec44965 --head 1d93c727`: 38 functions, 38 `RESULT: PASS`, zero
`SEVERITY:` lines, zero grade-1/2. `code_grade: pass` (not `n_a` — this range clearly contains new
Python: `check-instruction-paths.py`, `test-anchor-directions.py`, the `inflight_registry.py`
addition, etc. The `n_a` values recorded on earlier validator runs in `feature.json` predate this
range and are not what `validate-digest.py` will recompute against this pin).

Hunted fail-open per this project's history (dangling references resolving valid, partial matches
fabricating results):

- `check-instruction-paths.py`'s `_classify` only recognizes the two placeholders by exact string
  match (`prefix.endswith("<HARNESS_CONTROL_PLANE_ROOT>/")` etc.); any near-miss spelling falls
  through to `"unanchored instruction path"` — the safe (fail-closed) direction, not a fail-open.
- `dispatch-guard.sh`'s shell-less feature-tree-root check fails CLOSED on a `declared_root`/
  `expected_root` mismatch and on `AmbiguousWorktree`; it deliberately fails OPEN only on a generic
  resolver exception, consistent with the file's stated policy that every branch except the
  FEAT-declaration check passes through on its own failure. Verified `linked_worktrees()` degrades
  to `[]` on a non-git directory rather than raising, so the common no-worktree path never hits that
  fallback.
- `inject-expertise.sh`'s only unguarded array expansion (`"${sorted_idx[@]}"`) iterates an array
  explicitly initialized to `()`, which is safe under `set -u` in the bash versions in use (the
  classic "unbound array" gotcha applies to a never-assigned array, not one initialized empty) — no
  reachable path found that would violate the never-exits-nonzero contract SC-02 requires.

One informational item, not gating: `.claude/skills/harness/bin/run-unit-tests.sh` picks up two
blank lines with no other change (line 14-15) — cosmetic debris, most likely from the rebase this
task's dispatch named as in-scope. No behavioral effect; not worth a cycle to clean up.

The plan's own finding ledger (`plan.yaml:1245-1371`) carries several `disposition: open` items
(e.g. `PF-4ea5b56692f0684ae2a69722b19bc74f` on `set -uo pipefail`'s theoretical exit-1 versus the
literal-`exit`-grep test) already adjudicated by earlier product/validator panels as
`reader: should-not-exist`. I independently checked the concrete claim behind that one (unguarded
array expansion) and found no live trigger, so it is not restated here as a finding.

## Not raised

Issue #1260 is out of scope per this dispatch and was not evaluated.

## Summary

Fifteen tasks, all `status: done`; every automated SC re-run green at the pin; inspection SCs
confirmed by direct `git show` reads; no write-grant widened; code grades clean; no fail-open found
in the new anchor-resolution logic. No must-fix findings.
