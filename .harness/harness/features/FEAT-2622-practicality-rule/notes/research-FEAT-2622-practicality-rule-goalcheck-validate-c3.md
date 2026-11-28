# Goal-check: FEAT-2622-practicality-rule, validate run 2026-11-28-04, cycle 3

**BLUF: PASS.** All three perspectives pass. Both decision dispositions are met (DEC-206 amend,
DEC-123 amend). DEC-123's rewritten clause, DEC-260's D-06 bullet and `validate-digest.py`
state the same relief rule: every attributed row is resolved, or open with the row and the
current finding both discounted at a non-gating severity, and the team `must_fix` is empty. The
plan-side triage reason names the reader's original severity (D-03). The c2 must-fix premises
MF-1 and MF-2 are red at `edcda5be` and green at the pin. I measured both by EXECUTED probe.
Two advisories are low/form and non-gating.

Pin `0ce1c841`, base `3e979ae3`. Content reads use `git show 0ce1c841:<path>`. Executions ran on
a `git archive` of the pin at `/tmp/gc2622c3/pin`, with `HARNESS_PROJECT_DIR` set to the archive
and `HARNESS_AGENT_TYPE` unset. The commits after the pin (`git diff --name-status 0ce1c841
bd5f550c`) touch only this feature's `feature.json` and `plan.yaml` (status `building` →
`review`).

## Perspectives

- **operator — pass.** Carried by SC-02, SC-03, SC-05, SC-07, SC-09 and SC-15.
  - **SC-15 relief and denial.** `tests/unit/test-practicality-rule.py` ran 36/36 at the pin,
    rc 0. It has 8 carve-out cases, one per relief leg, plus `discounted-open-relieved`.
  - **Gate relaxation (full weight).** The fix round removes `_row_relieves` and
    `_matched_row_reason`. In their place, one rule in `_open_row_reason` requires a current
    finding (`current and all(map(_discounted_non_gating, current))`), and `_carveout_inputs`
    denies relief when `seen.get("must_fix")` is non-empty. This only narrows relief and grants
    none. See the probe table below.
  - **SC-07.** `git diff --name-status 3e979ae3 0ce1c841` shows no other feature path and no
    `runs/` path outside this feature (grep rc 1). `run_state.py` is unchanged
    (`git diff --quiet`, rc 0).
  - **SC-09.** Product-lead body L444–452 and the `teams/plan.yaml` comment L227–233 carry
    "naming the reader's original severity and exposure", "Never raise a severity" and the
    survives-triage routing. Validator-lead L483–485 and `teams/validate.yaml` L158–159 are
    unchanged since c2. The phrase `never revise a reader's severity` occurs 0 times in either
    agent body.
  - **SC-02, SC-03 and SC-05.** Their surfaces did not change in the fix round
    (`git diff --stat edcda5be 0ce1c841`), so they carry from c2.
- **reader — pass.** Carried by SC-01, SC-04, SC-08, SC-10 and SC-11. None of their surfaces
  changed between `edcda5be` and `0ce1c841`, so the c2 evidence stands. Re-executed at the pin:
  - `test-practicality-rule.py` 36/36, which includes the `unrated` refusal and acceptance cases
    for SC-04;
  - `test-digest-dev-skill.py` 12/12, rc 0.
- **code maintainer — pass.** Carried by SC-06, SC-12, SC-13 and SC-14.
  - **SC-06.** The new `_open_row_reason` calls `_discounted_non_gating`, which wraps
    `panel_findings.is_discounted` and `is_non_gating`. No new restatement of either.
  - **SC-12.** `gen-decisions-index.py --stdout | cmp - DECISIONS-INDEX.md` printed
    INDEX-EQUAL.
  - **SC-13.** `gen-agent-output.py --check` printed `agent output: ok`.
  - **SC-14.** Every result has 0 `FAIL` or `not ok` lines:

    | Test | Result |
    |---|---|
    | `test-validate-digest` | ALL PASSED, rc 0 |
    | `test-validate-digest-shadows` | 46/46 |
    | `test-plan-team` | 184/184 |
    | `test-validate-digest-plan-rollup` | rc 0 |

  - **Not re-run this cycle.** `test-panel-findings`, `test-plan-merge`,
    `test-check-state-records` and `test-check-omp-port`. Their files and code are unchanged
    since c2, where they passed. I rely on qa's c3 digest for the current run.

## Prior must-fix premises, re-measured (EXECUTED; P-06)

`/tmp/gc2622c3/probe.py` reuses the shipped `run_carveout` from `test-practicality-rule.py` (no
repo write). I ran it once at the pin, and once with only `validate-digest.py` swapped to its
`edcda5be` copy (O-07).

| Probe | Pin `0ce1c841` | `edcda5be` |
|---|---|---|
| resolved rows only, no team must_fix → relieved | PASS | PASS |
| resolved rows only, team must_fix non-empty → denied (MF-2) | PASS | FAIL, no errors |
| must_fix `[" "]` → denied | PASS | FAIL |
| open discounted row, current finding omitted → denied (MF-1) | PASS | FAIL |
| two open discounted rows, one current finding omitted → denied | PASS | FAIL |
| current finding re-rated discounted `low` → relieved | PASS | PASS |
| current finding adversary-controlled `med` → denied | PASS | PASS |
| current finding `unrated` → denied | PASS | PASS |

The verdicts are not uniform, and the relieve/deny pairs differ only in the discriminating input
(O-06). MF-1 and MF-2 are **fixed** under the same contract; their scenarios no longer occur.

## Decision dispositions (pinned `git show 0ce1c841:.harness/harness/docs/DECISIONS.md`)

- **DEC-206 amend (successor D-03): met.**
  - The plan row's clause "whether a defect exists at all, and how severe the reader judged it"
    has 0 hits at the pin.
  - Pinned L6804–6807 read: "never owns CONTENT — whether a defect exists at all — and never
    raises the severity the reader judged; it may lower a finding to at most `med`, or drop it,
    only when the practicality rule (DEC-260) discounts it, with a one-line reason beside the
    finding."
- **DEC-123 amend (successor D-06): met.** At the pin, the plan row's clause "carrying the same
  reader string and `disposition: resolved`, and every other on-disk row attributed to it is
  `resolved`." is gone. The rewrite is in place, per DEC-205. Pinned L2497–2506 read: "every
  finding the team digest attributes to it matches exactly one row … carrying the same reader
  string; every on-disk row attributed to it is `disposition: resolved` or, under the
  practicality rule (DEC-260), open with both the row and the team digest's current finding with
  its id discounted at a non-gating severity; and the team's `must_fix` is empty". The denial
  list adds "a discounted row whose current finding is omitted or not discounted, a non-empty
  team `must_fix`". Each clause maps to code at the pin:
  - identity → `_digest_finding_reason`;
  - every attributed row → `_open_row_reason` over all `rows`, filtered to `[index]`;
  - both discounted, current required → `_discounted_non_gating(row) and current and all(...)`;
  - must_fix empty → `_carveout_inputs`.
- **DEC-260 D-06 bullet (L8877–8884): agrees.** "an open row discounted at a non-gating severity
  does not deny relief, provided the team digest carries a current finding with that id,
  discounted at a non-gating severity too, and the team's `must_fix` is empty; a stale
  discounted row never stands in for a re-rated or omitted finding." Its D-03 bullet says "a
  one-line reason naming the reader's severity", which matches the plan-side text.
- DEC-31, DEC-228, DEC-230, DEC-237, DEC-174 and DEC-229 are `keep` rows and are not graded.

## Advisories (non-gating)

- **A-1 (low, form, T-05; carried from c2).** DEC-206 L6807–6808 still follows the lowering
  permission with an unqualified "A lead that supplies a severity the reader did not emit has
  manufactured evidence". Exposure `{trigger: plausible, vs_today: no_worse, control: harness}`.
  Static reading.
- **A-2 (low, form, T-05).** The DEC-123 row in DECISIONS-INDEX (its hand-written ` :: ` summary, L128)
  says "whose rows are resolved or discounted". It omits the current-finding and empty-must_fix
  conditions. The index is a pointer and the entry governs. Exposure `{trigger: contrived,
  vs_today: no_worse, control: harness}`, so it is discounted and at most med. Static reading.

## Principles applied

- harness-pm Expertise P-06 and O-07: I re-measured MF-1 and MF-2 against the `edcda5be`
  validator as a free mutant, not from the receipt's mutant table.
- harness-pm Expertise P-19: probes one boundary beyond the stated legs (a whitespace must_fix
  entry, a second omitted row, and a re-rated current finding at `low`, `adversary` or
  `unrated`).
- harness-pm Expertise P-16: I graded the affirmative D-06 and D-03 prose in DEC-260 and
  DEC-123 against the measured code.
