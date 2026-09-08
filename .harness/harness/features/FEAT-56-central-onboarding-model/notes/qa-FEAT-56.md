# QA gate — FEAT-56-central-onboarding-model (HEAD bb28c4d1, review_sha unpinned)

## BLUF: FAIL. Blocking unit kind (SC-06) reds on a real regression T-01 introduced — `deploy.sh`
mention in the rewritten SKILL.md trips the permanent `test-no-distribution.py` token sweep.
Everything else graded (SC-02, SC-05, SC-07, SC-08, SC-10; T-02/T-03 diff-vs-claim; T-04
mutation-proof reproduction) is clean.

## Must-fix
- **[T-01] `.claude/skills/harness-init/SKILL.md:50`** — the new per-clone-step paragraph says
  "nothing distributes `bin/` since `deploy.sh` was deleted (DEC-113)". The literal substring
  `deploy.sh` trips `TOKEN_RE` in `tests/unit/test-no-distribution.py` case2
  (`ALLOW_LIST` is fixed at exactly two paths, neither is this file, by design —
  `test-no-distribution.py:104`). Confirmed absent from SKILL.md at base 4b5dbb23 (`git show
  4b5dbb23:.claude/skills/harness-init/SKILL.md | grep deploy.sh` → no match), so this is a
  regression introduced by this feature, not pre-existing. Fails a permanent, already-standing
  unit test — not a new/weakened one. Fix: reword to avoid the literal token (e.g. "deploy dot
  s h" is not an option; state the DEC-113 removal without the four-token spelling), or drop the
  clause — the ALLOW_LIST's own comment says "EXACTLY TWO ENTRIES... a new unswept site fails
  rather than being silently absorbed", so widening the allow-list is the wrong fix here.
  Severity: high — this is SC-06's own gate, the feature's blocking one.

## Change-type audit (diff wins where it disagrees with the plan's label)
- **T-04** `logic` (declared) — diff-confirmed: `factory_config.py` +79 additive lines
  (`product_config_report`, `_check_product_configs`, `--check-product-configs`/`--repo` flags),
  plus new `tests/unit/test-fleet-product-config.py`. Agrees.
- **T-02** `bugfix` (declared) — diff-confirmed message/comment-only: read every hunk across all
  six files (`check-domain.sh:381-386`, `check-instruction-paths.py:12-16`, `check-state.sh:108,
  286,404-407,2433-2434`, `upgrade-config.py:1-4,188-189,231-234`, `gh-sync.py:254-256`,
  `layout_migration.py:118-124`) — every changed line is an f-string/print/comment; zero exit
  codes, globs, or control-flow tokens touched. Claim holds.
- **T-03** `bugfix` (declared) — diff-confirmed comment/citation-only: `test-check-state.py:3886`,
  `test-layout-migration.py:248-249`, `test-hooks-install.py:1-4`, `test-post-merge-sweep.py:783`,
  `post-merge-sweep.sh:66-68` — every hunk is a comment. No assertion, fixture, or behavior line
  changed. `test-merge-settings.py` still contains `harness-init` (item 5's unchanged claim,
  verified); `test-merge-gitignore.py`/`test-upgrade-config.py` have zero `git diff --stat`
  entries (untouched, verified); `prior-check-domain.sh.fixture` untouched. Claim holds.
- **T-01/T-05/T-06/T-07/T-08** `docs` (declared) — diff scope matches (prose/template/doc surface
  only) EXCEPT for the T-01 regression above: a `docs` task tripped a live behavioral gate
  (the unit suite), exactly the class this audit exists to catch, even though the SKILL.md hunk
  itself is prose-only and touches no executable path.

**Bugfix predicates (`.harness/harness.json` test_matrix.bugfix.when), evaluated against the diff:**
- `touches_runtime_code`: **true** for T-02 (all six files are `.claude/skills/harness/bin/*.py|*.sh`
  executed by gates) → obligates `unit`. Discharged by the standing suite (SC-06's bucket already
  includes these files' behavior indirectly; T-02's own intent explicitly forbids a new permanent
  string-pinning unit test — panel finding PF-557e8589 already resolved this choice). **false**
  for T-03 (comment-only; `post-merge-sweep.sh`'s one touched line has zero behavioral delta).
- `fix_confined_to_tests_and_contract_docs`: **false** for T-02 (touches production `bin/`
  scripts, not confined to tests). **true** for T-03 (all five files are `tests/**` or a
  comment-only `.sh` edit) → obligates `integration`, already the standing kind (satisfied, SC-07).
- `match_bug_class`: unresolvable placeholder repo-wide (no bug-class taxonomy entry fires for
  any diff yet — repository Expertise G-08), does not fire for either task.
- `matrix_ok: false` — required kind `unit` is present and its own dedicated new tests
  (`test-fleet-product-config.py`) are green, but the STANDING unit bucket that kind gates on
  carries a real, reproducible failure from this diff (see must-fix). `integration` resolves
  **satisfied** (exit 0, 0 `^FAIL `, no anchor-skip lines).

## Runner results — exit status and `^FAIL ` count reported SEPARATELY, never the tail line
- `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` (SC-06, run twice for stability):
  **exit=1**, **`^FAIL ` count=6** (raw grep) but **2 are the real defect** — see below.
  Four of the six lines (`BUG-1290 5a/5b/5c` + a second `5b`) are `test-factory-claim-mutation.py`'s
  own deliberate mutation-proof output printed under `MUTANT ACTIVE`/`MUTANT KEY-COLLAPSE ACTIVE`
  headers — that file itself reports `PASS test-factory-claim-mutation.py` (exit 0); a bare
  `^FAIL ` grep overcounts these (repo Expertise G-08). The two genuine lines are both from
  `test-no-distribution.py`: `FAIL case2_absence_no_unswept_distribution_tokens unswept token(s)
  found in: ['.claude/skills/harness-init/SKILL.md']` and the file-level `FAIL
  test-no-distribution.py`. Confirmed twice, same result, same single root cause both times.
- `.claude/skills/harness/bin/run-unit-tests.sh` (`.claude/skills` spelling, symlink target of
  `.agents/skills` — confirmed `os.path.realpath('.agents/skills')` resolves to
  `<worktree>/.claude/skills`): same command underneath; not re-run separately since the spelling
  is a symlink alias, not a different script — the `.agents/skills` run above already exercises it.
- `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` (SC-07): **exit=0**,
  **`^FAIL ` count=0**. Grepped the raw output for skip lines mentioning "anchor"/"skill": **zero
  matches** — REQ-07's no-skip clause holds.
- T-04's own verify, `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py &&
  python3 tests/unit/test-factory-config.py` (cross-checked byte-identical against
  `plan.yaml:190-191`): **exit=0** both scripts, 15/15 then 114/114, 0 `^FAIL ` lines.

## T-04 test-first audit — REPRODUCED, not adopted
- **(i) pre-change RED**: unreproducible without moving HEAD (prohibited). Assessed from the
  receipt only — `notes/receipt-harness-backend-dev-t04-eng.md` reports a hard `AttributeError`
  abort, consistent with a suite asserting something real. **Unverified by me, flagged as such.**
- **(ii) post-change mutant, case (e) alone reddens**: **REPRODUCED MYSELF**, disagreeing with
  nothing in the receipt. Built a disposable worktree (`git worktree add`, per repo Expertise
  G-06 — the in-place bash-write-guard denies scratch copies outside a bound checkout), mutated
  its `factory_config.py` by deleting exactly the `sys.exit(factory_cli.EXIT_REFUSED)` line inside
  `_check_product_configs`, confirmed removal by grep, then ran
  `tests/unit/test-fleet-product-config.py` in that worktree. Observed: **1 of 15 FAILING**, the
  failing case is exactly `(e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing
  stub`; all nine `(a)-(d)` shape/order/count checks and the four other `(e)` shape/stderr checks
  stayed `ok`. **This agrees with the receipt's claim exactly.** Restored the mutant worktree
  byte-identically (`git checkout --`, confirmed `git status --porcelain` clean) and removed the
  worktree via plain `git worktree remove` (clean tree, no `--force` needed).
- **SC-05 grade is tied to this mutation observation**, not the receipt: **met**. Both directions
  (all-ok exit 0/all-ok count; one-unreachable exit 2/named detail) assert in the one standing
  suite run, and the failing direction (case e under the deleted-exit mutant) is shown to redden
  specifically at the exit-code check, never elsewhere — the gate is not vacuous.

## Six mechanically-gradable SCs
| SC | Verdict | Command | Result |
|---|---|---|---|
| SC-02 | **met** | `grep -qF 'git config --get core.hooksPath \|\| echo "(unset)"'` and `grep -qF 'git config core.hooksPath .claude/skills/harness/hooks'` against SKILL.md, then `python3 tests/integration/test-hooks-install.py` | both greps match; suite exit 0 |
| SC-05 | **met** | see mutation-proof section above | case (e) alone reddens under the mutant; both directions assert in one run |
| SC-06 | **not_met** | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 1, real regression (see must-fix) |
| SC-07 | **met** | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0, 0 FAIL, 0 anchor-skip lines |
| SC-08 | **met** | `python3 .claude/skills/harness/bin/check-omp-port.py` then `check-instruction-paths.py` | `OMP port surface: ok` exit 0; `scanned 62 file(s), 0 violation(s)` exit 0 |
| SC-10 | **met** | `python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"` at HEAD, and the same content pulled via `git show 4b5dbb23:...` fed to the identical one-liner | HEAD exits 0; base content raises `yaml.parser.ParserError: while parsing a flow sequence... expected ',' or ']'` at line 28 — confirms the red direction without checking out |

Not graded (per assignment): SC-01, SC-03, SC-04 (inspection, review panel's), SC-09 (uat).

## Discovery-volume regression check (three edited gate scripts + two related checkers)
Ran each base (`git show 4b5dbb23:<path>`, written into a disposable worktree, never checked out
in-place) against **this same worktree's state** via `HARNESS_PROJECT_DIR=<FEAT-56 worktree>`
(honored by `harness_boundary.resolve_root` because this worktree carries `.harness/team-config.yaml`),
compared to the HEAD version run directly here:
- `check-state.sh`: HEAD 1358 lines total output / 1358 `note|bad|VIOLATION|INV-` lines, exit 1
  (pre-existing worktree-hygiene violations unrelated to this diff). Base run against the
  identical worktree state: same 1358 note/bad/violation lines, exit 1. **No volume change.**
- `check-instruction-paths.py`: HEAD `scanned 62 file(s), 0 violation(s)` exit 0. Base (same
  worktree tree, base script logic): identical `scanned 62 file(s), 0 violation(s)` exit 0.
  **No volume change.**
- `check-decision-anchors.py`: HEAD `examined 33 anchor(s), 0 failed` exit 0. Base: identical
  `examined 33 anchor(s), 0 failed` exit 0. **No volume change.**
- `post-merge-sweep.sh`: not independently run (no standing harness invoking it outside
  `test-post-merge-sweep.py`, already green per SC-06/07 audit above); its only diff hunk is the
  comment re-anchor confirmed in the T-03 audit.

Both disposable worktrees (`qa-t04-mutant-proof`, `qa-base-scripts-tmp`) were removed after use,
restored to byte-identical clean state first (`git checkout --` + `git status --porcelain` empty),
then `git worktree remove` without `--force` (a clean tree needs none).

## Final tree state
`git status --porcelain` in the FEAT-56 worktree: **empty** (clean), verified after every mutation
step above and again at the end of this run.

## Open questions
- None blocking. The must-fix above is the only gap; it is a one-line reword in a `docs` task's
  file, routable back to T-01 without re-diagnosis.
