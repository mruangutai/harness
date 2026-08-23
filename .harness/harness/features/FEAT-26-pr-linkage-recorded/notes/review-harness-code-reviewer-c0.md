# Code review — FEAT-26-pr-linkage-recorded — reviewed `ffe826e..bad32441dfc0`

## Verdict: FAIL (Stage 1)

## Stage 1 — spec compliance

**must_fix — T-07 omission, SKILL.md:211-212.** The plan's own intent for T-07 required
correcting the paragraph reading "the harness composes no issue-closing text into any pull
request body" because `closes` (documented four lines above, `SKILL.md:200`) makes that claim
false the moment it exists. The sentence is **still present, verbatim, unchanged**, in the
reviewed SHA:

```
211:Nothing links the branch to the parent issue, and nothing needs to: **the harness composes no
212:issue-closing text into any pull request body**, and the parent is closed by `gh-sync.py ship`,
```

Four lines above it, the mirror table now reads: "`gh-sync.py closes <feature-dir>` — prints one
`Closes #N` line per number in `feature.json`'s `github.source_issues`" (SKILL.md:200) — composing
issue-closing text is exactly what `closes` does. The doc self-contradicts.

**Why the task's own verify didn't catch it:** the source text wraps across two lines ("composes
no" / "issue-closing text..."), but T-07's verify uses a single-line `grep -q '<full phrase>' ...
&& exit 1`. I ran it directly against both `ffe826e` and `bad32441dfc0`:

```
$ grep -q 'composes no issue-closing text into any pull request body' SKILL.md; echo $?
1   # (at both ffe826e and bad32441dfc0 — never matches, because of the line wrap)
```

The check is vacuously satisfied whether or not the sentence was ever removed, so a real,
false, DEC-188-class "prose claim a command can check, written true and left standing after it
became false" — exactly the defect class `bad32441dfc0`'s own commit message describes fixing at
`feature-schema.json:28` — shipped in the same commit that closed that class elsewhere. This is
the P-14/DEC-169 pattern precisely: a token-sweep proves which words are absent, never that the
sentence they form together is false.

This is a T-07 (traces REQ-02, REQ-03, REQ-06) omission — the required correction was not made —
and a doc that will actively mislead a future author about what `closes` does. Fix: rewrite
SKILL.md:211-212 to the true statement (the harness DERIVES the closing keywords and prints them,
never posts, never closes a ticket itself — the language the T-07 intent already spells out), and
repair the task's own verify to a grep pattern that spans the wrap (e.g. `grep -Pzo` or a Python
substring check on the joined text) so a future regression is actually caught.

**Everything else in Stage 1 checked out:**
- T-01 schema property (`feature-schema.json:28-33, 90-94`) and its five test cases: read at
  HEAD, all pass (`test-validate-feature-json.py`), no `required`/`additionalProperties` touched.
- T-02 mirror (`gh-sync.py` `load_recorded`, `save_recorded`, `parse_source_issues`, `cmd_open`):
  read against the diff; the `save_recorded` absent-file refusal, the fixed-key rebuild, and the
  per-run refresh in `cmd_open` all match D-07/D-08/T-02's wording exactly. Four required test
  names present and green.
- T-03 `_record_pr`/`record-pr`/`--pr` wiring: all seven required test names present, plus the
  MF-1 regression test for the `int(pr_arg)` traceback the dispatch's own history flagged. Ran
  `test-gh-sync.py` at HEAD — `ALL PASSED`.
- T-04 `cmd_closes`: all four required cases present and green, including the no-gh-call
  assertion against the fake gh's own log (not just exit code) and the out-of-order assertion.
- T-05 INV-28 (`check-state.sh`): all six required labels present and green
  (`test-check-state.py`), warn-level, gated on `github.sync`, bool exclusion present in the shell
  (`isinstance(_pr, int) and not isinstance(_pr, bool)`).
- T-06 backfill: re-ran the task's own 23-entry verify block against the eleven touched
  `feature.json` files at HEAD — `bad=0`. Numbers match the plan's stated attributions exactly.
- T-08 DEC-200: re-ran the anchor-agreement check — `DECISIONS-INDEX.md`'s `@6568` lands exactly
  on `## DEC-200` in `DECISIONS.md`. DEC-186's scope question is correctly left open, not settled.
- No scope creep found: the diff's only touches outside the eight tasks' named files are the
  incidental trailing-newline additions `_atomic_write` makes to the four already-integer `pr`
  backfills (FEAT-20/21/22 feature.json) — a side effect of running `record-pr`, not a hand edit.

## Stage 2 — code quality (recorded, does not change the FAIL)

1. **`gh-sync.py:596-598` (dispatch's flagged line 597) — untested refusal branch, and it is
   exactly the bool-exclusion class this feature exists to get right.** When `gh pr list`
   returns exactly one element whose `number` field is not an int (missing, or a bool), the code
   correctly refuses to write:
   ```python
   number = found[0].get("number") if isinstance(found[0], dict) else None
   if not isinstance(number, int) or isinstance(number, bool):
       print(f"gh-sync: no merged pull request found on branch {branch}")
       return
   ```
   No case in `test-gh-sync.py` ever has the fake gh return `{"number": true}` or a dict missing
   `number`. I confirmed the gap is real, not cosmetic: dropping just the `isinstance(number,
   bool)` clause (a one-line "simplification" of exactly the kind this commit's own history shows
   this codebase making) turns a correct refusal into a silent `doc["pr"] = True` write —
   verified by hand-evaluating both the current and mutated guard against
   `found = [{"number": True}]`. Severity: med — real `gh` never returns a bool here, so the
   production likelihood is low, but the class (fail-open on a bool where `isinstance(x, int)` is
   true) is the one this repo has shipped twice before, and the test that would catch a
   regression here does not exist.

2. **No test drives the exact combination the plan's own intent names: `--pr` given AND a `pr`
   already recorded that differs.** T-03's intent states this in so many words: "It is never
   overwritten, on any path, including when pr_arg is given and differs." The suite has
   "record-pr never overwrites a pr that is already an integer" (query path, no `--pr`) and
   "record-pr --pr writes the number given without querying" (no pre-existing `pr`), but never
   both at once. Reading the code (`gh-sync.py:561-566`), the existing-int check runs before the
   `pr_arg is not None` branch, so the implementation is correct — but nothing pins it against a
   future reordering. Severity: low — code verified correct by inspection, gap is coverage only,
   on a clause the plan explicitly called out by name.

3. `check-state.sh`'s INV-28 status comparison, `str(pdoc.get("status", "")).split()[:1] !=
   ["Done"]`, is a first-whitespace-token match rather than the "exact string `Done`" the
   comment two lines above it claims. It doesn't misfire on any realistic status value (all seven
   enum values are single tokens), so this is a style note, not a finding with a failure
   scenario — not gating.

## Test runs performed (targeted only, per dispatch)
- `python3 .claude/skills/harness/bin/test-gh-sync.py` → `ALL PASSED`
- `python3 .claude/skills/harness/bin/test-check-state.py` → exit 0, all INV-28 lines `ok`
- Confirmed both scripts are wired into `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` (not dead).
