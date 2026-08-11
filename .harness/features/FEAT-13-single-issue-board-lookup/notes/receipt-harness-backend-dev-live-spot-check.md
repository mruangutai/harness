points_used: 1
item_id_match: yes

# T-02 live read-only lookup cost check

Date: 2026-08-10

## Preflight (proving the right code is under test)

- pwd: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup
- `grep -c 'def issue_board_item_id' .claude/skills/harness/bin/factory_gh.py` -> 1
- factory_gh.__file__ (printed in the same python3 -c invocation as the null/lookup calls):
  /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup/.claude/skills/harness/bin/factory_gh.py
- Fleet repo string used (from `.harness/factory/fleet.yaml`, `repos[0].name`): `mruangutai/harness`
  (matches the plan's example literal; confirmed by reading the file, not assumed).

## Issue chosen

Issue #216, board 3, owner mruangutai. Chosen because the plan named it as a reasonable default.
Checked it is not part of in-flight factory work: grepped `.harness/features/` for "216" — hits are
all in closed/historical features (FEAT-08, FEAT-04, FEAT-11, FEAT-10, FEAT-09, FEAT-05, FEAT-06) and
in this feature's own plan/notes (FEAT-13, which names #216 as the example issue). None of the
currently-active flows named in the dispatch (FEAT-12, FEAT-14/#204, FEAT-15/#239) reference #216.
On the live board, issue #216's own item is status "Done" with a linked, merged PR (#222) — it is
settled, not in-flight. Not re-rolled after the fact.

## Null control (before the measured window, nothing between the two reads)

- null1 = 1
- null2 = 1
- null delta = 0

The null delta is 0, so ambient board traffic did not perturb the rate_limit counter in this window;
a nonzero delta across the measured window below is attributable to the lookup call itself, not to
concurrent traffic landing between two adjacent reads.

## Round 1

- r1_base (gh api rate_limit --jq .resources.graphql.used) = 1
- lookup: `python3 -c "import sys; sys.path.insert(0, '.claude/skills/harness/bin'); import factory_gh; print(factory_gh.issue_board_item_id('mruangutai/harness', 216, 3))"`
  -> returned item id: PVTI_lAHOAAases4BfZ9Zzg2AMPA
- r1_after = 2
- r1_delta = 1

No other `gh` call was made between r1_base and r1_after other than the single lookup.

## Round 2

- r2_base = 2
- lookup (same command, same issue, re-run): returned item id: PVTI_lAHOAAases4BfZ9Zzg2AMPA
- r2_after = 3
- r2_delta = 1

No other `gh` call was made between r2_base and r2_after other than the single lookup.

Both rounds agree: delta = 1 in each. points_used: 1, taken directly from the agreeing pair — no
judgment call needed since the two rounds did not disagree.

## Step 4 — reference id, obtained AFTER both rounds' second readings (outside the measured window)

Exact command used:
```
gh project item-list 3 --owner mruangutai --format json --limit 200
```
then filtered in Python for the item whose `content.number == 216`.

Result: item id `PVTI_lAHOAAases4BfZ9Zzg2AMPA`, content.number 216,
content.url https://github.com/mruangutai/harness/issues/216, status "Done".

This matches the id the helper returned in both rounds exactly: PVTI_lAHOAAases4BfZ9Zzg2AMPA.

item_id_match: yes.

## Cross-check against the two previously recorded (conflicting) artifacts

Both prior artifacts share the leading `PVTI_lAHOAAases4Bf...` prefix per the plan's framing. This
live step-4 read returned `PVTI_lAHOAAases4BfZ9Zzg2AMPA`, which is the id the shipped helper also
returned in both rounds — i.e. the live reference and the helper agree with each other regardless of
which of the two prior artifacts either one matches. This task derived the reference live rather than
trusting either artifact, per the plan's instruction; no further reconciliation of the two historical
artifacts was attempted (out of scope for T-02).

## SC-10 bar

points_used = 1, which is at most 5. Bar met, both rounds, no softening needed since both readings
already came out favorably — the receipt reports both raw pairs above rather than a single preferred
number.

## Raw readings, restated together for auditability

- null1=1, null2=1, null_delta=0
- r1_base=1, r1_after=2, r1_delta=1
- r2_base=2, r2_after=3, r2_delta=1

## Bounds observed

No board mutation was made. No `factory_claim`, `factory_land`, or `factory_decompose` was run
against the live board. The only `gh` calls made were: two null-control rate_limit reads, two
paired rate_limit reads bracketing the two lookup rounds, and the one step-4 item-list read taken
after both rounds completed.
