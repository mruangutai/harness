# Merge ruling by delegated authority — FEAT-2337 — 2026-11-22 — post-validate CI fix

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorB7PostValidate`).

**Question.** After validate c2 (ESCALATE per `notes/answers-2026-11-22-manifest-gate.md`, pinned
at 9d9d940b), main merged origin/main (746a61ab, including FEAT-2257's required typecheck, which
passes) and opened PR #2391. PR CI's `checks` job failed the canonical-reader audit: the T-02
receipt reader `validate-digest.py::_read_receipt` used raw `json.loads`. The fix, b2151327 (built
test-first, evidence in `notes/ci-reader-audit-red-green.md`), decodes through
`artifact_accessors.strict_json_loads`. That only tightens behaviour: a receipt with a repeated key
is now Malformed and refused. Re-validate, or merge on CI?

**Ruling: A.** Merge on fully green PR CI; there is no validate c3. The c2 ruling already makes
clean-checkout PR CI the binding verifier, and that CI exercises both the receipt suite, with the
new row, and the head merged with main. The runner writes only strings and ints through
`json.dump`, so the stricter decode cannot refuse a legitimate receipt.

**Conditions.**
1. The green is on a head that includes b2151327 and the merge with main: the `checks` job
   (including the canonical-reader audit) and the integration result. Any red reopens the gate;
   nothing is relabelled.
2. This ruling is the `decided_by` for the CI-forced rework, and the ledger's `rework_rounds`
   reads 1 of 2 (one `regate` judgement).
3. Scope guard: A covers b2151327 only. If any further production change is needed to get CI
   green, A is void, and validate c3 (QA plus code reviewer at a new pin) runs before the merge.
