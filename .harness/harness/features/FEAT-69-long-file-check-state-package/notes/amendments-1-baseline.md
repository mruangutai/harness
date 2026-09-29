# FEAT-69 — amendment 1 (DEC-174 main-session-direct): the baseline SHA, two more anchored files, and the canonical-reader audit's true state

Recorded with `plan-merge.py record-amendments` during the build, before the pin. Three defects in the signed plan, each found by measurement:

1. **The baseline is `a726bad8`, not `e6f8493b`.** Every fact the grilling recorded (5,058 lines, 287 functions, the four below-bar functions including `inv_49`) was measured from the root checkout while it stood at a later commit; `e6f8493b` predates #1963, which added INV-49, and holds a 4,975-line check-state.py. The worktree was cut from `a726bad8`, and `--list` at `e6f8493b` lacks the INV-49 row, so a byte comparison against it can never be identical. Verified: `git show e6f8493b:…/check-state.py | wc -l` → 4975; `git show a726bad8:…/check-state.py | wc -l` → 5058; `code_grade.grade_source` at `a726bad8` → 287 functions, below-bar exactly `_quoted_scalar_closed` (3), `_unquoted_hash_digit` (2), `_inv41_invocation` (2), `inv_49` (3). SC-01's red-first and SC-02's identity are measured against `a726bad8`.
2. **`layout_migration.py` and `layout_fixtures.py` are in the touched set.** INV-27's coupled-reader table (`layout_migration.READER_TABLE`) names `check-state.py` as the file carrying the `os.path.join(H, "features"` join; the join moved wholesale into `check_state/ctx.py`, so the row moves with it — the file's own precedent (its factory_config row comment). Without it the split's full-table output carries an INV-27 CANNOT VERIFY line the baseline does not. Anchored to T-03 (suite and consumer migration).
3. **"The canonical reader audit must pass within T-02" cannot be met by this feature and is restated as parity.** At `a726bad8` `check-plan-routes.py --canonical-reader-audit` exits 2 with 69 `PLAN AMENDMENT REQUIRED` classifications (a FEAT-61 migration inventory whose `<module>::…` rows name sites the FEAT-62 decomposition removed; rows for plan-merge, factory_gh, handoff_done_when among them). T-02 re-keys the one row whose symbol moved (`station_of` → `check_state/ctx.py`), adds the package files to `scanned_files`, and holds the audit at parity otherwise; the exact delta is ledgered in `build-divergences.md`. The nine `<module>::…` grilling identities and `_handoff_exempt` name sites that exist in no file at baseline or pin — they are accounted for as already-missing, not re-keyed to a file that does not carry them.

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-03
    field: files
    was:
    - tests/integration/check_state_support.py
    - tests/integration/test-check-state*.py
    - .github/workflows/tests.yml
    - .github/CODEOWNERS
    - .omp/commands/harness.md
    now:
    - tests/integration/check_state_support.py
    - tests/integration/test-check-state*.py
    - .github/workflows/tests.yml
    - .github/CODEOWNERS
    - .omp/commands/harness.md
    - .claude/skills/harness/bin/layout_migration.py
    - .claude/skills/harness/bin/layout_fixtures.py
    reason: INV-27's coupled-reader row for the features-path join moves with the join into check_state/ctx.py (layout_migration's own precedent); its fixture row moves with it. Found by the first full-table diff against the baseline.
```

Not amendable by field (prose, in BRIEF.md and task intents): every `e6f8493b` reads `a726bad8`; T-02's "audit must pass" reads "audit at parity with the baseline, the re-keyed row and the package manifest ledgered". The signed plan is otherwise unchanged; the operator's rework ruling (2 rounds / 480 min) stands.
