# Seam ruling by delegated authority — FEAT-2397 — 2026-11-22 — misnamed validate run

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC9RunId`).

**Gap.** Main opened the validator run as `r-20261122-4-validate`, in an unpushed local commit
(`e54a4a35`). dispatch-guard then refused the `harness-validator-lead` start. The lead's run-dir
grant is `.harness/*/features/*/runs/*-validator/**`, so the run id must end in `-validator`. The
lead never started: there was no claim, no run dir and no digest.

**Ruling: A.** Drop the unpushed commit with `git reset --keep 4adf77ce` and open
`r-20261122-4-validate-validator`, the same shape FEAT-2337 used.

A BLOCKED close with `--refused-return` would be false. That form records a host refusing a
lead's final return, which needs a lead execution and a digest, and neither occurred. It would
also add a phantom run to the INV-22 run count.

The guard's "deleting runs[] entries is no substitute" protects runs that represent real events.
This entry was never dispatched and was never in any pushed history.
