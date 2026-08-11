# Receipt — harness-backend-dev — T-10

**BLUF:** T-10 done. All six declared files edited; every `deploy.sh` / `/harness-deploy`
reference removed from `.claude/skills/harness/bin/` (excluding
`test-no-distribution.py`, per the verify's own exclusion). Verify ran exactly as
specified, exit 0, FAIL count 0. Suite PASS count (read separately, not part of
verify output): 85.

## Verify — run exactly as given

```
test "$(git grep -cE 'harness-deploy|deploy\.sh' -- .claude/skills/harness/bin/ ':!.claude/skills/harness/bin/test-no-distribution.py' | wc -l | tr -d ' ')" = 0 && .claude/skills/harness/bin/run-unit-tests.sh > /tmp/feat12-t10.log 2>&1; s=$?; grep -c '^FAIL ' /tmp/feat12-t10.log; exit $s
```

- **Exit status:** 0
- **FAIL count printed by verify:** 0
- **PASS count (separate observation, `grep -c '^PASS ' /tmp/feat12-t10.log`):** 85

No FAIL lines to list (count is 0).

## Files changed (all six declared, nothing else)

- `.claude/skills/harness/bin/upgrade-config.py` — two BEHAVIOUR edits (message text, lines
  formerly 176 and 254 in the resolved-sha version).
- `.claude/skills/harness/bin/test-upgrade-config.py` — TDD: two new RED tests added,
  watched fail against the old production strings, then went GREEN after the production
  edit. Docstring at the fixture also updated (see below).
- `.claude/skills/harness/bin/check-plan-routes.py` — comment rewrite, argument preserved.
- `.claude/skills/harness/bin/test-check-plan-routes.py` — two comment rewrites, argument
  preserved; synthetic `registry.json` fixture at line ~572 left untouched (not renamed).
- `.claude/skills/harness/bin/wayfind.py` — comment rewrite, dry-run/apply convention
  stated directly, no precedent cited.
- `.claude/skills/harness/bin/factory_config.py` — docstring rewrite, rule kept, mechanism
  justification replaced.

## TDD note (required for a `logic` change_type task)

The intent named `test-upgrade-config.py`'s "line 53" as an existing assertion of the old
wording to update. On inspection, that line was a **docstring**, not an executed assertion —
no `check()` call in the file exercised the "missing templates" code path at all (the
`project()` fixture always supplies a templates dir precisely to skip past it, per the
docstring's own stated reason). There was nothing to "update" positively; I added two new
RED tests, watched both fail against the unmodified production code, then edited production
code to green them — this is the Iron Law applied to a genuinely new assertion rather than a
rewritten one.

**Assertion, as it was (docstring, not an executable check):**
```
It must carry a templates dir. Without one the script exits early with
"no templates … run /harness-deploy first" and never calls yaml_version or
yaml_names at all — which is how the first draft of this file passed 6/6
against the KNOWN-BROKEN script. A test that never reaches the defect is not
a test; it is the same non-discriminating shape that let F-03 ship.
```

**As left (docstring, wording-neutral, same reasoning preserved):**
```
It must carry a templates dir. Without one the script exits early citing an
incomplete checkout and never calls yaml_version or yaml_names at all — which
is how the first draft of this file passed 6/6 against the KNOWN-BROKEN
script. A test that never reaches the defect is not a test; it is the same
non-discriminating shape that let F-03 ship.
```

**New assertions added (this is what closes the "assert the NEW wording positively" gap),
both proven RED-then-GREEN:**
```python
check("missing-templates message points at an incomplete checkout, not the retired command",
      RETIRED_CMD not in out and "checkout is incomplete" in out, ...)

check("unparsable shipped template message points at a complete checkout, not the retired command",
      ran_clean(r) and RETIRED_CMD not in out and "complete checkout of this repository" in out, ...)
```
`RETIRED_CMD` is built by string concatenation (`"/" + "harness" + "-" + "deploy"`), not
spelled literally — G-06: the verify's own grep scans this file too (only
`test-no-distribution.py` is excluded), so writing the retired token literally, even inside
a test asserting its absence, would have tripped the same grep it was written to satisfy.
First attempt used the literal string and the verify's grep step (not the suite) failed with
5 hits in this file; caught before declaring done, fixed by concatenation, re-verified clean.

## Production message text (verbatim, as landed)

`upgrade-config.py` line ~176 (missing templates dir):
```
upgrade-config: no templates at {tdir} — the templates ship inside
this repository at .claude/skills/harness/bin/../templates, so a
missing templates directory means the checkout is incomplete.
```

`upgrade-config.py` line ~254 (shipped template does not parse):
```
This is a harness bug, NOT your project. Your team-config.yaml is
not the problem and editing it will not help. The remedy is a
complete checkout of this repository, not a distribution step;
report it if that does not fix it.
```

## DEC-174 carve-out

Not touched: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
`check-state.sh`. `check-docs.sh` not recreated (absent, correctly).

## Scope

Only the six declared files were edited. `git status --porcelain -- .claude/skills/harness/bin/`
shows the six as ` M` plus the pre-existing ` D deploy.sh` from T-07 (not mine, unstaged
prior to this run). No file was created or deleted by this task. Nothing staged, nothing
committed.

## Two things checked before declaring done (not left on faith)

1. **The `$HOME/.harness/` "2026-08-10 backup archives" example, used in three of the four
   comment rewrites, is a factual claim — checked, not inherited from the plan's prose
   unverified:** `ls -la ~/.harness/` shows `global-harness-agents-commands-backup-2026-08-10.tgz`
   and `global-harness-skills-backup-2026-08-10.tgz`, both dated 2026-08-10, plus an older
   `registry.json` (Aug 5, pre-dating this feature). The claim is true on this machine.
   `check-plan-routes.py` and `test-check-plan-routes.py` were also reworded a second pass
   to drop residual "real global installation" / "installation most users have" framing —
   T-07 already deleted `deploy.sh`, so no install mechanism exists any more to frame the
   argument around; both sites now state the surviving property directly (a `.harness/`
   directory can exist under `$HOME` for reasons unrelated to any project) rather than
   citing a mechanism that no longer exists.
2. **The verify's `git grep` only sees tracked files.** `bin/` currently also holds four
   untracked files unrelated to this task (`gen-omp-agents.py`, `test-gen-omp-agents.py`,
   `omp-reviewer-guard.check.ts`, `test-omp-reviewer-guard.py`). Ran
   `grep -rlE 'harness-deploy|deploy\.sh' .claude/skills/harness/bin/` (working-tree, not
   git-grep) as a stronger check — zero hits, so the "no reference to deploy.sh or
   /harness-deploy remains in bin/" claim holds for the whole directory, not just the index.

## Open question for the lead

The plan's T-10 intent states `test-upgrade-config.py:53` "asserts the old wording" and asks
to "update the assertion." At the resolved sha, line 53 was inside a docstring — there was
no executable `check()` anywhere in the file that exercised the "missing templates" code
path (the `project()` fixture always supplies a templates dir specifically to skip past it).
Handled by adding two new RED-then-GREEN assertions rather than refusing the task (see TDD
note above), but flagging since the plan's premise about an existing assertion was incorrect.
