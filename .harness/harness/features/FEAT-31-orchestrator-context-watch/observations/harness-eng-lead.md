# Observations — harness-eng-lead — FEAT-31

- 2026-08-22: simplify-eng. Sent the four angle dispatches in one message and passed
  `model: sonnet` on all four; `dispatch-guard.sh` blocked all four identically. This is
  exactly my own recorded G-16 (a habit error in a fan-out wave is multiplied by N, and a
  lesson recorded only in a log I never re-read mid-run will not prevent it). The Expertise
  entry existed, was in my context at spawn, and did not fire. The guard caught it, so the
  cost was one wasted turn rather than four mis-modelled runs — the enforcement layer is
  what actually held here, not my memory.

- 2026-08-22: REUSE's finding on the `"harness-orchestrator"` literal splits cleanly into a
  mechanical half (bind two compare sites at context-watch.py:301 and :599 to one module
  constant) and a structural half (extract the four-level walk shared by
  `discover_orchestrator_rows` and `_orchestrator_jsonl_paths`). I verified the site set
  myself with grep before authorizing anything: exactly two behavioural compares in the
  library, plus `context-watch-hook.py:41` which already uses a named constant
  (`IN_SCOPE_AGENT_TYPE`) and keys on the payload's `agent_type`, not meta's `agentType` —
  so a cross-file constant would unify the value, never the compare. The correct pattern
  already exists in the sibling file; the library is the one lacking it.

- 2026-08-22: the walk-extraction half is a ~34-line rewrite of the discovery path — the
  exact code where this feature's two escaping defects lived. Under the simplify pass's
  one-fix ceiling, at the last build step before `review_sha` pins, a refactor whose blast
  radius is the defect-bearing path is the wrong trade even when the finding is correct.
  Recorded here because the reasoning is about WHEN a correct finding should not be applied,
  which is the judgement this step exists to make.

- 2026-08-22: ALTITUDE's F1 recommended fold-in on that same extraction and I declined it,
  on evidence ALTITUDE itself supplied: the two walks ALREADY DIVERGE on error handling —
  `discover_orchestrator_rows` routes a malformed meta through `_unmeasured_row` (feeding
  `unmeasured_count`, a REQ-07 surface) while `_orchestrator_jsonl_paths` silently
  `continue`s. Unifying them therefore CHANGES an observable REQ-07 number that no standing
  assertion pins — so the suites could stay green while the footer's reported counts move.
  A "simplification" whose fix silently alters a reported number is the one shape this pass
  must not apply. The generalisable form: a duplication finding whose two copies already
  disagree is not a simplification, it is a behaviour question wearing a simplification's
  clothes.

- 2026-08-22: cross-angle finding nobody was assigned, found by reading across the four
  receipts (my own G-13 paying off). `context-watch-hook.py:19-20` states 3359 tool_use
  events / 94.8% matcher coverage; `plan.yaml`'s signed D-25 states 3280 / 93.9%. Both are
  internally consistent (each one's component counts sum to its own total), so neither is
  false — the corpus is "the 25 most recently modified orchestrator transcripts", which
  moves as the machine is used, and NEITHER statement says the corpus is time-varying. Two
  honest measurements of a moving set read as a contradiction to anyone who compares them.
  No decision turns on the gap (both support the same conclusion), so it is a briefing row,
  not a fix.
