# Validate c0 ESCALATE ruling — FEAT-2489 — 2026-11-24

Ruled by fable-advisor (AdvisorE2e_Val0) under the operator's delegated approval.

- **ESC-1:** amend SC-02 with a sixth sanctioned item, defined by contract: per-file aggregation, ceiling and parse scope, bounded by conservation and fail-closedness.
  - The BRIEF is edited and re-signed (signer work; this uses no rework round).
  - Evidence is a separate manual seam-straddle receipt; split-equivalence.py gets no new sample (C1).
- **CR-2:** fix the checker to compare bytes with line terminators preserved. No ledger entry: this conforms to T-02's signed intent. Regenerate equivalence-final.txt and re-run T-04.verify.
- **SEC-1:** backlog (path containment for `_copy_named_plans`).
- **QA-F1:** accepted (the two readings are identical).
- **#2519:** closed via the PR.
- **Fix round:** authorized within 2 rounds / 90 min.

## Full ruling (verbatim)

All materials read and verified at source: the digest (whole), both reviewer notes, SC-02's raw fifth item (BRIEF.md:27-32), T-02's full signed intent (plan.yaml:296-416), `structure_audit.py:868-899`, `canonical_reader_audit.py:228-241`, `split-equivalence.py:188-197`, `test-check-plan-routes.py:1946-1959`, the sign receipt, the DEC-23 precedent note, and issue #2519. Ruling follows.

# Advisor ruling on validate c1 ESCALATE — FEAT-2489 @ be0807b0 (fable-advisor, AdvisorE2b_Signoff, 2026-11-24)

**The escalation is correct and the verdict is endorsed. ESC-1 is resolved as option (a): SC-02 is amended with a sixth sanctioned item, defined by contract, signed by me under the delegated approval. One material disagreement with the digest before the itemized rulings — it is the one thing in this round that could go wrong.**

## Lead disagreement: the digest's hint to make the checker "sample a seam-straddling state" must not be followed into split-equivalence.py

The digest (CR-2 remedy, "An amended SC-02 may also want the checker to sample a seam-straddling state") plants a trap for the fix-round builder. A seam-straddling sample *cannot pass* the checker as designed: base prints one `carries 2` finding where the pin prints two `carries 1` findings, which is a count and multiset change no locator map covers — so passing it requires new modelling, which is exactly the widening C1 forbids ("never gains cross-line substitution… the remedy is adjusting the sample, never widening the map"). A builder who follows the hint either breaches C1 or ships a sample that permanently FAILs.

**Constraint on the fix round:** evidence for the amended class is a **separate manual receipt in notes** — run the base entry and the pinned entry once each on one seam-straddling perturbed tree (a broad catch in a retained and in a moved function; a parse-error variant alongside), record both outputs whole, and state the conservation argument (sites preserved, exits equal, summary +1). split-equivalence.py is not touched beyond CR-2. This matches how SC-02's other inspection-only surfaces are already evidenced (BRIEF.md:63).

## ESC-1 / OQ-1 — Amend SC-02: ruled, with the class wording and the ledger mechanics

**Verified.** `_broad_catch_findings` (structure_audit.py:892-899) emits one finding per census file against `BROAD_CATCH_CEILINGS.get(name, 0)`; `_scan_reader_tree` (canonical_reader_audit.py:228-241) drops exactly the unparseable file's candidates and keeps scanning. Both reviewer scenarios are real, both are outside the fifth item (they change counts and multiset, not locators), and both sides stay non-zero with **equal exit codes** (consolidation 1/1; canonical 2/2), so the lead's operational-low grading is also right. The two ratings coexist honestly under P-04; no revision needed.

**Option (b) is not merely out of scope — it is wrong.** The per-file keying is the audit's own documented design: "a ceiling is keyed by the bin-relative name, so a package file can never borrow a sibling's allowance" (structure_audit.py:888-891). Aggregating the three files would grant moved code the entry's allowance — the defect class FEAT-69 closed. (c) abandons a feature that is otherwise verbatim-proven and green. **(a) is ruled.**

**The amendment, by contract (Feature E lesson applied):** add a **sixth item** to SC-02's closed list, worded as a class keyed to the mechanism, with the two found instances as illustrations only:

> *Where an audit aggregates, ceilings, or scopes a quantity by physical file — a per-file count compared against a per-file ceiling, or a per-file parse whose failure admits or drops only that file's candidates — the pin's findings are those the unchanged per-file rules produce on the pin's file layout: contributing sites that SC-01's move separates yield one finding per file carrying that file's count; summary totals count those findings; a file's parse failure confines its effect to that file. Bounded by conservation and fail-closedness: every site counted at base is counted at the pin exactly once, in the file the move gave it; no tree clean at base gains a finding at the pin and no finding-triggering tree at base goes clean at the pin; mode exit codes are unchanged; each finding's text differs from base only in its locator (per item five) and its per-file count, in the producer's existing walk order. The broad-catch census and the reader-scan parse scope are illustrations, not a list.*

**Ledger mechanics — re-sign, not a DEC-23 amendment judgement.** DEC-23's ledger ("one amendment judgement per changed field, never a fresh signature") covers signed *plan-task* fields — `verify` is in `LEDGERED_FIELDS` (notes/answers-2026-11-24-t03-verify.md:17-22, where I used it for T-03). SC text in BRIEF.md is not a ledgered field and has no amend verb. The BRIEF's signature is its own `## Approval` block, "the GOAL's signature, which no plan change resets" (plan_merge/approval.py:348-357), content-bound only by the commit record. So the mechanics are: **(1)** this ruling recorded as a new answers note; **(2)** BRIEF.md SC-02 edited to add the sixth item; **(3)** the `## Approval` block re-signed by the same verb, new date, by me under the delegation — revoke-and-re-sign in effect, one commit naming ESC-1; **(4)** C5's evidence baseline re-pins to that commit ("BRIEF unchanged since the amended signature"). The plan signature and `signed_task_hashes` are undisturbed — they cover only each task's `{files, intent, verify}` (notes/answers-2026-11-24-inv32.md:7,18).

**Is C5 triggered?** Clarification first: "no seventh member without re-sign" is my Q1 *constraint*, not C5's text; C5 proper is "no contract re-narrowing," which forbids build-side shrinking and editing the fifth item's class wording. The amendment does neither — item five ships unedited, and this is signer-side widening, not build-time pressure. So **C5 is not breached; the Q1 re-sign constraint is what's triggered, and the re-sign above is precisely its prescribed vehicle.** C5 survives the amendment with its evidence re-pinned.

## CR-2 — No ledgered T-02 amendment is needed; the byte fix is *conformance to* the signed intent, not a departure from it

I checked T-02's intent end to end. It nowhere specifies text-mode capture. It specifies line-based *receipts*, and for comparison it says the opposite of what the script does: "every other character of a rewritten line, is left exactly as it was… Every line no recognized format matches is compared exactly, never rewritten… **No other normalization, wildcard or fuzzy match is applied anywhere**" (plan.yaml T-02 Locator paragraph), echoing SC-02's "every character outside the locators… byte-identical." `text=True` + `splitlines()` (split-equivalence.py:188-197) *is* an unauthorized normalization under that clause — the current script is the departure, the fix restores the signed contract. **Fix without any ledger entry**; T-02's own verify block needs no text change (its assertions parse the checker's PASS/FAIL/CLI/MAP lines, all format-stable), and T-04's verify is re-run, not amended. Regenerate `equivalence-final.txt` as the digest orders.

## SEC-1 — Backlog; the lead's dismissal stands

Verified at test-check-plan-routes.py:1946-1959: `os.path.join(td, plan)` with an inventory-controlled relative path escapes `td` on `../`, and `isfile`/`copyfile` follow symlinks. The lead's trust-domain argument also verifies: the inventory is a tracked file in the same repo as the test and the squad-writable bin libraries the same suite executes; an inventory editor already has code execution on the runner. Fixing it now would mean editing a signed, done task's file outside the must_fix set, with fresh red/green evidence owed under the verification rules — a round-expander with no gating value. **Backlog ticket** (one `realpath`-containment check plus a symlink rule, with its own red test), filed alongside OQ-3's disposition below.

## QA-F1 ('mapped' counts stdout only) — Accept; the two readings are provably identical

By the intent's own Locator rules, R1–R6 match only stdout lines and "every stderr line" is in the compared-exactly-never-rewritten set — so the number of stderr lines the map changes is identically zero, and stdout-only counting equals the intent's "stdout and stderr" quantity on every input. The intent's internal phrase "mapped old stderr lines" resolves as the identity map. **No amendment; no behavior change.** Align the wording in a comment while the CR-2 fix has the file open — zero-cost, optional.

## OQ-3 — Yes: `Closes #2519` in the PR

Verified: issue #2519's title ("--canonical-reader-self-test has 2 failures and no runner invokes it", FEAT-2458 B-4) is exactly T-01's scope ("Fix the canonical-reader self-test to the true named-plan contract and run it by default", plan.yaml:223,288), with the two-FAIL red receipt (`red-t01-canonical-self-test.txt`) and the default-run green in the QA manifests as the closure evidence. Close via the PR; cite the red receipt in the PR body. File the SEC-1 hardening ticket at the same time so the closure doesn't silently absorb the advisory.

## Rework budget — Yes, comfortably within

The round is: CR-2 byte fix + receipt regeneration + T-04 verify re-run + QA-F1 comment + the seam-straddling manual receipt. All closed-form, no design work; this is the "expectation: 1 round" case my sign-off priced. The SC-02 amendment is **signer work, not a builder round** — it consumes none of the 2 rounds / 90 minutes. Order of operations: amendment commit first (so the fix round builds against the final contract), then round 1, then validator c2.

**Not verified by me:** `plan_merge/amend.py:233` LEDGERED_FIELDS membership (relied on my own prior sourced ruling in answers-2026-11-24-t03-verify.md) `[unverified]`; the runtime traceback shape caveat from the original sign-off stands as recorded there.

**Sign line: ESC-1 resolved as amend-and-re-sign per the class wording above; CR-2 fix ordered without ledger entry; SEC-1 and path-hardening to backlog; QA-F1 accepted; #2519 closed via the PR; fix round authorized within the signed budget.** — fable-advisor (AdvisorE2b_Signoff), 2026-11-24.
