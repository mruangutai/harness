# BUG-2582 · plan goal-check: graded against the grilling, by perspective

**Yes. The plan delivers what the operator said they wanted.** Each of the three declared perspectives
passes at plan time. Both grilling destinations are carried by tasks, and every Settled ruling is
reflected in a decision and an SC. All three Not-yet-specified items are resolved: D-02 covers
validate-digest attribution, SC-04 covers sign-approval and INV-32, and DEC-123 is amended rather
than given a new entry. T-04 and T-05 cross nothing on the grilling's Out-of-scope list. T-05 widens
the surface set the grilling's Mission named, but this is disclosed and the operator can strike it
at signature.

Intent source: `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-plan-phase-station-and-rollup-2026-11-27.md`.
Graded files: `plan.yaml` and `BRIEF.md` in this feature directory, both pending. Base sha: `e69608659e31`.
This grade is at plan time. Nothing is built yet, so "pass" means the plan carries the outcome. It
does not mean the outcome has been observed.

## Per perspective

- **operator** — **pass**. This is Destination 1: a feature that follows INV-34's remedy can still
  receive its real plan. It is carried by SC-01, SC-02, SC-03, SC-04, SC-10 and SC-09 (regression),
  through T-01 (`union.py` `_convert_station_only` and the INV-34 remedy sentence) and T-04 (the
  start→convert witness through the real dispatch guard). The plan matches each Settled bullet for
  Defect 1:
  - `apply` drops the marker in the writer. D-01 and T-01 do this.
  - `_validate_station_only` stays unchanged in both directions. SC-02 and T-01's verify check this
    with `git diff --quiet <base> -- harness_yaml.py` plus the loader-pair case.
  - The INV-34 remedy gains the conversion line. SC-03 and T-01 add it.
  - The plan also seeds `approval: {status: pending}` and stamps `drafted_at` on conversion, which
    the grilling did not spell out. This serves the grilling's own stated reason ("re-enables the
    approval and STATE.md checks"). It is not new scope.
- **orchestrator** — **pass**, with one residual already disclosed in the BRIEF's Verification gaps.
  This is Destination 2: a plan run whose reader findings were all applied and recorded reports the
  real state instead of a forced FAIL. It is carried by SC-05, SC-06, SC-07, SC-11 and SC-09,
  through T-02 (`validate-digest.py` `_plan_reader_carveout`, checked on disk) and T-05 (the apply
  step runs `set-panel`). T-03 records it in the docs. The plan matches each Settled bullet for
  Defect 2:
  - The carve-out applies only in a plan-mission team. SC-05 checks the plan team, the product
    lead and `feature.json` `mission: plan`.
  - It applies only once every finding the reader raised is `resolved` on disk. SC-05 and SC-06
    cover this, including historical open rows.
  - The lead's claim is never enough. The `plan.yaml` on disk is re-read, and SC-06 includes the
    absent and mismatched cases.
  - Any open finding keeps the FAIL. SC-06 covers this.
  - Every other team keeps DEC-123's roll-up. SC-07 covers this.

  Residual: pm's own conduct, meaning whether pm actually resolves exactly the findings it applied,
  is unproven until the first plan run after ship. SC-11 proves the prompt text and the real
  record-panel → set-panel → validate-digest chain, not the agent's behaviour. The BRIEF names this
  gap at signature (DEC-187 excludes `eval`).
- **code maintainer** — **pass**. Carried by SC-08 (inspection, at `git show <review_sha>:`) and
  SC-09, through T-03 and T-05.
  - T-03 amends DEC-123, DEC-254 and DEC-228, regenerates `DECISIONS-INDEX.md`, and covers the SPEC
    roll-up paragraph and the `harness-team` roll-up row.
  - T-05 updates `plan-phase.md` and `panel-recording.md`.
  - At base, `git grep` for worst-member, worst-wins and roll-up statements across `.claude/skills`,
    `.claude/agents`, SPEC and the glossary turns up only SPEC.md:1976-1978, harness-team
    SKILL.md:115, DECISIONS/INDEX DEC-123, and the code comment `validate-digest.py` `# --- LEAD
    ROLL-UP: the top verdict must be the WORST member verdict`. Station-only prose shows up only in
    `reject-path.md`, and its reject flow (a finished station, which T-01 refuses to convert) stays
    true.
  - Advisory, not a fail: T-02 adds a carve-out comment block, but it does not say to qualify that
    unchanged `LEAD ROLL-UP` header comment. The perspective names SPEC, skill or team text, and
    that line is code, so it falls outside the promise. The build may qualify it in passing.

## T-04 and T-05 against the grilling's Out of scope

| Out-of-scope item | T-04 | T-05 |
|---|---|---|
| Plan readers' contract (FAIL carries findings) | untouched | untouched: it changes pm's `apply` step, and readers still return FAIL with findings |
| INV-34 firing time | untouched: test-only witness, no guard or check-state change (D-04) | untouched |
| Any other roll-up rule | untouched | untouched |
| #2622 and #2627 | untouched | untouched |

- **T-04 stays inside scope.** It adds cases to `tests/integration/test-lead-start-return.py` only
  and changes no gate. It proves Destination 1 end to end. D-04 is the scope-narrowing choice here:
  no dispatch-guard change.
- **T-05 stays inside the Out-of-scope list but widens the surface set.** The grilling's Mission
  named three surfaces: the loader and writer, the check-state remedy, and the validate-digest
  roll-up. T-05 adds a fourth: `teams/plan.yaml`'s apply prompt, `plan-phase.md`,
  `panel-recording.md` and a DEC-228 amend row. The widening is necessary rather than incidental:
  - The base apply prompt (`teams/plan.yaml` at `e69608659e31`, step `apply`) runs `record-panel`
    and `check`, and never `set-panel`.
  - `record-panel` writes every finding `open`.
  - So without T-05, nothing shipped ever writes `resolved`, the carve-out never fires, and
    Destination 2 is not delivered.
  - Base `panel-recording.md` already says a fixed `form` finding "stays present with disposition
    `resolved`". T-05 makes the prompt honour that and extends the same treatment to applied
    substance findings.

  The BRIEF discloses T-05 as a lead ruling that can be struck at signature (OQ-1), with SC-11 and
  the DEC-228 row going with it. The operator should weigh that striking T-05 leaves Destination 2
  without a trigger.

## SC plan-time grades

| SC | Grade | Carrier |
|---|---|---|
| SC-01, SC-02, SC-03 | planned (carried) | T-01, unit, with a red-first proof against base `union.py` and check-state |
| SC-04 | planned (carried) | T-01, inspection |
| SC-05, SC-06, SC-07 | planned (carried) | T-02, unit, with a red-first proof against base `validate-digest.py` |
| SC-08 | planned (carried) | T-03, inspection at the pin |
| SC-09 | planned (carried) | T-01 and T-02 verify blocks run the four integration suites |
| SC-10 | planned (carried) | T-04, integration, red-first via `LEAD_START_UNION` |
| SC-11 | planned (carried) | T-05 (prompt order) and T-02 `bug2582-producer-witness` and `bug2582-apply-prompt-resolves` |

None of these is `met` yet. No code has shipped, and the build-time goal-check grades them from
qa's and the reviewers' evidence.

## Open

- None blocking. One question for the operator at signature: keep T-05 (OQ-1). Striking it removes
  Destination 2's only trigger.
