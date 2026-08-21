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
