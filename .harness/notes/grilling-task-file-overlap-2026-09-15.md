# Grilling — plan-merge check names files shared by two tasks; spec-driven slices by ownership (#1725) — 2026-09-15

## Destination
`plan-merge.py check` on a drafted plan prints every file named by more than one task with the
task ids, advisory (exit unchanged), so pm and the plan readers see the overlap before a build
gates one task against another's half-finished tree. `harness-spec-driven` states the slicing
rule and the plan team's `scope` reader asks the question.

## Mission
mission: patch
reason: cause is known (a strict task chain layered over shared files; five of ten cycles were cross-task regates), files are bounded (plan-merge.py check, its test, one skill, one team prompt), and the output is an advisory line on an existing verb — no new gate or schema.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do all of them from plan (or patch) to ship")

## Settled
- Report, don't refuse → `check` prints one line per shared file: `OVERLAP <path>: T-02, T-07`.
  Exit code is unchanged by overlap; a plan with shared files is legal (some are unavoidable, e.g.
  a shared fixture JSON). The point is that pm sees it at draft.
- Matching → on the normalized `path` of each `files:` anchor (`path`, `path#symbol`,
  `{path, quote}` all reduce to `path`; DEC-232). Two anchors into the same file are one overlap.
- Slicing rule, `harness-spec-driven` → a task owns its files. A change across many files is sliced
  by file ownership (each file in exactly one task) or is one task with a per-file checklist —
  never by layer over shared files. A whole-tree `verify:` assertion belongs to the last task that
  touches those files, or to validate.
- `scope` reader prompt (`teams/plan.yaml`) → add the question: which tasks share files, and whose
  gate will the later one break? An answer is a `substance` finding.
- Build execution → `plan-merge.py` and its test are DEC-174 carve-out (it is the only plan write
  route and `check` is the plan-exit gate) → `main-session-direct`. Skill and team prose are
  dispatchable but tiny; pm may fold them into the direct task.

## Not yet specified
- none

## Out of scope
- Changing cycle counting (DEC-157) or pinning a tree for a task's gate — the tree moving is the
  point of a build.
- Refusing overlapping plans.
- Re-slicing BUG-285-canonical-reader's shipped plan.

## Facts I verified (so pm does not re-derive them)
- BUG-285-canonical-reader `plan.yaml`: strict chain T-09→T-01→T-02→…→T-08; shared files per pair
  from `files:` — T-06/T-07 11, T-03/T-04 10, T-04/T-07 8, T-02/T-07 6, T-02/T-04 5, T-03/T-07 5,
  T-05/T-07 4, T-02/T-03 4; 5 of 7 `regate` judgements are one task's gate tripping on another
  task's in-progress state (#1713 Finding 3).
- `plan-merge.py check` is `cmd_check` at `.claude/skills/harness/bin/plan-merge.py:2980`; it
  resolves anchors and routes (`_Routes`) and reads the BRIEF; it says nothing about overlap today.
- Anchor forms: `path`, `path#symbol`, `{path, quote}`; `path:NN` refused at write (DEC-232).
- `scope` reader prompt: `teams/plan.yaml:66-91`.
- `plan-merge.py` tests: `tests/integration/test-plan-merge.py`.
- Base: `origin/main` at 82c9d074.
