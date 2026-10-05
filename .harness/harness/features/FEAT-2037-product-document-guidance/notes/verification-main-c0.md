# Main verification — cycle 0

## Actual observed commands
From the assigned feature worktree, after the explicit product-checkout notation correction and origin/main merge:

- `python3 .agents/skills/harness/bin/check-skill-weight.py . && python3 .agents/skills/harness/bin/check-skill-refs.py . && python3 .agents/skills/harness/bin/check-instruction-paths.py`: exit 0. 55,847 words across 16 roles; refs ok (73 files); 68 instruction files, zero violations. No budget NOTE.
- `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit`: exit 0, 46 files, 8 workers, 25.79 seconds wall. Raw artifact://101.
- First updated-tree `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration`: exit 1, 73 files, 97.39 seconds wall. Only failing file was test-check-plan-routes.py, with six failures; raw artifact://102. Every failure named route deviation between new feature-worktree manifest and stale owner manifest. Do not suppress this failure or call this run green.

## Confirmed baseline cause and operator authorization
check-plan-routes.py lines 108–172 establishes the owner using worktree_owner and compares parsed manifest domains; no supported environment override is provided. Newly merged upstream #2071 added apps/packages/workspace grants to the feature baseline. Main inspected both manifests and found those grants absent from the owner's old main baseline. Root main had user-modified logs and untracked artifacts. Those are not this feature's work.

Main asked whether to sync owner baseline or leave it unchanged. Operator selected **Sync owner baseline**, authorizing a fast-forward only, preserving user files and stopping on conflict. `git merge --ff-only origin/main` in the owner checkout succeeded, from 652e70d4 to f35d3a72, without conflict or stash. This was authorized baseline maintenance, not feature implementation outside the worktree. No policy source was hand-edited outside the feature worktree. A new integration run was started after this actual prerequisite change; result not yet recorded here.

## Verification boundary
These are structural/regression receipts only. No live UAT assertion has been judged; no SC pass or final QA/independent panel claim. A live worktree-rooted OMP preflight is running separately. All formal UAT remains draft pending prerequisite review. No fixtures have been staged or restored, no production commit/pin, PR or merge.

## Integration after authorized recovery
`python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` after the owner fast-forward: **exit 0**, 73 files, 8 workers, 92.60 seconds wall; raw artifact://107. This confirms the supported baseline recovery, without changing any tests, gates, grants or feature scope. The preceding failing run is retained above.

## Runtime launcher identity
Actual executable `/Users/molchairuangutai/.bun/bin/omp`, version `omp/18.6.1`, SHA-256 `348d0987f05eab2f56b6f543933ca6bbb964d8d069cca9a55be3a5efffad041a`. A worktree-rooted CLI preflight uses `/tmp/harness-2037-build-preflight` for its disposable session. Delivery/conduct evidence remains pending; identity alone proves neither.
