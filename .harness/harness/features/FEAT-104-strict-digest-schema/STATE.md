# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: 2026-09-09-03-simplify-eng — the last of three this cycle
- squad: eng (simplify); product and validator also ran
- status: build complete, review-ready

**The build phase is DONE.** All nine planned tasks carry `status: done` in `plan.yaml`, the
blocking `qa_gate` PASSES, and the mandatory SIMPLIFY pass has run with nothing in `must_fix`.
The review-ready boundary is `ce1fd115`. `review_sha` is NOT pinned — pinning it, and running
`gh-sync.py status <dir> review`, are the validate seam and belong to the main session.

T-09 landed as `50c4bce9`: DEC-223 appended (the closed digest contract, the DOCUMENTED_OPTIONAL
and PASSTHROUGH tables, `adequacy_notes` required of every lead closing issue 37, the 22-key run
step shape with its governed `evidence` container gated on `schema_version` 2, and the
`stop_hook_active` hole named), DEC-126's falsified `adequacy_notes` clause corrected in place
under DEC-205, and DECISIONS-INDEX.md regenerated. Its own `verify:` exits 0 with an empty diff.
The plan's line anchors into DEC-126 were stale by two lines; the clause was identified by content
instead, and the devs and reviewers bullets are byte-unchanged.

Three commits after it are the main session's own, under the DEC-174 carve-out: `9be1d722`,
`9fc8543f` and `1a66d2cc` reset and reapplied enforcement-test repairs a team agent had authored,
and `ce1fd115` applied the one worth-doing simplify finding (a duplicated `iter_errors` call in
check-domain.sh). The full suite is green at that tip:
`env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh` exits 0 over 106
files, measured by this orchestrator both before and after the simplify apply.

Three simplify recommendations remain UNAPPLIED and gate nothing. S2 is the strongest — one run
state shape, two hand-written enforcement layers whose rejection messages have already drifted
inside this diff's own two files. S4 is a restatement in two lead agent files that those same files
say they do not make. S3 (the top-level key set triplicated across three sites) is pre-existing and
outside this diff — a backlog row. The main session may land S2 and S4 directly under DEC-174
before pinning, or carry them as briefing rows.

cycles_used 7/10 — three send-backs this cycle: the product lead's run digest carried
`adequacy_notes` as a prose scalar where the contract this feature itself shipped requires a list;
the QA gate failed its first pass and was re-graded; and that QA run's corrected verdict was written
to a sibling file, leaving the canonical `digest.md` reading FAIL until it was appended to. runs
13/20.

`check-state.sh` exits 1 with sixteen violations, none of them a defect in the delivered work.
One is NEW and self-clearing: INV-6 reports a validator run that graded code while `review_sha`
is unpinned. That is the recorded `qa_gate` run, and the pin is the next act — the main session's,
at `ce1fd115`. It was left unpinned deliberately rather than silenced by writing `code_grade: n_a`,
which would falsely assert the run graded no code. Ten are the known INV-26 card/plan mismatches
(task cards read `building` against a plan reading `done`, and the parent reads `building` against
a derived `review`) because D-23 moves no card to the done station before `gh-sync.py ship` and the
parent moves at validate entry. Five are INV-29 standing worktrees, four belonging to other
features and one — `qa-bug440-c3-probe` — whose terminal status cannot be determined because its
path is not under the worktrees segment.

## Open Questions

- Whether the INV-26 card/plan mismatch is a harness defect rather than drift. D-23 says nothing
  moves a card to the done station before `gh-sync.py ship`, yet INV-26 demands card equals plan
  station the moment a task records `done`. Every task in this feature now trips it. Unchanged from
  the previous cycle and still unanswered.
- Whether INV-6 and the build phase's own shape can both hold. The `qa_gate` is a validator-squad
  run that necessarily grades code, and it runs BEFORE the pin by design — so recording it honestly
  reddens INV-6 for the whole gap between the gate and the validate seam, and the only way to keep
  the gate green is to mis-record the run.
- `check-domain.sh`'s worktree-claim guard is keyed per persona with no per-session identity. A live
  `harness-eng-lead` claim on another feature refused this feature's eng lead its own run-directory
  write, and the same foreign claim under `harness-backend-dev` refused that member's receipt
  outright, while three sibling readers on three other personas were unaffected. Both writes
  succeeded once the foreign claim cleared. Raised by the simplify lead; a harness defect, not a
  finding about this diff.
- Whether a run directory holding a `digest-*.md` sibling beside `digest.md` should be flagged. An
  agent that writes its corrected digest to a new filename leaves the canonical digest carrying a
  stale operative verdict, and no gate notices because that file still validates clean. This cycle
  hit it once and repaired it by appending.
