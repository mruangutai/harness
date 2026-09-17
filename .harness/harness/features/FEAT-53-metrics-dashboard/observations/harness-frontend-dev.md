# Observations — harness-frontend-dev — FEAT-53

- 2026-09-16: A fixed configured scaleBand domain retained a zero-count grade as a rendered bar, while scaleUtc measured irregular-date gaps at the actual 1:60 ratio.
- 2026-09-16: Installing the DESIGN-pinned Neutral theme alongside the existing Astryx core pin requires npm peer resolution to retain test and StyleX peer packages; `--legacy-peer-deps` leaves the client unable to run its scoped verify.
- 2026-09-16: T-14 exact forbidden-path scan includes T-13 routes.test.tsx retired-route assertions, so it fails independently of T-14 source.
- 2026-09-16: Runtime-literal scans over TSX must exclude test modules when those tests intentionally preserve retired literals as negative-route assertions.
