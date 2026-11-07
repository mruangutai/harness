# Handoff — BUG-2180-inv26-fleet-routing, validate → ship — written at 909798ec, seq-3

## Next

Ship falls under the operator's standing directive of 2026-11-07 ("take each to a clean and green merge"). The main session will:
1. push the branch and open the PR against `main`;
2. get CI green;
3. merge;
4. fast-forward the main checkout;
5. run `gh-sync.py ship` from it.

After that, the Kaya corpus PR (FEAT-01-kaya-platform) can land: its local check-state no longer aborts on INV-26. No further run is owed by the orchestrator.

## Trust

- Validate c0 over 556a23ff returned FAIL with two substance must-fix items: R1, case_x complexity; and R2, the DEC-217 unit floor. Fix c1, commit 1e55b30c, resolved both. The readers qa, code, security and ui all PASS over 909798ec — `runs/2026-11-07-02-validate-validator/digest.md`, `runs/2026-11-07-03-fix-c1-validator/digest.md` — verified-at 909798ec
- SC-01..SC-04 pass, with fail-first evidence for every case:
  - integration: x.1..x.6 red at base 4a05030d and green at the pin;
  - unit: 7 behavioural FAILs at base, 9 PASS at the pin.
  — `notes/build-evidence-2026-11-07.md`, `notes/receipt-main-session-fix-c1.md`, `notes/qa-fix-c1.md` — verified-at 909798ec
- The live read-only smoke against the recovered Kaya feature exits 0, with no traceback. It made one GraphQL read, to mruangutai/kaya only — `notes/build-evidence-2026-11-07.md` — verified-at 554f219e (board.py unchanged since)
- One T-01 `files` amendment added `tests/unit/test-check-state-inv26-routing.py`, recorded through `record-amendments` on advisor ruling Inv26RoutingAdvisor — `notes/amendment-T-01-unit-floor-2026-11-07.md` — verified-at 909798ec
- `cycles_used: 1` of 10. Rework is 1 round of 1, 20 of 45 minutes, at fix close — `feature.json`, `feature-record.py spend` — verified-at 909798ec
- Lead returns did not reach `digest.md` through the yield hook (#2171):
  - The intake run is closed BLOCKED refused-return, because of an undeclared `amendments` key, with authorization `notes/refused-return-authorization-2026-11-07-01-product.md`.
  - The validate and fix returns were CLI-validated by `validate-digest.py` and appended verbatim, following the BUG-2161 precedent. In each case, the appended record equals the returned object.
  — verified-at 909798ec

## Dead ends

- No goal-check over the fix tip: the fix team excludes it, and the validate c0 goal-check graded both perspectives — `fix.yaml`, `build-phase.md` step 6 — verified-at 909798ec
- #2181 (gh-sync never adds board items) and INV-30 owner assumptions are out of scope and tracked separately — BRIEF `## Out of scope` — verified-at 909798ec

## Working set

- .harness/harness/features/BUG-2180-inv26-fleet-routing/feature.json
- .harness/harness/features/BUG-2180-inv26-fleet-routing/runs/2026-11-07-03-fix-c1-validator/digest.md
- .harness/harness/features/BUG-2180-inv26-fleet-routing/BRIEF.md

## Done when

Scope: PR merged green and `gh-sync.py ship` run
Authority: brief-perspective:.harness/harness/features/BUG-2180-inv26-fleet-routing/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2180-inv26-fleet-routing/BRIEF.md#code maintainer
