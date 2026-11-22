# FEAT-2297 T-09 — Kaya migration UAT receipt (SC-08)

## Publication

| Fact | Value |
|---|---|
| Repository | `mruangutai/kaya` |
| Source `main` SHA (read fresh, re-checked before branching) | `6303f9f8a60127df461c20bb45d4531c5aaf8af9` |
| Source blob `.harness/harness.json` | `d96b4484b03d1a161e8e61c11012c3ebc539fbff` (schema_version 2) |
| Branch (fresh runtime id) | `harness/json-schema-v3-20261122T221236Z-264fd6` |
| Branch commit (contents API, blob compare-and-swap) | `d11ba51d1e4032082611c8a70cf1c2ab40116905` |
| Remote blob written | `a3992874936d7fc934253107c874384b4204815b` (equals `git hash-object` of the local payload) |
| Payload | `notes/kaya-config-v3.json`, sha256 `b7e825e5226f54f9d653e9be81b364282234d3a88b50f295e57f81e11a4e6b0d` |
| PR | https://github.com/mruangutai/kaya/pull/29 |

**Production.** `upgrade-config.py . --config-only --templates <harness>/.agents/skills/harness/templates`
on a temporary copy of the remote file, then `artifact_accessors.load_harness_json` on the
result: valid, `schema_version` 3, every kind `unresolved`, `github.repo` `mruangutai/kaya`, board 9.

**Proposed diff** (template prose notes omitted):

- added `decision_dispositions_era_start` = `null`
- changed `schema_version`: `2` → `3`
- added `test_kinds.component.status` = `"unresolved"`
- added `test_kinds.eval.status` = `"unresolved"`
- added `test_kinds.functional.status` = `"unresolved"`
- added `test_kinds.integration.status` = `"unresolved"`
- added `test_kinds.typecheck.classifies_tests` = `false`
- added `test_kinds.typecheck.status` = `"unresolved"`
- added `test_kinds.ui.status` = `"unresolved"`
- added `test_kinds.unit.status` = `"unresolved"`
- plus 15 template prose notes (`_…` keys)

No direct push to `main`. Branch-protection and ruleset APIs return 403, and earlier PR 15 has
no recorded reviews; neither fact grants merge authority.

## Review and authorization

**Authorized: squash-merge**, given 2026-11-22 by the plan's advisor (`fable-advisor`, agent
`AmendmentRuling`, request #5; transcript `history://AmendmentRuling`). It acted under the operator's
standing instruction for this run: "take this all the way to clean and green merge. defer questions,
approvals to the fable-advisor." The advisor reviewed the PR diff itself (`d96b448..a399287`, one
file): version 2→3; exactly seven `status: "unresolved"` additions; every `cmd` still null and
every `_reason` kept; no detect/exclude/cmd/era/board/repo value touched; merge state clean.

**For the operator's attention:** SC-08 reads "I review … and authorize its merge". That review
was delegated here; this receipt does not claim the operator reviewed the PR personally.

## Landing

| Fact | Value |
|---|---|
| PR state | MERGED, 2026-11-22T22:14:24Z, squash |
| Merge commit (Kaya `main`) | `b9dec8df1de9c065bca3122c371a206d6f46c048` |
| Remote blob `.harness/harness.json` at `main` | `a3992874936d7fc934253107c874384b4204815b` (the validated payload) |

Read back through the fleet reader at the candidate code,
`factory_config.product_config(load_fleet(".harness/factory/fleet.yaml"), "mruangutai/kaya")`, after
clearing its memo: valid, `schema_version` 3, every kind `unresolved`, `github.repo`
`mruangutai/kaya`, board 9. `product_config_report` now reports Kaya `ok: true`; before T-09 it
was the version-2 refusal recorded in `notes/qa-config-reduction.md`.

Kaya's merged file carries the template's prose note on `decision_dispositions_era_start` in its
pre-amendment wording ("an absent key means the project has not adopted it"). It is unvalidated
prose. The Harness template and this repository's config now say an absent key means the same as
null (DEC-256). `upgrade-config.py` keeps present project values, notes included, so Kaya's copy
changes only when someone edits it.
