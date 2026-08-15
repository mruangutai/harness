# QA precommit sweep — FEAT-21, T-09 gate — 2026-08-14

Ground-pin confirmed: `HEAD ea937b17e132fdcc7780cbb5a65ab579eb57bb7d`, branch
`feat/FEAT-21-features-layout-migration`, `.harness/features` absent. All work below is READ-ONLY —
no source file was edited; mutation probes ran on a scratch copy at
`/private/tmp/.../scratchpad/bin-copy`, confirmed reverted/discarded, main tree untouched
(`git status --porcelain` on every probed file shows only the pre-existing target diff).

## Verdict: no blocking finding. Two advisory leftovers, not on the sanctioned list.

## JOB 1 — leftovers sweep

**(a) Literal pass.** `git grep -n '\.harness/features/'` outside `docs/**` returns hits in: sanctioned
survivors (harness-init/SKILL.md, templates/**, four check-plan-routes.py historical comments,
gh-sync.py's own historical-bug comment, layout_fixtures.py stubs, layout_migration.py's own
READER_TABLE regex literals, the M-is-asserted block in tests.yml — all three substitutions verbatim
correct: "Not a live hole as of 62fef85, pre-move:", "all 19 plan files", "Both halves measured at
62fef85, pre-move, not assumed:" — and every `.harness/harness/features/<FEAT>/**` historical
feature-record file, which is prior-feature narrative, not code that resolves a path), plus two
**not on the "already ruled" list**:

- **`.harness/expertise/harness-pm.md:7`** — "the `## Approval` section of a shipped plan under
  `.harness/features/`" — a stale path in **injected, per-spawn Expertise** (loaded at every
  harness-pm spawn, unlike `.harness/harness/features/**` feature-record narrative which is inert
  history). Advisory, not blocking: it is prose illustrating a pattern, not a mechanism that
  resolves anything, but it is exactly the kind of "an agent following its own written
  instructions" surface REQ-04 cares about, and this file was missed.
- **`test-harness-yaml-corpus.py:232`** — a synthetic fixture string
  `'writes: [".harness/features/*/BRIEF.md ## Approval", "x/**"]\n'` used only to prove a
  correctly-quoted/folded line is not flagged by the YAML-safety scanner. Self-consistent, resolves
  nothing on disk (same shape as the sanctioned `test-validate-feature-json.py` FEAT-99-x survivor),
  just not itself named on the "already ruled" list. Advisory only — harmless.

`check-state.sh:51`'s comment ("`.harness/features/<FEAT>/{BRIEF,PLAN}.md`") is stale relative to the
migrated code three lines below it, but T-05's verify only binds the code pattern, not comments, and
this is the same "narrative, true as written" class T-04's four comments were explicitly exempted
under — not filing it as a new finding, noting it for completeness.

**(b) Arithmetic pass**, run independently over `.claude/skills/harness/bin/` before reading T-09's
own note:
- P1 `os.path.join(...,"..",...,"..",...)`: all hits are 4-level bin→repo-root climbs (unrelated to
  the features segment; they resolve `REPO_ROOT`, stable regardless of feature layout) — no finding.
- P2 `os.path.join(X, ".harness", ...)`: `factory_config.harness_root()`'s use, `check-plan-routes.py`'s
  manifest probe, `check-state.sh`'s 14 migrated joins, `gh-sync.py`'s new walk-up, `validate-feature-json.py`'s
  migrated glob, `layout_migration.py`/`layout_fixtures.py` (the detector itself) — all correct.
- P3 comma-joined tuples naming `"features"`: **one hit, `factory_claim.py:43`**
  (`FEATURES_ROOT = os.path.join(factory_config.harness_root(), ".harness", "features")`) — legacy
  shape, unmigrated.

I ran this independently before reading `notes/layout-boundary-2026-08-14.md`. **My result agrees
exactly with T-09's own depth sweep**: `factory_claim.py:43` is the one stale arithmetic resolver,
correctly classified there as sanctioned (unit-9 territory per "Already ruled", unreachable today —
no feature carries a factory block, the lane has never run) and routed to the next factory-lane unit
rather than fixed here. No disagreement with the note.

## JOB 2 — rename integrity

```
git ls-tree -r --name-only ea937b1 -- .harness/features/ | sed 's|^\.harness/features/|.harness/harness/features/|' | sort
  vs.
git ls-files -- .harness/harness/features/ | sort
```
Diff: **empty**. Tracked-file counts: **old 572, new 572** — exact match, nothing lost.

`git diff HEAD --name-status -M -- .harness/`: **567 R100** (pure renames) + 4 lower-similarity
renames + 1 A/1 D + 2 M, every one of them inside FEAT-21's own record
(`STATE.md`/`feature.json`/`plan.yaml`/`notes/layout-boundary...`/`observations/harness-orchestrator.md`)
or `.harness/logs/2026-08-14.md` and `.harness/team-config.yaml` — all expected: FEAT-21's own
bookkeeping is being live-edited by the concurrent orchestrator run (per the dispatch's own warning),
and `team-config.yaml`/the daily log are T-02's and normal bookkeeping's edits respectively. No
content lost outside that expected set.

`.harness/features` does not exist on disk (confirmed `ls`/`find`). `git status --porcelain --ignored
.harness/harness/features`: 567 `A` (matches the tracked-file count) + 5 `AM` (FEAT-21's own live
files) + **24 `!!` ignored run-dirs** (including FEAT-21's own) + **3 `??` untracked review notes**
under `FEAT-20-migration-detector/notes/` — both classes of untracked content the plan called out by
name travelled to the new location. Nothing remains at the old path.

## JOB 3 — suite confirmation + adequacy

**Confirmation run** (once, not eleven investigations):
- `run-unit-tests.sh --kind unit`: exit **0**, **97 PASS**, 0 FAIL.
- `run-unit-tests.sh --kind integration`: exit **0**, **89 PASS**, 0 FAIL. Named suites present and
  green: `test-check-state.py`, `test-check-plan-routes.py`, `test-gh-sync.py`,
  `test-validate-digest.py`, `test-check-domain.py`, `test-bash-write-guard.py`,
  `test-harness-yaml.py`, `test-factory-integration.py`.

**Adequacy — mutation-proven, all three genuinely discriminating (not vacuous):**

| Case | Mutation applied to scratch copy | Result | Verdict |
|---|---|---|---|
| `test-gh-sync.py` `migrated_depth` | reverted the walk-up loop to never execute (`while True:` → `while False:`), forcing the old fixed 3-level climb | **RED** — "project not onboarded" printed, exactly the pre-fix defect | discriminates |
| `test-gh-sync.py` `not_onboarded` | left the walk-up intact, changed only the fallback's SKIP message text | **RED** on the message-text assertion; `migrated_depth` stayed green (unaffected) | discriminates |
| `test-validate-feature-json.py` `migrated_depth`, conjunct 1 ("reports ONE file") | reverted `discover_paths`'s glob to the legacy `.harness/features/*/feature.*` shape | **RED** — "0 file(s)" | discriminates |
| `test-validate-feature-json.py` `migrated_depth`, conjunct 2 (scanning line names migrated glob) | reverted only the `print()` scanning-line text to the legacy shape (glob left migrated) | **RED** — scan still finds 1 file but the message names the legacy path | discriminates |
| `test-check-plan-routes.py` `case_22a_unreadable_feature_dir_exits_2`, the added `.harness/*/features/` conjunct | reverted only the unreadable-path message string to the legacy shape | **RED** on that conjunct alone (exit code and `FEAT-A` conjuncts stayed true) — reproduced via a standalone probe script driving the copy directly, since running the full suite copy in isolation hit unrelated `CLAUDE_PROJECT_DIR`/template-path dependencies outside the scratch tree | discriminates |

All five probes: mutation confirmed applied (diffed against the source), the probe process ran to
completion and printed a real PASS/FAIL, and reverting the mutation (fresh copy from the source file)
restored green. None of the three plan-cited assertions is vacuous.

## SC evidence

- SC-01/SC-03/SC-04: `run-unit-tests.sh --kind unit`/`--kind integration` exit 0, PASS counts above.
- SC-05: `find .harness -maxdepth 1 -iname 'features'` — empty; `.harness/features` absent (Job 2).
- SC-13: `test-gh-sync.py::migrated_depth`, `test-validate-feature-json.py::case_migrated_depth_discovery_scans_the_segment_layout` — both PASS in the live suite and both mutation-proven above.
- SC-14: `test-check-plan-routes.py::case_22a_unreadable_feature_dir_exits_2`'s added conjunct, `test-validate-feature-json.py::case_migrated_depth`'s conjunct 2 — both mutation-proven above; the third message (the CI workflow error string) is form-checked only, per the plan's own scoping, not by a suite — unmeasured by design, not a gap.
- SC-02/SC-07/SC-09/SC-11/SC-12: `verify: inspection` in the BRIEF — not re-derived here; T-09's own note and the Job 1/Job 2 evidence above are the record a reviewer reads for these.

## Open findings — routed, not blocking

1. `.harness/expertise/harness-pm.md:7` names the legacy path in injected, per-spawn Expertise.
   Advisory — narrative illustration, not a mechanism, but should be swept in a follow-up given it
   reaches every harness-pm spawn.
2. `test-harness-yaml-corpus.py:232` carries an unlisted (but harmless, self-consistent) legacy
   literal — same class as the sanctioned FEAT-99-x survivor, just not itself named. No action
   needed; noting for completeness.

Neither blocks T-09's commit.
