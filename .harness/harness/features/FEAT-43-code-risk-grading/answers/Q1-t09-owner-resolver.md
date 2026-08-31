# Q1 — T-09 owner resolver correction

**Decision:** Approved by the operator on 2026-08-28.

T-09 resolves the owner checkout through `harness_boundary.worktree_owner`, invokes that owner's `check-domain.sh` resolver directly when it differs from the branch checkout, preserves owner-manifest parity, and does not set the retired `HARNESS_PROJECT_DIR` override. `test-no-distribution.py` remains unchanged.

This is an implementation correction preserving the approved REQ-09 behavior. The plan approval remains valid.
