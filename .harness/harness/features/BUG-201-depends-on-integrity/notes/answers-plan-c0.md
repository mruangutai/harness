# Operator answers — BUG-201 plan c0 — 2026-09-07

- Q-A / PF-d26198866e2756a2288bf70a4226659b: Existing consumers that encounter a malformed plan with a dangling `depends_on` must surface the specific validation error rather than silently degrading it to “no plan” or `{}`. This is in scope for BUG-201.
