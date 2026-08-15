# QA confirm-rerank — FEAT-14 — Q1 reclassified MED/advisory

## Verdict on the rerank: AGREE. Q1 is advisory, not blocking.

Predecessor's measurement stands unchanged (`qa-confirm-falsifiability.md`): reverting
`load_recorded`'s reader from `json.loads` to `yaml.safe_load` leaves `test-gh-sync.py` 74/74 green
— B-5's reader-contract (JSON-only) is unbound by any assertion that can fail on it. Not disputed,
not re-measured here.

## The two points hold up

1. **Re-filing hazard stays closed under the mutant.** `yaml.safe_load("")` → `None` → fails
   `isinstance(doc, dict)` at `gh-sync.py:295` → `SystemExit`. Confirmed by predecessor's own
   corroboration step: pre-fix `gh-sync.py` + HEAD's `test-gh-sync.py` produces exactly 6 failures,
   all `fix1 *` rows — the property "refusal happens at all" does discriminate. What's unpinned is
   which branch/reader, not whether HIGH-2's hazard reopens. Correct.

2. **B-5 is a non-blocking backlog companion, not an SC.** Confirmed independently: grep of
   `plan.yaml` for `B-5` finds no task entry, and no `verify: automated` claim is attached to it.
   `STATE.md:37/86` framing (fix-cycle companion, non-blocking) is consistent with that absence.
   Structurally unlike HIGH-3, where the gap falsifies a plan-declared verification method.

## The two things Mike asked me to check for

**(a) Some other changed unit in `1c5fd67` left unbound by the same gap** — checked
`git diff 1c5fd67..12e3fa2 --stat` per predecessor's Step 0: pin-only, only `feature.json` changed
since. The changed units in the reviewed diff are `gh-sync.py`/`test-gh-sync.py` and
`check-domain.sh`/`test-check-domain.py`. The comment-tolerance/reader-contract gap is specific to
`load_recorded`'s JSON/YAML boundary — nothing else in the diff shares that specific reader
contract. HIGH-1's schema-crash fixture (predecessor Step 3) has its own separate, already-noted
adequacy gaps (route coverage, crash-vs-import attribution) — real, but distinct findings, not this
one recurring. No second instance found.

**(b) Does `test_matrix` independently require a discriminating test for every changed unit?**
Read `.harness/harness.json` directly (not re-run). The matrix operates at **kind-presence**
granularity, not per-assertion discriminating power: `bugfix.always: [unit]`, plus a
`__bug_class__`-conditioned kind. `test-gh-sync.py` is a `unit`-kind file
(`detect: .../test-gh-sync.py` is covered generally under the unit glob via
`.claude/skills/harness/bin/test-*.py`) and it ran green under `run-unit-tests.sh --kind unit`.
The matrix asks "does a unit test exist and pass for this change type" — it is satisfied by
presence, and says nothing about whether any specific assertion inside that file discriminates a
specific reader mutation. So no, the matrix does not independently escalate this: `matrix_ok: true`
for kind-presence is a true statement even with the inverse-fixture gap live. This does not change
the answer.

## Reclassification

- `VERDICT: PASS` (carrying this as advisory).
- Finding kept verbatim in `coverage_gaps`: B-5's reader contract (JSON-only vs YAML-tolerant) has
  no fixture that feeds `load_recorded` a comment-bearing document and asserts rejection —
  `test-gh-sync.py:720-722` is a comment, not an assertion.
- Re-filed as **non-blocking** open_question, ranked top of the advisory list — cheap to close in a
  follow-up: one fixture, one assertion, in the existing `fix1` block.
