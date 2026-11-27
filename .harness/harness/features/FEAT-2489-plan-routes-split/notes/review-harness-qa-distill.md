# QA distill — FEAT-2489-plan-routes-split (validate c1 ESCALATE, c2 ESCALATE, c3 PASS)

**PASS. Five ops applied in two batches; no suite run, no diff reviewed (suite n/a, matrix_ok n/a).**

- Craft batch `c486b80fd0f2736faa646d0f60f63f5fc0eb15d7d4fc561704130c832c599da0` → `.harness/expertise/harness-qa.md`
  - before: Patterns 15, Gotchas 15, Outcomes 10, Open 1 · after: Patterns 15, Gotchas 15, Outcomes 10, Open 0
- Repository (`harness`) batch `f3f4dcdf8a9ab08a0fd35ffb2762952aa64329fd082db3c6cfcd9292ba826856` → `.harness/harness/expertise/harness-qa.md`
  - before: Gotchas 14 (others 0) · after: Gotchas 15 (others 0)
- Receipt: `notes/expertise-receipt-f63f7a3f5811595b940b508feb93c85cc16383c4a0b590a93055d1a637c1ed63.json`

## Dispositions

| Candidate | Disposition |
|---|---|
| 1. Pristine-runner substitution concealed 4 traceback lines (`notes/qa-c2-cr3-probe.md` P4) | **Applied** — craft G-04 replaced (displacing the old task-verify-vs-kind rule, now forced by DEC-255 runner receipts): run each side whole-process by its own entry |
| 2. Matched `git archive` trees made equivalence measurable | **Applied in part** — the new part, attributing a difference by swapping only code over a fixed tree (c3 crossbin probe), folded into the same G-04. The archive-tree method itself is **rejected** as already covered by P-07, P-15 and G-15 |
| 3a. bash-write-guard blocks `$VAR` cp/rm/redirect targets (3 log bullets) | **Applied** — repo G-13 widened from redirect to cp/rm plus python-driver cleanup; craft Open Q-01 **dropped** as resolved (literal vs variable target explains the inconsistent sessions) |
| 3b. Stale helper call shape → misleading defect wall (2 log bullets) | **Applied** — repo G-15 added as a pointer to validate-digest.py's living call site |
| 3c. Dispatch named a non-existent CI consolidation step | **Applied** — craft G-02 replaced at equal length: confirm a dispatch-named gate exists |
| Log: bare-CR boundary probe on CR-2 | **Rejected** — an instance of existing P-11, a story not a rule |

## Open questions

None.
