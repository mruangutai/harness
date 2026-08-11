# Receipt — harness-backend-dev — FEAT-13 fix01

**BLUF:** all three vacuous-pass gaps closed. Three new assertions added (`tests_added: 3`), each
proven to redden under a real mutation and confirmed clean (byte-identical) on restore.
`test-factory-decompose.py:1030` renamed and its adjacent comment fixed — it no longer implies
coverage it never had. Both suites green (unit 10/10 scripts / 610 checks, integration 97/97),
T-01's own `verify:` also re-run and passing, `git status --porcelain` on
`.claude/skills/harness/bin/` shows only the four intended test files.

**All line numbers below were re-verified with `grep -n` against the current worktree state after
every edit** (not computed by arithmetic) — see the exact commands under each section.

## Mutation method

Per the dispatch's precedent: copied `.claude/skills/harness/bin/` to a scratchpad
(`/private/tmp/.../scratchpad/mutbin/`) using **literal absolute paths**, never a shell variable —
`bash-write-guard.sh` parses Bash-tool `cp` targets textually and does not expand `$VAR`; a variable
target like `$SCRATCH/mutbin` is read as the literal string and denied as "outside your domain"
even though the real destination is outside the repo entirely. Confirmed empirically (see
`open_questions` Q1). All mutation runs used `cd <scratchpad>/mutbin && python3 test-*.py` — script-dir-first
`sys.path` guarantees `import factory_gh`/`factory_claim`/`factory_land` resolves the mutated copy,
not the worktree's. Every mutation's pre/post state verified by `sha256sum` against the worktree
original; every restore hash-matched.

## FIX 1 — `_ISSUE_ITEM_QUERY` no-state-scoping pin

**Assertion:** `.claude/skills/harness/bin/test-factory-gh.py:674` (verified:
`grep -n "issue_board_item_id: _ISSUE_ITEM_QUERY" test-factory-gh.py`). STRUCTURAL, not a keyword
blacklist and not a whole-text equality check: extracts the argument-name list inside the query's
`issue( ... )` selection via `re.search(r"issue\s*\(([^)]*)\)", ...)`, splits on `,` then `:`, and
asserts the result equals exactly `["number"]`. **Scope, stated precisely: this guards the
argument list of the `issue(...)` selection only** — it does not (and is not claimed to) guard a
state filter added elsewhere in the query text, e.g. on the `projectItems(first: 100, ...)`
connection.

**(a) reddens under a state-scoping form not copied from the assertion's own literals** — mutation:
```
-    issue(number: $number) {
+    issue(number: $number, state: OPEN) {
```
`factory_gh.py:297`. Assertion's own code contains no literal `"state"` or `"OPEN"` anywhere — it
only names the argument `number` and manipulates the parenthesised text generically. Command/cwd:
`cd /private/tmp/.../scratchpad/mutbin && python3 test-factory-gh.py`. Verbatim red:
```
FAIL  issue_board_item_id: _ISSUE_ITEM_QUERY's issue(...) selection takes exactly the argument {number} — no state/filter argument of any spelling
        arg_names=['number', 'state'] query='query($owner: String!, $name: String!, $number: Int!) {\n  repository(owner: $owner, name: $name) {\n    issue(number: $number, state: OPEN) {\n      projectItems(first: 100) {\n        totalCount\n        nodes { id project { number } }\n      }\n    }\n  }\n}\n'
1 of 154 FAILING.
```
Only that one assertion failed (154 total, 153 still passed) — isolated proof, not collateral noise.

**(b) does NOT redden under a pure whitespace/reformat change:**
```
-    issue(number: $number) {
+    issue(
+      number:   $number
+    ) {
```
Same cwd/command. Verbatim: `154/154 checks passed.` — zero failures.

Restored, verified `sha256sum factory_gh.py` == worktree original after each of the two mutations.

**Rename at `test-factory-decompose.py:1030`** (verified:
`grep -n "the lookup call args are exactly" test-factory-decompose.py`): old name claimed "the
lookup carries no state scoping" while asserting only the recorder's call-tuple equality —
`issue_board_item_id` takes no `query`/`state` kwarg at all, so that assertion could never redden
from the regression it was named for. Renamed to "the lookup call args are exactly (repo,
issue_num, board_number) — NOT the no-state-scoping property, which this check cannot exercise
(see comment above)". Also rewrote the block comment starting at `test-factory-decompose.py:992`
(verified: `grep -n "^# --- D-04-3c" test-factory-decompose.py`), which stated the same false claim
in prose ("it pins that decompose's own call shape never asks the lookup to filter by state") —
left standing it would have kept the audit trap alive even with the check renamed.

**Where the no-state-scoping property is guarded now, precisely:** on `_ISSUE_ITEM_QUERY`'s
`issue(...)` argument list, at `test-factory-gh.py:674` — the only place that reads the query's
own text. It does not cover a state filter added to a different selection in the same query (see
the scope note above). `test-factory-decompose.py:1030` (renamed) verifies only decompose's own
call-site arguments — a different, narrower property, and no longer misnamed as the query-text one.

## FIX 2 — `issue_view` field lists at `factory_claim.py:274` and `factory_land.py:63`

**Design call — fakes-vs-direct-assertion:** ran the stated criterion rather than reasoning about
it. Read both fixture builders: `test-factory-land.py`'s `Recorder.issue_view` ignored `fields` and
returned `{"title":..., "state":...}` unconditionally; `test-factory-claim.py`'s ignored `fields` and
returned the full `issue_data(...)` dict (which always carries exactly the five keys production
requests). Made **both fakes honour `fields`** (`{k: v for k, v in full.items() if k in fields}`).

**The no-ripple arithmetic, stated explicitly (this is what answers "which existing assertions
changed behaviour"):** the qa mutant-proof cited in the dispatch measured the ORIGINAL (fields-blind)
suites at 95/95 (`test-factory-claim.py`) and 56/56 (`test-factory-land.py`). After this cycle's
changes — the fake-honouring fix PLUS one new `"state" in fields` assertion, per file — the counts
are 96/96 and 57/57: **exactly +1 in each file, and no other check's pass/fail changed.** That +1
is the new assertion, nothing else. This is the actual evidence the fake change rippled nothing;
production always requests every key its own fixtures carry, so filtering by `fields` is currently
a no-op on every pre-existing case.

This is the stronger fix per the dispatch's "if cheap and no ripple, do it" rule: with fakes
honouring `fields`, dropping `"state"` from production now produces a genuine **behavioural** red
(wrong exit code, crash) rather than only an argv-shape mismatch — see the land mutation below,
where it cascades into 6 other checks failing on the real exit code, not just the field list.
Kept the mandated explicit `"state" in fields` assertion at both call sites as well — additional,
not a substitute; it is the one that names the cause when the behavioural cascade fires.

### `factory_land.py:63`

**Assertion:** `test-factory-land.py:235` (verified:
`grep -n "requested fields include" test-factory-land.py`, in the `(M1)` happy-path block) —
`"state" in issue_view_calls[0][1][2]`.

**Mutation:**
```
-    issue = factory_gh.issue_view(args.repo, args.issue, ["title", "state"])
+    issue = factory_gh.issue_view(args.repo, args.issue, ["title"])
```
`factory_land.py:63`. Command/cwd: `cd /private/tmp/.../scratchpad/mutbin && python3 test-factory-land.py`.
Verbatim red (direct assertion, plus the behavioural cascade the fake-honouring change produced):
```
FAIL  (M1) exits 0
        2
...
FAIL  (M1) issue_view's requested fields include "state"
        [('issue_view', ('acme/widget', 42, ('title',)))]
Traceback (most recent call last):
  ...
  json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```
M1 now exits 2 (the closed-issue refusal path fires because `.get("state")` reads `None`) instead
of 0 — total-outage behaviour, not just an argv mismatch. Six other M1 checks cascaded to FAIL as a
side effect of the same root cause (exit 2 instead of 0); the direct field-list assertion is the
one that names the cause. Restored; `sha256sum factory_land.py` matched the worktree original.

### `factory_claim.py:274`

**Assertion:** `test-factory-claim.py:391` (verified: `grep -n "requested fields include"
test-factory-claim.py`, in the `(C2)` happy-path block) — `"state" in c2_issue_view_calls[0][1][2]`.

**Mutation:**
```
-            repo_name, num, ["number", "title", "state", "assignees", "labels"],
+            repo_name, num, ["number", "title", "assignees", "labels"],
```
`factory_claim.py:274`. Running the full suite from the mutated cwd crashes before reaching C2: an
earlier, unrelated M7-labelled test at `test-factory-claim.py:336` does an unguarded
`json.loads(out)` against what is now an empty refusal stream and raises uncaught — itself further
evidence of the same total-outage regression, just hit further upstream by a test that was not
written defensively. **This is the tradeoff the fakes-honouring fix created:** turning the fake
behavioural makes the mutation's blast radius bigger, and here it is big enough to kill the whole
script before my own C2 assertion gets a chance to run.

To prove **C2's own new assertion** reddens in isolation, independent of that earlier crash, built
a truncated copy of the test file — module setup (source lines 1–295: imports, `Recorder`,
`board_item`, `issue_data`, `run_main`, `patch_gh`) plus the C2 block only (source lines 375–392,
which brackets its own `json.loads` in `try/except` and does not crash) — via:
```python
lines = open("test-factory-claim.py").read().splitlines(keepends=True)
head = "".join(lines[0:295])
c2 = "".join(lines[374:392])
src = head + c2 + "print('\\nISOLATED C2 RUN DONE:', RAN, FAILS)\n"
open("_isolated_c2.py", "w").write(src)
```
run against the same mutated `factory_claim.py`, from:
```
cd /private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/cd83b531-197f-4da6-a4a5-9bb0ec5fcaa5/scratchpad/mutbin && python3 _isolated_c2.py
```
Verbatim red:
```
FAIL  (C2) whole stdout parses as one JSON object
FAIL  (C2) exit 0
        1
FAIL  (C2) issue_view's requested fields include "state"
        [('issue_view', ('acme/widget', 42, ('number', 'title', 'assignees', 'labels')))]

ISOLATED C2 RUN DONE: 3 3
```
The temp isolation script (`_isolated_c2.py`, built from the exact snippet above) was deleted
immediately after use and never left the scratchpad; it is reproducible from that snippet if a
reviewer needs to re-run it. Restored `factory_claim.py`; `sha256sum` matched the worktree original.

## T-01 `verify:` (task_verify)

Fix cycle against T-01's approved file set; re-ran T-01's own `verify:` verbatim, from the worktree
root:
```
bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit &&
python3 .claude/skills/harness/bin/test-factory-integration.py &&
grep -q 'def issue_board_item_id' .claude/skills/harness/bin/factory_gh.py &&
! grep -q 'factory_gh\.project_items' .claude/skills/harness/bin/factory_decompose.py &&
! grep -q 'factory_gh\.project_items' .claude/skills/harness/bin/factory_land.py &&
test "$(grep -c 'factory_gh\.project_items' .claude/skills/harness/bin/factory_claim.py)" = 1
```
Exit 0. `test-factory-integration.py` tail: `97/97 checks passed.` The unit run's own tail (all 10
scripts, no FAIL lines) is the same output already shown under "Final gates" below. `task_verify: pass`.

## Final gates (worktree root)

```
bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit         # exit 0, 610/610 checks, 10/10 scripts
bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration  # exit 0, 97/97 checks
git status --porcelain -- .claude/skills/harness/bin/
```
```
 M .claude/skills/harness/bin/test-factory-claim.py
 M .claude/skills/harness/bin/test-factory-decompose.py
 M .claude/skills/harness/bin/test-factory-gh.py
 M .claude/skills/harness/bin/test-factory-land.py
```
Exactly the four intended test files, no production files, no scratchpad residue.

## files_touched

- `.claude/skills/harness/bin/test-factory-gh.py` — FIX 1 assertion
- `.claude/skills/harness/bin/test-factory-decompose.py` — FIX 1 rename + comment fix
- `.claude/skills/harness/bin/test-factory-land.py` — FIX 2 fake fix + assertion
- `.claude/skills/harness/bin/test-factory-claim.py` — FIX 2 fake fix + assertion

## open_questions

- Q1 (non-blocking, informational): `bash-write-guard.sh`'s Bash-tool `cp`-target extraction does
  not expand shell variables — a `cp ... "$SCRATCH/mutbin"` command is parsed as the literal string
  `$SCRATCH/mutbin` and denied as in-repo-but-out-of-domain, even when the actual resolved
  destination is outside the repo (which the guard's own `..`-relpath carve-out would otherwise
  pass). Worked around by using literal absolute scratchpad paths throughout, per this cycle's
  "adopt or beat the precedent" instruction. Flagging since the qa precedent this dispatch cited
  may hit the same thing; not filing as #218/#241/#242 since it's a different mechanism (variable
  non-expansion, not the direct-mutation block those cover).
