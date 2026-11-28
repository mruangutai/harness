# Code review c2 — BUG-2566 — PASS

Both c1 must-fix items are closed at `f4048ad3f9fbe9326d9799485fb97d87547d27be`. No new blocking defect. SC-10 remains operator UAT in `notes/uat.md`.

## Stage 1 — Spec compliance: PASS

- SC-01–05, D-01–03 (T-01): `tests/unit/omp-hooks.test.ts:2467–2530,4451–4590` covers governance, the exception and Main recovery, fingerprint mutations/exclusions, and the host-bound latency check. SC-07/08 rely on the build/validation receipts; this review did not rerun tests, mutants, or typecheck.
- SC-06 (T-01), inspection: `.omp/extensions/harness-hooks.ts:46–48,68–125,1641,1775–1818,1939–1967` shows the import-derived one-module baseline, full-content hashing via the classified nonblocking descriptor, sole new export, first refusal, exact BLOCKED exception through normal validation, and shared merge prefilter. Pinned `ls-tree` lists only `harness-hooks.ts`; the same inventory at `87efcd8a` and absence of the legacy import confirm D-04.
- SC-09 (T-02), inspection: `.harness/harness/docs/SPEC.md:799–833` covers fingerprint/root, content, exclusions and rationale, refusal/restart, the BLOCKED exception, untouched Main calls, and the one-time restart of pre-feature sessions.
- Fix range `8e18c053..f4048ad3`: only the test changed outside feature records. **Literally not just test + `notes/`**: the delta also includes `feature.json`, c1 `runs/` and `observations/` bookkeeping. `71d686d6..f4048ad3` changes only `feature.json`'s pin field. No hook, SPEC, or plan change in the fix range; no Python or human-tagged commits in the full review range.

## Stage 2 — Quality: PASS with advisories

- **Closed — FIFO (T-01):** `tests/unit/omp-hooks.test.ts:4513–4522` calls the detector and prints its reason only after `mkfifo` returns status 0 **and** `lstatSync(path).isFIFO()` is true. Failed spawn/nonzero status or wrong kind exits 3; an absent path after status 0 throws, also failing the parent's success tuple. Timeout and missing output fail too. No fixture-controlled path passes as the deletion case.
- **Closed — reason root (T-01):** `tests/unit/omp-hooks.test.ts:4458–4474,4484,4490,4504,4522,4544,4574` pins `no longer matches ${H} on disk`. All six calls use fresh `mkdtemp` roots (the FIFO child inherits cwd); a cwd-relative path therefore has an extra path component or `../` before `H`, and cannot match the anchored phrase. The build receipt at line 50 records M3 at 7 pass / 6 fail; the pin supports that result by inspection.
- No new production fail-open or silent-failure path found: from a content baseline, a missing, unreadable, or nonregular path compares unequal; a mismatch returns before policy is called, except that the exact BLOCKED case still faces normal validation.
- **Substance · low · T-01** — `tests/unit/omp-hooks.test.ts:4458–4465,4507–4523`: direct repeated Bun runs leave 13 copied fixture trees per complete run, including the FIFO/probe, because the fixture has no teardown. On a persistent runner or developer host, repeated runs accumulate copies until external tmp cleanup.
- **Substance · low · T-01 (carried advisory)** — `tests/unit/omp-hooks.test.ts:2467–2478,2504–2518`: if the production predicate regressed to accept lowercase `blocked`, these cases would still pass while a ready stale child with that value reached validation instead of receiving the stale reason. The present predicate is correct by SC-06 inspection; normal validation still judges the yield.

## Principles applied

- Model the Domain: checked that the stale guard and Main merge gate share one prefilter, so their command boundaries cannot drift independently.
