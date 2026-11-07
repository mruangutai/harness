# Retrospective panel recording — FEAT-2081

**Recording succeeded; INV-32 remains FAIL.** Missing-panel evidence is repaired at canonical feature plan.yaml panel. High substance F1 remains open as PF-5bfc6ea843dcdddb994445126b398fb1. T-03/T-04 amendment requires operator re-signature; no implementation or amendment is authorized by this receipt.

## Exercised evidence

- Control-plane plan-merge.py record-panel ran with the absolute feature plan.yaml, digest runs/2026-10-05-01-validator/panel-c1.md, cycle 1, and absolute last-run directory. Exit 0; stdout: ADDED PF-5bfc6ea843dcdddb994445126b398fb1; PANEL cycle 1 from the specified digest to the canonical plan; APPLIED the canonical plan.
- Loaded panel confirms scope / harness-code-reviewer, design / harness-ui-reviewer, and goalcheck / harness-pm ran. should-not-exist / fable-advisor skipped because fable-advisor is not available in this session's agent registry. Scope assessment is durable, not an accepted native signed-plan return.
- Finding summary: T-03/T-04 omit CI provisioning of the pinned historical checker required by the differential integration test. Recorded severity high, kind substance, disposition open; content-hash ID above.
- Automatic command-induced check-state --changed report was read, not rerun: INV-32 high-open violation, skipped-reader note, and separate building-state missing notes/handoff-plan.md violation. That automatic invocation was not the requested feature-scoped --only invocation (harness_boundary.changed_state_feedback invokes only --changed).
- Exactly one explicit scoped check: env HARNESS_PROJECT_DIR=<feature-tree-root> python3 <control-plane-root>/.agents/skills/harness/bin/check-state.py --feature FEAT-2081-ci-shard-structure-audit --only INV-32. Exit 1: VIOLATION INV-32: FEAT-2081-ci-shard-structure-audit finding PF-5bfc6ea843dcdddb994445126b398fb1 is high and remains open without operator risk acceptance. Also printed the fable-advisor skipped-reader note. Source inspection confirmed both flags in check_state/runner.py; harness_boundary.resolve_root supports HARNESS_PROJECT_DIR, explicitly not host-owned CLAUDE_PROJECT_DIR. Used the supported boundary rather than cwd or an unsupported HARNESS_ROOT override.

## Protected-content comparison

Read-only before/after SHA-256 comparison of sorted JSON loaded plan values excluding only panel is unchanged: 76eaa7f289b6bdaf52782ffba53c8ff85cad1131366daccbb975407b0325916e. This covers all six tasks, one decision, routing, thresholds, and approval. BRIEF bytes unchanged: 7f72288253d8a6c5e0b8132af1938df2ed3ed2f3fe7ea92e8e39aa644d927e1a. Approval remains approved, approved_by operator (Mike Ruangutai), via main session, date 2026-10-04. No commit, disposition resolution, GitHub change, gh-sync, build, test, lint, formatter, or whole-suite gate was performed.

## Open questions

- Operator/Main must handle T-03/T-04 historical-baseline provisioning amendment and re-signature, or explicit operator risk ruling; this receipt does neither.
- Native retrospective signed-plan scope-return protocol remains unresolved as documented in panel-c1.md; no retry or signature toggling occurred.
- Automatic feedback's missing plan handoff is outside this recording assignment; lead bookkeeping was untouched.
