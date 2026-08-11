# QA — FEAT-13 T-01 — test_matrix gate on 56abf27

## Verdict

PASS. `matrix_ok: true`. All three commands green, coverage traced per-SC with `file:line`
anchors, and all four mandated mutants reddened the correct assertion (none stayed green).
Zero send-back cycles (`cycles: 0`).

## Commands run (worktree root, pinned SHA 56abf27, diff base 6dfbf7c)

1. `bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit`
   exit 0. 10 scripts, all PASS: test-harness-yaml-corpus.py 13/13,
   test-render-brief.py 15/15, test-team-catalog.py 10/10, test-factory-cli.py 33/33,
   **test-factory-gh.py 153/153**, test-factory-config.py 56/56, test-factory-workspace.py 30/30,
   **test-factory-decompose.py 175/175**, **test-factory-claim.py 95/95**,
   **test-factory-land.py 56/56**.
2. `bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration`
   exit 0. test-validate-digest.py, test-gh-sync.py, **test-check-state.py**,
   test-check-expertise.py, test-gen-decisions-index.py, test-bash-write-guard.py,
   test-check-domain.py, test-harness-yaml.py, test-upgrade-config.py, test-check-plan-routes.py,
   test-merge-settings.py all PASS; **test-factory-integration.py 97/97** PASS (SC-08's
   end-to-end decompose→claim→workspace→land journey included).
3. Task `verify:` verbatim (unit + `test-factory-integration.py` directly + the four greps).
   exit 0.

`matrix_ok: true` — both required kinds (`cross_module` → `unit`, `integration`) are `status:
active` with real `cmd`, both ran, both green, and the green is on tests that are themselves
part of the `56abf27` diff (`test-factory-gh.py`, `test-factory-decompose.py`,
`test-factory-land.py`, `test-factory-claim.py`, `test-factory-integration.py` all changed in
this commit — P-05).

## Per-SC coverage (SC-01..SC-09; SC-10 is T-02's live check, out of scope here)

- SC-01 — `test-factory-gh.py:647,651` ("issue_board_item_id: made exactly ONE call" /
  "ZERO calls hit project item-list", asserted on `argv[1:3]`).
- SC-02 — three separate anchors, each asserting `project_items` zero AND `issue_board_item_id`
  once, with argument-VALUE pinning, not just counts:
  - decompose: `test-factory-decompose.py:959,961` (D4-3, `(REPO, issue_num, 3)`).
  - land: `test-factory-land.py:215,218,221` (M1, asserts `args.repo` value AND explicitly
    `!= OWNER` — the mis-wire this exists to catch).
  - claim: `test-factory-claim.py:475,477` (R4, `(REPO, 61, BOARD)`).
- SC-03 — the two no-item cases are SEPARATE `check()` calls: recognised-empty →
  `test-factory-gh.py:682` (empty nodes, totalCount 0, returns None, no raise); unrecognised
  (absent `"issue"` key) → `test-factory-gh.py:709`, explicitly commented as distinct from
  the adjacent explicit-null case at `:694`. Verified this discrimination is load-bearing via
  mutant M1 below, not just present.
- SC-04 — `test-factory-gh.py:768` (totalCount 3, one node, raises; message asserted to
  name both totals in the following check()).
- SC-05 — `test-factory-decompose.py:1009-1035` (D4-3c: closed issue still resolves the existing
  item via `issue_board_item_id`, no `project_item_add`). Note: this is a call-shape pin, not a
  simulation of gh's own state filtering — consistent with the BRIEF's explicit constraint
  ("Proof is unit call-shape assertions plus one live read... explicitly chosen against a
  FEAT-11-style live measurement"); the live half is T-02, not this gate.
- SC-06 — `test-factory-claim.py:530-553`, TWO separate cases: R6a (closed, unowned, `:532`)
  and R6b (closed, self-owned + `factory:claimed` + agent in assignees, `:546`) — the
  discriminating case per D-05's ordering. Reachability confirmed by mutant M3.
- SC-07 — `test-factory-land.py:330-347` (M7): exits 2, POSITIVE assertions that the push
  happened (`push_calls`, `:341`) and the PR was created (`pr_create_calls`, `:344`) before the
  refusal, plus `field_set_calls == []` (`:347`). Reachability confirmed by mutant M4.
- SC-08 — `test-factory-integration.py` stub branch keyed on query text
  (`.claude/skills/harness/bin/test-factory-integration.py` diff, `"projectItems" in query_text`),
  synthetic node's `project.number` pinned to 9 = the fixture's board number; full journey run at
  97/97 in command 2 above.
- SC-09 — `test-factory-claim.py:568,569` (R8): poll path calls `project_items` exactly once
  with the unchanged station-and-open query string, and asserts `issue_board_item_id` is never
  called on that path.

## Mutant results (M1–M4) — all reddened the correct assertion, restored, worktree untouched

All mutations applied to a scratchpad copy at
`/private/tmp/.../scratchpad/qa-bin/` (copied from the pinned worktree), never the repo. Restored
via the Write tool after each; `diff` against the worktree source confirmed byte-identical
after every restore, and `git status --porcelain -- .claude/skills/harness/bin/` in the worktree
showed no changes throughout.

- **M1** — `factory_gh.issue_board_item_id`: replaced the key-presence guard with
  `issue = repository.get("issue"); if issue is None: return None`. Ran
  `python3 test-factory-gh.py`. **1 of 152 FAILING**: `issue_board_item_id: repository dict with
  NO 'issue' key at all RAISES (distinct from the explicit-null case above)`. Exactly the check
  this mutant should kill, nothing else moved.
- **M2** — `factory_land._main`: changed `_find_item_id(args.repo, ...)` to
  `_find_item_id(owner, ...)` (the bare board-owner login FEAT-13's plan calls out as the live
  hazard). Ran `python3 test-factory-land.py`. **3 of 56 FAILING**: the three (M1)-labelled
  argument-value assertions in `test-factory-land.py` — "is the repository string, NOT the bare
  board-owner login", "is explicitly NOT the board-owner login", "called with (repo, issue,
  board_number)".
- **M3** — `factory_claim._main`: moved the closed-issue refusal (5a-pre) to AFTER the
  self-ownership branch (5a). Ran `python3 test-factory-claim.py`. **2 of 95 FAILING**: both
  `(R6b)` assertions — "closed, self-owned issue exits 2, NOT re-emitted at exit 0" and its
  "stdout empty" companion. R6a (unowned closed issue) stayed green, as expected — only the
  self-owned case discriminates the ordering.
- **M4** — `factory_land._main`: moved the `issue.get("state") != "OPEN"` check to before the
  branch push (reading `issue_view` early instead). Ran `python3 test-factory-land.py`. **2 of 56
  FAILING**: both M7 positive-sequencing assertions — "the push already happened before the
  closed-issue refusal" and "the pull request WAS already created before the closed-issue
  refusal". `field_set_calls == []` alone stayed green under this mutant (as flagged in the
  dispatch) — the two positive assertions are what catch it, and they're present.

No mutant stayed green; no `must_fix` needed on assertion strength.

## Other checks

- Docstring rewrites in `factory_decompose.py` (`_find_existing_item_id`, the block above the
  deleted `_item_repo`) match D-01/D-02/D-03 verdicts verbatim — reworded opener now states the
  no-state-filter property "by construction," the stale `project_items`-truncation-guard
  sentence is replaced, both `# ----` rule lines preserved.
- Forbidden-token check (`factory_gh\.project_items` grep) passed live in command 3; confirmed
  independently — zero hits in decompose/land, exactly one (the claim poll) in claim.
- `_item_repo` fully deleted, no stray references anywhere in `bin/*.py`.
- The plan's `argv[:2] == ["project", "item-list"]` text is confirmed wrong at source
  (`factory_gh.py:88`, `run_gh` prepends the binary) — tests correctly use `argv[1:3]`. Not
  failed on, per dispatch; flagged here for pm/operator.
- `receipt-harness-backend-dev-lookup-swap.md` documents HALF A RED→GREEN with the actual
  `AttributeError` before the helper existed, confirming the mandated split and test-first
  order were followed, not just claimed.

## Phase 1 vs Phase 2 — no gap

Phase 1 (BRIEF/plan only, before reading code) expected: one-call/zero-list assertion (SC-01);
three call sites each independently zeroing `project_items` (SC-02); a two-way null-vs-absent
split (SC-03); a truncation-over-count raise (SC-04); decompose recovering a closed issue's item
(SC-05); claim's closed-issue refusal asserted twice, unowned and self-owned (SC-06); land's
failure point pinned by push+PR-create positives (SC-07); the integration journey (SC-08); the
poll's shape held constant (SC-09). All nine are present in Phase 2 with the anchors above. No
coverage gap between Phase 1 expectations and Phase 2 findings.

## coverage_gaps

None on this surface. (Standing gap, already adjudicated per dispatch: no test guards
`_ISSUE_ITEM_QUERY`'s literal text against a future edit reintroducing a state filter — already
raised by eng-lead, not mine to add.)

## Bounds honored

No commit, no push, no PR. No `gh` mutation, no live board read (that's T-02, not run here). No
edits inside DEC-174's four carve-out scripts. No repo-file mutation — all four mutants ran in
the scratchpad copy only, restored and verified identical before being reported.
