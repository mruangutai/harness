# Answers — FEAT-1928 — run build-docs-product — 2026-09-29

Q1 (DEC-236 allocated; amend T-03?) → **Yes, amend T-03 to DEC-237, not DEC-549.**

Operator ruling. Facts checked by the main session across local and fetched refs:
- origin/main's highest decision is DEC-235.
- DEC-236 is taken by `feat/FEAT-1896-dashboard-from-prototype` (in flight).
- DEC-237 through DEC-548 are taken only by local branch `feat/FEAT-46-decision-standard`: last commit 2026-09-04, unmerged, no PR, on a divergent numbering scheme (396 entries up to 548). The operator does not treat that stale branch as an allocation; if it is revived it renumbers against main, as it would have to anyway.

So T-03's "next unallocated" check is satisfied by DEC-237 with this recorded exception for `feat/FEAT-46-decision-standard`. Replace DEC-236 with DEC-237 throughout T-03, preserve every other signed T-03 requirement, and add to T-03 that DEC-237 must record the 2026-09-29 build ruling (every live schema property required; `none`/`[]` sentinels; no null; conditional fields always present; closed minimal list entries) as superseding DEC-223's documented-optional tier.
