# Receipt — harness-backend-dev — T-05 (finish the ninth file: test-check-plan-routes.py)

## Scope

Single file: `.claude/skills/harness/bin/test-check-plan-routes.py`. The other eight T-05 files
landed at `df132c6` and were not touched. `check-plan-routes.py` was mutated temporarily for §C
mutation testing, then fully restored (hash-verified, empty `git diff`).

## §A — repoint both write sites (filename only)

`:839` and `:904` (`open(os.path.join(fd, "feature.yaml"), "w")` -> `"feature.json"`). The
`:834-836` status loop header (Backlog/Plan/Ready/Building/Review/Done, `("done", True)`) is
byte-identical — untouched, per T-05 item 7.

Baseline RED, captured before any edit:
```
PASS case_24_Backlog_is_checked
PASS case_24_Plan_is_checked
PASS case_24_Ready_is_checked
PASS case_24_Building_is_checked
PASS case_24_Review_is_checked
FAIL case_24_Done_is_skipped exit 1, checked=True: 'scanning .../.harness/features/*/{plan.yaml,PLAN.md}\nVIOLATION T-01: .claude/skills/harness-spec-driven'
PASS case_24_done_is_checked
...
1 FAILURE(S): ['case_24_Done_is_skipped']
```
Exactly the one failure named in the dispatch — nothing else red.

## §B — re-derive the four fixture bodies (`:883-901`)

`harness_yaml.load_file` (`.claude/skills/harness/bin/harness_yaml.py:237-250`) is a plain
`safe_load` with no extension dispatch, so the four bodies were written as strict JSON — which
`safe_load` and `json.load` both parse identically, closing the "YAML worked-example in a .json
fixture" gap named in the dispatch:

| case | old body | new body | guard held down |
|---|---|---|---|
| `a_sequence` | `- a\n- b\n` | `["a", "b"]\n` | `isinstance(doc, dict)` (`:426`) |
| `a_bare_scalar` | `shipped\n` | `"Done"\n` | `isinstance(doc, dict)` (`:426`) |
| `status_is_a_list` | `status:\n  - shipped\n` | `{"status": ["Done"]}\n` | `str()` wrap (`:433`) |
| `a_mapping_with_no_status` | `feature_id: FEAT-A\n` | `{"feature_id": "FEAT-A"}\n` | `bool(token) and` (`:434`) |

The `"1 violation(s) across 1 plan(s)"` assertion at (now) `:909` still holds — confirmed in the
green run below (`case_24_feature_yaml_*` all PASS). The stale line citation in the adjacent
comment (`check-plan-routes.py:422` for the `str()` wrap) was corrected to `:433`, its current
location.

## §C — three mutants against the live source (not `CHECK_PLAN_ROUTES_BIN`)

`_is_shipped` does `import harness_yaml` **inside** its own `try:`, so a copy of the script
sitting alone in a tempdir (the `CHECK_PLAN_ROUTES_BIN` override) fails that import and every
fixture reads as not-shipped — every case would survive every mutant with no error, which is the
vacuity trap the dispatch warns about. Mutated `check-plan-routes.py:395-434` in place instead.
sha256 before any mutation: `b5c1ba3867e23a759a00705dc16bc4817d43676d779d2a19d950af01e772bbe8`.
Same hash after every restoration below (re-verified after all three).

**Mutant A** — deleted `if not isinstance(doc, dict): return False` (`:426-427`). Verbatim:
```
FAIL case_24_feature_yaml_a_sequence_is_checked_not_crashed exit 1, stderr='Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-', stdout=''
FAIL case_24_feature_yaml_a_bare_scalar_is_checked_not_crashed exit 1, stderr='Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-', stdout=''
PASS case_24_feature_yaml_status_is_a_list_is_checked_not_crashed
...
2 FAILURE(S): ['case_24_feature_yaml_a_sequence_is_checked_not_crashed', 'case_24_feature_yaml_a_bare_scalar_is_checked_not_crashed']
```
(the `stderr=` value is truncated to 120 chars by the test's own `check()` call — this is the
real, full string the suite prints, not a shortened paraphrase of it.)
Predicted result matched exactly. `a_mapping_with_no_status` surviving mutant A is correct (it
is a dict, so `.get` works with or without the isinstance guard) — not a vacuity signal.
Restoration: `git diff -- .claude/skills/harness/bin/check-plan-routes.py` empty, sha256 matches
`b5c1ba3867e23a759a00705dc16bc4817d43676d779d2a19d950af01e772bbe8`.

**Mutant B** — dropped `bool(token) and` from the return (`:434`). Verbatim:
```
FAIL case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed exit 1, stderr='Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-', stdout=''
PASS case_24_eleven_key_feature_json_Done_is_skipped_end_to_end
...
1 FAILURE(S): ['case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed']
```
Only `a_mapping_with_no_status` failed, as predicted. Restoration: `git diff` empty, sha256
matches.

**Mutant C** — dropped the `str()` wrap around `doc.get("status", "")` (`:433`). Verbatim:
```
FAIL case_24_feature_yaml_status_is_a_list_is_checked_not_crashed exit 1, stderr='Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-', stdout=''
PASS case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed
PASS case_24_eleven_key_feature_json_Done_is_skipped_end_to_end
...
1 FAILURE(S): ['case_24_feature_yaml_status_is_a_list_is_checked_not_crashed']
```
Only `status_is_a_list` failed, as predicted. Restoration: `git diff` empty, sha256 matches.

**No case survived all three mutants** — each of the four is caught by at least one mutant, and
no case is redundant (the three mutants catch disjoint sets: {a_sequence, a_bare_scalar},
{a_mapping_with_no_status}, {status_is_a_list}). No vacuity signal.

## §D — the corrected instruction, relayed

The operator's original dispatch instructed deleting the `isinstance(doc, dict)` guard and
expecting `a_mapping_with_no_status` to FAIL. That pairing does not hold on disk:
`a_mapping_with_no_status` parses to a dict (`{"feature_id": "FEAT-A"}`), so `.get` succeeds with
or without the isinstance guard — confirmed above, it survives Mutant A. The comment at
`:886-900` (unchanged) is describing the `bool(token)` guard, not the isinstance one. §C's matrix
(the corrected form, run above) is what was executed; not treated as BLOCKED.

## §E — `harness_yaml.load_file` kept

No switch to `json.load`. Confirmed by reading `harness_yaml.py:237-250`: it is a pure
`safe_load`, no extension dispatch — this is exactly why the §B fixture bodies had to be valid
JSON (a superset relationship, not a dispatch), and it is why the four bodies parse correctly
either way.

## §F — the eleven-key end-to-end case

Added `case_24_eleven_key_feature_json_Done_is_skipped_end_to_end`, based on
`.claude/skills/harness/templates/feature.json`'s eight required keys plus the three optional
keys (`max_total_runs`, `github`, `factory`) from `feature-schema.json`, giving all eleven.

**Deviation from the dispatch's literal assertion, found empirically and corrected:** the first
draft of this case asserted `"ungranted (NOBODY)" not in stdout and "across 1 plan(s)" in
stdout`, matching the reading that "skipped" pairs with "found and cleared". That assertion
FAILED on its own first run — the real output was `"0 violation(s) across 0 plan(s)"`, not
`"across 1 plan(s)"`. Debugging the failure surfaced `check-plan-routes.py:568-569`
(`if _is_shipped(entry.path): continue`), which excludes a shipped feature from
`discover_plans()`'s own count entirely, not merely from its violations. The failure is what
found the behaviour, not a pre-check. `"across 1 plan(s)"` alone would also have been the wrong
assertion to prove the plan was *reached*, since it's satisfied identically by the checker never
finding the directory at all (case_19a3's fail-open). The case instead pairs the same eleven-key
document with only `status` flipped — `Done` (0 plans, no violation) then `Building` (1 plan, 1
violation on the fixture's ungranted path), the second run acting as the control for the first —
so only the status value changes the outcome, proving the document was actually parsed and
`_is_shipped` actually consulted. No schema-validity assertion was added (that is T-11's, per the
dispatch).

## §G — the two comments

`:867` → `# no feature.json at all`; `:871` → `# A feature.json THAT PARSES BUT IS NOT A
MAPPING`. `case_24_feature_yaml_*` and `case_24_no_feature_yaml_*` test **names** were left
unrenamed, per the dispatch's explicit instruction (the underscore spelling does not match the
grep, and nothing pins them).

Measured: `grep -c 'feature\.yaml' .claude/skills/harness/bin/test-check-plan-routes.py` = **0**.

## §H — Rule 15

`check-plan-routes.py:405` (the "first draft put the return OUTSIDE its own try" incident
record) was not touched, per instruction. Its remaining `feature.yaml` occurrences (`:238`,
`:405`, `:566`) are the operator's, not mine.

## §I — prohibited-tool window

`gh-sync.py`, `factory_decompose.py`, `factory_claim.py` were never invoked against
`.harness/features/`. The integration run above exercises their fixture-based suites
(`test-gh-sync.py`, `test-factory-integration.py`) against tempfile fixtures only, which is
legal.

## §J — T-05's verify, run exactly as written

```
python3 - <<'PY'
import subprocess, sys
bad = []
n = open('.claude/skills/harness/bin/test-harness-yaml-corpus.py').read().count('feature.yaml')
if n != 4:
    bad.append(...)
r = subprocess.run(['.claude/skills/harness/bin/run-unit-tests.sh'], capture_output=True, text=True)
if r.returncode != 0:
    bad.append(...)
print('\n'.join(bad) if bad else 'OK')
sys.exit(1 if bad else 0)
PY
```
Output: `OK`. Exit code: `0`.

`--kind integration`, run separately, in full:
```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration
...
97/97 checks passed.
PASS test-factory-integration.py
```
Exit code: `0`. Every `PASS test-*.py` line:
```
PASS test-validate-digest.py
PASS test-gh-sync.py
PASS test-check-state.py
PASS test-check-expertise.py
PASS test-gen-decisions-index.py
PASS test-bash-write-guard.py
PASS test-check-domain.py
PASS test-harness-yaml.py
PASS test-upgrade-config.py
PASS test-check-plan-routes.py
PASS test-merge-settings.py
PASS test-factory-integration.py
```
Note: the bare `run-unit-tests.sh` in T-05's `verify:` clause (no `--kind` flag) is a different,
narrower gate than `--kind integration` — `test-check-plan-routes.py` is in `INTEGRATION_SCRIPTS`
(`run-unit-tests.sh:18`), so `--kind integration` is the run that actually exercises the file
this task changed; both are reported above rather than treated as equivalent evidence.

## §K — the expected red that is not mine

Run directly against the live corpus (argv-less), after all restorations above, for real:
```
$ .claude/skills/harness/bin/check-plan-routes.py
scanning /Users/molchairuangutai/GitHub/harness/.harness/features/*/{plan.yaml,PLAN.md}
OK T-01 granted to harness-backend-dev, harness-dev-ops
...
35 violation(s) across 16 plan(s)
```
Exit code: `1`. `35 violation(s) across 16 plan(s)` — measured, matches the dispatch's stated
expectation exactly (no `feature.json` exists in any live feature dir until T-08). Not chased.

## Deliverable checklist

1. T-05 verify clause: exit 0, `OK` — shown in §J.
2. `--kind integration`: exit 0, full `PASS` list — shown in §J.
3. Three mutation runs, verbatim, each restored and hash/diff-verified — §C.
4. `feature.yaml` occurrence count in the file: **0**.
5. `git status --porcelain`:
```
 M .claude/skills/harness/bin/test-check-plan-routes.py
```
   (plus this receipt, untracked.)
6. No `feature.json` exists under `.harness/features/` — confirmed via `find`.
7. Nothing in A–G could not be done. The one deviation (§F's assertion shape) is disclosed above
   with the empirical evidence that forced it.
