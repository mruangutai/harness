# BRIEF — BUG-148-gate-record-correction

## Problem

Two records that are read as current truth assert that `gen-decisions-index.py --check` passed as a
gate on 2026-08-03. The flag does not exist. Measured in this worktree at `41c16c7`: the command
exits 2 with `gen-decisions-index: unrecognized argument(s): --check. Wrote nothing.`, and the
module docstring says outright "There is no --check"
(`.agents/skills/harness/bin/gen-decisions-index.py:9-10`, argv parser at `:240-259`). On
2026-08-03 argv validation did not yet exist — it landed at `ffbdbfa1` (2026-08-05,
"perf(#140): validate argv so --help stops rewriting the index"). At the preceding commit
`99b380e3` (2026-08-02) `main()` read `stdout_mode = "--stdout" in sys.argv[1:]`, so an
unrecognized `--check` fell through to the WRITE path: the script regenerated
`DECISIONS-INDEX.md` in place and exited 0. The recorded exit 0 is therefore the exit code of a
write that destroys exactly the drift a check would have reported.

The two records are:

1. `.harness/harness/docs/DECISIONS.md` DEC-174, the evidence sentence "Every gate was green —
   `run-unit-tests.sh`, `check-docs.sh`, `check-state.sh`, `gen-decisions-index.py --check` —
   while:" (`DECISIONS.md:4308-4309` at `41c16c7`).
2. `.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md:14-15`, "**All four gates
   green:** ... `gen-decisions-index.py --check` 0".

DEC-174 is the entry that argues self-hosting missed real defects while its gates were green. An
evidence list that includes a gate which never ran weakens the very argument it supports, and any
reader who copies the invocation gets exit 2 today — or, on an older tree, a silent rewrite.

## Goal

Correct the two live records so each says plainly that `gen-decisions-index.py --check` was never a
supported mode and that its apparent success could not prove index drift, and names the read-only
form a reader should use instead. Nothing else changes: DEC-174's ruling stands, and every
historical artifact — receipts, research notes, prior plans, reviews, observation logs — is left
exactly as written.

## Requirements

- REQ-01: Both live records carry a dated correction of the false gate claim, in place. Dated means
  each correction names the 2026-08-03 run it corrects and the `ffbdbfa1` (2026-08-05) commit that
  ended the fall-through; the FEAT-05 record additionally names the correction date 2026-09-06.
- REQ-02: Each correction states that `--check` was never a supported mode and that its apparent
  success could not prove index drift, giving the measured mechanism — before `ffbdbfa1` an
  unrecognized argument fell through to the write path, so the exit 0 was a regeneration of
  `DECISIONS-INDEX.md`.
- REQ-03: Each correction names the read-only drift form
  `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`, where a
  reader would otherwise reach for `--check`.
- REQ-04: DEC-174's ruling, its carve-out table and the three gates that genuinely were green are
  unchanged, and no historical artifact is modified. The correction touches the evidence claim only.
- REQ-05: `DECISIONS-INDEX.md` stays in sync with `DECISIONS.md`.

## Success Criteria

- SC-01: At `review_sha`, `git show <review_sha>:.harness/harness/docs/DECISIONS.md` between the
  `## DEC-174` and `## DEC-175` headings contains no claim that `gen-decisions-index.py --check`
  was a green gate (the string "Every gate was green" is absent from that region), and does state
  the unsupported-mode fact, the pre-`ffbdbfa1` write-path fall-through, that the exit 0 could not
  prove index drift, and the `--stdout | diff` form.
  verify: inspection
- SC-02: At `review_sha`,
  `git show <review_sha>:.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` no longer
  claims four green gates including `gen-decisions-index.py --check` 0, and states each of: that
  `--check` was never a supported mode; the pre-`ffbdbfa1` write-path fall-through; that the
  exit 0 could not prove index drift; the `--stdout | diff` form; and the correction date
  2026-09-06.
  verify: inspection
- SC-03: At `review_sha`, `git diff 41c16c7..<review_sha> --
  .harness/harness/docs/DECISIONS.md` — where `41c16c7` is the branch base
  (`41c16c736e3cc4b2b331757081c90a24f2ba977d`) recorded at `plan.yaml` `lanes.resolved_at`, so a
  reader can check the baseline — shows added and removed lines only inside DEC-174's evidence
  paragraph: no line of the DEC-174 heading, the three-bullet defect list, the "Self-hosting caught
  none of these" paragraph or the carve-out table appears as a `+`/`-` line.
  verify: inspection
- SC-04: `bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` exits 0 with
  `test_committed_index_matches_a_fresh_regeneration` and
  `test_no_amendment_construct_survives_in_the_authority` both `ok`
  (`tests/integration/test-gen-decisions-index.py:339,836`) — the index matches a fresh
  regeneration and the correction introduced no amendment construct. The runner is a bash
  script (`run-unit-tests.sh:1`), so it is invoked with `bash`, never `python3`. Baseline: run
  in this worktree on 2026-09-06 at `41c16c7`, pre-correction, it exited 0 with both tests `ok`;
  it still discriminates, because lengthening DEC-174 without regenerating `DECISIONS-INDEX.md`
  reddens `test_committed_index_matches_a_fresh_regeneration`.
  verify: automated      evidence: integration
- SC-05: `git diff --name-only 41c16c7..<review_sha>` lists no path outside these three plus this
  feature's own directory: `.harness/harness/docs/DECISIONS.md`,
  `.harness/harness/docs/DECISIONS-INDEX.md`,
  `.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md`.
  `41c16c7` (`41c16c736e3cc4b2b331757081c90a24f2ba977d`) is the branch base recorded at `plan.yaml`
  `lanes.resolved_at`, the same baseline SC-03 grades against. It replaces
  `git merge-base origin/main <review_sha>`, which is not a usable baseline here: measured on
  2026-09-06 in this worktree at `41c16c7`, that merge-base is `8bdc2477` and the range already
  lists three foreign paths from pre-existing ship commits
  (`BUG-440-digest-verdict-reconciliation/plan.yaml`, `FEAT-55-issue-types-created-work/feature.json`,
  `FEAT-55-issue-types-created-work/plan.yaml`), which no task in this feature can affect.
  verify: inspection
- SC-06: Reading both corrected passages, the operator confirms the correction says what he meant,
  rewrites no ruling, and reads as current truth rather than as an apology appended to history.
  verify: uat

## Verification gaps

- `test_matrix.docs.always` is `[]`, so this change requires no test kind. Both tasks are
  `change_type: docs`: every changed file is a record under `.harness/`, no runtime code is touched,
  and the deliverable is prose. SC-04's evidence is an EXISTING integration suite that already
  asserts the index invariant — this feature adds no test, and none is required.
- `component`, `ui` and `typecheck` carry `cmd: null` (`status: unresolved`) and `eval`/`functional`
  are `excluded` with `signed: DEC-187`; none covers a surface this change touches, so nothing rests
  on a null runner.
- The wording of a decision record cannot be graded by any runner. SC-01..SC-03 are inspection and
  SC-06 is the operator's read; that is the whole of the correctness evidence for the prose itself.

## Constraints

- **DEC-205 — BLOCKS.** `DECISIONS.md` states current truth: a correction rewrites the entry it
  corrects and never appends a dated sub-section beside it. So DEC-174's correction is an in-place
  rewrite of the evidence sentence, not a note under it. Enforced mechanically:
  `test_no_amendment_construct_survives_in_the_authority` rejects a `**Amendment` line
  (`tests/integration/test-gen-decisions-index.py:836-870`).
  The enforcement layer says the same of the other record: `check-domain.sh:1798-1800` denies an
  over-budget FEAT-05 `STATE.md` with "STATE.md is {n} lines — budget is 120. It holds no history:
  ## Current is replaced, never appended." That sentence is the rationale attached to the
  LINE-BUDGET denial message, not a standalone rule elsewhere in the file, so read it as the
  enforcement layer's own characterisation of `STATE.md` as a current-truth record — not as an
  independent prohibition on appending. Both records are current-truth records by their own
  enforcement, which is why D-01 corrects both in place rather than appending a dated note beside
  the false claim.
- **DEC-150 — BLOCKS.** `FEAT-05-pyyaml-file-parsers/STATE.md` is already 165 lines against the
  120-line budget and carries 7 `##` sections against the two the vocabulary allows
  (`check-domain.sh:1798-1805`). A `Write` of it is denied pre-hoc; only `Edit` is not
  (`check-domain.sh:1820-1824`). The correction is therefore an in-place `Edit` of lines 14-15 and
  adds no section. The pre-existing over-budget state is left as it is: shrinking a completed
  feature's record is out of scope, and the PostToolUse shape report that fires on it is expected
  and non-blocking.
- **DEC-174 — SUPPLIES.** It is the entry under correction. Its ruling — the harness plans its own
  work but does not execute changes to its own gates — is untouched by this feature.
- **DEC-179 — SUPPLIES.** Routing is resolved at plan time; `check-domain.sh --resolve` gave
  `harness-documentor` for both `docs/` paths and `harness-orchestrator` for the FEAT-05 `STATE.md`.
- **DEC-217 and `harness.json` `test_matrix` — SUPPLIES.** They are why `docs` requires no kind; see
  Verification gaps.
- **DEC-120 — BLOCKS.** Only the main session records approval. `## Approval` stays `pending`.
- Out of scope, by the user's settled call: issues #201 and #206 are separate later flows, and no
  new index-drift check is introduced here.

## Approval

status: pending
