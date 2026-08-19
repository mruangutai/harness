# Distillation — harness-code-reviewer — FEAT-25

Inputs: my own review artifact `review-harness-code-reviewer-c1.md` (FEAT-25-claim-feature-root) and
the three relayed observations in the dispatch. No observations log exists for this feature (globbed,
zero hits, confirmed by the dispatcher). No Patterns displacement made — room existed elsewhere.

## Section counts (measured, before any op applied in this run)

Patterns 15/15 (FULL, untouched) · Gotchas 14/15 (room for exactly 1) · Outcomes 4/10 (room) ·
Open 0/5.

## check-expertise.sh output (before any op — nothing applied this run)

```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```
Exit code: 0.

## Ruling on the three relayed observations

### 1 — "mutation proofs assert both halves" — ACCEPT, reshaped, into Outcomes (room, no displacement)

Checked against O-01 first, per the relay's own honest pre-judgement. O-01 is scoped to *coverage
gaps*: "add one non-shipped probe case that fails on it" to prove an untested branch is really
untested. F-2 (surviving mutant, weak assertion) fits that shape cleanly and I judge it already
covered — no new entry needed for F-2 alone.

F-1 does not fit O-01's shape and is where the real gap is. F-1 is not a coverage gap — case 18's
assertion already exists and correctly reddens on the mutation (`FAIL - case 18: clean -> exit_code
0` printed). The defect is that the harness's own reporting/exit-code chain swallows that correct
detection (`EXIT CODE: 0` regardless). O-01's "add a probe that fails" framing has no room for
*validating an already-firing assertion whose failure doesn't propagate* — a different mechanism
(broken accumulation/exit-status, not missing coverage). I rate this non-redundant and worth its own
entry, at Outcomes because it is a verification-of-evidence discipline like O-01/O-03, not a
code-analysis heuristic like the Patterns section.

```yaml
op: add
section: Outcomes
target: (new)
entry: "WHEN publishing a mutation-test proof — mutant caught or mutant surviving — DO show both
  that the mutation landed in the exact executed bytes and that the run reached completion — either
  alone can't distinguish a real result from an unapplied mutation or a broken harness."
why: "FEAT-25 review F-1 (mutant killed the assertion but exit code stayed 0 — a reporting fail-open,
  not a coverage gap) and F-2 (mutant survived, proving a weak assertion). F-2 alone already fits
  O-01; F-1 needed its own entry because O-01's 'add a probe that fails' shape doesn't cover
  validating an assertion that already fires but whose failure the harness swallows."
file: .harness/expertise/harness-code-reviewer.md
```

### 2 & 3 — both FALSE claims in my own review, same root cause — ACCEPT, merged into ONE Gotchas
entry (uses the last available slot; Gotchas would overflow the cap of 15 if added separately)

**Item 2** (F-3's "zero test coverage" addendum): confirmed false at source. Re-read
`test-factory-claim.py:964,975-977,372,858-863,988,995-996` myself — `sc13b_fixture` gives issue 908
the label `feature:FEAT-99-missing`, explicitly commented `# blocker gate: no_plan, feature dir does
not exist`, and it runs with the real (restored) `FEATURES_ROOT`, landing on the second `no_plan`
branch (`root_exists() == True`, confirmed at `factory_claim.py:122-124`: `root_exists` tests the
shared root via `os.path.isdir`, not the per-feature dir). My grep swept for
`unparseable|root_exists|YamlParseError|corrupt|malformed` — none of which the fixture uses; it
spells the condition as a synthetic feature name. The branch IS exercised; what's actually missing is
an assertion pinning *which* text is emitted (weaker than what I originally wrote, not absent).

**Item 3** (F-1's blast-radius claim of a "2-file, 4-site defect class"): confirmed false.
`grep -n "fails += 1" test-check-state.py` → zero matches (verified myself, matching the relay's
independent run). The three `test-check-state.py` sites I cited only wrap the *print*, not an
accumulator — `allok = allok and ok` sits outside the `if not ok and detail:` guard there. The
defect is a single site: `test-layout-migration.py:418` only.

Both are the same failure mode: a sweep/grep anchored on an adjacent, plausible-looking feature (a
conditional's syntax; a set of synonym vocabulary words) instead of the actual defect signature
(the accumulator's placement; the fixture's real spelling), generalizing a finding onto code that
doesn't have it. Per the entry-format rule ("citing more than one incident is a distillation smell:
keep the rule, drop the cases"), I merged these into one rule rather than filing two — which also
fits the one remaining Gotchas slot exactly (14 → 15, at cap after this op; no further room without
displacement).

```yaml
op: add
section: Gotchas
target: (new)
entry: "WHEN a sweep or grep supports an absence or blast-radius claim DO verify the search terms
  match the actual vocabulary/pattern at the cited sites before generalizing — an anchor on the
  wrong feature (syntax instead of the defect, a synonym instead of the fixture's spelling) reports
  false absence as verified."
why: "Two corrections to my own FEAT-25 review: a 'zero coverage' grep that missed the fixture's
  actual label (FEAT-99-missing, not any of my 5 search terms), and a '4-site defect class' claim
  keyed on the surrounding conditional rather than the accumulator that doesn't exist at the other
  3 sites. Merged per the no-instance-stacking rule; also the only way both fit — Gotchas had room
  for exactly 1 more (14/15), not 2."
file: .harness/expertise/harness-code-reviewer.md
```

## Ops derived independently of the relay

None. Re-reading my own review artifact end to end, everything else in it (the SC-04-scope
distinction, the "held dirt not read" note, the scratchpad-isolation technique for building mutation
proofs without touching repo files) either restates an existing entry (P-07, O-04) or isn't durable
enough to pass the six-spawns test on its own. No additional op filed.

## Patterns section

Untouched. No candidate this run displaced a Patterns entry — both accepted items had genuine room
elsewhere (Outcomes 4→5/10, Gotchas 14→15/15), so no displacement judgement was forced.
