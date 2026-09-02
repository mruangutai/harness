# Answers — FEAT-53 plan-signature briefing — 2026-09-01

## DEC-1 — backend framework
**Ruling: HOLD the settled web-framework decision.** Reject D-03's stdlib `ThreadingHTTPServer`
reversal. pm must return to the originally settled "a real web framework (backend + a JS charting
lib) is justified" and pick one (FastAPI, Flask, or a Node server), recording it as a D-NN with a
DEC-190-style justification (named alternatives rejected, why this one). The operator's stated
reason: a reversal recorded only inside a decision's `because:` clause, never surfaced, is not an
acceptable way to change a settled call — resurface it as its own visible decision if engineering
still believes it's right, but do not silently keep the stdlib server without that visibility.

## DEC-2 — client build
**Ruling: KEEP the client build.** No change — D-20 (React + TanStack on Astryx, npm package under
`bin/dashboard/client/`, committed `dist/`) stands as drafted.

## DEC-3 — charting fallback
**Ruling: ACCEPT the TanStack Charts alpha with the documented rollback.** No change — D-08 stands
as drafted (dead `react-charts` reference struck, `T-18` probing all 13 capabilities before client
UI is built).

## DEC-4 — two HIGH panel findings
**Ruling: FIX BOTH before re-submitting for signature.**
- `PF-328f8f3c`: scope KPI 4's absent-touchpoint-file-is-zero rule to POST-instrumentation features
  only. Pre-instrumentation features (the ~50 that predate this feature shipping) must report
  "unavailable — not tracked", never a zero. A zero must only ever mean "tracked and genuinely zero."
- `PF-7408d83a`: add a task that actually wires `T-15`'s chart into `T-14`'s panel, and change the
  verify assertion to check the chart is actually rendered (not that the file matches design
  tokens/instruction text).
- Order: DEC-3 is already settled (alpha accepted, T-18 stands), so both fixes may proceed together
  without waiting further.
Plan returns to the operator for signature only after both are fixed — do not ship either as a known
issue.

## DEC-5 — prototype
**Ruling: REQUIRE it opened and reviewed before signing.** The operator (main session, on the
user's behalf) will open and review the rendered prototype directly. This does not block pm's DEC-1/
DEC-4 fix cycle — proceed with those in parallel. Do not treat this as waived.

## Backlog (B-1..B-10)
**Ruling: ACCEPT ALL TEN as backlog issues, each labeled "Dashboard"** when filed via
`gh-sync.py backlog`. None struck.

## Harness defects (Q7-Q11, non-blocking)
Noted, not actioned in this feature. Filed for a separate BUG alongside the bash-write-guard
heredoc-classification defect and the plan-approval-stub gap the main session already found and
fixed directly in this run. No action needed from pm.
