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
- 2026-08-21: I authored a `verify:` for T-15 asserting `"DEC-129" not in team-config.yaml` to prove
  three miscited comments were fixed. `grep -n DEC-129 .harness/team-config.yaml` at `62f861c` shows
  FOUR hits: `:89`, `:90`, `:91` (the miscitations) and `:108`, which cites DEC-129 CORRECTLY for the
  per-feature `DESIGN.md` layout. A file-global absence assertion for a token that has a legitimate
  use is a verify that fails on correct code. Scope the assertion to the lines carrying the defect
  (here: lines containing `except` and an approval fragment), and assert the REPLACEMENT is present
  per line, not just the old token absent file-wide.
- 2026-08-21: A dispatch cited DEC-119 as check-domain.sh's fail-open-loudly precedent. `awk` over
  `DECISIONS.md:2356-2408` for `fail.open|loud` returned zero lines; the real precedent is DEC-127
  `@2805`, body `:2839`, plus the code's own comments at `check-domain.sh:798` and `:811`. A cited
  decision NUMBER is as rottable as a line anchor — grep the entry's body for the claim, not just the
  index row for the surface.


- 2026-08-21: a text-anchored gate rule must be tested against the payload shapes the ATTACK can
  choose, not the shapes the FILE contains. The ruling handed me "deny an Edit payload containing a
  two-space `status:` key", justified by a corpus measurement that was entirely correct — 23/23
  plan.yaml carry exactly one such line and it is always the approval block's. The corpus fact was
  true and the rule still failed: `Edit(old_string="status: pending", replace_all=true)` and
  `old_string="status: pending\n  approved_by:"` both flip the signature and neither payload contains
  a two-space line start at all. The discriminator was measured on the FILE; the payload is written by
  the attacker and need not resemble the file. Substituting "does old_string occur inside the target
  fragment's on-disk byte range" closed all three shapes with less logic and no indentation
  dependency. Build the truth table over payloads before accepting an anchor.
- 2026-08-21: `check-plan-routes.py` budgets `verify` at 50 machine-field lines per task
  (`:281`, `BUDGETED_FIELDS` at `:286`) and `intent` is NOT budgeted. Adding a third copy-paste red
  proof to T-03's verify pushed it to 58 and made the plan exit 1. Three mutation proofs differing
  only in a literal name collapse to a `for lit in A B C` loop: 44 verify lines to 18, same
  assertions. A red-proof-per-literal pattern is the shape that hits this budget first.
- 2026-08-22: judged whether an edit to a SIGNED plan's `verify:` needs a new signature, and the
  discriminator that held was WHERE THE ANSWER COMES FROM, not diff size. T-15's clause read
  `endswith(" plan.yaml approval:")` (leading space) against a grant whose preceding character is a
  slash, so it was unsatisfiable by construction; the task's own `intent:` mandated the grant string
  verbatim and the two sibling clauses fixed the grammar, so the signed text alone forced the one-char
  fix -> covered, no signature. Contrast the same feature's #551 occurrence count: the corrected
  number existed nowhere in the plan and had to be measured externally -> new content, operator.
  Rule: forced-by-the-artifact = covered; requires-choosing-among-readings = needs the signature.
- 2026-08-22: an assert that aborts a python heredoc HIDES every later clause, so "it fails for this
  reason" is only half the check. Run a corrected copy in scratchpad to reach the tail before
  declaring a single cause — the claim "and no other reason" is otherwise unmeasured.
