# Observations — harness-product-lead — FEAT-10-software-factory

- 2026-08-08 (seg6): dispatching two members in parallel onto PAIRED documents (pm on plan.yaml,
  visual-designer on DESIGN.md) created a cross-file divergence neither could see. I authorised
  visual-designer to fix the `factory_workspace` PONR row (DESIGN.md:113) as a cheap adjacent fix,
  while my pm dispatch excluded the same defect's plan.yaml half (:884). pm correctly declined and
  filed it as Q2. Result: two signable documents stating different points of no return for one
  tool — the exact MF-2 defect shape, introduced by the run that was fixing MF-2. Cost one
  send-back. The trigger to watch: an "adjacent, costs you nothing" fix authorised in ONE member's
  file when the defect has a half in another member's file.

- 2026-08-08 (seg6): the dispatch's site list for MF-2 named DESIGN.md:101 and plan.yaml:593. The
  third site (plan.yaml:571-572) was in the SAME LINE the validator quoted as evidence for the true
  half — "the first mutation is ensure_labels ... The point of no return is the first successful
  create_issue". A reviewer citing a line for one clause does not read the rest of it. Re-running
  the enumeration wide (grep `point of no return|first successful|first mutation`) found it in one
  pass and also proved the `_reason` site list complete.

- 2026-08-08 (seg6): pm returned `tasks: 13, decisions: 12` in its send-back digest and
  `tasks: 12, decisions: 13` in its first — transposed. Ground truth from the file is 12 tasks
  (T-01..T-12) and 13 decisions (D-01..D-13). Metadata counters in a member digest drift between
  returns from the same member in the same run; recount from the artifact rather than taking the
  later return as the correction.

- 2026-08-08 (seg6): pm emitted `sc_status: [{id: SC-14, verdict: not_met, ...}]` on a PRE-BUILD
  plan edit. Honest in substance ("unbuilt, no test exists yet") but it is not a goal-check verdict,
  and every SC is unbuilt at this stage. Passing it up would read as a failed criterion. Dropped to
  `[]` with the reason stated.
