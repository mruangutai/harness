# STATE

## Current

- feature: FEAT-20-migration-detector
- run: none in flight — returned to the operator for one ruling
- squad: none
- status: awaiting-user

**Phase: validate, complete. The feature is built, both gates passed, and nothing gates the ship
except one criterion that cannot be met as written.** All four tasks done — `14ca661` T-01,
`d3207e7` T-02, `2c35398` T-03, `396f1ad` T-04 — with every `verify:` re-run in this session rather
than read from a receipt. Issues #361-#364 closed; parent #360 on `Review`.

**Blocking qa gate: PASS.** Matrix union `{unit, integration}`, both green, and both registration
greps fired — the part that matters, since a suite exiting 0 without running the new file is this
feature's own subject. **Review panel: PASS**, `must_fix: []`, `severity_max: med`, which under
`advisory_unless_high` gates nothing. **Goal-check: 14 of 15 SCs met**, each verified first-hand at
the pin.

**The one open item, and it is the operator's alone.** The brief's file-boundary criterion (SC-10)
forbids every file outside a closed set of eight — but the harness writes per-feature bookkeeping
on every run, so **no feature can ever meet that sentence literally**; 19 `.harness/` paths changed
here. The feature's *shipped surface* is nonetheless exactly the eight permitted files with zero
renames, which I re-derived myself rather than take from pm: `git diff --name-only 88b1182..434307a`
returns 27 paths, 8 outside `.harness/`, and `--diff-filter=R` is empty. pm recommends signing the
narrower shipped-surface reading and leaving the signed text standing. **I do not mark an SC met,
waived or edited, and neither does pm** — it goes up.

**`review_sha` is `434307a`**, moved from `ea476fd` so the pin names the tree the goal-check actually
verified. The panel ran at `ea476fd`; qa measured the two identical across all eight source files, so
no verdict is affected.

**Budget: `cycles_used` 3 of 10** — two from the plan phase, one from qa's in-run send-back. Both
build dispatches and the panel were clean first passes; an ESCALATE is not rework and added none.
**`len(runs)` 7 of 20**, and a floor, since T-01 and T-02 were main-session-direct.

**Close-out and the CEO briefing are deliberately NOT done.** Close-out is gated on the SCs passing,
distillation happens once and cold, and a briefing written now would be superseded by the ruling it
is waiting on. `notes/handoff-validate.md` carries both branches for the successor.

## Open Questions

**Blocking — the operator's ruling.** The brief's file-boundary criterion forbids the bookkeeping
every feature necessarily writes, so no feature can meet it literally. This one's shipped surface is
exactly the eight permitted files, zero renames, 14 of 15 criteria verified first-hand. Sign the
narrower shipped-surface reading as the recorded ruling with the signed text left standing, or amend
the wording in an approval-gated re-plan. **No shipped code changes either way** (SC-10;
`notes/uat-goalcheck-c0.md`).

Non-blocking, all riding to the briefing's backlog:

- **A session-entry code path that executes files from the scanned tree.** `check-state.sh` runs
  `cd "$root"` before its heredoc, so `sys.path[0]` precedes `PYTHONPATH` and a planted
  `harness_yaml.py` or `layout_migration.py` at `CLAUDE_PROJECT_DIR` runs at every session entry.
  Byte-identical at `88b1182`, so pre-existing and **not** this feature's regression — but it wants
  its own ticket.
- **The approved plan contradicts its own code, and DEC-194 now repeats it.** Both assert every
  finding names the reader path, while the `no-evidence` and `no-rows` causes correctly name none.
  No SC turns on it. Narrow **both** documents, before unit 3 opens, since units 3-7 are told to cite
  DEC-194 as their maintenance contract. pm's to word.
- **The suite is correct-today, not pinned against regression** — a new criterion the brief never
  stated, so not adopted in either direction. First mutation target is named: delete any one of
  INV-27's three unrendered cause branches and confirm the suites stay green.
- **Two harness defects.** `bash-write-guard` refuses redirects whose target is a shell variable and
  refuses the scratchpad path, so the `verify:` clauses are not runnable verbatim. And the playbook
  says to record the phase in `feature.json` `phase:`, which `feature-schema.json` forbids via
  `additionalProperties: false`.
