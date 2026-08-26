# T-14 — stale review_sha detection (issue #867)

T-14 is appended; the plan carries 14 tasks and 12 decisions, `check-plan-routes.py` exits 0,
`source_issues` reads `[845, 867]`, and both approval blocks still read `pending`.

## The defect

`check-state.sh` INV-6 (`.claude/skills/harness/bin/check-state.sh` circa :221-229, inside the
`feature.json` loop that opens at :177) tests only that `review_sha` is present and not a
`harness_yaml.PLACEHOLDER_UNSET` value. A pin that resolves but no longer matches the reviewed text
passes. Measured live on FEAT-41: `review_sha: e5afc19` against a `plan.yaml` last committed at
`c056f49`, 54 insertions and 9 deletions later, with no GAP-7 and no INV-6 line emitted.

An absent pin says nobody reviewed this. A stale pin asserts a review that did not cover the text,
and is byte-identical in shape to a true one.

## INV-32, not a second INV-6 finding

INV-6 asserts a pin exists; the new check asserts the pin is current. Different preconditions —
INV-6 needs only `feature.json`, INV-32 needs a git work tree and a plan file — hence different
silences. One number would put two fail-open surfaces behind one grep-able string, and six existing
cases in `test-check-state.py` assert on INV-6's exact text. INV-32 is free: absent from
`check-state.sh`, and `check-plan-routes.py`'s invariant-collision scan reports no other unbuilt
feature claiming it (checked at `ee66ae2`).

No top-level `invariants:` key was added to `plan.yaml`. The merge tool refuses a differing
top-level key (`MergeRefusal(7)`, step-8 branch at `plan-merge.py:284-297`), and the collision scan
infers the claim from the `INV-32` tokens in T-14's `intent:` via `INV_TOKEN_RE`
(`check-plan-routes.py:647`). If a second feature later claims 32, add the declaration then.

## Byte comparison, not commit comparison

`git show <review_sha>:<path>` bytes against the working copy's bytes. A commit-equality
implementation reports two false positives — a plan changed and changed back, and a plan reviewed
before an unrelated commit landed on the path. Case `(inv32.b)` is built as the revert shape
(X, Y, X, pin the first commit) precisely so a commit-equality implementation reds it.

The path must be relative to `git rev-parse --show-toplevel`, not to `root`: `root` is
`CLAUDE_PROJECT_DIR` and is not guaranteed to be the repository top.

## Placement

`check-state.sh` is opened by T-02, T-04, T-06, T-07; `test-check-state.py` by T-02, T-04, T-06,
T-07, T-11. T-07 is the last on the script, T-11 the last on its test (it deletes a unit), so
`depends_on: [T-07, T-11]` puts T-14 after every task that opens either file and collides with
none. T-14 does not depend on T-13 and never names the pre-rename writer, so it is correct
whichever side of T-13 it runs.

## Open items

- The trace is `REQ-07` and it is a stretch — see the DIGEST for the REQ/SC text I recommend and
  did not write. The BRIEF was not edited this cycle.
- Four deliberate silences (no git tree, unresolvable sha, no plan file, no validator run) are
  fail-open by choice. The rest of `test-check-state.py` staying green is the regression net
  against over-firing.
