# STATE

## Current

- feature: FEAT-17-guard-boundaries
- run: .harness/features/FEAT-17-guard-boundaries/runs/2026-08-11-06-rescope-product/digest.md
- squad: product
- status: awaiting-user

PLAN RE-SCOPED, still awaiting signature. BRIEF.md and plan.yaml remain signature-ready:
approval.status pending, 7 tasks, 9 REQ, 10 SC, now 9 decisions (D-09 added). T-01..T-06 are
main-session-direct (all four DEC-174 carve-out files plus the extracted harness_boundary.py),
T-07 is team, routed to harness-documentor.

The re-scope: #103's founding evidence — FEAT-09's 205-line feature.yaml written from a session
ROOTED in a stray worktree — is OVERTAKEN by DEC-180 / issue #132 and is now recorded as such in
BRIEF.md's Problem section with the a29ad06 re-measurement (211-line feature.yaml exits 2, 70-line
handoff note exits 2 — identical to the real checkout). The rooted case is fully governed; what
remains for it is lost work, not an ungoverned write. Still live and unchanged: #261's shell route,
and writes INTO a stray worktree from a harness-rooted session plus creating one.

CUT: T-02's module-level hoist, and with it SC-03's no-PyYAML cluster on both routes and REQ-02's
bootstrap clause. The resulting divergence — under the PyYAML bootstrap grant the Bash route refuses
a stray root and the Write route does not — is recorded as D-09, reversible at signature, not
hidden. KEPT: the root-side rule itself, on the standing ruling that a stray worktree is a MISTAKE
plus the lost-work risk, and because SC-06's mutation proof is only reachable with the session root
pinned inside a worktree. REQ-02 was rewritten, not merely re-justified: its old mechanism claim
was false at a29ad06.

Gates re-run at the orchestrator tier against the RE-SCOPED plan: check-plan-routes.py reports
0 violations across 1 plan (DEVIATION on T-01..T-06, OK on T-07); all 11 unique literal files:
paths independently resolved with check-domain.sh --resolve and each matches its declared lane;
harness_yaml.load_plan parses the amended plan (previously UNVERIFIED, now closed).

Cycles 6 of 10 — one lead send-back in this run, where pm's first return stated REQ-02 wider than
the plan delivers. Nothing is signed and no build work was dispatched. Seam note:
notes/handoff-plan.md (seq-3).

## Open Questions

- Q1 SC-03's no-PyYAML half splitting into its own criterion: MOOTED by the re-scope — the cluster
  was cut, so there is no half left to split. Reversible at signature via D-09, which restores both
  the hoist and the cluster together.
- Q2 Whether SC-03 survives: it does, narrowed to the forbidden/allow pair plus the two-directional
  wording assertions. It is the sole criterion asserting the root-side rule's UN-MUTATED refusal on
  each route; SC-06 is a mutation criterion and cannot stand in.
- Q3 Backlog, not planned here: both guard suites sit in run-unit-tests.sh INTEGRATION_SCRIPTS
  despite matching the unit glob, so --kind unit never runs them.
- Q4 Backlog, not planned here: bash-write-guard.sh resolves RELATIVE operands against the harness
  root rather than the agent cwd. Untriaged — defect or intended conservatism.

ANSWERED and struck: INV-25 severity. It remains a FAILURE, not a warning (operator, 2026-08-11).
