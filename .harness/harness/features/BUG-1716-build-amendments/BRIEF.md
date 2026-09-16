# BRIEF — BUG-1716 Build amendments

## Problem

During build, an engineering lead can learn that a signed task's `intent`, `files`, or `verify` text is incomplete or worse than the code needs while the signed success criteria, task set, and decisions remain intact. The lead must currently stop and send a fully reasoned answer through an operator round-trip and a product amendment run before the same task is dispatched again. BUG-285 measured this three times on one task: three blocked engineering runs, three product amendment runs, three operator round-trips, two cycles, and about $17 even though the operator adopted each recommendation.

## Done when — by perspective

**end user (engineering lead)** — I can make a more code-efficient or reliable correction to a signed task's how in the same run when it changes only `intent`, `files`, or `verify`, preserves every success criterion and the task set, and conforms to every recorded decision. I know to stop with a recommended question when any eligibility condition fails.

**orchestrator** — I can transcribe eligible amendments from the lead digest into the task text and judgement ledger with one command, without a product amend run or task re-dispatch. The signed approval survives and the continuation remains a run rather than consuming a cycle.

**operator** — I can audit signed task text against every recorded departure, overrule an amendment at ship on its ledger entry, and derive the amendment overrule rate from `judgements[]` rather than memory.

**reader (reviewer / qa)** — I can see where build departed from the signed how and independently decide whether each departure serves the signed success criteria and decisions. My coverage and quality checks remain anchored on the BRIEF, decisions, and reviewed diff rather than on amended task text.

**code maintainer** — I can rely on one closed digest shape, one controlled transcription route, one judgement vocabulary, one task-text hash definition, and explicit failure remedies across the scripts, schemas, tests, decisions, and operating instructions.

## Success criteria

- SC-01 (end user): An engineering-lead digest accepts `amendments: [{task, field, was, now, reason}]` only for task fields `intent`, `files`, and `verify`, with a reason of at most 240 characters, and refuses entries naming an SC or decision id; the lead instructions require all three eligibility conditions, same-run application, and `BLOCKED` with `open_questions` plus a recommendation for every ineligible change.
  verify: automated        evidence: integration
- SC-02 (orchestrator): `plan-merge.py record-amendments --digest <digest.md>` copies every eligible task-field value byte-for-byte from the digest, changes no other plan field, records the corresponding `amendment` judgement in the same invocation, preserves approved approval bytes, and requires no task re-dispatch or product transcription run.
  verify: automated        evidence: integration
- SC-03 (operator): Signing approval stores a deterministic SHA-256 for each task's `intent`, `files`, and `verify`; INV-40 reports an unrecorded post-signature text difference with its remedy and is silent after an amendment judgement names that task.
  verify: automated        evidence: integration
- SC-04 (operator): The controlled feature-record route marks exactly the selected amendment judgement `overruled: true`, refuses absent or ambiguous selections without mutation, and the ledger alone yields total amendments, overruled amendments, and their one-line rate.
  verify: automated        evidence: unit
- SC-05 (reader): At `review_sha`, Stage 1 reads each amendment as a departure from signed how and checks it against BRIEF success criteria plus `plan.yaml` decisions, producing a `substance` finding only when it does not serve them; Stage 1 never anchors on task text, while Stage 2 and `code-grade.py` remain recomputed from the reviewed diff by `validate-digest.py`.
  verify: inspection
- SC-06 (end user): Acceptance fixtures replay BUG-285 T-03's three recommendations—keyword-only text source with no second accessor or exemption, `parse_gh_json` accepting any JSON value, and `manifest_domains(agent=None)`—and classify all three as eligible amendments conforming to the recorded decisions with no new ask.
  verify: inspection
- SC-07 (code maintainer): At `review_sha`, DEC-23, DEC-32, DEC-157, DEC-229, and DEC-230 state the amendment authority, approval survival, run-not-cycle accounting, and six-kind ledger consistently, cite DEC-226 as precedent, and explicitly preserve the three task-text-independent cross-checks.
  verify: inspection

## Verification gaps

none.

## Constraints

- DEC-174 BLOCKS team execution for `validate-digest.py`, `plan-merge.py`, `feature-record.py`, `check-state.py`, and each of their tests; every such task is `main-session-direct` with an execution reason.
- DEC-223 SUPPLIES the closed digest contract: `amendments` must be declared rather than passed through as an ad hoc key.
- DEC-229 SUPPLIES the byte-preserving, orchestrator-runnable `record-panel --digest` precedent; its approval reset rule changes only for task-text amendments, while task-set changes still reset approval.
- DEC-230 SUPPLIES the append-only judgement ledger and the `BLOCKED` question-with-recommendation fallback; its exhaustive kind set gains `amendment` as the sixth kind.
- DEC-226 SUPPLIES the precedent for replacing repeated in-flight authorization with an auditable operator ruling at ship.
- DEC-157 SUPPLIES cycle accounting: because no gate failed, continuation after an eligible amendment is a run, not a rework cycle.
- DEC-23 and DEC-32 currently BLOCK builder-side task-text amendments; their current-truth wording must be reconciled without granting authority to change success criteria, the task set, or recorded decisions.
- `validate-digest.py` must never be re-anchored on task text. QA derives coverage from the BRIEF without source access; code-review Stage 1 reads the BRIEF and decisions; Stage 2 plus `code-grade.py` evaluates the reviewed diff.
- Every validator or mutation failure must leave its target byte-identical and name the rejected amendment and remedy.

## Out of scope

- Giving `fable-advisor` any seat in build — it was deliberately removed from the discussion.
- Generalizing prior `answers-*.md` rulings as precedent — a lead that proceeds has no repeated question.
- Letting the engineering lead change a `decisions:` entry or a success criterion — those remain DEC-23 and DEC-32 asks.
- Issue #1683's general top-level write route — `record-amendments` is task-scoped and independent of it.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-15
