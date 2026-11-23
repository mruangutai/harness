# Simplify pass — BUG-2399 plan draft — 2026-11-22

Scope: `BRIEF.md` and `notes/research-BUG-2399-run-records-tracked-draft.md` (plan surface, flag-only). The main session hosted four parallel read-only `reviewer` dispatches, one angle each (harness-simplify), because the pm has no spawn tool and product-lead cannot dispatch eng-squad members. Precedent: FEAT-2257 plan. The settled grilling scope was declared not flaggable.

| Angle | Reader | Result |
|---|---|---|
| reuse | S2399Reuse | no findings: the plan extends merge-gitignore, the checkout-upgrade procedure and the existing integration fixtures, with no second helper |
| simplification | S2399Simplification | 1 finding (below) |
| efficiency | S2399Efficiency | no findings: the repeated integration runs are deliberate red/green and boundary steps |
| altitude | S2399Altitude | no findings: the rule sits in a new DEC and SPEC, the migration in the existing merger and upgrade surface |

## Findings for pm (flag-only; pm applies)

- **SIMP-1** — `notes/research-BUG-2399-run-records-tracked-draft.md:37`. The `Upgrade safety contract` section restates the migration procedure that T-02 and SC-02 already specify, and adds conditions of its own (refuse a dirty index, preserve byte identity). Cost: three separately maintained statements of one rule can drift, and the implementer cannot tell which conditions are required. Alternative: keep the complete upgrade contract once, under T-02; make SC-02 a concise acceptance statement; delete the separate section, folding any condition that must survive into T-02.
