# Receipt — harness-data-engineer — simplify-eng (SIMPLIFICATION angle)

**Scope:** one commit, `9a30ea5`, all eight tasks. Flag-only — no source file touched.

## Findings

### F-1. Two hand-written refusal branches in `_record_pr` share one literal verbatim, and no test distinguishes them
- **File/line:** `.claude/skills/harness/bin/gh-sync.py:589` and `:597`.
- **Summary:** Both branches print the exact string
  `f"gh-sync: no merged pull request found on branch {branch}"` for two different causes —
  line 589 fires when the `gh pr list` JSON parses to an empty/non-list value; line 597
  fires when exactly one result came back but its `number` field is missing or not a
  clean int. (A third, related branch at line 581 covers a `gh` process failure and
  appends extra detail, so it is already distinguishable — not part of this finding.)
  Confirmed by `grep -n "no merged pull request found on branch"
  .claude/skills/harness/bin/gh-sync.py` → exactly those two lines, byte-identical text.
- **Cost:** two independent hand-written copies of one message for two different
  conditions. If a future edit rewords one (e.g. to add the malformed field's raw value)
  without touching the other, the two causes silently diverge in what the operator sees,
  and nothing catches it: `test-gh-sync.py`'s cases for `record-pr` (`gh-sync.py:1447-1538`
  by current line numbers) assert only `returncode` and `doc.get("pr")`, never stdout
  text, for both the empty-list case (`PR_LIST_JSON: "[]"`, line 1462) and every other
  case — grep of `PR_LIST_JSON` in `test-gh-sync.py` turns up no member-with-bad-`number`
  fixture at all, so the line-597 branch is presently **unexercised by any test**.
- **Alternative:** a single shared early-return (e.g. one local `no_merged_pr()` closure
  or a fallthrough that unifies the two conditions before the print) removes the second
  copy without touching any assertion — nothing in the suite currently pins the two
  messages as distinct, so unifying them costs no coverage.
- **Rank:** later-feature. Not a correctness bug (both paths still refuse to write,
  matching the docstring's stated "same shape" rule), and the qa gate already passed
  45/0 on this diff — this is a duplication note for whoever next touches `_record_pr`,
  not a fix to apply now.

### F-2. `--pr` is parsed with `int()` twice against the same string, once to validate and discard, once to use
- **File/line:** `.claude/skills/harness/bin/gh-sync.py:971` (`main()`'s MF-1 parse-boundary
  check) and `:566` (`_record_pr`'s own `number = int(pr_arg)`).
- **Summary:** `main()` calls `int(pr_arg)` solely to raise `die()` on a non-numeric value
  (result discarded — no variable captures it), then passes the original string `pr_arg`
  through to `cmd_ship`/`record-pr`, which calls `int(pr_arg)` again inside `_record_pr` to
  get the number it actually writes.
- **Cost:** negligible per-call (two `int()` calls on a short digit string, paid once per
  `ship --pr` or `record-pr --pr` invocation — not a hot path). The real cost is a second
  place that must agree with the first on what "a valid `--pr` value" means; today both
  are bare `int()`, so they cannot drift in practice, but the duplication is the kind that
  invites exactly that drift the next time either call site is edited in isolation (e.g.
  to strip a `#` prefix).
- **Alternative:** `main()` already proves `pr_arg` parses; it could pass the parsed
  `int` through to `cmd_ship(..., pr_arg=int(pr_arg))` / `_record_pr(feat_dir, repo,
  int(pr_arg))` instead of the original string, collapsing the two `int()` calls into one.
- **Rank:** later-feature. Same qa-passed caveat as F-1 — flagging for a future touch,
  not proposing a change now.

### Checked and ruled out (no finding)

- **INV-28's `str(pdoc.get("status", "")).split()[:1] != ["Done"]` construct**
  (`check-state.sh:1073`) is not new complexity: the identical pattern
  `str(_fj.get("status") or "").split()[:1] in (["Done"], ["Abandoned"])` already exists
  at `check-state.sh:1295`, confirmed pre-existing via `git log -S` → introduced in
  `514aacd` (#352), well before `9a30ea5`. INV-28 reuses the file's own established
  status-comparison idiom rather than inventing a new one (matches expertise P-08/G-06).
- **Task-id citations added to comments** (`(T-02, FEAT-26)`, `(T-03, FEAT-26)` etc. at
  `gh-sync.py:156, 288, 321, 370-371, 390`) match a citation convention already present
  in the same file before this commit — `git show 9a30ea5^:.claude/skills/harness/bin/gh-sync.py
  | grep -nE '\(T-[0-9]+/FEAT|\(FEAT-[0-9]+'` returns pre-existing citations
  (`(T-01/FEAT-23)`, `(FEAT-18)`, `(FEAT-24 T-04)`, `(FEAT-03 B-1)`) at lines 6, 8, 24, 29,
  107, 276, 292, 312, 434, 656, 694, 726, 757, 795. These are present-tense statements of
  fact carrying a provenance tag, not narration of "what changed" — no finding.
- **The exactly-one rule's four refusal shapes** (zero merged, two-or-more merged, unset
  branch, non-integer `--pr`) are one coherent rule spelled across genuinely different
  guard positions: `--pr` is validated at the CLI parse boundary (`gh-sync.py:967-973`,
  by design — MF-1's own comment states this keeps `_record_pr`'s never-die contract for
  its internal caller `cmd_ship`), while the branch-derived zero/two-or-more cases are
  guarded inside `_record_pr` itself because they depend on a live `gh` call `_record_pr`
  owns. Splitting validation across the CLI boundary and the function body is a deliberate
  boundary, not four independently invented shapes — no finding beyond F-2 above.
- **Guard clauses in `_record_pr`** (`doc` unreadable, `doc` not a dict, `branch` unset)
  are not caller-pre-filtered dead code: the standalone `record-pr` CLI subcommand
  (`gh-sync.py` main() dispatch, `elif cmd == "record-pr": _record_pr(feat_dir, repo,
  pr_arg)`) calls `_record_pr` with no prior read of `feature.json` at all, so every guard
  is live on that path even though `cmd_ship`'s own prior `load_recorded()` call makes some
  of them practically unreachable on the `ship` path specifically. Checked per G-02 —
  not flagged.
- **The eleven backfilled `feature.json` diffs** are spelled identically across all
  eleven files: `git show 9a30ea5 -- <path>` for each of FEAT-01, FEAT-02,
  FEAT-03-subissue-mirror, FEAT-04-decisions-index, FEAT-05-pyyaml-file-parsers,
  FEAT-08-remove-cost-tracking, FEAT-10-software-factory, FEAT-20-migration-detector,
  FEAT-21-features-layout-migration, FEAT-22-docs-layout-migration, FEAT-23-ship-flow-fixes
  shows only `-  "pr": null,` / `+  "pr": <int>,` (three of the eleven — FEAT-20, -21, -22
  — additionally normalize a missing trailing newline on the closing `}`, unrelated to
  the `pr` key). No spelling divergence across the eleven.
- **`cmd_closes`'s rendering path** has no conditional inside the function body at all
  (`gh-sync.py`, `def cmd_closes`: a `load_recorded` call followed by one `for n in
  rec["source_issues"]: print(...)` loop). The only conditional near it is `main()`'s
  ordinary command dispatch (`if cmd == "closes": ...; return`), not a construct with a
  single reachable branch. No finding for item 3.
- **DEC-200's text, the signed plan/BRIEF, and DEC-186's open scope question** are out of
  scope per this dispatch's explicit rulings — not re-examined.
