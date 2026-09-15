# Observations — harness-backend-dev — BUG-285-canonical-reader

- 2026-09-14: T-09 removes the obsolete shell differential script before the canonical-reader inventory, so its internal json.load is not a live parse surface.
- 2026-09-14: Present malformed issue receipt fields must be refused before create paths; null remains legitimate unrecorded state.
- 2026-09-14: Shared feature.json validation must preserve absent github/factory blocks while rejecting present recorded parent or issues corruption before either consumer can create issues.
