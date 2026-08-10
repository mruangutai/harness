# DESIGN — FEAT-11 GraphQL field resolve

**Scope of this document: the operator-facing failure surface only.** There is no graphical surface
in this feature and no prototype is required (see the gate at the end). What is designed here is the
one stderr line a human reads at a terminal when the factory stops — which this project already
treats as a designed artifact, with a grammar centralized in `factory_cli.body`.

## BLUF — the plan's three error branches cannot fire as written

D-02 branches on a null `data.user`, a null `data.user.projectV2` and a null `projectV2.field` in an
exit-0 response. **`gh api graphql` exits 1 on all three.** Verified live, 2026-08-10, this account,
against the `user(login:)`-shaped query D-02 was written for:

| Case | Response | Exit |
|---|---|---|
| owner `github` (an org) | `data.user: null` + `errors[].type: NOT_FOUND` | **1** |
| `mruangutai` board 9999 | `projectV2: null` + `errors[].type: NOT_FOUND` | **1** |
| board 3 field `NoSuchField` | `field: null` + `errors[].type: NOT_FOUND` | **1** |

`run_gh` (`factory_gh.py:79`) raises `GhError` on any non-zero exit, so it raises **before** any
branch inspects the envelope. Two consequences, both requirement failures:

- **REQ-03 produces the outcome it forbids.** The graphql argv carries `-f owner=…`, not `--owner`,
  so `_value_from_argv` matches nothing and falls back to `" ".join(argv[:2])`. The operator reads:
  `factory: decompose: gh api graphql failed: api graphql — gh: Could not resolve to a User with the login of 'github'.`
  That is "a GraphQL null surfacing as a confusing message", verbatim.
- **REQ-02's field-not-found path breaks live.** `_validate_stations`
  (`factory_decompose.py:255-268`) reaches two errors: the field-missing one it propagates from
  `project_field_options`, and the option-missing one it builds itself. Only the **field** one is
  affected — a field typo now yields `Could not resolve to a Unions::ProjectV2FieldConfiguration`.
  The `Redy` case is an *option* typo (`test-factory-decompose.py:1035`), resolved in Python after a
  successful exit-0 read, and is unaffected.

SC-04/05/06/07 still pass, because their fixtures return **exit 0** with a partial envelope for
these three states, which real `gh` does not produce for them. Green suite, unmet requirements.
(An exit-0 partial envelope is not fiction in general — the wider probe found two states that
genuinely arrive that way. See Contract 2.) See Q1.

## Contract 1 — the grammar, and the rule D-02 breaks

`factory_cli.body`: `{what}: {value} — {next_step}`, rendered as
`factory: {tool}: {what}: {value} — {next_step}`.

**Slot 3 is what the operator does next, never the cause.** Existing sites hold to it: "install gh,
or point FACTORY_GH at its path", "widen --limit or narrow with --query", "check the board number".
D-02 branch (a) puts `"organization-owned boards are not supported"` — a cause — in the action slot.

## Contract 2 — four owner/board states, not two

`user(login:)` returns the *same* NOT_FOUND for an organization and for a misspelled login. D-02
exists to stop a mistyped board number reading as "org unsupported"; the same collapse it forbids
then happens one level up with a mistyped **owner**.

`repositoryOwner(login:)` discriminates all of them. It is one query, still cost 1, and
`ProjectV2Owner` is the interface both concrete types satisfy, so the `projectV2(number:)` selection
is unchanged. That recommendation stands.

**Correction, 2026-08-10.** This document previously asserted that `repositoryOwner` discriminates
all three states at exit 0, with no errors array. <!-- ok-stale --> That was measured on
`repositoryOwner(login:)` **alone**, and does not survive the combined document
(`notes/research-FEAT-11-combined-query-probe.md`, six cases, same account, same day). The combined
query splits across **two** exit codes: unknown-owner stays exit 0, but the organization case —
REQ-03's own branch — came back at **exit 1 with an `errors` array**, because `projectV2(number:)`
fails underneath the owner selection. `__typename` is readable in that exit-1 envelope too, so the
org branch still fires before `projectV2` is inspected; only the transport changed, not the
discrimination.

The required message set, `what` / `value` / `next_step`, with the measured transport of each state:

| State | Transport | what | value | next_step |
|---|---|---|---|---|
| `repositoryOwner` null | **exit 0**, no `errors` key | `project owner not found` | `<owner>` | `check the owner login` |
| `__typename` = `Organization` | **exit 1** + `errors[]` in the probed case † | `organization-owned board not supported` | `<owner>` | `run against a user-owned board` |
| `projectV2` null | **exit 1** + `errors[]` | `project not found` | `<owner> project <number>` | `check the board number` |
| `field` null, or `field` `{}` | `null` → **exit 1** + `errors[]`; `{}` → **exit 0** | `project field not found` | `<field>` | `field-list for <owner> project <number> does not offer it` |
| option not offered | resolved in Python after exit 0 | `project field option not found` | `<option>` | `field <field> on <owner> project <number> does not offer it` |

The five message rows are unchanged, byte for byte. Only the transport column is new.

† No organization owning an accessible board was reachable from this account, so the org case was
measured against `github` / board 1: the exit 1 came from `projectV2(number:)` failing beneath the
owner selection, and an org that *does* own a reachable board would return exit 0. That is not
load-bearing — `__typename` is readable in both envelopes and the org branch is read before
`projectV2`, so the message fires either way. `BRIEF.md:137` records the same gap.

**The not-single-select case folds into `project field not found` — agreed, no sixth row.** `Title`
is a real field that the inline fragment does not match, so `field` is `{}` at exit 0. The operator's
next action is identical to a misspelled field name: read the field list, pick a single-select field.
A distinct row would buy precision they cannot act on, and its wording could not reuse the frozen
string anyway. The imprecision is **accepted, not resolved**, in the same form as the frozen
`field-list` wording: the field does exist, and the message says it was not found. The load-bearing
consequence is that the implementation must test **both** `None` and `{}` — `{} is None` is `False`,
so `if field is None` alone passes and then sends `--field-id None` to `item-edit`.

The last two are **frozen byte-identical** to `factory_gh.py:206-210` and `:251-256` (REQ-02). The
frozen wording names `field-list`, a subcommand the tree will no longer invoke — **keep it anyway,
and do not "tidy" it later**: it reads as an instruction to a human who can still type
`gh project field-list` themselves, which is exactly what the action slot is for.

## Contract 3 — no failure in this path may be valued `api graphql`

Every `GhError` the resolver raises names the operator's own inputs — owner, board number, field or
option. The `_value_from_argv` fallback is not acceptable here for **any** failure in this path,
including a genuine transport or auth failure: `value: api graphql` tells the operator nothing they
can act on.

## The mechanism half is engineering's, not this document's

The requirement, stated without an implementation: **the resolver must distinguish "gh failed" from
"GitHub returned a diagnosable envelope."** The membership test is the envelope, **not the exit
code**: stdout that parses to a mapping containing a `data` key is diagnosable and must be mapped to
the table above, whatever the exit code and whether or not an `errors` key is present. Its
complement — stdout that does not parse to such a mapping — is the transport or auth failure. How
that is achieved belongs to `harness-backend-dev`.

## Open questions

- **Q1 — resolved, and its own wording corrected.** D-02 was rewritten and SC-04/05/06 reshaped.
  Q1 originally said every fixture must carry exit 1 plus the partial envelope; <!-- ok-stale -->
  that holds for **three** of the five states, not all. The measured split is three exit-1 fixtures
  (org as probed †, board-not-found, field-null) and **two exit-0** fixtures (unknown owner with no
  `errors` key; not-single-select with `field: {}`). A fixture set that is uniformly exit 1 certifies a
  transport that does not exist just as surely as one that is uniformly exit 0.
- **Q2 — resolved.** REQ-03 now names both reasons (`BRIEF.md:30-32`) and SC-11 covers the
  owner-not-found state with the exit-0 transport. Verified in `BRIEF.md`, not inferred.

## Prototype gate

**`needs_prototype: false`.** No screen, control or flow a person operates — a transport swap inside
two functions of a CLI library that has no command line of its own. The whole human surface is one
stderr line whose grammar is already fixed; a prototype would show nothing the message table above
does not pin exactly. The wording is *designed here*, not prototyped.
