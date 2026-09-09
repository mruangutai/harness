# Receipt — harness-dev-ops — T-18

Task: T-18 — Remove the dead `cli_min_version` key from this project's live `.harness/harness.json`.

Cross-checked against `plan.yaml` T-18 (lines 2006–2041): intent and verify text match the
dispatch verbatim. No divergence found.

## 1. Pre-edit verify (expect RED)

```
python3 -c "import json,sys;d=json.load(open('.harness/harness.json'));sys.exit(1 if 'cli_min_version' in d else 0)" &&
! grep -q cli_min_version .harness/harness.json &&
test "$(bash .claude/skills/harness/bin/check-state.sh | grep -c 'INV-')" -gt 0
```

Result: exit code 1 (RED, as expected — the `json.load` clause failed because the key was
present). No stdout printed before the short-circuit.

## 2. Edit

Removed line 3 of `.harness/harness.json` — `"cli_min_version": "2.1.217",` — via the edit
tool's `CUT 3.=3`. Nothing else touched.

## 3. Post-edit verify (expect GREEN)

Same command, run again:

```
=== POST-EDIT VERIFY (expect GREEN) ===
EXIT CODE: 0
```

GREEN. All three clauses passed: `json.load` confirmed the key absent from the parsed
mapping, the grep found no literal `cli_min_version` string anywhere in the file, and
`check-state.sh` ran to completion and emitted at least one `INV-` line (no team-config
parse complaint observed — T-19 was not touching `.harness/team-config.yaml` at the moment
this ran).

## 4. Diff — `git diff -- .harness/harness.json`

```diff
diff --git a/.harness/harness.json b/.harness/harness.json
index 36e32758..1706f1b5 100644
--- a/.harness/harness.json
+++ b/.harness/harness.json
@@ -1,6 +1,5 @@
 {
   "schema_version": 2,
-  "cli_min_version": "2.1.217",
   "_panel_era_start_note": "The date the adversarial plan panel (FEAT-45) became available in THIS project. INV-32 does not grade a plan signed before it, because a plan signed before the panel existed cannot carry a record of one. null means this project has no pre-panel era, so every approved plan is graded — the right value for a project onboarded after FEAT-45. Each repository's harness.json is its own, read from that repository's own default branch, so this MUST be per-project: a hardcoded date would export one repository's history as another's gate (BUG-1071 panel finding F2).",
   "panel_era_start": "2026-08-31",
   "_handoff_done_when_baseline_note": "This is the FROZEN list of handoff notes that existed at THIS FEATURE'S BASE COMMIT, ...
```

Exactly one line removed from one file. `schema_version` unchanged, no reflow, no reorder.

## 5. Status — `git status --porcelain`

```
 M .harness/harness.json
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-t18-eng.md
```

Only the production file and this receipt. No `.harness/team-config.yaml`, no `templates/`
paths — T-19's concurrent work was untouched.

No commit made.

## Result

T-18 complete. VERDICT PASS, task_verify pass.
