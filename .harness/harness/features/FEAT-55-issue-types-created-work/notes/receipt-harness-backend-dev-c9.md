# Receipt — harness-backend-dev — FEAT-55 T-04/T-06/T-08 fix cycle (D-21/D-22)

## BLUF
Both signed corrections landed. All seven named suites exit 0 with zero FAIL lines. Nothing
outside the three target files was touched.

## Changes (exactly the three named files)
1. `.claude/skills/harness/bin/feature-schema.json` — added optional `typed` property to both
   the `github` object and the `factory` object (D-21). Each is an object whose values are
   `"created"`, `"adopted"`, or the promoted boolean `true`; neither added to `required`; both
   objects keep `additionalProperties: false`; each description names D-20 and states absence
   means UNKNOWN/never-typed.
2. `.claude/skills/harness/bin/gh-sync.py:918-919` (was :918-924) — removed the false comment
   and the appended `+ ["--repo", repo]` from the capability-query call in
   `detect_issue_types`; now exactly `[GH] + gh_issue_types.capability_query_args(repo)` (D-22).
3. `tests/integration/test-gh-sync.py:763-768` (was :763-765) — the "every call pins --repo"
   assertion now accepts an `api graphql` line only when it carries the exact
   `owner=implentio` AND `name=fake` GraphQL values (D-22/F-02); every other logged call keeps
   today's `--repo`/`repos/`/`auth` predicate unchanged. Message text updated to match.

## Per-suite results (each run separately, `env -u HARNESS_AGENT_TYPE`, exit code + FAIL-line count captured, not tail-read)

| suite | exit | FAIL lines |
|---|---|---|
| tests/integration/test-gh-issue-types.py | 0 | 0 |
| tests/integration/test-gh-sync.py | 0 | 0 |
| tests/integration/test-gh-backlog-issue-types.py | 0 | 0 |
| tests/integration/test-factory-issue-types.py | 0 | 0 |
| tests/integration/test-factory-decompose.py | 0 | 0 |
| tests/unit/test-factory-gh.py | 0 | 0 |
| tests/integration/test-factory-integration.py | 0 | 0 |

T-04 verify (`test-gh-issue-types.py || exit 1; test-gh-sync.py`): pass.
T-06 verify (adds `test-gh-backlog-issue-types.py`): pass.
T-08 verify (`test-factory-issue-types.py || exit 1; test-factory-decompose.py || exit 1; test-factory-gh.py`): pass.

## Red-proof for the amended C assertion
Mutated `gh_issue_types.py:105` in place (`"-f", "owner=" + owner` → `"-f", "owner=WRONGOWNER"`),
hash before `886b7841a959edbc73c447c806c8bba1`. Re-ran `test-gh-sync.py`: line 11 —
`FAIL  every call pins the pinned repo - --repo/repos flag, auth, or an api graphql line
carrying the exact owner=implentio and name=fake GraphQL values`, with the logged call showing
`... -f owner=WRONGOWNER -f name=fake ...`. Restored the file (reverse of the same substitution);
post-restore hash `886b7841a959edbc73c447c806c8bba1` (identical); `git status --porcelain` for
that path: clean. Re-ran `test-gh-sync.py` after restore: exit 0, 0 FAIL lines. Note:
`gh_issue_types.py` is a non-goal file for this dispatch — it was mutated only transiently as the
scratch probe and is confirmed byte-identical afterward; it does not appear in the final
`git status --porcelain`.

## Schema-refusal proof
`validate-feature-json.py` run against the real (amended-schema) `feature.json` for this feature:
exit 0 (schema still loads and the real file still validates). Built a scratch copy at
`/tmp/schema-refusal-scratch/feature.json` (outside the repo, never touched a tracked path) with
`github.bogus_undeclared_key = true` injected; running the validator against it: exit 1,
`undeclared key 'bogus_undeclared_key' at /github` — refusal proven positively. A second scratch
copy with `github.typed = {"parent": "created", "T-01": true}` validated: exit 0 — confirms the
new declaration is actually load-bearing, not just present. Scratch dir removed;
`git status --porcelain` shows no trace of either scratch file.

## `git status --porcelain` (verbatim, post-restore)
```
 M .claude/skills/harness/bin/feature-schema.json
 M .claude/skills/harness/bin/gh-sync.py
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
 M .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-pm.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml
 M tests/integration/test-gh-sync.py
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/answers-build-blockers-20260905.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/research-FEAT-55-planamend-c9.md
```
(plus this receipt and my observations log, written after this snapshot). `feature.json`,
`observations/harness-pm.md`, `plan.yaml`, and the two untracked `notes/` files predate this
dispatch (the plan amendment landing D-21/D-22 and the PM's blocker Q&A) — none of them were
touched in this segment.

## Tool-behavior finding (not a code defect)
`edit` on `tests/integration/test-gh-sync.py` reported a successful apply (new snapshot tag) that
never reached the real filesystem: a follow-up `read`/`bash sed`/`md5sum` on the identical
absolute worktree path kept showing the pre-edit content, and a retry of the identical edit
against the reported-new tag was rejected as "byte-identical" — the edit tool's own view believed
the new content was already live while disk disagreed. Filed via `xd://report_issue` (rejected:
out of my write domain). Worked around with a `python3` heredoc in `bash` performing the same
single-anchor replacement, confirmed against `git status --porcelain`. Recorded in my
observations log (not Expertise — this is a report of the tool, not a project fact).

## Open questions
None blocking. No contradiction found between plan.yaml's amended T-04 intent and this dispatch's
measurements.
