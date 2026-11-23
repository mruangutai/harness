# Red-first — BUG-2399 T-01

## Subjects
- Base (red) subject: `git show 9eb07b4f3cd235c234a10edddbfe5542c1e85fba:.claude/skills/harness/bin/prune-run-evidence.py > /tmp/b2399/prune-run-evidence.py`
  sha256 `3ce3bb40d97f8cb7c3274826f6cc4f3db653f38eadca8de76a0411a5aef02af9`. It sits in a directory with copies of the worktree's sibling bin modules (artifact_accessors, harness_boundary, harness_yaml), so its sibling imports resolve. The worktree's own pruner was untouched at the time and byte-identical to it.
- Fixed (green) subject: `.claude/skills/harness/bin/prune-run-evidence.py` sha256 `4ccdd6bf77e6ab07a590d64f8c734c849730e90a0f8fade0eaee1c5a3413b08c` (uncommitted, worktree HEAD ebb0a8553aba48f64f13f9e3d436f97d51689879)
- Test file: `tests/unit/test-prune-run-evidence.py` sha256 `1f896bd059ac3b75450977374fb493d4b61530859741f90e1f8807ca2b3d08bc`. Both runs used this file.
- Fixtures are real `git init` repositories whose `.gitignore` holds `.harness/*/features/*/runs/**`, so the index assertions can only pass through `git add -f`. The env vars CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR and HARNESS_AGENT_TYPE were unset, and inherited GIT_* variables are stripped from fixture git calls.

## Red: base subject
```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
PRUNE_RUN_EVIDENCE_BIN=/tmp/b2399/prune-run-evidence.py python3 tests/unit/test-prune-run-evidence.py
```
exit 1, stderr empty (0 bytes). There was no import, setup or collection error: 27 checks PASS, including all 25 pre-existing ones, and the 9 failures are assertion FAILs:
- SC-01 `dry-run names every non-UI file of every recorded run it would stage, and nothing else`: no `would stage` lines
- SC-01 `prune force-stages every surviving non-UI file of every recorded run, kept or pruned, nested qa/ included, byte-identical`: rc=0, every expected path missing from the index
- SC-01 `a repeated prune exits 0 and leaves the same staged records`
- SC-01 `staging never follows a linked run or linked subdirectory and stages no external content`: staged=[]
- SC-02 `prune refuses with exit 2 naming every missing cycle_evidence path`: rc=0
- SC-02 `a refused prune changes no file and no index byte`: base pruned ui/
- SC-02 `dry-run refuses with exit 2 naming every missing cycle_evidence path`: rc=0
- SC-02 `a refused dry-run changes no file and no index byte`
- SC-02 `complete cycle evidence permits the prune and stages every digest`

stdout:
```
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
PASS - dry-run names no deletion target through a symlink
PASS - dry-run leaves every link destination's ui/ byte-identical
PASS - prune removes no ui/ through a symlink and still prunes the real run
PASS - prune names each symlink it skipped
PASS - a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes
FAIL - staging never follows a linked run or linked subdirectory and stages no external content
       []
FAIL - dry-run names every non-UI file of every recorded run it would stage, and nothing else
       would remove runs/briefing-reconciliation-validator/ui
would remove runs/build-c0-eng/ui
would remove runs/distill-validator/ui
would remove runs/fix-c3-eng/ui
would remove runs/fix-c5-eng/ui
would remove runs/validate-c1-validator/ui
would remove runs/validate-c4-validator/ui
would remove runs/validate-ship-validator/ui
kept 4 of 13 run(s): fix-c5-validator, simplify-eng, stray-run, validate-c2-validator

PASS - dry-run leaves every file and the git index byte-identical
FAIL - prune force-stages every surviving non-UI file of every recorded run, kept or pruned, nested qa/ included, byte-identical
       rc=0 missing=['briefing-reconciliation-validator/.run-identity.json', 'briefing-reconciliation-validator/digest.md', 'briefing-reconciliation-validator/notes/sentinel.txt', 'briefing-reconciliation-validator/state.yaml', 'build-c0-eng/.run-identity.json', 'build-c0-eng/digest.md', 'build-c0-eng/notes/sentinel.txt', 'build-c0-eng/qa/deep/manifest-integration.json', 'build-c0-eng/state.yaml', 'distill-validator/.run-identity.json', 'distill-validator/digest.md', 'distill-validator/notes/sentinel.t
PASS - prune stages no ui/ file and nothing of an unrecorded run
FAIL - a repeated prune exits 0 and leaves the same staged records
       kept 4 of 13 run(s): fix-c5-validator, simplify-eng, stray-run, validate-c2-validator

FAIL - prune refuses with exit 2 naming every missing cycle_evidence path
       rc=0 
FAIL - a refused prune changes no file and no index byte
       
FAIL - dry-run refuses with exit 2 naming every missing cycle_evidence path
       rc=0 
FAIL - a refused dry-run changes no file and no index byte
       
FAIL - complete cycle evidence permits the prune and stages every digest
       kept 1 of 3 run(s): validate-c3-validator

9 failure(s)
```

## Green: fixed subject
```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
python3 tests/unit/test-prune-run-evidence.py
```
exit 0, stderr empty (0 bytes), 36 PASS, 0 FAIL.

stdout:
```
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
PASS - dry-run names no deletion target through a symlink
PASS - dry-run leaves every link destination's ui/ byte-identical
PASS - prune removes no ui/ through a symlink and still prunes the real run
PASS - prune names each symlink it skipped
PASS - a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes
PASS - staging never follows a linked run or linked subdirectory and stages no external content
PASS - dry-run names every non-UI file of every recorded run it would stage, and nothing else
PASS - dry-run leaves every file and the git index byte-identical
PASS - prune force-stages every surviving non-UI file of every recorded run, kept or pruned, nested qa/ included, byte-identical
PASS - prune stages no ui/ file and nothing of an unrecorded run
PASS - a repeated prune exits 0 and leaves the same staged records
PASS - prune refuses with exit 2 naming every missing cycle_evidence path
PASS - a refused prune changes no file and no index byte
PASS - dry-run refuses with exit 2 naming every missing cycle_evidence path
PASS - a refused dry-run changes no file and no index byte
PASS - complete cycle evidence permits the prune and stages every digest
all checks passed
```
