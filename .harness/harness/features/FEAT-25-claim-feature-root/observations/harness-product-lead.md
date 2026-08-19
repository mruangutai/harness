# Observations — harness-product-lead — FEAT-25

- 2026-08-19: run `2026-08-19-5-goalcheck-product`. Four shape checks to apply to pm's goal-check
  return before I accept it. Recorded here because I have no SendMessage and cannot inject them
  mid-flight; if my context resets, these are the send-back criteria.

  1. **SC-04 and SC-06 are structurally identical and must be graded by one stated rule.** Both are
     factually true at `8d7b273`, both have a partial standing assertion, and both have a clause
     verified only ad-hoc. SC-04: tests assert `absent_root in err` and `"no matching plan task"
     not in err`; the clause "stating that no plan could be read there" is asserted by no test
     (panel R-3, grep-measured). SC-06: case 22 asserts only the `features: CLEAN — evidence
     migrated` summary line; the "reads `factory_claim.py` … reports it `migrated`" clause was
     verified by qa's ad-hoc `layout_migration.scan(REPO_ROOT)` introspection (`qa-c1.md:121-124`),
     not by a standing assertion — that is F-2. If pm returns one met and the other unmet without a
     stated reading of `verify: automated`, send it back.
     Discriminator pm should engage: **SC-02 builds the pinning requirement into its own text**
     ("proven by running it once against the unmodified line"); SC-04 and SC-06 do not. The BRIEF
     author knew how to demand pinning when they wanted it. That asymmetry is textual evidence that
     SC-04/SC-06 grade program behaviour and that unpinned text is a durability backlog row.
     The panel's "does not gate" answers a SEVERITY question, not a met/unmet one — inheriting it
     is not reasoning.

  2. **SC-07's first conjunct ("each suite passes") is exposed to F-1 and my dispatch did not aim
     F-1 at SC-07.** F-1 proves `test-layout-migration.py` can print `FAIL - <name>` and exit 0
     when `detail` is empty (case 18's three assertions call `check(name, ok)` with two args). The
     count clause survives — a failed case emits `FAIL - `, not `ok   - `, so it is not counted —
     but "passes" does not survive if it was measured by exit code alone. qa's record reads "PASS
     incl. case 22 (41/41 `ok - ` lines)" (`qa-c1.md:50-51`); the denominator looks restated from
     the numerator, so **zero-FAIL was never asserted**. Require one grep of the layout suite's
     output for `FAIL`. Zero FAIL lines → SC-07's "passes" conjunct is sound and F-1 stays backlog.
     Any FAIL line → SC-07 unmet as written. "Pre-existing" assigns the remedy's owner; it says
     nothing about whether SC-07's evidence is sound.

  3. **No SC requires the clean-worktree measurement.** qa measured `test-factory-integration.py`
     PASS 106/106 in the DIRTY tree (`qa-c1.md:52-53`), so SC-03 is ownable by pm running that
     script directly — expect `mine`, not `inherited`. The `run-unit-tests.sh --kind integration`
     exit code is a GATE concern for the orchestrator's ship decision, not an SC. If pm marks an SC
     unmet on gate-honesty grounds that is a category error and I catch it. I forbade worktrees, so
     pm is not to be dinged for inheriting the clean-pin gate result.

  4. **Clause (b)'s `load_board` verdict must be scoped to ADDED LINES of the graded diff.**
     `load_board` is present in the repo — the panel found it in `check-state.sh`,
     `board-station.py`, `test-factory-config.py`, `test-gh-sync.py`, `test-gh-board.py`. A
     repo-wide grep returns five legitimate hits and reads as a clause-(b) failure. Check the shape
     of pm's evidence string, not only its verdict.

- 2026-08-19: my own derivation of SC-08 clause (a)'s allowed set, taken from `plan.yaml`
  `files:` at lines 111-114, 229-231, 383-386, independent of any member: six paths, all under
  `.claude/skills/harness/bin/` — `factory_claim.py`, `test-factory-claim.py`,
  `test-factory-integration.py`, `layout_migration.py`, `layout_fixtures.py`,
  `test-layout-migration.py`. qa's `git diff --name-only d1ffd7f...HEAD` (`qa-c1.md:31-33`) is
  exactly that set.

- 2026-08-19: UAT — I read `BRIEF.md` end to end myself. Its sections are Problem / Goal /
  Requirements / Success Criteria / Verification gaps / Constraints / Approval. **No UAT section
  exists and no criterion names a UAT.** This is my own verification, not a passthrough of pm's.

- 2026-08-19: `dispatch-guard.sh` blocked my first Agent call because I passed `model: opus`. The
  guard is right (DEC-152/155) and the re-dispatch without it succeeded. Cost: one blocked call.
  Do not pass `model:` — not even to match a member's own pin.
