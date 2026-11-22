# Build ruling by delegated authority — FEAT-2337 — 2026-11-22 — fix-run receipts

Authority: the operator's delegation, recorded in `notes/answers-2026-11-22-signoff.md`.
Ruled by `fable-advisor` (`AdvisorB3FixRun`). The question was raised by the T-03 builder.

**Gap.** T-02 (06b60905) binds a qa unconditional PASS to the *registered* `review_sha`. A
receipt passes only at that pin, or at a descendant whose intervening commits touch only the
feature's directory. `teams/fix.yaml` runs the dev's fix and then QA over the fixed tip in the
same validator-lead run, and the orchestrator re-pins only after the lead returns (build-phase
step 6). So every fix-run qa PASS is refused. QA then has no legal green digest (`matrix_ok`
n/a or false beside PASS is rejected), and every fix run returns FAIL whether or not the fix
worked. Neither the BRIEF nor the plan considered fix runs.

**Ruling: A — fix it in code**, as a T-02 follow-up within T-02's own `files:`, recorded as a
deviation:

- **Detecting a fix run.** The registered run id from `digest_destination.registered_destination`
  must have the shape `fix-c<N>-validator`, and the payload's dispatch-forwarded
  `harness_mission == "fix"` must corroborate it. Both must be present and agree, or the PASS is
  refused. The classification never comes from the digest object, the receipt JSON or anything
  the lead writes.
- **Which commit counts.** In a fix run, `tested_commit` must equal `git -C <trusted root>
  rev-parse HEAD` (the same runtime-derived root), and `review_sha` must be its ancestor
  (`merge-base --is-ancestor`), with a clean working tree. The lead's reported head (state.yaml
  `head_sha`, digest headline) is never the anchor. Coverage, schema-1, exit-0, all-pass and
  empty-claim refusals are unchanged.
- **Validate runs** keep the strict rule: the exact pin, or a feature-directory-only descendant.
- **Records.** DEC-255 states both rules. BRIEF SC-06 gains an amendment line for the fix-run
  clause. T-02's receipt-case table gains these rows:
  - positive: a fix-slug run with a code-changing descendant that equals HEAD;
  - negative: tested ≠ HEAD;
  - negative: divergent history;
  - negative: a validate-slug run with code changes, still refused;
  - negative: the run slug and the mission disagree;
  - negative: a dirty working tree.

**Out of scope, recorded as an open question.** A second, pre-existing binding fails the same
way. `_head_is_pin_error` requires every code-reviewer's `reviewed` head to equal the recorded
pin, and `harness_review_pin` cannot override it. So a fix-run `code` step re-verifying the
fixed tip is also refused. FEAT-2337 did not create this and does not fix it: DEC-255 names it
as an open question, filed as a backlog bug. Fixing only the QA receipt binding does not make a
fix run pass end to end.
