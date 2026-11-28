# Research — FEAT-2622 practicality rule (pm draft, 2026-11-28)

Observed at worktree HEAD `3e979ae3cd303fdf65746bf13c8c8e041dac4964`, plan pending, no review_sha.

## Bottom line

The rule fits existing machinery with one shared predicate in `bin/panel_findings.py`, a required
`exposure` key on `schemas/digest/common.json` `$defs.finding`, one semantic gate in
`validate-digest.py`, and a carried-and-checked key in `plan_merge/panel.py` record-panel. Forward
only needs no era marker. Both leads' "never revise a reader's severity" lines need the amendment,
and DEC-206's content clause is the decision text that says the same thing.

## Facts (each command-checked at the HEAD above)

- `$defs.finding` is closed (`additionalProperties: false`), requires
  `kind, scope, severity, reader, summary, why`; `severity` is free `text`, not an enum.
  Six persona schemas reference `$defs.findings`: code-reviewer, security-reviewer, ui-reviewer,
  eng-lead, product-lead, validator-lead. **QA's schema has no `findings`** (it has
  `coverage_gaps`, a string list), so QA's part of the rule is testing guidance, not a field.
- `must_fix` is `$defs.string_list`: free prose. Observed entries cite findings by short PF id
  (`PF-15af8306 (med, scope): ...`, FEAT-2581 repanel3 digest) or by `MF-1 (T-02, substance,
  high): ...` (BUG-2582 validate c2). Nothing links an entry to a finding mechanically.
- `panel_findings.py`: `REQUIRED_KEYS = (id, severity, reader, kind, summary, disposition)`,
  `FINDING_KEYS = REQUIRED_KEYS + (scope, resolved_by)`, `NON_GATING_SEVERITIES = {info, low,
  med}`, `gates_signature` treats any other severity (incl. `unrated`) as gating. `shape_faults`
  is used by set-panel, record-panel, sign-approval and check-state INV-32.
- `plan_merge/panel.py#_digest_finding` builds each panel row from the lead fan-in digest and drops
  every key outside the closed set (`why` included).
- The plan-panel fan-in `<run_dir>/panel-c<N>.md` is read by record-panel and never by
  validate-digest; fable-advisor (should-not-exist) is a non-harness reader (DEC-206) whose return
  is not schema-validated. So a plan-level discounted-high finding is caught only if record-panel
  checks it.
- `check_state/run_state.py` INV-15 comment: a historical digest record is checked for top-level
  keys only, "never a live-schema re-validation, since a historical record may hold keys today's
  closed contract refuses". validate-digest runs on live yields (hook) and on close-run of the run
  being closed.
- `tests/unit/test-digest-dev-skill.py` validates the `yield({data: ...})` examples in agent
  bodies against the live schemas: three examples carry findings (code-, security-, ui-reviewer)
  and will redden when `exposure` becomes required.
- `gen-agent-output.py --check` prints `agent output: ok`; `gen-decisions-index.py --stdout`
  equals the committed index (both at HEAD).
- Routes (`check-domain.py --resolve`): bin and tests → backend-dev/dev-ops(/qa); schemas,
  `.omp/agents/*`, skills, teams, templates, references → NOBODY; DECISIONS* → documentor.
  DEC-174 plus operator constraint 6 make every task main-session-direct.
- Durations (integration-durations.json): test-validate-digest 36.6s, test-plan-merge 27.5s,
  test-check-state-records 12.8s, test-plan-team 10.3s. These force the gate work into two tasks
  to keep each verify under 60s.

## Resolutions of the grilling's "Not yet specified"

1. **Panel findings carry `exposure`.** `panel_findings.FINDING_KEYS` gains `exposure` as an
   OPTIONAL key validated when present; record-panel REQUIRES it on every digest finding it newly
   transcribes, carries it into the row, and refuses a discounted finding at a gating severity.
   Optional in the shape keeps every existing plan's panel rows legal (forward only); required at
   the writer means every new row has it. `gates_signature` is unchanged: a discounted finding
   cannot land above `med`, so it never gates a signature.
2. **Missing `exposure` is a refusal** at the schema (like `kind`), because harness readers yield
   schema-bound objects and a refusal costs one re-yield. The DEC-206 parallel survives as the
   literal sentinel `unrated` — legal only in a lead digest transcribing a reader that gave none —
   and an `unrated` exposure is never discounted, so an omitted judgement keeps the reader's
   severity (fails closed toward today's behaviour, never toward suppression).
3. **Forward only without an era marker.** Validation already binds only live yields and the run
   being closed; INV-15 never re-validates history; the panel key is optional in shape. A marker
   would add a writer-owned stamp (DEC-254-style) to defend a case that cannot occur. Residual:
   a lead run open across the landing commit whose durable digest lacks `exposure` is refused at
   close-run — the main session lands this with no run open (open question OQ-02).

## Product lead amendment — yes

record-panel will refuse a discounted finding at a gating severity. The product lead transcribes
fable-advisor's unvalidated return; under the current "never revise a reader's severity" line it
has no lawful remedy for such a refusal, and a gating plan finding is exactly the operator
escalation the rule forbids (it withholds signature until ruled). So the product-lead fan-in rule
needs the same triage authority as the validator lead, bounded the same way: downward only, with
a one-line reason, never `kind`.

## Decision record search (DECISIONS-INDEX)

- DEC-31 keep: the gate is unchanged; the rule only decides what may enter it.
- DEC-206 amend: "The lead never owns CONTENT — whether a defect exists at all, and how severe the
  reader judged it." The lead now lowers severity or drops a finding the rule discounts.
- DEC-228 keep: `kind` stays; `exposure` is an additional key.
- DEC-230 keep: an unclassifiable exposure is one question with a recommendation; `unrated`
  never routes to the heavier path silently — it keeps today's severity.
- DEC-237 keep: exposure lands in the canonical schema and reaches agents through
  gen-agent-output.py only.
- DEC-174 keep: planned through Harness, executed main-session-direct.
- New decision: the rule itself (three questions, enums, predicate, `med` ceiling, must_fix
  link, adversary exception, `unrated` sentinel, forward-only basis). Written by T-05 with the
  next free DEC number; plan D-01..D-05 are its content.

## Rejected alternatives (so a later scan does not re-suggest them)

- A structured `must_fix` (list of finding references): would change every persona's must_fix
  contract and the validator-lead's non-finding entries (pm not_met rows); the summary/PF-id
  containment check catches the honest copy case at no contract cost (OQ-01).
- An era key in harness.json for digests: nothing re-validates history, so it defends nothing.
- `med` vs `low` ceiling: `med` is DEC-31's non-gating band and code-review's "wrong behaviour in
  an unlikely case", which is the contrived case by definition.
