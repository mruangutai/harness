# Goal-check: FEAT-2622-practicality-rule, validate run 2026-11-28-02, cycle 1

**BLUF: FAIL, on one partial SC.** reader and code maintainer pass. operator is **partial**: SC-09's
clause "a remedy touching signed text reaches the operator only when its finding survives triage"
is in the validator-lead body and in `teams/validate.yaml`. It is absent from the product-lead body
and from the lead comments in `teams/plan.yaml`. The plan never asked for it there (T-03 step 5,
T-04 step 4), so this is a plan defect that the build carried out faithfully. Both decision
dispositions (DEC-206 amend, DEC-123 amend) are **met** at the pin. Every relief path I probed
fails closed except the one intended path, an open row discounted at a non-gating severity, which
relieves.

Pin `d131c231`, base `3e979ae3`. Every content read uses `git show d131c231:<path>` or a
`git archive` of the pin at `/tmp/gc2622/pin`.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **partial** | SC-02, SC-03, SC-05, SC-07, SC-15 met; SC-09 partial | see SC table; the gap is SC-09 |
| reader | pass | SC-01, SC-04, SC-08, SC-10, SC-11 | see SC table |
| code maintainer | pass | SC-06, SC-12, SC-13, SC-14 | see SC table |

## SC verdicts

- **SC-01 met (automated).** `common.json $defs.exposure` (an anyOf of a closed mapping and the
  const `unrated`), required on `$defs.finding`. `tests/unit/test-practicality-rule.py` cases
  `practicality-{missing-exposure,offenum-exposure,extra-key,missing-inner-key,invalid-string}-refused`
  and `-wellformed-accepted` pass at the pin (I ran it: 29/29, rc 0). Fail-first is in
  `notes/fail-first-T-01.md`, red at base 16 of 16. Per OQ-04, one shared `$ref` is cited.
- **SC-02 met (automated).** `panel_findings.practicality_fault` is wired into
  `validate-digest.py _severity_errors`. The `severity_case` rows pass: discounted-high and
  discounted-unrated are refused; med, adversary-high, regression-high, plausible-high and
  unrated-exposure-high are accepted.
- **SC-03 met (automated).** `_discounted_must_fix_errors` / `_names_finding`. Cases
  `practicality-mustfix-{summary,pfid}-refused` and `-other-finding-accepted`.
- **SC-04 met (automated).** `_unrated_errors` gated on `_STATES_OWN_EXPOSURE`. Cases
  `practicality-unrated-{refused,accepted}-*` cover all six personas.
- **SC-05 met (automated).** `plan_merge/panel.py _validate_finding_exposure`, plus
  `shape_faults` → `_exposure_row_faults`. `tests/unit/test-practicality-record-panel.py` passes
  6/6 at the pin (I ran it). `tests/integration/test-panel-findings.py case_exposure_shape`
  7a–7c covers the legacy row returning `[]` and a malformed exposure being reported. Fail-first
  is in `notes/fail-first-T-02.md` (5 of 5).
- **SC-06 met (inspection).** `panel_findings.py` defines `is_discounted`, `is_non_gating`,
  `practicality_fault` and `exposure_faults` once. `validate-digest.py` calls them in
  `_severity_errors`, `_discounted_must_fix_errors`, `_discounted_verdict_errors` and
  `_row_relieves`. `plan_merge/panel.py` calls them in `_validate_finding_exposure`.
  `gates_signature` reads `is_non_gating`. Advisory A-2 applies.
- **SC-07 met (inspection).** `git diff --name-status 3e979ae3 d131c231`:
  - No path under another feature's directory changed.
  - The only `runs/` paths are five files of this feature's own plan run
    `runs/2026-11-28-01-plan-product/`, all status `A`. No existing run record was modified.
  - `bin/check_state/run_state.py` is unchanged (`git diff --quiet` exit 0).
  - I read the SC's "no runs/ record" as "no shipped record". If it is read literally, those five
    added files are the only exception.
- **SC-08 met (inspection).**
  - `harness-code-review/SKILL.md § Exposure — the practicality rule` states the three questions,
    the ceiling (at most med; "never `must_fix`, never an escalation, never the reason for a new
    test or another fix round") and the adversary exception.
  - `.omp/agents/harness-security-reviewer.md`, the paragraph "The practicality rule.", states
    the same.
- **SC-09 partial (inspection).**
  - Met:
    - The validator-lead body, step "4. Triage by the practicality rule, before routing", carries
      every clause, including signed text.
    - The `teams/validate.yaml` lead comment ("triage by the practicality rule before routing …
      a remedy touching signed text reaches the operator only when its finding survives this
      triage") carries every clause.
    - Neither agent body contains `never revise a reader's severity` (grep, 0 hits).
    - The product-lead body § Hosting plan and the `teams/plan.yaml` tail comment carry: lower
      only downward, with a one-line reason, never revise kind, lower rather than drop in the
      plan team.
  - **Missing:**
    - The signed-text clause is absent from `.omp/agents/harness-product-lead.md`. Its only
      operator mention is the DEC-228 dissent line.
    - The signed-text clause is absent from the `teams/plan.yaml` lead comments. Its nearest
      text is "High, critical, or unrated `substance` findings that survive apply return to the
      operator's one batched signature review". Behaviourally, a lowered-to-med finding therefore
      does not return to the operator, but the stated clause is not there.
    - The product-lead body says "applied before you write panel-c<N>.md", which I accept as "at
      collation". `teams/plan.yaml` names no timing.
  - Cause: the T-03 step 5 and T-04 step 4 intents never asked for the clause, while the T-03
    verify list for product-lead omits "signed text" and validator-lead's includes it.
  - Exposure of the gap: `{trigger: plausible, vs_today: no_worse, control: harness}`. It is not
    discounted, and it is a form fix in two documents.
  - Remedy owners: T-03 (`harness-product-lead.md`) and T-04 (`teams/plan.yaml`), both
    main-session-direct.
- **SC-10 met (inspection).**
  - `teams/plan.yaml` scope, should-not-exist and design prompts require exposure.
    should-not-exist says "write exposure: unrated, never omit it".
  - `teams/validate.yaml` code, security and ui prompts require exposure.
  - The fan-in header comment in `teams/plan.yaml` lists `exposure`, as do
    `references/panel-recording.md` and `templates/plan.yaml` (panel finding example).
- **SC-11 met (inspection).** The trust-boundary sentence plus "neither a coverage gap nor a
  finding" appear in `harness-tdd-enforcement/SKILL.md`, `harness-verification-rules/SKILL.md`
  and `.omp/agents/harness-qa.md`.
- **SC-12 met (inspection).**
  - DEC-260 at pinned line 8845 states the three exposure questions (record bullet), the enums,
    the predicate, the med ceiling, the `must_fix` link, the adversary exception, `unrated` and
    forward-only.
  - The DEC-206 and DEC-123 amendments are covered in the dispositions section below.
  - **Executed:** `gen-decisions-index.py --stdout | cmp - DECISIONS-INDEX.md` on the pin archive
    printed INDEX-EQUAL.
- **SC-13 met (automated).** **Executed:** on the pin archive, `gen-agent-output.py --check`
  printed `agent output: ok` with rc 0, and `tests/unit/test-digest-dev-skill.py` passed with
  rc 0. The red-at-schema-only state is recorded in the T-03 receipt row; I did not re-measure it.
- **SC-14 met (automated).** **Executed** on the pin archive with `HARNESS_PROJECT_DIR` set to it:
  - `test-validate-digest` ALL PASSED.
  - `-shadows` 46/46.
  - `test-panel-findings` PASS.
  - `test-plan-merge` PASS.
  - `test-check-state-records` rc 0.
  - `test-check-omp-port` 39/39.
  - `test-plan-team` 184/184.

  The fail-first measurement is disclosed deviation 2 (a direct run of base
  `case_f59_record_panel_writes_from_a_lead_digest` gives rc 5, naming exposure). I accept it as
  disclosed and did not re-measure it.
- **SC-15 met (automated).** The `verdict_case` rows (severity_max discounted-only refused,
  witnessed accepted, FAIL discounted-only refused, FAIL with must_fix accepted) and the
  `run_carveout` relieved and denied pair all pass.

## Decision dispositions (pinned `git show d131c231:.harness/harness/docs/DECISIONS.md`)

- **DEC-206 amend, met.** The planned clause "how severe the reader judged it" has 0 hits at the
  pin (1 at base). Lines 6802–6805 now read "never owns CONTENT — whether a defect exists at all —
  and never raises the severity the reader judged; it may lower a finding to at most `med`, or drop
  it, only when the practicality rule (DEC-260) discounts it, with a one-line reason". That is D-03
  as signed. See advisory A-1.
- **DEC-123 amend, met.** Lines 2499–2502 extend "every other on-disk row attributed to it is
  `resolved`" with "or, under the practicality rule (DEC-260), open at a non-gating severity with a
  discounted exposure", and the open-finding exception is carved to match. That is D-06 as signed.
  Code agrees: `validate-digest.py _row_relieves`.
- **The receipt's deviation 3 (rewrite, not "Amended by") is correct.** DEC-205 ("The amendment
  convention is ended … A correction rewrites the entry it corrects") makes rewriting in place the
  only lawful landing. Mode 2's amend test asks whether the intended current text replaced the
  clause, and it did. The step-2 instruction in T-05 conflicted with DEC-205, which is a plan-text
  defect with no effect on the landing.
- DEC-31, DEC-228, DEC-230, DEC-237, DEC-174 and DEC-229 are keep rows and are not graded. The new
  entry is DEC-260, line 8845, with index row 243 and back-refs from DEC-123 (row 128) and DEC-206
  (row 204).

## Relief probes (execution-backed; `/tmp/gc2622/probe.py`, pin vs base)

All probes ran against the pin's `validate-digest.py`. The fixture's code_grade/artifact noise is
present on every case and is ignored.

- **Severity spelling variants.** `HIGH`, ` high`, `High`, `medium`, `unrated`, `none` and
  `critical` on a discounted finding all hit the rule. `Med` passes the ceiling, as it should, by
  trimmed and case-folded `is_non_gating`.
- **Malformed exposure.** `Contrived`, `contrived `, a missing control, `Unrated`, an absent
  exposure and `{}` are all schema-refused and never discounted, so the rule fails closed.
- **A non-discounted gating finding beside a discounted one.** A FAIL with severity_max high
  stands, with no rule error.
- **FAIL with `code_grade: fail` and only discounted findings.** Accepted.
- **must_fix links.** The full PF id in upper case, an 8-hex prefix, a 14-hex prefix in brackets
  and a whitespace- or case-variant summary are all refused. A 7-hex prefix is not caught, which
  is within the OQ-01 ruling.
- **Carve-out.** Only an open `med` row with a discounted exposure relieves. These deny relief:
  - a row with severity `Med` (shape enum, fail-closed);
  - discounted plus a plausible open med row;
  - a discounted row at high (malformed panel);
  - an unrated row;
  - a row with a malformed exposure;
  - an adversary row;
  - a digest that claims discounted while its row says plausible;
  - a legacy row with no exposure.

  At base, every carve-out case denies relief.

## Advisories (not gating)

- **A-1, low, form.** DEC-206 keeps "A lead that supplies a severity the reader did not emit has
  manufactured evidence" right after the new lowering permission, unqualified. A reader can take
  it as forbidding the lowering. Exposure: `{plausible, no_worse, harness}`.
- **A-2, low, form.** `_severity_max_errors` restates the gating band as the literal
  `("high","critical")` beside `is_non_gating`. `_reviewer_fail_errors` treats `severity_max: none`
  as gated, so a discounted-only FAIL with `severity_max: none` is not refused. No relief is
  granted wrongly. Exposure: `{contrived, no_worse, harness}`, at most med.
