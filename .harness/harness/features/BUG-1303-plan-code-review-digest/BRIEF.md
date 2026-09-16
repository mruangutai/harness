# BRIEF — BUG-1303 Plan-phase code-review digest is unwritable

## Problem

A `harness-code-reviewer` dispatched in the plan phase cannot return a digest that validates. The
validator already implements DEC-207 plan-review mode (`_is_plan_review`, `_pending_plan_review_error`
in `.claude/skills/harness/bin/validate-digest.py`), but **the two contracts the reviewer actually
reads never mention it**: `.claude/skills/harness-code-review/SKILL.md` has zero matches for `plan:`,
`DEC-207` or pre-signature, and the persona `## Output` block in `.claude/agents/harness-code-reviewer.md`
and `.omp/agents/harness-code-reviewer.md` offers only `reviewed: "base..<review_sha>"`.

Worse, that block **does not list `code_grade` at all**, while the validator's schema requires it for
this persona. Measured at `c369fb1f`: for the sixteen personas, comparing each schema's required
field set against the block the persona is told to write, `harness-code-reviewer` is the **only**
persona missing a required field, and the field is `code_grade`. So the persona's documented digest
is unconditionally invalid in **every** phase, and in the plan phase a reader that did its job settles
as `failed` with two errors — the missing field, and `code_grade cannot be bound to review_sha`.

B-9 of `.harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.md:85`;
assigned to issue #1303 by `.harness/notes/grilling-six-residual-bugs-2026-09-05.md:19`.

## Goal

A code reviewer that follows only the contract it is handed can return a valid digest in the plan
phase and in the post-pin phase alike — and the class of defect that produced this (a documented
output block that disagrees with the validator schema) is caught mechanically from now on, for every
persona, instead of being discovered by a reader whose correct work was thrown away.

## Requirements

- REQ-01: A code reviewer working from only its persona `## Output` block — every DIGEST field it
  lists, the `artifact:` path that block names, and the `Write` grant sentence that tells the
  reviewer where its report may be written — together with `harness-code-review/SKILL.md`, can write
  a plan-phase digest that `validate-digest.py` accepts while `review_sha` is unpinned and the plan's
  `approval.status` is `pending`.
- REQ-02: The reviewer's documented output block names every field the validator requires of that
  persona, `code_grade` included, with the exact legal values; and the `artifact:` path it documents,
  along with the persona's stated `Write` grant for that report, names a location under that
  feature's own `.harness/<repo>/features/<FEAT>/notes/`, which is what the validator requires of an
  artifact before it will bind `code_grade` at all.
- REQ-03: Ordinary post-pin code review remains exactly as strict as today — the SEC-01 `review_sha`
  binding, the DEC-209/BUG-1081 mechanical recomputation of `code_grade`, and INV-6's requirement of a
  pinned `review_sha` are unchanged in behaviour.
- REQ-04: A divergence between any persona's documented output block and the validator schema is
  detected mechanically, for all sixteen personas, and reads as a named failure rather than a smaller
  passing count when discovery breaks.
- REQ-05: The rule that a persona's documented output block is an enforced half of the digest
  contract is recorded in `.harness/harness/docs/DECISIONS.md` and indexed.

## Success Criteria

Commands run from the repository root of the reviewed worktree. `<review_sha>` is the pinned review
commit; `<base>` is `merge-base(main, <review_sha>)`.

- SC-01: The full digest-validator suite passes on the reviewed tree, including the new
  contract-conformance section, with no `FAIL` line.
  `python3 tests/integration/test-validate-digest.py` exits 0 and its output contains no line starting
  `FAIL`. Baseline: observed exit 0, zero `^FAIL ` lines, final `ALL PASSED.` in 18.9s at sha
  `c369fb1f` in worktree `BUG-1303-plan-code-review-digest`, before any task of this feature landed —
  so a red at review is attributable to this feature's own change rather than to inherited breakage.
  verify: automated      evidence: integration
- SC-02: The new conformance check discriminates in both directions within one run: a synthetic
  documented block that omits a required field is reported as a failure, and the same block carrying
  that field is accepted. Both are named cases in the suite output, so neither can be ever-green.
  verify: automated      evidence: integration
- SC-03: The plan-mode values the reviewer is now told to write are derived from the validator's own
  constants (`_PLAN_REVIEW_PREFIX`, `CODE_GRADE_VALUES`), not from a string retyped into the test, and
  each of the reviewer's three contract sources is asserted individually to document them —
  `.claude/agents/harness-code-reviewer.md`, `.omp/agents/harness-code-reviewer.md` and
  `.claude/skills/harness-code-review/SKILL.md`. The assertions are on COMPOSITES, never bare
  substrings: the literal `reviewed: ` joined to `_PLAN_REVIEW_PREFIX`, and a line whose first
  non-space token is `code_grade:` carrying the `n_a` member. A bare form would prove nothing —
  measured at `c369fb1f`, `n_a` already occurs at `.claude/skills/harness-code-review/SKILL.md:112-113`
  in an unrelated passage, and bare `plan:` survives in ordinary prose ("the plan:"). The two
  agent-file copies are additionally asserted to carry the artifact-path fragment
  `features/<FEAT>/notes/review-harness-code-reviewer-`, so the half of D-06 that is fatal on its own
  is guarded by the suite rather than only by one task's verify.
  verify: automated      evidence: integration
- SC-04: Post-pin strictness is untouched, proven structurally rather than by re-reading behaviour:
  `git diff --name-only <base>..<review_sha>` names neither
  `.claude/skills/harness/bin/validate-digest.py` nor any file under `.claude/skills/harness/bin/`,
  and the pre-existing SEC-01, BUG-1081 and branch-corroboration cases in the suite still pass
  unmodified. Graded from two artefacts that already exist: the reviewer runs that one `git diff`
  command at `<review_sha>` and cites its output, and T-03's `verify:` — which runs the whole
  `tests/integration/test-validate-digest.py` suite — is the evidence that the pre-existing cases
  still pass. No task adds an assertion for this criterion, because a test cannot assert what its
  own change set does not contain.
  verify: inspection
- SC-05: Every persona in the validator's own registry gets its own assertion — a per-persona pass
  line, not a single aggregate — and the persona set under test is DERIVED from that registry
  (`validator.ALIAS` / `validator.SCHEMAS` keys), never hand-typed beside the map it grades. Any
  registry persona for which `CONTRACT_SOURCES` supplies no documenting path is reported as a named
  per-persona failure carrying that persona's name, so a seventeenth persona added to the validator
  reddens this section by name instead of shrinking a still-passing count. Today's registry maps all
  sixteen personas, every mapped path exists and every documented block is locatable, so those
  branches have zero live executions: the guarantee is therefore DEMONSTRATED to report red within
  the same suite run, in the both-directions shape SC-02 uses. On synthetic input, in one call of the
  grading helper, each of an unmapped roster persona, a mapped source absent from disk, a source
  whose documented block cannot be located, and a required field present only OUTSIDE the block is
  reported as a named failure, while a fully-mapped synthetic control reports none. The grading is
  scoped to the persona's documented block, not the whole file, because seven of the sixteen personas
  share two files.
  verify: automated      evidence: integration
- SC-06: `git show <review_sha>:.harness/harness/docs/DECISIONS.md` contains a new entry whose ruling
  is that a persona's documented output block is part of the enforced digest contract and must carry
  every field the validator schema requires; `git show <review_sha>:.harness/harness/docs/DECISIONS-INDEX.md`
  carries that entry's row with a hand-written ruling after ` :: `, and re-running
  `.agents/skills/harness/bin/gen-decisions-index.py` leaves the index byte-identical. Graded from
  T-04's own `verify:` output — which runs the `documented output block` grep and the
  `gen-decisions-index.py --stdout | diff -q -` idempotence check — plus a reviewer reading both
  files at `<review_sha>` and citing `file:line`.
  verify: inspection
- SC-07: `git show <review_sha>:.claude/skills/harness-code-review/SKILL.md` documents the
  plan-phase form where a plan-phase reader will meet it — in or adjacent to the pinned-SHA
  instruction that currently sends every reader to `base..review_sha` — and cites DEC-207. Graded by
  a reviewer citing `file:line` at `<review_sha>`.
  verify: inspection
- SC-08: `.claude/agents/harness-code-reviewer.md` is still a faithful generated adapter of
  `.omp/agents/harness-code-reviewer.md` after the change — body-identical from the
  `# Harness: Code Reviewer` heading onward, differing only in frontmatter. Graded from evidence that
  already exists rather than from a new test: T-02's own `verify:` output, which runs
  `python3 .claude/skills/harness/bin/sync-agent-adapters.py --check` (rc 0) and the body-compare of
  the two copies, plus the standing wiring that runs the same `--check` from
  `check-omp-port.py:156-166`. That gate compares all sixteen adapter pairs over the whole file, so no
  task adds an integration assertion for this criterion: a third copy of a green gate is duplicate
  coverage, not evidence (D-07).
  verify: inspection

## Verification gaps

- No gap. The only automated kind these criteria rest on — `integration` — carries a live runner in
  `.harness/harness.json`. Nothing here rests on a `cmd: null` kind, and no browser, LLM or database
  surface is touched. SC-04, SC-06 and SC-08 are graded by inspection because each names an
  observation about the change set, the pinned tree, or an existing standing gate that the change
  set's own tests cannot make; each names the command output it is graded from.

## Constraints

- **DEC-207 supplies** the mechanism: plan-review mode is already legal and already implemented. This
  bug does not change what it permits; it makes the reviewer's contract say so.
- **DEC-209 (BUG-1081) and SEC-01 bind**: `code_grade` is recomputed from a repository-derived range
  and the digest's claim is refused when it disagrees. No task may weaken this, and no task edits
  `validate-digest.py`.
- **INV-6 binds**: a validator run requires a pinned `review_sha`. Plan mode is a distinct target, not
  a fallback for a missing one.
- **DEC-174 supplies the route**: `validate-digest.py` and its own tests are the enforcement layer and
  are edited main-session-direct, tests run explicitly. `.claude/agents/**`,
  `.claude/skills/harness-code-review/**` and `.omp/agents/**` resolve to NOBODY, so they are
  main-session-direct too. Only the DECISIONS.md edit routes to a team lane (harness-documentor).
- `.agents/skills` is a symlink to `.claude/skills`: one inode, two spellings. Paths are written in
  the `.claude/...` form.
- `.omp/agents/**` is the canonical persona source and `.claude/agents/**` are generated adapters
  (D-07): the body change is authored in the `.omp` file and the `.claude` copy is regenerated with
  `sync-agent-adapters.py --apply`. The two copies differ only in frontmatter.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-05
