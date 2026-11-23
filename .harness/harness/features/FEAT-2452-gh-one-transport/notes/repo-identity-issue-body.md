Found in FEAT-2452 validate c3 (`runs/r-20261123-7-validate-validator/digest.md`, `notes/review-harness-code-reviewer-c3.md`). Ruled ship-with-backlog under the operator's delegated authority (fable-advisor, `notes/answers-2026-11-23-validate-c2.md`).

**Severity:** high per harness-code-reviewer, med per harness-validator-lead. The two ratings are carried unreconciled (P-04).

## R1: wayfind trusts a relation's number and drops its repository
At pin `caeebc7c` (and identically at base `b788e9da`), `wayfind.py`'s `sub_issues`, `frontier`, `parent_of` and `resolve` keep only the relation's `number`. Its repository is discarded, even though GitHub allows cross-repository sub-issues and parents, and the REST relation objects carry `repository_url`. Measured scenarios:
- A foreign child `other/repo#11` makes `frontier` advertise local `#11`.
- A foreign parent `other/repo#2` makes `resolve --apply` exit 0. It comments on and closes the ticket and edits local `#2`'s body. The real map never gets its mandatory gist line (DEC-167).

**Preconditions:** a human-made cross-repository relationship on a wayfinding map, plus a same-numbered local issue whose body carries `## Decisions so far` (the latter only for the body write).

**Blast radius:** every wrong write lands in the local repository, as a close plus a body edit that stay in GitHub history. No foreign-repo write and no privilege boundary is crossed. The frontier misdirection is read-only.

## S2: create URL not bound to the create argv
`factory_gh.py:244-253` (`issue_number_from_url`) accepts a well-formed foreign `owner/repo` in gh's returned create URL. The URL's owner/repo is never checked against the repository the create argv named. Reaching this needs faulty or substituted gh output.

## Remedy direction
- Verify each relation's repository (from `repository_url`) against the operating repository, and refuse foreign or unverifiable relationships before advertising or writing.
- Bind the create URL's owner/repo to the create argv.
- Coverage gap: no test exists for a foreign-repository sub-issue or parent.
- Add-on (low, S1): issue-URL host labels have no DNS 63/253 length bound. The authority is never fetched.
