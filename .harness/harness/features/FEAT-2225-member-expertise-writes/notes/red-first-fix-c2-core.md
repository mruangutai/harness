# Red-first — validate c2 fix, F2 (T-01 core): anchor the write chain on an authorized base, never HEAD

Slice owner: MergeGate. Files: `.claude/skills/harness/bin/expertise-merge.py`,
`tests/integration/test-expertise-merge.py`, `tests/unit/test-expertise-ops.py`. Not committed.

Command: `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`
Red runs point `EXPERTISE_MERGE_BIN` at a copy of the bin directory (the suites' existing override).

## RED 1 — new tests against the pre-change core (HEAD's expertise-merge.py, the c1 HEAD anchor)

Logs: `/tmp/f2225-c2/red-pre-unit.txt`, `/tmp/f2225-c2/red-pre-int.txt`. Unit exit 1, integration exit 1:
- `case_u44_authorized_base: completed without raising` (`authorized_base` did not exist)
- `verify c2 member: unreceipted G-01 deletion COMMITTED before the first receipted application refuses (base=default)`
- `verify c2 member: … refuses (base=--base)`
- `verify c2 lead: … refuses (base=default)`
- `verify c2 lead: … refuses (base=--base)`
- `verify c2: no default branch and no --base refuses with 15, NO AUTHORIZED BASE`

So the c2 finding ran as an executed exploit: a G-01 deletion committed on the feature branch, then a legitimate P-01 application, made verify-receipt exit 0 for both the member lineage (harness-backend-dev, parent lead) and the lead lineage (harness-product-lead, parent orchestrator). That held with and without `--base`, because HEAD was accepted as an anchor.

## RED 2 — QA mutant N2 (unchained-active-batch guard removed) against the new core

The mutant changes `if unchained or anchor not in states:` to `if anchor not in states:`. Logs: `/tmp/f2225-c2/red-n2-*.txt`. Unit exit 0; integration exit 1:
- `verify c2: an active batch off the write chain refuses and is named (unchained-batch guard)`

The fixture: run-f adds P-01; the file is reverted to the baseline by hand; run-a re-adds the identical P-01. The file and run-f's final effect agree, and the chain reaches the base through run-a. Only the guard catches run-f's batch, which is off the chain. Under the N2 mutant, this check is the only one that failed.

## Fix

- New public `authorized_base(real_root, base)`: the merge-base of HEAD with `--base` when given. Otherwise it uses the default branch, the first of `refs/remotes/origin/HEAD`, `refs/remotes/origin/main`, `refs/heads/main` that resolves (`_default_branch`).
- If none resolves, or the commit shares no history with HEAD, it refuses with exit 15 and `NO AUTHORIZED BASE: …`.
- `_refuse_unreceipted_content` now anchors ONLY on that commit's blob of the destination; absent there still means "absent". The HEAD anchor is gone.
- Ordered/superseded chain walking, identical-add preservation, the uncommitted-deletion refusal, exit codes and output contract are unchanged.
- With `--base`, the anchor is the merge-base with HEAD rather than the base blob itself. When the PR contains the base, that is the same commit. When main has moved past the fork (the supersession fixture's `base_z`), it is the fork point, which is where the receipted writes actually start; without that, the existing supersession `--base` control would refuse.

## GREEN

Same command, real code: exit 0. Unit 202 PASS, integration 375 PASS, 0 FAIL (`/tmp/f2225-c2/green-*.txt`).

Controls kept green:
- clean (`verify full: a clean receipted add verifies`, the c2 committed-clean feature-branch checks for both lineages, with and without `--base`);
- supersession (`replacement receipt verifies…` with `--base` and with none, plus withdrawal);
- post-replay (`supersession: replay now succeeds…` followed by verification of the up-to-date file);
- the c1 uncommitted deletion/edit refusals.

## code-grade (path mode)

Production (bar 4): `_default_branch` 4, `authorized_base` 4, `_refuse_unreceipted_content` 4, `_committed_state` 5.

Tests (bar 3): `_feature_branch_fixture`, `_check_committed_tamper`, `_check_feature_branch_clean`, `_check_no_authorized_base`, `_check_unchained_active_batch` 4, `case_verify_authorized_anchor` 5, `_git`/`_branch_repo`/`_authorized_or_refusal` 5, `case_u44_authorized_base` 4.

## Boundary

The anchor is only as independent as the default-branch ref. A checkout whose HEAD *is* the default branch anchors on HEAD, because the merge-base with itself is HEAD. Feature work happens on `feat/<id>` branches, so this case is the main checkout, not a distill PR.
