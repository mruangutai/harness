# Operator decision and signature — BUG-2190 — 2026-11-08

## Operator decision (verbatim)

> for CI, i don't think we need to test gh login or gh functionality in general. we're already running CI in gh so any test in gh is superseded in my opinion

The operator gave this decision after reviewing the DEC-221 conflict. The evidence was real CI on draft #2189, where the Repository-state gate failed with `INV-37 FEAT-01-kaya-platform: invalid authoritative repository binding: product config unreadable … gh api contents failed`. The operator chose Option A: amend DEC-221 so that INV-37 runs the remote binding verification only where `gh` is authenticated, and otherwise validates `factory.repo` locally (shape and `fleet.yaml` membership). gh-sync and mirror/merge/sweep preflight stay fail-closed.

## Signature

- Signed by the main session on this decision, under the standing 2026-11-07 directive (BUG-20261006 `notes/operator-ship-directive-2026-11-07.md`).
- Advisor ruling Inv26RoutingAdvisor routed the DEC-221 change to the operator. This note records the operator's answer.
- Rework ruling: 1 round / 45 minutes. This is the `propose-rework` patch baseline.
- No panel ran (patch lane), so no finding is overruled.
- This authorizes the DEC-221 amendment and the index regeneration as an eligible T-01 `files` amendment, plus the mirror transaction and the build.
