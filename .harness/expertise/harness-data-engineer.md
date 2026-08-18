# Expertise — harness-data-engineer

## Patterns (max 15)
- P-01: WHEN judging whether a measured cost is negligible DO state it in the unit matching its
  frequency — per-call, per-session, or share of the surrounding budget — not a bare number. A
  reader cannot check "negligible" against a figure with no scale attached.

## Gotchas (max 15)
- G-01: WHEN timing-probing a CLI that shells out to an external service (e.g. `gh`) DO wire the
  fake-binary env vars first, or run from a directory outside any real target — probing from a
  real project root can reach production and issue live network calls.

## Outcomes (max 10)

## Open (max 5)
