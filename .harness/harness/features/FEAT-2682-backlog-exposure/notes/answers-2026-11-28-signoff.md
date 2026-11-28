# Operator sign-off: FEAT-2682 patch intake (2026-11-28)

**Signed:** BRIEF SC-01..SC-06 and plan.yaml T-01. **Rework ruling:** 1 round, 45 minutes, as proposed by `feature-record.py propose-rework` for a patch mission.

Rulings on the intake lead's open questions:
- **Q-01, accepted.** `change_type: api` stands. `enhancement` is a backlog nature, not a change_type.
- **Q-02, accepted.** A malformed backlog item exits 2 even when `github.sync` is off. Refusal before any GitHub call takes priority over the old SKIP.
- **Q-03, accepted.** DEC-138 and DEC-260 stay as they are (`keep`). The item grammar is a CLI detail, not a decision.
- **Q-04, accepted.** No commit on main mentions FEAT-2643 (`git log --oneline --grep=FEAT-2643 origin/main` returned nothing on 2026-11-28), so T-01's guard holds.

**Constraint:** the build starts only after FEAT-2643 merges to main.
