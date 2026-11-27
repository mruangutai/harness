# T-01 red-first receipt — BUG-2451 (main-session-direct, DEC-174)

Worktree HEAD 114658fb. Subject under RED: `git show 47d6c54de1d91459f84f61ca92e27a47ba553308:.claude/skills/harness/bin/prune-run-evidence.py`
(blob d9e3ced785f5e18ac4d1896aa63aeff686b2acbf, sha256 55df0581f38f88489e5ba876a617cd9f74bd245dfbd94972c3f3526e201a93ef),
written temporarily as the sibling `.claude/skills/harness/bin/prune-run-evidence-47d6c54d.py` so its sibling imports resolve, removed after each run.
HEAD's pruner was byte-identical to 47d6c54d's (`git diff --stat 47d6c54d HEAD` on it was empty).

Command (from the worktree root, with CLAUDE_PROJECT_DIR / HARNESS_PROJECT_DIR / HARNESS_AGENT_TYPE unset):

    PRUNE_RUN_EVIDENCE_BIN=$PWD/.claude/skills/harness/bin/prune-run-evidence-47d6c54d.py python3 tests/unit/test-prune-run-evidence.py

## RED 1 — tests written, no production file edited yet
Test sha256 1c8af9734be1426b9a21c3121059689d389412c8cb25a60923d36afe1eab8afc. Exit 1, `6 failure(s)`. All are assertion failures. The setup and imports ran: 46 other checks PASSed in the same run.

```
FAIL - dry-run prints no staging output
       would remove runs/briefing-reconciliation-validator/ui
would remove runs/build-c0-eng/ui
would remove runs/distill-validator/ui
--
FAIL - prune starts no subprocess and exits 0
       rc=1 log=subprocess.Popen ('git', ['git', '--literal-pathspecs', 'add', '-f', '--pathspec-from-file=-', '--pathspec-file-nul'], '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpky_gy943/repo/.harness/harness/features/FEAT-9-thing', None)
 Traceback (most recent call last):
  File "<string>", line 10, in <module>
--
FAIL - prune prints no staging output
       removed runs/briefing-reconciliation-validator/ui
removed runs/build-c0-eng/ui
removed runs/distill-validator/ui
--
FAIL - pruner invokes no git subprocess
       
PASS - prune refuses with exit 2 naming every missing cycle_evidence path
PASS - a refused prune changes no file and no index byte
--
FAIL - complete cycle evidence permits the prune, keeps every digest and leaves the index alone
       removed runs/validate-c1-validator/ui
removed runs/validate-c2-validator/ui
kept 1 of 3 run(s): validate-c3-validator
--
FAIL - five-file current claims and historical restoration
       ['force-stag', 'git add', '`runs/**` is ignored', 'would stage', 'staged runs/', 'subprocess', '_stage', 'force-stag', 'git add', '`runs/**` is ignored', 'DEC-238 ship bullet text', 'force-stag', 'git add', '`runs/**` is ignored', 'would stage', 'ship prune paragraph text']
6 failure(s)
6 failure(s)
```
`prune starts no subprocess` records the audit-hook log `subprocess.Popen ('git', ['git', '--literal-pathspecs', 'add', '-f', ...])`. The hook raises inside the subject, so the old pruner's `git add -f` is caught before it reaches the index.

## RED 2 — final test file, after the pruner_claims split for code-grade
Test sha256 7e044f01940b744921ceb0cee788b184f062b41139de86151d4e6d17bc760b08, same command and subject, exit 1, `5 failure(s)`:
```
FAIL - dry-run prints no staging output
FAIL - prune starts no subprocess and exits 0
FAIL - prune prints no staging output
FAIL - pruner invokes no git subprocess
FAIL - complete cycle evidence permits the prune, keeps every digest and leaves the index alone
5 failure(s)
```
The five-file check does not appear here because it reads the current docs, which were already fixed by then, not the subject.

## GREEN — fixed pruner (sha256 0237578f304edc37c0ad33b19768586f83960b08c42b35f07a9d78811efd35ed), same final test file
T-01 `verify:` run verbatim → exit 0, `all checks passed`, 0 FAIL lines. The grepped lines:
```
PASS - five-file current claims and historical restoration
PASS - pruner invokes no git subprocess
PASS - real temporary git repository index is byte-identical
```

## c1 fix — MF-1, MF-2, QA-F1..F3 (validate run 2026-11-26-02, pin b2c1f55e)

The tests were written first, with no production edit. The final test file's sha256 is
291b798eeb5427ff20d80ca60a85f581bac55d957f6c52f2b07c569e4405931d, and every run below used that file.

### MF-1 RED, against the pinned pruner
- Subject: `git show b2c1f55e:.claude/skills/harness/bin/prune-run-evidence.py` (blob 81c95494f9c7464ff3b6762b746a2a874f5d5160, sha256 0237578f304edc37c0ad33b19768586f83960b08c42b35f07a9d78811efd35ed). It was written temporarily as the sibling `bin/prune-run-evidence-b2c1f55e.py` and removed afterwards.
- Command: `PRUNE_RUN_EVIDENCE_BIN=$PWD/.claude/skills/harness/bin/prune-run-evidence-b2c1f55e.py python3 tests/unit/test-prune-run-evidence.py`
- Result: exit 1, `4 failure(s)` and 48 PASS. All four failures are assertions in the new `unreadable_ui_cases`. Its fixture is a tracked repository with chmod 000 on `runs/fix-c3-eng/ui/evidence`, `runs/fix-c5-eng/ui` and `runs/validate-c2-validator/ui/evidence`, beside readable prunable lanes.
```
FAIL - dry-run fails with exit 1 naming every unreadable directory under a recorded run's ui/
       rc=0 
FAIL - prune fails with exit 1 naming every unreadable directory under a recorded run's ui/
       rc=1 Traceback (most recent call last):
FAIL - a prune over unreadable ui/ directories removes no readable lane and changes no index byte
       
FAIL - refused prunes over unreadable ui/ directories leave every feature file byte-identical
       
4 failure(s)
```
- What the failures show:
  - The pinned dry-run exits 0 and names nothing.
  - The pinned prune deletes readable lanes, then crashes inside `rmtree` with a traceback (exit 1, no names).

### Fix
- `_unreadable_dirs` no longer removes `ui` from the walk. Its body is now `for _walked in os.walk(run_dir, onerror=note): pass`.
- `os.walk` keeps `followlinks=False`, so a linked ui/ or a linked subdirectory is still never descended, and a linked run directory is still skipped before the walk.
- The module docstring and the function docstring now say "its ui/ included".
- Fixed pruner sha256: a6bc1fe5972c768ff847e9a740ebfb71dcba291263fbb8a0d71e9eb98399ad7a.

### GREEN
T-01 `verify:` run verbatim exits 0, with 55 PASS, 0 FAIL and `all checks passed`. The three grepped lines matched, and the index diff is empty.

### QA-F1 and QA-F2: against 47d6c54d (sha256 55df0581…a93ef, same command with the `-47d6c54d.py` sibling)
- Result: exit 1, `12 failure(s)` and 40 PASS.
- **F1:** `no_git_cases` now has an unhooked leg per mode, each in a fresh tracked repository. The new `prune leaves the real git index byte-identical` leg FAILs with `rc=0 index 9148 -> 8663 bytes`, a natural RED from the real `git add -f`.
  - The dry-run leg stays PASS. 47d6c54d's dry-run never wrote the index, so it has no natural RED there.
- **F2:** `real temporary git repository index is byte-identical` now always prints. It printed `FAIL` here, and PASS requires every hooked behavioural leg and every unhooked index leg to pass.
- **Subject switch (MF-2):** in the same run, the five-file check FAILs on the subject's own text, e.g. `prune-run-evidence-47d6c54d.py: force-stag`, `…: git add`, `` …: `runs/**` i… ``. `pruner_claims` and the whole-file scan now read TOOL.
- Full list of the 12 failures:
```
FAIL - dry-run prints no staging output
FAIL - prune starts no subprocess and exits 0
FAIL - prune prints no staging output
FAIL - prune leaves the real git index byte-identical
FAIL - pruner invokes no git subprocess
FAIL - real temporary git repository index is byte-identical
FAIL - complete cycle evidence permits the prune, keeps every digest and leaves the index alone
FAIL - dry-run fails with exit 1 naming every unreadable directory under a recorded run's ui/
FAIL - prune fails with exit 1 naming every unreadable directory under a recorded run's ui/
FAIL - a prune over unreadable ui/ directories removes no readable lane and changes no index byte
FAIL - refused prunes over unreadable ui/ directories leave every feature file byte-identical
FAIL - five-file current claims and historical restoration
```
- **F3:** `dry_run_cases` now also asserts `dry-run leaves every file in the feature byte-identical, feature.json included` with `tree_bytes(feat)`. The hooked dry-run leg and the unhooked dry-run leg also compare the whole feature tree.

### MF-2 guard probes
Each probe is a scratch copy of the worktree (rsync without .git, node_modules or features/) under /tmp/bug2451-c1-probes, with exactly one mutation, then `python3 tests/unit/test-prune-run-evidence.py` run in that copy:

| probe | mutation | rc | five-file detail |
|---|---|---|---|
| control | none | 0 | PASS (all checks passed) |
| ship-extra-space | ship paragraph `placeholder. Before` → `placeholder.  Before` | 1 | FAIL ['ship prune paragraph text'] |
| bullet-extra-space | DEC-238 bullet `value. Before` → `value.  Before` | 1 | FAIL ['DEC-238 ship bullet text'] |
| ship-wrap-change | ship paragraph rewrapped (`it⏎  refuses with` → `it refuses⏎  with`) | 1 | FAIL ['ship prune paragraph text'] |
| ship-intro-claim | harness-ship.md step intro, outside the paragraph, gains ``; `runs/**` is ignored`` | 1 | FAIL ['harness-ship.md: `runs/**` is ignored'] |
| test-comment-claim | test comment above NO_SUBPROCESS gains `` `runs/**` is ignored`` | 1 | FAIL ['tests/unit/test-prune-run-evidence.py: `runs/**` is ignored'] |
| decisions-other-claim | DEC-238 "Abandon prunes." bullet, outside the ship bullet, gains `` `runs/**` is ignored.`` | 1 | FAIL ['DECISIONS.md: `runs/**` is ignored'] |
| index-row-claim | DEC-238 index row gains `force-stages records` | 1 | FAIL ['DECISIONS-INDEX.md: force-stag'] |
| pruner-docstring-claim | pruner docstring gains ``; `runs/**` is ignored`` | 1 | FAIL ['.claude/skills/harness/bin/prune-run-evidence.py: `runs/**` is ignored'] |

- The control run (no mutation) also shows that DEC-257's own text is excluded: its `force-staging` and `git add -f` wording sits in the unchanged DEC-257 section and does not trip the scan.
- How the guard compares text now:
  - The restoration check is literal. The current section must equal the 5e51124e text with the one sentence inserted after its anchor, exactly as wrapped (`restored()`).
  - The insertion is pinned to `REFUSALS` by replacing only `"\n  "` with a space.
  - The ship paragraph section ends at a blank line or EOF.
- The forbidden-claim scan reads whole files with no git:
  - TOOL, this test file without its `FORBIDDEN` literal, DECISIONS.md without the DEC-257 section, DECISIONS-INDEX.md without the DEC-257 row, and harness-ship.md.
  - Phrases are matched across line wraps.
