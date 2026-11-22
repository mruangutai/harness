# Goal-check — FEAT-2297

FAIL: SC-08 still lacks literal operator-personal review; SC-01 has a confirmed invalid-input acceptance defect. Required integration evidence remains red. Final QA resolves the former missing-measurement question; reduction passes the signed D-06 gates.

Supplementary reconciliation within run `validate-validator`, not a second goal-check cycle. Review pin `47d2e50243ad7fb080e13ef48115756d7d3b7c61`; base `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568`. No source/test changes or suite/checker reruns by PM. Original pinned inspection references are retained below. QA evidence is `notes/review-harness-qa-c1.md` (abbreviated QA below), including its terminal-newline supplement. BRIEF, plan D-01–D-08 and feature.json signed amendments govern.

## Perspectives

- **operator — partial:** reader refusal and upgrade evidence exists (SC-02/03), but invalid repo whitespace is accepted (SC-01), and advisor authorization does not establish personal review (SC-08).
- **code maintainer — met:** SC-04 fixture/census proof and SC-05 measured reduction discharge the outcomes under amended D-06. Stale committed measurement text remains a form defect, not missing measurement.
- **reader — partial:** concrete unit/integration and disposition evidence exists, but required integration is red and the change receipt's Kaya pointer is broken (SC-07/09/10).

Every perspective has traced tasks: operator T-01/03/09; code maintainer T-02/04–07/10; reader T-03/08/10. Coverage is complete; discharge is not.

## SC outcomes

| SC | Verdict | Method / concrete evidence |
|---|---|---|
| SC-01 | partial | automated: QA:38–44 unit 65/65 production-runner receipt; QA:77 loader fail-first (52 failures/4 errors). QA:113–121 confirms github.repo='acme/repo\n' accepted, contrary to the no-whitespace contract implicated by D-03/present-invalid refusal. QA F-03 also identifies absent non-object-root test coverage, though probes refuse those roots. |
| SC-02 | met | automated: QA:78 readers fail-first (62 failures/2 errors), QA:38–59 final integration results: reader suite passes, sole red is test-corpus-real-owner.py against v2 host owner. Targeted Readers/RemoteProductConfig/Gates/CheckState assertions cover refusal and preserved policies; that separate required-kind red is not waived. |
| SC-03 | partial | automated: QA:79 upgrade fail-first (4 failures/1 error), final upgrade file passes. QA F-04: missing/unparseable repair-source behavior holds in probes but no test asserts that explicit clause. |
| SC-04 | met | automated: QA:80 builder/census five-bypass red; completed fixture suite passes within 94 successful integration files. Checked freshness and delegated writers are covered by that census suite. |
| SC-05 | met | automated: QA:81,86–89 scratch checker and negative controls at actual pin/base: Gate A -583, 152 disposed rows, 67 assessed files; Gate B +1557, total +974 reported. Signed D-06/feature.json amendments replace total-negative gating; no new amendment needed. Historical committed receipt is stale, not proof of measurement absence. |
| SC-06 | met | automated: QA:82 wrong-route baseline exit 2; candidate audit exit 0, zero unresolved across 101 Python files; passing readers GenericReads cases carry non-config regression. Audit is separate CI evidence, not falsely counted as a matrix suite. |
| SC-07 | partial | inspection: original pinned references: DECISIONS.md:8472–8534, SPEC.md:91–118,187,1431–1441, templates/README.md:30–47 and checkout-upgrade.md:15–24 align. However changes-config-contract.md points to absent receipts/t09-kaya.txt rather than actual notes/uat-kaya-migration.md; documentary traceability is incomplete. Both DEC amendments below are met. |
| SC-08 | not_met | uat: notes/uat-kaya-migration.md, Review and authorization / Landing; QA F-02. kaya#29 merged b9dec8df1de9c065bca3122c371a206d6f46c048 with advisor AmendmentRuling authorization under standing delegation and validated remote-main v3/statuses. Receipt explicitly disclaims operator-personal review. BRIEF verification gap/T-09 require it; landing is established, personal acceptance is not. |
| SC-09 | partial | automated: QA:38–44 unit 65/65; QA:83 loader/review-evaluation/board-normalization fail-first. Preserved cases green on base are not falsely called new-behavior reds. Integration clause remains qualified by QA:51–59 required real-owner red. |
| SC-10 | partial | automated: QA:39,51–59 final integration 94/95, test-corpus-real-owner.py exit 1 against v2 host. QA:84 readers/branch/merge red-first proves new cross-process behavior; preserved cases pass, but required kind is not satisfied. Attribution is verified, not waiver. |

## Decision-disposition landing

- **Row 9 (zero-based 8), DEC-221 amend → D-08: met.** Pin `47d2e50243ad7fb080e13ef48115756d7d3b7c61`, `.harness/harness/docs/DECISIONS.md:7311–7315`: best-effort transport plus strict Python refusal, only DEC-198 TypeScript leniency. T-08 owns remediation; none missing here.
- **Row 10 (zero-based 9), DEC-254 amend → D-02: met.** Same pin/path:8357–8367: absent=null replaces omission exemption; activation, drafted_at eligibility and grandfathering retained. T-08/T-10 own that file.
- Eight keep rows are not graded. DEC-256:8501–8509,8523–8534 records amended D-06/retirement; D-07 still requires operator review.

## Findings and reconciliation

- **substance / high / T-09:** personal-review acceptance missing (SC-08). Main owns acceptance escalation; PM cannot substitute advisor authorization or mark UAT passed.
- **substance / med / T-01:** terminal-newline acceptance confirmed by QA:113–121 for github.repo='acme/repo\n' and excluded signed='DEC-187\n'. The repo case violates whitespace exclusion and therefore SC-01/D-03's invalid-present contract. The signed marker case is an additional schema-boundary defect, not evidence of a fresh policy waiver.
- **substance / high / main routing:** required integration red against real owner v2 remains a gate failure. Candidate schema v3 behavior and host installed state are distinct; no test weakening or automatic waiver is inferred.
- **substance / low / T-01:** QA F-03/F-04 identify explicit SC-01/03 test gaps; successful exploratory probes do not replace automated assertions.
- **form / low / T-10:** committed qa-config-reduction.md names historical 1b904355/837e7096. Withdraw the previous med missing-measurement concern: QA supplied current 47d2e502/9fd1f6b4 measurement. Refresh record text before citing it as the pinned receipt.
- **form / low / T-08:** change receipt's missing Kaya pointer must target actual notes/uat-kaya-migration.md without claiming personal review.
- D-06 Gate A/B, INV-13 retirement and deferred #2393 are settled, not findings.

## Open questions

1. Will the operator personally review/accept kaya#29 or explicitly amend that requirement? Blocking ship; Main/T-09 already owns escalation.
2. Former OQ-QA **resolved**: final manifests and scratch reduction are available (QA:38–44,86–89). Unit passes; integration remains red; reduction passes. No additional evidence collection or rerun is requested by this reconciliation.
