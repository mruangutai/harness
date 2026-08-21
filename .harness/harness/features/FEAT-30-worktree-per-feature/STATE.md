# STATE

## Current

- feature: FEAT-30-worktree-per-feature
- phase: build — ENDED, blocked on one operator ruling (phase recorded here; the shape gate denies a
  `phase` key in feature.json)
- run: 2026-08-20-01-build-eng — returned BLOCKED. T-01 PASS, T-02 PASS, T-06 PASS, T-08 FAIL, T-10 PASS
- squad: eng
- status: blocked
- cycles_used: 7 of 13 (six remaining). Runs 7 of 20, informational.

All five team-lane tasks are BUILT. **Nothing is committed and nothing is staged**, deliberately:
`gates.qa_gate` is blocking, the integration suite is red, and SC-09 is violated right now — a test
that passed at `49c528a` fails at HEAD. No task was marked `done` in plan.yaml and no `close-task`
was run, because nothing has landed; recording otherwise would falsify the board. The five team tasks
remain `building`.

**THE BLOCKER — one ruling, one line.** `test-harness-yaml.py` asserts exactly one guarded import in
`bin/` against a hardcoded allowed set of three; `feature-worktree.py` is a fourth because T-01's
signed intent REQUIRED it ("import harness_boundary lazily and, if the import fails, exit 2 with a
message naming the module"). Approved plan versus existing invariant, and no task owns the
reconciliation. Option A: add the file to the allowed set (one line, but a file in no task's `files:`).
Option B: drop the guard (in scope, breaks no test, departs from a signed instruction). **Recommend A**
— `check-domain.sh` is already allowed for guarding first-party `feature_schema`, and the test's own
comment keeps assertion 2 a subset so new cases can land. Measured in fairness to B: NOTHING tests the
guarded branch, so `exit 2` is not load-bearing on any evidence. One failing assertion, 18 ok lines.
Full analysis: `notes/orchestrator-M20-signed-intent-vs-existing-invariant.md`.

Briefing for the operator: `notes/ship-review-2026-08-20-01-build-eng.md` (+ rendered `.html`).
Work order for the operator's five tasks: `notes/layer0-segments-FEAT-30.md`.

Suites: unit exit 0 / 179 PASS / 0 FAIL (unchanged from baseline, correct). Integration exit 1 / 212
PASS / 2 FAIL, where the 2 lines are ONE defect reported twice (assertion + script summary). Growth
+122 decomposes as 74 + 32 + 14 + 2 runner lines, so both suites are genuinely discovered, not
passing silently.

Reviewed substantively, not by verdict: SC-02 via `merge-base` against the pre-create tip; SC-04 and
SC-07 print per-path `MISSING/DIFFERS/VERIFIED` and `WOULD DISCARD` with content hashes, never counts;
SC-08 drives two concurrent `Popen` writers asserting by named entry; SC-01b case A asserts all six
pairwise write-window overlaps plus "no other branch advanced". I also invoked the CLI against the
REAL repo: `list --repo harness` returns the FEAT-31 tree, exit 0, legacy one-segment worktree
included and main checkout excluded.

## Open Questions

- **Q1, BLOCKING — the guarded-import ruling above.** Only the operator can settle it; both remedies
  alter something signed.
- **Q3 — `plan.yaml`'s T-10 `verify:` is unrunnable as written.** It copies a single file, which
  cannot import sibling `harness_boundary` and dies `ModuleNotFoundError` before any assertion, on the
  pristine file — verified by inspection, no `sys.path` manipulation exists. The member re-expressed it
  as `cp -R` matching T-06's precedent and disclosed it. The plan still needs pm's one-line fix or every
  future re-verification of T-10 fails spuriously.
- **Q2 is SETTLED, not open.** The `cp -R … "$T/bin"` contradiction is persona, not syntax: the guard
  does not expand `$T` (it printed the literal), but `bash-write-guard.sh:49-57` exits early for no
  `agent_type` and for `harness-dev-ops`. Four consistent points: T-02 dev-ops green, T-06 backend-dev
  denied, orchestrator denied, operator carries no `agent_type`. **T-03/T-04/T-05 will run literally
  as written for the operator.**
- **Both plan-text defects trace to ONE choice** — T-01 importing a sibling module. Guarded form trips
  the cap (Q1); sibling nature breaks a one-file copy (Q3). Neither is a builder error.
- **Weakest points, stated plainly.** (1) T-01's red proof reddens at the fixture GUARD, so SC-01's
  static isolation assertions are green without being shown able to redden. (2) `list` uses
  `commonpath` as required but no `worktrees-old` sibling case asserts it, so a `startswith` refactor
  would pass. (3) T-10's case B satisfied itself via the committer-failure path ~13 times without
  calling the predicate — R-02's failure mode 3, NOT the documented flake; the squad fixed it and got
  8/8. Had it been retried past as "the known flake", SC-01b would have shipped green and incapable of
  red.
- **Fail-open window until T-04.** `harness_boundary.py:37` and `check-domain.sh:644` hard-code one
  path segment; `dest_for` writes two. Do NOT create a real feature worktree with the new CLI until
  T-04 lands. The live FEAT-31 tree is one segment, so it IS governed today.
- **I cannot verify any red proof at layer 1 by construction** — each begins by copying `bin/` to
  temp and the guard denies the orchestrator's `cp`. Red-proof claims rest on members' reported output.
- Backlog B-1..B-10 are enumerated in the briefing. B-1 matters soonest: the qa gate will emit a FALSE
  "integration missing" FAIL on T-04, because `test_kinds.integration.detect` names 4 scripts while
  the runner runs 12, and T-04's own test files are not among the 4.
- **This feature falsifies DEC-193** (`.claude/worktrees/<id>/` versus the delivered `<repo>/<id>`).
  No task touches docs; nothing detects a falsified decision. Recommend am.3 after T-04, routed to
  `harness-documentor` through product-lead — a team lane, not operator hands.
- SC-06 named by no task; D-01 names three subcommands where the intent specifies four; carried Q11,
  Q12, Q14, Q15, Q16. Q13 superseded by the DEC-193 item — DEC-95 is NOT falsified, it makes no claim
  about path depth. D-09 unchanged.
