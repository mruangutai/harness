# Expertise — harness-ai-dev
## Patterns (max 15)
- P-01: WHEN a procedure step tells its reader to load a specific file at point-of-use DO verify the governing constraints actually live there, not only in a separate authoring source — a rule stated only elsewhere is invisible to a reader who never opens that other file.
- P-02: WHEN a decision creates a second call site into a shared "who does X" inventory DO add a row for it in the same pass — an inventory that is accurate only until the second caller arrives stays wrong indefinitely, because nothing forces the addition afterward.
- P-03: WHEN dispatched to audit a diff or artifact for issues DO grep the plan's own signed decisions log for the same concern first — a pass that only rediscovers an already-recorded, already-owned decision costs a full dispatch to relearn what one grep would have shown.
- P-04: WHEN flagging duplicated code for a fold-in DO check whether the copies already diverge in observable behaviour — if they do, file it as a behaviour question naming which copy is intended, never as a refactor recommendation.
- P-05: WHEN sizing a finding for triage DO state its blast radius and timing — lines rewritten, whose code path, how late in the pipeline — that sizing is part of the finding, not only the reviewer's call afterward.
## Gotchas (max 15)
- G-01: WHEN proposing to de-duplicate code that a drift detector watches DO check what text or string the detector actually scans for first — a probe moved behind a function call can emit no signal at all, silently disabling the detector that made living with the duplication safe.
- G-02: WHEN judging whether a regex or charset filter bounds a risk DO check separately whether it validates identity/format or cardinality/count — a filter validating every item's name can still leave the number of matching items completely unbounded.
- G-03: WHEN a change multiplies the count of self-writable files injected into every spawn DO treat their content as ungated by design — a structural validator checks schema, budget and naming, never meaning, so trust in what gets written still rests entirely on the author.
## Outcomes (max 10)
## Open (max 5)
