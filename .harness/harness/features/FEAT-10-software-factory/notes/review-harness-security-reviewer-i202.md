# Security review — i202 — gate integrity after check-docs.sh removal

**Verdict: PASS, out of scope for a finding.** All three targeted checks came back clean. Base
resolved as `c4fea5d` → `c4fea5ddce6414b9e7e503f03ab446f248452212` (the dispatch's `c4fea5db` does
not resolve on its own; noting this so the next reader isn't confused). Review sha:
`835b2976abd649fb814385d7d9b5b19fb7e1431a`.

## Q1 — Gate integrity / fail-open

**bin/ scripts.** `git grep -n 'check-docs' 835b297 -- .claude/skills/harness/bin/` returns one
hit: `check-state.sh:856`, inside a comment explaining the removal ("INV-10 IS GONE, AND THE
NUMBER IS RETIRED WITH IT..."). No code, no `[ -x check-docs.sh ] && run`, no `|| true`, no loop
entry. Read directly at the SHA (`check-state.sh:840-870`): the INV-10 block that used to invoke
`check-docs.sh` is deleted outright, not wrapped in a guard.

`run-unit-tests.sh` and `deploy.sh` at 835b297: no match for `check-docs` in either (checked via
`git show <sha>:<path> | grep`).

**Hook registrations** (the surface the first pass under-covered — `.claude/settings.json` is
outside `bin/` and `.github/`, and is exactly where a `PreToolUse`/`PostToolUse` command pointing
at a deleted file would fail open per G-01/DEC-100 — non-2 exit is non-blocking, no stderr).
`git grep -n 'check-docs' 835b297 -- .claude/settings.json .claude/settings.local.json` — no
match. Full read of `git show 835b297:.claude/settings.json`: five hook registrations
(`inject-expertise.sh`, `check-domain.sh` ×2, `branch-create-gate.sh`, `bash-write-guard.sh`,
`dispatch-guard.sh`, `validate-digest.py`) — none reference `check-docs.sh`.

**Non-.md hits repo-wide.** Full `git grep -n 'check-docs' 835b297` (63KB) filtered to non-`.md`
files: every hit is a `.txt`/`.html`/`.yaml` artifact under `.harness/features/FEAT-0{3,4,7,8,9,10}-*/`
— shipped digests, plan bodies and a rendered ship-review HTML narrating past runs where
`check-docs.sh` was invoked and passed. None are executable, none are hook config, none are CI
config. Historical record, not live enforcement.

**No orphaned test file.** `git ls-tree -r 835b297 -- .claude/skills/harness/bin/` has no
`test-check-docs.py`; `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays have no
dangling entry for it.

## Q2 — CODEOWNERS

`git diff c4fea5d..835b297 -- .github/CODEOWNERS` is a one-line comment edit removing
`check-docs.sh` from a parenthetical list inside the file's "NOT OWNED, deliberately" section.
`check-docs.sh` was never an owned path — it appeared only in prose explaining why certain other
`bin/` scripts are intentionally unowned. No path lost an owner: the two actual entries
(`/.github/` and `/.claude/skills/harness/bin/run-unit-tests.sh`, both `@mruangutai`) are
unchanged. Ownership scope is neither widened nor narrowed.

## Q3 — CI

`git grep -n 'check-docs' 835b297 -- .github/` returns nothing. Full read of
`git show 835b297:.github/workflows/tests.yml`: the `integration` job runs
`run-unit-tests.sh --kind integration` and the promoted `check-plan-routes.py` route gate —
neither ever invoked `check-docs.sh`. No CI step disappears (there was nothing to disappear) and
no step goes red waiting on a deleted binary.

## Second gate touched in this diff: test-gen-decisions-index.py

The commit also rewrites `test_row_per_distinct_dec_matches_authority` in
`.claude/skills/harness/bin/test-gen-decisions-index.py` (DEC-104's strike removed the fenced
`## DEC-83` duplicate the old assertion counted on) and deletes two `check-docs.sh`-specific test
functions (`test_checker_scans_root_level_markdown`,
`test_checker_flags_planted_stale_phrase_in_index` — correctly, since the binary they exercise no
longer exists).

Verified by execution, not just reading the diff (per P-04): extracted `835b297` into a scratch
dir with `git archive` (never the working tree, which carries FEAT-11/FEAT-12 edits) and ran
`test-gen-decisions-index.py` directly. All 8 tests pass, including
`test_row_per_distinct_dec_matches_authority` and `test_committed_index_is_complete_and_within_budget`
— both of which still run against the **live** `docs/harness/DECISIONS.md` /
`DECISIONS-INDEX.md` at that SHA (via `REAL_DECISIONS`/`REAL_INDEX`, not only a synthetic plant).
The rewritten test still asserts the fence-guard against a synthetic `DEC-9999` fixture *and*
still asserts row-count-matches-distinct-DEC-count against the real authority file copied into a
temp dir — the index-vs-authority relationship is intact, not degraded to a synthetic-only check.

`test-gen-decisions-index.py` is in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` array (confirmed
by direct read), and CI's `tests.yml` runs `--kind integration`, so this gate is exercised on
every push/PR, not silently dropped to unit-only.

## Scope note

Per DEC-188 (cited in the commit message and the dispatch), the *decision* to remove the
propagation checker and rely on human diff review is not re-litigated here — only residue from the
mechanics of removal was in scope, and none was found.
