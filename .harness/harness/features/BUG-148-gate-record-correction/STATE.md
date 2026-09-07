# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-07-01-product/digest.md
- squad: none (cycle-5 wording fix landed; validate remains complete)
- status: validate-complete, awaiting the operator's SC-06 re-read of the shortened DEC-174 passage
- station: review (`plan.yaml` `status: review`, unchanged — `done` is written at ship)
- review_sha: **re-pinned to `651e60e24f4181a8a29bcaf8d6719a3636fb59f7`**, the cycle-5 commit,
  because the wording fix moved the product diff off `87e6033`. `cycles_used` 4 → **5** of 10.

**Cycle 5 — the operator's SC-06 read: facts accepted, wording too long.** One dispatch,
`runs/2026-09-07-01-product/digest.md` (harness-product-lead → harness-documentor), PASS, 0
send-backs; the cycle is charged to the operator's send-back itself, not to the run.

DEC-174's evidence paragraph is now **88 words over 8 lines, from 115 over 10** (−23%). The words
came out of exactly three places, all narration rather than fact: the quoted commit subject
`"perf(140): validate argv so --help stops rewriting the index"`, the source line
`stdout_mode = "--stdout" in sys.argv[1:]`, and the trailing hedge `one way or the other`. Every
required fact stands — three genuinely green gates named, `--check` never a supported mode, the
pre-`ffbdbfa1` (2026-08-05) fall-through to the WRITE path and its exit 0, the regeneration that
overwrote exactly the drift a check would have reported, and the read-only
`--stdout | diff` form — and the paragraph still ends `while:` so the three defect bullets read as
its continuation.

Measured by this orchestrator in this worktree at `651e60e2`, independently of the digest:
- T-01's verify verbatim: `Every gate was green` ABSENT from the `## DEC-174`..`## DEC-175` region;
  all five required strings PRESENT after whitespace/markup normalisation.
- `tests/integration/test-gen-decisions-index.py` exit **0**, 14 `ok`, including
  `test_committed_index_matches_a_fresh_regeneration`, `test_no_amendment_construct_survives_in_the_authority`
  and `test_preserves_hand_written_rulings_by_dec_number` (SC-04's evidence, re-run at the new pin).
- SC-03 shape: **one hunk**, `@@ -4306,13 +4306,11 @@`, wholly inside the evidence paragraph.
- SC-05 shape: two modified product paths only — `DECISIONS.md` and `DECISIONS-INDEX.md`; the index
  diff is **anchor-only** (normalising `@[0-9]+` → `@N`, zero unpaired changed lines), and DEC-174's
  own row keeps `@4302` and its hand-written ruling verbatim.
- **FEAT-05 `STATE.md` byte-identical**: `git status --porcelain` on that path returns zero bytes,
  and it is absent from the cycle-5 commit's file list. It was read, never edited.
- DEC-174's ruling paragraph, carve-out table, three defect bullets, gate's-test argument and
  enumerated enforcement layer are unchanged; the region diff touches none of them.
- **D-05 ruling 3 is now stronger, not weaker.** The shortened DEC-174 mechanism clause and
  FEAT-05 `STATE.md:14-20` agree almost verbatim ("never a supported mode … an unrecognized
  argument fell through to the WRITE path, so that exit 0 was a regeneration of `DECISIONS-INDEX.md`
  that overwrites exactly the drift a check would have reported; it could not prove index drift"),
  where before they agreed only in substance.

**SC states at `651e60e2`:** SC-01 met · SC-02 met (unchanged file) · SC-03 met · SC-04 met
(re-run, exit 0) · SC-05 met · **SC-06 NOT MET — the operator's re-read of the shortened passage is
the one remaining gate.** No UAT artifact is on disk and none is fabricated here.

**The panel's PASS is recorded honestly.** `runs/2026-09-06-08-validator/digest.md` graded the
PREVIOUS wording at `87e6033`; it was not re-run for a paragraph the operator himself sent back on
length. What carries forward is mechanical and was re-measured above at the new pin; what grades
wording is SC-06, which is exactly the gate still open. If the operator wants the panel re-run over
the new prose rather than his own read, that is one validator dispatch.

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
