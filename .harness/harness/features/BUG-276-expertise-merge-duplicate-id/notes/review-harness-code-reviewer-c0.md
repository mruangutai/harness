# Code review — BUG-276 — pinned SHA ef8efd99a28cdabce9ac867c21b895e6cb0ea584 (base 6d969ed3)

## BLUF

FAIL. Stage 1 passes cleanly — all four REQs and six SCs MET, verified against code at the pin.
Stage 2's behavioural hunt (fail-open, bypass, ordering, exit precedence) also found nothing:
the guard is `compute_union`'s first statement (D-03), id-keyed (D-02), and its `MergeRefusal(11)`
propagates through an unwritten `transform()` closure before any tempfile is staged, so both the
existing-file and absent-file refusal paths are structurally byte-identical/no-create. The single
blocker is mechanical, not behavioural: `code-grade.py` over the mandated range
(`merge-base(origin/main, review_sha)..review_sha` = `6d969ed3..ef8efd99`) reports the new
integration test function `case_duplicate_proposal_ids` at **grade 1** against a test-code bar of
3 (ABC 47.9) — a gated, blocking result per `harness-code-risk-grading` and the review protocol's
own instruction to report `code_grade: fail` and file a `high` finding for it.

## Stage 1 — spec compliance

| Criterion | Verdict | Evidence |
|---|---|---|
| REQ-01 (no silent discard, names section+id) | MET | `expertise-merge.py:123-138` `_check_proposal_duplicate_ids`; message line built at `:130-132` includes `section=` and `id=` tokens |
| REQ-02 (refusal leaves destination exactly as before) | MET | `harness_merge.py:143` — `new_bytes = transform(base)` raising means `locked_update` never reaches the `tempfile.mkstemp`/`os.replace` block at `:145-153`; nothing is opened for write |
| REQ-03 (existing outcomes unchanged) | MET | pre-existing `case_add_only_compatibility` (T-02's cited REQ-03/SC-04 evidence, not duplicated); diff never touches the conflict (`:150-151`) or cap (`:156-159`) branches, unchanged below the new guard call at `:139` |
| REQ-04 (exit table matches actual codes) | MET | docstring exit table, `expertise-merge.py:14-19`, lists exactly 0/6/7/8/9/11 — read directly off the worktree file |
| SC-01 (different texts, exit 11, sha256 unchanged) | MET | `test-expertise-merge.py` case27a, `:1311-1327` |
| SC-02 (identical texts, same refusal, keyed on id not text) | MET | case27b `:1330-1345`; guard unpacks `eid, _` — never reads `text` |
| SC-03 (`compute_union` raises MergeRefusal(11) directly, unit-level) | MET | `test-expertise-ops.py` case_u23a/b/c, `:361-413` |
| SC-04 (no regression: add-only 0, divergence 7, cap 8) | MET | pre-existing `case_add_only_compatibility` untouched; conflict/cap branches unedited |
| SC-05 (absent destination, exit 11, no file created) | MET | case27c `:1348-1355`; `os.path.exists(path_c) is False`; structurally guaranteed — `transform` raises before `result[...]` is set |
| SC-06 (exit table lists exactly what `apply` can return, no 10/12) | MET | table has no `10`/`12` line; both codes are raised only on the `cmd_ops` path (`_resolve_replace_or_drop:296`, `_malformed:170`) |

D-01/D-02/D-03 shape checks: `MergeRefusal(11, ["AMBIGUOUS TARGET section=<s> id=<i>
reason=..."])` matches the sibling `_check_base_ambiguity` message shape (`:282-287`); the loop
destructures `eid, _` (no text compare); `_check_proposal_duplicate_ids(...)` is `compute_union`'s
first body line (`:139`), before `order = list(base_order)` (`:140`). No scope creep — diff
touches only the new helper, one call line, two docstring lines, and the two test files' new
cases plus registration.

## Stage 2 — code quality

### Behavioural hunt: clean

- **Bypass:** `compute_union` has exactly one call site in the whole tree —
  `expertise-merge.py:515` inside `cmd_apply.transform` (repo-wide grep) — so no parallel route
  skips the guard. `UNION_APPLY = False` would skip it, but that literal is dead in production
  (docstring `:24-28`) and pre-existing, unrelated test scaffolding.
- **Refusal-to-exit-0 degrade:** none. `MergeRefusal` propagates unmodified through
  `locked_update` (no `except` around the `transform` call, `harness_merge.py:143`) into
  `cmd_apply`'s `try/except harness_merge.MergeRefusal` (`:557-560`), which prints and
  `sys.exit(refusal.code)`s — no fallthrough to the `ADDED`/`sys.exit(0)` tail.
- **Ordering vs. staged mutation:** guard fires before `order`/`merged`/`result` are built and
  before `tempfile.mkstemp` is called — no partial-write or partial-result path exists.
- **Precedence vs. 7/8/9:** 9 runs pre-lock, unaffected; 11 precedes 7/8 inside the lock because
  it is the first statement of the function both fall through — matches D-03's intent.
- **Test binding (D-08 self-check):** case27a/b assert `returncode == 11`, four message tokens,
  and a before/after sha256; case27c asserts `os.path.exists() is False`; `run_apply` shells the
  real CLI (`subprocess.run`, `:102-106`), not a stub. u23a/b/c bind `e.code`, `e.lines[0]`
  prefix and three tokens. All four are behaviour-bound, not name-only greps.

### Mechanical grading — blocking

Ran `code-grade.py --base 6d969ed3 --head ef8efd99a28cdabce9ac867c21b895e6cb0ea584` (the
repository-derived range; matches `git merge-base origin/main ef8efd99` = `6d969ed3`, so the
plan's own `base` is the canonical range here):

- **`_check_proposal_duplicate_ids`** (`expertise-merge.py:116`) — cyclomatic 4, cognitive 6, ABC
  6.9 — **grade 4, PASS** against the production bar of 4.
- **`case_duplicate_proposal_ids`** (`tests/integration/test-expertise-merge.py:1310`) —
  cyclomatic 7, cognitive 2, ABC 47.9, driver **abc** — **grade 1** against the test-code bar of
  3 — **FAIL, high**. The three sub-cases (a/b/c) each inline their own
  write-hash-propose-run-assert sequence; the same file already has an established extraction for
  exactly this shape — `_assert_case24_ambiguous(root, stem, label, what, entry_text,
  extra_checks)` (`:1192-1209`), parametrized and reused by case 24's sub-cases. `case27` does not
  reuse it or an equivalent, so all three ~13-line blocks are duplicated inline; the ABC blowup
  (47.9) is the mechanical signature of that. Concrete cost: a future edit to one assertion
  sequence (e.g. adding a `reason=` check) that is applied to a/b but missed on the third copy
  regresses silently, exactly the copy-paste-divergence failure mode stage 2 exists to catch —
  the existing `_assert_case24_ambiguous` extraction was built to prevent this same drift on the
  sibling `ops` path.
- **`case_u23`** (`tests/unit/test-expertise-ops.py:361`) — cyclomatic 10, cognitive 9, ABC 32.6,
  driver abc — **grade 2** against the test-code bar of 3 — FAIL-but-non-blocking, **med**,
  reason required: three sub-cases repeat a `try/compute_union/except MergeRefusal` block with
  three assertions each; each assertion is independently load-bearing (D-08 — the u23 checks are
  a unit-level pin the plan's own goalcheck panel confirmed reddens pre-fix), so the complexity is
  substantive, not accidental, but the same `_assert_case24_ambiguous`-style extraction would
  clear grade 3 here too. Not gating on its own; noted so the REASON REQUIRED line is answered.

## Dismissed, with reason

- Guard only runs when `UNION_APPLY` is True — pre-existing, dead-in-production, unrelated seam.
- D-09 (no exit-11 row in `harness-distill/SKILL.md`) and D-07 (parse/render silent-drop) — signed
  dead ends per shared context; not re-raised.
- case27b "redundant with u23b" — already litigated and rejected in the plan record
  (PF-d6fb0ad9); not re-opened.

## Findings

1. **[high]** `tests/integration/test-expertise-merge.py:1310` `case_duplicate_proposal_ids` —
   grade 1 (cyclomatic 7 / cognitive 2 / ABC 47.9, driver abc) against test-code bar 3. Extract a
   shared assertion helper mirroring `_assert_case24_ambiguous` (`:1192`) for the three sub-cases
   to bring it back under bar. **must_fix.**
2. **[med]** `tests/unit/test-expertise-ops.py:361` `case_u23` — grade 2 (cyclomatic 10 /
   cognitive 9 / ABC 32.6, driver abc) against test-code bar 3. Non-blocking; reason: three
   independently load-bearing sub-case assertions, not accidental branching — same extraction
   pattern would improve it but is not required to pass.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Spec compliance and fail-open/bypass hunt both clean; blocked solely by a grade-1 test function (case_duplicate_proposal_ids, ABC 47.9) below the test-code bar.
  severity_max: high
  findings: 2
  must_fix: ["tests/integration/test-expertise-merge.py:1310 case_duplicate_proposal_ids is grade 1 (cyc7/cog2/ABC47.9) against test-code bar 3 — extract a shared assertion helper (mirroring _assert_case24_ambiguous:1192) for its three sub-cases"]
  spec_violations: []
  code_grade: fail
  reviewed: "6d969ed3..ef8efd99a28cdabce9ac867c21b895e6cb0ea584"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-276-expertise-merge-duplicate-id/.harness/harness/features/BUG-276-expertise-merge-duplicate-id/notes/review-harness-code-reviewer-c0.md
```
