# Receipt — T-03 — harness-backend-dev

## Task
FEAT-56-central-onboarding-model, T-03: reconcile the onboarding-premise tests (comment/docstring
edits only). Cross-checked plan.yaml lines 521-592 against the dispatched `intent:` and `verify:` —
verbatim match, no mismatch.

## Edits (all comment/docstring, no assertion/fixture/control-flow line moved)

1. `tests/integration/test-layout-migration.py` — case 14 comment (~lines 251-253). Replaced the
   false "harness-init installs the whole bin/ into products" premise with: a copy or worktree of
   the control plane carries every reader file, only the control plane carries the fleet
   declaration → NOT APPLICABLE. `build(tmp, marker=False)` (line 254) and both `check(...)` calls
   (lines 256-257, 260-261) are byte-identical to before — confirmed by diff (only the comment
   block changed, 4 lines → 3 lines of comment, code lines untouched).

2. `tests/integration/test-check-state.py` — comment above
   `case_inv32_era_comes_from_project_config` (lines 3889-3890). Replaced "a literal compiled into
   a file that /harness-init copies everywhere" with "the boundary is the project's own, read from
   that repository's own harness.json, which for a fleet member lives on its default branch."
   The four assertions and the mutation proof (`case_inv32_era_guard_is_load_bearing`, lines
   3857-3886, and the function body at 3892-3905) are untouched. Did not run the whole file as
   verify (per instruction — it takes ~48s); verify used a scoped `grep` instead.

3. `tests/integration/test-hooks-install.py` — module docstring line 4. Added the clause "— the
   control-plane clone's own —" naming the subject of the per-clone step. Nothing else in the file
   changed; ran the whole file as this task's own verify and it passed (see below), which proves
   `case_commands_verbatim_in_skill`, `case_sc08_before_and_after`, `case_sc13_idempotence`,
   `case_sc13_reporting_and_red_proof`, and `case_sc14_end_to_end_and_red_proof` all still pass
   unchanged.

4. `tests/integration/test-post-merge-sweep.py` (~lines 783-785) and
   `.claude/skills/harness/bin/post-merge-sweep.sh` (~lines 68-69). Both cited
   "harness-init SKILL.md:73/:78". Read the CURRENT SKILL.md (414 lines, post e502adca) and found
   the section heading at line 62: `#### The per-clone step: point git at the tracked hooks
   directory`. Replaced both line citations with "harness-init SKILL.md, the per-clone step
   section", keeping the surrounding sentence and all behaviour. No new line number was introduced
   into either file. The `.sh` change is comment-only (inside the module docstring of
   `_resolve_main_checkout_root`).

## Items 5-7: UNCHANGED, verified by grep for "harness-init"

- `tests/integration/test-merge-settings.py`: **2 matches** (lines 14 and 144 — "a gate
  harness-init calls HARD" / "harness-init treats its exit as a HARD GATE"). Docstring clause
  remains true; no edit made.
- `tests/integration/test-merge-gitignore.py`: **0 matches**. No edit made.
- `tests/integration/test-upgrade-config.py`: **0 matches** for "harness-init", and no T-02 remedy
  string is asserted anywhere in this file (checked for `remedy`/`MSG_` patterns too — no hits). No
  edit made; T-02's messages were not touched.

## Item 8

`tests/integration/fixtures/prior-check-domain.sh.fixture` (note: actual path is
`tests/integration/fixtures/`, not `tests/fixtures/` as paraphrased in the dispatch — same file,
confirmed via glob) — untouched. `git status --porcelain` on that exact path is empty.

## Verify — run VERBATIM from the worktree root

```
python3 tests/integration/test-layout-migration.py &&
python3 tests/integration/test-hooks-install.py &&
python3 tests/integration/test-post-merge-sweep.py &&
grep -qF "read from that repository's own harness.json" tests/integration/test-check-state.py &&
! grep -qF 'SKILL.md:73' tests/integration/test-post-merge-sweep.py &&
! grep -qF 'SKILL.md:73' .claude/skills/harness/bin/post-merge-sweep.sh
```

Output (last lines of each script plus overall result):

```
== test-layout-migration.py ==
ok   - case 20 parity: CANNOT_VERIFY undeclared-segment (carries detail) — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY undeclared-segment (carries detail) — the cause clause is identical in both
ok   - case 20 parity: CLEAN names nobody at either site — real gate and render name the same reader set
ok   - case 21: real root's harness/docs surface is CLEAN with migrated evidence
ok   - case 22: real root's harness/features surface is CLEAN with migrated evidence
[41 'ok ' lines total, 0 '^FAIL ' lines, exit 0]

== test-hooks-install.py ==
PASS: (e-red) core.hooksPath points at the tracked dir after setup
PASS: (e-red) real merge succeeds
PASS: (e-red) RED PROOF: the shim reports the missing sweep rather than silently doing nothing
PASS: (e-red) RED PROOF: with the shim repointed at a nonexistent sweep, the worktree SURVIVES the merge
EXIT=0
[29 'PASS:' lines total, 0 '^FAIL ' lines]

== test-post-merge-sweep.py ==
PASS: (i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the script happens to run from
PASS: (i) the milestone close call reached gh for R's LANDED milestone (810)
PASS: (i) DIVERGENCE PROOF: WT_CALLER's own divergent milestone (811) was NEVER closed — the sweep did not write into the wrong copy
PASS: (i) the terminal worktree under R was removed, proving feat_dir was found and ship succeeded against the correct main-checkout copy
EXIT=0
[52 'PASS:' lines total, 0 '^FAIL ' lines]

== grep checks ==
grep -qF "read from that repository's own harness.json" tests/integration/test-check-state.py -> rc=0
! grep -qF 'SKILL.md:73' tests/integration/test-post-merge-sweep.py -> rc=0 (pattern absent)
! grep -qF 'SKILL.md:73' .claude/skills/harness/bin/post-merge-sweep.sh -> rc=0 (pattern absent)
```

Ran the exact verify block chained with `&&` end-to-end, captured into `rc=$?` (a variable, not a
tail read) and separately counted `^FAIL ` across the full combined output:

```
rc=0
FAIL_count=0
```

Did NOT run `tests/integration/test-check-state.py` as a whole (per instruction — ~48s, only the
scoped grep is required). Did NOT run the whole project suite.

## git status / HEAD

```
$ git status --porcelain
 M .claude/skills/harness/bin/post-merge-sweep.sh
 M .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
 M tests/integration/test-check-state.py
 M tests/integration/test-hooks-install.py
 M tests/integration/test-layout-migration.py
 M tests/integration/test-post-merge-sweep.py
```

Plus this receipt (untracked, new file) and its containing `notes/` run dir. `feature.json` and
`plan.yaml` under `.harness/harness/features/FEAT-56-central-onboarding-model/` were already
modified before this dispatch started (task status transitions from concurrent orchestrator/sibling
activity — task T-03's own status flip to `building` is visible at plan.yaml:528) — not touched by
this task, reported per O-06 rather than reverted.

```
$ git rev-parse HEAD
7b63d5835fb33b4f9e7bf37f3c4897ba10497ef3
```

Matches the HEAD given in the dispatch (`7b63d583`). No commit made.

## Conclusion

Every edit in items 1-4 is a comment or docstring. No assertion, fixture argument, or control-flow
line moved — confirmed by `git diff` (5 files, 13 insertions / 12 deletions, entirely inside
`#`-comment blocks or triple-quoted docstrings). Verify block passes end-to-end (rc=0, 0 FAIL
lines). Items 5-7 confirmed unchanged with grep evidence recorded above. Item 8's fixture is
untouched.
