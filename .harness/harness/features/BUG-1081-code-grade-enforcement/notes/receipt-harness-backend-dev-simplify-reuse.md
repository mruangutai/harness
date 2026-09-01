# REUSE angle — BUG-1081 code-grade enforcement

Verdict: one real finding. Everything else checked in the dispatch's "particular things"
list came back clean — recorded below with the evidence, not just asserted.

## Finding 1 — `_load_test_kinds(root)` spelled twice in one diff, one fails open

- **file/line**: `.claude/skills/harness/bin/code-grade.py:42-44` and
  `.claude/skills/harness/bin/validate-digest.py:686-698`
- **summary**: both files define a function named `_load_test_kinds(root)` that reads
  `<root>/.harness/harness.json` and returns its `test_kinds` mapping — same name, same
  file, same key, two independent bodies, both **added by this diff** (confirmed via
  `git diff <merge-base>..HEAD -- code-grade.py`: `+def _load_test_kinds(root):` at line
  22 of that diff; validate-digest.py's copy is likewise new, part of the T-01
  BUG-1081 work).
- **cost**: they have already diverged on day one, not hypothetically. `code-grade.py`'s
  version (`json.load(stream)["test_kinds"]`) raises a raw `KeyError`/`FileNotFoundError`
  straight out of `main()` on a missing file or missing key — uncaught, since `main`'s
  `except ValueError` doesn't catch either. `validate-digest.py`'s version fails
  *closed with a named repair* (`(None, "<path> could not be read (...)")` /
  `(None, "<path> carries no test_kinds policy...")`) per this feature's own D-05
  refuse-with-a-named-repair contract. A future edit to harness.json's schema, or a
  future hardening of one loader's error handling, has to be remembered and applied to
  the other by hand — nothing forces it, and the one silently missed regresses to a
  crash on one call path while the other keeps refusing cleanly.
- **alternative**: give `code_grade.py` — the seam both files already import from
  (`from code_grade import classify, commit_oid, gated_set` in validate-digest.py;
  `import code_grade` in code-grade.py) — the one `_load_test_kinds(root)`, with
  validate-digest.py's fail-closed-with-repair behavior (it's the stricter of the two
  and already matches this feature's own error-handling convention), and have both
  callers import it. `code_grade.py` already owns the sibling test_kinds consumer
  (`_is_test_path(relative, test_kinds)`), so the loader belongs next to it, not
  re-derived per call site.
- **nature**: bug

## Checked, clean — the dispatch's specific candidates

- **`code-grade.py` vs `code_grade.py`'s new `classify()` seam**: `code-grade.py` at
  HEAD correctly imports and calls `code_grade.classify(...)` (two call sites, lines 56
  and 103) and defines no local `_is_test`/`_blocks`/`_severity`/`_record`. D-03's "one
  importable seam consumed by both the CLI and the validator" holds. (An earlier pass
  of this same read, before re-verifying against `git show HEAD:... | md5sum`, mistook
  a stale tool-cache snapshot for the current file and nearly reported the opposite;
  ground-truthed against the working tree and HEAD, which are identical here —
  `git status --porcelain` shows no diff on either `code-grade.py` or `code_grade.py`.)
- **`_git_line_or_none`/`_repo_root_for_feature`/`_canonical_review_range`**: no
  existing repo-root-from-feature-dir or generic git-line helper is being reimplemented.
  `harness_boundary.py`'s `resolve_root(bin_dir)` resolves root from the *script's own
  install location*, a different input shape (`bin_dir` vs `feature_dir`) that only
  coincidentally shares the "four `..` segments" arithmetic — not the same function.
  `_current_branch_or_none` (validate-digest.py:884) already calls
  `_repo_root_for_feature` rather than re-deriving the path itself, so within this file
  the arithmetic is centralized exactly once, not restated.
- **`_is_test_path` in `code_grade.py`**: grepped the full `bin/` tree for a second
  "is this a test path" spelling outside `code_grade.py`'s own `_is_test_path` and
  `code-grade.py`'s `_load_test_kinds` (which only loads the policy, doesn't match a
  path against it). No third spelling found; `check-expertise.sh`'s `classify_tier` and
  `worktree_terminal.classify`/`harness_boundary.classify` are unrelated domain
  classifiers that happen to share the word "classify".
- **Test fixture duplication** (`test-validate-digest.py`'s `_git_quiet`/
  `_init_test_repo`/`_commit_file` vs `test-code-grade-cli.py`'s `git`/`write`/
  `commit`/`make_repo`): both hand-roll a temp git repo + `.harness/harness.json`
  builder. This is real, but it is this codebase's established, repo-wide convention —
  every `test-*.py` in `bin/` is a standalone script with its own fixture helpers, no
  `conftest.py` or shared test-support module exists anywhere in the directory (checked
  across `test-worktree-terminal.py`, `test-check-state.py`, `test-post-merge-sweep.py`,
  etc.), and this diff did not introduce that convention. Flagging it here would
  re-litigate a repo-wide pattern, not a defect this diff created — noted per the
  skill's "note the skip with its reason" rather than raised as a finding.

## Verification

`git -C <worktree> status --porcelain`:
```
 M .harness/harness/features/BUG-1081-code-grade-enforcement/feature.json
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/qa-test-matrix-c1.md
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-backend-dev-simplify-simplification.md
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-dev-ops-simplify-altitude.md
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-orchestrator-reachability.md
```
No source file under review was edited by this read.
