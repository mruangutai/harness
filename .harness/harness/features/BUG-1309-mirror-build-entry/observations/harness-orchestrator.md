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
- 2026-09-08 (BUG-1309 c15): a fix that patches the NAMED instances of a parser class passed a 27-case bed and my own 23-check hook probe, while the class defect survived in three unnamed forms (-F, --cleanup, --attr-source). What found them was asking the REAL dependency first — for each candidate token sequence, does real git actually perform the merge? — instead of only asking what the gate decides. That same question falsified one of the two reported blockers: pm's --exec-path form prints the exec path and exits, so there was no merge to gate.
- 2026-09-08 (BUG-1309 c15): I wrote a full review_sha by extending an abbreviated sha from memory and feature-json-merge.py accepted it without complaint — no tool validates that a pin resolves at write time. Caught only because I re-read it against git rev-parse HEAD immediately after. Resolve the full sha with rev-parse and compare, every time.
- 2026-09-08 (c16): the operator ruling that a fix be "comprehensive" turned into a PLAN gap, not a
  code gap: two of its four clauses (merge control ops ALLOW, code-grade 4) were absent from the
  signed plan, so handing the operator a packet alone would have had them implement unapproved
  behaviour. Routing the ruling through pm BEFORE writing the packet cost one product run and made
  the packet quotable from the plan.
- 2026-09-08 (c16): pm's own read found SC-04 read literally MANDATES the deny the ruling reverses
  (`git merge --abort` is a merge command) — an emergent-SC case I would have mis-routed as
  approved-but-unmet. Asking "does this trace to a criterion?" as an explicit acceptance line in the
  dispatch is what surfaced it.
- 2026-09-08 (c16): a 10-line probe importing `merge_ref` and printing its return for ten command
  forms verified every red-before-green claim in the packet in one call, including the three
  preserved bounds. Cheaper and more discriminating than re-running the integration bed, and it
  belongs in the packet-writing step rather than after it.
- 2026-09-08 (c16): `python3 -c` inline scripts against plan.yaml are refused by bash-write-guard —
  it reads `'intent'` inside the quoted script as a redirect target. Write the probe with the Write
  tool into /tmp and run the file (G-08 generalises: guard misparses quoted spans).
- 2026-09-08 (BUG-1309, SC-11): an operator-approved BRIEF amendment cannot pass through 'reset approval to pending'. `.harness/*/features/*/BRIEF.md ## Approval` is a main_session.writes fragment and check-domain.sh's approval_guard denies pm AND the orchestrator; sign-approval is refused at the tool. So the correct intermediate state after an approval-gated amendment is an append-only edit leaving the OLD signature byte-identical and visibly stale, plus an explicit re-signature instruction returned up. Verified: pm's amendment landed as one hunk (@@ -160,0 +161,12 @@) with the approval block untouched.
- 2026-09-08 (BUG-1309, c18): a goal-check re-derives its own clause table from the SC text, so a later grader can enumerate MORE clauses than an earlier one. c17 split SC-04 into ten clauses and closed three named gaps; c18 split it into eleven and the eleventh (the ambiguity deny's reason WORDING) had never been graded at all. Closing every named gap is therefore not the same as meeting the criterion, and a cycle authorised against a named gap list can still return the SC unmet.
- 2026-09-08 (BUG-1309, c18): two of three closed gaps closed CONDITIONALLY ON THE RUNTIME, not on the fixture — gap C's unreadable arm binds only because the process is non-root, and gap B's ordering case survives its mutant because glob.glob returns fixtures in creation order on APFS. Reproduced the glob order myself in a scratch tree before letting the finding travel. A test whose discrimination depends on filesystem enumeration order is a behaviour witness, not a defence.
- 2026-09-08: BUG-1309 c19. plan-merge.py has an `amend` verb (AMENDABLE_KEYS = tasks, decisions) that replaces ONE field of ONE item under compare-and-swap on its sha256 — the orchestrator role text still describes the tool as add-only, which is now wrong. Even so the right route for a post-approval copy change was `apply` with a NEW decision (D-19), not `amend` of the executed task intent: rewriting an approved spec to match code written after it erases that the operator changed their mind (rule 15).
- 2026-09-08: BUG-1309 c19. Before promising a copy change is cheap, grep the tracked tree for the OLD string first: it was pinned in three places at once — the gate source, the plan task intent (verbatim, as the spec), and two UAT steps — plus two test assertions keyed on tokens the new copy deletes (`recovery-required`, `absent`). The plan quotation is the one nobody looks for.
