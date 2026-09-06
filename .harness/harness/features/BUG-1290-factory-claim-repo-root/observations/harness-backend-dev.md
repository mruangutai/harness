# Observations - harness-backend-dev

- 2026-09-05: BUG-1290 T-01: edit tool with a relative path (tests/unit/test-factory-claim.py) landed on the main checkout instead of the worktree, silently — confirmed only by comparing git status --porcelain in both trees. Redid the edit with the full absolute worktree path; reverted the accidental main-checkout diff with git checkout since it was the sole pending change there (G-18).
- 2026-09-05: BUG-1290 T-01: switching run_main() from patching claim.FEATURES_ROOT to patching factory_config.features_root (per T-01 step 3) intentionally reddens ~19 pre-existing cases (M3/M6/M7, B1/B3/B4/B5/B5-bis/B5-ter, X) that depend on this file's own fixture features, because production factory_claim.py at eb9d044e still reads its own hardcoded FEATURES_ROOT constant, not the new seam. This is expected fallout of a pure test-first task, not a bug — T-03 restores all of them to green by making factory_claim.py consult factory_config.features_root per candidate, using the same fixture_features_root monkeypatch already installed here.
- 2026-09-05: T-03 (BUG-1290): the plan's cited deletion range for FEATURES_ROOT (`:46-50`) precisely
  excluded `_BIN_DIR`'s own declaration line even though `_BIN_DIR` and the `harness_boundary` import
  in `factory_claim.py` become otherwise-unused after the deletion — a deliberately scoped plan can
  leave dead module-level names behind rather than widening a task's file-list touch; followed the
  plan's literal line range instead of doing unscoped cleanup.
- 2026-09-05: T-03 c2 send-back said "remove `_BIN_DIR` and `harness_boundary`, both dead" scoped to
  factory_claim.py alone; grepping the file confirmed it, but grepping the test tree found
  `tests/unit/test-factory-claim.py:1235` reading `claim._BIN_DIR` live (check "BUG-1290 5d"). Deleting
  it as instructed broke that test (123/124, AttributeError). A send-back's stated grep scope (one
  file) is not proof of zero live references elsewhere — check the test tree too before deleting a
  module-level name a task calls dead.
- 2026-09-05: T-04 — on the hardlinked pair .claude/skills/harness/bin/layout_migration.py and .agents/.../layout_migration.py (same inode), two successive `edit` calls reported success (fresh read/grep right after showed the new content) but a later independent `bash` check (sed/md5sum/stat -f %m) showed the on-disk bytes and mtime unchanged from before either edit, and a subsequent `read` also showed the stale pre-edit content — yet a re-`edit` attempt was rejected as stale against the tool's own (unpersisted) prior tag. Worked around with a bash/python3 in-place string replace, confirmed via stat -f %i (hardlink intact) and the task verify passing. Could not file via xd://report_issue: check-domain blocks harness-backend-dev from that path in this worktree.
