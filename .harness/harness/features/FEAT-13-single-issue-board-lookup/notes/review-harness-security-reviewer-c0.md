# Security review — FEAT-13, `6dfbf7c..d4951c2`

## BLUF

PASS. In scope (new `gh` GraphQL call built from operator/config-supplied values, new response
trust logic, new receipt of a live board read), no `must_fix`. One `info`-level note: the diff's
own trust decisions are all sound, but I found no defense-in-depth control worth flagging above
that, so the floor for a diff genuinely in scope with zero findings is `info`, not `n/a` (`n/a` is
reserved for scoped-out diffs — corrected below from my first pass, where I mis-set `severity_max:
n/a` alongside `in_scope: true`, which is self-contradictory).

## What I checked

**GraphQL construction — `factory_gh.py:292-424`, `issue_board_item_id`.**
`_ISSUE_ITEM_QUERY` is a module-level constant using `$owner`, `$name`, `$number` placeholders.
The call site passes `owner`, `name`, `number` as separate `-f`/`-F` tokens
(`"-f", "owner=" + owner`, `"-f", "name=" + name`, `"-F", "number=" + str(number)`), each glued
into a single argv element with the flag name prefixed. This is `gh api graphql`'s documented
variable-binding form, not string interpolation into the query text — confirmed by reading the
constant directly, not inferred from a comment. `number` is `str()` of an `argparse
type=int`-validated value, so it can never carry a stray character. The single-token
`"owner=" + owner` / `"name=" + name` form also defeats flag-reparsing (an owner value starting
with `-` cannot be read by `gh` as a new flag, since it never appears as its own argv element).
`test-factory-gh.py:654-657` and the integration fixture (`test-factory-integration.py`, new
`"projectItems" in query_text` branch) both assert on the literal argv tokens, not a pattern —
this is identity, not shape, so it closes the injection question rather than just narrowing it.

**`repo.split("/")` validation — `factory_gh.py:326-334`.** Rejects anything that isn't exactly
two non-empty parts before use. `repo` at every call site (`factory_claim.py`'s `fleet["repos"]`
entries and `--repo`, `factory_land.py`'s `--repo`, `factory_decompose.py`'s `--repo`) is
operator/fleet-config-authored, not remote/attacker input — this is a local CLI tool run by the
operator or an agent acting on the operator's behalf, so there is no privilege boundary being
crossed even before the split-and-glue mitigation above.

**Untrusted-response trust — `issue_board_item_id`'s response walk.** Every dict/list/key access
on the parsed GraphQL response is guarded (`isinstance` + key-presence) before use, including the
one the dispatch flagged: `totalCount` is required present and `int`-typed, and a `totalCount >
len(nodes)` truncation is a hard `GhError`, not a silent short read. `project.number` is checked
present and only then compared to `board_number`. A crafted or malformed response (e.g. a
`gh` update changing shape, or a network-corrupted body) fails loud via `GhError`, not by
returning a wrong id or a false-negative `None` that would look like "already added" when it
wasn't — this is the correct direction for the claim/land/decompose call sites, since a wrong
`None` there means re-adding a board item, and a wrong id means acting on someone else's item.
I did not find a path where a response can make `issue_board_item_id` return an id it should not.

**The synthesized item dict — `factory_claim.py:236-243`, traced downstream (the dispatch's
"claiming work that is not the agent's" surface).** `--issue` mode builds a sparse stand-in for a
real board item: `{"id": found_id, "content": {"number": args.issue, "repository": repo_name}}`,
versus the full item the old whole-board scan handed downstream. I traced every consumer of this
dict from its construction to the label/assign/field-set write at the end of `_main` (lines
251-350):
- `_repo_name_of(it)` reads only `content.repository` — present in the synthesized dict, so its
  URL-fallback branch (which would otherwise print a warning and derive a repo name from a
  `repository` URL key the synthesized dict never sets) is never reached for this path.
- `(it.get("content") or {}).get("number")` — present.
- `item.get("id")` at the final `project_field_set` call — present, is `found_id`.
- Every authorization-relevant field — `state`, `labels`, `assignees` — is read exclusively from
  `issue`, a **separate**, freshly-fetched `factory_gh.issue_view(repo_name, num, [...])` call
  (line ~271), never from `it`/`item`. The synthesized dict carries none of these keys and none
  of the guard conditions (`5a-pre` closed-issue refusal, `5a` self-ownership, the
  already-claimed check, the assignee check, the blocker gate) touch it.
No guard reads a field the synthesized dict omits via a permissive `.get()` that would read
absence as permissive. This closes the concern: fail-open via the sparse stand-in is not
reachable.

**Cross-repo collision, no `--repo` given.** The new per-repo loop takes the first fleet repo
(in `fleet.yaml` order) whose `issue_board_item_id` lookup is non-`None`, then `break`s. If two
fleet repos both carry an issue numbered `args.issue` on the same board, fleet-config order
decides which one wins deterministically. The pre-change path (`project_items` filtered by
`content.number == args.issue` with no repo predicate) had the same ambiguity, just resolved by
board API iteration order instead of config order — this diff does not introduce the ambiguity,
it only changes which deterministic order breaks the tie. Not a finding.

**Error-message data exposure — `GhError` construction in the new code.** Every new `GhError`'s
`value` argument is `repo + " issue " + str(number)` or similarly built from already-known,
non-secret identifiers — never `e.stdout`/`e.stderr` from the underlying `gh` call. The
partial-failure recovery path (`except GhError as e: ... json.loads(e.stdout)`) only uses
`e.stdout` to attempt recovery of a valid `{"data": ...}` envelope; on failure it re-raises with a
fixed `next_step` string, not the raw stdout/stderr text. Consistent with the pre-existing
`GhError` docstring contract ("value is always the repository, issue number, field name... never
the class name, never a traceback") — this diff does not weaken it.

**Receipts and qa note.** Read
`notes/receipt-harness-backend-dev-live-spot-check.md` (T-02 live read) and
`notes/receipt-harness-backend-dev-lookup-swap.md` (T-01) in full, and grepped both plus
`qa-FEAT-13-T-01-c0.md` and `feature.yaml` for token/secret/credential patterns — none found. The
live receipt records a GraphQL project-item node id (`PVTI_lAHOAAases4BfZ9Zzg2AMPA`) and a repo
name (`mruangutai/harness`) — an opaque object identifier and the operator's own already-public
repo, neither a credential. No board mutation was made per the receipt's own bounds section.

**Callers — `factory_claim.py`, `factory_land.py`, `factory_decompose.py` diffs.** All three
replace a whole-board `project_items` scan with `issue_board_item_id`; `repo`/`board_number`
provenance is fleet-config or CLI args as above. `factory_land.py`'s new `state != "OPEN"` check
sits after push and PR-create per its own comment (D-04), matching the dispatch's note that this
is intentional, not a gap. `factory_land.py`'s pre-existing `"--title", title` argv construction
(GitHub issue title, potentially set by a lower-trust repo contributor, flows into `gh pr create`
argv) is unchanged by this diff — the diff only widens the `issue_view` field list from `["title"]`
to `["title", "state"]` — so it is out of scope for this review; noting it for the record, not
filing it, since self-scoping bounds this review to the diff.

**Deletion regression check (P-04) — ran the actual suite, did not trust the receipt's GREEN
claim.** `factory_decompose.py` deletes `_item_repo` and the old `_find_existing_item_id` body.
`grep -rn "_item_repo\b" .claude/skills/harness/bin/` returns zero hits (fully removed, no dead
reference). Ran `bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit` myself
(read-only, no `gh` calls): all ten suites PASS, including `test-factory-claim.py`,
`test-factory-land.py`, `test-factory-decompose.py`, `test-factory-gh.py`. No fail-open left by
the deletion.

## Already-adjudicated items — not seen as new, nothing to relitigate

Did not encounter anything touching the `argv[:2]` prose correction, the ratified `claim --issue`
exit-2 delta, `land`'s closed-issue bug (#238), or #218/#241/#242 beyond what the dispatch already
named.

## DEC-174 carve-out

No touch to `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, or `check-state.sh` in
this diff.

```yaml
VERDICT: PASS
DIGEST:
  headline: "New gh GraphQL lookup binds owner/name/number as query variables (not string-interpolated), defensively type-checks the untrusted response, and the sparse synthesized item dict in factory_claim.py never reaches an authorization decision — traced to source, no fail-open path found."
  in_scope: true
  scope_reason: "Diff adds a new outbound GraphQL call built from operator/fleet-config values, changes untrusted-response trust logic three call sites route claim/land/decompose actions on, and adds a live-board-read receipt to the repo."
  severity_max: info
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "operator/fleet-config value -> gh CLI argv (factory_claim/land/decompose -> factory_gh.issue_board_item_id)", stride: T, mitigated: true }
    - { boundary: "owner/name/number -> GraphQL query text", stride: I, mitigated: true }
    - { boundary: "GitHub GraphQL response -> claim/land/decompose action target (item id)", stride: T, mitigated: true }
    - { boundary: "gh stdout/stderr -> operator-visible GhError message", stride: I, mitigated: true }
    - { boundary: "synthesized sparse item dict -> claim authorization decisions", stride: E, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-13-single-issue-board-lookup/notes/review-harness-security-reviewer-c0.md
```
