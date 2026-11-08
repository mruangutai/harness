# Operator signature — BUG-2181 — 2026-11-08

## Authority

The operator's directive, verbatim:

> start issue://2181. take it to green and clean merge. defer to advisor for questions.

Advisor ruling Inv26RoutingAdvisor (2026-11-08):
- (A) The guarded item-add lives in `gh_board.set_station`, so every caller inherits it. Adding the missing card is the reconciliation, and a GhError stays a BoardError.
- (B) `repo-board-provisioning.md` gets a doc note only, with no audit or registration finding.
- The same patch-lane conditions as BUG-2190 apply: the main session signs under the directive and builds directly (DEC-174), and harness-validator-lead validates.

## Signature

- The main session signs on the directive above. This bypasses a separate per-plan approval prompt, which the directive's "take it to green and clean merge" authorizes.
- Rework ruling: 1 round of 45 minutes, the `propose-rework` patch baseline.
- No panel ran (patch lane), so no finding is overruled.
- The intake return was closed BLOCKED as a refused return, because of the undeclared `amendments` key (#2171). The plan and BRIEF themselves were verified on disk: `notes/refused-return-authorization-2026-11-08-01-product.md`.
