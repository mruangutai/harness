# Receipt — harness-dev-ops — T-07 — cycle 1

## Task
Pin `inject-expertise.sh`'s unreadable-file guard (`[ -r "$f" ] || continue`, line 69 at HEAD —
the intent's cited line 68 has drifted by one) with a new `case13` in
`.claude/skills/harness/bin/test-inject-expertise.py`. Only that file was written.

## What case13 asserts
Fixture: `.harness/expertise/harness-qa.md` (craft), `.harness/harness/expertise/harness-qa.md`
(readable repository file, distinguishable body "REPO BODY THIRTEEN"), and a **dangling
symlink** at `.harness/kaya/expertise/harness-qa.md` created via `os.symlink` pointing at a
target that does not exist. `HOME` is a fresh temp dir via `fresh_home()`.

Four assertions, all required:
1. `r.returncode == 0`
2. injected context contains `"## Your Expertise — harness repository (repository tier)"` and
   `"REPO BODY THIRTEEN"`
3. `"kaya"` does not appear anywhere in the injected context
4. `r.stderr` decodes to the empty string

## Observation A — case13 against the shipped hook (unmutated)
Command:
```
python3 .claude/skills/harness/bin/test-inject-expertise.py
```
Result: `PASS case13: dangling symlink in repository tier -> unreadable guard skips it, no leak,
clean stderr`. Full suite: `19/19 cases passed.` Exit 0.

## Observation B — case13 against the guard-removed mutant (the acceptance proof)

Mutant construction (never touches the real script — copy first):
```
cp .claude/skills/harness/bin/inject-expertise.sh <scratch>/inject-expertise-mutant.sh
sed -i '' '/\[ -r "\$f" \] || continue/d' <scratch>/inject-expertise-mutant.sh
```
Diff check (must be exactly one removed line):
```
$ diff .claude/skills/harness/bin/inject-expertise.sh <scratch>/inject-expertise-mutant.sh
69d68
<   [ -r "$f" ] || continue
$ diff ... | grep -c '^<'
1
```
Confirmed: the mutant differs from the original by exactly the one guard line.

Run:
```
INJECT_EXPERTISE_BIN=<scratch>/inject-expertise-mutant.sh python3 .claude/skills/harness/bin/test-inject-expertise.py
```
Result:
```
FAIL case13: dangling symlink in repository tier -> unreadable guard skips it, no leak, clean stderr
        checks=[True, True, True, False, False] stderr='head: <tmp>/.harness/kaya/expertise/harness-qa.md: No such file or directory\n<scratch>/inject-expertise-mutant.sh: line 58: <tmp>/.harness/kaya/expertise/harness-qa.md: No such file or directory\n<scratch>/inject-expertise-mutant.sh: line 58: [: : integer expected\n'
18/19 cases passed.
```
Process exit status: **1** (non-zero — `main()` returns `fails`, `sys.exit(1 if main() else 0)`).

case13 **FAILS** under mutation, exactly as required. The failing checks are index 3 (`"kaya"
not in ctx` — false, "kaya" leaked into the injected context because the dangling symlink was
read as if valid) and index 4 (`stderr == ""` — false, `head` and the `wc -l`/`[` integer
comparison in `cap_body` both error on the dangling link).

Mutant copy deleted after the run (`rm -f <scratch>/inject-expertise-mutant.sh`) — never
committed.

## Observation C — restore verification
`.claude/skills/harness/bin/inject-expertise.sh` was never edited (only a copy in the scratch
directory was mutated). Confirmed with:
```
$ git diff -- .claude/skills/harness/bin/inject-expertise.sh
```
Output: empty. Exit 0.

## verify: — run exactly as specified in the plan
```
set -u
out=$(.claude/skills/harness/bin/run-unit-tests.sh --kind unit 2>&1)
echo "$out"
echo "$out" | grep -q '^PASS test-inject-expertise.py$' || exit 1
echo "$out" | grep -q '^FAIL ' && exit 1
grep -q 'def case13' .claude/skills/harness/bin/test-inject-expertise.py || exit 1
grep -q 'os.symlink' .claude/skills/harness/bin/test-inject-expertise.py || exit 1
exit 0
```
Full runner output read in full (not just tail) — final relevant lines:
```
...
PASS case13: dangling symlink in repository tier -> unreadable guard skips it, no leak, clean stderr

19/19 cases passed.
PASS test-inject-expertise.py
```
No `^FAIL ` line anywhere in the full multi-suite output. `def case13` and `os.symlink` both
present in the test file. `VERIFY_EXIT=0` (captured via `$rc`, not a piped `$?`).

## Case count
Before: 12 `def caseN()` functions (case1..case12), 18 total case reports (case5 and case12
each emit multiple sub-reports). After: 13 `def caseN()` functions, 19 total case reports.

## Files touched
- `.claude/skills/harness/bin/test-inject-expertise.py` (added `case13()`, added to `main()`
  call list after `case12()`; cases 1-12 untouched, not renumbered)

`.claude/skills/harness/bin/inject-expertise.sh` — untouched, verified via empty `git diff`.
