# FEAT-2225 — scoped plan re-review, c2

**PASS — PF-35d0f7a433ed64af6ae1c772dbc21e87 closes in the applied proposal; no new substance defect found in T-04.** This is a pending-plan verdict, not implementation approval or evidence that enforcement already works.

## Stage 1 — applied-text compliance

- Independently read the prior finding, panel-c1 and application note, then assessed the actual BRIEF SC-05, D-03 and T-04 text. Closure does not rely on the PM's resolved disposition.
- **SC-05:** `BRIEF.md:25` explicitly requires DEC-220's owner/binding/mirror-receipt predicate before internal synchronous gh merge, including refusal of replay-valid missing, wrong-repository and recovery-required build-entry evidence.
- **D-03:** `plan.yaml:140-142` puts that existing predicate inside the same owner-root lock as fresh head/base, replay and synchronous merge, and explicitly rejects reliance on another host Bash event.
- **T-04:** `plan.yaml:255` now requires existing owner resolution and `_handle_owners`/`_enforce_receipt`, with `resolve_binding`, `mirror_evidence_problems` and `receipt_allows_merge`, before internal gh. It requires one unambiguous owner matching feature/PR, retains historical-feature and recovery-required refusals, rejects replay-only authorization, and forbids an internal-subprocess exemption. `plan.yaml:256` preserves ordinary merge behavior and applies distill recognition to git/gh and Main.
- **Discriminating verification design:** `plan.yaml:257` independently requires replay-valid candidates with missing receipt, wrong-repository evidence and recovery-required receipt to refuse before fake gh executes, with existing recovery guidance; a valid same-owner/binding/mirror receipt must permit merge. These are planned assertions, not executed tests.

## Stage 2 — existing seam and no-new-defect assessment

The applied predicate matches DEC-220's “One binding and receipt predicate” (`/Users/molchairuangutai/GitHub/harness/.harness/harness/docs/DECISIONS.md:7183-7197`). Existing code resolves authoritative binding, checks immutable mirror evidence and gates receipt status/provenance (`/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/merge-gate.py:248-285`; `feature_schema.py:500-525,560-590,632-647` in that same bin directory). Reuse avoids a second policy; explicit unique-owner matching prevents inheriting `_handle_owners`' ordinary zero-owner allowance. The task requires actual refusal before merge, not merely calling a hook helper that prints a deny response.

No new substance defect found in T-04's applied text: authority, close/replay integrity, preserved Write/grants, synchronous locking and terminal verification requirements remain coherent with this correction. No unrelated task, should-not-exist/design/goalcheck review or redraft performed. No diff, tests, builds, lint, formatters or approval/signature actions; plan-phase review has no pinned production SHA (`feature.json:5`; `plan.yaml:3-6`). SC-06 implementation inspection remains outside this narrowly assigned re-review.

## Open questions

None. Findings: none. Must-fix: none.
