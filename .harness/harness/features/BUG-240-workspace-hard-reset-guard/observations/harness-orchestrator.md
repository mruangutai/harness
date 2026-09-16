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
- 2026-09-07: a panel re-run over a one-commit fix stayed WIDE on purpose and it paid. All four
  reviewers got the full two-file diff, not the delta; code-reviewer then found F-C1-01 in the
  OSError fallback the fix INTRODUCED, which a delta-scoped re-run framed as "did F-PANEL-01 get
  fixed" could not have surfaced. Narrow means the fix scope, never the reading scope.
- 2026-09-07: the lead re-rated a reviewer's med to low on an unreproduced ARGUMENT (denial hits
  both spellings -> isdir False -> clone arm -> git clone refuses at exit 2). Plausible and I let
  it stand as non-gating, but I recorded IN STATE.md that it is an argument and that no reviewer
  reproduced it. A re-rating whose basis is not recorded is indistinguishable later from one that
  was measured.
- 2026-09-07: STATE.md's shape gate is 120 lines and it fired at 133 on a phase-closing rewrite.
  The over-run was entirely archival: per-finding narrative that already lives in the run digests.
  Write the ## Current replacement as pointers plus the delta, and the budget is never close.
- 2026-09-07: before dispatching a panel at an inherited pin, `git diff --name-only <pin>..HEAD`
  settles in one call whether later bookkeeping commits invalidate it. Here both later commits were
  feature-dir only, so the pin held and no re-pin was needed — cheaper than reasoning about it.
- 2026-09-07: I re-ran the blocking gate myself after the qa step reported it green. Same numbers
  (exit 0, 0 FAIL, 39 ok, 0 skip). Cost one call; the alternative was carrying the only blocking
  gate in the project on a digest field.
