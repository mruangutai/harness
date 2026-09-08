# Observations - harness-orchestrator

- 2026-09-08: BUG-1309 c13. A panel escalation whose remedies all sit main-session-direct still needs the PLAN amended first: two of three remedies contradicted signed task text (T-05's "merge as its first non-flag argument" literally specified PANEL-2's defect), so dispatching the implementation before pm's amend would have shipped code against the plan. plan-merge.py `amend` leaves approval bytes byte-for-byte, so the amendment does NOT reset approval to pending and no plan-panel re-run is forced — but the signature then covers text signed on a different day, which is a separate operator act.
- 2026-09-08: BUG-1309 c13. pm returned "Q2: the R-3 remedy is gated by nothing" — an amendment that specified behaviour but named no test case. Authorising the fifth amendment cost one spawn and closed it; had I accepted the PASS, the fix would have shipped with zero automated evidence and the panel would have found it at c8. A lead's non-blocking-looking coverage question is worth one more spawn before the code is written, never after.
- 2026-09-08: BUG-1309 c13. My dispatch named tests/unit/test-gh-sync-build-entry.py as the host for a new case; pm refused it and re-derived the integration file, because T-04's verify greps the integration runner's "ok    <name>" format while the unit runner prints "PASS <name>". Before naming a test HOST in a dispatch, check which runner's output format the task's own verify block greps.
- 2026-09-08: BUG-1309 c13. Moving a feature station backwards (review to building) turns INV-33 red immediately (review_sha covers plan text that no longer exists) and adds an INV-26 parent row. Re-pinning at the amendment commit clears INV-33 and costs nothing when no validator run is pending; the INV-26 parent row belongs to whoever owns the phase by execution_mode, and a main-session-direct segment means the main session runs gh-sync.py status, not me.
- 2026-09-08: BUG-1309 c13. A harness-product-lead run returned a complete, well-formed VERDICT/DIGEST/artifact and the host reported it "failed (exit 1) — Subagent called yield with null data". Read the returned block before believing the status line; a correct return can arrive under a failure banner.
- 2026-09-08: BUG-1309 c13. bash-write-guard misparsed a heredoc carrying an ASCII arrow and refused the whole command as a redirect to a file named "building". Pass observation entries as a file path, never inline on the command line.
- 2026-09-08: BUG-1309 c14. A hand-written parser rewrite passed its own new tests, the whole
  integration file (24 cases) and four other suites, while silently ALLOWING `git merge --no-ff X` —
  the shape the rewrite's own tests never fixture. The new cases all put the flag BEFORE `merge`
  because that was the reported bug; nothing put one AFTER it. Reading the diff for what the fix
  STOPPED handling, not only for what it started handling, is what found it: the old code filtered
  every `-`-prefixed word out of the whole argv, so it survived shapes the new token walk drops.
- 2026-09-08: BUG-1309 c14. My first probe claimed four regressed shapes; the panel refuted two of
  them by running the same probe against the pre-change source, where `git merge -m 'msg' X` and
  `git -C /repo merge --no-ff X` were ALREADY net-allow. Pre-existing hole and introduced regression
  look identical when you only measure the new code. Measure the base in the same call.
- 2026-09-08: BUG-1309 c14. Dispatching the validator panel and the pm goal-check concurrently over
  one pinned SHA cost one round instead of two and produced two independent confirmations of the same
  defect from different lenses (security bypass table vs. enumerated operator command forms). Both
  read-only, disjoint notes paths, neither able to move the tip — the collision O-10 warns about
  could not arise.
- 2026-09-08: BUG-1309 c14. `harness-validator-lead` returned a complete VERDICT/DIGEST/artifact and
  the host reported `failed (exit 1)` — "Subagent called yield with null data". Second occurrence in
  this feature (harness-product-lead was the first). A correct return read as a failed run; treating
  the status as authoritative would have discarded the panel that found the gating defect.
- 2026-09-08: BUG-1309 c14. `inflight_registry.py feature-root --feature BUG-1309` returned the
  control-plane root while the feature directory lived only in the worktree — the registry held NO
  CLAIMS, so it fell back. Globbing both candidate roots settled it in one call, and the worktree path
  was what the shell-less leads needed as HARNESS-FEATURE-TREE-ROOT.
- 2026-09-08: BUG-1309 c14. An unmet SC whose remedy sits in DEC-174-reserved files opens no fix
  cycle: there is no lead to route it to, so cycles_used correctly stayed 13/14 while the feature
  became not-shippable. Counting it as rework would have exhausted the budget for work no squad could
  have done.
