# Expertise — harness-ai-dev

## Patterns (max 15)
- P-01: WHEN a procedure step tells its reader to load a specific file at point-of-use DO verify
  the governing constraints actually live there, not only in a separate authoring source — a rule
  stated only elsewhere is invisible to a reader who never opens that other file.
- P-02: WHEN a decision creates a second call site into a shared "who does X" inventory DO add a
  row for it in the same pass — an inventory that is accurate only until the second caller arrives
  stays wrong indefinitely, because nothing forces the addition afterward.

## Gotchas (max 15)
- G-01: WHEN proposing to de-duplicate code that a drift detector watches DO check what text or
  string the detector actually scans for first — a probe moved behind a function call can emit no
  signal at all, silently disabling the detector that made living with the duplication safe.

## Outcomes (max 10)

## Open (max 5)
