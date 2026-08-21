# FEAT-30 simplify pass — SIMPLIFICATION angle — harness-data-engineer

Read-only review of diff `49c528a..fbb3bc0`. Four new files inspected in full:
`.claude/skills/harness/bin/{feature-worktree.py, expertise-merge.py,
test-feature-worktree.py, test-expertise-merge.py}`. No edits applied.

## Checks performed (so a low finding count reads as coverage, not silence)

- Read `expertise-merge.py` end to end; traced `compute_union`, the lock
  acquire/release path, and both exit-7/exit-8 sites against
  `test-expertise-merge.py` cases 4 and 5.
- Read `feature-worktree.py` end to end; traced `dest_for`, `resolve_repo`,
  `cmd_create`, `cmd_list`, `cmd_remove`'s three gates.
- For every module-level "mutation-only" constant (`UNION_APPLY`,
  `REFUSE_ON_DIRTY`, `REQUIRE_LANDED`) I checked the claim in the file's own
  comment ("a test mutates this by name") against `plan.yaml` T-06/T-02 verify
  blocks rather than trusting the comment — confirmed load-bearing in both
  cases (`plan.yaml:1032-1043` for T-06, `plan.yaml:460-467` for T-02). Not
  reported as simplification candidates.
- Empirically checked the minimum length of a `git status --porcelain` line
  (fresh throwaway repo, one untracked 1-char filename): confirmed minimum is
  4 chars (`"?? x"`), never ≤3.
- Grepped the full diff for change-narration language ("now also handles",
  "changed to", "no longer", "instead of") — the three hits found describe
  present-tense behaviour or test fixture state, not the change itself; none
  qualify as narration-style comments.
- Read `test-feature-worktree.py` end to end (873 lines): traced
  `create_four`/`create_one`, `_is_under`, `assert_commit_isolation`,
  `_run_committer`/`_git_retry`'s retry rationale.

## Findings

### F-A — `create_four` duplicates `create_one`'s info-building logic
- **File**: `.claude/skills/harness/bin/test-feature-worktree.py`
- **Line**: `create_four` at 138-158 vs. `create_one` at 306-320
- **Summary**: `create_four` loops over `WT` and inlines the exact same
  "call the CLI, take last stdout line as dest, call `_expected_owner`, build
  an `info` dict of the same five keys" sequence that `create_one` (added
  later in the same file, for the `remove` cases) already encapsulates as a
  function.
- **Cost**: two copies of the owner/segment/branch/repo_key resolution logic
  to keep in sync; a change to the `info` dict's shape (e.g. adding a field)
  requires touching both call sites, and nothing enforces they stay
  identical.
- **Alternative**: rewrite `create_four` to call `create_one(fx, repo, fid)`
  per entry, keep the existing `check(...)` call using the returned `r`, and
  store the returned `info` in `created[fid]`. Preserves every existing
  assertion string and every `check()` call verbatim — this is a call-site
  consolidation, not an assertion change.
- **Severity**: low. **Apply marker**: `apply-candidate`
  (`test-feature-worktree.py` is in the apply-permitted set).

### F-B — `_status_paths`'s short-line fallback is unreachable for real `git status --porcelain` output
- **File**: `.claude/skills/harness/bin/feature-worktree.py`
- **Line**: 199 — `rest = line[3:] if len(line) > 3 else line.lstrip()`
- **Summary**: `git status --porcelain`'s line format is always two status
  characters, a space, then a path of at least one character — minimum
  4 chars. Verified empirically (fresh repo, one untracked 1-char-named file
  → `"?? x"`, length 4). The `else` branch (`line.lstrip()`, a different
  parse of the same line) can only fire on a line git itself never emits.
- **Cost**: an extra conditional a reader must resolve on every read of this
  function, defending against an input shape that doesn't occur; no test in
  `test-feature-worktree.py` constructs a ≤3-char status line, so the branch
  is neither exercised nor asserted on.
- **Alternative**: `rest = line[3:]` unconditionally. I could not rule out
  every conceivable porcelain edge case (e.g. an exotic quoting mode) with
  100% certainty from one empirical probe plus a format read, so I am not
  fully confident this is risk-free — flagging at low severity rather than
  asserting it outright.
- **Severity**: low. **Apply marker**: `apply-candidate`.

### F-C — `compute_union`'s within-proposal dedup path has no test constructing that input (missing test case, not an apply)
- **File**: `.claude/skills/harness/bin/expertise-merge.py`
- **Line**: 127 (`seen = set(base_by_id)`), 133-134 (`if eid not in seen:
  merged_list.append(...)`)
- **Summary**: once an id's already in `base_by_id` the `continue` on line
  ~129-131 handles it, so by the time execution reaches `if eid not in seen`,
  `eid` is guaranteed absent from `base_by_id`. The only case that guard still
  discriminates is a **single proposal file** listing the same
  section+id twice with the same or different text — the second occurrence
  is silently dropped rather than raising a conflict (a divergent second copy
  in the SAME proposal is not routed through the conflict path at all, only
  divergence against the base is).
- **Not an apply**: removing the guard would not simplify safely — it is the
  only thing stopping a duplicated-in-one-proposal id from being appended
  twice — and per this dispatch's scope, a finding whose only remedy is a new
  test case is not a simplify apply.
- **Missing test case**: a proposal file containing the same section+id twice
  with *different* text, asserted to either exit 7 (routed through the same
  divergence check the base-vs-proposal comparison uses) or silently keep the
  first occurrence — whichever `check-expertise.sh`'s own semantics require.
  Currently untested either way.
- **Severity**: info. **Apply marker**: `backlog-only` (names a coverage gap,
  not a code change).

## Explicitly not re-reported (already settled per dispatch)
F-1, F-2, F-4, F-5, F-6, and the plan-surface A-1/A-2/A-5/A-6 rows — none
re-derived here.

## Explicitly checked and NOT flagged
- `UNION_APPLY`, `REFUSE_ON_DIRTY`, `REQUIRE_LANDED` — each is the target of
  an explicit build-time mutation red-proof in `plan.yaml`'s T-06/T-02
  `verify:` blocks; not dead code despite always being `True` in the shipped
  source.
- Exit codes 7 and 8 in `expertise-merge.py` — each reachable (cases 4/5 in
  `test-expertise-merge.py`), distinct, individually asserted, and their
  ordering (conflict-check before cap-check) is forced by `plan.yaml`'s
  numbered algorithm steps (T-06 intent, steps 4 then 5), not a code choice.
- `cmd_list`'s `except ValueError: continue` around `os.path.commonpath` —
  same commonpath idiom family as settled F-6; not filed separately to avoid
  double-counting the same site family.
- The continuation-line guard in `parse_expertise`
  (`current is not None and sections.get(current)`) — the second conjunct is
  not redundant with the first: `sections.get(current)` is falsy exactly when
  the section has zero entries yet, which is the real case this guard exists
  to exclude (a continuation line with nothing above it to continue).
