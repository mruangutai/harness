# Handoff — BUG-285-canonical-reader, ship → integration — at deeeab5c, seq-28

## Next

Main owns the integration boundary the orchestrator cannot cross: integrate current `main` into `feat/BUG-285-canonical-reader`, preserve the reviewed feature behavior, create and merge the feature PR, record its number, then run canonical ship synchronization from the main checkout after the merge. The operator explicitly authorized those actions in `notes/answers-2026-09-15-integrate.md`.

After the merge is on `main`, run `gh-sync.py ship` against the main checkout's BUG-285 feature directory, verify the parent/task board and issue states are terminal, and remove the feature worktree from outside it.

## Trust

- The operator accepted BUG-285 as ready to ship and selected B-1 through B-5 in `notes/answers-2026-09-15-fix-c1-validator.md`; the later `notes/answers-2026-09-15-integrate.md` rescinds the run-only PR prohibition and authorizes integration.
- Final reviewed implementation tip is `5be21a432b87ed648c0bed50fbf9a2642c84e0a9`; final validator run `runs/2026-09-15-fix-c1-validator/digest.md` is PASS with the required matrix complete and no must-fix findings.
- Ship briefing and rendered HTML are committed at `c1ba0418`; operator acceptance and all five backlog links are committed at `deeeab5c`.
- B-1 through B-5 are open and were read back from GitHub: #1705, #1706, #1707, #1708, and #1709. `gh-sync.py backlog` is non-idempotent; do not invoke it again for these rows.
- The feature worktree was clean at `deeeab5c` before this handoff write.
- The last harness state check found no BUG-285-local violation; its sole violation was unrelated standing worktree BUG-1563.
- UAT is not required because validation's UI reviewer self-scoped out after a 152-path census.

## Dead ends

- Do not mark the plan `done` or run `gh-sync.py ship` from this worktree before the merge; canonical ship synchronization follows the landed feature record on `main`.
- Do not rerun any B-1 through B-5 backlog command; each call creates a new issue.
- Do not broaden the feature during main integration. Any conflict is resolved to the reviewed canonical-reader contract; unrelated current-main changes stay current-main-owned.
- Do not interpret review SHA `5be21a43` being behind record-only commits as stale implementation review; later commits contain only governed feature records, the briefing, operator answers, and handoffs.

## Working set

- `.harness/harness/features/BUG-285-canonical-reader/STATE.md`
- `.harness/harness/features/BUG-285-canonical-reader/feature.json`
- `.harness/harness/features/BUG-285-canonical-reader/plan.yaml`
- `.harness/harness/features/BUG-285-canonical-reader/notes/ship-review-2026-09-15-fix-c1-validator.md`
- `.harness/harness/features/BUG-285-canonical-reader/notes/answers-2026-09-15-integrate.md`

## Done when

Scope: the reviewed feature is merged without scope drift, PR linkage is recorded, canonical ship sync reaches terminal GitHub state from `main`, and the feature worktree is removed from outside it.
Authority: brief-sc:SC-01
Authority: brief-sc:SC-04
Authority: brief-sc:SC-07
