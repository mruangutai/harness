# Receipt — T-07 — record the boundary rule in DECISIONS.md

**DEC-193 is appended at the end of `docs/harness/DECISIONS.md` (79 appended lines, heading at line 5687) and
the index is regenerated with its ruling hand-written. Verify passes at exit 0. Nothing is staged or
committed.**

Files in the working tree: `docs/harness/DECISIONS.md`, `docs/harness/DECISIONS-INDEX.md`.
`git diff --stat docs/` — `DECISIONS-INDEX.md | 1 +`, `DECISIONS.md | 79 +++`, 80 insertions, 0
deletions. Hunk headers (`git diff -U0 docs/`): `@@ -210,0 +211 @@` and `@@ -5685,0 +5686,79 @@` —
one appended row, one appended entry, no other row or line touched.

## Verify command output, verbatim, and its exit status

Command run from `/Users/molchairuangutai/GitHub/harness`. The chain up to and including
`test-gen-decisions-index.py` is byte-identical to `plan.yaml:927`; the trailing
`; echo "VERIFY_EXIT=$?"` is mine, appended only to capture the exit status this dispatch requires.
Because the chain is `&&`-joined, that value is the first failing step's status or the final test's
`0`:

```
shasum docs/harness/DECISIONS-INDEX.md > /tmp/feat17-idx-a && python3 .claude/skills/harness/bin/gen-decisions-index.py && shasum docs/harness/DECISIONS-INDEX.md > /tmp/feat17-idx-b && diff /tmp/feat17-idx-a /tmp/feat17-idx-b && python3 .claude/skills/harness/bin/test-gen-decisions-index.py; echo "VERIFY_EXIT=$?"
```

Terminal output:

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_supersession_declared_in_body_prose_is_harvested
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
VERIFY_EXIT=0
```

`diff` printed nothing (the index is a fixed point of the generator) and the shasum/gen steps printed
nothing, which is why the block starts at the unit test's first `ok` line.

## Second generator run (the ruling is a fixed point)

```
python3 .claude/skills/harness/bin/gen-decisions-index.py; echo "GEN2 EXIT=$?"
GEN2 EXIT=0
grep -n "DEC-193" docs/harness/DECISIONS-INDEX.md
211:- DEC-193 @5687 [worktree,domain,map,state] refs: DEC-150 DEC-151 DEC-153 DEC-174 DEC-180 DEC-189 :: Exactly two locations hold code under harness authority; any other checkout cannot be created, written into, or host a governed session; one shared module decides both write routes, divergences recorded.
```

The hand-written ruling survived regeneration unchanged. No `⚠ RULING PENDING` remains on disk.

## The exact DEC-193 index row I hand-wrote

Only the text right of ` :: ` is mine; everything left of it is generated:

```
Exactly two locations hold code under harness authority; any other checkout cannot be created, written into, or host a governed session; one shared module decides both write routes, divergences recorded.
```

30 words, 174 non-whitespace characters — inside `test-gen-decisions-index.py`'s 30-word cap and
20-character floor (`test_committed_index_is_complete_and_within_budget`). The index is 211 lines
against its 260-line budget.

## Where the three divergences and the `--resolve` note appear

Answering the intent clause *"What did NOT converge, said plainly…"* (`plan.yaml:947-959`). All four
sit in DEC-193's section beginning **"What did NOT converge, said plainly so a later reader does not
take it for drift this rule failed to close."**, which opens by stating that the requirement commits
to one shared **implementation**, not to identical verdicts.

1. **DEC-153's Bash-route blanket allow** — first bullet of that list: "The Bash route keeps
   DEC-153's blanket allow for governed agents writing under `.claude/worktrees/`, which the Write
   route does not have."
2. **No product-base domain enforcement on the Bash route outside the harness root** — second
   bullet, including why the outside-repo pass-through was narrowed rather than dropped (D-07).
3. **The PyYAML bootstrap-grant divergence** — third bullet, named as chosen in the 2026-08-11
   re-scope, with the mechanism quoted as the condition `if _run_domain and not _no_parser` rather
   than a plan-time line number, and closing "The Bash route is deliberately not weakened to match".
4. **The `--resolve` note** — its own paragraph immediately after that list: "`check-domain.sh
   --resolve` answers from inside an out-of-place worktree even though the hook now refuses writes
   there", with INV-25 named as the loud signal.

The index ruling carries no parity claim either: it says "one shared module decides both write
routes, divergences recorded".

## How the one-implementation claim is scoped, in both directions

Answering `plan.yaml:970-978`. The paragraph **"What the one-implementation claim rests on, stated no
wider than the evidence."** states, in one place:

- **Root-side, kept:** the mutation edits the named legitimate-location constant in an isolated copy
  of `harness_boundary.py`, one identical payload's verdict flips on BOTH routes, and because
  `CLAUDE_PROJECT_DIR` is pinned inside the worktree the flip is observed through the **ROOT-SIDE**
  check and only there — "direct evidence that the root-side rule has one implementation, and it is
  the strongest evidence this rule carries".
- **Target-side, narrowed:** "covered by behavioural cases on both routes and is **NOT**
  mutation-proved", closing with "Neither half may be widened into the other, and narrowing the claim
  does not drop the root-side proof."

## Line numbers deliberately not copied from the intent

The intent cites `check-domain.sh line 676` for the `domain_check` gate. At HEAD that call is
`if _run_domain and not _no_parser:` at `check-domain.sh:534`; line 676 is inside an unrelated
docstring. The entry states the quoted condition and the mechanism instead of the integer, so the
claim is true and stays true. Re-verified at HEAD for the entry's other present-tense claims:
`harness_boundary.classify` and `worktree_owner` exist (`harness_boundary.py:232`, `:359`); the Bash
route's root-side check is at `bash-write-guard.sh:128`, ahead of its `if _no_parser` exit at `:490`;
the `--resolve` branch exits at `check-domain.sh:255`, before `_governed` is computed at `:271`.

## Open

- Not committed, not staged, per the dispatch. `plan.yaml` untouched — T-07 `status:` is still
  `pending` and is the dispatcher's to flip.
