# Handoff — BUG-2181-board-item-add, validate → ship — written at 5d78ffc3, seq-2

## Next

Ship falls under the operator's directive of 2026-11-08: "start issue://2181. take it to green and clean merge". The main session will:
1. push the branch and open the PR against `main`;
2. get CI green;
3. merge;
4. fast-forward the main checkout;
5. run `gh-sync.py ship` from it.

No further run is owed by the orchestrator.

## Trust

- Validate c0 over 5d78ffc3 returned PASS. The readers qa, code, security, ui and goalcheck (applicability only) all ran, with no must-fix items — `runs/2026-11-08-02-validator/digest.md` — verified-at 5d78ffc3
- SC-01..SC-03 are met. Fail-first evidence:
  - unit u.1 and u.3 (add/set on an absent item) are red at base 5f935b55;
  - integration a.2 is red at base;
  - board-station case 3 is red at base;
  - all are green at the pin.

  — `notes/build-evidence-2026-11-08.md`, `notes/review-harness-qa-c0.md` — verified-at 5d78ffc3
- `cycles_used: 1` of 10, as the lead reported it: one QA return-contract correction inside the run, with no source remediation — `feature.json` — verified-at 5d78ffc3
- Lead returns:
  - The intake return carried an undeclared `amendments` key and was closed BLOCKED as a refused return under `notes/refused-return-authorization-2026-11-08-01-product.md` (#2171).
  - The validate lead's first return failed `readers[].reason`. Its corrected re-yield passed `validate-digest.py`, and the lead appended that record itself; the record equals the returned object.

  — verified-at 5d78ffc3

## Dead ends

- An Auto-add audit or registration finding was rejected by advisor ruling Inv26RoutingAdvisor: it would mandate a workflow that this fix makes unnecessary — `notes/operator-signature-2026-11-08.md` — verified-at 5d78ffc3
- `factory_decompose.py`'s own guarded add is left unchanged — BRIEF — verified-at 5d78ffc3

## Working set

- .harness/harness/features/BUG-2181-board-item-add/feature.json
- .harness/harness/features/BUG-2181-board-item-add/runs/2026-11-08-02-validator/digest.md
- .harness/harness/features/BUG-2181-board-item-add/BRIEF.md

## Done when

Scope: PR merged green and `gh-sync.py ship` run
Authority: brief-perspective:.harness/harness/features/BUG-2181-board-item-add/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2181-board-item-add/BRIEF.md#code maintainer
