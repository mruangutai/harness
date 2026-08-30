# Receipt — validate-substring-c29 (cycle 29, resumed under operator authorization)

## BLUF

**BLOCKED.** The dispatch's premise — that the `re.search(r"\b1 file\(s\)", r.stderr) is None`
predicate fix and `import re` at line 13 are already applied to
`.claude/skills/harness/bin/test-validate-feature-json.py` — is **not true of this worktree right
now**. The file has zero uncommitted changes, and worktree HEAD is `f9a4233c47fced65c2a7eb63ff3949884b65ccdb`,
not the `1d292c2b2e22486fd7ad47fa9021ddec880dabcb` the dispatch names. I did not edit the source file
(per the non-goals) and did not fix anything silently. I ran the requested acceptance checks against
the actual current state so the discrepancy is grounded in fresh evidence, not assumption.

## What I found

1. **HEAD mismatch.** `git rev-parse HEAD` → `f9a4233c47fced65c2a7eb63ff3949884b65ccdb`. The
   dispatch asserts HEAD is the merge `1d292c2b2e22486fd7ad47fa9021ddec880dabcb`. These are
   different commits — the worktree has moved (or was never at) the commit the dispatch describes.

2. **The fix is absent.** `.claude/skills/harness/bin/test-validate-feature-json.py` line 13 is
   `import sys` (no `import re` anywhere in the import block — confirmed by reading lines 1-23).
   Lines 349-351 still contain the ORIGINAL predicate:
   ```
   check("case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep "
         "(scans the real repo root, not the tmp fixture with its single file)",
         "1 file(s)" not in r.stderr, r.stderr)
   ```
   not the `re.search(r"\b1 file\(s\)", ...)` predicate the dispatch says is on disk.
   `git diff -- .claude/skills/harness/bin/test-validate-feature-json.py` against both the working
   tree and against HEAD is **empty** — no local modification exists to this file at all.

3. **`git status --porcelain` (worktree)**:
   ```
    M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
   ?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q13-cycle-29-substring-gate.md
   ```
   No modification to the test file, one unrelated tracked change to `feature.json` (2 lines) and
   one untracked answers file — neither is the change this dispatch describes.

4. **Running the test file as-is reproduces the original bug it was supposed to fix**:
   `python3 .claude/skills/harness/bin/test-validate-feature-json.py` → exit `1`, with:
   ```
   FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real
   repo root, not the tmp fixture with its single file) scanning …/FEAT-43-code-risk-grading/.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
   …/feature.json: undeclared key 'briefing' at /. …

   1 FAILURE(S): ['case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep
   (scans the real repo root, not the tmp fixture with its single file)']
   ```
   This is exactly the substring-collision failure mode the fix (`\b1 file(s)\b`-anchored
   `re.search`, not `"1 file(s)" not in r.stderr`) exists to prevent: `"41 file(s)"` contains the
   literal substring `"1 file(s)"`, so the un-fixed predicate trips on it.

## Predicate proof (fresh, direct — step 1 of the acceptance list, run for the record even though
   the code it targets is not present)

```
$ python3 -c "
import re
def predicate(stderr):
    return re.search(r'\b1 file\(s\)', stderr) is None

s41 = 'some output 41 file(s) changed'
s1 = 'some output 1 file(s) changed'
print('41 file(s) case -> predicate result (should be True, does NOT trip):', predicate(s41))
print('1 file(s) case -> predicate result (should be False, DOES trip):', predicate(s1))
"
41 file(s) case -> predicate result (should be True, does NOT trip): True
1 file(s) case -> predicate result (should be False, DOES trip): False
```
This confirms the *predicate itself*, written from the dispatch's spec, behaves correctly in
isolation — as it did when this was proven in an earlier segment of cycle 29. It does **not**
confirm the predicate is on disk in the target file, because it is not.

## Checks not run

Per the assignment: "If any check fails, do NOT fix it silently — return FAIL with the exact output
and stop." Step 2 (the target test file) already failed against the actual on-disk state, and the
underlying premise (HEAD, diff --stat, applied fix) is contradicted by direct evidence. Running the
remaining acceptance steps (unit-test gate, code-grade, further status checks) against a worktree
that does not match the dispatch's described state would produce results attributable to the wrong
commit/fix state. I stopped here rather than continue accumulating evidence against a false premise,
and rather than re-apply the fix myself — the assignment is explicit that editing the source file is
out of scope for this dispatch ("do NOT edit that file again").

## Note

This run was halted mid-verification by an operator stop earlier in cycle 29 and has now been
resumed under operator authorization, per the assignment framing. On resume, the worktree state does
not match what the framing describes as already-applied. This is reported as found, not smoothed
over.
