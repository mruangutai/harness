# Code review — BUG-276 — narrow re-review, pinned SHA a641a5b8 (base 6d969ed3)

## BLUF

PASS. The refactor cost the test none of its proving power. All nine propositions from case27
survive, each read line-by-line at the rewritten site (not inferred from "everything else is
unchanged"), and a live run of the file confirms all nine checks still execute and PASS under
their original names. `case_duplicate_proposal_ids` now grades 5 (cyc1/cog0/ABC3.0); the new
sibling `_assert_case27_ambiguous` grades 3 (cyc6/cog5/ABC25.2) — exactly at, not above, the
test-code bar of 3. No grade-1/blocking function remains in the graded range. `code_grade` for the
mandated range `6d969ed3..a641a5b8` is `grade_2`, not `pass` — the range still contains the
pre-existing `case_u23` at grade 2 (see below); this is correctly non-gating. Scope: this cycle
reviews only `tests/integration/test-expertise-merge.py:1310-1371` (the commit's only code
change); spec compliance and the six SCs are not re-litigated (passed in full at ef8efd99, see c0).

## The nine propositions (test-expertise-merge.py, current file = a641a5b8 content, confirmed
unchanged since: `git diff a641a5b8 0bad9f08 -- tests/integration/test-expertise-merge.py` is empty)

`_assert_case27_ambiguous` at `:1310`. `check(exit_check_name, r.returncode == 11, combined)`
sits at `:1327`, **before** the `if base_sections is not None:` branch (`:1328`) — so the exit-11
assertion is unconditional across all three sub-cases, not duplicated per-branch.

1. **case27a exit 11** — SURVIVES. `case_duplicate_proposal_ids:1345-1351` calls the helper with
   `base_sections=[("Patterns",[("P-01","one")])]`; unconditional check at `:1327` fires. Live run:
   `PASS case27a: duplicate ids exit 11`.
2. **case27a all-four-token message** — SURVIVES, unweakened. `base_sections is not None` →
   branch `:1329-1335` checks `"AMBIGUOUS TARGET" in combined and "section=Patterns" in combined
   and "id=P-02" in combined and "reason=" in combined` as one conjunctive check, byte-identical
   logic to the pre-refactor inline version. Live run: PASS.
3. **case27a destination bytes unchanged** — SURVIVES. `:1336-1337`, same branch, `before` was
   hashed at `:1324` (only when `base_sections is not None`). Live run: PASS.
4. **case27b exit 11** — SURVIVES. Same unconditional `:1327` check, called from
   `case_duplicate_proposal_ids:1354-1360` with `texts=("ALPHA","ALPHA")`. Live run: PASS.
5. **case27b SAME full four-token assertion, not weakened to a substring** — SURVIVES. `case27b`
   also passes `base_sections=[...]` (not None), so it takes the identical `:1329-1335` branch as
   case27a — the same four-token conjunctive check, not a lesser one. This is the exact guarantee
   PF-d6fb0ad9 protects (refusal keyed on duplicated id, not divergent text): the sub-case is
   present, still asserts all four tokens, and the docstring at `:1355` still states the intent
   ("refusal is keyed on the duplicated id, not on divergent text"). Live run: PASS.
6. **case27b destination bytes unchanged** — SURVIVES. Same branch as (3), `:1336-1337`. Live run:
   PASS.
7. **case27c exit 11** — SURVIVES. `case_duplicate_proposal_ids:1363-1368` calls the helper with
   no `base_sections` kwarg → defaults to `None` (`:1310` signature). The unconditional check at
   `:1327` still fires regardless of branch. Live run: PASS.
8. **case27c carries AMBIGUOUS TARGET** — SURVIVES, correctly NOT strengthened beyond the
   pre-refactor single-token check. `base_sections is None` → `else` branch `:1338-1340`: `check(
   message_check_name, "AMBIGUOUS TARGET" in combined, combined)`. Matches the original inline
   `case27c` check exactly (diff shows identical single-token assertion pre- and post-refactor).
   Live run: PASS.
9. **case27c: nothing created at the path** — SURVIVES. `:1340`, same `else` branch:
   `os.path.exists(path) is False`. Confirmed the helper takes no write/hash action for the
   absent-destination case: `before = None` is set unconditionally at `:1322`, and `write_file` /
   the before-hash (`:1323-1325`) sit strictly inside `if base_sections is not None:` — so when
   `base_sections=None`, `write_file` is never called (no base file created) and no before-hash is
   taken. A helper that created the destination on this path would falsify this exact
   proposition; it does not. Live run: PASS.

**Fixture intact.** `write_entries(..., [("Patterns", [("P-02", texts[0]), ("P-02", texts[1])])])`
at `:1326` — both entries are `P-02` under `Patterns` for every call, unconditionally.
Parametrization at the call sites: (a) `("ALPHA","BRAVO")` `:1349`, (b) `("ALPHA","ALPHA")`
`:1358`, (c) `("ALPHA","BRAVO")` `:1366` — matches the spec exactly; no accidental collapse of (b)
into (a)'s shape (they use different `texts` tuples, and the divergent-vs-identical distinction is
the entire point of (a) vs (b)).

**Mechanical grading** (`code-grade.py --base 6d969ed3 --head a641a5b8`, run directly, matches the
Contract's pre-taken measurement exactly):

- `_check_proposal_duplicate_ids` (`expertise-merge.py:116`) — grade 4, PASS (production, bar 4,
  untouched by this commit).
- `_assert_case27_ambiguous` (`:1310`) — cyc 6 / cog 5 / ABC 25.2 — **grade 3, PASS** against
  test-code bar 3.
- `case_duplicate_proposal_ids` (`:1341`) — cyc 1 / cog 0 / ABC 3.0 — **grade 5, PASS**.
- `case_u23` (`tests/unit/test-expertise-ops.py:361`) — cyc 10 / cog 9 / ABC 32.6 — **grade 2**,
  `REASON REQUIRED`. **Not reopened**: this is the same function c0 already found and dismissed
  non-blocking, with a written reason (three independently load-bearing sub-case assertions, not
  accidental branching; same extraction pattern would improve it but is not required to pass).
  Unchanged by this commit — it is still inside the mandated range
  `merge-base(origin/main, a641a5b8)..a641a5b8` because that range spans the whole feature branch,
  not just this fix cycle's own commit, so `code_grade` for the range is `grade_2`
  (non-gating: `RESULT: FAIL` for the function but the run exits clean once reasoned; per protocol,
  grade 2 never blocks the build) — carried forward here to answer the tool's `REASON REQUIRED`
  line, not as a new finding.

Live full-file run: `python3 tests/integration/test-expertise-merge.py` — all 9 case27 checks plus
every other case PASS; file-level `PASS test-expertise-merge.py`.

## Code quality: is `_assert_case27_ambiguous` a good sibling of `_assert_case24_ambiguous`/
`_assert_case25_malformed`, or does the `base_sections is not None` branch serve two shapes badly?

Good sibling, not a bad-smell branch. The two branches reflect a genuine feature difference the
prior helpers never had to represent: case24/25 always operate against an existing base file, so
their helpers never branch. case27's third sub-case is deliberately the absent-destination path
(the commit's own docstring, `:1310-1316`, states this explicitly), and roughly half the helper —
path resolution, entries write, `run_apply`, and the unconditional exit-11 check — is identical
work shared by all three calls. Splitting into two helpers would either duplicate that shared
setup or require a third indirection layer for ~4 lines of divergence per branch. The grade (3,
at bar) and the live-run pass confirm the branch does not conceal a coverage loss. Not a finding.

## Dismissed, with reason (not reopened)

- `case_u23` grade-2 — CLOSED by c0 with a written reason; carried forward only to answer the
  tool's `REASON REQUIRED` line (non-gating med, per protocol), not re-litigated or re-graded here.
- Spec compliance / SC-01..SC-06 — passed in full at ef8efd99 (c0); out of scope this cycle.
- `.claude/skills/harness/bin/expertise-merge.py` `_check_proposal_duplicate_ids` and
  `harness_merge.py` — unchanged by this commit; not re-reviewed.

## Findings

1. **[med, non-gating]** `tests/unit/test-expertise-ops.py:361` `case_u23` — grade 2 (cyc 10 /
   cog 9 / ABC 32.6) against test-code bar 3. `REASON REQUIRED` per the tool: three
   independently load-bearing sub-case assertions (D-08, a unit-level pin the plan's own
   goalcheck panel confirmed reddens pre-fix), not accidental branching — substantive complexity,
   not a defect. Already disposed by c0; not must_fix.

No gating finding. No new must_fix.

```yaml
VERDICT: PASS
DIGEST:
  headline: Refactor of case_duplicate_proposal_ids into _assert_case27_ambiguous preserves all nine case27 propositions verbatim (verified line-by-line, not by exclusion) and clears the grade-1 bar — case_duplicate_proposal_ids now grades 5, the helper grades 3, both at or above the test-code bar; the range's only remaining sub-bar function is the pre-existing, already-dismissed grade-2 case_u23.
  severity_max: med
  findings: 1
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "6d969ed3..a641a5b8"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-276-expertise-merge-duplicate-id/.harness/harness/features/BUG-276-expertise-merge-duplicate-id/notes/review-harness-code-reviewer-c1.md
```
