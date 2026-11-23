# Observations — harness-pm — FEAT-2452-gh-one-transport

- 2026-11-23: Removing a dual override pin from test support makes old code fall back to the default binary on inherited PATH; a red run is only safe if an offline PATH sentinel lands before the regression, and a factory-only override passing at baseline is not discriminating.
- 2026-11-23: Grilling "no DEC amendments" collided with DEC-205/254 when a settled deletion (gh_bin) falsifies a present-tense implementation sentence in a kept DEC; check each kept DEC whole section for implementation claims the plan deletes, not only its policy clause.
- 2026-11-23: gh label create (no --force) on an existing label prints "label with name X already exists; use --force ..." with no 422 (cli/cli pkg/cmd/label/create.go); a milestone-style 422 conjunction would reject the idempotent case.
- 2026-11-23: plan-merge check enforces a 50 machine-field-line budget per task (DEC-182); a literal file list in a verify heredoc blew it, derive the list from plan.yaml instead.
- 2026-11-23: an SC demanding variable X be absent from test support conflicts with a confinement that strips X by name; strip by prefix (GH_*) to satisfy both.
- 2026-11-23: Adding 4 file lines plus 8 verify lines to T-05 tipped it to 53 machine-field lines (budget 50); check FAILs only at check time, not at amend. Count headroom before appending verify assertions.
- 2026-11-23: Dispatch-named receipt path notes/receipt-amend-apply-*.txt is outside pm domain; pm can only write notes/receipt-harness-pm-*.md. tee to a permitted path works only with a literal absolute path (shell var refused).
- 2026-11-23: A fix that closes a failing-first gap with a red from a DIFFERENT failure point (pre-loop label create vs the plan's per-item close failure) discharges the SC's literal text but not the signed task's reading of the issue; grade both separately. A feature-intermediate commit that broke the policy is a legitimate free mutant.
