# Observations - harness-orchestrator

- 2026-09-07 (BUG-240): the panel's HIGH rested on `os.path.realpath` not canonicalizing component
  casing. I re-measured the premise myself in one python -c before spending a cycle (P-06) —
  realpath equality False, `os.path.samefile` True on the same directory. Cost ~5 seconds and would
  have saved a whole cycle had the finding been wrong.
- 2026-09-07 (BUG-240): the fix-cycle lead digest asserted "observed RED before the edit and GREEN
  after" but carried neither output, despite the dispatch demanding both verbatim. I proved it
  independently in a /tmp copy by reverting ONLY the identity block: exactly 1 of 39 failed, and it
  was the new case. Generalises: a digest that asserts the discriminating evidence without carrying
  it is indistinguishable from one that invented it — the acceptance criterion has to be checked,
  not merely written.
- 2026-09-07 (BUG-240): entering `review` turned two silent conditions into hard violations at once
  — INV-26 (no mirrored issues; `gh-sync.py open` had never run for this feature) and the missing
  handoff notes. Neither was visible at `building`. Moving the station is itself a measurement.
- 2026-09-07 (BUG-240): the bash write guard resolves only LITERAL ABSOLUTE paths. `mv`/`cp`/`rm`
  with a shell variable or a relative path is refused as out-of-domain even for a path squarely
  inside my own domain, and a heredoc is refused as a redirect. Cost three refused calls before I
  switched to a Write-tool helper script plus absolute paths.
- 2026-09-07 (BUG-240): a host-killed lead run's directory slug gets REUSED by the next run of the
  same squad. The F-PANEL-01 fix wrote its digest into the killed build run's dir, whose state.yaml
  still read `team: build, T-02: pending`. Two runs, one directory, and only the `ls` of runs/
  showed it. Check the digest's own headline against the state.yaml's `team:` before crediting.
- 2026-09-07 (BUG-240): STATE.md's 120-line budget bit three times in a row. The section that kept
  overflowing was per-run findings, which belong in the run's digest — the fix was to replace the
  findings text with the digest path and keep only disposition and reason.
- 2026-09-07 (BUG-240): `notes/handoff-<phase>.md` from a worktree is not merely awkward, it is
  impossible for a feature not yet on the default branch. check-domain calls handoff_done_when.py
  with the PROJECT root, so `_feature_dir()` rebuilds the feature dir under the MAIN checkout and
  every Authority pointer misses. A `finding:<worktree-relative-path>#F-NN` pointer would satisfy
  the gate; I refused it because it hard-codes a path that dies with the worktree.
- 2026-09-07 (BUG-240): one segment per dispatch held. Three lead dispatches completed at 11m54s,
  17m27s and 5m13s where the old multi-segment pattern was killed at ~14 min twice.
