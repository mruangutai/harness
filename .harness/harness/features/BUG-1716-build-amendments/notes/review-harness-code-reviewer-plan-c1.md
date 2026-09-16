# Scope and architecture review — BUG-1716-build-amendments

PASS. The draft has no orphan success criteria or task traces, no task without a live requirement, and no missing settled requirement. The dependency graph is acyclic and operationally topological even though T-09 is listed before T-07/T-08: its explicit `depends_on` holds it until T-05 through T-08 complete. Predecessor changes do not invalidate downstream verification blocks.

DEC-174 routing is exact for the four named gate scripts and their changed tests: T-02 (`validate-digest.py`), T-03 (`feature-record.py`), T-04 (`plan-merge.py`), and T-05 (`check-state.py`) are each isolated `main-session-direct` tasks with execution reasons. No task mixes those gate surfaces with a team route. The prose and skill work is separately tasked; keeping those tasks main-session-direct because the resolved surfaces have no team grant is allowed by the operator's “may use team routes,” not a routing violation.

The plan covers the same-run eligibility boundary and fallback, the closed digest contract, one-command byte-preserving transcription without redispatch, the sixth judgement kind and exact-entry overrule, signed task-text hashes and INV-40, validation independent of task text, run-not-cycle accounting, and the three BUG-285 returns in both digest and transcription fixtures. SC-01 through SC-07 are each traced by at least one task, and every task serves a traced SC.

Architecture is proportionate. `record-amendments` is a deep mutation interface that centralizes validation, compare-and-splice, cross-file atomicity, and ledger append. `overrule-amendment` is the narrow ledger seam. Hash production is owned by signing and verification is explicitly required to use the identical canonical definition; no second public adapter or speculative seam is introduced. The split preserves locality around each existing enforcement script while dependencies connect the cross-script contract.

No substantive, form, or proportionality finding.
