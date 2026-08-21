# Observations — harness-pm — FEAT-32

- 2026-08-21: `bash-write-guard.sh` denies a `sed -i` whose target is a shell VARIABLE — it printed
  "targets $P, outside your domain", i.e. it resolved the literal `$P`. Never pass a write target
  through a variable; either inline the absolute path or use the Edit tool. The Edit tool worked on
  the same file immediately after.
- 2026-08-21: the same guard ALLOWED `python3 - <<PY` rewriting that identical `plan.yaml`, because
  the command carries no write pattern it recognises. That is #627 reproduced by accident while
  planning the feature that adds three more such CLIs. Recorded in the BRIEF as a stated bound, not
  designed around.
- 2026-08-21: `run-unit-tests.sh --kind integration` prints three lines containing the word `ERROR`
  inside a test's own NAME (gh-sync expected-output cases). A baseline written as "zero ERROR lines"
  is therefore false at HEAD. Write the baseline as "no line BEGINNING `FAIL`, exit 0" instead.
- 2026-08-21: `check-plan-routes.py <plan>` prints one line per task and a global summary; running
  it with no argument reports over EVERY live plan, so other features' DEVIATION lines appear.
  Always pass the plan path.
- 2026-08-21: FEAT-30's T-06 `verify:` is the reusable red-proof shape — `cp -R bin` to a tempdir,
  mutate one named literal in the copy with a heredoc python, require the suite to FAIL under
  `<TOOL>_BIN` pointing at the copy, then require the unmutated suite to PASS. It generalises to two
  mutants in one verify (T-03 here does UNION_MERGE and PRESERVE_BASE_BYTES) at the cost of two
  tempdir copies.
- 2026-08-21: inside a `verify: |` block the 6-space YAML indent is stripped by the loader, so a
  `<<'PY'` heredoc whose body and terminator sit at that indent is correct Python at column zero.
  I nearly "fixed" a working block on this false premise. Load the YAML and print the string before
  editing a verify for an indentation bug.
- 2026-08-21: a folded `>-` scalar tolerates a colon-space freely (it is block content), unlike a
  plain scalar. All eight `decisions[].because` values here carry them and `safe_load` is clean.
- 2026-08-21 (amendment round, S-01): a dispatch's own framing of a measurement was wrong once in
  seven rulings. R5(a) said T-05's three `not os.path.exists(path + ".lock")` assertions would pass
  VACUOUSLY; at c32f332 they go RED, because D-02 locks a sibling `.lock` file that is never removed.
  The vacuum only appears via the two workarounds the same ruling forbids. Conclusion unchanged,
  premise wrong — re-derive even the measurement a ruling hands you as settled.
- 2026-08-21: THREE line anchors cited through several planning rounds by three tiers had all drifted
  by c32f332: `bash-write-guard.sh` `:617/:628/:676` are `:618/:625/:634`, and `check-domain.sh`'s
  `SHAPE_PATTERNS` is `:727` not `:677`. Converted every one to a symbol reference. The pattern: the
  claim stays true while the pointer dies, so nothing ever fails.
- 2026-08-21: "record the impossibility" was the wrong frame. The right move was to ask WHICH HARM
  needs the impossible thing — the loss needed an unbounded PreToolUse refusal, the false report
  needed exactly one correction round, and neither needed the wait. A one-shot SubagentStop refusal
  is not a weak wait; it is the full strength of every digest contract in `validate-digest.py`.
- 2026-08-21: a plan-wide `verify:` fix that is self-locating beats one that hard-codes a path.
  `cd "$(git rev-parse --show-toplevel)"; export CLAUDE_PROJECT_DIR="$PWD"` at the head of all 13
  blocks is correct in the worktree AND on main; pinning the worktree path would have rotted at merge.
- 2026-08-21: `bash-write-guard.sh` denied a `cat >> observations/harness-pm.md` heredoc from inside
  the feature directory — it resolves the RELATIVE path against `CLAUDE_PROJECT_DIR`, not the shell's
  cwd, so a legitimate in-domain append reads as out-of-domain. Append to a `notes/` or
  `observations/` file with the Write tool and an absolute path.
