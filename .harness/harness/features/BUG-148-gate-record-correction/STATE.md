# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-06-08-validator/state.yaml
- squad: none (validate phase COMPLETE; the reviewer panel returned and the run is recorded)
- status: validate-complete, awaiting the operator's SC-06 read
- station: review (`plan.yaml` `status: review`, unchanged — `done` is written at ship).
  `gh-sync.py status <dir> review` re-run idempotently before the panel: parent #1417 and
  sub-issues #1418/#1419 all confirmed at review.
- review_sha: `87e60330104e63b2efa366852a5e514f8eb73b36`, UNMOVED through this phase. The three
  commits after it (`0591c878`, `633ca8e2`, `43b4a4cd`) touch only this feature's own STATE.md,
  feature.json and observations, so the pin still carries the whole product diff.

**The panel PASSED, clean.** `runs/2026-09-06-08-validator/digest.md` (harness-validator-lead,
`review` team at cycle 0): four reviewers ran, none skipped, `severity_max: info`, `must_fix: []`,
`matrix_ok: true`, **0 send-backs** — `cycles_used` stays 4 of 10. Each reviewer's note is at
`notes/review-harness-<persona>-c0.md`.

- code (`harness-code-reviewer`) PASS — SC-01/02/03/05 met, every clause read separately and
  whitespace-normalised; the DECISIONS-INDEX regeneration proven anchors-only by an `:NNN`-normalised
  full-file diff that came back EMPTY; D-05 ruling 3's same-mechanism-same-terms confirmed by
  side-by-side read, which is the only evidence that property can have.
- qa (`harness-qa`) PASS, GATE-ONLY — `docs` required-kind set `[]` re-derived independently against
  the pinned diff and `harness.json:238`. SC-04 AUDITED, not executed, by the operator's ruling for
  this phase; cited to `notes/qa-BUG-148-2026-09-06.md:44-54`, with the transfer to this pin proven
  by an empty `f60d5d27..87e6033` stat over the three product paths.
- security PASS — no security surface; secret-shape census clean; the quoted-sha/code-line
  disclosure question answered in both directions and dismissed.
- ui PASS — scoped out on a measured extension census (every changed file `.md`/`.json`/`.yaml`),
  not on a guess.

**SC states at `87e6033`:** SC-01 met · SC-02 met · SC-03 met · SC-04 met (audited) · SC-05 met ·
**SC-06 NOT MET — the operator's UAT read, the one remaining gate.** No UAT artifact exists on
disk; it is being obtained separately and is not fabricated here.

Evidence measured by this orchestrator in this worktree, independently of every digest, at the pin:
- SC-01: `Every gate was green` ABSENT from the `## DEC-174`..`## DEC-175` region; all four required
  facts present after whitespace normalisation (the prose is hard-wrapped, so a raw substring test
  gives a false negative on `--check` was never a / supported mode).
- SC-02: `All four gates green` absent, `--check` 0 gone from the gate list, all four facts plus
  `2026-09-06` present; file still 170 lines / 7 `##`, i.e. the pre-existing shape left as found.
- SC-03: one hunk at `@@ -4305,8 +4305,16 @@`, entirely inside DEC-174's evidence paragraph.
- SC-05: 23 paths — the three allowlisted records plus 20 inside this feature's own directory.

**REQ-04 closed at rung 1, not returned to the operator.** The panel's only open question (F-A,
info) was that `no historical artifact is modified` is graded by no criterion, since SC-05 admits
this feature's whole directory as a class. Measured here: `git diff --name-status 41c16c7..87e6033`
shows every one of the 20 feature-dir paths as `A`, and exactly three `M` entries — the two
`docs/` records and `FEAT-05-pyyaml-file-parsers/STATE.md`, which ARE the correction. No historical
artifact was modified. The validator lead holds no shell, which is why it could not close this itself.

## Open Questions

- Q1 (RESOLVED at rung 1): SIMPLIFY's altitude angle asked whether FEAT-05 `STATE.md`'s bold
  `Corrected 2026-09-06 under BUG-148:` lead-in narrates where DEC-174 states. Premise fails —
  D-05 ruling 1's "treatment" is the in-place mechanism, not the rhetorical register, and REQ-01
  positively requires the FEAT-05 record to name the date. The register itself is what SC-06 puts
  to the operator; carry it into that read rather than pre-deciding it.
- Q2 (non-blocking, harness defect): DEC-153's disposable-worktree perturbation carve-out is
  unreachable for `harness-qa` on any non-`tests/**` path — both guards deny, and a self-created
  sibling worktree is refused under DEC-218 claim binding.
- Q3 (non-blocking, harness defect): `harness-digest-dev` forbids `suite: n/a` with `VERDICT: PASS`
  (DEC-173), but a read-only reviewer dispatch runs no suite, so an honest reader has no legal value.
- Q4 (non-blocking, advisory): of SC-04's two named tests only
  `test_committed_index_matches_a_fresh_regeneration` was proven red-capable;
  `test_no_amendment_construct_survives_in_the_authority` was observed green, never perturbed. The
  panel dismissed it as non-gating on a stronger ground than QA's own — both edits are in-place
  rewrites per D-01, so this diff cannot newly violate the property. Backlog row candidate.
- Q5 (non-blocking, the main session's act): the untracked source copy of the grilling artifact
  under `.harness/harness/notes/` was removed on purpose and MUST NOT be restored.
- Q6 (non-blocking, harness defect): `handoff_done_when.py::_feature_dir` cannot resolve `brief-sc:`
  or `plan-task:` pointers for a feature whose directory lives only in a worktree — it strips the
  `.claude/worktrees/<name>/` prefix and rejoins to the MAIN checkout root. Both handoff notes cite
  `finding:` and `approval:` pointers instead, which resolve against the same root.
- Q7 (non-blocking, gap in this BRIEF, for the ship record): REQ-04's `no historical artifact is
  modified` had no criterion grading it. It holds on measurement (see `## Current`), but a future
  BRIEF of this shape should carve the feature's own directory out of the allowlist or state the
  clause as its own SC. Backlog row candidate.
- Panel findings `PF-a2df57f48de3e81d49745cfd1adaa20b` (med, accepted-by-design, disclosed in
  BRIEF's Verification gaps) and `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` (low, informational) remain
  open by design; neither was ruled on and neither gates.
