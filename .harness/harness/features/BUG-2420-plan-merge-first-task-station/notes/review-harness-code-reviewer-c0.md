# PASS — first-station writer; one non-blocking test-oracle finding

Reviewed `d5be53927009df8e7848f860f9d0b4b03b89f9ad..c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`, restricted to T-01's three source/test paths. Dispatch and feature.json pins agree. Git status was clean; the three range commits contain no `[harness:human]` attribution. Default-branch merge-base is `9eb07b4f3cd235c234a10edddbfe5542c1e85fba`; the assigned pre-fix base is the later build-entry commit.

## Stage 1 — specification: PASS

Read BRIEF SC-01..03, signed T-01 and empty decisions, settled signoff/correction notes, product SPEC §2.2–2.3 and DEC-120/174/225 before judging compliance. No scope creep or production-behavior mismatch found; no build amendments were reported.

- SC-01: stations.py:193–299 distinguishes missing task from missing own status, derives field indentation from the id column, bounds discovery to tasks and the next sibling, inserts below the id, and retains the existing rewrite shape and STATION/APPLIED output. Unit rows at tests/unit/test-plan-merge-first-station.py:90–115 exercise all three outcomes. Nested verify prose remains untouched.
- SC-02: unit:144–154 requires successful insertion plus the complete original APPROVAL substring (including approved status); stations.py:258–267 splices task lines without serializing approval.
- SC-03: tests/integration/test-plan-merge.py:5142–5165 applies into tasks: [], checks the exact status-less task mapping, sets building and reloads it. Apply production code is unchanged.
- Lock/update inspection: stations.py:278–290 transforms the bytes supplied inside the existing lock; guards.py:229–234 retains feedback after release, and harness_merge.py:141–179 retains atomic replacement. Absent-task handling preserves content, although the unchanged shared writer still replaces identical bytes.

## Stage 2 — quality: PASS with advisory

**F1 — med / substance / owner T-01:** unit:84–87,108 uses membership-based line differences, losing order and multiplicity. Concrete reasoned scenario: a writer regression swapping T-01 and T-02 title lines while correctly rewriting T-02's status passes this row's “every other byte” assertion, despite assigning each task the other's title. The other unit assertions do not inspect titles. Prefer comparing the complete expected output (and exact original bytes for refusal). This is an oracle weakness, not an observed production corruption; non-blocking, no must-fix.

Captured red/green evidence binds the same unit/integration blobs as the pinned diff. Red distinguishes nested-prose corruption, plain insertion refusal, and the approval assertion's success prerequisite; rewrite/missing-id controls stay green. Green receipt reports both scripts passing and 12 graded records, production grades 4 and test grades 3–5, with no ungraded paths. Source complexity remains local and bounded; no new abstraction seam is needed.

## Principles applied

- Model the Domain: the station-site result separates absent task, present status-less task and existing status without parallel presence booleans; exact field indentation encodes ownership locally.

## Limitations and open questions

No tests, builds, linters, formatters, mutants or grading commands were run, as assigned; captured results are evidence inputs, not independent execution. F1's mutant is reasoned, not measured. Final pinned verification belongs to Gate QA. Red integration receipt contains failure excerpts rather than the complete stream. No open questions.
