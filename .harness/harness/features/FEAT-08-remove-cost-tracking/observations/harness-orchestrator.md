# Observations — harness-orchestrator — FEAT-08-remove-cost-tracking

- 2026-08-05: The cost reporter is cumulative over a RETENTION WINDOW, not over project
  history, so the top-line total can DECREASE between runs as old transcripts age out.
  Baselining by "the largest prior total" picked FEAT-04's block (6735.17) over today's
  (6057.34) and produced a nonsense -677.84 delta. Sorting metered blocks by `priced_on`
  then mtime and diffing `by_agent` gave the real 237.73. P-01 says diff `by_agent`, not
  the top line; it does not say how to CHOOSE the baseline, and that is where it broke.

- 2026-08-05: A coordinator sent three successive corrections on one mechanism (the
  DECISIONS-INDEX supersession marker), each contradicting the last, the third read off
  the generator source. Verifying the third at source BEFORE dispatching a fix showed pm's
  plan was already correct and in fact sharper than the correction — the false sentence is
  the ruling PROSE, which the generated marker never touches, so the marker could not have
  fixed the criterion at all. A relayed correction is a claim, not a measurement; P-06's
  verify-the-premise rule applies to corrections from ABOVE, not just findings from below.
  Cost of checking: two greps and one 6-line probe. Cost of not checking: a fix cycle that
  would have made the plan worse.

- 2026-08-05: The empirical probe that decided task ORDER took 8 lines and settled a
  question three prose sources had left open: `validate-digest.py` REQUIRES `cost_usd` but
  IGNORES unknown keys, so the removal hazard is one-directional (loosen the gate first,
  remove the producer second). Reading the schema dict would have shown the requirement but
  NOT the extras tolerance — that only came from running it. In a self-hosted repo the
  running gates are the thing under change, so ordering constraints are measurable rather
  than arguable, and PLAN should carry them as decisions rather than discovering them.

- 2026-08-05: My dispatch's "18 files" surface count was a floor for ONE grep pattern.
  Widening it added three false positives (duplicate-key YAML fixtures) but the real find
  came from a DIFFERENT direction — `.harness/README.md`, which the sweep never covered
  because the pattern set did, and which CLAUDE.md names as the layout authority. Four cost
  references there, including an INV-11 description. Handing pm the widened sweep AND an
  explicit LEAVE list for the near-misses meant zero spawn time spent re-judging them.

- 2026-08-05: A concurrent flow (FEAT-09-plan-time-route-check) has BRIEF.md and PLAN.md
  but no feature.yaml and no STATE.md, so `check-state.sh` reports its unapproved BRIEF
  alongside mine. Two flows in plan phase therefore make the shared gate read 2 VIOLATIONs
  when both are simply pending signature. The gate cannot distinguish "pending terminus"
  from "regression", so an orchestrator must state which its own violations are rather than
  reporting the exit code.

- 2026-08-05: product-lead's send-back was worth its spawn — it caught T-08 editing
  `teams/*.yaml`, which `test-harness-yaml-corpus.py` scans LIVE, with no clause invoking
  that test; pm's own re-audit then found the same shape in T-06, T-07 and T-10. G-12
  existed and was in my dispatch as a binding instruction, and pm STILL missed it on four
  tasks. Stating the rule is not enough; the lead re-deriving which files a live test reads
  is what caught it.

- 2026-08-05 (ship successor): the handoff's `## Trust` line "check-state.sh zero
  violations — verified-at ae2443d" was FALSE on arrival and TRUE forty minutes later, at
  the same SHA, with nothing of FEAT-08 changed between. A concurrent flow signed its BRIEF
  in the gap. So a repo-wide gate's verdict is not a property of the SHA at all, and a
  handoff note pricing it as verified-at-a-SHA is mispricing the claim's kind, not its
  truth. Both readings were captured verbatim rather than one being taken as the baseline.

- 2026-08-05 (ship successor): three SC numbers looked falsified on arrival — 89 vs 96 cost
  lines, 67-of-67 vs 69-of-69. Every one reconciled EXACTLY once the glob was restricted to
  the seven features that existed at approval, which the BRIEF itself names one criterion
  earlier. The apparent drift was two in-flight feature dirs the glob also catches. The
  cheap wrong move — declaring the criterion unmeetable and routing a re-plan — was one
  restricted grep away from being disproved, and the criterion's POPULATION, not its number,
  was the thing that had gone unstated.

- 2026-08-05 (ship successor): a whole-file rewrite of `feature.yaml` to repair four stale
  fields silently dropped the predecessor's `resolved:` block, and with it two of the five
  lines that a success criterion COUNTS. Nothing warned; the file parsed and the gate passed.
  Whole-file writes over a file that other criteria measure by line count need the count
  re-measured after the write, the same way an edit to a generated artifact needs the whole
  unit suite.
