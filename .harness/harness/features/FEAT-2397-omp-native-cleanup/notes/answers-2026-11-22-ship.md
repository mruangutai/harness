# Ship ruling — delegated authority — FEAT-2397 — 2026-11-22

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC12Ship`) over `notes/ship-review-r-20261122-6-validate-validator.md`.

1. **Ship and squash-merge after green CI.** c2 PASSed at `eda06a68` with must_fix empty. All three
   binding sign-off conditions are evidenced: the tripwire, the #9(iii) cut ruling, and the SC-10
   real-run receipt.
2. **#1248: close as completed by FEAT-2397.** The issue asked for a version floor or detection; the
   floor branch was delivered. omp ≥18.0.11 is pinned in DEC-201 and was observed 7/7 on omp
   19.1.0. Silence on pre-floor hosts was ruled by AdvisorC1Grill, and the manual probe is the named
   diagnostic.
3. **#612: close as completed.** The issue's question is answered by native `task.perCallModel:
   "off"` (DEC-155), with the escalation route agent-visible in `.omp/rules`. The config is pinned
   by `tests/integration/test-check-omp-port.py`.
4. **Distill: skip.** Every task was main-session-direct, so each lesson is Main procedure: seam
   order, the `-validator` run-id suffix, exact-command receipts, the base-clone control. This
   follows the FEAT-2337 and BUG-2420 precedent.
5. **Backlog: two rows.**
   - macOS clean-clone unit failures at origin/main: test-omp-hooks FEAT-2225 ×5,
     test-factory-config (21) `/var`→`/private/var` realpath, and the BUG-1290 lines;
   - gate-runtime headroom: 41 s observed against the 45 s per-script timeout.

   Don't file the hermetic `CLAUDE_PROJECT_DIR` sanitizers; the sign-off already disposed of them.
