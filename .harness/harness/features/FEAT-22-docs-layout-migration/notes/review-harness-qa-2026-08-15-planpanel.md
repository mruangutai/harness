# FEAT-22 · S-02 · plan-quality review — MF-4 class exhaustiveness (planpanel)

**BLUF: FAIL — a third, unfound member of the class exists.** `test-harness-yaml.py`'s
`COLLECT_FIXTURE["harness-documentor"]` (`:81-96`) is an exact-list-equality assertion against
`.harness/team-config.yaml`'s real, live grants, reached through `harness_yaml.manifest_domains()`
— the module the file's own docstring says reconstructs `check-domain.sh`'s grant-collection logic
(`:105-126`). T-02 adds `.harness/*/docs/**` to `harness-documentor`'s grants; **MEASURED LIVE**
(simulated team-config.yaml, real `manifest_domains()` call): the returned `mine` list gains that
entry, breaking the fixture's exact-match assertion. This test runs in the **integration suite**.
No task in the plan — not T-02, not T-04 (which touches this exact file for an unrelated path fix),
not T-05, not T-06 — updates `COLLECT_FIXTURE`. T-05's own verify would correctly catch the extra
integration `FAIL` and block the cluster commit (`test "$(grep -cE '^FAIL test-' "$i")" = 1`), so
this would not ship silently — but there is no task assigned to fix it, which is precisely the
"unfound class member" bar this hunt exists to clear. **MUST-FIX.**

The MF-4 class itself (verdicts driven by `HARNESS_CONTROL_PLANE` through `harness_boundary`) is
proven complete inside `test-check-domain.py`'s 19 legacy lines, all mapped into T-05's
enumeration, across a 27-file sweep with zero further candidates. This finding sits in a
closely-related but distinct family — a grant-list equality flip driven by `team-config.yaml`
through `harness_yaml.manifest_domains()`, not by `HARNESS_CONTROL_PLANE` through
`harness_boundary.classify`. It is reported because it is the same shape of defect (an unaccounted
verdict flip with no owning task) and the dispatch's own framing ("a `NEW MEMBER` ... is a
`MUST-FIX`") does not gate on which exact mechanism carries it.

T-05's, T-03's and T-10's `verify:` blocks are otherwise syntactically sound, reference paths that
exist at the pin, and every one fails cleanly (not with a load/syntax error) when run against the
unbuilt tree — the expected state pre-build. T-10's arithmetic reproduces exactly against the pin.
One low-severity wording ambiguity in T-01, not a defect in the plan's logic.

Pin confirmed: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`.

## HUNT 2 — MF-4 class census

**27 `test-*.py` files exist under `.claude/skills/harness/bin/`.** No `test-*.sh` files exist —
the `.sh` files there are enforcement scripts, not tests, so the shell-script sweep the dispatch
asked for returns nothing to add.

Partition:
- **T-04's 6** (`test-harness-yaml.py`, `test-team-catalog.py`, `test-validate-digest.py`,
  `test-gen-decisions-index.py`, `test-no-distribution.py`, `test-factory-config.py`) — path-only
  breaks per the dispatch's own scope fence (T-04's class, not MF-4's). Not re-litigated.
- **T-05's 5** (`test-check-domain.py`, `test-bash-write-guard.py`, `test-check-plan-routes.py`,
  `test-factory-integration.py`, `test-layout-migration.py`) — the MF-4 class itself.
- **`test-check-state.py`** — deliberately excluded by the plan (D-07/T-05 intent).
- **15 unscheduled** — swept and **rejected**, zero candidates in every one:
  `test-branch-create-gate.py`, `test-check-expertise.py`, `test-factory-claim.py`,
  `test-factory-cli.py`, `test-factory-decompose.py`, `test-factory-gh.py`, `test-factory-land.py`,
  `test-factory-workspace.py`, `test-gh-board.py`, `test-gh-sync.py`,
  `test-harness-yaml-corpus.py`, `test-merge-settings.py`, `test-render-brief.py`,
  `test-upgrade-config.py`, `test-validate-feature-json.py`. Grepped each for
  `docs/harness`, `harness_boundary`, `is_control_plane`, `classify`, `check-domain`,
  `bash-write-guard`, `check-plan-routes`, `HARNESS_CONTROL_PLANE`: zero hits in 14 of 15.
  `test-merge-settings.py` hits `check-domain.sh`/`bash-write-guard.sh` (lines 33, 58, 66, 68, 76,
  115, 117) but only as string literals in a `hook_present()` detector over `settings.json` JSON —
  it never calls `classify`/`is_control_plane_target`/the hooks themselves, so no assertion's
  verdict is a function of `HARNESS_CONTROL_PLANE`'s contents. Rejected.

**`test-check-state.py`'s exclusion, verified directly** (not trusted from the plan's own
reasoning): grepped for `--resolve`, `harness-documentor`, `classify(` — zero hits. Its one docs
site (`:1619`, `os.path.join(tmp, "docs", "harness")`) sits inside `case_x`, an INV-27 sandbox that
builds fixtures entirely from `layout_fixtures.STUB`'s **legacy form** and exercises
`layout_migration.py`'s MIXED/CLEAN detection — not `harness_boundary.classify`'s grant/target
logic. T-03's rewrite of `HARNESS_CONTROL_PLANE` cannot flip any assertion in this file. The plan's
exclusion is correct, confirmed by reading, not by trusting the plan's own comment (per
Expertise P-03).

**`test-check-domain.py`'s 19 legacy lines, individually mapped.** `git grep -cE` at the pin
returns exactly 19 (matches the eng re-fire's re-measurement in
`notes/research-FEAT-22-s01g-mf4-a4.md`). All 19 line numbers (35, 58, 519, 712, 717, 720, 726,
729, 730, 732, 787, 789, 793, 801, 820, 823, 824, 826, 924) fall inside a range T-05's intent names
explicitly. No orphan line found.

**`test-bash-write-guard.py` and `test-factory-integration.py` swept beyond the plan's named
anchors** (dispatch step 5): grepped both files whole for `docs`. Every hit lands exactly on the
line numbers T-05 already names (`:85,87,89,107,110` and `:28,329-333` respectively) — nothing
beyond the plan's own anchors exists in either file.

**Census result for the strict MF-4 class (`HARNESS_CONTROL_PLANE` via `harness_boundary`):** all
verdict-flip sites live inside T-05's five files, as enumerated. Sweep of the remaining 22 test
files (27 total minus T-05's 5) found zero additional strict-class members — fifteen were
candidates on file existence alone and all fifteen were rejected on read content, not assumed;
`test-check-state.py`'s exclusion was independently confirmed, not trusted from the plan's own
text.

**But the mechanism grep run over the 15 unscheduled files was NOT run over T-04's six** in the
first pass of this sweep — a gap in the census the advisor caught. Run subsequently
(`grep -nE 'harness_boundary|is_control_plane|classify\(|check-domain|bash-write-guard|check-plan-routes|HARNESS_CONTROL_PLANE'`
over all six): four of six are clean. `test-harness-yaml.py` and `test-no-distribution.py` and
`test-factory-config.py` hit the pattern on `check-domain.sh`/`check-plan-routes.py` MENTIONS —
read each in place:
- `test-no-distribution.py:76-77,101` — asserts `check-plan-routes.py` (the file) EXISTS on disk.
  Presence check, not a resolution call. Rejected.
- `test-factory-config.py:144` — a comment describing `check-domain.sh`'s general refusal
  behavior, not an assertion invoking it. Rejected.
- `test-harness-yaml.py:28,356-363` — the `COLLECT_FIXTURE` mechanism itself (see BLUF): a real
  finding, but it is the grant-list/`manifest_domains()` family, not
  `HARNESS_CONTROL_PLANE`/`harness_boundary.classify`. Counted separately above, not as a strict
  MF-4 member.

No member of the strict, `HARNESS_CONTROL_PLANE`-driven class exists beyond T-05's five files.
This is a proven-complete count for that specific class — but the class as **actually needed**
(any unaccounted verdict flip from this feature's edits) has the one member above.

**T-01's eleven-file enumeration reconciles with T-04+T-05's files: lists exactly**: T-04's 6 +
T-05's 5 = 11, matching T-01's "ELEVEN files" (`plan.yaml:239-278`). One wording nit, **low
severity**: T-01's closing line, "A red outside those eleven files plus test-gen-decisions-index.py
is collateral breakage" (`:272-273`), names `test-gen-decisions-index.py` a second time even
though it is already one of T-04's six and therefore already inside "those eleven." Read in context
this is explainable — RED STATE 3 gives that file a second, later-clearing failure mode (stale
committed artifact, until T-09) distinct from its first (absence, cleared at T-04) — but the literal
phrase reads as if a twelfth file exists. Not a MUST-FIX: no test or verify clause depends on the
literal count "eleven," and the intended meaning is recoverable from the surrounding paragraph.
Flagging for a one-clause rewrite (e.g. "...eleven files, one of which — test-gen-decisions-index.py
— reds a second time for a different reason...").

## HUNT 5 — does the MF-4 clause actually run?

`bash -n` on all three tasks' whole `verify:` blocks (T-03, T-05, T-10): **clean, no syntax error,
no unbound-variable issue** (none of the three uses `set -u`, and none references a variable before
assignment).

**T-05's block**: `$B` is set at the very top (`B=.claude/skills/harness/bin`, line 2 of the
block) before any use. All five files it references exist at the pin, as does
`run-unit-tests.sh`. Ran the whole block against the unbuilt pin: it fails with `integration FAILs
are not the one expected` — a controlled, named assertion failure, not a load/import/collection
error. This is the expected state (nothing is built yet), **and it is also a real measurement**:
running the block executes both `run-unit-tests.sh --kind unit` and `--kind integration` for real
against the pin, and the failure text (`grep -cE '^FAIL test-' "$i"` != 1, i.e. it measured 0) means
**both suites carry zero `FAIL` lines at `0f12f14` today** — independently corroborating T-01's
stated pre-move baseline (0 FAIL in each, 15 PASS unit / 12 PASS integration).

**The `grep -qF` fixed-string check** (`:605-606`) targets
`hook(".harness/harness/docs/SPEC.md", "harness-documentor")` character for character. The current
call at `test-check-domain.py:924` reads `hook("docs/harness/SPEC.md", "harness-documentor")` —
same call shape (double-quoted string literal, comma-space, two positional args, single line, no
third argument, no wrap). A pure path-substitution edit, which is exactly what T-05's intent
prescribes, reproduces the target string exactly; this was independently confirmed live in
`notes/research-FEAT-22-s01g-mf4-a4.md` §3 (test B: sed-simulated substitution → exact match, exit
0; test D: the sibling `:789` `--resolve` call, which carries the identical migrated path string
after the move, does **not** match, because the anchor is the `hook(` call shape, not the path —
confirming the two sites stay distinguishable). Re-verified reasoning here, not re-run (the prior
note's live run stands as the discriminating evidence; re-deriving the call shape from the current
file confirms nothing has drifted since).

**T-03 and T-10** were also run at the pin: both fail with named, non-error messages
(`factory_config does not match the migrated row`; `no depth sweep section` after a benign
"file not found" on the not-yet-created boundary note, which `T-10`'s own verify tolerates via
`grep -q` on a missing file — that is a controlled `grep` miss, not a crash). Both runs exited at
their FIRST failing check, so T-03's `awk` anchor (guarding the `guide.md` window) and T-10's
`exp`/`got` table compare never actually executed inside those runs — each was run **standalone**
to close the gap:
- **T-03's `awk` block**, run alone against `harness_boundary.py` at the pin: parses cleanly and
  fails with `site 315: the paragraph around guide.md does not name .harness/*/docs/** as the
  grantor` — confirming (a) the `awk` has no syntax error, (b) `guide.md` is already a unique
  anchor at the pin (the count-check did not fire), and (c) the literal isn't present yet, which is
  correct pre-build.
- **T-10's `exp` heredoc + `sed 's/^ *//'`**, run standalone: reproduces the same five
  `path:count` lines, in the same order, as `git grep -cE ... | sort`'s live output — confirmed
  identical shape and sort order.

## HUNT 5b — T-10's arithmetic re-derived at the pin

Ran `git grep -cE 'docs/harness|"docs", ?"harness"' -- .claude CLAUDE.md .harness/expertise | sort`
directly. **Every figure T-10 cites reproduces exactly:**

| Claim | Measured |
|---|---|
| 25 files on the three live surfaces | 25 (counted) |
| `test-check-domain.py` 19 | 19 |
| `test-bash-write-guard.py` 5 | 5 |
| `test-check-plan-routes.py` 6 | 6 |
| `test-factory-integration.py` 4 | 4 |
| `layout_fixtures.py` 3 | 3 |
| `layout_migration.py` 6 | 6 |
| `25 - 15 - 3 - 2 = 5` final table | arithmetic checks: T-03(3 files)+T-04(6)+T-06(6)=15; T-05 removes a further 3 to zero (`test-bash-write-guard.py`, `test-check-plan-routes.py`, `test-factory-integration.py`); T-07 removes 2 (Expertise files); 25-15-3-2=5, matching the final table of `layout_fixtures.py`(3), `layout_migration.py`(6), `test-check-domain.py`(1), `test-check-state.py`(1), `test-layout-migration.py`(1) |

No figure fails to reproduce. T-10's verify is grounded in real numbers, not asserted ones.

## Scope fences honored

Did not re-litigate MF-4's closure (only mechanically confirmed the fix that closed it still holds
at the pin and the grep that verifies it can pass). Did not touch Q6/Q7/Q8, the heredoc mechanism,
the two-segment fixture row, FEAT-21's filed set, r7's signature, or Q2. Did not opine on the
35-file survivor partition, the detector's migrated regexes, or T-07/T-08's verbatim-specification
(code-reviewer's lane).

```yaml
VERDICT: FAIL
DIGEST:
  headline: A third verdict-flip site exists outside T-04/T-05's enumeration — test-harness-yaml.py's COLLECT_FIXTURE (integration suite) breaks the moment T-02 edits team-config.yaml, and no task in the plan updates it.
  suite: pass
  matrix_ok: n/a
  failures: 0
  coverage_gaps: []
  open_questions: []
  must_fix:
    - { id: F-02, severity: high, area: "test-harness-yaml.py:81-96 COLLECT_FIXTURE['harness-documentor']", note: "Exact-list-equality assertion against the real .harness/team-config.yaml, reached through harness_yaml.manifest_domains() (the file's own docstring: reconstructs check-domain.sh:105-126's grant-collection logic). MEASURED LIVE by simulating T-02's team-config.yaml edit and calling manifest_domains(): the returned 'mine' list for harness-documentor gains '.harness/*/docs/**', breaking the fixture's exact match. Runs in the integration suite (run-unit-tests.sh:18). No task updates COLLECT_FIXTURE -- not T-02, not T-04 (which edits this same file for an unrelated path fix at :686 only), not T-05, not T-06. T-05's own verify would correctly block on the resulting second integration FAIL, but no task is assigned to fix the cause." }
  findings:
    - { id: F-01, severity: low, area: T-01 RED STATES prose, note: "'eleven files plus test-gen-decisions-index.py' (plan.yaml:272-273) reads as naming a 12th file; test-gen-decisions-index.py is already one of T-04's six inside the eleven. Recoverable from context (it reds a second time for a different, later-clearing reason), not a build-blocking ambiguity." }
  census:
    test_files_total: 27
    scheduled_T04: 6
    scheduled_T05: 5
    excluded_check_state: 1
    unscheduled_swept_and_rejected: 15
    strict_mf4_class_HARNESS_CONTROL_PLANE_members: 0   # beyond T-05's 5 files, which fully account for all 19 legacy lines in test-check-domain.py; sweep of the remaining 22 files, including T-04's six by mechanism grep, found no further HARNESS_CONTROL_PLANE-driven flip
    adjacent_verdict_flip_members_found: 1   # F-02, a team-config.yaml/manifest_domains()-driven flip, same defect shape, different mechanism
  hunt5:
    bash_n_clean: [T-03, T-05, T-10]
    verify_fails_controlled_at_pin: true
    grep_qF_target_reproducible: true
    awk_T03_standalone_parses: true
    sed_T10_standalone_shape_matches: true
  hunt5b:
    all_figures_reproduced: true
  baseline_corroboration: "run-unit-tests.sh executed for real via T-05's verify at the pin: 0 FAIL lines in both unit and integration, corroborating T-01's stated pre-move baseline."
  files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-qa-2026-08-15-planpanel.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-qa-2026-08-15-planpanel.md
```
