# Plan-panel c4 — scope reader — FEAT-55-issue-types-created-work

## BLUF
**All five rulings HOLD in plan.yaml as written, independently re-verified against the file (not
against pm's or the goal-check's account).** R1 — the ruling this cycle exists to press hardest on —
genuinely closes PF-df3caaeb/F1: the pre-seeded remnants in T-03 case F, T-05 case G and T-07 case I
are real backfill-set members, and the zero-`updateIssue` assertions can now actually redden against
a backfill-before-refusal-check implementation. One new finding, `med`: none of the three refusal
cases (T-03 F, T-05 G, T-07 I) exercises the scenario where the required-set's *backfill*
contribution is the ONLY source of a missing type — an implementation that silently drops backfill
candidates from the missing-types computation (while still ordering "backfill after refusal"
correctly) passes every case in this plan.

## Five discharged fixes — HOLD / DID-NOT-LAND, one line each
- **R1 (T-03 case F / T-05 case G / T-07 case I pre-seeded remnants): HOLDS.** See detailed
  re-derivation below.
- **R2 (T-06 §5 / D-13 use `harness_merge.locked_update`, not `json.dump`): HOLDS.** `D-13 choice`
  reads "written through the established locked atomic writer, harness_merge.locked_update"; T-06 §5
  reads "WRITE IT THROUGH THE ESTABLISHED LOCKED ATOMIC WRITER, NEVER A PLAIN TRUNCATING DUMP... Do
  not open the receipt with open(path, "w") and json.dump into it". Independently confirmed
  `harness_merge.locked_update` is a real primitive (`.claude/skills/harness/bin/harness_merge.py:121`)
  already used by `gh-sync.py`'s own `save_recorded` via `feature_json_write.write_feature_json`
  (`gh-sync.py:806-809`), so the claimed reuse is grounded, not aspirational.
- **R3 (D-12 four canonical keys; false "EXISTING key" claim corrected): HOLDS.** `D-12 choice`:
  "It has exactly four legal keys... Bug, Feature, Task, and the literal key parent" and "a NET-NEW
  key inside the existing github block and not an existing one". T-01 assertion 5, T-02's
  `LEGAL_OVERRIDE_KEYS = ("Bug", "Feature", "Task", "parent")`, T-03 case E and T-07 case D all use
  only the four canonical keys; no surviving `change_type`- or nature-keyed override found anywhere
  in `plan.yaml` outside the two deliberate negative-test literals (`{"bugfix": "Defect"}` as an
  assertion that a change_type key is ignored).
- **R4 (T-10 §1 exempts `--create-in` from the configured-repo gate; BRIEF SC-10 edited): HOLDS.**
  T-10 §1: "SKIP ONLY WHEN NO --create-in TARGET WAS SUPPLIED... THE EXPLICIT OPT-IN IS EXEMPT FROM
  THE CONFIGURED-REPOSITORY AVAILABILITY GATE". BRIEF SC-10: "Under the explicit create opt-in the
  configured-repository availability gate does not apply, because the repository reported on is the
  one the operator named." Both read consistently.
- **R5 (REQ-10 on T-07 / T-08 traces): HOLDS.** T-07 `traces: [REQ-01, REQ-03, REQ-05, REQ-06,
  REQ-07, REQ-08, REQ-10]`; T-08 `traces: [REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08,
  REQ-10]`.

## R1 — the pressed ruling — full re-derivation (legs a and b, all three cases)

**T-03 case F.** FAKE_TYPES=partial declares only Bug and Feature (Task absent). Fixture: 4 tasks
(bugfix/config/logic/feature) + parent. Pre-seed: feature.json already carries the bugfix task's
number `501` in `github.issues` and `github.typed[<tid>] = "created"`.
- (a) holds: the bugfix task's type is Bug (D-01), which the `partial` fake table declares
  ("`partial`, echo a nodes array declaring only Bug and Feature"). T-04 §4's stated selection rule
  is literally "every already-recorded key whose recorded provenance value is the string `created`"
  — `501`'s provenance is exactly `"created"`, so it is a genuine member.
- (b) holds: config/logic/feature tasks are unrecorded and all three resolve to Task (D-18) via
  `type_for_change_type`, which `partial` does not declare — the correct implementation refuses
  before any create or backfill. A backfill-before-refusal-check implementation instead applies the
  bugfix remnant's Bug type first (declared, succeeds) — emitting one `updateIssue` argv carrying a
  node id derived from `501` — before it (still) refuses on the missing Task types for the other
  three tasks. The "ZERO argv containing updateIssue... including, named separately, zero updateIssue
  argv carrying a node id derived from 501" clause reddens against that implementation and is
  satisfied only by check-then-backfill.

**T-05 case G** (backlog route — no `"created"` string vocabulary; `typed: false` beside a recorded
number is this route's created-but-not-yet-typed provenance, per T-06 §5's own rerun rule "when
typed is not true, apply_issue_type"). Pre-seed: `backlog-issues.json` records `"bug:a defect"` →
`{"number": 601, "typed": false}`.
- (a) holds: T-06 §3 computes `required` over "the WHOLE item list" via `type_for_nature`, which
  includes the bug item regardless of its recorded state; its type Bug is declared by `partial`
  (Bug, Feature only); the chore item resolves to Task, undeclared, forcing refusal. `601`/`typed:
  false` is exactly the shape T-06 §5's per-item "already recorded... when typed is not true, apply"
  rule would pick up on a rerun.
- (b) holds: a backfill-before-refusal-check implementation processing items in order would reach
  the already-recorded bug item first and apply its (declared) type — emitting an `updateIssue` argv
  against `601` — before any check of the chore item's undeclared Task forces a refusal. The
  "ZERO argv containing updateIssue... zero updateIssue argv carrying a node id derived from 601"
  clause reddens against that ordering.

**T-07 case I** (factory route). Pre-seed: `factory.yaml` records the bugfix task's number `701`
with `factory["typed"][tid] = "created"`.
- (a) and (b) hold by the same structure as T-03 case F: Bug (bugfix task's type) is declared by
  `partial`; config/feature tasks resolve to Task, undeclared, forcing refusal; a
  backfill-before-refusal-check implementation would apply `701`'s Bug type first, producing the
  `updateIssue` argv the "ZERO... including, named separately, zero updateIssue argv carrying the
  node id derived from 701" clause exists to catch.

**Conclusion: R1 fix LANDED on all three files.** This closes the exact gap the c3 predecessor
review (`notes/review-harness-code-reviewer-planpanel-c3.md`) found unsound ("no implementation,
buggy or correct, can produce an updateIssue call in any of these three cases" against the c5
fresh-fixture edit) — the pre-seeded, declared-type remnant is what gives the assertion a
distinguishing implementation to fail against.

## New finding (med) — the required-set's backfill contribution is never the sole trigger for a refusal

**Content anchors:** T-04 §4 ("THE REQUIRED SET IS NOT ONLY WHAT WILL BE CREATED: add the type of
every already-recorded key that section 6 will backfill"), T-08 §6 ("THE REQUIRED SET ALSO COVERS
THE BACKFILL"), T-06 §3 ("compute gh_issue_types.missing_types(required, declared) over the WHOLE
item list").

**Why:** In all three refusal cases (T-03 F, T-05 G, T-07 I), the *unrecorded, to-be-created* tasks
already need a type the fake does not declare (Task, via config/logic/feature or the chore item), so
refusal fires whether or not the backfill remnant's type is folded into `required` at all. No case
anywhere isolates the clause "add the type of every already-recorded 'created' key" as the sole
source of a missing type — e.g. a rerun where every task and the parent are already recorded
(zero new creates) and the only unresolved item is a backfill remnant whose type the repository does
not (or no longer) declares. A concrete implementation that silently omits backfill candidates from
the `missing_types` computation — while still correctly gating "backfill only after the refusal
check passes" (satisfying every assertion R1 verified above) — computes an empty `required` set on
such a rerun, never refuses, and proceeds straight into the backfill loop. There, `apply_issue_type`
looks up `declared[type_name]`, which is absent, producing an uncaught `KeyError` instead of
`refusal_text`'s clean, actionable message — exactly the ungraceful failure mode REQ-07 exists to
prevent ("the refusal names the missing type and the configuration change that repairs it"). This
implementation passes every currently-specified case in T-03, T-05 and T-07.

## Topology / traceability / SC-decidability hunt — clean
- `depends_on` is a valid topological order: T-01→T-02→{T-03,T-05,T-07}→{T-04,T-06(+T-05),T-08},
  T-09(∅), {T-02,T-09}→T-10, T-11(∅)→T-12. No forward reference, no cycle.
- Every `REQ-01`..`REQ-11` is traced by at least one task; every task's `traces:` cites an existing
  REQ. No orphan REQ id, no dangling reference.
- Every `SC-01`..`SC-12`'s `verify:` method is produced by an identifiable task: SC-04/SC-11 are
  `inspection` (reviewer-graded, correctly not task-owned); SC-10 is `issue_types_live`, produced by
  T-09+T-10; the rest (`automated`/`integration`/`unit`) each map to a named case in T-01, T-03,
  T-05, T-07 or their implementation counterparts. No SC whose verify method nothing produces.
- No `verify:` block asserts presence of anything a predecessor task deletes or renames; the
  compatibility paths (`type_label`, `CHORE_TYPES`) are explicitly preserved by T-04/T-06/T-08, not
  removed.

## Still-live, previously-disposed findings — re-measured, unchanged, not re-raised as new
Re-checked against current content and found byte-identical in substance to the c3 predecessor's
corroborations and the c6/c7 repair notes' own LEAVE roll-calls (`PF-56a2ce7a`, `PF-45294813`,
`PF-e27f1c30`, `PF-0c12a033`, `PF-9a71cb9a`, `PF-62b2b8ae`, `PF-e74a2da8`, `PF-1280cd8f` residue (a)
at T-10 §6). None is newly discovered here; all remain queued at their existing dispositions
(`batched_to_signature_review` / `awaiting_user`), and I did not re-verify each at the same depth
this cycle since none is this cycle's assigned focus.

## Explicit one-line verdicts
1. R1 (T-03 F / T-05 G / T-07 I pre-seeded remnants): **HOLDS — both legs verified for all three
   files.**
2. R2 (locked atomic writer): **HOLDS.**
3. R3 (four canonical override keys): **HOLDS.**
4. R4 (opt-in exempt from configured-repo gate): **HOLDS.**
5. R5 (REQ-10 traces): **HOLDS.**
6. New: required-set-backfill-only refusal path is untested anywhere in the plan — **med**, not
   gating alone but worth folding into a case (e.g. an all-recorded rerun whose sole backfill
   remnant's type the fake no longer declares) before signature.
