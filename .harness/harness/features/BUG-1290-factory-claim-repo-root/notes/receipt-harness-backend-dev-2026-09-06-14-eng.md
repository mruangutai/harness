# Receipt — harness-backend-dev — BUG-1290 T-05/T-06 printed-FAIL literal 5b arm

**BLUF:** `tests/unit/test-factory-claim-mutation.py` now carries a second, independent arm that
proves the operator's literal directive: under a mutation collapsing `_BlockerCache`'s issue-map
cache key from `(repo, feature)` to `feature` alone, the real suite (run through the existing,
unmodified `_run_suite()`) PRINTS `FAIL  BUG-1290 5b`, guarded by a reached-marker written to
`sys.__stdout__`. `test-factory-claim.py` is unmodified by me and stays at 125/125. Production is
byte-identical to `c488218e`.

**Mechanism (two sentences):** `_mutate_and_run_key_collapse()` patches the module attribute
`factory_claim._BlockerCache` with `_KeyCollapsingBlockerCache`, a real subclass whose
`issue_number` resolves `canonical = self._first_repo_for.setdefault(feature, repo)` and delegates
to `super().issue_number(canonical, feature, task_id)` — so the first repository seen for a
feature id supplies every later repository's issue-map lookup, the exact defect B-3's `(repo,
feature)` keying closed — and `_key_collapse_proof()` then asserts `_case_line(output, "FAIL",
"5b")` is non-`None` and that the mutant's class-level `_reached` flag actually flipped, printing
`MUTANT KEY-COLLAPSE ACTIVE` to `sys.__stdout__` (never `sys.stdout`, which the suite captures) the
first time the collapsing lookup runs.

## Verification (all runs: `env -u HARNESS_AGENT_TYPE python3 <file>`, worktree root)

1. `tests/unit/test-factory-claim-mutation.py` — exit 0. Verbatim:
   ```
   MUTATION PROOF: 3/3 cases reddened
   MUTANT KEY-COLLAPSE ACTIVE
   FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
   KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed
   ```
   All three requested lines present: existing arm's `MUTATION PROOF: 3/3 cases reddened`, the new
   arm's printed `FAIL  BUG-1290 5b` line, and its `MUTANT KEY-COLLAPSE ACTIVE` reached marker.

2. `tests/unit/test-factory-claim.py` (standalone, unmutated) — exit 0. Verbatim final line:
   `125/125 checks passed.`

3. **Negative control.** Edited line 175 of the mutation file in place (`return
   super().issue_number(repo, feature, task_id)` — delegates unchanged, no key collapse), re-ran:
   exit 1, verbatim tail: `MUTANT KEY-COLLAPSE ACTIVE` / `KEY-COLLAPSE MISSING: 5b` /
   `KEY-COLLAPSE PROOF: INCOMPLETE`. This proves the arm CAN go red — it does not pass regardless
   of the mutation. Restored line 175 to `return super().issue_number(canonical, feature,
   task_id)`, re-ran: exit 0, identical output to step 1 (`KEY-COLLAPSE PROOF: FAIL BUG-1290 5b
   printed`). No probe file was created; the edit-and-revert was done in place on the target file
   itself, per the assignment's instruction.

4. `git diff --stat c488218e -- .agents/ .claude/skills/ bin/` — empty output. Production
   byte-identical to `c488218e`.

5. `git status --porcelain` (post-restoration):
   ```
   M .harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json
   M tests/unit/test-factory-claim-mutation.py
   M tests/unit/test-factory-claim.py
   ?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b27.md
   ?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-14-eng.md
   ```
   `test-factory-claim.py`'s `M` predates my run (I never wrote it — read-only, per the
   assignment); no `.orig`/`.bak`/probe survivors. The added receipt file itself is the only new
   untracked entry beyond what the assignment already named.

## Scope notes

- Only file touched: `tests/unit/test-factory-claim-mutation.py`. `_run_suite()`, `_case_line()`,
  `_baseline()`, `_mutate_and_run()` and `_mutation_proof()` (the existing `features_root` arm)
  are untouched in structure and semantics — reused as-is by the new arm.
- `main()` now runs both arms unconditionally (`features_root_ok = _mutation_proof()` then
  `key_collapse_ok = _key_collapse_proof()`, `sys.exit(0 if both else 1)`) — neither short-circuits
  the other; `_baseline()` remains the sole shared prerequisite gate, as it already was before this
  change.
