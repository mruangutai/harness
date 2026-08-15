# Receipt — harness-backend-dev — T-02

## BLUF

`check-plan-routes.py` implemented per PLAN.md:167-233, TDD RED→GREEN, all three
required receipts (a/b/c) and the full verify chain pass, verbatim output below.
`run-unit-tests.sh:6` carries exactly one added element (`test-check-plan-routes.py`)
appended to whatever FEAT-08 left there — re-read fresh immediately before writing,
confirmed unchanged by a second read afterward.

## TDD

RED confirmed first: ran `test-check-plan-routes.py` before `check-plan-routes.py`
existed — 3 explicit case failures plus a `FileNotFoundError` traceback from the
static-source cases, all for the right reason (script absent). Then wrote the
production script and iterated to GREEN, fixing bugs surfaced by the tests
themselves (not pre-written around them):
1. My own docstring contained the literal word "fnmatch" while explaining why the
   script must not use it — that failed case 9 until reworded without the banned
   token.
2. `docs/harness/**` is granted to `harness-documentor`, so my first "ungranted path"
   fixture wasn't actually ungranted — replaced with a path outside every domain glob.
3. `check-plan-routes.py` used `.startswith("SHARED ")` to parse an OUTPUT line from
   check-domain.sh (not to match a filesystem path) — legitimate use, but the task's
   receipt (b) demands zero `startswith` hits in this file regardless of purpose, so
   replaced with `re.match(r"^SHARED ", line)`.
4. Case 17's original assertions (no VIOLATION line naming T-01, exit 0) pass
   vacuously if the fixture task block ever stops parsing (zero tasks parsed also
   yields zero VIOLATIONs and exit 0) — the exact fail-open shape this codebase's
   review hunts for. Added a positive assertion that an `OK`-prefixed line naming
   T-01 is present, closing that gap.

## Receipt (a) — 17 named cases, cross-checked two ways

First derivation used `grep -o 'check("case_...'`, which only matches single-line
`check(` calls and silently missed `case_07` (written as a multi-line call) while
double-counting `case_17`'s two `check()` sites — a false receipt of the exact
"compound token" shape this dispatch warned about. Re-derived correctly:

```
$ grep -o 'case_[0-9][0-9]' .claude/skills/harness/bin/test-check-plan-routes.py | sort -u
case_01
case_02
case_03
case_04
case_05
case_06
case_07
case_08
case_09
case_10
case_11
case_12
case_13
case_14
case_15
case_16
case_17
$ grep -o 'case_[0-9][0-9]' .claude/skills/harness/bin/test-check-plan-routes.py | sort -u | wc -l
      17
```
Cross-checked against a live run's `PASS case_NN` lines (19 lines: case 07 has one
assertion, case 17 has three — no-VIOLATION, has-OK, exit-0 — every other case has
one or two; all 17 numbered cases appear at least once):
```
$ python3 .claude/skills/harness/bin/test-check-plan-routes.py | grep -c '^PASS case_'
19
$ python3 .claude/skills/harness/bin/test-check-plan-routes.py | grep '^PASS case_'
PASS case_01_ungranted_undeclared_exits_nonzero
PASS case_02_output_has_task_id
PASS case_03_output_has_offending_path
PASS case_04_all_granted_exits_0
PASS case_05_ungranted_declared_main_session_exits_0
PASS case_06_wildcard_produces_unresolved_glob
PASS case_07_wildcard_exit_status_matches_task_removed
PASS case_08_source_mentions_check_domain_sh
PASS case_09_source_has_no_fnmatch
PASS case_16_source_has_no_glob_to_re
PASS case_10_template_has_lanes_section
PASS case_11_template_has_team_token
PASS case_12_template_has_main_session_direct_token
PASS case_13_runner_lists_this_test
PASS case_14_granted_but_main_session_produces_deviation
PASS case_15_deviation_plan_still_exits_0
PASS case_17_midpattern_wildcard_grant_no_violation
PASS case_17_midpattern_wildcard_grant_reports_ok
PASS case_17_midpattern_wildcard_grant_exits_0
```
16 and 17 are separate functions/case-number-prefixes (`case_16_source_has_no_glob_to_re`
vs `case_17_midpattern_wildcard_grant_*`), satisfying "16 and 17 as SEPARATE cases."

## Receipt (b) — three separate greps, zero hits each

```
$ grep -n "fnmatch" .claude/skills/harness/bin/check-plan-routes.py
(no output, exit 1)

$ grep -n "glob_to_re" .claude/skills/harness/bin/check-plan-routes.py
(no output, exit 1)

$ grep -n "startswith" .claude/skills/harness/bin/check-plan-routes.py
(no output, exit 1)
```
`startswith` was used once (checking a `SHARED ` output-line prefix from
check-domain.sh's stdout, not path matching) and was replaced with
`re.match(r"^SHARED ", line)` to bring this grep to zero as required (see TDD note 3).

## Receipt (c) — no test-cost-report.py, line 6 verbatim, one-element diff (unabridged)

```
$ grep -n "test-cost-report.py" .claude/skills/harness/bin/run-unit-tests.sh
(no output, exit 1)

$ sed -n '6p' .claude/skills/harness/bin/run-unit-tests.sh
SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-render-brief.py" "test-harness-yaml.py" "test-harness-yaml-corpus.py" "test-upgrade-config.py" "test-team-catalog.py" "test-check-plan-routes.py")

$ git diff 47ed11f -- .claude/skills/harness/bin/run-unit-tests.sh
diff --git a/.claude/skills/harness/bin/run-unit-tests.sh b/.claude/skills/harness/bin/run-unit-tests.sh
index 4933a68..f24a106 100755
--- a/.claude/skills/harness/bin/run-unit-tests.sh
+++ b/.claude/skills/harness/bin/run-unit-tests.sh
@@ -3,7 +3,7 @@ set -uo pipefail
 cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

 BIN_DIR=".claude/skills/harness/bin"
-SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-render-brief.py" "test-harness-yaml.py" "test-harness-yaml-corpus.py" "test-upgrade-config.py" "test-team-catalog.py")
+SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-render-brief.py" "test-harness-yaml.py" "test-harness-yaml-corpus.py" "test-upgrade-config.py" "test-team-catalog.py" "test-check-plan-routes.py")

 # Drift detector: any test-*.py under BIN_DIR not in the explicit list is misconfigured.
 for f in "$BIN_DIR"/test-*.py; do
```
Confirms: FEAT-08's removal of `test-cost-report.py` (already gone at the moment I
read line 6, before any edit of mine — the `-` line above is the 12-entry array with
NO `test-cost-report.py`) is preserved, and exactly one element was appended on top
of it (the `+` line adds only `"test-check-plan-routes.py"`).

## Full verify chain — invocation and observed output

```
$ python3 .claude/skills/harness/bin/test-check-plan-routes.py && \
  .claude/skills/harness/bin/run-unit-tests.sh && \
  python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-09-plan-time-route-check/PLAN.md
```

Own test file: `ALL PASS` (19 `PASS case_*` lines across 17 numbered cases, exit 0
— see receipt (a) for the full listing).

Runner: exit 0, no `MISCONFIGURED` drift line, **13** `PASS test-*.py` lines (not
the 14 PLAN.md:312's receipts table predicted — that table was written before
FEAT-08 removed `test-cost-report.py`; 13 = the 12 entries surviving FEAT-08's
removal + this task's new one):
```
PASS test-validate-digest.py
PASS test-gh-sync.py
PASS test-check-state.py
PASS test-check-expertise.py
PASS test-gen-decisions-index.py
PASS test-bash-write-guard.py
PASS test-check-domain.py
PASS test-render-brief.py
PASS test-harness-yaml.py
PASS test-harness-yaml-corpus.py
PASS test-upgrade-config.py
PASS test-team-catalog.py
PASS test-check-plan-routes.py
```
(The runner also emits informational PyYAML-bootstrap-marker stderr/systemMessage
noise on this machine, unrelated to this task's edit — pre-existing behaviour of an
unrelated script under test.)

Final plan check, full stdout:
```
DEVIATION T-01 .claude/skills/harness/bin/check-domain.sh, .claude/skills/harness/bin/test-check-domain.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
OK T-02
OK T-03: declared main-session-direct (.claude/skills/harness/templates/PLAN.md ungranted)
OK T-04: declared main-session-direct (.claude/skills/harness-spec-driven/SKILL.md ungranted)
0 violation(s) across 1 plan(s)
```
exit 0. Matches PLAN.md:227-228 exactly: zero violations, exactly one `DEVIATION`
line naming T-01, exit 0.

## Design notes (decided, not asked — cheap/reversible)

- DEVIATION granularity is per-task: when a task's literal `files:` entries all
  resolve to a granting agent and it declares `main-session-direct`, one line is
  emitted joining all its paths and the union of granting agents — not one line
  per path (matches the disambiguation in the dispatch and the T-01 verify).
- `--resolve` output lines are parsed with a plain equality/regex-anchor check, never
  a second path matcher: `NOBODY`, `SHARED <pattern>`, or an agent name per line.
- Glob entries (`*`/`?`) are reported as `UNRESOLVED-GLOB` and excluded entirely
  from the OK/VIOLATION/DEVIATION verdict computation for that task, per D-04.

## Open question (non-blocking)

With no argv and a cwd where `.harness/features/*/PLAN.md` matches nothing (e.g.
invoked from the wrong directory), `check-plan-routes.py` prints
`0 violation(s) across 0 plan(s)` and exits 0 — a clean answer from a run that
checked nothing. This is not a spec violation (D-01/verify never specify a non-empty
default-glob requirement) and I did not change behaviour to address it, but it is a
fail-open shape worth having on record for whoever wires this into pm's PLAN-write
step or a future `check-state.sh` invariant (D-01's open question).

## Files touched

- `.claude/skills/harness/bin/check-plan-routes.py` (new)
- `.claude/skills/harness/bin/test-check-plan-routes.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one array element appended at line 6)
