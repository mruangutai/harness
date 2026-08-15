# Observations — harness-orchestrator — FEAT-17-guard-boundaries

- 2026-08-12: TWICE in one feature I asserted "working tree clean" in a dispatch while my own
  uncommitted `review_sha` pin sat in feature.json. Both the goal-check lead and the qa lead caught
  it and flagged it back — correctly, since a dispatch premise that is asserted rather than measured
  is exactly what the members are told not to trust. The pin is written seconds before the dispatch,
  so the window is self-inflicted every time. Commit the pin, or say "tree carries my pin and
  nothing else", before claiming cleanliness. Cost: two flagged premises and a paragraph of
  re-derivation in each digest.

- 2026-08-12: The DEC-174 carve-out splits ASSESSMENT from CHANGE, and that split is what let a
  review panel run at all on the four gate files. Dispatching "review, and nobody fixes — findings
  come back to the operator" was accepted cleanly by the validator lead. The failure mode to avoid
  is reading the carve-out as forbidding the panel outright: that would have shipped a high finding
  unfound. But it also means a panel FAIL has NO lead to route the fix to, so the routing table's
  FAIL row is a dead end and the return is ESCALATE.

- 2026-08-12: Running the qa gate and the review panel CONCURRENTLY cost one real thing: the panel
  could not hand its unfalsifiable claim to qa mid-run (issue #284's usual workaround). I pre-empted
  it by telling the panel to NAME the claim and the fixture it needed, and committing to sequence
  the probing myself. That worked — the gap arrived named rather than silent. But the two runs then
  each carried a blind spot the other closed (panel ran no tests; qa was single-member and audited
  no spec/security/UI), and reconciling that was mine to do at no spawn cost.

- 2026-08-12: My P-06 (verify a panel's central premise before it costs a cycle) paid off in the
  opposite direction this time — both high/med findings were REAL and reading them at source made
  the relay stronger, not cheaper. F-B was actually WORSE than the operator's hypothesis: they asked
  whether a fourth import route exits 1 instead of 2, and check-state.sh exits 0 while printing
  "all state invariants hold". Verifying let me say that upgrade in my own voice.
