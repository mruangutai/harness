# Receipt — harness-dev-ops — T-10 (c1)

## Result

`tests/manual/probe-issue-types.py` written, executable, host-only live probe.
Verify passed against the real GitHub API for the configured repo
`mruangutai/harness`; default invocation produced `CAPABILITY ABSENT`, matching the
intent's stated expectation for that repo at eb9d044. Nothing was created anywhere.

## Live finding (not mine to fix — reporting, not editing)

`gh_issue_types.capability_query_args(repo)` builds a `gh api graphql` call whose
owner/name already travel as GraphQL variables. `gh-sync.py:detect_issue_types`
(line 923, landed under T-01/T-04) appends `["--repo", repo]` to that same call.
Against the real `gh` CLI on this host (2.92.0) `gh api graphql --repo ...` fails
outright: `unknown flag: --repo`. That failure is currently invisible because
`test-gh-sync.py` exercises it only against a fake `gh` that accepts any flag —
exactly the "fixture-derived pass would make the one live gate a no-op" risk this
task exists to catch, except it caught it in a sibling file rather than in this one.
My probe never appends `--repo` to the graphql call (see the comment on `_classify`
in the script) and gets a correct real answer. I did not touch `gh-sync.py` — out of
my non-goals and it carries T-04's in-progress edits. Raised as `Q1` below.

## Verify — run verbatim, full output

```
$ py=$(command -v python3)
$ repo=$("$py" -c "import json; print(json.load(open('.harness/harness.json'))['github']['repo'])")
$ out=$("$py" tests/manual/probe-issue-types.py); rc=$?
DEFAULT_OUT: probe-issue-types: CAPABILITY ABSENT mruangutai/harness declares no native issue types
DEFAULT_RC: 0
$ skip=$(env PATH=/usr/bin:/bin "$py" tests/manual/probe-issue-types.py); rc=$?
SKIP_OUT: probe-issue-types: SKIP gh not on PATH (mruangutai/harness)
$ echo "probe verdict names $repo, creates nothing, and skips without gh"
probe verdict names mruangutai/harness, creates nothing, and skips without gh
```

Full script exited 0 in both invocations; grep assertions for exactly-one-verdict-line,
repo-naming, "creates nothing", and the gh-absent SKIP all passed (no `exit 1` branch
of the verify fired).

## Nothing created

- Default invocation only ran the read-only `gh api graphql` capability query
  (no `--repo` flag, since it isn't valid there — see above) against
  `mruangutai/harness` and printed the verdict. No issue, no comment, no label,
  no mutation of any kind.
- `gh issue list --repo mruangutai/harness --state all --search "probe-issue-types"`
  returns zero matching issues.
- `git status --porcelain` from the worktree root shows exactly one untracked file
  under my control, `tests/manual/probe-issue-types.py`; every other entry belongs
  to already-landed sibling tasks (T-01 through T-09, T-11) per the dispatch's
  "already landed" list.
- The opt-in `--create-in` path (section 6 of the intent, LIVE PASS / creates a
  throwaway issue) was written but never invoked — the verify does not exercise it
  and neither did I. It is unverified by any automated gate, exactly as the intent
  says: "no automated gate exercises --create-in".

## Scope

Only file written: `tests/manual/probe-issue-types.py` (new, executable). No edit to
`.harness/harness.json`, `gh_issue_types.py`, `gh-sync.py`, or any test. Nothing
staged, nothing committed.
