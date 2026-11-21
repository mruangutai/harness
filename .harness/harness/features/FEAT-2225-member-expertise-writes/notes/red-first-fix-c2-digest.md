# Red first — validate c2 fix, DigestContract slice (F2: committed tamper at validate-digest)

## Scenario

qa's craft file holds G-01 on the default branch (`origin/main`, with `origin/HEAD` pointing
at it). On the feature branch `feat/mx`, G-01 is deleted with no op and the deletion is
committed. qa then applies P-01 legitimately through `expertise-merge.py member-ops`.

New group `run_member_expertise_committed_tamper_cases` in tests/integration/test-validate-digest.py
(4 checks):
- committed tamper live: the member's yield is refused
- committed tamper live: the lead's yield is refused
- committed tamper durable: the durable check refuses (a lead record claiming the add)
- committed tamper durable: close-run refuses the run at its digest stage

Fixture change only, for the other groups: `_mx_tree` now gives each tree a local bare
`origin` (an ignored `.mx-origin.git` inside the tree), sets `origin/HEAD -> origin/main`, and
moves the work onto `feat/mx`. `_mx_prior_on_main` publishes the pre-existing G-01 to main.
No assertion in leaf, lead, supersession, authority or F2 changed.

## RED: against the current core (HEAD e0e93f60 `expertise-merge.py`, which anchors on HEAD)

Bin copy at `/tmp/t04c2/redbin`, with `expertise-merge.py` from `git show HEAD:` and every other
file from the worktree:
`VALIDATE_DIGEST_BIN=/tmp/t04c2/redbin/validate-digest.py python3 tests/integration/test-validate-digest.py --only run_member_expertise_committed_tamper_cases`
→ exit 1, 0/4. All four checks FAIL: the live yields exit 0, the durable CLI prints
`digest ok`, and close-run passes its digest stage. Controls in the same red run: F2 6/6 and
leaf 13/13 stay green on the old core with the new fixture. Raw output: `/tmp/t04c2/red-vd.txt`.

## GREEN: with T04MergeGate's `authorized_base` change in the worktree

`python3 tests/integration/test-validate-digest.py` → exit 0, `ALL PASSED.`
member-expertise: leaf 13/13, lead 13/13, supersession 8/8, authority 10/10, F2 6/6,
committed tamper 4/4. Raw output: `/tmp/t04c2/green-vd.txt`.

## validate-digest change

`_verify_receipt` still passes no `--base`, and its docstring records why. With no base, the
core anchors on the merge-base of HEAD with the default branch (`authorized_base`), never on
HEAD, and refuses (15, NO AUTHORIZED BASE) when that cannot resolve. Resolving a base in
validate-digest would duplicate that resolver. Its own `_default_branch_or_none` reads only
`origin/HEAD`, so the two could disagree. Nothing comes from a digest field.

## Grades (path mode)

`_verify_receipt` 4. Test functions: `_mx_tree` 3, `_mx_origin` 5, `_mx_publish` 5,
`_mx_prior_on_main` 5, `_mx_f2_prepare` 4, `_mx_committed_tamper_prepare` 5,
`_mx_committed_tamper_live` 5, `_mx_committed_tamper_durable` 4,
`run_member_expertise_committed_tamper_cases` 5.
