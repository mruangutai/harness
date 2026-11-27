# Run 05 acceptance criteria (written before any return)

Source: notes/answers-2026-11-27-04-plan-product.md (Q-R4-1). No reader runs; send back only on these.

- T-01: plan.yaml T-01 intent AND verify require EVERY Run A / Run C invocation's own matched flag to be true for a passing receipt; equal log/matched totals alone never pass. Leak reporting (refused payload reaching the parent) still evaluates before the match/classification step. Grep token: a per-invocation matched check in verify (not only a totals comparison).
- T-02: each batch target in T-02 carries a DISTINCT task literal, and each per-target tool_input assertion (toStrictEqual) names that target's own literal. Grep token: two different task strings in T-02 batch witnesses; no shared 'probe' across both targets.
- Dispositions (schema has only open|resolved): PF-cbf8dece633693ce07ab5a284be1a0cf, PF-25a87adffad1fd1f463f52b21ddb5b3e, PF-3e23c499bba318c133baf80026c1592a -> resolved, resolved_by T-01. PF-120f5374d27296822e9d10ea9d8adab9, PF-50024d3fe46e0d0aeb31788c55e947bf -> resolved, resolved_by T-02. The supersession (cbf8/25a8 by 3e23; 120f by 5002) is recorded in pm's note. No other disposition changes.
- Plan-merge verbs only (apply / set-panel / record-panel / check); record-panel --cycle 4 --digest runs/2026-11-27-05-plan-product/panel-c4.md exit 0; check exit 0; approval.status pending.
- Gate: after the pass, no panel finding with severity high, critical or unrated is open.
