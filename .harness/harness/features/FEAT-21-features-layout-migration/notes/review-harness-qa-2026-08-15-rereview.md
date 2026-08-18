# QA re-review — FEAT-21, pinned `4a98cc4` — 2026-08-15

**PASS. All four jobs measured, not read. The must-fix delivery holds behaviorally, SC-10's
discriminating mutant genuinely reddens the case, the walk-up flatten preserves semantics on
all three depths, and the re-measured `tests.yml` numbers are true at HEAD.** No new blocking
finding. One structural observation on the `fpath` fallback, advisory only.

Ground-pin: `HEAD 4a98cc4d8310939971f0e523d0689f4d309a22c9`, branch
`feat/FEAT-21-features-layout-migration`. `git log --oneline ea937b1..4a98cc4` → 10 commits
(`d033b9d`, `5c39f8c`, `649b36b`, `3df7002`, `b1d3925`, `835692a`, `1f717da`, `b517049`,
`1c95e81`, `4a98cc4`) — the dispatch's four-commit framing covers only the source-bearing set
(`d033b9d`, `b1d3925`, `4a98cc4`) plus close-out bookkeeping, which is the rest; consistent with
the prior panel's own correction of an undercounted range (`review-harness-qa-2026-08-14-panel.md`
Job 2). Read-only on the working tree throughout: `git status --porcelain` on every probed
production file (`check-state.sh`, `gh-sync.py`, `layout_migration.py`, `tests.yml`) is empty.
All mutation/fixture work ran on `cp -R` copies or `Write`-created fixtures under
`/private/tmp/.../scratchpad/`, never in place.

## JOB 1 — must-fix delivery, proven behaviorally

**(a) Staged fixture violation, ran the REAL `check-state.sh`, asserted the label resolves.**
Fixture: `<scratch>/job1/fixture/.harness/harness.json` +
`.harness/harness/features/FEAT-XX-fixture/BRIEF.md` with no `## Approval` section.
`CLAUDE_PROJECT_DIR=<scratch>/job1/fixture bash check-state.sh` emits:

```
VIOLATION  .harness/harness/features/FEAT-XX-fixture/BRIEF.md has no '## Approval' section — cannot tell if the goal is signed.
```

`test -e` on the leading path token, from the fixture's own cwd: **resolves** (`RESOLVES: yes`).
The label opens.

**(b) KEYS stayed bare — confirmed by source read and by live measurement.** `briefs`, `plans`,
`plan_docs`, `states` are all keyed by `os.path.basename(os.path.dirname(p))` — bare basenames,
unqualified (`check-state.sh:64-86`). Ran the real population logic against this repo's own
`.harness/` at HEAD: **12 features have a `plan.yaml`, `plan_docs.get(_feat)` returns a `dict`
for all 12 (hits=12, misses=0 among those 12), never `None`.** The 9 features with no
`plan.yaml` correctly miss (they're on `PLAN.md` or have neither) — that miss is the documented
`continue` branch, not a bug. `INV-26`'s station-mirror comparison at `check-state.sh:1160-1162`
derives `_feat` the identical way (`os.path.basename(_fp)` over the same glob shape), so the
lookup **is reached** with real data whenever a plan.yaml exists — not vacuously skipped for
every feature as D-08's hazard describes for the un-fixed shape.

**(c) `fpath` fallback probed directly.** Reached it via a feature name absent from `_feat_dirs`
(`fpath("NOT-A-REAL-FEAT", "BRIEF.md")` → `.harness/?/features/NOT-A-REAL-FEAT/BRIEF.md`). What
an operator would see: a literal `?` segment that does not resolve to any real file — worse than
the pre-fix bare label in one sense (it *looks* qualified but is a dead path). **Structural
observation, not a regression:** every top-level feature-discovery glob in `check-state.sh` — 15
call sites, grepped exhaustively (`grep -c 'glob.glob(...)'` on the file returns 16 total; the
16th, `line 309`, globs `runs/*` under a feature dir already found by one of the 15, not an
independent discovery path) — uses the shape `.harness/*/features/*`. So **every** `feat`/`_feat`
value the script ever binds already comes from a migrated-shape directory. A project still on the legacy `.harness/features/*`
layout is invisible to every glob in this script (empty discovery, not a `?`-labelled finding), so
`fpath`'s fallback branch is reachable only via direct invocation like this probe, not through any
live code path the script exercises today. Advisory, not blocking — worth a backlog note if it
isn't already covered by B-1/B-3 (nothing stages a legacy-only tree either).

## JOB 2 — SC-10 parity, re-run the discriminating mutant

Scratch copies of `.claude/skills/harness/bin/` at `<scratch>/job2/bin-copy` (mutated) and
`<scratch>/job2/bin-clean` (unmutated control), both `cp -R` from the tracked tree at `4a98cc4`.

**Mutation applied:** `check-state.sh`'s MIXED branch, dropped the blamed-reader clause:
```
-  bad.append(f"INV-27 {_sname}: layout is MIXED — evidence {_ev}; "
-             f"readers {_lmod.blame_text(_srep)}. {_lrem}")
+  bad.append(f"INV-27 {_sname}: layout is MIXED — evidence {_ev}; "
+             f"{_lrem}")
```
Confirmed applied: `diff` against the tracked source shows exactly this one-line change, nothing
else.

**Mutated copy:** `python3 test-layout-migration.py` → exit **1**.
`FAIL - case 20 parity: MIXED, one migrated reader on legacy evidence — real gate and render
name the same reader set` — GATE output no longer names `readers ...`, CI output still does.
**RED, and RED on exactly the named case.**

**Unmutated control copy:** `diff` against tracked source empty. `python3
test-layout-migration.py` → exit **1**, but the *only* failures are the pre-existing,
already-documented case-1 scratch-location artifacts (`non-zero feature-dir count`, `non-zero
reader-file count`, `X+Y+Z == 2`) — a scratch tree has no `.harness/factory/fleet.yaml` marker, so
case 1 fails at baseline regardless (matches the prior panel's own framing,
`review-harness-qa-2026-08-14-panel.md` Job 3). **All ten case-20 parity assertions are `ok`,
including the MIXED one.** The mutant reddens the case; the clean tree does not. **The
discriminating mutant is genuine — not vacuous.**

## JOB 3 — walk-up behavioral equivalence after the `/simplify` flatten

Three staged trees under `<scratch>/job3/`, ran the real `gh-sync.py open <feat-dir>` against
each (with `github.sync: false` in `harness.json` so the skip message names which file was found,
proving root resolution without needing `gh`):

| Tree | `feat_dir` | Output | Interpretation |
|---|---|---|---|
| legacy depth (`<tmp>/.harness/features/FEAT-XX`, manifest+config at `<tmp>/.harness/`) | resolved root `<tmp>` | `gh-sync: SKIP — github.sync is not enabled for this project` | root found `<tmp>/.harness/harness.json` — correct |
| migrated depth (`<tmp>/.harness/harness/features/FEAT-XX`) | resolved root `<tmp>` | same message | same — correct |
| un-onboarded (`<tmp>/a/b/c/FEAT-XX`, no `team-config.yaml` anywhere up to `/`) | fallback arithmetic root | `gh-sync: SKIP — no .harness/harness.json — project not onboarded` | the message printed today, per the comment at `gh-sync.py:735-739` |

All three exit 0 (a `skip()`, not a crash). The flattened `while` loop (`gh-sync.py:740-743`)
terminates correctly at either a found manifest or filesystem root (`_d == os.path.dirname(_d)`);
the un-onboarded case walked all the way to `/` and fell through to the `else` (old three-level
arithmetic), reaching `skip()` exactly as the comment says. **Termination and fallback
reachability both hold; semantics unchanged by the flatten.**

## JOB 4 — suites and re-measured numbers

**Suite confirmation, run once:**
- `run-unit-tests.sh --kind unit` → exit **0**. 15/15 suites `PASS test-*.py`, 0 `FAIL`. 97
  `PASS <case>` lines (case-level), 706 `ok` lines (case-level, other convention). **No movement**
  from the precommit round's "97 unit" figure — same number, same convention
  (`review-harness-qa-2026-08-14-precommit.md` used the 97 count; the panel's "706 ok" is the
  same suite counted the other way — both conventions checked here and both match exactly).
- `run-unit-tests.sh --kind integration` → exit **0**. 12/12 suites PASS, 0 FAIL, 89 `PASS`
  lines, 634 `ok` lines. **No movement** — matches the panel's "12/12 suites (634 ok)" exactly.

**`tests.yml` re-measured numbers, verified independently at `4a98cc4`:**
- `git ls-files '.harness/harness/features/*/PLAN.md' '.harness/harness/features/*/plan.yaml' | wc -l`
  → **20**, exact match to the comment's claim.
- `git check-ignore -v .harness/harness/features` → **exit 1** (not ignored), exact match.

Both are true at HEAD, not just asserted in the comment.

**Layout detector and state gate, discovery counts reported (not just exit codes):**
- `layout_migration.py .` → exit 0: `features: CLEAN — evidence migrated`, `docs: CLEAN —
  evidence legacy`, **`examined 21 feature dir(s), 1 doc root(s), 7 reader file(s)`** — non-zero
  on all three, a real sweep, not an empty one exiting 0 by vacuity.
- `check-state.sh` → exit 0, **zero `VIOLATION` lines**, ~40 `note`-severity lines spanning at
  least 10 distinct `FEAT-*` directories (`FEAT-02`, `FEAT-05`, `FEAT-06`, `FEAT-08`, `FEAT-09`,
  `FEAT-13`, `FEAT-14`, `FEAT-15`, `FEAT-19`, `FEAT-20`, `FEAT-21`) — several of them carrying the
  segment-qualified `.harness/harness/features/FEAT-NN/...` label shape from D-08, each resolving
  to a real file. A non-zero, multi-feature discovery set, not an empty sweep.

## Already-ruled items — no re-file

Nothing in this range regressed any sanctioned survivor (`harness-init/SKILL.md`, `templates/**`,
the four historical `check-plan-routes.py` comments, `FEAT-99-x`, unit-9 files, `docs/**`), the
branch-gate segment literal, the segment-level readability guard, the walk-up manifest choice, or
the two-segment fixtures. Confirmed by re-grepping the same surfaces touched by this range's
commits (`check-state.sh`, `gh-sync.py`, `tests.yml`) — no new hits outside the already-ruled set.

## SC evidence

- **SC-10** — `test-layout-migration.py` case 20 parity, mutation-proven both directions: gate-side
  (prior panel, `check-state.sh`'s MIXED clause) and render-side (prior panel,
  `layout_migration.render()`); **gate-side re-proven independently here** at `4a98cc4` with the
  exact mutation named in this dispatch (RED on mutated copy, GREEN on clean copy).
- **D-08** — bare keys: `check-state.sh:64-86` (source) + live `plan_docs.get(_feat)` measurement
  above (12/12 hits, 0 misses among plan.yaml-bearing features). Qualified labels:
  `check-state.sh` fixture run above, `test -e` on the extracted path token.
- **T-10 walk-up** — `gh-sync.py:740-753`, all three depth/onboarding cases run behaviorally
  above, real binary, no mocking.
- **`tests.yml` re-measurement** — both `git ls-files` and `git check-ignore` commands re-run
  independently, exact match to the comment's claim.

## Coverage gaps (Phase 1 vs Phase 2)

None new opened by this range. The dispatch's four jobs are all proven behaviorally rather than
by re-reading the prior notes; no Phase-1-derivable surface (approval-gate enforcement, INV-26
station parity, walk-up root resolution, the CI comment's own numeric claims) is left unmeasured.
Standing gaps carried from the prior segments (B-1 nothing stages two repository segments, B-2/B-3
zero-discovery guards, ~181/186 test cases unprobed) are unchanged by this range and not this
dispatch's to close.

## New findings

- **Advisory, not blocking.** `fpath`'s fallback (`.harness/?/features/<FEAT>/...`) is reachable
  only by direct call today — every discovery glob in `check-state.sh` already requires the
  migrated shape, so a legacy-only project produces empty discovery rather than a `?`-labelled
  finding. Worth folding into B-1/B-3's "nothing stages a non-migrated tree" framing rather than
  filing as its own row.

artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-15-rereview.md
