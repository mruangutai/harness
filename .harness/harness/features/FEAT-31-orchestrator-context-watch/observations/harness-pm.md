# Observations — harness-pm — FEAT-31

- 2026-08-21: plan.yaml plain scalars broke safe_load three times in a row on a colon-space inside
  prose (decisions[].choice, decisions[].because) — "two lanes: T-03 writes...", "by hand: a
  running...". YAML reads it as a nested mapping. Fix is an em dash. Worth a pre-return regex over
  the file — any line matching ^\s*(- )?[a-z_]+: \S.*:\s — which catches every one before
  check-plan-routes.py does, and each round trip through the checker cost a Bash call.
- 2026-08-21: check-plan-routes.py with no argument reports over EVERY live plan, so DEVIATION
  lines from other features appear in the output. Read the trailing block for your own plan; the
  summary line is the only global fact.
- 2026-08-21: bash-write-guard blocks a heredoc redirect into my own observations log; the Write
  tool is the only route. Appending therefore means Read-then-Write, not >>.
