# Observations — harness-dev-ops — FEAT-53-metrics-dashboard

- 2026-09-17: A task-local wrapper can preserve the native pool transcript while grading only its adapter markers; retain CI’s direct native-runner exit so unrelated failures remain visible.
- 2026-09-17: The native pools can fail on committed dashboard artifacts or fixture isolation even when the client Vitest aggregate passes; retain separate unmasked runner evidence and classify each failure by its reported target.
