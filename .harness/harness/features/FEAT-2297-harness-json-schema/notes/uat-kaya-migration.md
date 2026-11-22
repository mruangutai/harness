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

Pending.

## Landing

Pending. A prepared payload or an open PR is not a main landing.
