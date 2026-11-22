# Security review — BUG-2294 — c1

FAIL — T-01 introduces an intermediate-symlink deletion escape; fix target containment before shipping.

Reviewed c1724230c4d931ad46d433c8ba93df8cf312f898 → 70981edd6f9f110965a0148b4490ed2673d262dc. Scope IN: filesystem names and links select destructive CLI targets. Reviewed all five T-01 paths and the additional feature-record/documentation diff; no credential additions identified. Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent.

## SEC-01 — substance / med / T-01 / security-reviewer — must fix

`.claude/skills/harness/bin/prune-run-evidence.py:118-129`: `present` accepts directory symlinks (`keep_set:81-82`), `_ui_targets` follows them, and `rmtree` now receives a path *beneath* that link. A local actor able to plant `runs/build-alias -> validate-c2-validator` can cause a later operator prune to delete the PASS-kept validator's UI, provided its served commit differs from the shipping pin. The real validator name is kept; the alias is not. Alternatively, pointing the alias outside the feature deletes that destination's `ui/` with the operator's filesystem permissions. This requires unusual local filesystem access, so severity is med, not an asserted privilege escalation.

[INFERENCE, static trace; not executed] The base passed the symlink itself to `shutil.rmtree` (base:124), which rejects a directory symlink. The reviewed pin instead passes `alias/ui`; the alias becomes an intermediate path component and the target's real UI directory is removed. Thus this particular escape is newly reachable, not merely the unchanged selector's pre-existing symlink acceptance. A direct `ui` symlink remains a leaf symlink and is a different case.

This violates SC-01's kept-UI guarantee and destructive-scope constraint. Require no-follow containment of run/UI targets, preserving protected identities; add regressions for a run symlink to a kept run and to an outside directory, asserting destination bytes survive. Existing new fixtures contain only real directories and do not discriminate this regression. T-01 owns both remedy paths.

## Other inspection

SC-03: pinned pruner:65-115,134-145 and ship command:38-54 retain selectors, explicit-keep validation, refusals, step placement and both invocations; the pinned DEC-238 diff changes its ship clause only. Ordinary-directory deletion is narrowed to UI. Feature/root lookup and their existing path handling are unchanged, not newly introduced findings. No network/auth/dependency surface is added.

No tests, builds, linters, formatters or adversarial executions run (read-only assignment). QA should run T-01's `python3 tests/unit/test-prune-run-evidence.py` and the containment regressions after repair.

Open questions: none.
