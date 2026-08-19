# Receipt — harness-backend-dev — 2026-08-19-8-eng — apply-bin

## Result: applied the finding as specified

Deleted 21 of the 22 dead two-line `json.dump({"github": {"sync": True, "repo": "implentio/fake",
"board": None}}, ...)` blocks in `.claude/skills/harness/bin/test-gh-sync.py`. Each deleted site was
verified individually against the three criteria before removal (immediately preceded by `stage(...)`
with no intervening `harness.json` write, `stage()` not overriding `sync=`/`repo=`, nothing reading
`harness.json` between the two). All 21 passed. The site at `# --- the real open` (originally line
399) was located by its comment, not by line number, and is untouched — confirmed by post-edit grep:
only one occurrence of the target literal remains in the file, immediately preceded by that comment.

Deletion was done bottom-up by matching the exact two-line literal text, not by line-number list, so
the "numbers go stale after the first deletion" trap did not apply.

## Verification

- `ok`-line count of `test-gh-sync.py`: **104 before, 104 after** (`diff` of the two `ok`-line sets
  is empty — same set, same order, not just same count).
- `python3 .claude/skills/harness/bin/test-gh-sync.py`: rc=0, zero `FAIL` lines.
- Pinned line `an unusable board config is a loud failure, not a skipped station write` — still
  present as `ok` (line 98 of output).
- `bash .claude/skills/harness/bin/run-unit-tests.sh --kind all`: rc=0. `grep -c FAIL` on the full
  output returned 4, but all 4 are `ok`-prefixed lines whose *test name* contains the substring
  "FAIL" (e.g. `ok    FAIL over an escalating member is rejected`) — zero actual `FAIL`-prefixed
  result lines. Suite fully green.

No ceiling-of-one-fix was needed — nothing reddened.

## Sites declined: none

All 21 candidate sites matched the three verification criteria and were deleted. No site was left in
place beyond the one explicitly excluded by the dispatch (`# --- the real open`, line 399,
untouched).

## Files touched

- `.claude/skills/harness/bin/test-gh-sync.py` (only file changed; no other file touched)
