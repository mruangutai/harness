# Handoff — FEAT-38-decisions-current-knowledge, validate → ship — RECONSTRUCTED 2026-08-31

**READ THIS FIRST.** This is not the handoff INV-17 expects at the seam. It was reconstructed after
FEAT-38 shipped because no `handoff-validate.md` was written when validation ended. Every claim below
points to a record that already existed; it neither backdates an author nor claims a successor received
this note. Treat it as a repair of the disk record, not evidence that the original relay occurred.

## Next

At the validate → ship seam, the only remaining action was the operator's UAT for SC-13, then ship on a
pass; a failure routed to `harness-product-lead` for a fix cycle — `notes/handoff-build.md` —
verified-at b460650. Ship later completed: PR #996 merged and `gh-sync.py ship` ran —
`notes/handoff-ship.md` — verified-at eb7e751.

## Trust

- At validate close, all 28 tasks were done, the blocking QA gate passed, and 15 of 16 live criteria were
  met; SC-13 alone was unrun UAT — `notes/handoff-build.md` — verified-at b460650
- The UAT was repointed at `635cd3ba` and made operator-ready before ship — `notes/handoff-build.md` —
  verified-at 635cd3ba
- At the shipping pin, the full suite exited 0, the QA gate passed, the delta panel passed, and 17 of 17
  live criteria were met — `notes/handoff-ship.md` — verified-at eb7e751

## Dead ends

- Do not represent this reconstruction as a timely handoff or as proof that validation and ship were
  relayed correctly; the missing original is the defect this file records — `STATE.md` — verified-at
  eb7e751
- Do not change FEAT-38's `Done` status or add an exemption to silence INV-17; the feature shipped and
  the invariant correctly requires the missing record — `feature.json`, `check-state.sh` — UNVERIFIED

## Working set

- `STATE.md`
- `feature.json`
- `notes/handoff-build.md`
- `notes/handoff-ship.md`
- `notes/uat-FEAT-38.md`
