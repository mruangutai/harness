# Research — FEAT-11 — the combined query, probed live

**BLUF: the combined `repositoryOwner` + `projectV2` + `field` document costs 1 point and
discriminates all four owner/board/field states — but it does NOT do so at a single exit code.
Two states arrive at exit 0 and three at exit 1**, so a resolver that diagnoses only inside
`except GhError` misses two, and one that diagnoses only on the happy path misses three.

Read-only probe, run 2026-08-10 by harness-pm under an explicit orchestrator ruling that a
read-only GraphQL query is categorically different from SC-01's board-6 write measurement. No
writes, no `item-edit`, no new board, no new repo, no issue touched.

## The document probed

```
query($owner: String!, $number: Int!, $field: String!) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        id
        field(name: $field) {
          ... on ProjectV2SingleSelectField { id name options { id name } }
        }
      }
    }
  }
}
```

`... on ProjectV2Owner` on a `RepositoryOwner` selection is legal and resolves — measured, not
inferred. Both `User` and `Organization` satisfy the interface, so one selection covers both.

## The command

```
gh api graphql -f query="$Q" -f owner="$OWNER" -F number="$N" -f field="$F"
```

## Measured facts — six cases, 2026-08-10, account `mruangutai`

| # | Input | Exit | `data` envelope | `errors` key |
|---|---|---|---|---|
| 1 | `mruangutai` / 3 / `Status` | **0** | `__typename: User`, `projectV2.id`, `field` with 5 options | absent |
| 2 | `nosuchlogin-zzq-9931` / 3 / `Status` | **0** | `repositoryOwner: null` | **absent** |
| 3 | `mruangutai` / 3 / `Title` | **0** | `projectV2.id` present, `field: {}` | absent |
| 4 | `github` (an org) / 1 / `Status` | **1** | `__typename: Organization`, `projectV2: null` | `NOT_FOUND`, path `[repositoryOwner, projectV2]` |
| 5 | `mruangutai` / 9999 / `Status` | **1** | `__typename: User`, `projectV2: null` | `NOT_FOUND`, same path |
| 6 | `mruangutai` / 3 / `NoSuchField` | **1** | `projectV2.id` present, `field: null` | `NOT_FOUND`, path `[…, field]` |

Three consequences the plan is built on:

- **Case 2 is the surprise.** An unknown owner is not an error to `gh` at all: exit 0, no `errors`
  key. The owner-not-found branch therefore lives on the SUCCESS path.
- **Case 3 pins the `field: {}` shape at exit 0.** `Title` is a real field that is not
  single-select, so the inline fragment matches nothing and the object is empty. `{} is None` is
  `False`, so an implementation testing `field is None` passes and then sends `--field-id None`.
- **Case 4's `__typename` is readable at exit 1**, before `projectV2` is reached. The org refusal
  therefore does not depend on an org board existing.

On every exit-1 case, **stdout still parses as JSON carrying both `data` and `errors`** — verified
with `json.load` on stdout alone, exit 0. `gh`'s own one-line diagnostic goes to stderr.

## Cost

`gh api rate_limit --jq .resources.graphql.used` differenced across one call: **1**. The 104→2
claim in BRIEF is unaffected by the move from `user(login:)` to `repositoryOwner(login:)`.

## The guard regexes, tested both ways

BSD `grep` on Darwin does not reliably honour `\s`/`\b`, and a pattern that never matches makes
`test "$(grep -c …)" = 0` pass vacuously. POSIX classes under `grep -E` were run against the probed
document (expect 1, 0, 0) and against a deliberately over-scoped decoy using
`projectsV2(first: 100)` plus `fields (first: 100)` with a space (expect 1, 1, 1). Both came out as
expected:

- `field[[:space:]]*\([[:space:]]*name[[:space:]]*:` — present
- `fields[[:space:]]*\(` — absent
- `(first|last)[[:space:]]*:` — absent

Re-verified against the `repositoryOwner` text, not the earlier `user(login:)` draft.

## Baselines, re-derived at `c1d161706ab4867c00078b966e1969203ee6ca92` (HEAD)

`factory_gh.py`: quoted `"field-list"` = 1, bare `field-list` = 4 lines, `"project", "view"` = 1,
`fields[[:space:]]*\(` = 0, `(first|last)[[:space:]]*:` = 0.
`test-factory-integration.py`: quoted `"field-list"` = 1, `"project", "view"` = 1.
`git diff bd295b0e…c1d1617` over `team-config.yaml` and the three task files: empty, so the lane
resolution is unchanged; `check-domain.sh --resolve` re-run at HEAD returns
`harness-backend-dev` / `harness-dev-ops`, exit 0, for all three.

`GhError` stores `argv`, `status`, `stdout`, `stderr` only (`factory_gh.py:41-44`) — there is no
`value` attribute, so any criterion about the value slot must be asserted against the rendered
message string.

## What could NOT be probed read-only

- **An organization owning an existing, accessible board.** No such board is reachable from this
  account. Not blocking: `__typename` is present in both the exit-0 and exit-1 envelopes (cases 1
  and 4), so the org branch fires before `projectV2` is inspected regardless of exit code.
- **A genuine transport or auth failure envelope.** Unprobable without breaking auth. Not blocking:
  the rule is the complement of every measured case — stdout that does not parse to a dict carrying
  `data` — and its test is a stub either way.

## Where this contradicts DESIGN.md

DESIGN.md's Contract 2 says `repositoryOwner` "discriminates all three at exit 0". That was measured
on `repositoryOwner(login:)` **alone**. In the combined document it holds only for case 2; cases 4,
5 and 6 exit 1. The five message rows are unaffected and stay byte-faithful — only the exit-code
reasoning under them changes.
