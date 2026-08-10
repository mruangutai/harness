# STATE

## Current

- feature: FEAT-10-software-factory
- mission: ship — phase still recorded `build`. Its exit predicate stays met (12/12 tasks DONE, qa
  gate PASS) and ship's entry is the operator's acceptance, which has not happened.
- status: awaiting_user — the criteria question is CLOSED; what remains is the commit, the cycle
  budget, and three named residuals. ZERO blocking gates.
- review_sha: f9488a2 — the whole diff is UNCOMMITTED against it; nothing staged by me.

- **ALL 20 CRITERIA ARE MET — 20 met / 0 partial / 0 not_met**, on the STRICT clause-level bar the
  operator ruled stands. The 20/20-vs-17/20 question is SETTLED and must not be re-opened.
  SC-13, SC-18 and SC-19 were closed by added assertions, then re-graded independently by pm at
  runs/goalcheck2-product/digest.md. pm verified each by MUTATION on a scratchpad copy, not by
  reading. Seventeen of the twenty are carried forward from earlier runs, not re-verified today.

- **A BLOCKING PRODUCTION DEFECT WAS FOUND BY THE OPERATOR'S LIVE RUN AND IS FIXED.**
  factory_gh.py:266 passed the board NUMBER to `gh project item-edit --project-id`, which takes the
  GraphQL node id. The factory could never move an item between stations — all three callers
  (decompose:363 ready, claim:330 building, land:99 review) were dead. Every test passed because the
  stub `gh` never READ that flag. Fixed at factory_gh.py:268-271 by resolving the id via
  `gh project view`, uncached by deliberate choice. Publish also now REFUSES a plan with no
  top-level `feature` key (factory_decompose.py:287-293, exit 2, zero remote calls) instead of
  writing a `feature:None` label and exiting 0.

- gates: qa PASS (blocking, green — run-unit-tests.sh exit 0, unit 10/10 files, integration 14/14
  files, 0 FAILs, re-measured by me AFTER the fix); docs PASS exit 0; review panel FAIL-but-ADVISORY
  (severity_max med, must_fix empty — DO NOT start a fix loop on it); security PASS info.
- budget: 10 of 10 cycles. TWO were added this run and my count is CONTESTABLE — see Open Questions.
  ZERO headroom remains for the ship phase.
- runs: 29 of 20, informational only (INV-22). Each of the four added resolved a named blocker.
- the briefing notes/ship-review-build-2026-08-09.md is STALE on five points now and was NOT
  refreshed — no briefing trigger fired. Close-out (ship-refresh, distillation) still deliberately
  skipped: both are feature-close and this feature is not closing.

## Open Questions

- BLOCKING · THE COMMIT — and it is FAR SIMPLER than the inherited note said. I re-derived all four
  traps at HEAD and THREE ARE STALE. The branch is already `feat/FEAT-10-software-factory` with two
  commits on it (2a3e91c the door change, b89c00a the OMP port), so no branch needs cutting. The two
  staged deletions are gone — 2a3e91c committed them, `git diff --cached` is EMPTY. The OMP stream is
  committed, not intermingled, and run-unit-tests.sh is clean. check-state.sh's diff is ONE hunk of
  52 additions opening "INV-24 (DEC-186)" — T-08's own work, not foreign dirt. WHAT IS ACTUALLY LEFT:
  a normal pathspec commit of 15 untracked factory modules under .claude/skills/harness/bin/, the
  INV-24 pair, .harness/harness.json, the two DECISIONS docs, and this feature dir. STILL TRUE AND
  STILL THE RISK: every factory module is UNTRACKED, so `git stash` would DROP them and
  `git checkout --` cannot restore them. Nothing is git-recoverable until it is committed.
- NON-BLOCKING · DEAD ASSERTION at test-factory-integration.py:691-692. `os.path.isdir` on the
  workspace payload path passes even under a factory_workspace.py that produces no checkout, because
  the fixture pre-creates that exact directory at :676. It costs nothing today — SC-19's clause rests
  on :704-708, which does redden — but it reads as coverage to the next reader. Drop it or move the
  makedirs whenever this file is next touched.
- NON-BLOCKING · SC-18's assertion has two named residuals, neither demoting the clause: a
  module-scope alias not containing "fleet" evades the source-text rule, and the enumeration covers
  factory_*.py rather than all of bin/. Also AsyncFunctionDef coverage is itself unprotected — the
  self-test fixture has no `async def`, so dropping it from the scope list stays green. Two fixture
  lines whenever this scan is next touched.
- NON-BLOCKING · publish now makes 3N board calls per N-task plan where it made 2N, because
  project_field_set sits in the decompose loop and the id lookup is uncached. Chosen deliberately for
  parity with the already-uncached _field_list call and to respect factory_gh.py:11's
  never-cache-at-import intent. Worth watching against a real board.
- NON-BLOCKING · SCOPED OUT, reported not fixed: publish accepts a feature dir at ANY path while
  claim hardcodes .harness/features/ (factory_claim.py:43), so a plan can be published that claim
  cannot resolve. Any answer is a contract between publish and claim, not a one-line fix.
- NON-BLOCKING BUT LIVE HARNESS DEFECT · SIX FILES STILL CARRY THE PRE-DEC-187 MODEL, two of them
  TEMPLATES (.claude/skills/harness/templates/README.md:30, templates/harness.json:82), so every new
  /harness-init seeds the contradiction.
- NON-BLOCKING · HARNESS DEFECT, sixth recurrence (issue #199): the `notes/receipt-<agent>-<runid>.md`
  path harness-handoff prescribes is DENIED by the domain hook for most personas. harness-pm's grant
  at .harness/team-config.yaml:88-98 has no receipt-*.md pattern at all. pm filed to
  notes/research-* instead and disclosed it.
- NON-BLOCKING · ORCHESTRATOR CANNOT SELF-VERIFY A RED PROOF. The domain hook denied me a scratchpad
  `cp` of factory_gh.py to reproduce the project-id red myself (correctly — DEC-151, guardrail
  evasion). I verified the assertion STATICALLY instead: test-factory-gh.py:306 asserts
  `pid == "PVT_kwFAKE" and pid != "3"` against board number 3, so it excludes the buggy value by
  construction. Structural, not executed-by-me.
- NON-BLOCKING · CYCLES ARE 10 OF 10 AND THE COUNT IS DISCLOSED, NOT ASKED. The operator ruled this
  run's new work adds zero and I honoured that for all four dispatches. The +2 is entirely inside
  assert2-eng, where two of DEC-157's three triggers fired at once: an unmet-SC re-dispatch AND the
  lead's own reported member send-back. DEC-157's worked example uses six distinct runs and does not
  cover one run firing two triggers. Consequence: the ship phase begins with zero rework headroom.
  RECOMMEND raising max_total_cycles to 12 as part of the ship decision, or overturning the count
  to 8. Either is a user decision recorded in feature.yaml.
- NON-BLOCKING · plan.yaml line 1435 still records task 08 `status: pending`. Stale; pm's to fix.
- NON-BLOCKING · gh-sync.py open not run. RULED by the operator: wait for the factory to own it.
- HARNESS DEFECTS for the owner, none this feature's: four check-state violations across FEAT-04 and
  FEAT-07, all the IDENTICAL lead-digest-contract defect (DEC-156); two inert `<!-- ok-stale -->`
  markers one line off their target.
