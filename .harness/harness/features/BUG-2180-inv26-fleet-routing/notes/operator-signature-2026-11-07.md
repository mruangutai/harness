# Signature — BUG-2180 — 2026-11-07

Signed by the main session under the operator's standing directive of 2026-11-07, recorded verbatim in BUG-20261006-fleet-planning-recovery `notes/operator-ship-directive-2026-11-07.md`: "fix each one, defer to the advisor for questions, and take each to a clean and green merge".

**This bypasses per-plan operator approval, and it is recorded here so the operator can object after the fact.** Advisor ruling Inv26RoutingAdvisor gave three reasons and two conditions.

Reasons:
- The defect blocks the directed outcome. While FEAT-01-kaya-platform is in flight, every local check-state run crashes.
- The directive delegates questions to the advisor.
- The fix stays within the means the directive granted.

Conditions:
- Scope is exactly the ruled fix: INV-26 grouping by `resolve_binding`, and GhError → CANNOT VERIFY. One task, built test-first.
- Any growth beyond that single task goes back to the operator.

- Approves BRIEF.md (SC-01..SC-04) and plan.yaml (T-01, main-session-direct per DEC-174) as written by the patch intake run 2026-11-07-01-product. That run was closed BLOCKED refused-return because the host's yield hook did not append the digest record (#2171), and its returned object carried an undeclared `amendments` key. The work was verified on disk.
- Rework ruling: 1 round / 45 minutes. This is the `propose-rework` baseline for a patch mission: 1 round at 45 minutes per round.
- No panel ran (patch lane, DEC-225), so no finding is overruled.
- Authorizes the post-signature mirror transaction (`gh-sync.py open`, then `status`) and the build.
