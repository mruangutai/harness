### REUSE reader — BUG-1304 — verdict: ADEQUATE, nothing to recommend

**BLUF: both routes share the predicate and the message builder.** `check-domain.sh`'s
`claim_checkout_guard` and `bash-write-guard.sh`'s `claim_checkout_guard` both compute
containment and the claim set through `harness_boundary.claim_worktrees` (harness_boundary.py:247)
and `harness_boundary.inside` (harness_boundary.py:244), and both render every refusal string
through the single `harness_boundary.claim_set_refusal` (harness_boundary.py:273) — including the
control-plane-expertise carve-out (`claim_set_refusal`'s `expertise_segment` branch, same file)
and the ambiguous-registry / unreadable-registry cases. Neither guard spells its own containment
test, its own expertise-path carve-out, or its own refusal wording. That is exactly the DEC-193
seam requirement and it holds.

**Containment primitive dedup already landed in this diff, not left behind.** `select_base`'s prior
local `inside()` closure (harness_boundary.py, old ~443-448) is deleted in this same diff and now
calls the module-level `inside()` — the diff removes a pre-existing duplicate rather than adding
one (harness_boundary.py:506, comment "All containment decisions use the module-level primitive
shared with claim_worktrees").

**The only per-file variation is the two hosts' pre-existing error-reporting convention, and it
is precedented, not new tech debt.** `check-domain.sh:770` and `bash-write-guard.sh:729`'s new
`claim_checkout_guard` bodies are structurally identical (import, `real()`, `inside()` early-out,
`try/except AmbiguousWorktree/UnreadableRegistry/Exception`, containment check, refusal) and differ
only in `deny(...)` (bash-write-guard.sh, its established host-local reporter) vs
`print(...); sys.exit(2)` (check-domain.sh). This exact split — same logic, same two reporting
idioms — already exists for the pre-existing sibling `feature_checkout_guard` in both files
(check-domain.sh:737, bash-write-guard.sh:699), which this new function sits directly beside and
mirrors. It is the established pattern for this codebase's two guard hosts, not a fresh duplication
this diff introduced.

**Secondary check (helper restatement):** `claim_worktrees` (harness_boundary.py:247) reuses
`linked_worktrees` (harness_boundary.py:150, `.git/worktrees` pointer enumeration) and
`worktree_for_feature` (existing) rather than re-parsing `.git` pointers or re-walking registries.
`inflight_registry.live_claims` reuses the existing `_matches`/`_visible`/`_parse` helpers rather
than re-implementing claim filtering. Nothing new in the diff restates an existing exported helper.

No recommendation. Ceiling of one was not spent because nothing cleared the bar.
