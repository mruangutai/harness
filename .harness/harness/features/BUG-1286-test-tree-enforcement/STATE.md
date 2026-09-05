# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: feature-close distillation complete
- squad: none
- status: done

MERGED as `7a5e6cfa` (PR #1301). `gh-sync.py ship` completed, every recorded card reached Done and
milestone #44 is closed. `plan.yaml` station `done`, all five task stations `done`, `pr: 1301`,
`review_sha` `bb3a31ed`, `cycles_used` 11 of 11.

Feature-close distillation ran once per squad, three leads concurrently, each scoped to its own
members' files so no squad's `check-expertise.sh` sweep could read another's mid-write file. Ten
member Expertise files were updated plus the orchestrator's own repository tier (Gotchas 14→15,
Outcomes 0→1). Both corpus-wide `check-expertise.sh` sweeps exit 0; the single ADVISORY line on
`harness-security-reviewer` predates this feature and is a flag for a human, not a violation.

Rejection was first-class: members rejected candidates on merit as already covered by live entries,
and the validation lead recorded its own relay as over-broad rather than smoothing it. Nothing was
manufactured to justify a dispatch.

Run reconciliation, continuing the pre-merge pass: `runs/2026-09-05-04-product` and
`runs/2026-09-05-1-validator` were discarded — both digests fail the lead contract with no
`artifact:` line at all, and each is superseded by a valid successor covering the same single run
(`-05-product`, `-2-validator`). The three distillation runs are recorded. `runs/` is gitignored, so
the deletions appear in no diff, which is why they are written down here and in
`notes/run-reconciliation-2026-09-05.md`.

`notes/handoff-validate.md` was written retrospectively at close and says so: validate and ship ran
in one session, so no note existed at the seam. The checker was right that it was missing.

## Open Questions

- **INV-29 is the one violation left and it is not the orchestrator's to clear**: this worktree
  still stands for a feature that reached a terminal state. Removal is the main session's act from
  OUTSIDE the tree — `git worktree remove` exits 0 from within the tree it deletes. The checker
  itself says to run it from the main checkout. The tree is now committed and clean, so `remove`
  will no longer decline.
- **HARNESS DEFECT, reported independently by all three squads and verified at source: at a full
  Expertise section there is NO legal write.** `harness-distill` mandates displacement;
  `expertise-merge.py` registers only `apply` over a union, where a matching id with new text is
  exit 7 and a new id at cap is exit 8, both writing nothing — and a whole-file write is barred by
  DEC-125. The exit-8 remedy "condense" is itself a replace, so it is unreachable by the same route.
  Cost this feature: roughly ten accepted rules stranded in notes, and capacity rather than judgement
  selected which entries landed. Either `expertise-merge.py` gains a replace/drop verb keyed to an
  existing id, or the distillation contract stops instructing displacement.
- Consequence of the above, needing a drop by whoever holds the pen: `harness-pm`'s repository tier
  now injects a true new entry AND its false predecessor at every spawn, because the corrected entry
  could not be removed.
- Backlog filing is the main session's: `gh-sync.py backlog` for B-13, B-9, B-10, B-11 and B-6, with
  B-4, B-5, B-8 and B-14 consolidated into B-6 and B-7, B-12 and B-15 struck.
- Carried, unchanged: the integration suite is not hermetic against `HARNESS_AGENT_TYPE` (B-13), and
  run-digest hygiene produced four superseded digests written without their contract block across
  this feature.
