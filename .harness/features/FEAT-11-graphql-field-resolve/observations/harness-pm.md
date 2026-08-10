# Observations — harness-pm — FEAT-11-graphql-field-resolve

- 2026-08-10 (goal-check): a criterion enumerating N distinctions needs N-1 pairwise inequality
  assertions, and inequality is NOT transitive. SC-11 named two distinctions; the suite asserted
  org != unknown and board != org, and the record (`notes/qa-c0.md:71`) read that as covering
  "distinct from org and board-absent". A collapse of unknown-owner into the board-not-found message
  passes every check in the file. Counting comparisons against the criterion's own enumeration is
  what found it; reading the labels did not.
- 2026-08-10: writing a UAT script for a CLI tool, the target of the write came from a config file
  (`.harness/factory/fleet.yaml`, board 3) and NOT from the `--repo`/`--board` flags I was reading.
  My first draft would have sent the operator's one live measurement at the wrong board while
  carefully snapshotting the right one. Trace the tool's own resolution of its target from `_main`
  before writing any step that mutates something.
- 2026-08-10: a restore-verification step that compares `item.get(<field key>)` before/after reports
  "clean" for every item when the key is wrong — `None != None` is False. Any check keyed on a name
  discovered at runtime needs an explicit "key absent -> CANNOT VERIFY" branch, or it is the same
  vacuous-assertion class the feature had already been bitten by once (MF-1).
