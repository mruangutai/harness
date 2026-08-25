# Amendment 2 — grading D-10's repository-level failure posture (FEAT-34, 2026-08-24)

**BLUF.** `BRIEF.md` gains one criterion, `SC-15`, `verify: automated`, `evidence: integration`,
grading D-10's three-way posture with each branch asserted separately. Amendment 2 is **purely
additive** — no existing REQ or SC is edited — and it needs one re-signature. `## Approval` is
untouched and is now stale. `plan.yaml` was not opened for writing.

## The gap, re-checked at source (not adopted from the dispatch)

- `BRIEF.md` `SC-04` (pre-amendment lines 179-182): grades only the POSITIVE second-repository case
  — a `Done` feature in a second repo producing an `INV-29` finding. **Confirmed, verbatim.**
- `BRIEF.md` `REQ-04` (lines 62-63): "with no per-repository exception to remember or later remove".
  **Confirmed.** No criterion in `SC-01`..`SC-14` names an absent checkout, an unenumerable checkout
  or a fleet load failure. A silently skipped repository passes the signed brief.
- Highest ids before this amendment: `SC-14`, `REQ-13`. **Confirmed.** New criterion is `SC-15`.

## Why one criterion, not three

The three branches share one fixture, one call and one command, and the brief's own established shape
for multi-branch posture is a single criterion with clauses asserted separately — `SC-12` and `SC-13`
are both written that way. Splitting into three would triple the grading surface without adding a
single distinct piece of evidence. The separate-assertion requirement lives inside `SC-15`'s text,
which is where it binds the grader.

## Why no new requirement

`REQ-04`'s no-exception clause already commits the outcome. A new REQ would restate it more narrowly
and give the goal-check two homes for one commitment. What was missing was falsifiability, which is a
criterion's job.

## Evidence reachability — checked, not assumed

- Evidence command is T-02's `verify:`, cross-checked against `plan.yaml`: it is exactly
  `python3 .claude/skills/harness/bin/test-worktree-terminal.py`. **No mismatch.**
- `evidence: integration` is live: `harness.json` `test_kinds.integration.cmd` is
  `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` (non-null), its `detect` list
  names `.claude/skills/harness/bin/test-worktree-terminal.py`, and `run-unit-tests.sh:18`
  `INTEGRATION_SCRIPTS` contains the same basename. The kind reaches the file on both routes.
  `component`, `ui`, `eval`, `typecheck` and `functional` remain `cmd: null` and are not used.

## Does `case_second_repo` really supply what `SC-15` needs

**Shape: yes. Arrangement: no — and that arrangement is T-02's, already commissioned.**
`case_second_repo` in `test-worktree-terminal.py` builds a probe root with
`.harness/harness/docs/SPEC.md`, a `workspace_root`, a `.harness/factory/fleet.yaml` declaring ONE
repo (`acme/second-repo`), a real second git repository with a landed `Done` feature and a real
`git worktree add`, and runs the call in a fresh subprocess with `CLAUDE_PROJECT_DIR` set. Branches
(j)/(k)/(l) each need new arrangement on that shape, not a new shape: a second `repos` entry with no
directory; a third entry whose directory exists as a plain non-git directory; and a re-write of the
probe `fleet.yaml` to unloadable bytes plus a second subprocess call. All inside T-02's granted file.

**Honest caveat, non-blocking.** Today the probe root is NOT itself a git repository — nothing calls
`_repo(probe_root)`. `classify_all(root)` returns `classify(root)` for the harness checkout, and
clause (c) of `SC-15` requires the harness checkout's own records to still come back. Whoever builds
(l) must make the probe root a real git repository, or pin what "the harness root's own records" is
in a fixture where the root cannot be enumerated. That is fixture arrangement inside T-02's file, so
it needs no plan edit.

## Open items

- The `## Approval` block still reads `amendments-signed: Amendment 1`. Re-signature required before
  ship; the main session owns that block.
