# BUG-2003 goalcheck — validate c0

FAIL: all perspectives are traced by T-01, but SC-03 is only partially evidenced at review pin 85038f8c1acbb38e2b6f758540941bc5cfdaf1ba. No tests or builders were run by this reader.

## Delivered perspectives

- **operator — partial** (SC-01 met; SC-03 partial): committed tests/unit/omp-hooks.test.ts:1054–1064 exercise both allowed destinations through write/edit pre/post with no domain calls; :1093–1110 prove the mixed-edit refusal. receipt-t01-fail-first.txt:3,6 names their red state; receipt-t01-pass.txt:3–8 records 106 pass, zero fail and literal verify exit 0. Ordinary write payload controls (:1112–1123) and main-session pre-write controls (:1125–1137) pass, but do not cover every promised regression clause below.
- **security/harness owner — pass** (SC-02, SC-04 met): committed tests :1014–1018,1066–1091 enumerate refused schemes/device suffix, both routes/stages, named refusals and no URI domain calls, including pre-edit MV; fail-first receipt :4–5 and pass receipt :5 establish discrimination. Committed adapter domainTarget → fileDomain is the single decision for input.path and every extractEditPaths section/MV destination; preDomain and postDomain both delegate to fileDomain. Allowed targets skip only their own gate; refused targets produce blocking results without resolution. SC-04 was graded from the required git show of the pin, not working source.
- **code maintainer — pass** (SC-05 met): committed tests :1012–1137 cover allowed/refused URIs, out-of-domain mixed edits and pre/post callbacks. Fail-first receipt records four named new failures and 102 unchanged passes; pass receipt records 106 passes and identifies unchanged controls separately. This meets SC-05 without turning unchanged controls into fail-first proof.

## SC verdicts and finding

SC-01 met (automated); SC-02 met (automated); SC-03 partial (automated); SC-04 met (inspection); SC-05 met (automated). All trace to plan.yaml tasks[T-01].traces; no perspective or SC is orphaned.

- G-01 — kind: substance; reader: harness-pm; severity: medium; task: T-01. SC-03 promises real out-of-domain writes and edits retaining payloads/refusal, plus main-session write/edit behavior. The only forbidden real-file test is mixed edit (:1093–1102); its payload check inspects only file_path and post checks only isError. Ordinary payload control covers allowed write, while main-session control exercises only pre-write. There is no forbidden write pre/post control, full Edit payload/refusal composition assertion, or main-session edit/post control. Shared committed implementation plausibly preserves these behaviors, but inspection cannot discharge an automated criterion. Add the missing controls within the existing owned test file and let QA run the assigned gate; unchanged controls need not fail first.

## Evidence provenance and boundaries

Receipts cited above are feature notes/receipt-t01-fail-first.txt and notes/receipt-t01-pass.txt. The former explicitly uses unmodified adapter 7fba7e1d; the latter records the completed suite. git diff f9e23bcb 85038f8c1acbb38e2b6f758540941bc5cfdaf1ba -- .omp/extensions/harness-hooks.ts tests/unit/omp-hooks.test.ts .omp/tests produced no output (exit 0), establishing equivalence for these surfaces, including .omp/tests, between the supplied code parent and pin. This is not a claim that the patch itself introduced no changes against the older defect baseline. No QA digest was present in the notes directory when read; this grading uses the named build receipts and committed assertions, not an invented QA run.

Open questions: none for product scope. Coordination and automated defect-report attempts were refused by the live write tool as agent:/Bug2003Validate.DisappointedFly and xd:/report_issue respectively. This is a host/tool observation, not evidence of a defect in the pinned adapter; it prevented requesting a QA pointer and reporting that tool discrepancy. No source, tests, brief or plan changed.
