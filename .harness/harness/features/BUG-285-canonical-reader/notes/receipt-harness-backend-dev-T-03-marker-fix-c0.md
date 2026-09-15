# T-03 marker-fix receipt — PASS

`read_marker` preserves its established absent-marker fallback while still raising `MarkerUnreadable` for every malformed or unreadable present marker.

## Fail-first and green

- Before the test harness seam was restored, the exact focused command failed on missing `artifact_accessors` import. The regression was then added and executed RED with only `absent marker is None` failing: the accessor raised `ArtifactAccessError` whose cause was `FileNotFoundError`, and `read_marker` converted it to `MarkerUnreadable`.
- After the minimal provenance check at the accessor boundary, the exact focused command passed:

```sh
python3 tests/unit/test-run-identity.py
```

Output: 29 `PASS` lines, including `absent marker is None`, `truncated marker is unreadable`, `array marker is unreadable`, and `invalid UTF-8 marker is unreadable`; exit 0.

## Signed T-03 verification

Executed verbatim, exit 0:

```sh
python3 tests/unit/test-factory-gh.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/integration/test-merge-settings.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-board-lifecycle.py
```

Evidence: all seven chained scripts executed and passed; reported counters include `test-factory-gh.py` 257/257, `test-sync-agent-adapters.py` 18/18, and final `test-board-lifecycle.py` `all checks passed`.

## Protected-path proof and exclusions

Before/after SHA-256 values are identical:

- `STATE.md`: `9c8d7ec8c35512d11d6b55faae7bf9f2197e1f08ac06c5a4110d39f9a8b19978`
- `feature.json`: `710d340af747069ef331ee7c3a9c21431275cd5a292b29710d5e07fc01df3323`
- `plan.yaml`: `ef1463384bb506866a3b015d649179fe1bfeb365a37789cb17cbe5a2219aab17`
- `tests/integration/test-bash-write-guard.py`: `2da47e7d76d739cab7a5729c98e8147bb8d05309d5212e1074cf3fe44c2e68bd`

Touched production/test files: `.claude/skills/harness/bin/run_identity.py`, `tests/unit/test-run-identity.py`. `artifact_accessors.py` and all concurrent T-06 paths were not edited. No raw parser, caller wrapper/helper, T-04, direct T-05–T-07, classification machinery, formatter, linter, build, broad suite, or commit was run.