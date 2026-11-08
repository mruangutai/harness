# Handoff — BUG-2190-inv37-offline-binding, validate → ship — written at cf13aab6, seq-3

## Next

Ship falls under the operator's standing directive of 2026-11-07 and the operator's DEC-221 decision of 2026-11-08. The main session will:
1. push the branch and open the PR against `main`;
2. get CI green;
3. merge;
4. fast-forward the main checkout;
5. run `gh-sync.py ship` from it.

After that, the Kaya corpus PR #2189 (FEAT-01-kaya-platform) can land. A simulated tokenless-CI check-state over that branch merged with this fix shows no INV-37 finding; the only finding is the env-local INV-31 hooksPath. No further run is owed by the orchestrator.

## Trust

- Validate c0, over 33c0c181, returned FAIL with two med substance must-fix items:
  - SC-02: the recovery-guidance repository is not asserted;
  - SC-03: no non-mapping factory case.

  Fix c1, commit fcc91963 (tests only), resolved both, and QA mutants M4 and M6 are now killed. qa, code, security and ui all PASS over cf13aab6 — `runs/2026-11-08-02-validator/digest.md`, `runs/2026-11-08-03-validator/digest.md`, `notes/qa-c1.md` — verified-at cf13aab6
- SC-01..SC-06 pass. Fail-first evidence:
  - integration i.1–i.5, i.9 and i.10 are red at base c6bd42d2;
  - the base output reproduces #2189's CI failure text;
  - unit u.1, u.2 and u.5 are red at base.

  — `notes/build-evidence-2026-11-08.md`, `notes/fix-evidence-c1-2026-11-08.md` — verified-at cf13aab6
- DEC-221 is amended on the operator's verbatim decision of 2026-11-08, and the index is regenerated — `notes/operator-signature-2026-11-08.md`, `.harness/harness/docs/DECISIONS.md` — verified-at cf13aab6
- Four T-01 amendments were recorded through `record-amendments`:
  - `files`: DECISIONS.md and the index;
  - `files`: the reader-inventory row;
  - `files` and `verify`: the unit basename, because the suite layout forbids a duplicate basename;
  - `files`: the table.py `gh:auth` declaration required by FEAT-62 SC-04.

  — `notes/amendment-T-01-*.md` — verified-at cf13aab6
- `cycles_used: 0` of 10. Both leads reported 0, and none is inferred — `feature.json`, `feature-record.py spend` — verified-at cf13aab6
- Lead returns did not reach `digest.md` through the yield hook (#2171). The intake, validate and fix returns were CLI-validated by `validate-digest.py` and appended verbatim, following the BUG-2161 and BUG-2180 precedent. In each case, the appended record equals the returned object — verified-at cf13aab6

## Dead ends

- Option B, a CI PAT, was rejected by the operator: CI does not verify gh-dependent state — `notes/operator-signature-2026-11-08.md` — verified-at cf13aab6
- There was no goal-check over the fix tip, because the fix team excludes it. The c0 goal-check graded both perspectives — `runs/2026-11-08-02-validator/digest.md` — verified-at cf13aab6
- `resolve_binding` is unchanged by ruling. gh-sync and mirror/merge/sweep preflight still fail closed — BRIEF — verified-at cf13aab6

## Working set

- .harness/harness/features/BUG-2190-inv37-offline-binding/feature.json
- .harness/harness/features/BUG-2190-inv37-offline-binding/runs/2026-11-08-03-validator/digest.md
- .harness/harness/features/BUG-2190-inv37-offline-binding/BRIEF.md

## Done when

Scope: PR merged green and `gh-sync.py ship` run
Authority: brief-perspective:.harness/harness/features/BUG-2190-inv37-offline-binding/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2190-inv37-offline-binding/BRIEF.md#code maintainer
