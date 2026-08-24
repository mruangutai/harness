# Security re-check — FEAT-33 board-lifecycle-native, cycle c1

Reviewed the uncommitted working-tree diff against HEAD (e8a6058) — `git diff HEAD --
.claude/skills/harness/bin/board_lifecycle.py` — since the fix cycle has not been committed.
Cross-checked against `notes/receipt-harness-dev-ops-fixcycle-c1.md`.

## VERDICT: PASS — severity_max: info

## c0 must-fix: CLOSED

The confused-deputy gap (project exists under `owner` but is not linked to `repo_name`,
allowing a served repo's own remote `harness.json` to redirect a field-schema mutation onto an
unrelated live board) is closed. Established by:

- Reading the actual diff (not the receipt's prose): `_project_linked_repos` (`board_lifecycle.py:328-383`)
  is a new, read-only, paginated GraphQL query (`repositories(first: 100, after:)`, capped at 10
  pages with a `GhError` refusal on truncation — never a silent partial list).
- Tracing every mutation reachable from `cmd_provision` by hand: after `resolved = project_resolve(...)`
  returns non-None, the guard (`board_lifecycle.py:538-553`) sits unconditionally before BOTH
  remaining branches — `project_single_select_create` (field absent) and
  `project_single_select_extend` (field exists) — with no code path that reaches either without
  first passing the guard. `factory_cli.refuse` (`factory_cli.py:50-52`) calls `sys.exit`
  directly, so a refusal cannot fall through.
- Running `test-board-lifecycle.py` and `test-factory-integration.py` myself, not trusting the
  receipt's reported counts: 46/46 and 131/131, including the three new "linkage guard
  (MUST-FIX 1)" assertions (refuses exit 2, zero mutations, refusal names project+repo+reason).

## The five questions

**1. Is the guard before EVERY mutation reachable from `cmd_provision`?**
Yes. The `resolved is None` branch (create-then-link) is the only OTHER write path in the
function, and it does not need the guard: `project_create` makes a brand-new project and
`project_link_repository` links it to `repo_name` itself in the same call — there is no existing
board it could hijack, by construction. The two guarded branches (`project_single_select_create`,
`project_single_select_extend`) are the only mutations reachable once `resolved` is non-None, and
both sit strictly after the guard at `board_lifecycle.py:538-553`. `_field_probe` between the
guard and the branches is read-only (confirmed in c0, unchanged here).

**2. Can the pagination cap hide a linkage, and which way does it fail?**
Fails closed in both directions I could construct:
- **Cap exceeded** (>1000 linked repos): raises `GhError`, propagates unhandled out of
  `cmd_provision` (not caught locally), reaches `factory_cli.run`'s generic trap — zero mutation,
  same as any other unhandled `GhError` in this module today.
- **Missing/malformed `pageInfo`** (e.g. `pageInfo` absent, or `hasNextPage` absent from it):
  `page.get("hasNextPage")` returns `None`, which is falsy, so the loop returns the names
  collected so far — a truncated `names` list. A truncated list can only ever *remove* a
  genuinely-linked repo from the accepted set, never *add* an unlinked one — the direction that
  matters for this threat model. Worst case this misfires as a false refusal on a legitimate
  provision (an availability/correctness annoyance, not a security gap) if GitHub's schema ever
  returns a partial `pageInfo` shape mid-connection, which I have no evidence it does.
- Same reasoning for an unresolvable `owner` or a non-`ProjectV2Owner` `__typename`: both collapse
  to `names == []`, which refuses rather than admits.

**3. Does the `nameWithOwner` comparison match how `repo_name` is spelled everywhere it originates?**
`repo_name` is either `_own_repo(root)` (this checkout's own `harness.json` `github.repo`) or
`fleet.yaml`'s `repos[].name` (`factory_config.py:229-238` `repo_entry`) — both hand-authored
`owner/name` strings, the same value already passed verbatim to every other `gh` call in this
file (`--repo repo_name` in `audit`/`reconcile`/`retitle`). GitHub's `nameWithOwner` returns the
canonical-case `owner/name` form. If a fleet operator declared a repo in different case than
GitHub's canonical casing, the `in` check (case-sensitive) would false-refuse — but that same
mismatch would already break `--repo repo_name` on every other `gh` call in this module (GitHub's
CLI is lenient there, so it wouldn't surface the same way), making it a pre-existing spelling
convention this fix inherits rather than a new hole it opens. No case-mismatch scenario lets an
unlinked repo read as linked — only the reverse (false refusal), which fails closed.

**4. Does the same weakness exist anywhere else in the diff?**
No. `retitle` never resolves a Projects v2 project number at all — its writes
(`gh issue edit --title`, `board_lifecycle.py:933`) act on issues enumerated via
`gh issue list --repo repo_name` (`board_lifecycle.py:876`), i.e. issues that belong to the
served repo's own tracker by construction of the `--repo` argument, which is itself allowlisted
against `fleet.yaml`/own-repo before use (confirmed unchanged from c0). The confused-deputy class
is specific to Projects v2's per-owner (not per-repo) numbering — a property `retitle` never
touches. `audit`/`reconcile`'s issue-level writes remain bounded by `set_station` →
`issue_board_item_id`, unchanged by this fix cycle, confirmed still passing (reconcile #783
regression cases, unmodified, both PASS).

**5. Did the fix introduce a new surface?**
No new injection surface. `_project_linked_repos` sends `owner`, `number` via `-f`/`-F` GraphQL
variable bindings — the identical mechanism `project_resolve` (already cleared in c0) already
uses for the same two values — never string-interpolated into the query text. The one new value,
`after` (the pagination cursor), is not attacker-influenced: it is GitHub's own opaque
`pageInfo.endCursor`, relayed verbatim from a prior response of the same query, and reaches `gh`
through the same `-f after=` variable binding, not string concatenation. `owner`/`number`
themselves are not new inputs — they are the same served-repo-declared values `project_resolve`
already consumes; this query adds no attacker-reachable value that wasn't already in scope.

## Threat model (delta from c0)

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Served fleet member's remote `harness.json` → board owner/number used by `provision`'s field-schema mutations | Tampering (confused deputy) | **true** — closed by the linkage guard, verified above |
| New `_project_linked_repos` GraphQL query's own variables | Injection | true — variable-bound, not interpolated; identical pattern to `project_resolve` |
| Pagination/malformed-response edge cases in the new query | Information disclosure / Tampering | true — every failure mode traced fails closed (refuse), none fails open |
| `retitle` / `audit` / `reconcile` write paths | Tampering | true — unchanged from c0, re-confirmed passing |

## Scope census

Diff reviewed: `board_lifecycle.py` (the fix), `test-board-lifecycle.py` and
`test-factory-integration.py` (new fixtures/cases exercising it). No other file in the working
tree diff (`SKILL.md`, `feature.json`, `FEAT-34/BRIEF.md`) carries executable security surface.

## Open questions

None blocking. c0's Q1 (trust-domain scope of fleet members) is now moot — the guard makes the
answer irrelevant to whether this ships.
