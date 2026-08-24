# FEAT-26 validate seam — the panel's three must-fixes, and the ship

## Next
Nothing on this feature. It is merged as `5135ed6` (PR #752), `pr` reads `752`, status is Done,
parent #732 and milestone #22 are closed, and #492 closed from the `Closes #492` keyword.

Three things it leaves open, all filed or recorded rather than carried:
- **DEC-186's bound, operator's call.** `record-pr` reads GitHub with `gh pr list --state
  merged`. DEC-186 names four closed read-back purposes and this is not one of them. Both
  readings — widen to five, or rule the mirror outside DEC-186's scope — are in DEC-200.
- **#747** — move `status` out of `plan.yaml`. Filed here, not built here.
- **Q7, non-blocking.** REQ-05 and SC-08 keep pre-amend counts ("eleven", "twenty-three")
  while `## Problem` says twelve of twenty-seven. Deliberate: they describe the plan's
  enumerated scope. The consequence is real and now observed — `FEAT-24` still carries
  `pr: null` and INV-28 names it. That is REQ-04 working, not a defect.

## Trust
- `run-unit-tests.sh --kind all` at merge: **45 scripts PASS, 0 FAIL, exit 0**.
- Goal-check: **11 of 11 signed criteria MET, 0 NOT MET, 0 UNVERIFIABLE**, each row citing a
  command run in the worktree or a `file:line` read.
- `check-state.sh` at merge: one violation, FEAT-34's unsigned BRIEF — a different flow.
- **The seat was proved on itself.** `record-pr` run against this feature's own directory
  after merge resolved `feat/FEAT-26` to `752`. Then `ship` printed `pr already recorded as
  #752 — not overwritten`, which is SC-03 observed live rather than asserted.
- INV-28 emits exactly one line on the shipped tree, naming `FEAT-24`.

## Dead ends
- **A single-line `grep` cannot assert the absence of a sentence that wraps.** T-07's verify
  was exactly that. It returned VERIFY-OK, I reported the task done, and the false sentence
  was still on the page. The rule: **only an *absence* assertion turns a line wrap into a
  false green** — presence assertions break loudly. Grade the pattern's span against the
  matcher's unit, and note which way a failure would point. The repair is a whole-file
  whitespace-normalised check, red-proved in both directions.
- **A fixture keyed on the thing under change grades the change, not the behaviour.**
  `case_749c` probed `source_issues`, the key this feature adds. Green on `main`, red the
  instant the schema change merged. Caught by running the suite **in the worktree**; on
  `main` alone it looked fine. Probe with a key no schema declares.
- **A feature that adds a schema key could not write data using that key.** `check-domain.sh`
  resolves through `CLAUDE_PROJECT_DIR`, so a worktree write was graded against `main`'s
  schema. Not a workaround — filed as #749, fixed, merged as `569d417`. FEAT-26 survived only
  because `--post` reports after the write lands; a `--pre` route on the same rule blocks it.
- **A branch cannot be cut off a closed issue.** The guard refused `chore/492-...` after
  `Closes #492` had already closed it. The open parent #732 is the branch anchor at terminal
  time, not the source ticket.
- **Two lead digests in one day wrote their YAML into the return, not the file.** Both were
  repaired from their own text. A contract problem, not a slip.

## Working set
- `.harness/harness/features/FEAT-26-pr-linkage-recorded/` — `feature.json` (`pr: 752`,
  `status: Done`, `github.source_issues: [492]`), `plan.yaml` (T-01..T-08 all `done`),
  `STATE.md`, and `notes/research-FEAT-26-goal-check.md`.
- `.claude/skills/harness/bin/gh-sync.py` — `record-pr`, `cmd_closes`, `source_issues`
  mirroring, and the docstring's DEC-200 paragraph.
- `.claude/skills/harness/bin/check-state.sh` — INV-28, hand-written under the DEC-174
  carve-out, sitting before INV-25's block.
- `feature-schema.json` — `github.source_issues`; the `pr` annotation names all 3 readers.
- `test-gh-sync.py`, `test-check-state.py`, `test-validate-feature-json.py` — the
  assertions, including `case_749c`'s repaired fixture.
- `.claude/skills/harness/SKILL.md:208-215` — the corrected closing-keyword paragraph.
- `DECISIONS.md` / `DECISIONS-INDEX.md` — DEC-200.
