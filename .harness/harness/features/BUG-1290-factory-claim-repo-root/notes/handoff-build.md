# Handoff — BUG-1290, build → validate (final cycle, tree at 72a97b99) — RECONSTRUCTED 2026-09-08, seq-1

## Next

Pin `review_sha` at `72a97b99`, run `gh-sync.py status <feature-dir> review`, then dispatch the
validation panel through `harness-validator-lead` over the B-27 fix. Input paths: `plan.yaml`
(T-01..T-05, all `done`), `notes/qa-2026-09-06-15-validator.md`, and the two B-27 dev-ops receipts
under `notes/`. SIMPLIFY already ran and applied nothing, so the pin may be taken immediately.

## Trust

- RECONSTRUCTED after the fact, not contemporaneous: no build-seam note was ever written, and every claim below is transcribed from an artifact named beside it — `notes/ship-review-2026-09-06-19-ship.md` row B-24 — verified-at 3faada88
- All five build tasks PASS; claim resolves each candidate's features root from its own repository segment — `notes/build-digest-reconstructed-2026-09-05-07-eng.md` — verified-at 3faada88
- Every `verify:` was re-run by the orchestrator on the committed tree, not accepted from the digest — same digest, "Independent verification by the orchestrator" — verified-at 3faada88
- qa test-matrix gate PASS, graded over the feature diff `main..HEAD` rather than the fix cycle's incremental diff — `notes/qa-2026-09-06-15-validator.md` BLUF and "Matrix resolution" — verified-at 3faada88
- SIMPLIFY was an empty pass: no applyable findings, one backlog-only row noted, both suites re-run green — `notes/receipt-harness-dev-ops-2026-09-06-b27-simplification.md` BLUF — verified-at 3faada88
- HEAD did not move across SIMPLIFY, so the pin is safe to take — `notes/receipt-harness-dev-ops-2026-09-06-b27-verify.md` — verified-at 3faada88
- The literal case-`5b` failure the operator demanded prints: `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed` — `notes/receipt-harness-dev-ops-2026-09-06-b27-simplification.md` — verified-at 3faada88
- The run digests that carried the eng lead's own prose are gone: `runs/` is gitignored and died with the worktree — `STATE.md` `## Current` — verified-at 3faada88

## Dead ends

- Do not widen either layout reader pattern to fit the code it watches; T-03 binds a paren-free local instead — `plan.yaml` T-04 step 1 — verified-at 3faada88
- Do not treat T-01's red `verify:` as a defect; it is the designed red-state discriminator — `notes/ship-review-2026-09-06-07-ship.md` — verified-at 3faada88
- Do not collapse the two files' duplicate expression of the property; the duplication is the operator's directive and simplify declined it on that ground — `notes/handoff-ship.md` Dead ends — verified-at 3faada88
- Do not re-run the eng segment to recover the lost lead digest; the five member receipts are the surviving primary evidence — `notes/build-digest-reconstructed-2026-09-05-07-eng.md` — verified-at 3faada88

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/build-digest-reconstructed-2026-09-05-07-eng.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/qa-2026-09-06-15-validator.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json`
- `tests/unit/test-factory-claim-mutation.py`

## Done when

Scope: the validation panel has graded the pinned tree over the B-27 fix
Authority: brief-sc:SC-08
Authority: brief-sc:SC-02
