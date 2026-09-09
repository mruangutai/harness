# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: .harness/harness/features/FEAT-104-strict-digest-schema/runs/paneltranscribe-c1b-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE, at the operator signature gate. BRIEF.md and plan.yaml are drafted and
`pending`; only the main session signs. The three-segment plan panel ran: pm's goal-check
(FAIL, six findings, all closed in `planfix-c1`), the two adversarial readers (`fable-advisor`
and `harness-code-reviewer`, both ran, four surviving findings, `severity_max: high`), and the
transcription into `plan.yaml`'s `panel` key with all three readers recorded.

PF-4bd91290deaf98062943319ff3ea5641 is high and GATING — the git-show base-revision pin
contradicts this repository's own vendored-fixture ruling, and CI clones shallow today. Under
DEC-176 it enters the operator's one batched signature review; neither the orchestrator nor pm
may accept its risk.

Signature packet: `notes/ship-review-plan-signature-c1.md`. cycles_used 2/10, runs 6/20.
Next on approval: `gh-sync.py open`, then the build phase (a new orchestrator, per DEC-159 —
plan ends at the user gate).

## Open Questions

- OD-1 PF-4bd91290deaf98062943319ff3ea5641 (high, gating): accept the vendored-fixture remedy
  rewriting SC-06 / T-01 PART 6 / T-08, or overrule with a recorded reason. Blocks signature.
- OD-2 PF-d2cefa75a1931540efa60d3561f7df6b (med): drop the three observed-traffic PASSTHROUGH
  rows, or record why D-02 overrides REQ-04's documented-block-only sentence.
- OD-3 PF-4d84bb7e52beff3ee62eb98a7115ae9e (low) and OD-4 PF-7469688fee994f7ec08ad85dea1d1f8b
  (low): two one-sentence wording corrections, to T-01 PART 1 and SC-11.
- OD-5: keep or strike T-02, retained at `status: abandoned` (see backlog B-1 — it costs a false
  INV-26 red).
- OD-6: T-09 corrects one falsified clause in DEC-126's Applied record; the decision log is touched.
