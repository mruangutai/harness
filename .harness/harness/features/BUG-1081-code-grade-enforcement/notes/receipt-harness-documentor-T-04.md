# Receipt — harness-documentor — BUG-1081 T-04

**DEC-209 records the enforcement-ownership ruling; DEC-208 was already taken on `origin/main`.**
One entry appended to `.harness/harness/docs/DECISIONS.md`, one generated index row with an authored
ruling. All five named checks green, index diff empty, nothing committed.

## Number allocation — DEC-208 was NOT free

The expected number was taken. Commands run from `/Users/molchairuangutai/GitHub/harness`:

```
$ git fetch origin main -q
$ git show origin/main:.harness/harness/docs/DECISIONS.md | grep -oE '^## DEC-[0-9]+' | sort -t- -k2 -n | uniq | tail -4
## DEC-205
## DEC-206
## DEC-207
## DEC-208
$ git show feat/BUG-1081-code-grade-enforcement:.harness/harness/docs/DECISIONS.md | grep -oE '^## DEC-[0-9]+' | ... | tail -4
## DEC-204 ## DEC-205 ## DEC-206 ## DEC-207
$ for b in $(git branch -r --format='%(refname:short)'); do ... grep -qE '^## DEC-208 ' && echo "TAKEN on $b"; done
TAKEN on origin/feat/FEAT-50-run-artifact-integrity
TAKEN on origin/main
```

`origin/main`'s DEC-208 is FEAT-50's run-artifact-integrity entry. Max across every remote ref is 208,
so **DEC-209** is the first free number. The gap is intentional and `gen-decisions-index.py` never
asserts contiguity. DEC-208 will arrive on this branch at merge; the branch's index legitimately has
no row for it yet.

## Entry contents — every claim read off the shipped code, not the plan

`.harness/harness/docs/DECISIONS.md`, `## DEC-209 — Mechanical code-grade state is computed by the
digest gate, not trusted from the reviewer` (appended at EOF, so no existing `@line` anchor moved).
Grounded in `.claude/skills/harness/bin/validate-digest.py` at branch tip (T-02, `7c23beb`):

- Recomputation runs for all four enum values on any non-plan review
  (`if code_grade in CODE_GRADE_VALUES and not _is_plan_review(reviewed)`), and a mismatch names the
  expected value (`code_grade_enforcement_error`).
- Canonical range `merge-base(<default branch>, review_sha)..review_sha`, resolved with `git -C root`
  where `root` is `_repo_root_for_feature(feature_dir)` (`_canonical_review_range`).
- Five named refusals verified present: unresolvable `origin/HEAD`, unresolving `review_sha`, no merge
  base, degenerate range (`base_oid == head_oid`) in `_canonical_review_range`; missing/malformed
  `test_kinds` in `_load_test_kinds`; committed `SyntaxError` and any other exception in
  `_classify_canonical_range`, each returning a string, never raising.
- `n_a` iff `reviewed_python_change` reports no `.py` path; deletion-only therefore grades `pass`
  (`_mechanical_code_grade`).
- Import, not subprocess: `from code_grade import classify, commit_oid, gated_set` (line 32).

**FEAT-43 framing checked before transcribing** (P-07/P-15). The pre-fix file at `17a2317` states it
in its own words: `_derived_reviewed_python_change` "is reached only for `code_grade == 'n_a'`;
`pass`/`fail`/`grade_2` never reach this and are never gated on base derivation, so an unresolvable
default branch cannot" brick validation. The dispatch's "that exemption WAS the bypass" is accurate,
and the entry says so.

Refs computed by the generator from body mentions: `DEC-122 DEC-127 DEC-207`. DEC-127 (rejection vs.
crash), DEC-122 (this hook's exit-2 rejection) and DEC-207 (plan-review target) are each load-bearing
in the prose. **DEC-174 was deliberately not cited** — D-03 references it, but it rules on what the
harness may execute, not on where grading logic lives, so the entry does not rest on it.

## Verification — all run in the worktree

```
$ python3 .agents/skills/harness/bin/gen-decisions-index.py
V1 exit=0

$ .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
V2 exit=0
```
V2 emitted **zero bytes**; an empty diff is the pass condition, not a failed command.

```
$ python3 -c "...assert len(ids)==1; assert any(...)"
V3 OK ['DEC-209']
V3 exit=0

$ python3 .claude/skills/harness/bin/test-gen-decisions-index.py
ok - test_row_per_distinct_dec_matches_authority
... 11 tests, all ok, including test_committed_index_is_complete_and_within_budget
TEST1 exit=0

$ python3 .claude/skills/harness/bin/test-check-plan-routes.py
ALL PASS
TEST2 exit=0
```

Index is 208 lines (budget 260). The new ruling is 28 words (cap 30) and well over the
20-non-whitespace-character floor.

**Negative probe — the V3 clause is not vacuous.** Run in-memory against mutated copies (nothing on
disk touched; `mktemp`+redirect is refused by bash-write-guard for this persona):

```
A committed inputs: PASS
B blanked ruling: correctly REJECTED -> no non-empty ruling
C duplicate heading: correctly REJECTED -> heading count 2
```

```
$ git -C <worktree> status --porcelain
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/features/BUG-1081-code-grade-enforcement/plan.yaml
$ git -C <worktree> diff --numstat
1	0	.harness/harness/docs/DECISIONS-INDEX.md
51	0	.harness/harness/docs/DECISIONS.md
1	1	.harness/harness/features/BUG-1081-code-grade-enforcement/plan.yaml
```

`plan.yaml` was ALREADY modified at spawn (its `T-04 status:` line — 1 insertion, 1 deletion) and is
not mine; my diff is the two doc files, both pure additions. Nothing committed. Nothing staged.

## Two things the next reader should know

1. **The dispatch's quoted `verify:` differs from the plan's by notation only.** The dispatch wrote the
   title's em dash as the escape `\u2014` inside the regex; `plan.yaml` T-04 carries the literal `—`.
   Python's `re` resolves `\u2014` to U+2014, so both patterns match the same heading, and the clause
   passes as written in either form. Not treated as a BLOCKED-worthy mismatch; recorded because the
   dispatch demanded a byte-level cross-check.
2. **The main checkout at `/Users/molchairuangutai/GitHub/harness` is on `main` but behind
   `origin/main`** — its `DECISIONS.md` has no DEC-208 and is byte-identical to this branch's copy.
   That is why a number allocated from the local working tree would have collided, and why the
   allocation was read from `origin/main` instead.

## Open question

- Q1 (non-blocking): the *only* automated protection against a wrong-tree edit here was reading
  `git status` in both trees afterwards. A relative-path edit issued while the process cwd is the main
  checkout lands there silently, and a content-derived snapshot tag still matches when the two copies
  are byte-identical. Worth a harness-side guard.
