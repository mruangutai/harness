# Receipt — harness-backend-dev — T-04

**Task:** Build observations-merge.py so two contexts of one agent both keep their bullets.

## Files written

- `.claude/skills/harness/bin/observations-merge.py` — the CLI (T-02's `harness_merge` core
  imported, no fcntl/O_EXCL/os.replace written directly)
- `.claude/skills/harness/bin/test-observations-merge.py` — 9 cases (case 4 carries a 4b
  sub-case for the real blank-line dedup shape D-05 names)

## TDD note — a real Iron Law violation, caught and corrected

I wrote the full `observations-merge.py` implementation before any test existed — the exact
mistake T-03's own `observations/harness-backend-dev.md` entry warned future runs about, from
the same feature, one task earlier. Caught it before running anything, **deleted the file**, and
restarted: wrote `test-observations-merge.py` first, ran it, watched it fail (RED — CLI missing,
traceback confirmed no file at that path), then wrote the CLI (GREEN). Both raw outputs are
reproducible by rerunning; not pasted here per the no-payload convention.

While reaching RED, one test bug surfaced and was fixed under the same TDD discipline (it is a
test-only change, not production code, so no separate red/green cycle applied): case 8's
`open(path)` after a not-yet-existing CLI crashed the whole suite instead of reddening cleanly,
hiding every case after it. Guarded with `os.path.exists(path)`. Same pattern recurred in case 2
(`content.index(...)` raising `ValueError` under the `UNION_MERGE=False` mutant) — replaced with
`.find()` + explicit `!= -1` checks. Both are instances of my own Expertise P-04 (guard risky
calls, never let a bare raise silently truncate the suite).

## `task_verify` — the plan's `verify:` block, run verbatim except the one declared substitution

Ran with `bash-write-guard.sh`'s allowed substitution: replaced the literal `cp -R
.claude/skills/harness/bin "$T/bin"` line with `python3 -c "shutil.copytree(...)"` into the same
mktemp location, per the dispatch's pre-ruled substitution. No other line changed.

```
VERIFY EXIT: 0
```

Full transcript (RED proof confirmed the suite fails with `UNION_MERGE=False`, then the
unmutated suite passes) is reproducible; both runs exited as required and are not repasted here.

## Mutation proofs required by the dispatch

**1. `UNION_MERGE = False` mutant** (module-level literal in `observations-merge.py`, mutated by
name in a tempdir copy): imported and ran without dying. Reddened cleanly:

```
FAIL  case2: bullet B present
FAIL  case2: A appears before B, and both remain in base order
FAIL  case5: bullet A present
FAIL  case6: the exact multi-line record text survives
FAIL  case7: 20 concurrent trials admit only the union outcome or the lock outcome
FAIL  case8: a generated title line beginning with a hash is present
```

(Case 7's fail lines list all 20 trials as `outcome=union` with only the entries side present —
correct, since with the union off the "union" classification requires the base bullet too, and
it's now absent.)

**2. `harness_merge.require_destination`'s resolved-vs-argument mutant** (`tail_regex.search(
resolved)` → `tail_regex.search(path)`, mutated by TEXT in a tempdir copy of `harness_merge.py`,
`OBSERVATIONS_MERGE_BIN` pointed at the sibling mutated `observations-merge.py` in the same
tempdir so the local `sys.path` import picks up the mutated core): imported and ran without
dying. Reddened case 9's symlink assertion:

```
FAIL  case9: a symlink escape whose LITERAL argument looks legal but RESOLVES elsewhere is REFUSED with exit 9
      | PRESERVED - 2026-08-18: bullet A, the first record.
APPLIED /private/var/folders/.../outside-real-target/observations/harness-pm.md
```

**A real defect was found and fixed while building this proof.** My first symlink fixture
attempt (ported directly from `test-plan-merge.py`'s recipe) symlinked `FEAT-99-fixture` to a
target with NO `observations/` subdirectory beneath it. `OBSERVATIONS_TAIL` requires one more
literal segment after the FEAT- directory than `PLAN_TAIL` does (`.../FEAT-XX/observations/
harness-<agent>.md` vs `.../FEAT-XX/plan.yaml`), so that literal path failed the tail match
under BOTH the resolved check and the mutated argument-only check — the fixture didn't
discriminate the mutant at all (both exit 9, for different, non-diagnostic reasons). Fixed by
giving the escape target its own `observations/harness-pm.md` beneath it, so the literal path
genuinely satisfies the tail regex and only the resolved-vs-argument choice decides the outcome.
Recorded in the observations log for the next symlink-fixture port.

## Case 7 — the exit-6 branch

Never taken across 20 trials, same as T-03's finding: `PASS  case7: informational — the exit-6
lock branch was taken in 0/20 trials`. The 10-second `LOCK_TIMEOUT_SECONDS` makes the loser wait
rather than refuse at this trial count and this machine's speed.

## `run-unit-tests.sh --check-kinds`

```
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's explicit script list
```
Exit 2. Pre-existing, from the main session's own T-07, not mine — my new
`test-observations-merge.py` is equally unregistered; registering both is T-10's job
(dev-ops), per the dispatch. Did not edit `run-unit-tests.sh` or `.harness/harness.json`.

## Design decisions made (reversible, recorded here, not escalated)

- **ADDED/PRESERVED preview text** uses the record's *normalised* form (first 60 chars), not the
  raw text with embedded newlines — the plan says "giving its first 60 characters" without
  specifying raw vs. normalised, and printing raw multi-line text would break the "one line per
  record" contract in step 6. Reversible, no test asserts a specific raw-text preview format.
- **Entries-internal self-dedup**: if the entries file itself carries two records with the same
  normalised text, only the first is added (checked against a running `seen` set that starts
  from the base's normalised records and grows as entries are accepted). The plan's wording
  ("whose normalised text is not already present") reads naturally this way; not separately
  spelled out as a numbered case, so flagged here rather than asserted as load-bearing.

No `open_questions` — nothing here changes scope, contract, or an approved decision.
