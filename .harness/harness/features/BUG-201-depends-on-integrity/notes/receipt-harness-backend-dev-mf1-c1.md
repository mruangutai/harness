# Receipt — harness-backend-dev — MF-1 complexity fix (c1)

Task: MF-1 remedy (no plan T-NN; this is a review-gate fix). `task: none`.

## Change

Extracted two private helpers from `_validate_plan_depends_on` in `harness_yaml.py`:
- `_depends_on_entries(t, path)` (line 391) — non-list rejection + returns the coerced entries.
- `_dangling_edges(tasks, known, path)` (line 411) — the per-task/per-entry dangling scan, in the
  same outer-task/inner-entry order as before.

`_validate_plan_depends_on` (line 427) now just builds `known`, calls `_dangling_edges`, and raises
the D-02 aggregate exception. Every message string, the `", "` join, and the call position inside
`validate_plan_doc` (line 343) are untouched. Neither helper name contains
`_validate_plan_depends_on`; each has exactly one call site, inside `_validate_plan_depends_on`.

## code-grade.py — before / after

| function | metric set | before | after |
|---|---|---|---|
| `_validate_plan_depends_on` | cyc/cog/abc | 10 / 14 / 17.4 → grade 3, bar 4, **FAIL, high** | 4 / 1 / 7.3 → **grade 5, PASS** |
| `_depends_on_entries` | cyc/cog/abc | n/a (new) | 4 / 4 / 6.8 → **grade 4, PASS** |
| `_dangling_edges` | cyc/cog/abc | n/a (new) | 4 / 6 / 6.9 → **grade 4, PASS** |

No other record in the file regressed: the pre-existing FAILs (`_validate_plan_tasks` grade 2,
`manifest_domains.walk` grade 2, `_resolve_identity` grade 2, `require_or_bootstrap` grade 3,
all out of scope) are identical before/after except for line-number shift from the insertion.

## Differential probe (behaviour preservation)

Loaded `git show HEAD:.../harness_yaml.py` (pre-refactor) and the edited file side by side,
called `_validate_plan_depends_on` on both with four fixtures. All four message/status pairs were
byte-identical:

1. single dangling (`T-02` → `T-99`): both raise `... depends_on names task ids absent from this
   plan - T-02 to T-99`.
2. two dangling edges (`T-01`→`T-88`, `T-02`→`T-99`): both raise ONE exception naming both, in
   order, joined `", "`.
3. bare-string `depends_on: "T-01"`: both raise `... tasks (T-01) \`depends_on\` must be a list of
   task ids, got 'T-01'`.
4. integer task ids (`1`) with matching string `depends_on: ["1"]`: neither raises.

Probe script and copied original module were written under `/tmp/mf1_probe/` and deleted after the
run; not part of this worktree.

## Nine suites (all `env -u HARNESS_AGENT_TYPE`, from the worktree root)

| suite | exit | result |
|---|---|---|
| `tests/unit/test-plan-depends-on.py` | 0 | 12/12 |
| `tests/unit/test-harness-yaml-corpus.py` | 0 | 16/16 |
| `tests/integration/test-harness-yaml.py` | 0 | all named checks ok |
| `tests/integration/test-plan-merge.py` | 0 | PASS (test-plan-merge.py) |
| `tests/integration/test-check-plan-routes.py` | 0 | ALL PASS |
| `tests/unit/test-factory-claim.py` | 0 | 133/133 |
| `tests/integration/test-gh-sync.py` | 0 | ok (unrelated refuse() cases, no regressions) |
| `tests/integration/test-factory-decompose.py` | 0 | 162/162 |
| `tests/integration/test-check-state.py` | 0 | all named checks ok |

No test file was edited.

## SC-04 grep (superseded — see follow-up below)

`grep -rn "_validate_plan_depends_on" .` (from worktree root) tree-wide: real source matches were
exactly `harness_yaml.py:343` (the one call site, inside `validate_plan_doc`) and
`harness_yaml.py:427` (the one `def`), PLUS two docstring-prose mentions at lines 395/415 that named
the function by literal string inside the new helpers' docstrings. The lead flagged this on
assessment: prose-vs-code adjudication on a grep-only criterion is exactly what the binding ruling
on helper naming was meant to prevent. Fixed in the follow-up section below — the two docstrings no
longer spell the literal name.

## git status

`git -C <worktree> status --porcelain` before this receipt showed only `harness_yaml.py` modified
by me, plus pre-existing sibling-agent activity unrelated to this task
(`feature.json` modified, four `notes/review-*-c1.md` files untracked) — not touched by me, noted
per O-06.

## Files touched by me

- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.claude/skills/harness/bin/harness_yaml.py`
- this receipt
- observations log

## SC-04 prose follow-up (c2)

Reworded the two docstring sentences flagged above so neither spells the literal string
`_validate_plan_depends_on`; both now say "its caller"/"the caller" instead. No executable line
touched — confirmed by `git diff -- .claude/skills/harness/bin/harness_yaml.py`, whose only
non-elided hunks are the two docstring blocks in `_depends_on_entries` and `_dangling_edges`
(the rest of the shown diff is the pre-existing, uncommitted MF-1 refactor itself, since HEAD is
still unmoved and nothing is committed).

**`_depends_on_entries` docstring (line ~395), reworded:**
> Raises the same `PlanSchemaError` its caller has always raised when the value is present but not
> a list — bare-string rationale unchanged: a bare string is legal YAML but not a legal
> depends_on: iterated as-is it would walk CHARACTERS and report phantom missing ids instead of
> the real shape error.

**`_dangling_edges` docstring (line ~415), reworded:**
> Outer loop over tasks in order, inner loop over entries in order — the exact collection order
> the caller has always used, preserved so the D-02 exception below lists pairs in the same order
> as before.

**SC-04 grep, re-run:**

```
grep -n "_validate_plan_depends_on" .claude/skills/harness/bin/harness_yaml.py
343:    _validate_plan_depends_on(tasks, path)
427:def _validate_plan_depends_on(tasks, path):
```

Exactly two lines: the call site and the `def`. No third match anywhere in `harness_yaml.py`.

**code-grade.py, re-run (`env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/code-grade.py
.claude/skills/harness/bin/harness_yaml.py --json`), unchanged from the table above:**

| function | grade | cyc | cog | abc | result |
|---|---|---|---|---|---|
| `_validate_plan_depends_on` | 5 | 4 | 1 | 7.3 | PASS |
| `_depends_on_entries` | 4 | 4 | 4 | 6.8 | PASS |
| `_dangling_edges` | 4 | 4 | 6 | 6.9 | PASS |

All three metrics byte-identical to the pre-follow-up table (docstring text is not graded).
Pre-existing out-of-scope FAILs (`_validate_plan_tasks`, `manifest_domains.walk`,
`_resolve_identity`, `require_or_bootstrap`) unchanged.

**Three suites re-run (each `env -u HARNESS_AGENT_TYPE`, from worktree root):**

| suite | exit | result |
|---|---|---|
| `python3 tests/unit/test-plan-depends-on.py` | 0 | 12/12 |
| `python3 tests/unit/test-harness-yaml-corpus.py` | 0 | 16/16 |
| `python3 tests/integration/test-plan-merge.py` | 0 | all named checks PASS, `PASS test-plan-merge.py` |

No test file edited. The other six suites from the original nine-suite table were not re-run per
dispatch instruction (no executable line changed, already green this cycle) — recorded, not
silently omitted.

`git -C <worktree> status --porcelain` still shows only `harness_yaml.py` modified by me, this
receipt, and the observations log among my own files; `feature.json` and the four sibling
`notes/review-*-c1.md` files remain pre-existing unrelated activity (O-06), unchanged by this pass.
