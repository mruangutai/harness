# QA Gate — FEAT-12 End copy-based distribution — d543809

## Verdict: PASS

Matrix satisfied. Both blocking judgment questions resolved in the implementation's favor,
each settled by a mutant, not by reading. One narrow, deliberate coverage gap found and
reported (not blocking — see Findings).

## Required kinds, derived independently

Matrix (`logic → unit`, `config/docs/scaffolding → []`) plus the SC-declared floor
(SC-02, SC-10 both name `integration` as evidence — the matrix alone doesn't carry that):

| Task(s) | change_type | Matrix requires | Also required (SC evidence) |
|---|---|---|---|
| T-07, T-10, T-13 | logic | unit | — |
| T-03, T-06 | config | none | — |
| T-08, T-11, T-12, T-14 | docs | none | — |
| T-01, T-02, T-04, T-05, T-09 | scaffolding | none | — |
| (SC-02, SC-10) | — | — | integration |

**Net requirement: unit + integration.** Both ran.

- `run-unit-tests.sh` (full): exit 0, 23/23 test scripts PASS, 0 FAIL. Baseline reproduced exactly.
- `run-unit-tests.sh --kind unit`: exit 0, 11 scripts PASS, 0 FAIL.
- `run-unit-tests.sh --kind integration`: exit 0, 12 scripts PASS, 0 FAIL — includes
  `test-check-plan-routes.py` (SC-02) and `test-upgrade-config.py` (SC-10).

matrix_ok: **true**.

## T-07 / T-10 / T-13 verify cross-check

All three `verify:` blocks quoted in the dispatch were run **verbatim** against `plan.yaml`'s
own text — byte-for-byte match, no mismatch. All three exit 0:
- T-07: `104` PASS-lines, `0` FAIL-lines (script-level count is 23; 104 includes per-case PASS
  lines from `test-no-distribution.py`'s own case output, confirmed by isolating
  `^PASS test-` = 23).
- T-10: `0` FAIL-lines.
- T-13: 18 case-level PASS lines, `0` FAIL/MISCONFIGURED, `29` unit-script PASS lines.

No BLOCKED.

## Mutation proofs (all run in `.claude/worktrees/qa-feat12-mutation`, a disposable worktree
off `d543809`; every mutation reverted with `git checkout --`, confirmed via
`git status --porcelain` before removing the worktree)

1. **Judgment 2 / Case 4, presence half.**
   - Mutant A: deleted only the override-precedence sentence from DEC-113's section
     (`resolves it first` → `handles it eventually`), heading survives. →
     `case4_presence_dec113_precedence_rule_survives` **FAILED** as required.
   - Mutant B: restored, then moved the literal string `resolves it first` **out of**
     DEC-113's section into DEC-102's section (DEC-113's own wording changed to a synonym
     that doesn't contain the substring). → **still FAILED** — confirms the assertion is
     scoped to the DEC-113 **slice** (`slice_section`), not a whole-file grep. Had the
     assertion been whole-file, mutant B would have passed vacuously.
   - Both mutants restored; `git status --porcelain` clean before removal.

2. **SC-10 — `test-upgrade-config.py` cases 6 and 7.** Mutated the replacement wording in
   `upgrade-config.py` (`"checkout is incomplete"` → `"something went wrong"`,
   `"complete checkout of this repository"` → `"a full clone of this project"`). Both cases
   went **FAIL** (`7/9` instead of `9/9`) — confirms both assert the replacement string
   **positively**, not merely `RETIRED_CMD not in out`. Restored; clean.

3. **Case 2's `ALLOW_LIST`.** Removed the `test-check-plan-routes.py` entry (and its comment)
   from `ALLOW_LIST` in a copy. `case2_absence_no_unswept_distribution_tokens` **FAILED**,
   matching exactly `['.claude/skills/harness/bin/test-check-plan-routes.py']` — its own
   synthetic-`registry.json` fixture (line 573) trips the sweep the instant the exemption is
   removed, exactly as plan.yaml's intent predicted. Restored; clean.

## Judgment 1 — Case 1's absence half scoped to tracked files (`git ls-files`)

**Read: tracked-only is correct.** Confirmed against both constraints named in the dispatch:

- **Clone-harm theory.** `factory_workspace.py:125` clones the remote (`git clone
  https://github.com/<repo>.git`), which never carries untracked or gitignored content.
  `git ls-files` scopes the absence check to exactly what a clone would carry — nothing wider
  is needed to close the harm the feature is retiring, and nothing wider is claimed.
- **Machine-independence (SC-02b's own standard).** `git ls-files` reads the git index of
  *this checkout*, not ambient filesystem state — unlike a `$HOME`-shaped walk or a raw
  filesystem crawl, it does not vary with what worktrees or scratch files happen to sit on
  this particular machine today. A filesystem walk excluding `.claude/worktrees/` would be
  exactly the defect class SC-02b rejects: it would pass or fail depending on what else is on
  disk, not on what the repository actually ships.
- **The assertion names its own scope.** `git_ls_files()`'s docstring says explicitly:
  "deliberate scope limit, not an oversight," and the check name is
  `case1_absence_no_deploy_sh_tracked_anywhere` — "tracked" is in the identifier itself, not
  left implicit.

The literal "anywhere under the repository root" reading is impossible (a real gitignored
`deploy.sh` sits in FEAT-13's worktree, confirmed present on disk at dispatch time). Tracked-only
is the correct scoping, not a deviation to flag.

## Judgment 2 — Case 4's presence assertion (slice + `resolves it first`) vs. the approved
intent (whole-file grep for `harness/teams`)

**Read: the deviation is a deliberate and necessary improvement, not a regression, and it is
now proven to discriminate.**

- Confirmed empirically: `harness/teams` appears in `docs/harness/DECISIONS.md` only at line
  2320, nowhere near DEC-113's section (lines 1964–1974). A literal implementation of the
  approved intent (`grep -q 'harness/teams' docs/harness/DECISIONS.md`) is exactly what
  T-14's own verify does — and it is vacuous with respect to DEC-113's content, matching an
  unrelated section. That means, with T-14's verify vacuous on this clause, case 4's
  slice+substring check is the **only** thing gating SC-08's presence half.
- Mutation proofs 1A and 1B above (Judgment 2, mutants A and B) show the slice+substring
  assertion **does** discriminate: it fails when the precedence rule is deleted from DEC-113's
  section, and it fails (correctly) even when the same literal substring is relocated
  elsewhere in the file. The implementation is stronger than the literal approved intent, not
  weaker, and the strength is measured rather than assumed.
- **Not a blocking finding.** SC-08's presence half is genuinely gated.

## SC-02, case-numbering note (non-blocking)

BRIEF/dispatch text refers to "case 20's `$HOME`-shaped trap [that] builds its own synthetic
`registry.json`." The synthetic-registry fixture actually lives in the function currently
named `case_21` (`case4_a_bare_harness_dir_is_not_a_project_root` /
`case_21_a_bare_harness_dir_is_not_a_project_root`) in `test-check-plan-routes.py`; `case_20`
in the current file is the earlier source-text scan (a different, four-times-defeated
mechanism, per its own docstring). The behaviour the dispatch describes is present and
verified — `case_21` ran and passed with the real `~/.harness/registry.json` deleted, proving
the fixture never depended on it — but the case number drifted between planning and the
current tree (likely a reorder during iteration). Cosmetic; not a coverage gap.

## Coverage gap — T-10's comment edits inside `test-check-plan-routes.py` (finding, low severity)

`test-no-distribution.py`'s case 2 `ALLOW_LIST` exempts `test-check-plan-routes.py` from
**all four** tokens (`harness-deploy`, `deploy\.sh`, `harness-registry`, `registry\.json`),
path-scoped rather than path-and-token scoped — a choice plan.yaml makes explicit ("Do not
restructure ALLOW_LIST into path-and-token pairs"). Currently that file contains none of the
`deploy.sh`/`harness-deploy` tokens (confirmed by grep) — only the legitimate synthetic
`registry.json` at line 573. But because the exemption is path-scoped, **no standing test in
`run-unit-tests.sh` would catch a regression that reintroduced `deploy.sh` prose into this
specific file's comments** (e.g. T-10's rewrite at lines 558/958-959 being reverted). The only
thing that ever checked this was T-10's own task-local `verify:` — a one-shot grep, not a
persisted test — which already passed once and is not re-run by any suite. This is the same
shape as Expertise gotcha G-04 (a task-local pass proving less than a standing per-kind test).
Severity: **low** — it is a comment-only regression risk (no behavioural surface), the
tradeoff is documented and deliberate in plan.yaml, and the file's *behavioural* coverage
(case 20/21, the actual root-resolution logic) is untouched by this gap.

## SC evidence, for pm's goal-check

| SC | Test | Result |
|---|---|---|
| SC-01 | `run-unit-tests.sh` full run, ALL PASS after deploy.sh/harness-deploy.md deletion | satisfied |
| SC-02 | `test-check-plan-routes.py` under `--kind integration`, all cases incl. case_21 (registry-independent) | satisfied |
| SC-02b | inspection only (per BRIEF) — not a test-runner claim; T-09's verify output is the cited evidence, not re-derived here | n/a to qa |
| SC-03 | `test-no-distribution.py` case 3 (`case3_presence_fleet_yaml_safe_loads`, `case3_presence_fleet_has_exactly_two_repos`, `case3_presence_kaya_default_branch_is_master`) | satisfied |
| SC-04 | inspection (BRIEF: no test kind reaches `kaya-ai`) | n/a to qa |
| SC-05 | inspection — sha256 manifest diff (T-04's verify) | n/a to qa |
| SC-06 | uat — operator's own blocking check | n/a to qa |
| SC-07 | `test-no-distribution.py` case 2 (`case2_absence_no_unswept_distribution_tokens`, `case2_presence_scan_reached_the_tree`), mutation-proven above | satisfied |
| SC-08 | `test-no-distribution.py` case 4, all six assertions, mutation-proven for the presence half (Judgment 2) | satisfied |
| SC-09 | inspection (BRIEF) | n/a to qa |
| SC-10 | `test-upgrade-config.py` cases 6/7 under `--kind integration`, mutation-proven | satisfied |

## Tree state

Confirmed clean before finishing: `git status --porcelain` on the main checkout shows only
the pre-existing, unrelated entries that were present before this run started (`feature.yaml`
modification and two untracked FEAT-14/FEAT-15 directories — none touched by this gate).
`git worktree list` confirms `.claude/worktrees/qa-feat12-mutation` was removed. No commit,
stage, or push was made. No source file was edited outside the disposable worktree.

## 2026-08-10 — s2-diff-coverage: mapping the diff to declared tasks

**Verdict on this narrow derivation: matrix_ok true, no send-back.** The earlier PASS was
correct — the gap the dispatch worried about (a changed path claimed by no task, whose
`change_type` was therefore never derived) does not exist in this diff.

**Restricting `f9488a2..d543809` to FEAT-12's own commits.** The raw range spans 52 commits and
touches ~150 files, but nearly all of it belongs to other work landed in the same window —
FEAT-10 (software factory), FEAT-11 (GraphQL field resolve), issues #202/#203/#204/#211/#216/#217,
and several grilling sessions — none of it FEAT-12's. FEAT-12's own commit set, identified by
message (`FEAT-12:`/`FEAT-12 signed`/`FEAT-12 build pauses`/the `[harness:t-NN]`-tagged commits
matching this plan's team task IDs T-07/T-10/T-12/T-13/T-14, plus the one log entry that records
FEAT-12 dispatch) is:

`f3452bf, 96d5d5c, 8782ee1, 275de45, 5042f40, e987c6d, 9e49ba7, ff75afb, 65d40cb, 8b53ebd, d543809`

Excluded deliberately: `6c89fff`, a merge of `origin/main` into the FEAT-12 branch that carries
unrelated `bash-write-guard.sh`/`test-bash-write-guard.py`/`test-harness-yaml.py` changes from
other work (visible in the full-range diff but authored elsewhere) — including it would have
misattributed those files to FEAT-12. Their absence from FEAT-12's own commit set is itself the
check that the wider range's noise was correctly excluded.

**Union of `git show --name-status` across those 11 commits: 45 unique changed paths.**

Every one maps to exactly one of three buckets:

1. **Declared by a task's `files:` list, in-repo** — 27 paths: `.claude/commands/harness-deploy.md`
   (T-08); `harness-init/SKILL.md`, `harness-team/SKILL.md`, `templates/README.md`,
   `templates/team-config.yaml`, `.harness/team-config.yaml` (T-11); `check-plan-routes.py`,
   `factory_config.py`, `test-check-plan-routes.py`, `test-upgrade-config.py`, `upgrade-config.py`,
   `wayfind.py` (T-10); `deploy.sh` (T-07); `run-unit-tests.sh`, `test-no-distribution.py` (T-13);
   `fleet.yaml` (T-06); `.harness/README.md`, `README.md`, `docs/harness/SPEC.md` (T-12);
   `docs/harness/BUILD.md` (T-12 and T-14 both); `docs/harness/DECISIONS.md`,
   `docs/harness/DECISIONS-INDEX.md` (T-14); `notes/kaya-agents-count-before.txt` (T-02);
   `notes/kaya-harness-manifest-before.txt` (T-01); `notes/kaya-harness-manifest-after.txt` (T-04).
2. **Bookkeeping, non-source** — 18 paths: `.harness/features/FEAT-12-end-copy-distribution/`
   `BRIEF.md`, `STATE.md`, `feature.yaml`, `plan.yaml`, every other `notes/*` (receipts, research,
   answers, handoff, measurements), both `observations/*.md`, and `.harness/logs/2026-08-10.md`.
   Feature scaffolding and run artifacts per the dispatch's own instruction — classified, not
   flagged.

**Undeclared paths (coverage_gaps): `[]`.** Nothing in the diff is logic-shaped and unclaimed by
any task — every `.py`/`.sh` change under `.claude/skills/harness/bin/` (`deploy.sh`,
`upgrade-config.py`, `test-upgrade-config.py`, `check-plan-routes.py`, `test-check-plan-routes.py`,
`wayfind.py`, `factory_config.py`, `run-unit-tests.sh`, `test-no-distribution.py`) is named in a
task's `files:` list, and each of those tasks' `change_type` (`logic` for T-07/T-10/T-13) was
already correctly derived and gated in the original run above.

**Inverse check — any task whose declared in-repo `files:` did not change: none.** T-01, T-02,
T-04, T-06, T-07, T-08, T-10, T-11, T-12, T-13, T-14 all have every in-repo declared path present
in the 45-path diff. T-03, T-05, T-09 declare only paths outside `CLAUDE_PROJECT_DIR`
(kaya-ai, `$HOME`) and correctly contribute nothing to this repo's diff, per the dispatch's own
note.

**Total changed-file count for the FEAT-12-restricted diff: 45** (27 task-declared, 18
bookkeeping, 0 undeclared).

This derivation does not change the matrix conclusion reached in the section above: the diff's
`logic`-typed files (T-07, T-10, T-13) are exactly the ones the original run required `unit` for
and ran; nothing newly surfaces a missing kind.
