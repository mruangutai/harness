# Ship review — FEAT-71 corpus independence

**Ready to ship.** At review_sha `5a2edb72`, Harness no longer depends on any prior feature's corpus
data, and `.harness/harness/features/` holds exactly five folders. Every gate and the full suite
(141 files) pass in a standalone clone. The validation panel is clean after one fix round, inside the
signed ruling (2 rounds / 90 min).

No report round was spawned. Assembled from the digests on disk:
`runs/2026-11-07-01-product/digest.md`, `runs/2026-11-07-02-product/digest.md`,
`runs/validate-validator/digest.md`, `runs/fix-c1-validator/digest.md` (all under this feature dir).

## Done when — graded

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator** — I can retain only this intake and the three recent Harness features, remove old project records, and obtain complete green merge evidence from an independent checkout without masking failures. | met | SC-01, SC-05 | `notes/merge-5a2edb72….log` (standalone clone, exact five survivors, all five gates); `notes/record-deletion-receipt.md`; goal-check `notes/research-FEAT-71-corpus-independence-goalcheck-validate-c0.md` |
| **code maintainer** — I can exercise the same contracts with synthetic fixtures instead of historical feature data, retain the useful accessor reproduction, and follow surviving documentation without deleted-folder pointers. | met | SC-02, SC-03, SC-04 | `notes/red-first-S1a.md`, `-S1b.md`, `-S2.md`, `-s3.md`, `-s4.md`; QA c0/c1 notes; `notes/omp-session-accessor-live-2026-11-07.md` |

(Survivors are five, not four: the operator added BUG-20261006-fleet-planning-recovery, which merged
mid-flight — `notes/answers-2026-11-07-02-product.md`.)

## What changed

- **Grandfather mechanisms deleted; rules now uniform:** `RUNS_AGENT_EXEMPT`, `BUILD_ENTRY_ERA_EXEMPT`,
  `HANDOFF_EXEMPT_LITERAL`, `handoff_done_when_baseline` (146 paths), `BRANCH_ERA_EXEMPT`.
- **Tests:** live-corpus reads, real-id fixtures and both corpus-size floors replaced by synthetic
  fixtures with asserted non-vacuity; canonical-reader classification no longer points at other
  features' plans (ownership is opt-in per row).
- **Probes:** BUG-1898 and FEAT-1928 live probes and their test kinds deleted, with the DEC-204
  merge-gate sentence; the FEAT-44 accessor probe moved byte-identical to `tests/manual/`.
- **Docs:** paths/anchors into deleted folders rewritten; truth updates for the removed mechanisms in
  DEC-159, DEC-213, DEC-215, DEC-220, DEC-250; index regenerated.
- **Pruned:** 120 feature folders, 148 tracked log/note records, and 9 operator-authorized local
  records in the main checkout (checksums in `notes/record-deletion-receipt.md`).

## Lead summaries

- **Product (intake, two runs)** — `runs/2026-11-07-01-product/digest.md`, `runs/2026-11-07-02-product/digest.md`:
  49-line BRIEF, one main-session-direct T-01; then the five-survivor amendment.
- **Validate c0 (BLOCKED)** — `runs/validate-validator/digest.md`: all SCs met, but CR-01
  (grade-1 test function, high) and Q-1 (touched locally-run kind had no recorded run).
- **Fix c1 (PASS)** — `runs/fix-c1-validator/digest.md`: CR-01 fixed at `5a2edb72`; Q-1 discharged by a
  live run recorded on both baseline and feature (identical, pre-existing probe defect). No must-fix.

## Open questions and escalations

None open. Q-1 resolved by measurement, not waiver.

## Spend and ledger

4 runs · 32 wall-clock min · 16 rework min · 1 of 2 rework rounds · tokens unmeasured (null — see
B-2) · `cycles_used` 1 / 10 · 6 judgements.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-07T14:34:19.907502+00:00 | T-01.intent | operator answer: fifth survivor BUG-20261006 | — |
| 2026-11-07T14:34:40.674514+00:00 | T-01.verify | operator answer: fifth survivor in the exact-set assertion | — |
| 2026-11-07T14:43:13.689694+00:00 | T-01.verify | builder-learned: fresh clone has no core.hooksPath (INV-31) | — |
| 2026-11-07T14:58:27.118126+00:00 | T-01.verify | builder-learned: feature-branch clone has no local main (INV-29) | — |
| 2026-11-07T15:07:25.276187+00:00 | T-01.verify | builder-learned: local main = feature tip to model the post-merge tree | — |

overrule rate: 0/5

## Operator notes

- Main-session dispatches bypass the return hook in this host (B-2): every lead return was validated
  with `validate-digest.py` and appended with its own writer by the main session
  (`notes/intake-record-provenance.md`). That is also why tokens are null.
- `verify` exits were 0 at `3e6add2a` and `5a2edb72`; the tee'd logs carry no final exit marker
  (B-6). An earlier non-hermetic run was polluted by the main session's exported
  `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR`.
- Until this merges, `check-state` in the main checkout reports INV-52 (FEAT-02 and
  FEAT-03-subissue-mirror share a branch) because the era exemption is gone and those folders still
  exist on `main`. The merge removes both.
- Not this feature's: INV-25/INV-29 for `/private/tmp/probe-6f6166a9` and the `BUG-2180` worktree
  belong to other sessions.
- Kaya's in-flight FEAT-01-kaya-platform lost its accidental FEAT-01 prefix exemption from INV-17;
  measured: it is at `ready` with a five-section handoff-plan, so nothing fires today.

## Proposed backlog

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `probe-omp-session-accessor.py` case3 has a stale premise (omp 18.18.0 defines `getContextUsage` in subagents); identify the subagent by nested session-file shape so cases 4–6 run. |
| B-2 | bug | Main-session dispatches in this host don't match the hook's `ompMainTask` tool name, so no schema-control refusal, no claim, no validated digest append and no token stamp. |
| B-3 | chore | `test-check-state-handoff.py:case_t14_exempt_shape` is grade 2 (CR-02 advisory). |
| B-4 | chore | `test-post-merge-sweep.py:_t07_sweep` is grade 2 (CR-03 advisory). |
| B-5 | chore | Two unit copies of the module feature-id collector remain (no unit test-support module exists); the three integration copies share `feature_id_probe_support.py`. |
| B-6 | chore | Make T-01-style standalone verifies hermetic (unset project-dir env) and append a final exit marker to the tee'd log. |
| B-7 | chore | `docs/invalid-states-audit.html` still describes the deleted runs-agent exemption map (dated audit snapshot). |
| B-8 | bug | The build-phase seam order (#2012: seam commit → pin → `gh-sync status review`) flips `plan.yaml`'s station after the pin, so INV-33's byte comparison reports every reviewed feature's pin STALE until it reaches `done`. FEAT-71 reports it now at `5a2edb72` (only change: `status: building → review`). |
