# Goal-check: FEAT-2622-practicality-rule, validate run 2026-11-28-03, cycle 2

**BLUF: PASS.** All three perspectives pass: operator, reader and code maintainer. All 15 SCs are
met at the pin, and SC-09 now carries every clause in all four files it names. Both decision
dispositions are met: DEC-206 amend and DEC-123 amend. DEC-123's rewritten carve-out matches
`validate-digest.py _matched_row_reason` and `_row_relieves`, clause for clause. Two advisories
carry over from c1, both low/form and non-gating.

Pin `edcda5be`, base `3e979ae3`. Every content read uses `git show edcda5be:<path>` or a
`git archive` of the pin at `/tmp/gc2622c2/pin`, run with `HARNESS_PROJECT_DIR` set to the
archive and `HARNESS_AGENT_TYPE` unset.

## Correction to my c1 note

c1 graded `teams/validate.yaml` as carrying every SC-09 clause. That was wrong. At `d131c231`,
its lead bullet ended at "with a one-line reason naming the reader's severity; a remedy touching
signed text …" and had neither "never raising a severity" nor "never revising kind". The code
reviewer's MF-4 was right, and my c1 grade of `partial` understated the gap. The c1 note stays as
written, because the record is not rewritten.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-02, SC-03, SC-05, SC-07, SC-09, SC-15 | see the SC rows below |
| reader | **pass** | SC-01, SC-04, SC-08, SC-10, SC-11 | see the SC rows below |
| code maintainer | **pass** | SC-06, SC-12, SC-13, SC-14 | see the SC rows below |

## SC verdicts

**SC-01, SC-04, SC-08, SC-10 and SC-13 are met, carried from c1.** The fix round
(`git diff --stat d131c231 edcda5be`) did not touch the surfaces that carry them:
- `schemas/digest/common.json`;
- `harness-code-review/SKILL.md`;
- the security-reviewer body;
- the reader prompts in `teams/*.yaml`.

Re-executed on the pin archive:
- `tests/unit/test-practicality-rule.py` ran 31/31 with rc 0.
- `gen-agent-output.py --check` printed `agent output: ok` with rc 0.
- `tests/unit/test-digest-dev-skill.py` exited rc 0.

**SC-02, SC-03 and SC-15 are met (automated).** `test-practicality-rule.py` passes 31/31 at the
pin. Since MF-2, each refusal case requires the rule's own message at its own location, and each
acceptance case requires a clean digest.
- `practicality-discounted-high-medmax-capped` isolates the `_severity_errors` ceiling.
- `practicality-carveout-{discounted-open-relieved, plausible-open-denied, stale-row-current-high-denied}`
  carry SC-15's relief and denial cases.

Fail-first evidence is in `notes/fail-first-T-01.md`. The MF-1 red case and its mutation proof
are in the receipt, §Fix round 1. I accept both as recorded and did not re-measure them.

**SC-05 is met (automated).** `tests/unit/test-practicality-record-panel.py` passes 6/6 at the
pin, and `test-panel-findings.py` passes 13/13. `plan_merge/panel.py` did not change in the fix
round.

**SC-06 is met (inspection).** It holds as in c1. The fix adds `_discounted_non_gating`
(`validate-digest.py`), which calls `panel_findings.is_discounted` and `is_non_gating` and does
not restate them.

**SC-07 is met (inspection), under ruling VAL-OQ-01.** I ran `git diff --name-status 3e979ae3 edcda5be`:
- No path outside `features/FEAT-2622-practicality-rule/` changed under any feature directory. The
  grep for other features' paths found nothing (exit 1).
- The only `runs/` paths are ten files under this feature's own
  `runs/2026-11-28-01-plan-product/` and `runs/2026-11-28-02-validate-validator/`. Every one has
  status `A`.
- The base tree has zero paths under this feature's `runs/`, so no historical record was
  rewritten.
- `bin/check_state/run_state.py` is unchanged (`git diff --quiet`, rc 0).

**SC-08 is met (inspection).** It carries from c1. Neither file changed in the fix round.

**SC-09 is met (inspection).** Clauses quoted at the pin:
- **`.omp/agents/harness-validator-lead.md`, §Assessing step 4:**
  - "Triage by the practicality rule, before routing … lowered to at most `med` or dropped, with
    a one-line reason beside it in your artifact naming the reader's severity and exposure. Never
    raise a severity. A remedy that would touch signed text reaches the operator (`open_questions`
    or `ESCALATE`) only when its finding survives this triage."
  - §Every finding carries `kind`: "never revise a reader's `kind`, and revise its severity only
    downward under the practicality rule".
  - Collation: step 4 sits in "Assessing", the list that turns five reader lists into one set.
- **`.omp/agents/harness-product-lead.md`, fan-in paragraph:**
  - "never revise a reader's `kind`, and revise its severity only downward under the practicality
    rule, applied before you write `panel-c<N>.md`, with a one-line reason recorded beside the
    finding".
  - "In this team a `contrived`, `no_worse`, non-adversary finding is lowered to at most `med`,
    never dropped, so its panel row exists".
  - "Never raise a severity. A remedy that would touch signed text reaches the operator
    (`open_questions` or `ESCALATE`) only when its finding survives this triage."
  - Collation: the fan-in is written before `apply`, so this is before routing.
- **`teams/validate.yaml`, lead digest comment:** "triage by the practicality rule before routing:
  a finding that is contrived, no_worse and not adversary-controlled is lowered to at most med or
  dropped, with a one-line reason naming the reader's severity, never raising a severity and never
  revising kind; a remedy touching signed text reaches the operator only when its finding survives
  this triage".
- **`teams/plan.yaml`, fan-in comment:** "the lead lowers to at most med a finding it discounts
  (contrived, no_worse, not adversary-controlled), with a one-line reason, never raising a severity
  or revising kind; in this team it lowers rather than drops, so the panel row exists … A remedy
  that would touch signed text reaches the operator only when its finding survives this triage."
  - Collation: the comment governs the fan-in file written before `apply`.
- **Banned phrase:** `never revise a reader's severity` appears 0 times in each agent body
  (`git show … | grep -c`).
- **Two softer readings, accepted:**
  - The validate.yaml bullet says the reason is "naming the reader's severity" rather than
    "recorded beside it". It is a bullet in the list of what the consolidated digest must carry,
    so the reason lands in the digest beside the finding.
  - plan.yaml states no explicit "before routing". Its fan-in timing implies it.

**SC-10 is met (inspection).** It holds as in c1. The fix changed only the lead comments in
`teams/*.yaml`, and the reader prompts are unchanged.

**SC-11 is met (inspection).** All three clauses are quoted from each file at the pin:
- **`harness-tdd-enforcement/SKILL.md` § Plausible inputs, not exotic ones:** "Tests target the
  code's plausible inputs. Adversarial and malformed-input tests belong only where input crosses a
  trust boundary (external input, credentials, a gate meant to refuse); their absence elsewhere is
  neither a coverage gap nor a finding."
- **`harness-verification-rules/SKILL.md`:** "Tests target the code's plausible inputs, so an
  adversarial or malformed-input expectation for code where no input crosses a trust boundary is
  neither a coverage gap nor a finding". Its "belong only where" clause is stated as the
  contrapositive, which is equivalent.
- **`.omp/agents/harness-qa.md`:** "Tests target the code's plausible inputs. Adversarial and
  malformed-input tests belong only where input crosses a trust boundary (…); their absence
  elsewhere is neither a coverage gap nor a finding".

**SC-12 is met (inspection).**
- DEC-260 begins at pinned line 8846 and states every element the SC lists:
  - the three questions (the record bullet);
  - the enums;
  - the discount predicate;
  - the `med` ceiling;
  - the `must_fix` link;
  - the adversary exception;
  - `unrated`;
  - forward-only (D-04).
- Its D-06 bullet now also states the stale-row condition.
- The DEC-206 and DEC-123 changes are graded under Decision dispositions below.
- **Executed:** `gen-decisions-index.py --stdout | cmp - DECISIONS-INDEX.md` on the pin archive
  printed INDEX-EQUAL.

**SC-13 is met (automated).** The re-executed results are listed above. The red state at the
schema-only commit is in the T-03 receipt row.

**SC-14 is met (automated).** Executed on the pin archive:

| Test | Result |
|---|---|
| `test-validate-digest-shadows` | 46/46 |
| `test-panel-findings` | PASS |
| `test-plan-merge` | PASS |
| `test-check-state-records` | rc 0 |
| `test-check-omp-port` | 39/39 |
| `test-plan-team` | 184/184 |
| `test-validate-digest` | ALL PASSED, rc 0 |

My first run of `test-validate-digest` hit my own 120 s timeout (rc 124). A re-run with `-u` and
a 900 s ceiling finished in 88 s: `ALL PASSED.`, rc 0, and no `FAIL` or `not ok` lines. The SC's
fail-first evidence is in `notes/fail-first-T-02.md`. Per the ruling, the base pool abort is an
environment fact and not a finding.

## Decision dispositions (pinned `git show edcda5be:.harness/harness/docs/DECISIONS.md`)

- **DEC-206 amend: met.**
  - The plan row's clause "whether a defect exists at all, and how severe the reader judged it."
    has 0 hits at the pin.
  - Pinned lines 6802–6806 read: "The lead never owns CONTENT — whether a defect exists at all —
    and never raises the severity the reader judged; it may lower a finding to at most `med`, or
    drop it, only when the practicality rule (DEC-260) discounts it, with a one-line reason beside
    the finding." That is successor D-03.
- **DEC-123 amend: met.** Pinned lines 2496–2503 replace "and every other on-disk row attributed
  to it is `resolved`" with three clauses:
  - "that row is `disposition: resolved` or, under the practicality rule (DEC-260), open with
    both the row and the digest's current finding discounted at a non-gating severity";
  - "and every other on-disk row attributed to it is `resolved` or open and discounted at a
    non-gating severity";
  - "An open row that is not so discounted, a stale discounted row whose current finding is not
    … keep worst-wins".

  The amendment is rewritten in place, per DEC-205. The plan row's reason ("every other case keeps
  worst-wins") holds.

  **Against the code** (`validate-digest.py`, at the pin):
  - The matched row: `_digest_finding_reason` → `_matched_row_reason(item, row, pfid)` returns
    `None` (relief) only when `row.disposition == "resolved"`, or when
    `_discounted_non_gating(row) and _discounted_non_gating(item)`. This is the text's "open with
    both the row and the digest's current finding discounted at a non-gating severity".
  - Every other attributed row: `_candidate_reason` → `_open_row_reason` → `_row_relieves(row)`
    gives resolved, or the row alone is discounted at a non-gating severity. This is the text's
    "every other on-disk row … resolved or open and discounted at a non-gating severity".
  - The predicates: `_discounted_non_gating` = `panel_findings.is_discounted(exposure)` and
    `is_non_gating(severity)`, which is the one shared definition (SC-06).
  - **Executed boundary probe** (P-19): an in-memory variant of `test-practicality-rule.py`'s
    `run_carveout` on the pin archive passed 32/32. It reused the shipped helpers; no file was
    written. Over an open discounted `med` row, with the current finding as listed:

    | Current finding | Outcome |
    |---|---|
    | plausible `med` | relief denied |
    | adversary-controlled contrived/no_worse `med` | relief denied |
    | `unrated` `med` | relief denied |
    | discounted `low` | relieved |

    The code therefore denies relief whenever the current finding is not discounted, even when its
    severity is non-gating. The text "a stale discounted row whose current finding is not [so
    discounted]" says the same. Code and decision agree.
- DEC-31, DEC-228, DEC-230, DEC-237, DEC-174 and DEC-229 are `keep` rows and are not graded.

## Advisories (not gating, carried from c1)

- **A-1 (low, form, T-05).** DEC-206 still follows the new lowering permission with an
  unqualified "A lead that supplies a severity the reader did not emit has manufactured evidence"
  (pinned line 6806). A reader can take it as forbidding the lowering. Exposure: `{trigger:
  plausible, vs_today: no_worse, control: harness}`.
- **A-2 (low, form, T-01).** `_severity_max_errors` restates the gating band as the literal
  `("high", "critical")` beside `is_non_gating`. Exposure: `{trigger: contrived, vs_today:
  no_worse, control: harness}`, so it is discounted and at most med.

## Principles applied

- harness-pm Expertise P-04 and P-06: I graded SC-09 and SC-11 per file and per clause by quoting
  each at the pin, and re-measured MF-4's premise directly rather than relying on the fix receipt.
- harness-pm Expertise P-19: one probe one boundary beyond the stale-row case (a current finding
  at a non-gating severity that is not discounted).
