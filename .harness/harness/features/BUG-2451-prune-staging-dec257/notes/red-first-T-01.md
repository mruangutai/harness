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
