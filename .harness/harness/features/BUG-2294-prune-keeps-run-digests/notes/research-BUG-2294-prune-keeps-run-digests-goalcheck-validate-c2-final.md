# Final goal-check c2 — BUG-2294

PASS at 88bf039f6ff31edbb1d5a4b2f6620762e3cc095a. Both perspectives pass; SC-01–03 and DEC-238 amendment are met. This supplements, without rewriting, research-BUG-2294-prune-keeps-run-digests-goalcheck-validate-c2.md: its SC-01/operator partial was conditional on independent QA execution, now supplied. No PM tests or implementation changes; this is evidence completion within c2.

## Perspectives and criteria

- **operator — pass:** SC-01 plus unchanged-policy evidence in SC-03 discharge durable-record preservation, safe UI pruning and unchanged invocation. T-01 traces all three SCs (plan.yaml:66–79).
- **code maintainer — pass:** SC-02 supplies the discriminating empty-keep/final-BLOCKED/no-UI regression; SC-03 supplies matching instructions and decision text.
- **SC-01 — met, automated:** review-harness-qa-c2.md:28–45 records independent execution at the exact pin: literal T-01 verify, python3 tests/unit/test-prune-run-evidence.py, 25 PASS / 0 FAIL, rc 0, 0.93 s; the unit runner includes that file among 63 passing files, rc 0. Its :34–35 audits the base c1724230 natural RED: seven semantic assertion failures including the three record-byte checks, not setup/import failures. Its :37–44 distinguishes four semantic symlink RED failures against 70981edd from five passing checks at the pin, with real-UI positive deletion and nonempty destination-byte comparisons. Subject/test hash matching (:8–15) binds receipts to the pin but is not itself execution; current-pin execution closes that former gap. Security's original raiser independently closes SEC-01 statically at review-harness-security-reviewer-c2.md:3–16.
- **SC-02 — met, automated:** QA :29–36 confirms the current-pin passing suite and audits the natural base RED: all ten cycle-evidence digests lost and post-prune INV-7 failed, while clean-before and empty-keep preconditions passed. This proves the required failure scenario rather than an incidental setup failure. Existing initial-note pointers to pinned tests/unit/test-prune-run-evidence.py:197–253 remain applicable. The approved feature-scoped INV-7 boundary is unchanged.
- **SC-03 — met, inspection:** initial note's pinned inspection remains valid: prune-run-evidence.py:12–17,120–146 and harness-ship.md:38–54; unchanged selectors, keep/refusal/CLI and both ship invocations/placement, with UI-only retention prose. Security c2 :26 corroborates unchanged-policy inspection. No automated execution is substituted for this inspection criterion.

## Decision disposition

**DEC-238 / amend / clause “it deletes engineering, product, reconciliation and distill run directories” / successor D-01 — met, inspection.** Direct git show at 88bf039f6ff31edbb1d5a4b2f6620762e3cc095a:.harness/harness/docs/DECISIONS.md:7990–7998 confirms the replacement current text: UI-only deletion, protected run directory/digest.md/state.yaml/.run-identity.json, #2177 rationale and retained selection/refusals. Abandon/INV-51 remains at :7986–7989; disposable-pin text follows at :7999. Initial note retains the index and unchanged-clause inspection. T-01 owns both decision files; keep dispositions are not graded.

## Limits and open questions

No unmet criterion or remediation. QA natural RED evidence is receipt-audited, not freshly rerun; green execution is independent at this pin. Security's SEC-C2-Q1 remains nonblocking: whether to separately authorize/reject linked ancestors and traversal-bearing feature selection, and define concurrent-writer expectations (security c2 :18–22). This pre-existing boundary does not reopen SEC-01 or expand T-01. Any actual T-01 remediation remains Main/main-session-direct. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no guidance invented. No UAT required.
