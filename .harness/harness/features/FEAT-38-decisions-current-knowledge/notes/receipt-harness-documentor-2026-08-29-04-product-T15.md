# Receipt — T-15 — rewrite documentor repository-tier Expertise P-01

**BLUF.** P-01 in the REPOSITORY-tier file `.harness/harness/expertise/harness-documentor.md` is
replaced: it no longer teaches where to place an appended correction inside a decision's section, it
now mandates rewriting the falsified entry in place while keeping the disproved claim as one undated,
unattributed clause. Every substantive clause of T-15's `verify:` passes. **The `verify:` block as
written in `plan.yaml` cannot pass**: its last gate invokes `check-expertise.sh` with no argument,
which is a usage error (exit 2) by the script's own contract, so the block exits 1 regardless of
file content. Observed exit status of the block run verbatim: **1**. This is a plan defect, not a
content failure — raised as Q1.

## The new P-01, in full

```
- P-01: WHEN a decision in `.harness/harness/docs/DECISIONS.md` proves wrong DO rewrite that entry
  in place to state current truth, and keep the falsified claim inside it as one undated,
  unattributed clause marked measured-false — without that clause the next reader re-proposes what
  the tree already disproved.
```

44 words (cap 50). File is 29 lines (repository budget 40).

## Evidence

Run from inside the worktree; `git rev-parse --show-toplevel` resolved to the worktree.

| Clause | Observed |
|---|---|
| `grep -qi 'amendment'` on the file | exit 1 — token absent file-wide, so `&& exit 1` does not fire |
| `grep -qE '^- P-01: WHEN '` | exit 0, matches line 4 |
| `grep -qE '^- P-02: '` | exit 0, matches line 8 |
| `check-expertise.sh` **with no argument** (as the plan writes it) | exit 2, prints `usage:` → block exits 1 |
| `check-expertise.sh "$E"` (the check the clause intended) | exit 0, `OK .harness/harness/expertise/harness-documentor.md` |
| whole `verify:` block, verbatim | **exit 1** (cause: the argumentless invocation above) |

Checker non-vacuity: `python3 .claude/skills/harness/bin/test-check-expertise.py` → 22/22 pass,
including `case3: token + real violation exits 1` and `case5: 41-line repository-form file over
budget`. The checker is shown rejecting malformed input, so its `OK` is evidence. (A scratch broken
copy was not writable — `check-domain.sh` correctly denies the documentor any path outside its
domain, so the unit test stands in for the hand-built negative control.)

Diff discipline, from `git diff -U1` on the target:
- one hunk, `@@ -3,6 +3,6 @@`, four lines out / four lines in — the whole of old P-01 for the whole
  of new P-01. P-02 appears as an unchanged context line; no `G-` or other entry line is touched.
- Worktree tracked modifications: `.harness/harness/docs/DECISIONS.md`,
  `.harness/harness/expertise/harness-documentor.md`, `.../plan.yaml`. Only the Expertise file is
  mine; the DECISIONS.md and plan.yaml changes were present at spawn (T-01–T-04 and status fields).
- `git -C /Users/molchairuangutai/GitHub/harness status --porcelain --untracked-files=no` → 0 lines.
  No tracked file in the MAIN checkout changed.
- Nothing committed.

## Notes for the reader

- The tier trap is real and worth recording: `.harness/expertise/harness-documentor.md` (craft) and
  `.harness/harness/expertise/harness-documentor.md` (repository) both carry a `P-01`, and only the
  repository one concerned placement. `notes/reconciliation-plan.md` names the craft path; it is
  wrong, and the craft P-01 (about grepping handed-down anchors) is untouched.
- New entry added: none. Nothing cites this feature or issue 615 — the file's
  `FEATURE_TOKEN_RE` gate would reject it anyway, and a rule is not an incident record.
- No clause of the `verify:` block tests the *substance* of the new rule: three greps test literals
  and the checker tests format. That the rule states rewrite-in-place plus a surviving undated
  clause is covered only by reading it — the text above is the artifact for that reading.
