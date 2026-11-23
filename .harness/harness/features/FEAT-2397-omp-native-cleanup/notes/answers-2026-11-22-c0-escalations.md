# Validate c0 escalations — delegated rulings — FEAT-2397 — 2026-11-22

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC10Escalations`). This answers the three blocking open questions of
`r-20261122-4-validate-validator` (ESCALATE; `runs/r-20261122-4-validate-validator/digest.md`).

## Q1(a) — `tests/unit/test-no-distribution.py` case6: recorded deviation

- **No revert.** T-02's rename of the CI exports to `HARNESS_PROJECT_DIR` is signed (grilling note,
  AdvisorC1Grill).
- **T-05's three bin comments** are reworded so they no longer spell the variable. The files are
  `check-plan-routes.py:718`, `check_state/ctx.py:295` and `check_state/worktrees.py:112`, all
  in-list.
- **case6 exempts `.github/workflows/` from its absence scan.** Workflows are callers that set the
  resolver's seam, the same rationale as the existing `test-*` exemption. The comment cites the T-02
  rename ruling. The presence half and every other scanned path stay.
- **The stale exemption-comment sentence is corrected.** It claims the variable is "assigned
  repo-wide in exactly one place".

## Q1(b) — `tests/unit/test-lead-stop-and-wake.py` floor: recorded deviation

- Drop the ≥1 once-only floor for DECISIONS.md. Zero occurrences is the true post-feature state,
  and the once-only claim is never re-authored.
- Keep the per-occurrence qualifier/STRUCK bound check, and don't assert strict zero.
- Add a positive control: `ONCE_RE` must match a fixed sample string, so a rotted detector still
  fails.

Both Q1 items are recorded deviations, not a plan amendment. They change no SC and no intent; the
test migrations are forced by signed behaviour changes.

## Q2 — Main-edge contract: wording deviation, DEC-204 untouched

- T-05's signed intent says "blocking task". That word is a drafting error that contradicts kept
  DEC-204 (DECISIONS.md:6561-6565): Main dispatches the orchestrator asynchronously.
- `.omp/commands/harness.md` therefore states one `task` call with `agent: harness-orchestrator`,
  running in the background per DEC-204. Main ends its turn and the result is injected.
- The `tasks[]`-per-flow guidance, the HARNESS-FEATURE first line and the no-per-call-model rule
  stay.

## Q3 — INV-26: a fresh receipt at the c1 pin

- **Cause.** `_inv26_accepted` (board.py:507-509) widens a done task's card only while the plan's
  station is `review`. The pin captured plan `building` while the board already read Review.
- **Correct seam order:** (1) task stations → done, (2) plan.yaml top-level status → review,
  committed, (3) gh-sync writes the board columns.
- **Gate timing.** INV-26 is a repository-state gate. It is satisfied by a fresh full check-state
  receipt at the c1 pin: exit 0, with positive discovery.

## c1 fix round: rework round 1 of 2

c0 was the initial validation. The consolidated batch covers:
1. **T-05 doctrine:**
   - the 23 affected DECISIONS-INDEX tails rewritten to current contracts, including the DEC-111
     strike and the durable successors;
   - SPEC:808-811;
   - DEC-214:7117-7119;
   - an appended correction to `t05-doctrine.md`;
   - the Q1(a) comments and the Q2 `harness.md` text.
2. **T-03:** decompose `tests/integration/test-check-domain.py::_feat2274_cases` and
   `tests/integration/test-layout-migration.py::_parity` to grade ≥3, with no assertion change.
3. **The Q1 test migrations.**
4. **Evidence.** Receipts record their actual execution ref and bind forward by blob identity:
   - T-02's actual-ref transient check;
   - an actual-base (522c94b2) to review changed-body grade report;
   - a fresh check-state receipt;
   - unit 67/67, exit 0.
