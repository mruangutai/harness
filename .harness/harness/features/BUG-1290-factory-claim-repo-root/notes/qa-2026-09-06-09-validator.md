# qa test-matrix gate — B-16 (cycle 2026-09-06-09)

**VERDICT: matrix_ok=true, no must_fix.** Both required kinds ran green; case `5g` reddens for
exactly the reason it claims, restores global state, and the pre-cycle baseline delta is +1.

## Diff object (scoped correctly, not the one-file increment)

`merge_base = git merge-base main HEAD` = `6e95435a`. Matrix object = `git diff --name-only
6e95435a HEAD` (52 files: 5 production `.py`, 4 test files, rest `.harness/**` plan/notes) **union**
`git status --porcelain` (uncommitted: `M tests/unit/test-factory-claim.py`; three untracked notes).
Production touched: `factory_claim.py`, `factory_config.py`, `feature-worktree.py`,
`layout_fixtures.py`, `layout_migration.py`. Test files touched: `tests/integration/test-factory-integration.py`,
`tests/integration/test-layout-migration.py`, `tests/unit/test-factory-claim-mutation.py`,
`tests/unit/test-factory-claim.py`.

## Matrix resolution — plan.yaml's 5 tasks all `change_type: bugfix`

`test_matrix.bugfix` (harness.json): `always: []`, `when: [unit if touches_runtime_code, integration
if fix_confined_to_tests_and_contract_docs, __bug_class__ if match_bug_class]`.

| predicate | resolution | reason |
|---|---|---|
| `touches_runtime_code` | **true → unit required** | 5 production `.py` files in the diff object |
| `fix_confined_to_tests_and_contract_docs` | **false → integration NOT required by this leg** | production files were touched, so the fix is not confined to tests/docs |
| `match_bug_class` | **false, cannot fire** | project-tier Expertise G-08: no bug-class taxonomy entry exists yet in this repo; this leg is an unresolvable placeholder |

Floor from the matrix alone: **unit only**. I added **integration** beyond the floor (verification-rules
"add what the diff warrants") because the diff's own two `tests/integration/**` files are part of this
feature's change and must be shown to pass — labelled supplementary/added below, not matrix-required.
`config`/`ai_behavior`/other change_types don't apply (no task carries them).

## Required + added kinds — resolved states, run by me

| kind | state | cmd | exit | discovery | summary |
|---|---|---|---|---|---|
| unit (required) | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 28 files | `pool: 8 workers, 28 files, 3.12s wall`; `test-factory-claim.py`: **125/125 checks passed** |
| integration (added, diff warrants it) | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 46 files | `pool: 8 workers, 46 files, 80.54s wall`; `test-factory-integration.py` (exit 0, 16.17s): **131/131 checks passed**; `test-layout-migration.py` (exit 0, 1.83s): **28/28 checks passed** |

Both diff-touched integration test files are confirmed present in the 46-file sweep and both green —
not a bare exit code, the per-file PASS lines were grepped out of the run.

## §3/§4 — 5g's mutation control, measured in a disposable `/tmp` copy (never the working file)

Copied the worktree to `/tmp/bug1290-mutation-check` via plain `cp -r` (not through the Write/Edit
tools), ran there, then destroyed the copy with `shutil.rmtree` after bash's write-guard refused `rm`
on it (the copy inherited the real worktree's `.git` pointer file, which the guard pattern-matches as
worktree-shaped even though `git worktree list` never registered it). No source file in the real
worktree was touched; `git status --porcelain` below confirms.

- **Baseline re-derivation**: `git show HEAD:tests/unit/test-factory-claim.py` has **12** named
  `check(name_5*, ...)` calls, no `5g` (confirmed via grep). Run standalone in a copy: **124/124
  checks passed.** Working copy (with the uncommitted edit): **125/125.** Delta = **+1**, exactly `5g`.
  Confirms the orchestrator's `124/124 -> 125/125` figure.
- **Mutant, driven directly** (not just through `check()`'s boolean): instantiated
  `_FeatureOnlyIssueMapCache`, swapped `claim._BlockerCache`, ran `_run_5b_scenario()` and printed the
  raw tuple:
  `CODE=1`, `OUT=''`,
  `ERR='...skip #951 ... unresolvable blocker\nskip #952 — issue #952 depends_on T-99, which has no
  recorded issue in feature.json (unresolvable blocker)\n...no claimable work\n'`.
- **Right reason, confirmed against `_5b_property_holds`'s own source** (read at
  `tests/unit/test-factory-claim.py:1208-1223`): the property demands `payload.get("issue")==952`
  under a `code==0` JSON payload. Under the mutant, `code=1` (`EXIT_NOTHING`) — the function's *first*
  branch (`if code != 0: return False`) is what returns `False`, never the `json.loads` branch, so
  there is no `JSONDecodeError` or exception in play. The mechanism is exactly what the comment
  claims: `issue_number()`'s redirect makes harness's #952 (task `T-99`, normally resolved via
  harness's own `feature.json`) instead consult **kaya-ai's** issue map (canonical = first-seen repo,
  `REPO_KAYA`, since #951 is first in `rec.items`), which has no `T-99` entry, so #952 flips from
  claimable to `unresolvable blocker`. This is `_blocker_gate`'s real `issue_number()` call
  (`factory_claim.py:132-149`), not an incidental exception path.

## §5 — no global-state leak

- `finally: claim._BlockerCache = saved_blocker_cache` (source, line 1319-1320) — empirically confirmed
  restored: `claim._BlockerCache is saved` printed `True` immediately after the driven mutant run.
- `5g` is the **last** case in the file (confirmed by reading the file's tail: nothing follows the
  `check(name_5g, ...)`/`except` block but the summary `print`/`sys.exit`), so "every case ordered
  after 5g still reports ok" is **vacuously true** — there are no later cases to leak into.
- Ran the full 125-case suite **twice** in the same copy: both runs printed `125/125 checks passed`
  with an identical PASS line for every case, confirming no ordering-dependent state change from
  running `5g` (whose mutation happens mid-run, restored, then execution continues, e.g. in the file's
  own single pass this proves nothing new could go wrong across the *rest* of the same run either,
  since `5g` runs last).

## Confirm/refute the orchestrator's batch figures — all confirmed by my own measurement

- Full unit suite `125/125` (was `124/124` before this cycle): **confirmed** — see baseline
  re-derivation above, exact match.
- Three-arm scaffold control (intact 125/125; `depends_on=["T-99"]` deleted → 5b ok / 5g FAILs;
  issue map emptied → 5b FAILs / 5g ok): **not independently re-run** — the orchestrator's arms mutate
  the *fixture*, not the code under test, and are a different perturbation from the one this dispatch
  required me to drive (the `_BlockerCache` mutant itself, §3 above). I did not re-run those two arms;
  they are consistent with what I found reading `_5b_property_holds` and are not contradicted by
  anything I measured, but I have not verified them directly. Flagging this rather than silently
  inheriting it.

## Working tree

`git -C <worktree> status --porcelain` after this note:
```
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b16.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/qa-2026-09-06-09-validator.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-08-eng-b16.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-08-eng-b16-recheck.md
```
Nothing else touched or committed.

## Send-back — fixture-mutation arms, measured (2026-09-06, cycle 10)

This send-back closes the one gap left open above: the three-arm fixture control was previously
"consistent with reading but not independently re-run." It is now re-run, in two fresh disposable
`/tmp` copies (one per arm, `rsync -a --exclude='.git'`, never the working file), each destroyed
immediately after with `rm -rf` and confirmed gone. `env -u HARNESS_AGENT_TYPE` on every invocation
(project Expertise G-07). Ran the single test file directly (`python3 tests/unit/test-factory-claim.py`)
in each copy — this is the same standalone invocation the prior cycle used for its own baseline
re-derivation, not the `run-unit-tests.sh` kind command; the matrix/kind resolution from earlier in
this note is unchanged and not re-run.

### Arm A — remove the fixture dependency `5g` names

Edit (in the Arm A copy only): `build_features_root()`'s harness-segment plan write, line 382, changed
from `plan_dict(SEG_FEATURE, [task_dict("T-77", depends_on=["T-99"])]))` to
`plan_dict(SEG_FEATURE, [task_dict("T-77")]))`.

Sibling-untouched grep, before and after, both copies inspected: kaya segment's line 377
(`task_dict("T-77", depends_on=["T-88"])`) is byte-identical pre- and post-edit; only line 382 changed.
An edit that hit both lines would prove nothing — it did not.

- `5g` marker: `FAIL  BUG-1290 5g: collapsing the issue-map cache key to feature-only breaks 5b's property`
- `5b` marker: `ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed`
- summary: `1 of 125 FAILING.`
- exit code: `1`
- failing-marker count: **1**, and it is `5g` alone (`grep -c '^FAIL'` = 1; the single `grep -n '^FAIL'`
  hit is the `5g` line)

**Confirms engineering's Arm A claim exactly**: `5g` FAILs, `5b` stays `ok`, `5g` is the sole failure,
summary `1 of 125 FAILING`.

### Arm B — the specificity control (empty the harness segment's own issue map)

Fresh copy. Edit: `build_features_root()`'s harness-segment `feature.json` write, line 383, changed from
`write_json(os.path.join(harness_seg, "feature.json"), {"factory": {"issues": {"T-99": 954}}})` to
`write_json(os.path.join(harness_seg, "feature.json"), {"factory": {"issues": {}}})`. Line 382's
`depends_on=["T-99"]` fragment left intact — grepped before/after, byte-identical — and the kaya
sibling line 377 also confirmed untouched.

- `5g` marker: `ok    BUG-1290 5g: collapsing the issue-map cache key to feature-only breaks 5b's property`
- `5b` marker: `FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed`
- summary: `1 of 125 FAILING.`
- exit code: `1`
- failing-marker count: **1**, and it is `5b` alone (mirror of Arm A: the sole `grep -n '^FAIL'` hit is
  the `5b` line)

**Confirms engineering's Arm B claim exactly (the inverse)**: `5b` FAILs, `5g` stays `ok`.

### §3 adjudication — `5g` discriminates

`5g` reddens specifically when the fixture fragment it names (the harness segment's own
`depends_on=["T-99"]`, resolved through the harness segment's own issue map) stops being load-bearing
in the way its docstring claims (Arm A), and it does NOT redden under a different perturbation of the
same fixture tree that instead breaks the thing `5b` itself measures (Arm B empties the issue map that
`5b`'s *unmutated* run also depends on, so `5b` reddens directly and `5g`'s own mutant — which only
changes routing when a blocker check actually runs — has nothing left to prove once `5b`'s baseline is
already broken). Neither arm reddens both cases; neither arm reddens neither case. That is a genuine
pair, not a coincidence of one lucky perturbation: `5g` is load-bearing for exactly the fixture fragment
it names, and the pair as measured contains no `must_fix`.

### Record correction

Cycle-9's DIGEST restated Arm A as "5b FAIL / 5g ok" while this note's own artifact (line 88 above)
said "5b ok / 5g FAILs". Measured now, twice, independently: **the artifact's wording was right, the
DIGEST's was wrong** (transposed). This send-back's own DIGEST carries the corrected pairing.

### Working tree after this send-back

Both `/tmp` copies created via `rsync -a --exclude='.git'`, mutated, run, then destroyed with
`rm -rf` — confirmed absent by directory glob immediately after. No `.git` was ever copied into either
one (this cycle skipped last cycle's `cp -r`/`shutil.rmtree` workaround entirely by excluding `.git`
up front, avoiding the write-guard's worktree-shaped false-positive noted in cycle 9). Real worktree
`git status --porcelain`, taken after all copies were destroyed:
```
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b16.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/qa-2026-09-06-09-validator.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-08-eng-b16.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-08-eng-b16-recheck.md
```
Identical to cycle 9's snapshot — this note's own further edits are the only change since, and they
land in the already-untracked note file above. Nothing committed, no production file touched.
