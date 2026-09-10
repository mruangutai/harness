# Plan-panel review — spec compliance — FEAT-58 (planpanel3 / scope) — cycle 0

**BLUF: FAIL.** Structurally the amended plan is sound — REQ/SC/task graph is complete and acyclic,
all nine `verify:` blocks execute as written, the three weight-bearing proofs can each report red,
and an independent re-audit of the amendment found zero disturbed ledger rows. But I found a SECOND
instance of the exact D-1×cross-feature-scan fail-open this plan was built to close (unaddressed,
in `board_lifecycle.py`'s ship-time board audit — a live, used code path), and N-07's own test
intent asserts a merge-gate.py exit-code contract that the tool has never had and does not propose
changing, which would block that task's own gate from ever passing a correct implementation.

## The seven shared questions

1. **Can each weight-bearing proof report red?** Yes, all three. N-04's merge-skipbits test is its
   own file, must-fail-today, with an explicit pre-change-reproduction step asserting the two runs
   DIFFER (BLOCKED, never weakened, if the fixture can't reproduce the shape). N-06's equivalence
   test explicitly excludes exit status and carries a discrimination clause (perturb X, assert
   inequality) against the vacuous-two-empty-sets trap. N-02's no-repair test has its own
   RED-PROOF instruction (route one break through `--repair`, confirm it reddens, revert). None of
   the three can pass vacuously as written.
2. **Are the positive controls load-bearing now, and can they see the NEXT defect?** Yes to both.
   N-05 Group 2's `REQUIRED_PATHS` now names all three non-features `.harness` subtrees plus the
   directly-in-`.harness` file, each its own assertion; Group 3's derived-not-literal proof was
   widened (GC-02b) to add a NEW top-level dir, a NEW `.harness` subtree AND a NEW **nested**
   `.harness/harness/<new>` subtree, which is the shape most likely to catch the next derivation
   regression rather than only this one.
3. **Did consolidation drop coverage?** No, by an independent method. I did not re-walk the
   digest's ledger row by row (the goal-check already did that); instead I read the CURRENT text of
   every amendment-touched task (N-01, N-02, N-05, N-06, N-08, N-09) and D-08, and matched each
   against what the ledger and prior findings (GC-01..GC-07, C-01..C-04) said should be there.
   Found all present, none disturbed: three-part D-08 derivation, owner-root refusal in N-07,
   shim-no-exec in N-04, index regen+`--check` in N-08, SC split (12→13) consistently threaded
   through N-01/N-09 `traces:`.
4. **The seven binding items.** All first-class, verified against REQ *text* (not the coverage
   table): REQ-06/REQ-07 (M-1/M-2) are mechanism REQs in their own right with their own SCs
   (SC-09/SC-10, SC-11) and own primary tasks (N-02, N-04) — not folded behind D-1..D-3.
5. **The interaction nobody planned for.** D-1 silently disabling D-4 in `merge-gate.py` is real
   (verified at source, see below) and N-07 fixes it correctly in design. **I found a second
   interaction of the identical shape, unaddressed** — see PP-01.
6. **The operator's shape rule.** Each of the nine tasks owns one coherent surface (fixture,
   mechanism, corpus read, hook tier, creation, audit, uniqueness, live correction, non-regression);
   the thirteen SCs read as observable outcomes with sanctioned measurement modes embedded, not
   test-design mechanics — those live in tasks' `intent`/`verify`, matching the BRIEF's own stated
   rule. No staple found.
7. **Executability.** All nine `verify:` strings run as literal shell against the real worktree:
   `git merge-base origin/main HEAD` resolves (`abff2a84`), the `:(exclude)` pathspec syntax is
   valid git (tested, exit 0), and `f58_sparse_fixture.py --self-check`/`--strict` have a defined
   meaning at every point they're invoked (N-01 defines both modes; N-09 is the first `--strict`
   call and by then every named test file exists per `depends_on`). `depends_on` is acyclic and
   correctly serializes the `bin/*` single-writer surfaces. One task-intent (not shell-syntax)
   defect found — see PP-02.

## Findings

| id | sev | lands on | finding | concrete change | premise verified at |
|---|---|---|---|---|---|
| PP-01 | **high** | D-3 (DoD) / REQ-03, plan scope (no task) | `board_lifecycle.py`'s cross-feature board-status audit (`_feature_dirs`/`_status_findings`, class 6/T-15) shares the *exact* D-1×cross-feature-scan shape N-07 fixes for `merge-gate.py`, and is untouched by any task or decision. `gh-sync.py ship <feat-dir>` — the real per-feature ship path — calls `board_lifecycle.audit_findings(repo)`, whose `root = harness_boundary.resolve_root(_BIN_DIR)` resolves to the **worktree** root (each worktree carries its own MARKER, so `resolve_root` never climbs past it — confirmed in `root_from_script`/`resolve_root`). Under D-1, `_feature_dirs(root)`'s glob then sees exactly one feature instead of ~79, so every future `ship` silently narrows the board-status cross-check to the shipping feature alone. The DoD note's own premise ("board station versus feature.json... None consults a second feature") is factually wrong for this call path. | Extend N-07 (or add a task) to route `board_lifecycle.py`'s feature enumeration through `harness_boundary.worktree_owner()` the same way N-07 does for `feature_for`, refusing rather than silently narrowing inside a worktree — or record an explicit operator-approved deferral, analogous to D-06, rather than leaving it silent. | `merge-gate.py:11` (`ROOT = sys.argv[1]`) + `merge-gate.sh` (`resolve_root($_selfbin)`, confirms the worktree-root pattern this defect mirrors); `board_lifecycle.py:472-477` (`_feature_dirs`), `:725` (`root = harness_boundary.resolve_root(_BIN_DIR)`); `harness_boundary.py:66-92` (`resolve_root`/`root_from_script` stop at the nearest MARKER, never climb to the owner root); `gh-sync.py:2011` (`cmd_ship`), `:2222-2233` (`_ship_audit` → `board_lifecycle.audit_findings`) |
| PP-02 | **high** | N-07 (task intent, PART 5 cases a/c), SC-07/REQ-04 | N-07's intent instructs `test-merge-gate-branch-uniqueness.py` to "assert a NON-ZERO exit" from `merge-gate.py` for the DENY cases, but `merge-gate.py` never calls `sys.exit`/`exit()` anywhere (grepped, zero hits) — the process always exits 0, and `deny()` signals refusal exclusively via `permissionDecision: "deny"` JSON on stdout. This plan proposes no change to that contract. If implemented as literally instructed, N-07's own machine-checked `verify:` can never pass for a *correct* fix to the D-1×D-4 interaction, since the asserted non-zero exit never occurs — blocking the very task that closes the interaction this plan exists to fix, or tempting an implementer to add a spurious `sys.exit` to a shared hook used by every feature's merges. | Correct N-07 PART 5 cases (a) and (c) to assert `permissionDecision == "deny"` on stdout JSON (mirroring the sibling file's established convention), not a non-zero process exit; case (b)'s "assert exit 0" needs no change since it already always holds. | `merge-gate.py` (no `sys.exit`/`exit(` call in the file, grepped); `merge-gate.py:169-176` (`deny()` body, no exit call); `tests/integration/test-merge-gate.py:53-56,65,89,...` (20+ existing assertions of the form `r.returncode == 0 and d == "deny"`) |

## Not re-raised (settled / out of scope per charter)

`lanes:` staleness (constraint a), D-06 open (constraint b), all-tasks-main-session-direct
(constraint c), thirteen-vs-twelve SC split (constraint d) — all confirmed present as described,
not re-litigated. Did not touch the six filed harness defects, FEAT-53's run dirs, or
597-omp-behavior-baseline.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Structurally sound and no dropped ledger coverage, but a second unaddressed D-1×cross-feature-scan fail-open (board_lifecycle.py's ship-time board audit) and an N-07 test-intent defect that would block that task's own gate from ever passing a correct fix"
  severity_max: high
  findings: 2
  must_fix:
    - "PP-01: extend this plan (N-07 or a new task) to close board_lifecycle.py's identical D-1×cross-feature fail-open in its ship-time board audit, or record an explicit operator-approved deferral"
    - "PP-02: correct N-07 PART 5 cases (a)/(c) to assert merge-gate.py's actual JSON permissionDecision:deny contract, not a non-zero process exit it has never had"
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should board_lifecycle.py's cross-feature board audit be brought into this feature's scope (mirroring N-07's owner-root fix), or explicitly deferred with operator sign-off given it ships silently degraded once agents work from sparse worktrees by default?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-58-corpus-outside-worktree/.harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c0.md
```
