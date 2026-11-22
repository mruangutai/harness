# Validate ruling by delegated authority — FEAT-2337 — 2026-11-22 — GC-03 owner-manifest gate

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorB6ManifestGate`). Raised by validate c1 (`r-20261122-4-validate-validator`,
ESCALATE, GC-03 high).

**Finding.** At `review_sha` 6143625f, the integration receipt has `runner_exit 1`. Its only
failing file is `tests/integration/test-check-plan-routes.py`: cases 04, 05, 15, 17, 19d and 19d2
report `DEVIATION <worktree>/.harness/team-config.yaml differs from <control plane>`. T-03 added the
signed harness-qa receipt grant to the worktree's `team-config.yaml`, and that is the one line that
differs. In an independent clone of the same commit the file exits 0, as main and QA each
reproduced.

**Ruling: A, amended.**
- **This is not a test defect.** `check-plan-routes.py` deliberately resolves a linked worktree to
  the control-plane root (`_owner_root`). Its parsed, route-level deviation check (FEAT-41
  T-09/T-15) is pinned, intended behaviour: it detects that a sanctioned grant is not yet deployed.
  Making it hermetic would remove that signal, so the B option is rejected.
- **Cycle 2.** The QA dispatch names this file as the one known red and requires an
  independent-clone run of it at the new pin (exit 0), preserved in the QA note. The red receipt
  is committed honestly; it is never relabelled.
- **Terminal verdict.** A cycle-2 validate whose only red is this file may **not** return PASS.
  `matrix_ok` is false on a red kind. Cycle 2 returns ESCALATE citing this ruling, and the
  escalation is recorded as resolved with this ruling as `decided_by`. Main proceeds to the PR
  when cycle 2 shows all three of:
  (a) the only red is this file;
  (b) the paired clone run of it exits 0 at the new pin;
  (c) GC-02's fix (34ef5cea) verifies at the new pin.
- **Clean-merge bar unchanged.** A fully green PR CI on a clean checkout is the binding green for
  this file and for everything else. Any red in CI blocks the merge, regardless of this ruling.

**Records.** This note. A process-documentation backlog item, explicitly not a defect: features
that edit `team-config.yaml` are structurally red on `test-check-plan-routes.py` in linked
worktrees until merge and deploy, so their dispatches must disclose it and pair it with clone
evidence.
