# Security review — FEAT-33 board-lifecycle-native

review_sha e8a6058e36f914ddb24877b57e272a8b488360b2, base faf409e89bc1f48f437cae9cca0593e1ffb2ade0.

## VERDICT: FAIL — severity_max: high

## Must-fix

**`board_lifecycle.py cmd_provision` mutates a Projects v2 board's field schema without ever
verifying the resolved project is linked to the repository being served — a served fleet
member's own remote config can redirect a schema write onto an unrelated board the operator's
`gh` credentials can reach.**

- `board_lifecycle.py:408-463` (`cmd_provision`) takes `owner`, `number`, `station_field`, and
  `stations` (the option names/text it will write) entirely from `_resolve_board` →
  `factory_config.board_for(fleet, repo_arg)` (`factory_config.py:301-321`), which reads
  `repo_arg`'s **own** `.harness/harness.json` **remotely, at that repo's own default branch**
  (`factory_config.py:253-298`, `factory_gh.file_at_ref`). `validate_board` (`factory_config.py:79-142`)
  checks only shape (non-empty owner, int number, non-empty station names) — never that the
  named project has anything to do with `repo_arg`.
- `factory_gh.project_resolve` (`factory_gh.py:493-545`) — the only check that gates
  `project_create` vs. reuse — confirms the project **exists** at `owner`+`number`. It never
  checks the project's linked repositories. Projects v2 numbers are per-owner, not per-repo
  (that's why a separate `linkProjectV2ToRepository` mutation exists at all,
  `factory_gh.py:594-630`), so any existing project number under `owner` satisfies this check.
- If the field name resolves as an existing single-select field, `project_single_select_extend`
  (`factory_gh.py:675-705`) **replaces the field's entire option set** with
  `existing + missing` — i.e. it does not delete existing options today, but it does append
  attacker-chosen option strings verbatim onto whatever field of whatever board `owner`+`number`
  named. If the field name does not exist at all, `project_single_select_create`
  (`factory_gh.py:645-672`) creates a **brand-new field** with an attacker-chosen name and option
  list on that board.
- **Concrete scenario:** anyone with write access to a served fleet member's default branch (a
  teammate, a merged external PR, or a harness worker agent editing that repo's own
  `.harness/harness.json` as ordinary feature work) sets that repo's `github.board.owner` /
  `number` to the operator's own login and to a **different** project number than the one
  actually meant for that repo — e.g. the harness's own live board (this diff's own comments and
  test fixtures repeatedly cite "board 3" and "board 2" by number, so guessing isn't even
  required). The next `board_lifecycle.py provision --repo <that repo>` — an operation this
  feature wires into `/harness-init`'s normal flow — then adds a new field or appends option
  values onto the **wrong** live board, one that repo has no legitimate claim over.
- This is the exact class of weakness the dispatch's #783 calibration names (a `--repo`-scoped
  operation trusting data that does not actually belong to the audited repo) — but on a *write*
  path, not `audit`'s STATUS read class that #783 already fixed. `_apply_fix`'s STATION/REASON/
  LABEL/STATUS writes (`board_lifecycle.py:640-663`) are safe from this: `gh_board.set_station`
  → `factory_gh.issue_board_item_id` (`factory_gh.py:771-879`) only acts when the *served repo's
  own issue* already carries an item on that board, so those writes stay correctly scoped even
  when `owner`/`number` are wrong. `cmd_provision`'s field-schema writes carry no equivalent
  check.
- Checked and not found: no test in `test-board-lifecycle.py` exercises "project exists at
  owner+number but is not linked to the audited repo"; no plan.yaml/DECISIONS.md entry discusses
  or accepts this as a scoped risk (grepped both for "linked", "confused deputy", "different
  repo", "belongs").
- **Fix direction (constraint, not implementation):** before either the create-field or
  extend-field branch, verify the resolved project's linked repositories include `repo_name` (a
  `repositories` connection is available on `ProjectV2`) and refuse otherwise — the same
  discrimination discipline this module already applies to owner/`__typename`/field-shape.

Severity: **high** — reachable by any actor who can commit to a served repo's default branch
(not solely the operator), against a board that repo has no ownership relationship to; the write
mutates live schema on the operator's own boards with no linkage check and no rollback path.

## Checked and dismissed (no finding)

- **GraphQL literal construction for single-select options** (`factory_gh.py:633-642`,
  `_options_literal`) — `option_names` (from `harness.json`'s declared stations) are embedded via
  `json.dumps(name)`, which produces a properly quoted, backslash-escaped string using exactly the
  escape sequences GraphQL's `StringValue` grammar also recognizes (`\"`, `\\`, `\n`, `\r`, `\t`,
  `\uXXXX`, with `ensure_ascii=True` covering non-ASCII too). A crafted option name cannot break out
  of the string literal into the surrounding mutation body. Confirmed by reading the escaping
  rules, not merely inferred from shape (only `name` is interpolated raw; `color`/`description`
  are hardcoded literals).
- **`--repo` reaching `gh` argv** (`board_lifecycle.py`, `retitle`/`provision`/`audit`/`reconcile`)
  — `_resolve_board` (`board_lifecycle.py:231-246`) rejects any `--repo` value that is not this
  checkout's own declared repo or a name present in `fleet.yaml`'s `repos[]` allowlist
  (`factory_cli.refuse`, exit 2) before it reaches any `gh` call, and every `gh` invocation uses
  list-form argv with no shell (`subprocess.run([gh] + list(args), ...)`, `factory_gh.py:153-155`)
  — no shell injection and no unauthenticated pass-through value.
- **`retitle`'s milestone-derived titles** (`board_lifecycle.py:733-812`) — the new title is built
  from that same issue's own milestone title and rest-of-title text, passed to `gh issue edit
  --title` via list argv. A collaborator who could set a misleading milestone title already
  controls that repo's issue titles directly (P-02: no privilege escalation). This is #782's
  known *correctness* defect (a milestone naming a non-existent feature), not a security gap.
- **Label creation shell-outs** (`factory_gh.py:186-195` `ensure_labels`,
  `board_lifecycle.py:625-637` `_ensure_abandoned_label`) — color and description are hardcoded
  constants; the only variable is the (allowlisted) repo name. No injection surface.
- **Secrets/dependencies** — grepped the full diff for token/secret/password/API-key shaped
  strings: none found beyond unrelated prose ("craft-token", "budget... token count"). No new
  third-party dependency: `board_lifecycle.py` and `factory_gh.py` import only stdlib and
  in-tree modules (`factory_cli`, `factory_config`, `gh_board`, `gh_cost_log`, `gh_issues`).
- **`gh-sync.py`'s new `status` subcommand** (T-13) — `repo`/`board` come from `load_config(root)`,
  derived by walking up from the feature directory to this checkout's own manifest
  (`gh-sync.py:1170-1183`), never from an externally supplied `--repo`. No cross-repo surface
  introduced there.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Served fleet member's remote `.harness/harness.json` → board owner/number/field/options used by `provision` | Tampering (confused deputy: repo B's config redirects a schema write onto board A) | **false** — see must-fix above |
| Served fleet member's remote `.harness/harness.json` → board used by `audit`/`reconcile` issue-level writes | Tampering | true — `issue_board_item_id`/`set_station` scope every write to items the served repo's own issues actually carry |
| `--repo` CLI argument → `gh` argv | Injection / Spoofing | true — allowlisted against fleet.yaml + own repo before use, list-form argv |
| GraphQL option-name literal construction | Injection | true — `json.dumps` escaping is GraphQL-compatible |
| `retitle`'s milestone-title → issue title write | Tampering | true (no escalation — actor already controls the value) |

## Open questions

- { id: Q1, question: "Does the operator consider all current and future fleet members to be
  within the same trust domain as the harness checkout itself (e.g. all repos the operator
  personally owns), such that the provision-side confused-deputy gap is an accepted risk rather
  than a defect to fix before this ships?", blocking: true }

## Scope census

In scope: `board_lifecycle.py` (new, 843 lines), `factory_gh.py`'s six new primitives (285 lines
added), `factory_config.py`'s `board_for`/`product_config` (pre-existing remote-config-trust
pattern, re-exercised by this feature's new caller), `gh-sync.py`'s new `status` subcommand and
`start-task` guard (204 lines changed). Read in full.

Out of scope / no security surface: `check-state.sh` (INV-26 widening, a gate-script change under
the DEC-174 carve-out — correctness/process, not a trust-boundary change), `DECISIONS.md`/
`DECISIONS-INDEX.md`/`BRIEF.md`/`plan.yaml`/notes/observations (documentation and planning
artifacts, no executable surface), `harness.json` template's one-line station addition (adds
`"plan"` to a declared list, no new input path), `templates/harness.json`, test files (exercise
the above, not their own surface).
