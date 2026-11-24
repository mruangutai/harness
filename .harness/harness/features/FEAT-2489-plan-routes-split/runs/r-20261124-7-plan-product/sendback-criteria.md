# Send-back criteria — apply c4 (written before dispatch, P-05)

Cycle-4 records in plan.yaml panel: PF-daf9c8a84d9cf8f0da611c26b91877eb (high, SC-02 W3),
PF-13006fd231e087314c1651e5679503d0 (med, T-02 lookalike token), PF-c01acc578f91cbed233d9afea356eea7
(med, T-04 MAP subset), PF-a4d2a5fd9eb5b8976b8ae883e1c4e624 (low form, T-01 prose).

Lead composition check (P-15): "unmodelled text compared exactly" and "a moved traceback frame FAILs" are
the same rule — an identical frame passes exact comparison, a moved one differs and FAILs. T-02 verify
asserts no 'Traceback' in the checker's own output; the sampled states print none, so no conflict, but
pm must not make the checker print tracebacks of its own.

Send back if any holds:

1. SC-02 item 5 still keys on the FIRST site a diagnostic names, or does not name Python traceback frames
   (`File "...", line N, in NAME`) as in the class; or it lets frame/site order or any non-locator byte change;
   or it takes the excluded-crash-traceback alternative.
2. W1 (producer-order exception) or W2 (retained-site line shift) wording changed beyond what (1) forces.
3. BRIEF's disclosed-departure note does not describe item 5 as it now reads, in one place, readable cold.
4. T-02 rewrite still applies to the leftmost lookalike match on any line, rather than the locator field of
   enumerated recognized diagnostic formats; a plan-read error echoing an input value is not compared exactly;
   or the text does not say unmodelled differences (traceback frames if unmodelled) FAIL.
5. T-04 verify still uses a subset (`<=`) for MAP lines; it must require the receipt's ordered MAP block to
   equal the live run's.
6. T-01 receipt prose near the checkpoint still names only canonical_reader_audit.py.
7. Ruled scope touched: SC numbering, new task, AST-identity checker, permanent equivalence test,
   approval.status (must stay pending), anything closed at c2-c4.
8. plan-merge.py check failures > 0; PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb not recorded resolved; any applied
   substance finding marked resolved; any PF id missing from the reported disposition list.
