# Receipt — harness-backend-dev — FEAT-11 MF-2 (cycle c2)

## What changed

One `check(...)` added to `test-factory-gh.py` immediately after the pre-existing board-vs-org
comparison, comparing `board_exc` to `unknown_exc` — the third SC-11 pairing that had no assertion.
`factory_gh.py` was not touched in the final diff (mutated and byte-restored for the falsifiability
proof — see below).

## 1. Check counts, before/after (self-measured, not relayed)

- Before edit: `git stash` the working change, run `python3 .claude/skills/harness/bin/test-factory-gh.py`
  → `118/118 checks passed.`
- After edit (stash popped): same command → `119/119 checks passed.`
- Delta: +1, matches exactly one new `check(...)` added.

## 2. Line numbers, post-edit

- New check: `test-factory-gh.py:461` (`check("board absent: message differs from the unknown-owner
  message", ...)`), immediately after the pre-existing `:459` org-comparison check.
- D-04 frozen rendered literals, post-edit:
  - `:332` — unchanged (above the edit site), matches prediction.
  - `:479` (was `:476` pre-edit) — shifted +3.
  - `:627` (was `:624` pre-edit) — shifted +3.
- The edit added exactly 3 lines (`git diff --stat`: `1 file changed, 3 insertions(+)`).

## 3. `factory_gh.py` sha256 / git status

- Before mutating: `f5978a33269828704f2225ccd2af851b131e45012ef2ac6c68ccfcf4c8ca1e02`
- After restoring: `f5978a33269828704f2225ccd2af851b131e45012ef2ac6c68ccfcf4c8ca1e02` — identical.
- `git status --porcelain .claude/skills/harness/bin/test-factory-gh.py
  .claude/skills/harness/bin/factory_gh.py` →
  ```
   M .claude/skills/harness/bin/test-factory-gh.py
  ```
  `factory_gh.py` is absent from the changed set.

## 4. `grep -n "differs from" test-factory-gh.py`

Before the fix — measured against `git show HEAD:...test-factory-gh.py` (HEAD is a valid pre-edit
reference: `git diff --stat` on the working tree shows only the 3-line insertion this cycle made, so
HEAD == pre-edit content), not relayed from the dispatch text (2 lines):
```
436:    check(f"organization ({label}): message differs from the unknown-owner message",
459:check("board absent: message differs from the organization message",
```
Same command against `git show HEAD:...` also confirms the pre-edit D-04 anchors used in section 2
(`grep -n "does not offer it"` → `332`, `476`, `624`), so those are measured, not relayed either.

After the fix — measured against the current file (3 lines):
```
436:    check(f"organization ({label}): message differs from the unknown-owner message",
459:check("board absent: message differs from the organization message",
461:check("board absent: message differs from the unknown-owner message",
```

## Falsifiability proof (per the dispatch's required standard)

1. Backed up `factory_gh.py` and recorded its sha256 (section 3 above) BEFORE mutating.
2. Mutated `factory_gh.py:270-272` (the board-not-found branch) to collapse it onto branch (a):
   `what` `"project owner not found"`, value `owner`, `next_step` `"check the owner login"`.
3. Ran `test-factory-gh.py`. Observed output: `2 of 119 FAILING`, and by name:
   - `FAIL  board absent: raises GhError naming owner + project number`
   - `FAIL  board absent: message differs from the unknown-owner message`

   This matches the dispatch's prediction exactly: exactly two named checks went red, `:459`
   (board-vs-organization) stayed GREEN, and the whole-suite `RAISED` invariant loop stayed green
   (no `NG` lines from that loop in the failing run's output).
4. Restored `factory_gh.py` byte-identically (sha256 match confirmed in section 3); `git status
   --porcelain` confirms it is absent from the changed set. Re-ran the suite post-restore:
   `119/119 checks passed.`

## Gate (a) — T-01's `verify:` block

Loaded via `harness_yaml.load_plan(...)["tasks"][0]["verify"]`, written to a scratch file, and
`diff`'d against the dispatch's quoted block written to a second scratch file (not eyeballed). The
`diff` reported exactly one line of difference: a trailing blank line appended by
`print(plan["tasks"][0]["verify"])`'s own newline, an artifact of my extraction method — the 17
content lines are byte-identical, confirmed by inspection of the diff output (`17a18 > <empty>`,
nothing else). Executed the LOADED string (the scratch file, run with `bash`, not the dispatch's
retyped copy). Output:
```
PASS
```

## Gate (b) — `run-unit-tests.sh --kind unit`

All 10 unit scripts reported `PASS` (`test-harness-yaml-corpus.py`, `test-render-brief.py`,
`test-team-catalog.py`, `test-factory-cli.py`, `test-factory-gh.py`, `test-factory-config.py`,
`test-factory-workspace.py`, `test-factory-decompose.py`, `test-factory-claim.py`,
`test-factory-land.py`). `test-factory-gh.py`'s own line: `119/119 checks passed.`
Overall exit code: 0.

## Gate (c) — `run-unit-tests.sh --kind integration`

All 12 integration scripts reported `PASS` (`test-validate-digest.py`, `test-gh-sync.py`,
`test-check-state.py`, `test-check-expertise.py`, `test-gen-decisions-index.py`,
`test-bash-write-guard.py`, `test-check-domain.py`, `test-harness-yaml.py`,
`test-upgrade-config.py`, `test-check-plan-routes.py`, `test-merge-settings.py`,
`test-factory-integration.py`). `test-factory-integration.py`'s own line: `97/97 checks passed.`
Overall exit code: 0.

## Constraints observed

- No live `gh` calls — every fixture used was the offline recorder/fake harness already in the
  test files.
- No DEC-174 carve-out file (`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `check-state.sh`) touched.
- No commit, no push.
- `factory_gh.py` net diff for this cycle: none (mutate-and-restore only, proven byte-identical).
