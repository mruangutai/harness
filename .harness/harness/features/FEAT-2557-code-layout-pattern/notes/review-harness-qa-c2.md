# QA gate — FEAT-2557 · run r-20261127-2-validate-validator · cycle 2

**BLUF: PASS. `matrix_ok: true`, `suite: n/a`, `kinds: []`, `fail_first: []`.** T-01 is
`change_type: docs`, and `test_matrix.docs.always` is `[]` with no `when:` at the pin, so no kind
is required. I ran no suite and wrote no receipt under `runs/r-20261127-2-validate-validator/qa/`,
and I invented none. T-01's verify re-ran green at the pin (exit 0). The index is in sync and the
anchors are clean. The fix delta touches only DECISIONS.md, DECISIONS-INDEX.md and the feature
dir. `plan-merge.py` and `check_state/ctx.py` are byte-identical across both pins and base.
I have no findings.

## Matrix at the pin

- Repository: harness. It is an unbound Harness feature, reviewed in the repo that holds it.
- Commit: `afd20116a2d5b9ffcbd243cb61c1f282e3935318`, the worktree `feature.json` `review_sha`.
  The blob at the pin reads the prior `5c600680…`, because a commit cannot carry its own SHA.
- Blob: `git show afd20116…:.harness/harness.json` gives `test_matrix.docs = {"always": []}` with
  no `when:`.
- Started tasks: T-01 only, `change_type: docs` (plan.yaml at the pin). There is no predicate to
  evaluate.
- Required kinds: **none**.
  - `unit`, `integration` and `typecheck` are active but not required, so I did not run them.
  - The `locally_run` kinds have detect surfaces under `tests/manual/probe-*.py`, which the diff
    does not touch, so they need no recorded run.
- I added no requirement. The fix delta is prose in two docs files, with no gate, hook, schema,
  config or test change.

## fail_first

Empty. In the BRIEF at the pin, SC-01..SC-06 each carry exactly one `verify: inspection` (BRIEF
lines 38, 43, 53, 58, 64 and 68). No SC is `verify: automated`.

## Pin checks (managed pin `pinned-checkout.py add … --persona harness-qa`)

The pin's HEAD was `afd20116`, and it was clean. Every command ran with `HARNESS_AGENT_TYPE` unset.
The pin was removed on return (rc 0).

1. **T-01 verify**, extracted verbatim from plan.yaml at the pin with yaml `tasks[0].verify`
   (32 lines) and run with `bash`. Result: **exit 0**, with the last line
   `LAYOUT-SKILL-AGENTS-DEC-OK`.
   - `check-decision-anchors.py` reported "examined 25 anchor(s), 0 failed".
   - `test-gen-decisions-index.py` passed 12/12 `ok`.
   - The scope check passed against `git merge-base HEAD main`.
2. **Index.** `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` exited 0 with no output.
   `check-decision-anchors.py` exited 0 (25 anchors, 0 failed). The DEC-259 row's `@8758` matches
   the heading's line in DECISIONS.md at the pin. The row's tag set changed from
   `[state,plan,dispatch,digest]` to `[plan,state,dispatch,skills]`. That change is generator
   output, which the zero diff confirms, and the hand-written ruling tail is unchanged.
3. **Scope.** `git diff --stat 5c600680..afd20116` lists 14 files.
   - Outside the feature dir, `git diff --name-only` gives only `.harness/harness/docs/DECISIONS-INDEX.md`
     (+1/−1) and `.harness/harness/docs/DECISIONS.md` (+7/−4).
   - Every other file is under `.harness/harness/features/FEAT-2557-code-layout-pattern/`.
   - The blob ids of `plan-merge.py` and `check_state/ctx.py` are identical at cf7b422b, 5c600680 and
     afd20116: `9c13c3d3…` and `78054688…` respectively.
   - `git diff --quiet cf7b422b afd20116 -- bin/plan_merge bin/check_state` gave 0.

## New probing: does the fix's prose match the tree? (assurance, not a matrix kind)

I checked each factual claim in the amended Because paragraph against the pin.

- **The re-export claim is accurate.** `plan-merge.py:141` reads
  `from plan_merge.approval import signed_task_hash  # noqa: E402,F401  INV-40's import`, and the
  function is defined at `plan_merge/approval.py:543`.
- **The loader claim is accurate.** In `check_state/ctx.py`, `_load_hash_module` (line 360) loads
  `os.path.join(sys.argv[2], "plan-merge.py")` by path, and line 370 shows the INV-40 failure text.
- **The autoload claim is accurate.** `harness-codebase-design` appears under `autoloadSkills:` in
  the frontmatter of `.omp/agents/` ai-dev, backend-dev, data-engineer, dev-ops, frontend-dev,
  eng-lead and code-reviewer. product-lead lists it too, but the prose does not say "only".
- **DEC-149 at the pin introduces `harness-codebase-design`.** It says doers receive the skill
  through dispatch, not preload. The new wording, "DEC-149 brought the skill in", is consistent
  with that and no longer cites DEC-149 for current autoload.

I found no discrepancy.

## Coverage gaps

None against the matrix. Phase 1 (BRIEF and plan only) expected no automated test: this is a
prose-only `docs` change, and every criterion is `inspection`.

## Principles applied

- harness-verification-rules (skill): I took the floor from the pinned `harness.json` blob and
  reported `kinds: []` with no receipt, rather than running unrequired suites to manufacture a
  `pass`.
