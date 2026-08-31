# SIMPLIFY — ALTITUDE angle — FEAT-38-decisions-current-knowledge

Diff `7ebfc9eb9c..8a7c75c4e5`, code surface only (`run-unit-tests.sh`, `gen-decisions-index.py`,
`harness.json`, `tests.yml`, `check-domain.sh`, `board_lifecycle.py`; `check-decision-anchors.py`
frozen and untouched). Read-only. **One finding rises above the leave bar; everything else checked
is clean or already has a named compensating mechanism.**

## Q1 — Residue of the deleted claims checker in any caller?

Checked `run-unit-tests.sh` (T-24, `INTEGRATION_SCRIPTS` array), `harness.json` (T-25,
`test_kinds.integration.detect`), `tests.yml`, `check-domain.sh`, `board_lifecycle.py` for any
surviving branch, special case, or literal referencing `check-decision-claims` /
`check_decision_claims`. **None found anywhere on the code surface** — both registration sites
were edited as single-line removals with nothing else touched, and the two commits (`8c879f5`,
`8a7c75c`) land in the order the runner's own KIND-DRIFT check forces. `check-domain.sh` and
`board_lifecycle.py`'s only edits in this diff are unrelated `DEC-186/DEC-192 → DEC-203` citation
sweeps (T-12/T-13), not claims residue. **`leave`** — clean removal, nothing to fold in or flag.

## Q2 — One authoritative statement of the registered-test-script list, or several that can drift?

Two, by design, with a named compensating control already in place: `run-unit-tests.sh:30-31`'s
`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` bash arrays, and `harness.json`'s `test_kinds.*.detect` globs.
`tests.yml` restates neither — it only calls `run-unit-tests.sh --kind {unit,integration}`, so it
is not a third site. The two arrays and `harness.json` are reconciled by a standing KIND-DRIFT
cross-check (`run-unit-tests.sh:76-140`, `FEAT-31 T-12`), which fails closed (exit 2) on any name
present on one side and absent from the other, runs on every invocation including `--check-kinds`,
and is itself exercised by `test-run-unit-tests-kinds.py`. This is exactly the "several statements
that can drift" pattern the angle asks about, but the compensating control is already built,
already named in the comment directly above it, and both registration commits in this diff
(T-24/T-25) cite it as the reason they had to land in a specific order. **`leave`** — not a new
duplication this feature introduced; the drift is already caught mechanically.

## Q3 — Is the accepted residual (semantic citation rot) right to accept, and is its compensating
control named where a reader will find it?

Contract 3 forecloses proposing a replacement; judging the naming is in scope. The gap is real and
recorded twice, but at two different altitudes:

- **`DEC-205`** (`DECISIONS.md:6255-6272`, the living, current-truth authority) states the one
  remaining mechanical check is anchor rot only, and explicitly records two rejected alternatives
  (a referenced-file watch, a periodic LLM audit) — but never states, in its own body, what
  currently substitutes for the rejected detector. A reader who opens DEC-205 six months from now
  to ask "what catches semantic drift today" is told what was rejected, not what compensates.
- **`BRIEF.md:130-138` and `:393-400`** (this feature's own planning artifact) states it plainly:
  "the detector for it is a human reading a diff," and names the compensating control precisely —
  SC-11 and SC-13, both human, neither a standing check, both scoped to this change only.

The complete answer lives in a feature-scoped planning document that is not where a future reader
of the permanent decision record looks. `DEC-205` is titled "this file states current truth" —
that is exactly the home this fact belongs in, one clause, stating what compensates today rather
than only what was declined. This is a naming/placement judgment, **not** a proposal to add
checkable-claim vocabulary to entries (Contract 4 untouched — no entry-authoring guidance is being
suggested, only a fact about present verification practice).

**Filed `briefing-row`, not `fold-in`:** the wording is the operator's to approve given how
recently and deliberately this exact area was fought over (three signatures on the brief, one
withdrawal); a dev-ops apply here risks re-opening settled text under time pressure with no second
reader.

## Priority

Only Q3 clears the bar. Recommend the lead carry it forward as a single backlog row: *"DEC-205
names what was rejected as a compensating control for lost semantic-citation checking but not what
currently substitutes for it (human review at SC-11/SC-13); consider one added clause naming that,
sourced from `BRIEF.md:130-138`."* Nothing else in this diff's code surface warrants a finding.
