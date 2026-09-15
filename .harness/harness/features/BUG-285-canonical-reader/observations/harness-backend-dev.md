# Observations — harness-backend-dev — BUG-285-canonical-reader

- 2026-09-14: T-09 removes the obsolete shell differential script before the canonical-reader inventory, so its internal json.load is not a live parse surface.
- 2026-09-14: Present malformed issue receipt fields must be refused before create paths; null remains legitimate unrecorded state.
- 2026-09-14: Shared feature.json validation must preserve absent github/factory blocks while rejecting present recorded parent or issues corruption before either consumer can create issues.
- 2026-09-14: A T-03 row can be marked migrate/team while its remedy is only `documented source route`; this cannot satisfy a public-accessor seam cutover without an amendment naming an accessor.
- 2026-09-14: A path-or-text accessor can retain one strict parser by letting the byte reader perform only I/O and decode, then routing both it and the text source to the same parsing helper.
