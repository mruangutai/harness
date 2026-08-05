# Observations — harness-product-lead — FEAT-09-plan-time-route-check

- 2026-08-05: The dispatch handed me a 12-path FEAT-08 exclusion list and said the intersection with
  #20 was "empty" — chosen for this slot on that basis. It was empty against the LIST but not against
  FEAT-08 as actually planned: `run-unit-tests.sh` was absent from the list, yet
  `FEAT-08/PLAN.md:243,250-252` edits the `SCRIPTS` array at `:6`, the same line FEAT-09 T-02 appends
  to. pm honoured the list correctly and still missed it. Found it by noticing `run-unit-tests.sh:6`
  lists `test-cost-report.py` and that FEAT-08 is a cost-REMOVAL feature — i.e. by reasoning about
  what the other feature must do, then opening its PLAN to confirm. Generalises P-01: a handed-down
  exclusion list is a claim about another artifact, so verify it against that artifact, not against
  itself. Cross-feature collision is the one class of finding a member structurally cannot see.

- 2026-08-05: pm's first return declared SC-08 "2 clauses / 2 fixtures" and the fixture map agreed —
  but T-02's `intent:` forbade THREE matcher shapes (`fnmatch`, glob-to-regex, `startswith` prefix).
  The count was internally consistent and still wrong, because the clause count was taken from the SC
  wording rather than from the intent the SC is supposed to cover. Comparing SC text against task
  intent text (not against the fixture count) is what surfaced it. Post-fix: 4/4, and the added
  fixture is behavioural — a mid-pattern wildcard grant (`team-config.yaml:278`) where the real
  matcher and a prefix comparison give different answers — because a source grep for `startswith` is
  defeated by any equivalent idiom.

- 2026-08-05: My own run `state.yaml` was BLOCKED by `check-domain.sh` for DEC-154 — I had added
  top-level `lead_checks:` and `send_backs:` keys holding assessment verdicts. The enforcement layer
  this very feature extends caught the lead extending it. Prose ceiling really is one `note:` per
  step entry; per-check verdicts go in `digest.md`.
