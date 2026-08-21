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
- 2026-08-21 (plan2b run): the SECOND hazard of the colon-space break is that it is invisible to a
  reader. I opened plan.yaml while the predecessor was still writing it: `wc -l` said 190 and
  `cat -n` stopped mid-T-01, then 90 seconds later the same file was 514 lines and had gone from
  safe_load FAILING to parsing. A `cat` of a plan mid-write looks like a *short plan*, not a
  truncated read — I nearly reported "only T-01 exists" as a finding. Sample size+md5 twice before
  reasoning about a plan's task set.
- 2026-08-21 (plan2b run): transcript mtime under ~/.claude/projects is NOT a liveness signal on
  this machine — `find -newermt -6M` over every *.jsonl returned zero, including my own session
  while it was actively running. To tell whether a sibling agent is still writing, sample the
  artifact's md5, and look for its observations log (which the predecessor writes near the end).
- 2026-08-21 (plan2b run): a dispatch's description of an artifact is the input most likely to be
  wrong. Mine asserted line count, task range, decision range and a `uat:` block, and was wrong on
  all four; it also asserted "zero grep hits" for a string that had three. Re-derive every
  structural claim from the file before treating any of it as a gap.
- 2026-08-21 (plan2b run): before inventing a top-level plan.yaml key because a dispatch names one,
  grep templates/plan.yaml AND every live plan AND check-state.sh for it. `uat:` appears in none of
  them, so writing it would have parked a narrowed criterion in a key no gate reads. This plan
  records no-task UAT routings as a D-NN instead (D-12).
