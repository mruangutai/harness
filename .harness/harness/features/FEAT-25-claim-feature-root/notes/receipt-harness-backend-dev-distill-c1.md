# Distillation receipt — harness-backend-dev

## Section counts

- Patterns: 15 before, 15 after (P-15 content replaced, count unchanged)
- Gotchas: 15 before, 15 after (G-01 content replaced, count unchanged)
- Outcomes: 0 before, 0 after
- Open: 0 before, 0 after

No observations log existed for this feature (`observations/harness-backend-dev.md` absent), so
all candidates judged here came from the lead's relay plus my own T-01/T-02/T-03/REUSE/SIMPLIFICATION
receipts under this feature.

## Candidate 1 — build test oracle from the resolver, not a re-spelled literal

**Rejected.** The underlying insight (T-01's module-scope cases call
`factory_config.harness_root()` to build the expected `FEATURES_ROOT` value rather than hardcoding
a fully independent literal path) is real but does not clear the bar to displace a capped entry.
It overlaps existing P-05 ("compare against an independent, distinctively-valued oracle instead of
self-comparison") closely enough that a new entry would mostly restate it with a narrower example.
Not distinct enough to earn a slot over what it would have to displace.

## Candidate 2 — module-scope, unpatched-default test cases catch a stale import-time constant

**Accepted.** Replaced P-15 (bracket a live call's cost measurement with a null-control read),
judged weaker: narrowly scoped to live-cost measurement, a rare backend-dev scenario, versus this
candidate's direct hit on the actual defect this whole feature existed to fix — a 114/114 green
suite over a stale module constant because every case monkeypatched it first, until two unpatched
cases were added. Source: **lead-relayed** (digest skim), corroborated by my own T-01 receipt
(`test-factory-claim.py` RED-first evidence section, the two new "unpatched FEATURES_ROOT default"
cases).

New P-15: "WHEN a module-scope constant is computed once at import time DO add at least one
unpatched-default test case that exercises it without monkeypatching first — if every other case
patches the constant before use, a suite can stay fully green forever over a stale default nothing
exercises."

## Candidate 3 — anchored grep sweep reporting "zero coverage" is not proof of absence

**Accepted.** Replaced G-01 ("The harness repo has no application source; src/** is empty here."),
judged weakest of all 30 entries: it is a bare repo-specific fact, not even WHEN/DO-shaped, and
fails the craft test outright (not true or useful in a repo never seen). Source: **lead-relayed**
(digest skim, review-panel R-4) — I hold no first-party artifact touching this incident; my own
REUSE-angle work this feature (six cleared candidates, receipt
`receipt-harness-backend-dev-2026-08-18-01-eng-reuse.md`) is the same anchored-search shape but a
different instance, so I treat the relay as sourcing this entry, not my own artifact.

New G-01: "WHEN a coverage sweep reports zero hits for a fixed list of anchor terms DO treat that
as inconclusive, not proof of absence — the real branch may be exercised by a fixture spelling the
condition in different words the sweep's terms never match, so read the fixture directly."

## expertise_update ops (verbatim, as reported in DIGEST)

```yaml
expertise_update:
  - op: replace
    target: P-15
    section: Patterns
    entry: "WHEN a module-scope constant is computed once at import time DO add at least one unpatched-default test case that exercises it without monkeypatching first — if every other case patches the constant before use, a suite can stay fully green forever over a stale default nothing exercises."
    why: "the defect this feature existed to fix; displaces a narrower, rarely-hit live-cost-measurement pattern"
  - op: replace
    target: G-01
    section: Gotchas
    entry: "WHEN a coverage sweep reports zero hits for a fixed list of anchor terms DO treat that as inconclusive, not proof of absence — the real branch may be exercised by a fixture spelling the condition in different words the sweep's terms never match, so read the fixture directly."
    why: "displaces a bare repo-specific fact that was never craft to begin with; new entry is a generalizable reviewing gotcha corroborated by my own REUSE-angle work's shape"
```

## Checker

`.claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-backend-dev.md` → `OK`.
