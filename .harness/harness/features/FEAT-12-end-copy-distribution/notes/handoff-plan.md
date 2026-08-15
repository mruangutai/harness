# Handoff — FEAT-12, plan → build — written at ff75afb, seq-1

<!-- RECONSTRUCTED, not inherited. The plan-phase orchestrator returned without writing
     this note, so the build phase started on the disk-only path (DEC-159). Written by
     the build-phase orchestrator from BRIEF.md, plan.yaml, STATE.md and the three
     product run digests. Anything I did not verify myself says UNVERIFIED. -->

## Next

Segment B of `notes/segments-layer0-2026-08-10.md` — T-06, T-08, T-09, T-11, main-session-direct.
T-08 and T-11 are what T-14 waits on, so they unblock the rest of the build. Then T-14 (product) and
T-13 (eng), then the qa gate.

## Trust

- BRIEF and plan are both `approved` / `operator` / `2026-08-10` — `BRIEF.md ## Approval`,
  `plan.yaml approval.status` — verified-at ff75afb
- D-06 is REVERSED, folding into T-03 and T-05, no new task — `plan.yaml approval.rulings`,
  `notes/answers-2026-08-10-03-product.md` — verified-at ff75afb
- 9 of 14 tasks are `execution_mode: main-session-direct` — `plan.yaml tasks[].execution_mode` —
  verified-at ff75afb, and I re-probed the domain hook on T-06/T-08/T-11's paths (exit 2)
- No task in this feature reaches a DEC-174 carve-out file; DEC-12 has exactly 3 inbound references
  and all 3 are under `docs/` — `git grep -nE 'DEC-12([^0-9]|$)'` — verified-at ff75afb
- kaya's `settings.json` wires EIGHT harness registrations across four hook events, not three —
  `notes/measurements-2026-08-10-orchestrator.md` M-1..M-6 — UNVERIFIED by me, taken by the
  plan-phase orchestrator in kaya on 2026-08-10
- 34 tracked kaya files lose local modifications in T-05's commit, all reproducible from this repo —
  `BRIEF.md ## Settled rulings` — UNVERIFIED by me
- SC-06 is a blocking UAT the operator runs himself against a factory checkout of kaya; no runner in
  this repository can observe another repository — `feature.yaml counts_note` — verified-at ff75afb

## Dead ends

- Do not re-run `gh-sync.py open` — it ran this phase and recorded milestone 6, parent 223 and 14
  sub-issues — `feature.yaml github:` — verified-at ff75afb
- Do not touch issue #206 — it is open and conflicts, and #203 lands first — operator's ruling in
  the ship dispatch
- Do not push anything in this repository and do not open a PR here — `BRIEF.md ## Settled rulings`
  Q1, which authorized a push to kaya and nothing else — verified-at ff75afb
- Do not edit `.harness/team-config.yaml` to grant `harness-documentor` a receipt path — the grant
  rides on open PR #222; route around it — operator's ruling in the ship dispatch
- Do not sweep `.harness/logs/**`, `.harness/notes/**` or `.harness/features/**` — records that were
  true when written — `plan.yaml` T-12 and T-14 intents — verified-at ff75afb

## Working set

- `.harness/features/FEAT-12-end-copy-distribution/notes/segments-layer0-2026-08-10.md`
- `.harness/features/FEAT-12-end-copy-distribution/plan.yaml`
- `.harness/features/FEAT-12-end-copy-distribution/feature.yaml`
- `.harness/features/FEAT-12-end-copy-distribution/runs/t12-product/digest.md`
- `.harness/features/FEAT-12-end-copy-distribution/BRIEF.md`
