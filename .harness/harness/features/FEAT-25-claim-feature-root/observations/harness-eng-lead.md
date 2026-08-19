# Observations — harness-eng-lead — FEAT-25-claim-feature-root

- 2026-08-19: Run `2026-08-19-1-eng`. I hold no `Bash`, but the dispatch required me to run each
  task's `verify:` myself before accepting it. Resolved by spawning `harness-dev-ops` as a
  **verify-only runner** — in-squad (DEC-118 holds), holds Bash, is not the doer, mutates nothing,
  and independently re-extracts the `verify:` block from `plan.yaml` with `yaml.safe_load` before
  running it. Both runs also byte-diffed their extraction against my dispatch string. This is the
  closest executable form of "acceptance evidence not authored by the doer" available to a lead.

- 2026-08-19: The `SubagentStop` `validate-digest.py --hook` fires every time a lead yields between
  async dispatch waves. A lead conducting a multi-step DAG has no in-flight return shape, so the
  only conforming options mid-run are terminating the run early or emitting a verdict for work not
  yet seen — both worse than the violation. Fired 5+ times across this run. Raised as a
  non-blocking open_question, not worked around.

- 2026-08-19: Pre-dispatch read of `test-factory-claim.py` found that T-02 step 5's eighth board
  item would break `check("(X) sc13b fixture: the seven skip lines are for exactly issues
  901..907", {n for n,_ in matches} == {str(n) for n in range(901, 908)})` — an assertion whose
  expectation MUST change while its name may NOT (the plan authorises exactly one rename and spent
  it elsewhere). Instructed: fix the expectation to `range(901, 909)` keeping exact-set equality,
  leave the name byte-identical, raise the stale name up. Catching this before dispatch cost one
  read; after dispatch it would have cost a send-back.

- 2026-08-19: There turned out to be TWO stale "seven" case names after T-02, not one — `:997`
  (901..907) and `:1003` (SC-13(b) pairwise distinctness). The doer's own open_question named only
  the first. Counting them myself is what turned a member's partial report into a complete one.
  The other three "seven" mentions (`:10`, `:333`, `:824`) are the SC-22 blocker-gate seven, a
  different set, correctly untouched.

- 2026-08-19: SC-08 clause (a) grades `git diff --name-only d1ffd7f...<head>`, but NONE of the
  three `verify:` blocks checks the diff at all — they only grep and run suites. The working tree
  carries five modified held-dirt files outside every `files:` list
  (`.claude/agents/harness-{eng,product,validator}-lead.md`, `DECISIONS.md`, `SPEC.md`), so a
  commit that sweeps the tree fails clause (a) on files this squad never touched. Flagged up; the
  commit pen is the orchestrator's (DEC-153).

- 2026-08-19: `test-factory-claim.py`'s `run_main()` unconditionally re-assigns
  `claim.FEATURES_ROOT` from the TEST MODULE's own `FEATURES_ROOT` global, so a case that patches
  `claim.FEATURES_ROOT` before calling `run_main` is silently clobbered. The T-02 doer found this
  while building the absent-root fixture and patched the test module's global instead, with
  save/restore in a `finally`. Any future case pointing the root somewhere must do the same.

- 2026-08-19: Pre-decided T-03 step 5's expected result from reading `test-check-state.py:1701-1736`
  and `:1744-1806` rather than waiting for the member to report: the suite builds its sandbox from
  every STUB key's `legacy` form, so a new key participates automatically. Split the routing in
  advance — an (x.3) failure means the doer's own stub matches both patterns (`[both]` form-set,
  fixable in `layout_fixtures.py`); an x.1/x.2/x.4/x.5 failure is the DEC-174 `check-state.sh`
  blocker. Without that split a self-inflicted stub error reads as a false BLOCKED.

- 2026-08-19: `.harness/notes/dec-11-frontmatter-enumeration-2026-08-19.md` was named to me as held
  dirt but appears nowhere in `git status --porcelain`. Unexplained; recorded, not acted on.
