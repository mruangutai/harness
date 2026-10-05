# UAT — FEAT-2081 CI shard structure audit
status: draft              # draft | ready | passed | failed — only the user sets passed/failed
branch: feat/FEAT-2081-ci-shard-structure-audit
review_sha:                # fill when pinned; authored against HEAD 0ebdaef7ed90787c25fbe2d584087c6bdfcf77ad (T-05 SPEC.md edit uncommitted)
uat_criteria: SC-09, SC-10 (verify: uat). SC-04/SC-05 (inspection) and SC-06 (automated) are prerequisites recorded below.
estimate: ~45 min wall clock (7 Actions runs at ~3–5 min each); ~20 min of attention.

This is a script and evidence ledger, not a pass report. Every blank field is filled from an observed
Actions run or a local command the reader can re-run. No local smoke run, workflow parse, synthetic
result or inferred timing substitutes for SC-09 or SC-10.

## Gate to `ready` (harness-uat step 2)

`status` may move from `draft` to `ready` only when every row below is observed green.

| prerequisite | source | observed |
|---|---|---|
| harness-qa verdict at review_sha | `notes/` QA verdict file | |
| harness-code-reviewer verdict at review_sha | `notes/` review verdict file | |
| SC-04 pinned inspection | "Reviewer inspection" section below | |
| SC-05 pinned inspection | "Reviewer inspection" section below | |
| SC-06 equivalence + single traversal (automated) | `notes/qa-structure-audit-equivalence.md` (summarised below) | met locally at the T-03 pins; reconfirm review_sha changes neither audit path (L-00) |
| Main's final whole-suite validation after all changes land | Main | |

## Already-met local evidence (referenced, not re-run)

### SC-06 — equivalence and single traversal (`notes/qa-structure-audit-equivalence.md`)
- Pins: baseline checker `8e0b9e900986d4e0e07414ffedb1c09a2a6a7554` (sha256 prefix `cfe27a19ad3e5156`); post-change checker sha256 prefix `608c6446013d6862`; host Apple M3 Pro, 12 cores, macOS, Python 3.14.5.
- Equivalence: 53 inputs (real tree + every structure-lock mutant/fixture), both entry paths — the in-process `consolidation_findings`/`feat62_findings`/`broad_catch_findings` calls used by `tests/integration/test-checker-structure-locks.py`, and the `check-plan-routes.py --consolidation-audit` CLI (exit, stdout, stderr byte-for-byte): `non_identical=[]`, `suite_failures=[]`.
- Instrumented traversal counts (instrumentation runs, separate from wall time), same fixture tree:

| entry path | checker | parsed trees (physical) | embedded | node occurrences | child-node visits | nodes not visited exactly once |
|---|---|---|---|---|---|---|
| in-process `consolidation_findings` | pre 8e0b9e90 | 210 | 2 | 432491 | 557328 | 30442 |
| in-process `consolidation_findings` | post | 99 | 1 | 202781 | 202781 | 0 |
| CLI `--consolidation-audit` | pre 8e0b9e90 | 210 | 2 | 432491 | 557328 | 30442 |
| CLI `--consolidation-audit` | post | 99 | 1 | 202781 | 202781 | 0 |

- Red-first, both paths: `CHECK_PLAN_ROUTES_BIN=<8e0b9e90 worktree>/.claude/skills/harness/bin/check-plan-routes.py python3 tests/integration/test-structure-audit-single-pass.py` → exit 1, 9 failures (in-process and CLI "every node visited exactly once" and "parses no source twice"); post-change → exit 0. Independent per-rule violating witnesses: the 53-input table rows with nonzero findings for each lock family (QA file lines 36–94).
- OQ-03 is settled: `check-state.py` is not an audit entry path; no real-entry prerequisite remains.

### SC-10 local part — structure-audit wall time (`notes/evidence-T-03.md`, amendment section)
Same host, interleaved, 3 runs each, baseline = detached worktree at `8e0b9e90`, current = feature worktree after `d89f9b23` (test-side parse cache retained by operator ruling 2026-10-04). All runs exit 0; structure-locks output stable across runs (`cmp`).

| path | baseline samples (s) | current samples (s) | median baseline → current |
|---|---|---|---|
| `tests/integration/test-checker-structure-locks.py` (in-process calls) | 3.03, 3.05, 3.07 | 2.56, 2.58, 2.57 | 3.05 → 2.57 |
| `check-plan-routes.py --consolidation-audit` (CLI) | 0.63, 0.64, 0.64 | 0.37, 0.36, 0.36 | 0.64 → 0.36 |

Both medians are lower; all three samples are recorded, none selected.

**Gap against T-06's controlled-run requirement (not hidden):** the recorded method ran each side
inside its own checkout, so [INFERENCE from the recorded method] each side audited its own `bin/`
(8e0b9e90's versus d89f9b23's) — same host and Python, but not one fixed corpus, and the "current"
side is pinned to d89f9b23's audit files, not yet to review_sha. L-00 closes the pin question;
L-01 is the same-corpus record, a mandatory user-executed UAT step for SC-10; until it is
filled, the same-corpus clause of SC-10 is not evidenced.

### L-00 — audit paths unchanged between the measured commit and review_sha
`git diff --stat d89f9b23 <review_sha> -- .claude/skills/harness/bin/check-plan-routes.py tests/integration/test-checker-structure-locks.py tests/integration/test-structure-audit-single-pass.py`
(Observed empty from d89f9b23 to 0ebdaef7 at authoring time.)
- output at review_sha:

### L-01 — controlled same-corpus structure timing (local; user-executed, required for SC-10)
Same host, same `python3`, one fixed private corpus (a clean detached worktree of review_sha), both
checkers pointed at it, interleaved baseline/current, three samples each, no sample discarded.
```bash
REVIEW_SHA=<review_sha>
git worktree add --detach /tmp/feat2081-cur  "$REVIEW_SHA"
git worktree add --detach /tmp/feat2081-base 8e0b9e900986d4e0e07414ffedb1c09a2a6a7554
BASE=/tmp/feat2081-base/.claude/skills/harness/bin/check-plan-routes.py
CUR=/tmp/feat2081-cur/.claude/skills/harness/bin/check-plan-routes.py
mkdir -p /tmp/feat2081-l01 && cd /tmp/feat2081-cur && python3 --version && uname -a
TIMEFORMAT=%R
for i in 1 2 3; do
  for side in base cur; do
    bin=$BASE; [ "$side" = cur ] && bin=$CUR
    { time env -u CLAUDE_PROJECT_DIR -u HARNESS_PROJECT_DIR CHECK_PLAN_ROUTES_BIN="$bin" \
        python3 tests/integration/test-checker-structure-locks.py >/tmp/feat2081-l01/locks-$side-$i.out 2>&1; \
      echo "exit $?" >>/tmp/feat2081-l01/locks-$side-$i.out; } 2>>/tmp/feat2081-l01/locks-$side.times
    { time env -u CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR=/tmp/feat2081-cur \
        python3 "$bin" --consolidation-audit >/tmp/feat2081-l01/cli-$side-$i.out 2>&1; \
      echo "exit $?" >>/tmp/feat2081-l01/cli-$side-$i.out; } 2>>/tmp/feat2081-l01/cli-$side.times
  done
done
cat /tmp/feat2081-l01/*.times
for i in 1 2 3; do cmp /tmp/feat2081-l01/cli-base-$i.out /tmp/feat2081-l01/cli-cur-$i.out && echo "cli output identical $i"; done
grep -h '^exit' /tmp/feat2081-l01/locks-*.out | sort | uniq -c
git worktree remove /tmp/feat2081-cur && git worktree remove /tmp/feat2081-base
```
- host / python3:
- locks test baseline samples (s): ; median:
- locks test current samples (s): ; median:
- CLI baseline samples (s): ; median:
- CLI current samples (s): ; median:
- CLI exit/stdout/stderr identical base vs current (3 × `cmp`):
- locks test exit 0 on every sample (both sides):
- expect: both current medians are lower than their baseline medians.
  result:

## Reviewer inspection — SC-04 / SC-05 (`git show <review_sha>:.github/workflows/tests.yml`)
Line hints are at 0ebdaef7 (tests.yml is unchanged by T-05); record the line at review_sha.

| item | hint at 0ebdaef7 | line at review_sha | holds? |
|---|---|---|---|
| SC-04 required context is job ID `integration`, no `name:` key | 403–404 | | |
| SC-04 `integration` `if: always()` at job level | 410 | | |
| SC-04 `integration` `needs: [checks, integration-shards]` | 405 | | |
| SC-04 parallel matrix on ubuntu-latest, `fail-fast: false`, `shard: [1, 2, 3, 4]` | 353, 357, 359 | | |
| SC-04 failed/skipped/cancelled dependency still reaches validator (`Validate shard completeness` `if: always()`, results passed literally) | 433, 436–437 | | |
| SC-04 trigger asymmetry: `push` only `main`, `pull_request` unfiltered | 19–22 | | |
| SC-04 no cancel-in-progress on main | 28–29 | | |
| SC-05 Unit suite → `checks` → `CHECKS_RESULT` → validator accepts only `success` | 97, 436 | | |
| SC-05 Validate feature execution state → same chain | 106, 436 | | |
| SC-05 Plan-route gate → same chain; summary and `examined` checks intact | 156–206, 436 | | |
| SC-05 Canonical-reader audit → same chain; summary/0-file checks intact | 218–234, 436 | | |
| SC-05 Instruction-path gate → same chain | 236–252, 436 | | |
| SC-05 Layout gate → same chain; summary/examined checks intact | 262–310, 436 | | |
| SC-05 Repository-state gate → same chain; tracked-corpus check intact | 328–348, 436 | | |
| download outcome must be `success` | 438, 448–451 | | |
| tested SHA is `github.sha` | 440, 445 | | |

reviewer / date:

## Live UAT — SC-09 and SC-10 (user executes)

### Setup
Mutations live only on a throwaway branch in a separate worktree, never in the feature worktree
and never on main. Repo: `mruangutai/harness`.
```bash
REVIEW_SHA=<review_sha>
git worktree add -b uat/feat2081-throwaway /tmp/feat2081-uat "$REVIEW_SHA"
cd /tmp/feat2081-uat
R=mruangutai/harness
```
Rules for every case:
- **Never run `gh run cancel`** (or the REST `runs/{id}/cancel` / `force-cancel` endpoints) and never press "Cancel workflow": each cancels the whole run, which is outside SC-09 (OQ-02). Nothing on main is cancelled.
- **Wait for the previous run to finish before pushing the next commit.** The concurrency group cancels an in-flight PR run when its branch is re-pushed (`cancel-in-progress` is true off main); that whole-run supersession would void the case.
- On `pull_request` the tested SHA is `github.sha`, the merge commit of `refs/pull/N/merge`, not the pushed head. Record both.

Find, wait for and record a case (run after each push; `CASE` is U-01 … U-08):
```bash
sleep 15                                       # let GitHub register the pull_request run
HEAD_SHA=$(git rev-parse HEAD)
RUN=$(gh run list -R $R -w tests.yml -c "$HEAD_SHA" --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN" -R $R                       # watching only; never cancels
gh run view "$RUN" -R $R --json url,headSha,attempt,status,conclusion,createdAt,updatedAt
gh run view "$RUN" -R $R --json jobs --jq '.jobs[]|[.databaseId,.name,.conclusion,.startedAt,.completedAt]|@tsv'
gh api repos/$R/actions/runs/$RUN/jobs --jq '.jobs[]|[.name,(.labels|join(","))]|@tsv'
AGG=$(gh run view "$RUN" -R $R --json jobs --jq '.jobs[]|select(.name=="integration")|.databaseId')
gh run view -R $R --job "$AGG" --log | grep -E 'INCOMPLETE:|MALFORMED:|PASS integration:|FAIL integration:|::error::'
mkdir -p /tmp/feat2081-uat-evidence/$CASE
gh run download "$RUN" -R $R -p 'integration-manifest-*' -D /tmp/feat2081-uat-evidence/$CASE
python3 - /tmp/feat2081-uat-evidence/$CASE <<'PY'
import json, pathlib, sys
for p in sorted(pathlib.Path(sys.argv[1]).rglob("*.json")):
    d = json.loads(p.read_text())
    print(p.parent.name, {k: d[k] for k in ("tested_commit", "kind", "shard_index", "shard_count", "runner_exit")},
          "selected", len(d["selected_files"]), "completed", len(d["completed_files"]),
          "nonzero", [r["path"] for r in d["completed_files"] if r["returncode"] != 0])
PY
gh pr checks "$PR" -R $R --required
```
Full selected/completed file lists stay in the downloaded manifests and the run's artifacts; record
the summary line per manifest and any file named by a case.

Record block used by every case below:
```
head commit (pinned):
tested SHA (manifest tested_commit / validator --commit):
Actions URL:
run attempt:
run created / integration completed (UTC):
per-job result: checks= ; shard 1= ; shard 2= ; shard 3= ; shard 4= ; integration=
runner labels (all ubuntu-latest?):
manifest identity + file-list summary (one line per manifest; "absent" if none):
validator lines:
required integration conclusion (gh pr checks --required):
```

### U-01 (SC-09) — passing positive control
```bash
git commit --allow-empty -m "UAT U-01 positive control (throwaway, do not merge)"
C1=$(git rev-parse HEAD); git push -u origin uat/feat2081-throwaway
gh pr create -R $R --draft --base main --head uat/feat2081-throwaway \
  --title "UAT FEAT-2081 throwaway — DO NOT MERGE" --body "FEAT-2081 SC-09/SC-10 UAT; closed unmerged afterwards."
PR=$(gh pr view uat/feat2081-throwaway -R $R --json number --jq .number)
```
Then pick the files for U-02 and U-04 from this run's shard logs (`selected <path>` lines, one job per
shard): `gh run view -R $R --job <shard job id> --log | grep ' selected tests/integration/'`.
(Local hint only, from the checked-in weights at 0ebdaef7: `tests/integration/test-onboarding-split.py`
→ shard 4, `tests/integration/test-panel-findings.py` → shard 3. The run log is authoritative.)
- record block:
- F2 (U-02 file) and its shard from this run's log:
- F4 (U-04 file):
- expect: the validator prints `PASS integration: <N> expected files completed exactly once across 4 shards at <tested SHA>`.
  result:

### U-02 (SC-09) — one failing test in one shard
```bash
F2=tests/integration/<file from U-01>
printf 'raise SystemExit("FEAT-2081 UAT U-02: deliberate failure")\n' > "$F2"
git commit -am "UAT U-02 failing test in one shard (throwaway)"; git push
```
- record block:
- shard holding F2 (from this run's `selected` lines; must match U-01):
- expect: the required `integration` job concludes `failure` (not `success`, not pending), with a validator line naming `F2 returned 1`.
  result:

### U-03 — dropped (operator ruling, 2026-10-05)
GitHub has no per-job cancel in its UI or REST API (only whole-run cancel/force-cancel; community
discussion #67407), so a live shard-only cancellation cannot be produced. The user dropped this case;
a `cancelled` shard result is covered by SC-02's automated rejection in T-02 (BRIEF OQ-02, amended).

### U-04 (SC-09) — one discovered test omitted from every shard
Restore F2, then delete F4 inside each shard's workspace only: the tested commit still
contains F4, so the validator's independent discovery (`git ls-tree` of the tested SHA) expects it.
In `.github/workflows/tests.yml`, directly before `- name: Integration suite (shard ${{ matrix.shard }}/4)`, add
```yaml
      - name: UAT U-04 omit one discovered file (throwaway only)
        run: rm tests/integration/<F4 file name>
```
```bash
git checkout "$C1" -- "$F2"
F4=tests/integration/<file from U-01>
# apply the step above, naming "$F4"
git commit -am "UAT U-04 omit one discovered test from every shard (throwaway)"; git push
```
After the run, confirm the tested SHA contains F4:
`gh api "repos/$R/contents/$F4?ref=<tested SHA>" --jq .path`
- record block:
- independent expected file: `gh api` output above:
- F4 absent from all four manifests' `selected_files` and `completed_files` (yes/no, per shard):
- expect: the required `integration` job concludes `failure`, with the validator line `INCOMPLETE: <F4>: omitted (no completed record in any shard)`.
  result:

### U-05 (SC-09) — restored exact passing coverage (= SC-10 run P1)
```bash
git checkout "$C1" -- .github/workflows/tests.yml
git commit -am "UAT U-05 restore exact coverage (throwaway)"; git push
git diff --exit-code "$C1" HEAD && echo "tree identical to C1"
```
- record block:
- `git diff --exit-code C1 HEAD` output:
- expect: the required `integration` job concludes `success`, with `PASS integration: <N> expected files completed exactly once across 4 shards`, N equal to U-01's N.
  result:

### U-06 … U-08 (SC-10) — three consecutive passing four-shard runs below 100 seconds
P1 is U-05's run. P2 and P3 are the next two runs on the same restored tree, each pushed only after
the previous one finished. These are the first three runs after restoration; none is discarded or
re-run, and the fastest is not selected.
```bash
git commit --allow-empty -m "UAT SC-10 P2 (throwaway)"; git push    # wait, record, then:
git commit --allow-empty -m "UAT SC-10 P3 (throwaway)"; git push
```
Critical path = earliest `integration-shards` job `startedAt` → `integration` job `completedAt`. It
includes runner setup, the dependency wait on `checks` if that is the later finisher, artifact
transfer and aggregation. `checks` timing is recorded separately so an unchanged gate bottleneck is
visible.
```bash
gh run view "$RUN" -R $R --json jobs --jq '
  ([.jobs[]|select(.name|startswith("integration-shards"))]) as $s
  | (.jobs[]|select(.name=="integration")) as $a
  | (.jobs[]|select(.name=="checks")) as $c
  | {shards: ($s|length),
     critical_path_s: (($a.completedAt|fromdateiso8601) - ([$s[].startedAt|fromdateiso8601]|min)),
     slowest_shard_s: ([$s[]|((.completedAt|fromdateiso8601)-(.startedAt|fromdateiso8601))]|max),
     checks_s: (($c.completedAt|fromdateiso8601)-($c.startedAt|fromdateiso8601)),
     checks_completed: $c.completedAt, last_shard_completed: ([$s[].completedAt]|max),
     integration_started: $a.startedAt}'
```

| run | head commit | tested SHA | Actions URL | attempt | 4 shards, all ubuntu-latest | integration | critical path (s) | slowest shard (s) | checks job (s) | checks later than last shard? |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 (U-05) | | | | | | | | | | |
| P2 | | | | | | | | | | |
| P3 | | | | | | | | | | |

- expect (U-06): P1 concludes `integration` = `success` with a critical path below 100 seconds.
  result:
- expect (U-07): P2 concludes `integration` = `success` with a critical path below 100 seconds.
  result:
- expect (U-08): P3 concludes `integration` = `success` with a critical path below 100 seconds.
  result:

### Baseline for comparison (supplied; observed, not re-run)
Run 37264903064 — https://github.com/mruangutai/harness/actions/runs/37264903064 — the brief's pin
`b046bdfed9fa262a25f53a41d566db2b90cd140b` (the `source_commit` of `tests/integration/integration-durations.json`;
the run's PR head is `8c18eec085fdcf8e382c0bbb5c09f42131e943eb`), one unsharded `integration` job.
- **170 s baseline = pool time**: the Integration suite step's own line `pool: 4 workers, 73 files, 170.49s wall`
  (`gh run view 37264903064 --repo mruangutai/harness --log`), rounded to the brief's 170. It is not a
  full-job figure and excludes setup, unit suite and gates.
- For context only, observed with `gh run view 37264903064 --json jobs` on 2026-10-05: the job ran
  04:45:31Z → 04:49:02Z (211 s), Integration suite step 04:46:06Z → 04:48:57Z.
- Note the sharded critical path includes setup and aggregation, so comparing it with the 170 s pool
  figure is conservative against the new design.
- comparison (user): P1/P2/P3 critical paths vs 170 s:
  result:

### Teardown
```bash
gh pr close "$PR" -R $R --delete-branch
git -C <feature or main checkout> worktree remove /tmp/feat2081-uat
```
- PR closed unmerged (URL):

## Sign-off (user only)
- SC-09 (U-01 … U-05):
- SC-10 live (U-06 … U-08 + baseline comparison):
- SC-10 local structure timing (L-01, same-corpus; the evidence-T-03 amendment is context only):
- final status (`passed` / `failed`), user, date:
