# c4 validate authorization — delegated ruling — FEAT-2397 — 2026-11-23

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (AdvisorC14C3Gate, which signed as AdvisorC15MatrixScope).

**Gap.** c3 (`r-20261122-7-validate-validator`) closed ESCALATE. Code passed the fix as correct in
kind, but the installed QA gate refused a scoped PASS: a QA PASS needs fresh DEC-255 production
unit and integration runner receipts.

**Ruling.**
1. **Authorized.** c4 completes round 2; it does not open round 3. An answered ESCALATE that is
   re-dispatched is not rework under DEC-157. The defect was in the c3 scoping ruling itself, so
   it is chargeable to the advisor, not to the feature. The gate is not waived.
2. **test-factory-config.** Its red appears only in Main's `$TMPDIR` clones, where `/var` realpaths
   to `/private/var`. QA's managed pins live under `/Users`, and both prior QA unit manifests on this
   host show it green, so c4 should expect green. If it reds in the pin anyway, QA reports honestly
   (`suite: fail`, ESCALATE). That would go to the operator; nothing is pre-authorized.
3. **Ledger:**
   - a `continue` judgement;
   - re-pin to the current tip (commits past `1133d63c` touch only the feature dir);
   - `run-start r-20261122-8-validate-validator` with no `--regate` and no `--succession`.

   QA runs both runners serially from its managed review-pin checkout, writing manifests under
   `runs/r-20261122-8-validate-validator/qa/`. Code's c3 PASS, the c2 goalcheck and the c1
   security/UI verdicts carry as skipped readers. Fail-first is the natural red in
   `notes/fix-c2-evidence/red-ci-env.txt`. Close PASS with `cycles_used 0`.
4. **Wall clock.** 44 of 90 minutes are used, and the authorization covers finishing c4 only.
5. **The README low/form finding is closed** by `8e3874be`.
