# Security review — FEAT-55, cycle 1 — OWASP + STRIDE @ cd6a3c0d

## Verdict: PASS (severity_max: low)

One low-severity hygiene finding (T-10's manual probe), no must-fix. Everything reachable
from an untrusted or operator-config boundary — `gh` invocation, GraphQL construction,
config-to-typed-value flow — uses the safe pattern already established in this codebase.

## What I looked at

- `gh_issue_types.py` (net-new, ~160 ln): `capability_query_args`, `node_id_args`,
  `apply_type_args`, `overrides_from_config`, `classify_capability`, `missing_types`,
  `refusal_text` — every one.
- `gh-sync.py`: `detect_issue_types`, `_required_issue_types`,
  `_refuse_undeclared_issue_types`, `apply_issue_type`, `_backfill_issue_types`, the
  `cmd_open`/`cmd_backlog` split, `load_config`'s new `issue_types` return.
- `factory_gh.py`: `detect_issue_types`, `apply_issue_type`.
- `factory_decompose.py`: `_issue_type_overrides`, `_task_issue_type`,
  `_required_issue_types`, `_refuse_on_missing_types`, `_backfill_issue_types`,
  `_task_labels`.
- `feature-schema.json`'s two `typed` additions (D-21) and every read of `typed` that
  gates control flow (`_parent_needs_type`, `_task_needs_type`, `load_factory`).
- `.harness/harness.json`'s `issue_types_live` addition, `github-mirror.md`'s 8th
  read-back purpose, `DECISIONS.md`'s D-18/D-19/D-20 text.
- `tests/manual/probe-issue-types.py` in full (T-10) — the one script here that talks to
  the real API — for command construction and GraphQL text, without running it.
- Full-diff grep for `shell=True|os.system|eval(|exec(` and for
  `token|secret|password|GITHUB_TOKEN|Bearer` across every named production file: no hits.

## Why the surface is mostly clean

**Command construction is argv-list throughout, never a shell.** Every `gh` call in
`gh_issue_types.py`, `gh-sync.py`, `factory_gh.py`, `factory_decompose.py` is
`subprocess.run([GH] + args, ...)` with `args` a Python list — no `shell=True`
anywhere in the four files, confirmed by grep. `repo` (owner/name), issue numbers, and
type ids are always separate argv elements or separate `-f key=value` GraphQL
variables (`capability_query_args`, `apply_type_args`, `node_id_args`) — never spliced
into a shell string or into the GraphQL query *text*. `CAPABILITY_QUERY` and
`APPLY_TYPE_MUTATION` are fixed strings; only the variables change per call. This is
the parameterized-query pattern, and it closes both shell injection and GraphQL
injection for every production call site.

**Config-sourced values are allow-listed before they can influence anything.**
`overrides_from_config` (fed by `.harness/harness.json`'s `github.issue_types`, an
operator-owned file) keeps only `key in LEGAL_OVERRIDE_KEYS` (`Bug`/`Feature`/`Task`/
`parent`) with a non-empty string value. The resulting override value is used only as
a **dict key** to look up a server-issued type id in `declared` (itself sourced from
GitHub's own GraphQL response) — it never reaches a shell or gets spliced into query
text. An override that doesn't match a declared type name causes
`_refuse_undeclared_issue_types`/`_refuse_on_missing_types` to exit 2 before any
create or apply-type call — fail-closed, not fail-open.

**`feature.json`'s new `typed` field cannot become untrusted control flow.**
Schema is `additionalProperties: false` with `oneOf` restricted to the literal enum
`"created"|"adopted"` or `const: true` (D-21) — a hand-edited or corrupted value fails
validation, and `factory_decompose.py`'s `load_factory` independently re-checks
`v is True or v in ("created", "adopted")` before trusting an entry. `feature.json`
itself is harness-internal state, not attacker-reachable input from outside the
system that already has write access to the repo.

**No new data exposure.** The only capped/truncated read-back is
`_capability_error`'s `stdout[:200]` in `gh_issue_types.py`, printed through the same
`gh-sync: ... - labels only` pattern this file already used for every other
environmental-skip message (pre-existing shape, not a new leak). No new log line, no
new receipt, carries a token, auth header, or `gh` credential artifact.

## Finding

**LOW — `tests/manual/probe-issue-types.py:97-101` (`_read_back_issue_type`), owning
task T-10.** This one function breaks the parameterized-variable pattern the rest of
the feature uses everywhere else: it builds the GraphQL query by Python `%`-formatting
`owner` and `name` directly into the query *text* inside quotes —
`'repository(owner:"%s",name:"%s")... issue(number:%s)' % (owner, name, number)` — then
ships the resulting string as the single `-f query=` value, instead of passing
`owner`/`name` as separate GraphQL variables the way `capability_query_args` does two
files away in the same PR. A `target` containing a `"` (e.g.
`x"){__schema{types{name}}}#`) would break out of the string literal and let arbitrary
GraphQL ride into the same authenticated `gh api graphql` call.

*Reachability, and why this stays low rather than high:* `owner`/`name` come only from
`--create-in TARGET`, a CLI flag the operator types themselves when explicitly opting
into this host-only manual probe (T-10's own docstring: never imports a fixture, never
runs unattended, requires a credentialled host). The "attacker" supplying the crafted
string is the same principal who already holds the `gh` session the injected query
would run under — no privilege crosses a boundary (P-02: an actor who already controls
the input already holds the privilege it grants). `number` is not attacker-influenced
in practice — it comes from parsing the URL `gh issue create` itself just returned in
the same run.

*Why it's worth recording anyway:* this is the one place in the feature that departs
from its own established-safe pattern, in a file whose purpose is explicitly to touch
the real API. If `_read_back_issue_type` or its calling convention is ever reused with
an externally-sourced target (a webhook payload, an issue title, anything not typed by
the operator's own fingers), the injection becomes live with no further code change.
Recommend it match `capability_query_args`'s `-f owner=`, `-f name=` shape before this
function acquires a second caller.

## STRIDE

| boundary | stride | mitigated |
|---|---|---|
| operator `.harness/harness.json` `github.issue_types` -> type resolution | T (config value could steer which type gets applied) | true — allow-listed keys, value only used as a lookup key against server-issued ids, refuse-before-create on any miss |
| `gh` subprocess argv construction (repo/number/type-id) | T (shell/argument injection) | true — list-form argv, `-f key=value` GraphQL variables throughout production code |
| `feature.json`/`factory.json` `typed` field -> create/backfill control flow | T (malformed receipt steering a re-apply or skip) | true — schema enum-closed, read side re-validates the same three literal values |
| `tests/manual/probe-issue-types.py`'s live GraphQL read-back | I/T (GraphQL text injection via `%`-formatted owner/name) | false — reachable only via an operator-typed CLI flag on a manual, host-only, opt-in script; no untrusted or automated path exists today |

## Open questions

None blocking. The T-10 finding is advisory (low, no signed decision it contradicts,
fixable by matching the existing pattern in the same file set).

```yaml
VERDICT: PASS
DIGEST:
  headline: "One low-severity GraphQL-text-interpolation hygiene gap in the manual probe (T-10); every production gh/GraphQL call site uses parameterized argv and allow-listed config, no must-fix."
  in_scope: true
  scope_reason: "Diff shells out to gh and issues GraphQL from config-sourced values (harness.json github.issue_types) and receipt state (feature.json typed) — a real trust boundary, audited in full."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "harness.json github.issue_types -> type resolution", stride: T, mitigated: true }
    - { boundary: "gh subprocess argv construction", stride: T, mitigated: true }
    - { boundary: "feature.json/factory.json typed field -> control flow", stride: T, mitigated: true }
    - { boundary: "probe-issue-types.py live GraphQL read-back text interpolation", stride: I, mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-security-reviewer-c1.md
```
