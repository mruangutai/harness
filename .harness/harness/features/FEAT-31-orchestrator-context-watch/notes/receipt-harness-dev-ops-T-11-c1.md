# Receipt — harness-dev-ops — T-11 — c1

## Task
FEAT-31 T-11: close the test-kind misclassification class by appending explicit paths
to `test_kinds.integration.detect` in `.harness/harness.json`, matching every entry in
`run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` array.

Cross-checked the dispatch's quoted `verify:` byte-for-byte against `plan.yaml`'s T-11
block (loaded via `harness_yaml.load_file`, not read whole) — identical. No mismatch.

## Re-derived counts at HEAD e5f88c4 (not trusted from the intent paragraph, which is stale
at 7299669)

- `run-unit-tests.sh` `INTEGRATION_SCRIPTS`: **14** entries (measured directly, printed
  below), not the intent's stale "12".
- `test_kinds.integration.detect` before edit named **6** explicit bin paths
  (`test-check-state.py`, `test-factory-integration.py`, `test-gh-sync.py`,
  `test-check-plan-routes.py`, plus two FEAT-30 arrivals: `test-feature-worktree.py`,
  `test-expertise-merge.py`) — not the intent's stale "4".
- Delta (`INTEGRATION_SCRIPTS` minus what `detect` names): **8**, unchanged from the
  intent's premise despite both base numbers moving. This matches Mike's own re-derivation
  in the dispatch (14 and 6, delta 8), not the plan's stale 12/4.
- `UNIT_SCRIPTS`: 18 entries, 0 of them already matched by `integration.detect` (correct —
  no cross-contamination existed before my edit).

Measured INTEGRATION_SCRIPTS (14): test-validate-digest.py, test-gh-sync.py,
test-check-state.py, test-check-expertise.py, test-gen-decisions-index.py,
test-bash-write-guard.py, test-check-domain.py, test-harness-yaml.py,
test-upgrade-config.py, test-check-plan-routes.py, test-merge-settings.py,
test-factory-integration.py, test-feature-worktree.py, test-expertise-merge.py.

## Prediction before running verify

Predicted (matching Mike's stated figure, re-derived independently above, not copied):
`absent from detect` = **8**, `wrongly in detect` = **0**, named misses = the 8 listed in
the dispatch's intent (test-validate-digest.py, test-check-expertise.py,
test-gen-decisions-index.py, test-bash-write-guard.py, test-check-domain.py,
test-harness-yaml.py, test-upgrade-config.py, test-merge-settings.py).

## verify — BEFORE edit

Command (verbatim from plan T-11 `verify:`, byte-diffed against the dispatch's quoted
copy — identical):

```
python3 -c "
import json, re
d = json.load(open('.harness/harness.json'))
ig = [g.strip() for g in d['test_kinds']['integration']['detect'].split('|')]
base = set(g.rsplit('/', 1)[-1] for g in ig)
src = open('.claude/skills/harness/bin/run-unit-tests.sh').read()
ints = re.findall(r'\"([^\"]+)\"', re.search(r'INTEGRATION_SCRIPTS=\((.*?)\)\n', src, re.S).group(1))
units = re.findall(r'\"([^\"]+)\"', re.search(r'UNIT_SCRIPTS=\((.*?)\)\n', src, re.S).group(1))
miss = [n for n in ints if n not in base]
wrong = [n for n in units if n in base]
print('integration array', len(ints), 'absent from detect', len(miss), miss)
print('unit array', len(units), 'wrongly in detect', len(wrong), wrong)
raise SystemExit(0 if not miss and not wrong else 1)
"
```

Output:
```
integration array 14 absent from detect 8 ['test-validate-digest.py', 'test-check-expertise.py', 'test-gen-decisions-index.py', 'test-bash-write-guard.py', 'test-check-domain.py', 'test-harness-yaml.py', 'test-upgrade-config.py', 'test-merge-settings.py']
unit array 18 wrongly in detect 0 []
```
Exit code: **1** (non-zero, confirms task premise: 8 absent, matches prediction exactly).

## Edit made

Single `Edit` to `.harness/harness.json`, `test_kinds.integration.detect` field only.
Appended the ten literal paths from the dispatch, each separated by `|`, preserving all
six pre-existing explicit paths and the leading `tests/integration/**` glob. Nothing else
in the file touched.

## verify — AFTER edit

Same command, output:
```
integration array 14 absent from detect 0 []
unit array 18 wrongly in detect 0 []
```
Exit code: **0**.

## Other checks

- JSON syntax: `python3 -c "import json; json.load(open('.harness/harness.json'))"` → no
  exception, prints nothing extra (i.e. loads clean).
- `git diff -- .harness/harness.json` shows exactly two hunks: (1) the `integration.detect`
  line, (2) T-03's pre-existing `budgets.orchestrator_context_warn_tokens` +
  `_orchestrator_context_warn_tokens_rationale` addition, unmodified by me — confirmed
  present verbatim, byte-identical to before my edit (re-read via `json.load` and printed;
  the two new keys and their values are unchanged).
- `.claude/skills/harness/templates/harness.json` diff: empty — untouched, confirmed via
  `git diff --stat`. Its `integration.detect` remains `tests/integration/**` with `cmd: null`,
  consistent with the task's premise that a fresh project should not inherit this
  repository's own bin-test paths.
- `git status --porcelain` before and after my edit: identical set of other modified/
  untracked files (STATE.md, feature.json, observations logs, other agents' receipts,
  plan.yaml, context-watch.py, a finding note) — none of these are mine; they belong to
  concurrent/earlier work in this multi-agent run. My edit added no new untracked or
  modified paths beyond `.harness/harness.json`, which was already modified (by T-03)
  before I started.

## Standing-duty questions, answered

1. **Basename-only comparison hole**: yes, it exists. `base = set(g.rsplit('/', 1)[-1]
   for g in ig)` strips all directory components, so a path appended with the wrong
   directory (e.g. `foo/bar/test-harness-yaml.py`) would satisfy `miss` while classifying
   nothing for real globbing purposes (globs match full paths, not basenames). I did not
   rely on this hole: every one of my ten appended paths carries the correct, verified
   directory `.claude/skills/harness/bin/`, matching the existing six entries' directory
   exactly, and the files that already exist at those paths were confirmed to be at that
   directory (the ones not yet created by T-07/T-12 are placeholders that harmlessly match
   nothing, per the task's own stated design).
2. **The `wrong` check** (`wrong = [n for n in units if n in base]`) is present and would
   fire: it is exactly what stops "fixing" this by pasting all 18 `UNIT_SCRIPTS` names into
   `detect` too — doing that would immediately produce `wrongly in detect 18` and a non-zero
   exit. I did not touch `UNIT_SCRIPTS` or `test_kinds.unit.detect`.
3. **What makes this exit non-zero**: any INTEGRATION_SCRIPTS basename absent from
   `integration.detect`'s explicit list (`miss` nonempty), OR any UNIT_SCRIPTS basename
   present in that same `detect` (`wrong` nonempty). After my edit, both are empty lists,
   so the gate is satisfied on both axes — not just the one it started failing on.

## Decisions cited

- **DEC-197** (@6362, current anchor — re-checked in this worktree's
  `DECISIONS-INDEX.md`, not from a remembered line number): "A test file matching two
  `detect` globs resolves to the kind that names it explicitly, never the catch-all;
  nothing implements it, so this entry is the enforcement." This is why appending explicit
  paths here is meaningful even though every one of them still also matches
  `test_kinds.unit.detect`'s catch-all `.claude/skills/harness/bin/test-*.py` — DEC-197
  is the rule that resolves the collision, not code, so this data change is what makes it
  operative for these ten files. Closes plan Q-B.
- **DEC-160** (@3996): `check-domain.sh` denies a run-state write carrying non-whitelisted
  keys, and any decision adding a `harness.json` key must say so. Not directly triggered —
  I added no new key, only extended an existing string value — but confirms this file's
  key set is a controlled surface and I stayed inside it.
- **DEC-174** (@4663, am.1–am.4): the harness plans its own work but never executes changes
  to its own enforcement layer (hooks/validators/gate scripts). This is why T-12 — the
  `--check-kinds` cross-check in `run-unit-tests.sh` that would make this class
  structurally impossible to reopen — is main-session-direct and explicitly out of my
  reach; I did the data half only, per the scope fence.

## Open question about T-12's absence (not acted on, no scope creep)

Without T-12's cross-check landing, this data fix is durable only until the next new
`test-*.py` bin script is added and someone forgets to update both this `detect` string
and `run-unit-tests.sh`'s arrays by hand (per Expertise gotcha G-03, already known). I have
not treated this as a reason to touch `run-unit-tests.sh` — that is explicitly fenced off
to T-12/main-session — and raise it only as an `open_question` per the dispatch's
instruction.
