# Observations - harness-backend-dev

- 2026-08-24: FEAT-34 T-01 — matching a worktree's owner_root against `factory_config.harness_root()` (or against `resolve_repo`'s returned owner_root) fails when the importing module itself lives inside a worktree, because `harness_root()` derives from the calling script's own file location, not cwd — it resolves to the worktree, not the true main checkout `git worktree list` reports. Fix used in `worktree_terminal.py`: match by repo SEGMENT NAME instead ("harness" literal, or the fleet entry whose trailing owner/repo segment matches); `resolve_repo`'s returned `default_branch` never actually depends on owner_root correctness so this still goes through the real `resolve_repo` per the no-re-derive rule.
- 2026-08-24 (FEAT-34 T-02): worktree_terminal.classify() reads features under .harness/<repo_segment>/features, not a hard-coded .harness/harness/features -- a second-repo fixture landing feature.json under the "harness" segment name silently gets git ls-tree errors -> klass unresolved, not the enumeration failure you'd expect. Cost one red run to find.
- 2026-08-24 (FEAT-34 T-02): case (g)'s pre-registered hypothesis (that classify(root) called with a fleet repo's own root cannot see that repo's own worktree because git worktree list only reports the cwd repo's worktrees) was falsified when classify() is called with root = that repo's own path, matching T-03 post-merge-sweep's documented one-call-per-repo-root contract. The concern would only bite a caller that called classify() on repo1's root expecting repo2's worktrees to appear there, which nothing in this feature's plan asks for.
- 2026-08-24 (FEAT-34 T-02): steering fleet resolution in a fixture needs a SEPARATE probe_root (its own SPEC.md + .harness/factory/fleet.yaml) from the actual fleet-member repo, plus a FRESH subprocess with CLAUDE_PROJECT_DIR set -- factory_config.FLEET_PATH is computed at import time so a same-process second classify() call after the first import cannot be re-steered.
- 2026-08-24 (T-02 c2): D-10 overturned c1's closing conclusion that REQ-04's cross-repo
  enumeration is satisfied by the caller iterating repos - classify_all(root) is now the
  entry point in worktree_terminal.py itself. Extending test-worktree-terminal.py for it
  required the probe_root fixture to become a REAL git repo with its own standing Done
  worktree (case_second_repo's probe_root was directory+SPEC.md only, sufficient for the
  FLEET_PATH/harness_root() import-time probe but NOT for asserting classify_all's harness
  half returns anything) - otherwise the harness-half assertion in case (i)/(l) passes
  vacuously against an empty list. Reused case_second_repo's second-repo fixture builder
  unchanged for cases (i)-(l) rather than inventing a second fixture shape, per the dispatch.
- 2026-08-24: T-02 c2 loop-back cycle 1 — a "RED PROOF" built by filtering the SAME real output
  and then asserting the filtered set lacks what was just filtered out is a tautology, not a
  demonstration (P-05 already names this pattern for mutate-in-place comparisons; the same trap
  reappears as filter-then-assert-absence on a single producer). Fix: build a second, independent
  producer (a local deliberately-wrong stub) and run both against the same fixture in the same
  subprocess so the two sides can actually diverge.
- 2026-08-24: FEAT-34 T-02 rework (classify-from-linked-worktree hole) — every existing case in
  test-worktree-terminal.py called classify(repo_root) from the repo root, so the main checkout's
  realpath always coincidentally equaled `root` and got skipped; none exercised classify(root) with
  root itself set to a linked worktree, which is how check-state.sh/post-merge-sweep.sh always call
  it. Added case_classify_from_linked_worktree() — RED against unfixed worktree_terminal.py:195-197,
  emits an unresolved record for the main checkout with feature_id=None. Pattern for future modules
  with a "root vs enumerated path" skip check: always add a case where root is NOT the first
  enumerated path, not just one where root == first entry.
- 2026-08-24: FEAT-34 T-01 rework — classify()'s main-checkout skip compared os.path.realpath(path)==os.path.realpath(root), which fails silently (fail-open into an unresolved/misclassified record, not a crash) whenever root is itself a linked worktree, because the main checkout's porcelain entry then never equals root. Fix: derive the main checkout from porcelain ORDER (index 0, per check-state.sh's INV-25 precedent at :1138-1143) rather than a value comparison to a caller-supplied argument — the same class of bug as comparing a lookup's absence to a caller's identity instead of to the data's own known-total shape.
