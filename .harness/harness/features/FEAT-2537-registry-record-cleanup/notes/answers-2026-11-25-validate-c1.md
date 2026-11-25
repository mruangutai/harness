# FEAT-2537 re-validate ruling — 2026-11-25

Run: r-20261125-3-validate-validator, ESCALATE at pin 635b5c15.

**Authority.** The operator delegated approval to fable-advisor; ruled by AdvisorF6Revalidate.

**Gap.** c1 delivered 'raw bytes' as a text-mode read, which left SC-02 literally partial while the c0 ruling allowed no second round.

**Ruling.**
- (b) is granted as the **completion of round c1**. It does not consume the rework budget.
- The reviewer's severity is re-rated from high to med.
- F2 (feature-dir records) is not a scope breach.
- QA alone re-checks; the code-reviewer must_fix closes on QA's receipts.

**Constraints.**
- Only `test-inflight-registry.py` changes, and only the case-18 helpers and state table:
  - read with `rb`;
  - use `object()` sentinels;
  - make the expectations encoded bytes;
  - assert empty stderr on silent rows.
- QA re-check: green; the base-swap reds persist; the default-to-v2 mutant dies; a CRLF writer mutant is red; the diff is confined to that file; the immutables are identical.
- Then ship without returning to the advisor.

## Full ruling (verbatim)

All decisive claims verified at source in the worktree at pin 635b5c15. Ruling follows.

---

# FEAT-2537 re-validate ruling — fable-advisor, under the operator's delegated approval — run r-20261125-3-validate-validator

## Authority

Operator delegation, continuing my c0 ruling of 2026-11-25 (`notes/answers-2026-11-25-validate-c0.md`). The escalation is correctly routed: my c0 ship condition required SC-02 met and forbade a second round, so only I can resolve the deadlock. I re-verified rather than trusting the digest:

- **All three reviewer observations are real.** `tests/integration/test-inflight-registry.py:504-509`: `_file_bytes` opens `"r", encoding="utf-8"` — text mode, universal newlines. `:486-487`: `_ABSENT = "<absent>"`, `_UNREADABLE = "UnreadableRegistry"` are string sentinels. `:565-567`: the warn check is `"treating as empty" in buf.getvalue()` compared with `warned is warns` — silent rows assert phrase-absence, not empty stderr.
- **But two of the three are not gaps against the governing texts.** My c0 constraint *itself* named `<absent>` as the absence representation ("`<absent>` for missing"), so the string sentinel is compliance with the ruling, not a defect against it; and SC-02's literal list is "return value, raise or no raise, and the file bytes after the call" — stderr content is not in it (the warning direction is separately asserted and passes). "Raise or no raise" **is** functionally asserted: `_check_strict_read:552-556` maps a raise to the sentinel and a no-raise to the return, and no plausible return of `live_claims` (a list of dicts) collides with the string.
- **The one genuine letter gap is the text-mode read.** My c0 scope line said case 18 "compares **raw bytes**". A utf-8 text read with newline normalization is not raw bytes; a CRLF-emitting mutant writer passes 200/200. This is a shortfall of the c1 delivery against its *own ruled scope*, not a new defect class.
- **Everything else green as digested:** 200/200 at pin, 12 base-swap reds in the ruled direction, default-to-v2 mutant dies, verify exit 0, immutables identical, docstring must_fix closed, and `git diff --stat 8ae96bea..635b5c15 -- . ':!.harness'` shows exactly the two ruled files (module +3/-… docstring-only per QA; test file 132 lines).

## Gap

The c1 round delivered SC-02's substance (both directions, both new envelopes, full returns, canonical serialization pinned) but implemented the ruled "raw bytes" clause as a decoded-text comparison, leaving SC-02 literally partial. My ruling's one-round budget then collided with its own ship condition, forcing this escalation.

## Ruling

### Q1 — (b) granted, **ruled a completion of round c1, not a second round; it does not consume the rework budget.**

Reasoning:

1. **Budget accounting.** The c0 scope said "compares raw bytes … no decoded-JSON comparison anywhere in the case." The text-mode helper is an incomplete delivery of that clause. Finishing a round's own ruled scope is not rework; the one-round budget stays spent-once. The "no second round" clause forbade *new* scope and re-litigation, not the closure of the round's own letter.
2. **Why not (a).** Accepting intent-met would ship SC-02 as "met" on a ruler's interpretive override while the operator's criterion says "the file bytes" and my own ruling said "raw bytes" — two records that the next auditor reads literally. The remedy is ~10 lines in a T-01 test file with a QA-only re-check; the cost of (a) is a permanently contested SC row plus a backlog item, which is more expensive than the fix. Backlogging a 10-line test fix is how letter gaps become folklore.
3. **Severity re-rated: med, not high.** The code-reviewer's high is overstated — every counterexample needs a mutant no code path on this platform produces, and two of three complaints contradict the governing texts (above). QA's low undersells the one real clause miss. Recorded as med; it closes in this completion, so the `severity_max: high` gate dissolves with it.
4. **Sentinels and stderr ride along, but as hygiene, not obligation.** Since the helpers are open anyway: `object()` sentinels close the theoretical collision class at zero marginal cost, and `buf.getvalue() == ""` on silent rows upgrades phrase-absence to silence. Neither alone would have justified a round.

### F2 — CONFIRMED: no scope breach.

Verified by git: outside `.harness/`, the 8ae96bea..635b5c15 range touches only the two ruled files. The feature-dir paths are station records my own ruling mandated (the ruling note itself, the ESCALATE record, `fix-c1-receipt.md`, run state, QA manifests). The c0 stop-and-rule clause governs source and behavior, not the bookkeeping that records compliance with it. The code-reviewer's form finding is dismissed.

## Constraints — c1-completion scope (exact; anything beyond is stop-and-rule)

**One file: `tests/integration/test-inflight-registry.py`, case-18 helpers and state table only.**

1. `_file_bytes`: open `"rb"`, return `bytes`; missing file returns the absence sentinel.
2. Sentinels: `_ABSENT = object()`, `_UNREADABLE = object()` (module-level, distinct).
3. Expectations in `_registry_states`: folded states `_canonical(...).encode("utf-8")`; untouched states `text.encode("utf-8")`; missing states the sentinel. No decoded comparison remains.
4. `_check_locked_write`: silent rows (`warns is False`) assert `buf.getvalue() == ""`; warning rows keep the phrase assertion.
5. **Zero diff** in `inflight_registry.py` and everything else.

**Re-check: QA only.** No code-reviewer round — must_fix 1 is closed by this ruling upon QA's receipts, since the remedy is mechanical and QA's mutant run is the stronger witness:
- whole file green at the new pin;
- base-swap: the 12 ruled-direction reds persist, controls green;
- default-to-v2 mutant still dies;
- **new: a CRLF-emitting writer mutant is red** (this is the witness that "file bytes" is now literal);
- diff vs 635b5c15 confined to the one file above; immutables byte-identical to base.

## Exact remaining steps to ship

1. Main session applies the five-point edit above (one commit on `feat/FEAT-2537-registry-record-cleanup`).
2. QA re-check per the list above; receipts under the new run's `qa/`.
3. Record: SC-02 → **met** (literal); code-reviewer must_fix 1 → closed by this ruling + QA receipts; F2 → dismissed; link this ruling from the r-3 digest.
4. **Ship at the resulting pin without returning to me.** Carried-forward rows (SC-01/03/04, DEC-199/204/218, security, ui, goal-check) stand; do not rerun. Backlog rows from c0 (dispatch-guard fail-closed; signoff correction) ship with the feature record as filed.
5. Any diff outside the one file, any QA red, or any new behavior delta → stop-and-rule, not a loop.
