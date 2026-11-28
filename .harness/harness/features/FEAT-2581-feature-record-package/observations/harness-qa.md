# Observations — harness-qa — FEAT-2581-feature-record-package

- 2026-11-27: Verify blocks that byte-compare stored `git diff` output go red as the object store grows: default abbrev went 8->9 hex at 65,536 objects (count-objects in-pack 65632), turning T-03 red with no code change. Control: GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.abbrev GIT_CONFIG_VALUE_0=8 restores green. Committed diff bytes need --full-index/--abbrev pinned.
- 2026-11-27: A multi-line verify block without set -e exits 0 under plain bash when an early python assertion fails and the last line passes (T-03); always run verify blocks with bash -e and report both.
