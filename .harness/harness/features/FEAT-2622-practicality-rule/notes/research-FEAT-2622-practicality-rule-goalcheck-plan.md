# Goal-check (plan exit) — FEAT-2622-practicality-rule

**Verdict: FAIL — one fix needed before signature.** The plan does deliver the operator's stated
intent (`.harness/notes/grilling-practicality-rule-2026-11-28.md`): every perspective is carried
and all seven dispatch constraints are met. The problem is T-01's `verify:`, which cannot pass
even when the build is correct. Four of its 16 red-first cases are already green at base, so the
gate that every other task depends on (they all list T-01 in `depends_on`) would stay red. The fix
is a single change to the test predicate in T-01 intent item 4. No BRIEF or decision changes.

Graded against plan.yaml and BRIEF.md in the feature worktree, base `3e979ae3`.
`plan-merge.py check`: 5 tasks, 28 anchors, 0 failures.

## Perspectives — one line each

- **operator: pass.** SC-02, SC-03 and SC-15 (T-01) cover the mechanical refusal of a
  contrived + no_worse + non-adversary finding in `must_fix`, at high or above, or as a sole FAIL.
  The adversary exception is accepted at `high` in SC-02 and SC-05. SC-05 (T-02) covers the
  plan-panel writer, SC-09 (T-03, T-04) the lead triage before routing, and SC-07 (T-02) forward
  only. Advisory: the grilling's "never an operator escalation" is enforced only by guidance
  (D-03 triage, SC-09). It is not refused mechanically. That matches the settled shape (Settled:
  must_fix or high+), but the operator should know at signature.
- **reader (reviewer / qa / panel): partial.** SC-01 and SC-04 (T-01), SC-08 (T-03, T-04),
  SC-10 (T-04) and SC-11 (T-03, T-04) carry it in full. The partial is SC-01's fail-first, which
  cannot be met as written (defect below). Until that is fixed, T-01's gate stays red, so the
  "gate tells me at yield" promise cannot land.
- **code maintainer: pass.** SC-06 (T-01, T-02) puts one predicate in `bin/panel_findings.py`,
  with no second non-gating set. SC-12 (T-05) covers the new DEC and the DEC-206/DEC-123
  amendments. SC-13 (T-03) regenerates the agent output through `gen-agent-output.py`, never by
  hand. SC-14 (T-01, T-02, T-03) keeps the existing suites green. All 15 SCs are traced by at
  least one task, and no SC is orphaned.

## Defect — T-01 verify cannot pass (measured)

At base, `$defs.finding` in `schemas/digest/common.json` has `additionalProperties: false`.
Running `digest_schema.validate_object("harness-code-reviewer", …)` against the base tree with a
finding that carries any `exposure` value returns
`DIGEST/findings/0: Additional properties are not allowed ('exposure' was unexpected)`.

T-01 intent item 4 says a schema refusal case passes when "some error names exposure". The
following four cases therefore print PASS on the base archive:

- `practicality-offenum-exposure-refused`
- `practicality-extra-key-refused`
- `practicality-missing-inner-key-refused`
- `practicality-invalid-string-refused`

The verify's red-first block lists those four as "not red at base" and exits 1. SC-01's "qa must
show the refusal cases fail against the base copy of the schema first" cannot be met for them on
that predicate.

**Remedy (T-01 intent item 4 only):** a schema refusal case passes when some error names
`exposure` **and** no error says `'exposure' was unexpected`. On the base schema the only error is
the unexpected-key one, so all four cases fail at base. On the new schema the `anyOf`/enum error
names the `exposure` path, so they pass. `practicality-missing-exposure-refused` is already red
at base and is unaffected.

## Operator's seven dispatch constraints

1. **Structured exposure on every reader finding — carried.** D-01 and the `common.json` finding
   (T-01) cover the code, security and UI reviewers and the eng, product and validator leads.
   The plan-panel readers are covered through the T-04 prompts and the record-panel requirement
   (T-02, D-05). fable-advisor is transcribed as `unrated` by its lead. QA has no `finding` in its
   schema (checked at base), so its part is guidance only, which D-01 states.
2. **validate-digest refusal — carried.** D-02 and SC-02/03 (T-01) refuse a discounted finding in
   `must_fix` or at a gating severity. The adversary exception is never discounted: the
   `is_discounted` intent excludes `control: adversary`, and
   `practicality-adversary-high-accepted` tests it.
3. **Validator-lead triage at collation — carried.** D-03, SC-09, T-03 step 4 (validator-lead
   body), T-04 step 5 (validate.yaml) and T-05 (the DEC-206 amend). "never revise a reader's
   severity" is replaced, and T-03's verify asserts it is gone. A remedy touching signed text
   reaches the operator only if its finding survives triage. The plan extends the same authority
   to the product lead (D-03) and amends DEC-123 (D-06). Both go beyond the grilling, are argued
   in their `because:`, and need the operator's signature.
4. **Adversarial / malformed-input tests only at trust boundaries — carried.** SC-11, T-04 step 2
   (harness-tdd-enforcement), T-04 step 3 (verification-rules), T-03 step 6 (harness-qa body) and
   T-04 step 5 (validate.yaml qa prompt).
5. **Forward only — carried.** D-04, SC-07, T-02's verify (`run_state.py` byte-identical to base),
   and `exposure` optional in the panel row shape (D-05, SC-05 legacy row).
6. **Every task main-session-direct — carried.** T-01 to T-05 all have
   `execution_mode: main-session-direct`.
7. **DEC-31/206/228/230 disposition stated — carried.** `decisions_affected` lists DEC-206 as
   amend (successor D-03), and DEC-31, DEC-228 and DEC-230 as keep. All four clauses are verbatim
   in DECISIONS.md (grep in the worktree). DEC-123 is amended too (D-06).

## Principles applied

- **Attack the Premise** was not applied; no repeated fix failures.
- The grading follows `harness-spec-driven` §"verify: is a literal block": each red-first verify
  was run against its consumer (expertise P-08).

## Re-grade after apply send-back

**Verdict: PASS. The plan delivers the operator's stated intent and is ready for signature.** The
amended T-01 intent item 4 closes Q-01, which I re-measured against base `3e979ae3`. The new
predicate turns no criterion previously graded met into a failure. `plan-merge.py check`
(control-plane copy) reports 5 tasks, 28 anchors and 0 failures.

### Q-01: closed by the fix (re-measured, not argued)

T-01 item 4 now says a schema refusal case passes when "some error names exposure and no error
contains the text 'exposure' was unexpected". I measured this with a probe. Base was a `git archive
3e979ae3`. Built was the same archive with only `common.json` patched, exactly as T-01 item 2 says
(`$defs.exposure` anyOf, `exposure` added to the finding properties and to `required`). The probe
ran `digest_schema.validate_object` for all six finding-carrying personas:

- **Base.** All five refusal cases print FAIL under the new predicate for every persona: missing,
  off-enum, extra key, missing inner key, and invalid string. The only error naming exposure is
  `DIGEST/findings/0: Additional properties are not allowed ('exposure' was unexpected)`, or there
  is none at all (missing). This means all four cases from the first grade are now red at base.
- **Built.** All five cases print PASS for every persona. The errors are `'exposure' is a required
  property` and `DIGEST/findings/0/exposure: … is not valid under any of the given schemas`. The
  well-formed and `unrated` accepted cases have no error naming exposure.
- **The other 11 red-first cases** (validate-digest refusals and carve-out relief) depend on the
  words `practicality rule`. `git grep -i practicality 3e979ae3 -- .claude/skills/harness/bin` is
  empty, so the 10 validate-digest refusal cases cannot be green at base. The carve-out
  `relieved` case is red at base because base `FINDING_KEYS` is closed and reports a row carrying
  `exposure` as an extra key, so the carve-out fails closed. [INFERENCE: I read this from
  `panel_findings.py` at base and did not execute it.]

The verify's set of 16 cases checks out: 16 case names contain refused or relieved, and every one
is red at base and green after the build. ALL-PASSED is satisfiable (expertise P-08).

### The other direction (G-07): nothing graded met is falsified

The amendment narrows the predicate for schema refusal cases only. Accepted cases and
validate-digest refusals keep their predicates. The red-first regex and the count of 16 are
unchanged, and no other task, SC or decision text changed. Under the built schema the stricter
predicate still passes, so SC-01's "refuses … accepts each well-formed form" holds. Operator and
code-maintainer grades stand as first graded.

One advisory, inherited and not caused by the fix (P-04/O-14). SC-01 quantifies over six persona
schemas, but item 4 does not say which persona(s) the schema cases run against. All six persona
schemas reference `common.json#/$defs/finding` (grep), and the probe measured identical behaviour
for all six. So the gap is between coverage the test executes and coverage inferred through a
shared definition, not a defect. qa should run the five schema cases per persona or cite the
shared `$ref`. This does not block signature.

### Perspectives, re-graded against the grilling artifact

- **operator: pass.** SC-02, SC-03 and SC-15 (T-01) cover the mechanical refusal of a contrived,
  no_worse, non-adversary finding in `must_fix`, at high or above, or as the sole basis of a FAIL.
  The adversary exception is covered in SC-02 and SC-05. SC-05 (T-02) covers record-panel, SC-09
  (T-03, T-04) covers lead triage before routing, and SC-07 (T-02) covers forward only. The first
  grade's advisory still stands: "never an operator escalation" is carried by D-03 triage guidance
  and not by a mechanical refusal.
- **reader (reviewer / qa / panel): pass**, up from partial. SC-01 and SC-04 (T-01), SC-08 (T-03,
  T-04), SC-10 (T-04) and SC-11 (T-03, T-04) cover it. SC-01's fail-first can now be met (measured
  above), so T-01's gate can go green and the "gate tells me at yield" promise lands. The
  per-persona advisory above applies.
- **code maintainer: pass.** SC-06 (T-01, T-02), SC-12 (T-05), SC-13 (T-03) and SC-14 (T-01, T-02,
  T-03) are unchanged from the first grade.

The operator's seven dispatch constraints stay carried exactly as first graded. The fix touched
none of them.
