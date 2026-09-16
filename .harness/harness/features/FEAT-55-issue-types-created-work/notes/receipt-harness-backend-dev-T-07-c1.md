# Receipt — harness-backend-dev — T-07 (FEAT-55) — c1

## Task
T-07: write the failing integration test for the factory routes (typing, labels, rerun) —
`tests/integration/test-factory-issue-types.py`. `change_type: scaffolding`. The only file
created is that test; `factory_decompose.py`, `factory_gh.py` and
`tests/integration/test-factory-decompose.py` are unmodified (T-08's job), confirmed by a
scoped `git status --porcelain` (see Verify below — empty for all three).

Verify string cross-checked against plan.yaml's own `T-07.verify` (`plan.yaml:1201-1210`):
identical to the dispatch. No mismatch.

## What the test does
Ten cases (A–J), one bash `FACTORY_GH` fake (Python-free, styled on T-03's `FAKE_GH_TYPES`),
driving real `subprocess` invocations of `factory_decompose.py` against a three-task fixture
(bugfix/config/feature) plus a parent. The fake answers auth, label create, the remote
`.harness/harness.json` contents read (board + optional `github.issue_types` override), the
project field-resolve/item-add/item-edit surface, the `projectItems` recovery query, `issue
create`, `sub_issues`, `blocked_by`, `--jq .node_id` / `--jq .id`, the `issueTypes` capability
query (FAKE_TYPES=absent/available/partial/nobug/failed) and `updateIssue`
(FAKE_TYPE_APPLY=fail) — every call today's unmodified `factory_decompose.py` makes, so every
run reaches step 6+ and exits 0 (or, where a case pre-seeds a `partial` disposition, still
completes instead of crashing).

Each of the 10 cases produced at least one **genuine** failure — not a fixture crash, not an
import error — because today's code has no `typed` schema key, never queries issue types,
never calls `updateIssue`, and never refuses. One artifact was caught and fixed during
verification: the fake's own trailing-newline-to-`\x01` conversion left one `\x01` on every
logged line; `read_log` now strips it, which turned two spuriously-failing "labels unchanged"
control assertions in CASE C into genuine passes (they assert TODAY's real behaviour, not the
absent typed behaviour, so they must pass) — confirmed by rerunning after the fix (30 FAILED,
down from 32, and the two that flipped are exactly the control assertions).

Per-case failure reasons (all real, none a crash):
- **A**: zero `updateIssue` argv exist at all → every per-issue typing assertion fails.
- **B**: `--label chore`/`--label bug` are still emitted today (T-08 must suppress them).
- **C**: zero `^factory: issue types ` diagnostic lines (today prints none).
- **D**: same as A — zero `updateIssue` argv, so no override assertion can pass.
- **E**: no `typed` key exists in `feature.json`'s `factory` block at all, before or after
  either run.
- **F**: same — `typed.parent` is never set to `"adopted"`.
- **G**: same as C — no diagnostic line on a zero-create rerun.
- **H**: the first six checks pass trivially (no `updateIssue` ever fires, so "nothing typed"
  is vacuously true both today and post-T-08) — the case's real teeth is the last check,
  "the tasks that are NOT recorded still get typed", which fails today (0 `updateIssue`
  calls) and is what proves T-08 didn't just refuse to do anything.
- **I**: today's code has no REQ-07 refusal, so it actually creates the parent + 2 remaining
  tasks; every "zero create"/"exits non-zero"/"remnant unchanged" assertion fails. The
  remnant's `typed` entry is additionally wiped by `write_factory`'s whole-block overwrite
  (today's `load_factory` doesn't carry an unknown `typed` key forward at all) — the case
  catches that too.
- **J**: identical shape to I, on the `nobug` capability response with a `full`-disposition
  remnant (no partial-recovery GraphQL needed for this one).

## Verify (verbatim, from the worktree root)
```
python3 -c "import ast; ast.parse(open('tests/integration/test-factory-issue-types.py').read())" || exit 1
for c in A B C D E F G H I J; do
  grep -qF "CASE $c:" tests/integration/test-factory-issue-types.py || { echo "MISSING case $c ..."; exit 1; }
done
for s in IT_feature IT_bug IT_task IT_story updateIssue issueTypes 4242 adopted created partial nobug github.issue_types; do
  grep -qF "$s" tests/integration/test-factory-issue-types.py || { echo "MISSING required assertion string: $s"; exit 1; }
done
python3 tests/integration/test-factory-issue-types.py && { echo "UNEXPECTED PASS: this test must be RED before T-08"; exit 1; }
echo "RED as required - all ten cases present"
```

Output (tail; full per-case ok/FAIL lines omitted here, all reviewed above):
```
...
30 FAILED
RED as required - all ten cases present
OVERALL_EXIT=0
```
The syntax check passed, all ten `CASE X:` markers and all twelve required substrings were
found, `python3 tests/integration/test-factory-issue-types.py` exited 1 (RED, 30 FAILED / 62
checks), and the verify script's own final echo + exit 0 confirms the block's contract.

## Scope check
```
git status --porcelain -- .claude/skills/harness/bin/factory_decompose.py \
  .claude/skills/harness/bin/factory_gh.py tests/integration/test-factory-decompose.py
```
→ empty output. `git status --porcelain -- tests/integration/test-factory-issue-types.py` →
`?? tests/integration/test-factory-issue-types.py` (new, untracked, unstaged).

## Notes for T-08
- `load_factory` currently drops any `"typed"` key from a pre-existing `factory` block (only
  recognized keys — `repo`, `parent`, `issues`, `items`, `edges` — survive the read), and
  `write_factory` writes the in-memory dict back whole. T-08 must extend both the read and
  the write side to carry `factory["typed"]` through, or every remnant-preservation case
  above (E/F/I/J) stays red for a schema reason rather than a behaviour one.
- The `partial`-disposition recovery path (case I) reaches `factory_gh.issue_board_item_id`
  (the `projectItems(first:` GraphQL query) before any refusal could fire under an
  earlier-ordered implementation — T-08's refusal must run before step 5 (`ensure_labels`),
  not merely before the per-task create loop.

## Files touched
- `tests/integration/test-factory-issue-types.py` (created)
