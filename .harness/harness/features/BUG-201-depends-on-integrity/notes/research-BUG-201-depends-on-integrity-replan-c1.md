# Replan c1 — BUG-201-depends-on-integrity

**BLUF: the plan is revised and internally consistent — REQ-05 and two tasks (T-05 test-first, T-06
production) deliver the operator's Q-A ruling, D-05 reconciles it with DEC-138 per site, and six
faulty criteria/task-design findings are repaired. One acceptance item could not be delivered:
`lanes.rows` has NO write route — `plan-merge.py apply` exits 7 CONFLICT on the `lanes` key and
`amend` accepts only `tasks`/`decisions`, both observed today. The lane resolution is recorded in
D-03's `because` instead, so nothing is unrecorded, but the `lanes:` block itself is unchanged and
that needs the tier above.** The validation rule is untouched: still missing-ids-only, no
self-dependency check, no cycles, no ordering. `approval.status: pending`, `## Approval` pending,
`panel:` untouched (3 readers, 10 findings).

## Per finding

- **PF-d26198866e2756a2288bf70a4226659b (Q-A) — DELIVERED, not merely repaired.** REQ-05 in
  `BRIEF.md` names the three swallow sites; SC-08 (factory_claim, unit) and SC-09 (gh-sync, both
  sites, integration) pin the observed ids and each carry a paired correct-plan case; T-05 (tests,
  `depends_on: [T-03]`) then T-06 (production, `depends_on: [T-05]`) deliver it; D-05 records the
  posture.
- **PF-7beea12ebdabef0e2f946b763f7be080 — REPAIRED.** SC-03 is now the invariant (every plan.yaml
  found under `.harness/harness/features/` loads with today's verdict, zero fail, zero dangling)
  with 67 as a FLOOR plus provenance (67 committed at `af859ee8` in the main checkout; 68 in this
  worktree, this plan.yaml included). No equality anywhere; it now agrees with T-04's own "AT LEAST
  67".
- **PF-6dda61c31b87efdc801848fb78af21fa — REPAIRED.** SC-02 now pins exactly what T-02 pins: exit
  status EXACTLY 5, `ILLEGAL PLAN` + the missing id in combined output, sha256 unchanged, plus the
  paired allow at exit 0 with the new task present. Exit 9 explicitly excluded.
- **PF-cc2bcfa945e44f6616257a66db45325d — REPAIRED.** SC-05 now requires the pre-rule run to import
  and reach its cases, the paired-allow cases to PASS in that same run, and the FAIL lines to be
  exactly the dangling cases. An `ImportError` or fixture error cannot green it.
- **PF-e9eff4c667f72ba3c65f06fecbc161d0 — REPAIRED.** T-03's `verify:` amended from four suites to
  eight (adds `test-factory-claim.py`, `test-factory-claim-mutation.py`, `test-gh-sync.py`,
  `test-check-plan-routes.py`); T-06's `verify:` runs the same eight. REQ-04's second half is now
  bound by SC-06 (the three `unit` suites) and SC-07 (the four `integration` suites) — split by kind
  so each criterion declares exactly one `evidence:`.
- **PF-3116cd3b98020bc5b450be865f3754bb — REPAIRED.** T-01 case 6 rewritten as three
  sub-assertions on MIXED id types (int ids with a string `depends_on`, and the mirror, both
  ACCEPTED; int ids with `[3]` REJECTED) and the intent now NAMES the variant it catches:
  coercion on one side only, which reddens both accept halves. The old same-type case, green under
  that variant, is gone.
- **PF-092cbd0b966447a02c1a6c5188f25c27 (info) — REPAIRED.** T-03's ACCEPTED sentence is now an
  explicit "NON-NORMATIVE NOTE, describing the null action of the rule above and NOT a behaviour to
  implement", with "write no branch, no special case and no test for it".
- **PF-4e86832239a56c223544656261a83cd7 — REPAIRED, measured not asked.** D-03's `because` now
  cites the DECISIONS.md paragraph by its anchor text ("The enforcement layer, enumerated:"),
  states that none of the five surfaces this plan touches appears in it, and records the
  `check-domain.sh --resolve` result putting `harness_yaml.py`, `factory_claim.py` and `gh-sync.py`
  in the same lane (harness-backend-dev, harness-dev-ops).
- **PF-4f91801bd1344ae2e8d1818b26cbd518 (info) — NO CHANGE, deliberately.** The exit-2 stop at
  `check-plan-routes.py` already satisfies "before it can be consumed"; nothing in the artifacts
  needed to move.
- **PF-e159de1959db1573573a45c1ed92a175 (info) — NO CHANGE, deliberately.** The non-list
  `depends_on` rejection stays recorded in T-01 case 5 and T-03's behaviour list, so the one
  widening remains declared and covered knowingly by the signature.

## The decision the signature carries: D-05

Per site, and why (DECISIONS.md DEC-138, plus the house pattern at `gh-sync.py:1160-1168`):
`_projected_for` **refuses** — `refuse(...)`, exit 2, one actionable line, no traceback — because its
own sibling branch already took that posture for a vocabulary miss at the same function, recording
that DEC-138's never-gates is about not blocking a flow, not dying in it, and DEC-138's named case
is `gh` absent/unauthenticated, not a locally malformed signed artifact. `_status_plan_doc`
**prints one line and returns None unchanged**, because `cmd_status`'s two guarded transitions
already decline correctly and non-gatingly (`gh-sync.py:1306-1307`, `:1318-1319`) — adding an exit
there would convert a designed decline into a gate. `factory_claim` **keeps returning no plan** but
carries the validator's message into a new `bad_plan` blocker reason, because it polls many
candidates and raising would abort every later one.

## Artifact changes

`BRIEF.md`: +REQ-05; +DEC-138 constraint bullet; SC-02/SC-03/SC-05 rewritten; +SC-06, SC-07, SC-08,
SC-09. `## Approval` untouched.

`plan.yaml`, in order, every write through `plan-merge.py`:
1. `apply --proposal` → `ADDED D-05`, `ADDED T-05`, `ADDED T-06` (exit 0)
2. `apply --proposal` (lanes rows) → `CONFLICT: top-level key 'lanes' carries two different
   values.` exit 7, file untouched
3. `amend --key lanes --id rows --field surface --show` → "--key lanes is not amendable" exit 2
4. `amend --key tasks --id T-03 --field verify` (sha `9690164…`) → AMENDED
5. `amend --key tasks --id T-01 --field intent` (sha `2d905bd…`) → AMENDED
6. `amend --key tasks --id T-03 --field intent` (sha `3f42828…`) → AMENDED
7. `amend --key decisions --id D-03 --field because` (sha `d8d9415…`) → AMENDED

Load proof, from the worktree: `env -u HARNESS_AGENT_TYPE python3
.claude/skills/harness/bin/check-plan-routes.py <this plan.yaml>` → `OK T-01`…`OK T-06`,
`0 violation(s) across 1 plan(s)`, exit 0. DAG re-read from the loaded doc:
T-01 `[]`, T-02 `[]`, T-03 `[T-01,T-02]`, T-04 `[T-03]`, T-05 `[T-03]`, T-06 `[T-05]` — topological,
no dangling edge. Every `traces:` names an existing REQ; REQ-01..REQ-05 each traced.

## Open question

- **Q1 (blocking for one acceptance item):** `plan.yaml`'s `lanes` key has no write verb.
  `factory_claim.py` and `gh-sync.py` therefore do not appear in `lanes.rows` even though T-06
  writes them. Either extend `plan-merge.py` (a dev-ops task: `lanes` as a union key on
  `rows.surface`, or a `set-lanes` verb) or accept D-03's `because` as the recorded lane fact for
  this feature.
