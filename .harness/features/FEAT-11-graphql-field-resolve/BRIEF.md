# BRIEF — FEAT-11 GraphQL field resolve

## Problem

The factory runs out of GitHub GraphQL budget and stops. On 2026-08-10, during the FEAT-10 live
verification run, `gh api rate_limit` showed graphql `used 4987/5000, remaining 13` while REST core
was untouched — the run halted with `exit 2` (issue #211). The failure is loud, not silent, and it
clears at the next hourly reset, so nothing is corrupted; what it costs is throughput. Every station
move a factory tool makes pays **104 points** for two board-shaped reads before a **1-point** write,
and `project_field_set` is the only call that runs inside a loop (`factory_decompose.py:444-458`), so
a four-task feature pays four rounds of it. The measured cause is `gh project field-list`, at 102
points regardless of `--limit` — the cost is in the query shape `gh` sends, not the data returned.

## Goal

Replace the two uncached board reads inside `project_field_set` and `project_field_options` with a
single GraphQL query that returns the project node id, the field id and every option id and name at
**cost 1**. A station move then costs 2 points instead of 104, and `factory_decompose` on a four-task
feature costs single-digit points instead of roughly 500. Nothing about the factory's observable
behaviour changes: the station-name and option-name error paths behave exactly as they do today,
same error type and same named value. What `_validate_stations` depends on is that a missing field
still **raises** — it propagates that error without reading its text.

## Requirements

- REQ-01: Moving an issue to a station costs a small, bounded number of GraphQL points, so a
  multi-task `factory_decompose` no longer exhausts the hourly budget.
- REQ-02: A field that the board does not offer, and an option that the field does not offer, fail
  exactly as they do today — same error type, same named value in the message.
- REQ-03: An owner that cannot be used is refused with an error that names which of the two reasons
  applies — the login resolves to nothing, or it resolves to an organization — rather than
  surfacing a GraphQL null as a confusing message. The two are never reported as each other.
- REQ-04: A resolution that fails never falls back to a substitute value. It raises, and no write is
  attempted.
- REQ-05: Every existing caller of the two functions keeps working without being edited.

## Success Criteria

- SC-01: A real four-task `factory_decompose` against board 6 consumes single-digit GraphQL points
  in total, and a single station move consumes 2 (against 104 today), measured by differencing
  `gh api rate_limit --jq .resources.graphql.used` across the run.
  verify: uat
  **Who runs it, and when:** the **operator**, as a named pre-ship step, before this feature is
  marked shipped. No agent in this flow may run it — the measurement writes to board 6, and writing
  to board 6 is outside every agent's authorization here. Until the operator runs it, SC-01 is
  `not_met`, and that is the expected state at the end of the build.
- SC-02: Resolving a field makes exactly one `gh api graphql` call and **zero** `gh project
  field-list` and `gh project view` calls, and neither invocation survives anywhere in
  `factory_gh.py`. (The literal words "field-list" still appear inside the error message text, which
  REQ-02 freezes — the criterion is about the *call*, not the token.)
  verify: automated      evidence: unit
- SC-03: The GraphQL query asks for **one named field and fans out nowhere** — the emitted query
  text selects a single field by name, contains no plural field-connection selection, and contains
  **no connection argument at all** (`first:`/`last:`). The no-connection-argument clause is the
  load-bearing one: a selection set with no connection argument cannot fan out, so this tests the
  query's *shape* rather than the spelling of one token. It is the guard against the over-scoped
  version of the same fix, which would resolve the same ids, pass every behavioural assertion, and
  cost the same 102 points.
  verify: automated      evidence: unit
- SC-04: A field the board does not offer raises `GhError` naming the field; an option the field does
  not offer raises `GhError` naming the option. Both messages still name the field/option value, and
  `_validate_stations` is therefore unaffected: it propagates `project_field_options`' `GhError`
  without reading its text (`factory_decompose.py:255-268`), so what it depends on is that a missing
  field still raises. The `Redy` case is an option typo whose operator-facing message
  `_validate_stations` builds itself (`factory_decompose.py:264-268`), and it never reaches
  `factory_gh` at all.
  verify: automated      evidence: unit
- SC-05: A board owner that resolves to an organization is refused with an error naming that reason,
  and the refusal fires on **either** transport envelope — proven by unit tests against **two**
  stubbed org-typed GraphQL responses, both required:
  (a) a **non-zero exit** whose stdout carries `__typename: "Organization"` with `projectV2` null
  alongside an `errors` array — this envelope is *measured* (probe case 4, an org whose board number
  does not exist); and
  (b) an **exit 0** response carrying `__typename: "Organization"` with `projectV2` **populated**
  (project id, field id, options) and **no `errors` key** — the envelope an org that *does* own a
  reachable board returns. This one is **derived, not measured**: no such board is reachable from
  this account (`notes/research-FEAT-11-combined-query-probe.md:97`), and it is `DESIGN.md:80-84`'s
  reasoning that fixes its shape.
  Fixture (b) is the discriminating half: against it, an implementation that reads `__typename` only
  inside `except GhError` returns *successfully* and writes to an org board, which is exactly the
  dead-branch defect D-03's single diagnosis walk exists to prevent. Fixture (a) alone cannot catch
  it. It cannot be exercised live — every board in play is user-owned (`gh api users/mruangutai --jq
  .type` returns `User`), which is why org support is out of scope.
  verify: automated      evidence: unit
- SC-06: A valid user owner with a board number that does not exist raises an error distinct from the
  organization refusal, so a mistyped board number is never reported as "org boards unsupported".
  Its fixture likewise reproduces the measured transport — non-zero exit, partial envelope.
  verify: automated      evidence: unit
- SC-07: A failed resolution raises and makes **zero** `gh project item-edit` calls — it never
  silently reuses the bare board number as `--project-id`. This is the D-02 "never falls back"
  property, carried into its new form.
  verify: automated      evidence: unit
- SC-08: `project_field_options(owner, number, field)` and `project_field_set(owner, number,
  item_id, field, option)` keep their exact signatures and return shapes, proven by
  `test-factory-decompose.py`, `test-factory-claim.py` and `test-factory-land.py` passing **without
  being edited** — all three patch at the `factory_gh` module boundary.
  verify: automated      evidence: unit
- SC-09: The end-to-end integration suite (`test-factory-integration.py`, which drives the real
  `factory_decompose` and `factory_claim` through a whole-CLI fake `gh`) passes **while its fake
  answers no `gh project field-list` and no `gh project view` call at all** — both handlers deleted,
  not merely unused. Deletion is the load-bearing half: with them gone, any surviving old-shape
  invocation hits the fake's unhandled-argv failure and reddens the suite; left in, a half-converted
  implementation passes silently. `harness.json` `test_kinds.integration` has a real `cmd`
  (`run-unit-tests.sh --kind integration`) and its `detect` names this file explicitly, so the
  evidence kind exists.
  verify: automated      evidence: integration
- SC-10: **Every** failure raised out of the resolve path names the operator's own input. Two
  falsifiable clauses, both asserted on the rendered exception message, because `GhError` keeps no
  `value` attribute (`factory_gh.py:41-44`): the message contains bare `<owner>`, `<owner> project
  <number>`, the field name or the option name — bare `<owner>` is the value for two frozen Contract
  2 rows (`project owner not found`, `organization-owned board not supported`), so omitting it would
  pass an implementation that broke both; and the message **never** contains
  the string `api graphql`. The negative clause covers the case nobody designed for — a genuine
  transport or auth failure, where today's generic fallback would name the subcommand and tell the
  operator nothing they can act on.
  verify: automated      evidence: unit
- SC-11: An owner login that resolves to nothing is refused with an error distinct from **both** the
  organization refusal and the board-not-found error, so a misspelled owner is never reported as an
  unsupported org. Its fixture reproduces the measured transport for this case, which is **exit 0
  with `data.repositoryOwner: null` and no `errors` key** — the one failure state `gh` does not
  report as a failure at all.
  verify: automated      evidence: unit
- SC-12: A field that exists on the board but is **not single-select** raises the same
  field-not-found error as an absent field. Its fixture carries the measured shape — exit 0, with
  `field` an **empty object**, not `null`. Without it, an implementation testing only `field is
  None` passes every other criterion here and then sends `--field-id None` to `item-edit`.
  verify: automated      evidence: unit

## Verification gaps

- **No test kind measures GraphQL cost.** `harness.json` `test_kinds` has no runner that can observe
  a rate-limit delta, and stub assertions prove only that the call shape changed, not that the cost
  fell. Cost is the entire point of this feature, so SC-01 rests on an operator-run live
  measurement (`uat`) and nothing else carries it. SC-02 and SC-03 are the automated proxies: they
  prove the expensive call is gone and that the cheap one was not written back to the expensive
  shape. They do **not** prove the number.
- **The organization path is never exercised against a real org, and one of its two fixtures is
  constructed rather than observed.** SC-05 rests entirely on stubs. Its exit-1 fixture was measured,
  but against an org whose board number does not exist — an artifact of no organization owning a
  board this account can read. Its exit-0 fixture, the one that catches the dead-branch bug, was
  **never observed at all**: its shape is derived from `DESIGN.md:80-84`'s reasoning that an org
  owning a reachable board returns exit 0 with `projectV2` populated. What the measurement does
  establish is that `__typename` is readable in the envelope at exit 1, before `projectV2` is
  reached. That the same is true at exit 0 is asserted, not observed. If org boards are ever brought
  into scope, neither stub is evidence.
- **The genuine transport/auth failure is stub-only.** SC-10's negative clause cannot be provoked
  without breaking authentication, so its fixture is a stub of the complement of every measured
  case. The rule it encodes — stdout that does not parse to a mapping carrying `data` is not
  diagnosable — is therefore asserted, not observed.

## Constraints

- `gh project item-list` (`project_items`) stays as it is — 31 points, once per invocation, never in
  a loop. Out of scope.
- The write stays on `gh project item-edit`. Measured at 1 point; `updateProjectV2ItemFieldValue`
  buys nothing.
- **No caching.** With the read at 1 and the write at 1, a station move is 2 points. Caching was the
  earlier recommendation and the measurements retired it.
- **No fallback to `gh project field-list`.** Keeping the 102-point path in the tree preserves the
  thing being removed — the same reasoning DEC-171 applied to the hand-rolled YAML parser.
- Organization-owned boards stay out of scope: refuse loudly, do not support.
- No new repo and no new board. Board 6 is the throwaway that already exists and is already owed
  cleanup.

## Scope note

This is genuinely small: **one task**, three files, all on the same granted surface. The change is a
transport swap inside two functions whose public signatures are frozen by three other test files.
The bulk of the work is the regression rewrite of the existing stub tests — both the unit stubs in
`test-factory-gh.py` and the whole-CLI fake in `test-factory-integration.py` — not new behaviour.

## Backlog

Closes issue #211 (`mruangutai/harness`, P0), recorded as `absorbs: 211` on T-01.

## Approval
status: approved
approved_by: operator
date: 2026-08-10
