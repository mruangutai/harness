# Receipt — harness-dev-ops — rehome-eng (T-03 comment re-home)

## BLUF
Re-homed the T-03 comment correction into its new location after main's six-way split of
`tests/integration/test-check-state.py`. The comment above `case_inv32_era_comes_from_project_config`
in `tests/integration/test-check-state-records.py` (lines 522-524) still carried the pre-merge false
clause — confirmed byte-for-byte against the lead's measured copy before editing. Applied the
corrected wording. Diff is comment-only (4 lines replacing 3, no code/assertion/fixture/docstring
touched). Scoped test file run: 29 cases, exit 0. Verify-clause grep matches exactly one line.

## BEFORE (verbatim, lines 522-524, read and confirmed identical to lead's copy)
```
# BUG-1071 F2 — the boundary is the PROJECT'S, read from harness.json, not a literal
# compiled into a file that /harness-init copies everywhere. These four pin that the value
# actually comes from config and that every unreadable state fails closed.
```

## AFTER (verbatim, lines 522-525)
```
# BUG-1071 F2 — the boundary is the PROJECT'S, read from that repository's own harness.json —
# which for a fleet member lives on its default branch — not a literal compiled into the
# checker. These four pin that the value actually comes from config and that every unreadable
# state fails closed.
```

Decision gate outcome: the comment DID still carry the false clause (unchanged from pre-merge base,
matching the lead's measurement exactly). Correction applied per step 3, verbatim as dispatched.

## Verification

### 1. grep for required literal (exactly one line)
```
$ env -u HARNESS_AGENT_TYPE grep -nF "read from that repository's own harness.json" tests/integration/test-check-state-records.py
522:# BUG-1071 F2 — the boundary is the PROJECT'S, read from that repository's own harness.json —
```

### 2. scoped python run (exit 0)
```
$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-state-records.py
ok - INV-32 plan panel fixtures, including inv32-red
ok - INV-32 unrated severities fail closed
ok - INV-32 pre-era plan is exempt with a note
ok - INV-32 era boundary is exact (08-30 exempt, 08-31 graded)
ok - INV-32 undated approval is a violation naming approval.date
ok - INV-32 era guard is load-bearing (real=0 mutant=1 violations)
ok - INV-32 era boundary comes from harness.json, not a literal
ok - INV-32 null panel_era_start exempts nothing
ok - INV-32 missing panel_era_start violates, naming the upgrade command
ok - INV-32 malformed panel_era_start exempts nothing
ok - BUG-440 INV-37 reconciles digest verdicts without mutation
ok - BUG-1305 INV-36 detects clobbers and stays silent on owned/legacy runs
ok - T-06 INV-37 fires at a done station with no task statuses
ok - T-06 INV-37 message discriminator names recover-terminal only
ok - T-06 INV-37 silent on build_entry opened
ok - T-06 INV-37 silent on build_entry recovered-terminal
ok - T-06 INV-37 silent when github.sync is false
ok - T-06 INV-37 silent on a feature with factory.issues
ok - T-06 INV-37 silent on an era-exempt feature
ok - T-06 recovery_command_for returns open for a non-era building plan
ok - T-06 recovery_command_for returns recover-terminal for each trigger alone
ok - case (inv33.a) a stale review_sha is reported
ok - case (inv33.b) a current review_sha is silent
ok - case (inv33.c) a terminal station is silent
ok - case (inv33.d) a pin with no plan file at that path is silent
ok - case (inv33.a) a stale review_sha is reported, naming the feature, the pinned sha and the last sha to touch the plan
ok - case (inv33.b) a current review_sha is silent even though a later commit touched the plan — a BYTE comparison, not a commit comparison
ok - case (inv33.c) a terminal station is silent — a shipped plan is a record, not a contract (operator Q6)
ok - case (inv33.d) a pin that resolves but holds no plan at that path is silent, at a NON-TERMINAL station
EXIT:0
```

### 3. git diff (comment-only)
```
diff --git a/tests/integration/test-check-state-records.py b/tests/integration/test-check-state-records.py
index 2c6c8cfd..b24c98ba 100755
--- a/tests/integration/test-check-state-records.py
+++ b/tests/integration/test-check-state-records.py
@@ -519,9 +519,10 @@ def case_inv32_era_guard_is_load_bearing():
         shutil.rmtree(iso_root, ignore_errors=True)


-# BUG-1071 F2 — the boundary is the PROJECT'S, read from harness.json, not a literal
-# compiled into a file that /harness-init copies everywhere. These four pin that the value
-# actually comes from config and that every unreadable state fails closed.
+# BUG-1071 F2 — the boundary is the PROJECT'S, read from that repository's own harness.json —
+# which for a fleet member lives on its default branch — not a literal compiled into the
+# checker. These four pin that the value actually comes from config and that every unreadable
+# state fails closed.
 def case_inv32_era_comes_from_project_config():
     """The SAME plan is exempt or graded depending only on the project's own
     `panel_era_start`. This is the case a hardcoded literal cannot pass: a plan signed
```
Confirmed: no assertion line, no fixture argument, no control-flow line, no docstring moved or
changed. Only the 3-line comment block was replaced by a 4-line comment block; the function
definition line (`def case_inv32_era_comes_from_project_config():`) is unchanged and unmoved.

### 4. git status --porcelain
```
 M tests/integration/test-check-state-records.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-rehome-eng.md
```
Only my one permitted production file and my own receipt. Nothing under `.harness/harness/docs/`,
`README.md`, or `tests/unit/` — those remain untouched, owned by the concurrent documentor.

## Notes
- Did not commit. Did not run the project-wide test suite, a formatter, or a linter.
- Did not re-run the other three `verify:` clauses (test-layout-migration.py, test-hooks-install.py,
  test-post-merge-sweep.py, or the two `!grep` clauses) — out of scope per dispatch; only the
  `test-check-state.py` grep clause's subject was at issue and is now satisfied by
  `test-check-state-records.py`.
