# SIMPLIFY · angle REUSE · FEAT-55 · read-only pass

BLUF: **0 REUSE findings, none worth applying.** `gh_issue_types.py`'s extraction held cleanly
across all three callers — no duplicated classification branch, no re-spelled mapping table, no
hand-rolled argv. `correctness:` list is also empty — no D-20 key-presence bug found anywhere in
the surface. `git status --porcelain` at end of run (verbatim, none of it mine):
```
 M .claude/skills/harness/references/github-mirror.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/qa-2026-09-05-01-validator.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
```
(github-mirror.md is the main session's own concurrent edit per the shared context; the other two
are a sibling QA agent's artifacts. None touched by me.)

## Three leads

1. **Extraction held — CONFIRMED.** `gh_issue_types.py:114-142` (`classify_capability`),
   `:100-107` (`capability_query_args`), `:13-26`/`:28` (mapping tables), `:158-159`
   (`missing_types`), `:162-167` (`refusal_text`) are each imported and called, never re-spelled,
   by all three callers:
   - `gh-sync.py:92` imports the module; calls at `:918-920` (capability), `:954/958-959`
     (parent/task type resolution), `:972/976` (missing/refusal), `:985-986` (apply), `:1641-1642`
     (backlog nature), `:1703` (backlog apply).
   - `factory_gh.py:29` imports it; calls at `:220-223` (capability), `:230-231` (apply).
   - `factory_decompose.py:44` imports it; calls at `:364/387/401/412/417/438/445`
     (overrides, type resolution, refusal, backfill apply).
   No duplicate `CAPABILITY_QUERY`/`APPLY_TYPE_MUTATION` text, no re-declared
   `DEFAULT_TYPE_BY_CHANGE_TYPE`/`DEFAULT_TYPE_BY_NATURE` dict literal, and no second
   classification branch found in any of the three callers (grepped for `"Bug"`/`"Feature"`/
   `"Task"`/`issueTypes`/`updateIssue` literals in all three files — the only GraphQL literals in
   `factory_gh.py` are the pre-existing, unrelated `_REPO_ID_QUERY`/`_ISSUE_ITEM_QUERY` at
   `factory_gh.py:609-612,778-782`, project-board queries with no overlap with issue types).

2. **Two call sites agree in argv shape post-D-22 — CONFIRMED; error-handling divergence is
   deliberate, not a REUSE gap.** `gh-sync.py:918` and `factory_gh.py:220` both invoke
   `gh_issue_types.capability_query_args(repo)` with no extra flags (D-22,
   `plan.yaml:186-201`, confirms the appended `--repo` was removed and both now agree). The
   remaining difference — `gh-sync.py:918-919` calls `subprocess.run` directly and reads
   `r.returncode`/`r.stdout`, while `factory_gh.py:220-223` calls `run_gh` and catches `GhError`
   — is explicitly documented as intentional in `gh_issue_types.py:2-4`: "`gh-sync.py` skips and
   exits 0 on an environmental failure, `factory_gh.py` raises `GhError` — two different failure
   semantics a shared runner here would have to pick one of, so each caller keeps its own." This
   is the same pattern `gh_issues.py:6-8` already establishes for the sibling module. Not a
   finding.

3. **`gh_issues.py`'s argv-builder pattern is followed, nothing hand-rolled — CONFIRMED.**
   `gh_issue_types.py`'s new argv builders (`capability_query_args`, `node_id_args`,
   `apply_type_args`, `gh_issue_types.py:100-107,145-146,149-155`) follow the exact shape
   `gh_issues.py:17-49` already established (bare functions returning `gh` argv lists, no
   execution, one docstring citing the two-callers-two-semantics tradeoff). No caller
   reconstructs a `gh api graphql` argv list, a node-id lookup, or an `updateIssue` mutation by
   hand anywhere in the diff.

## correctness: (D-20 key-presence check)
none — grepped `gh-sync.py`, `factory_gh.py`, `factory_decompose.py`, and all four new test files
for `"typed" in rec`/`"typed" in fac`/bare `.get("typed") is not None` patterns; every read of the
`typed` mapping in production code and tests compares against an exact value (`== "created"`,
`is True`, `is False`, `is not True`) or uses `"key" not in rec.get("typed", {})` — never a bare
`"typed" in rec` presence test that would misread ABSENT as present. No four-state provenance bug
found.

## decision_questions:
none.

## open_questions:
none — all three leads resolved by direct read, no unresolved lead.
