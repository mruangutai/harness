# Goal-check — BUG-148-gate-record-correction — delivery, cycle 5

**BLUF: all six criteria MET at `review_sha = 651e60e24f4181a8a29bcaf8d6719a3636fb59f7`.**
SC-01..SC-03 and SC-05 freshly measured here by their own declared git commands; SC-04 freshly run
(runner exit **0**, `^FAIL ` lines **0**, both named tests `ok`); SC-06 is a transcription of a UAT
performed in cycles 4 and 5 (`notes/uat-BUG-148-sc06-c5.md`) — the sole authorised non-measurement.
`must_fix: []`. REQ-01..REQ-05 are each traceable to the two corrected passages graded below.

All commands run with `git -C <worktree>` / from inside the worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-148-gate-record-correction`.

| SC | verify | verdict | command run (verbatim) | observed |
|---|---|---|---|---|
| SC-01 | inspection | **met** | `git show 651e60e2…:.harness/harness/docs/DECISIONS.md \| sed -n '/^## DEC-174/,/^## DEC-175/p'` then one grep per required fact | region = 129 lines. `Every gate was green` count **0** in-region. Each fact present separately: unsupported-mode (region L9), pre-`ffbdbfa1` (2026-08-05) write-path fall-through (L9-10), "could not prove index drift" (L10-12), `--stdout \| diff - .harness/harness/docs/DECISIONS-INDEX.md` (L13) |
| SC-02 | inspection | **met** | `git show 651e60e2…:.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` then one grep per required fact | 170 lines. `four gates` **absent**; file reads "**Three gates green:**" (L14). Each fact present separately: never a supported mode (L16-17), `ffbdbfa1` fall-through to WRITE path (L17-18), could not prove index drift (L19), `--stdout \| diff` form (L20), correction date `2026-09-06` (L15). The one `gen-decisions-index.py --check` mention (L16) is inside the correction ("was no gate at all"), not a claim |
| SC-03 | inspection | **met** | `git diff 41c16c736e3cc4b2b331757081c90a24f2ba977d..651e60e2… -- .harness/harness/docs/DECISIONS.md` | exactly one hunk, `@@ -4305,8 +4305,14 @@`: 2 `-` lines and 8 `+` lines, all inside the evidence paragraph. No `+`/`-` line touches the DEC-174 heading, the three defect bullets, the "Self-hosting caught none of these" paragraph or the carve-out table (all appear as context or outside the hunk) |
| SC-04 | automated (integration) | **met** | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration`, `rc=$?` | **runner exit status = 0**; `^FAIL ` line count = **0**; `ok - test_committed_index_matches_a_fresh_regeneration` and `ok - test_no_amendment_construct_survives_in_the_authority` both present (output L884, L888). 69.7 s wall |
| SC-05 | inspection | **met** | `git diff --name-only 41c16c736e3cc4b2b331757081c90a24f2ba977d..651e60e2…` | 30 paths. Outside the feature's own directory: exactly the three allowed — `docs/DECISIONS.md`, `docs/DECISIONS-INDEX.md`, `features/FEAT-05-pyyaml-file-parsers/STATE.md`. The other 27 are all under `features/BUG-148-gate-record-correction/` |
| SC-06 | uat | **met** | no command — transcription of performed reads; see `notes/uat-BUG-148-sc06-c5.md` | FEAT-05 passage read by the **operator** at cycle 4: facts accepted, only the DEC-174 passage sent back, on length. Shortened DEC-174 passage read at cycle 5 by **`fable-advisor`** under the operator's standing authorisation, relayed by the main session as binding: "SC-06 UAT PASS: the shortened DEC-174 passage is factual, concise, preserves the ruling/carve-out, and reads as current truth." The operator did **not** read the shortened passage |

## Provenance notes for the ship record

- **The working tree matches `review_sha` on every graded product path.** `git status --porcelain`
  over `.harness/harness/docs` and `features/FEAT-05-pyyaml-file-parsers` returns zero bytes, and
  `git diff --stat 651e60e2..HEAD -- .harness/harness/docs` is empty. So SC-04's working-tree run
  is a run of the reviewed content (this is the reason the run is a measurement, not a claim).
- **The dispatch's "exactly one later commit" understates it.** `651e60e2..286048c3` is **four**
  commits touching **five** files (`STATE.md`, `feature.json`, `notes/handoff-validate.md`,
  `notes/qa-digest-repair-verification-2026-09-07.md`,
  `observations/harness-orchestrator.md`) — all inside the feature's own directory, no product byte
  changed. The correction to the count does not change any verdict; recorded so the ship record is
  accurate (`git diff --name-only 651e60e2..286048c3`).
- **Nothing here was graded from another agent's claim.** The cycle-5 figures in the feature's
  `STATE.md` `## Current` agree with these independent measurements; they were not their source.

## Open questions carried, not resolved here

- Q4 (advisory, from `STATE.md`): of SC-04's two named tests only
  `test_committed_index_matches_a_fresh_regeneration` was ever proven red-capable;
  `test_no_amendment_construct_survives_in_the_authority` has only ever been observed green. SC-04
  as written asks for `ok`, which it has — the criterion is met on its own words; the fragility is a
  backlog row, not a gate.
- Q7 (gap in this BRIEF): REQ-04's "no historical artifact is modified" has no criterion grading it.
  It holds on the SC-05 measurement above (every non-allowed path is this feature's own), but a
  BRIEF of this shape should state it as its own SC.
- The reviewer panel's PASS graded the **previous** wording at `87e6033`; the wording now in the
  authority is carried by SC-06's advisor read, not by the panel. Ship on that basis knowingly.
