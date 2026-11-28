# BRIEF — FEAT-2622-practicality-rule Practicality rule for reader findings and tests

## Problem

Plan-panel and validate readers rate a finding by its mechanism ("can this happen?"), never by its
exposure ("will it, and what does it cost compared with today?"). Contrived findings therefore
become high-severity `must_fix` items, operator escalations, extra fix rounds and tests nobody
needs. Measured on 2026-11-27 (#2622): BUG-2565 fix rounds 2–4 spent about 60 of 113 rework
minutes on exotic YAML fed to a generator that only ever reads Harness's own 16 agent files,
costing three rounds, two budget extensions and residual issue #2604; BUG-2566 E-01 was rated high
by one reader and med by another although its outcome was the pre-feature behaviour, and it still
reached the operator because its remedy touched signed text.

## Done when — by perspective

**operator** — A finding whose trigger is contrived and whose outcome is no worse than today never
reaches me as `must_fix`, as a gating severity or as an escalation, while an adversary-controlled
finding at a real trust boundary keeps its severity however unlikely it is. Records already
shipped stay exactly as they are.

**reader (reviewer / qa / panel)** — Every finding I report states its trigger, its consequence
compared with today and who controls the trigger, and the gate tells me at yield when my severity
breaks the rule. My testing guidance tells me adversarial and malformed-input tests belong only
where input crosses a trust boundary.

**code maintainer** — The rule is one predicate in one place, called by both the digest gate and
the panel writer; the decision record states the rule and the leads' amended authority, and the
generated agent schemas come from the generator, not from hand edits.

## Success criteria

Terms used below. **Exposure record:** the finding key `exposure`, either the closed mapping
`{trigger: routine|plausible|contrived, vs_today: regression|no_worse, control:
harness|chance|user|adversary}` or the literal `unrated`. **Discounted finding:** a finding whose
exposure mapping has `trigger: contrived` and `vs_today: no_worse` and a `control` other than
`adversary`. **Non-gating severity:** `info`, `low` or `med` — `panel_findings.NON_GATING_SEVERITIES`,
the one set `gates_signature` already reads — compared trimmed and case-insensitively; every other
value, `none` and `unrated` included, gates (DEC-31, DEC-206). **Base:**
`3e979ae3cd303fdf65746bf13c8c8e041dac4964`.

- SC-01 (reader): In every persona schema that carries `findings` (code-reviewer,
  security-reviewer, ui-reviewer, eng-lead, product-lead, validator-lead), `digest_schema.validate_object`
  refuses a finding with no `exposure`, with an off-enum value, with a missing or extra key in the
  mapping, or with any string other than `unrated`; it accepts each well-formed form. qa must show
  the refusal cases fail against the base copy of the schema first.
  verify: automated        evidence: unit
- SC-02 (operator): `validate-digest.py` refuses a digest carrying a discounted finding at a
  gating severity, with an error containing the words `practicality rule`; it accepts the same
  finding at `med`, an `adversary`-controlled contrived no-worse finding at `high`, a `regression`
  or `plausible` finding at `high`, and an `unrated` exposure at `high`. qa must show each refusal
  case fails against the base validator first.
  verify: automated        evidence: unit
- SC-03 (operator): `validate-digest.py` refuses a digest whose `must_fix` entry names a
  discounted finding of the same digest — its summary contained after `panel_findings.normalize_summary`,
  or its PF id (`panel_findings.finding_id`) in full or by a prefix of at least `PF-` plus 8 hex
  characters — with an error containing `practicality rule`; a `must_fix` entry naming a
  non-discounted finding is accepted. qa must show the refusal fails against the base validator first.
  verify: automated        evidence: unit
- SC-04 (reader): `validate-digest.py` refuses exposure `unrated` in a code-reviewer,
  security-reviewer, ui-reviewer or eng-lead digest, with an error containing `practicality rule`
  (none of them transcribes a non-harness reader), and accepts it in a product-lead or
  validator-lead digest, where it records a non-harness reader's absent rating (DEC-206). qa must
  show each refusal fails against the base validator first.
  verify: automated        evidence: unit
- SC-05 (operator): `plan-merge.py record-panel` exits 5 when a fan-in digest finding has no
  `exposure`, exits 5 naming `practicality rule` for a discounted finding at a gating severity, and
  otherwise writes the exposure into the new `panel.findings` row unchanged (an adversary-controlled
  `high` included); a base row without `exposure` is carried byte for byte and
  `panel_findings.shape_faults` returns `[]` for it, while it reports a malformed `exposure`. qa
  must show the record-panel cases fail against the base `plan_merge/panel.py` first.
  verify: automated        evidence: unit
- SC-06 (code maintainer): At `review_sha`, the discount test and the non-gating set are defined
  once, in `bin/panel_findings.py`, and both `validate-digest.py` and `plan_merge/panel.py` call
  that definition rather than restating the enums or the predicate. The reviewer cites the
  symbol in each file read with `git show <review_sha>:<path>`.
  verify: inspection
- SC-07 (operator): Forward only. `git diff --name-only <base>..<review_sha>` lists no path under
  another feature's directory and no `runs/` record, and `bin/check_state/run_state.py` (INV-15,
  which never re-validates a historical digest against the live schema) is unchanged in that
  range; legacy panel rows stay legal per SC-05.
  verify: inspection
- SC-08 (reader): At `review_sha`, `harness-code-review/SKILL.md` and the security reviewer's
  `.omp/agents/harness-security-reviewer.md` body state the three questions asked before a
  severity, the rule that a discounted finding is at most `med` — never `must_fix`, never an
  escalation, never the reason for a new test or another fix round — and the adversary exception:
  an adversary-controlled trigger at a real trust boundary (external input, credentials, a gate
  meant to refuse) is not discounted by likelihood.
  verify: inspection
- SC-09 (operator): At `review_sha`, the validator-lead and product-lead agent bodies, and the
  lead instructions in `teams/validate.yaml` and `teams/plan.yaml`, say the lead applies the rule
  at collation before routing, lowers to at most `med` or drops a discounted finding with a
  one-line reason recorded beside it, never raises a severity and never revises `kind`, and
  sends a remedy touching signed text to the operator only when its finding survives that triage;
  in the plan team the product lead lowers a discounted finding rather than dropping it, so its
  panel row exists. Neither agent body still contains `never revise a reader's severity`.
  verify: inspection
- SC-10 (reader): At `review_sha`, each reader step prompt in `teams/plan.yaml` (scope,
  should-not-exist, design) and `teams/validate.yaml` (code, security, ui) requires an exposure
  record per finding; the should-not-exist prompt says to write `unrated` rather than omit it; the
  lead fan-in shape, `references/panel-recording.md` and `templates/plan.yaml` list `exposure`
  among a panel finding's keys.
  verify: inspection
- SC-11 (reader): At `review_sha`, `harness-tdd-enforcement/SKILL.md`,
  `harness-verification-rules/SKILL.md` and the `harness-qa` agent body say tests target the
  code's plausible inputs, that adversarial and malformed-input tests belong only where input
  crosses a trust boundary, and that their absence elsewhere is neither a coverage gap nor a finding.
  verify: inspection
- SC-12 (code maintainer): `git show <review_sha>:.harness/harness/docs/DECISIONS.md` carries a
  new decision stating the rule (the three questions, the exposure enums, the discount predicate,
  the `med` ceiling, the `must_fix` link, the adversary exception, the `unrated` sentinel and the
  forward-only basis), DEC-206's clause that the lead never owns how severe the reader judged a
  finding is replaced by the bounded triage authority, and DEC-123's plan-team carve-out names an
  open row discounted at a non-gating severity; `gen-decisions-index.py --stdout` equals the
  committed index at that pin.
  verify: inspection
- SC-13 (code maintainer): At `review_sha`, `gen-agent-output.py --check` prints
  `agent output: ok` and `tests/unit/test-digest-dev-skill.py` passes, so the six agents' `output:`
  frontmatter carries `exposure` from the generator and every worked yield example validates. qa
  must show both red at the commit that changes the schema, before the agent files are regenerated.
  verify: automated        evidence: unit
- SC-14 (code maintainer): At `review_sha`, `tests/integration/test-validate-digest.py`,
  `test-validate-digest-shadows.py`, `test-panel-findings.py`, `test-plan-merge.py`,
  `test-check-state-records.py`, `test-check-omp-port.py` and `test-plan-team.py` pass. qa must
  show the failing state by running the base commit's copy of `test-plan-merge.py` against the pin,
  where its record-panel fixture findings lack `exposure`.
  verify: automated        evidence: integration
- SC-15 (operator): A discounted finding never fails a review or its team. `validate-digest.py`
  refuses, with an error containing `practicality rule`, a digest whose `severity_max` is `high`
  or `critical` while it carries a discounted finding and no other finding at a gating severity,
  and a code-, security- or ui-reviewer `FAIL` whose every finding is discounted, with `must_fix`
  empty, a non-gating `severity_max` and `code_grade` not `fail`; it accepts that `FAIL` when a
  non-discounted gating finding or a `must_fix` entry is present. In a plan-team product-lead
  digest, a reader `FAIL` whose only open panel row is discounted at `med` is relieved (DEC-123 as
  amended), while the same row with trigger `plausible` still denies relief. qa must show each
  refusal and the relief fail against the base validator first.
  verify: automated        evidence: unit

## Verification gaps

- eval is excluded (DEC-187): whether readers actually answer the three questions honestly, and
  whether fewer contrived findings reach the operator, is not proven by any test. SC-08, SC-09,
  SC-10 and SC-11 rest on inspection of the guidance text; the outcome rests on the operator's
  reading of later features' digests.
- component and ui are unresolved: this feature touches no TypeScript or UI surface, so no SC
  rests on them.

## Constraints

- BLOCKS: DEC-174 — every task changes a gate, its schema or its tests and executes
  main-session-direct (operator constraint 6).
- BLOCKS: DEC-31 — the `must_fix` non-empty or `severity_max` at high or above gate is unchanged;
  the rule only decides which findings may enter it.
- BLOCKS: DEC-237 — `.omp/agents/*.md` `output:` frontmatter is regenerated by
  `gen-agent-output.py` from `digest_schema.PERSONAS`, never hand-edited; declared live properties
  are required.
- AMENDED: DEC-206 — a lead still never invents a reader's finding or raises its severity, but may
  lower to at most `med` or drop a finding the rule discounts, with a one-line reason.
- AMENDED: DEC-123 — worst-wins stands, but the plan-team reader carve-out also relieves a reader
  whose only open panel rows are discounted at a non-gating severity.
- SUPPLIES: DEC-228 (`kind` and record-panel), DEC-230 (one question with a recommendation when a
  reader cannot classify; never the heavier route), DEC-254 (`decisions_affected:` rows).
- Not yet specified items from the grilling, resolved (reasoning in
  `notes/research-practicality-rule.md`): a panel finding carries `exposure` as an optional
  key of the closed panel shape that record-panel requires on every new row; a missing exposure
  is a refusal, and `unrated` is the lead's transcription of an absent rating, never discounted;
  forward only needs no era marker because no gate re-validates a historical digest.

## Out of scope

- Re-grading shipped digests and auditing open backlog issues — the operator ruled forward only.
- Changing the DEC-31 gate itself — the rule decides which findings may enter it.
- #2627 (worktree removal after a squash merge) — worked in another session.

## Approval

status: approved
approved-by: operator
date: 2026-11-28
