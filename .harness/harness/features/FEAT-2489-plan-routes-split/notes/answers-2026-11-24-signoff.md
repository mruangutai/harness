# Sign-off rulings — FEAT-2489 — 2026-11-24

Ruled by fable-advisor (AdvisorE2b_Signoff) under the operator's delegated approval ("start E2. same parameters as feature E, defer to Advisor").

- **Signed:** BRIEF.md and plan.yaml approved as applied (panel cycle 4).
- **Findings:** all six panel findings are accept-as-applied; none is overruled and none is sent back.
- **Grill amendment:** Q3 is amended so that SC-02's fifth sanctioned item is included as a class.
- **Rework:** 2 rounds / 90 minutes.
- **Conditions:** C1-C7 below.

## Full ruling (verbatim)

All evidence is read: BRIEF (including the raw full text of SC-02's fifth item, which no prior reader quotes whole), plan.yaml with the panel block, c1–c4, the goal-check, my own grill ruling, and spot-verification at source (`check-plan-routes.py:1166-1176` `_exemption_finding`, `:1180` `_row_label`, `:1380` `_unaccounted_candidate_findings`, `:1690` summary print; `tests.yml:184,236,243`). Ruling follows.

---

# E2 plan sign-off ruling — FEAT-2489-plan-routes-split (fable-advisor, 2026-11-24)

**Lead disagreement with the orchestrator's framing, before the rulings:** Q1 asks me to accept the fifth item *by overruling* the six open findings. That is the wrong disposition and would poison the record. Five of the six findings were **correct** — they are what forced the fifth item into existence and then forced it into class shape — and their remedies are now applied in the text I read. The closing act is **accept-as-applied** (finding valid, remedy applied, verified by the signer), not overrule. An overruled high finding with an applied remedy is a contradiction in the ledger: it says the reviewer was wrong about a defect the plan then fixed. None of the six is overruled; none is sent back.

## Q1 — The fifth sanctioned item vs. my Q3 "exactly these, nothing else"

**Authority.** My own grill Q3 ruling; the Feature E distilled lesson ("brief class contracts, never instance lists"); DEC-174's cutover proof ("identical violation set before and after"); BRIEF.md:32 raw; the producers at source.

**Gap.** My Q3 closed the delta at four items after grepping the file for its own name and finding "only the T07 tables, refusal message prefixes, and docstrings." That grep was the instance-level check the Feature E lesson warns about: the filename reaches diagnostics at *runtime* — through inventory rows (`_exemption_finding:1166-1176`, `_row_label:1180`), scanned AST candidates (`_unaccounted_candidate_findings:1380`), structure-audit node locators, and interpreter traceback frames — none of which a static grep of the source for its own name surfaces. Three consecutive scope re-reads each finding one more forced member (blank-reason row → removed-row candidate → traceback frames) is the empirical proof that any *list* here is wrong; only the class terminates.

**Ruling.** **Accepted, as a class — my Q3 is amended, not merely excepted.** A verbatim move provably cannot satisfy items 1–4 alone on any tree where a diagnostic names moved code; refusing the fifth item would make SC-02 unsatisfiable, the exact defect my own lead disagreement flagged against "byte-identical summaries." I rule the delta as the class, and the applied BRIEF.md:32 already states it correctly: *membership is decided by what the diagnostic prints, never by where the printed value comes from*, covering every output surface (finding text, refusal messages, tracebacks, line-numbered locators, both streams, any mode), with the named producers as "illustrations, not a list," echoed input data excluded, and exactly two bounded exceptions (producer-order placement; retained-site line shift). That wording cannot cascade: it requires no per-producer enumeration to maintain, and it is a consequence-of-the-move clause, not new behavior.

The six findings, each verified against the applied text:

| Finding | Disposition | Where the remedy sits, verified |
|---|---|---|
| PF-2411…32ff3 (high) | **accept-as-applied** | BRIEF.md:32 admits the forced filename change it correctly said SC-02 forbade. |
| PF-6159…1415e (high) | **accept-as-applied** | Class wording ("illustrations, not a list"; membership-by-print) closes the class, not the sampled instance. |
| PF-daf9…877eb (high) | **accept-as-applied** | Traceback frames are in the class, one locator per frame, frame order and non-location bytes fixed; SC-02 is satisfiable on a malformed-but-readable inventory. The `rows: null` example is written into BRIEF.md:32 verbatim. [Runtime traceback shape unverified by me; producers verified at :1625ff per c4.] |
| PF-b14b…9838 (med) | **accept-as-applied** | T-02 Locator paragraph: full-line formats R1–R6, rewrite "that field's path span, and nothing else"; every other character compared exactly. The quoted-exemption-value mask is closed. |
| PF-1300…503d0 (med) | **accept-as-applied** | Same paragraph names the plan-read diagnostic explicitly: a named plan equal to `…check-plan-routes.py::_classification_document` is echoed input, never rewritten. |
| PF-c01a…6eea7 (med) | **accept-as-applied** | T-04 verify: `[l for l in final if l.startswith('MAP ')] == maps` — final receipt's MAP block equal line-for-line and in order to the live run's, each line fullmatching the strict same-NAME regex. No foreign entry admitted. |

**Constraints.** The class ruling is the contract's final shape; the build may not re-narrow it to the sampled instances, and no seventh member may be added without re-sign — the class as worded already absorbs anything the move forces.

## The checker's design — sufficient, and the normalizer is refused

**Authority.** PF-293c (my own cycle-1 proportionality ruling: only the CLI-equivalence half is sanctioned evidence); PF-b963 (receipt samples are evidence, not scope); SC-01's move-detected diff.

**Gap.** The assignment asks whether a path-rewrite-plus-line-masking normalizer should replace "rests on reading the diff."

**Ruling.** **The fail-closed design is sufficient; do not build the normalizer.** Three reasons, in descending force. (1) Line-number masking *weakens* evidence: a masked locator accepts any line number, including a wrong one, so the normalizer converts a loud FAIL into a silent pass on exactly the defect class it claims to cover. (2) Modelling exact line shifts instead of masking requires computing the move's offsets per symbol — that is the AST-identity checker the panel already refused at PF-293c; it would re-enter through the back door, heavier, inside a one-time throwaway script. (3) The inspection residue is not weak evidence here — it is the *strong* evidence: Python prints a frame's or node's `lineno` from the parsed file, so if SC-01's diff shows the bytes sitting in order in the new module, the printed location at the pin is correct by construction; the only thing that could falsify it is a non-verbatim or reordered move, which is precisely what the move-detected diff exposes. Fail-closed plus SC-01 is a sound division of labor; a normalizer would duplicate SC-01's proof with lower fidelity.

**Constraints.** C1 below freezes this: the checker must never grow cross-line substitution, line-number wildcards, or traceback rewriting. A sampled state that trips the fail-closed path is fixed by changing the sample, never by widening the map.

## Q2 — The two disclosed departures

**Authority.** c2's grading of the install gap ("cannot create a false audit pass"); DEC-183 (tests.yml frozen, nothing in-tree verifies it); T-03 item 3 (the COUPLED comment); tests.yml:236 verified: the frozen text says the summary producer "carries a comment pointing back here."

**Ruling.** **Both accepted.** (a) Complete-install scope: Q3's "every tree state" quantifies over what a runnable checker audits, not over deployments missing required files; a bin missing a module dies loudly at import before any audit runs, which cannot fake a pass. Case 19b's copy list carrying both modules is the right and whole coverage. (b) The frozen tests.yml comment: the COUPLED comment in the entry's `main`, naming `canonical_reader_audit._run_canonical_reader_audit` as the producer, keeps tests.yml:236's pointer ("carries a comment pointing back here") literally true at the entry — the reader who follows the frozen comment lands one hop from the truth. Editing tests.yml to fix a comment would trade a verified invariant (byte-identical workflow, `projection_confined` red on any change) for cosmetics. Correct call.

## Q3 — Record-panel readers loss

**Ruling.** **Backlog; not blocking.** plan.yaml's `panel.readers` today lists only scope/should-not-exist/design; the cycle-1 goal-check ran (its note exists and is substantive) but has no readers row — consistent with the claim that later record-panel runs replaced rather than merged the array. The audit trail survives because `notes/research-FEAT-2489-…-goalcheck-plan.md` is on disk and `last_run`/`cycle` are recorded, so this feature's sign-off is not impaired. File one harness backlog ticket for record-panel: merge-not-replace on `readers`, and include the `reason: none` string serialization (visible at the scope row) in the same ticket — same tool, same fix. Do not hand-edit plan.yaml history.

## Q4 — pm Expertise curation notes

**Ruling.** **Distill, not backlog** — with one carve-out. The plan-merge-apply exit-7 claim is an expertise-accuracy question; distillation is the venue with edit rights over Expertise, and an entry asserting an unverified exit code should be verified against `plan_merge` source there and corrected or dropped. The record-panel reason-'none' *observation* likewise goes to the pm feature log for distill; the underlying *tool behavior*, if confirmed a defect, is already covered by Q3's backlog ticket. Nothing here blocks signature.

---

## Sign line

**Signed — approve BRIEF.md and plan.yaml as applied.** fable-advisor (AdvisorE2b_PlanSign), under the operator's delegated approval ("defer to Advisor"), 2026-11-24, at the plan state carrying the c4 remedies (panel cycle 4). All six open findings: **accept-as-applied**; none overruled, none sent back. Grill Q3's sanctioned-delta list is amended to include the fifth item **as a class**, per the Q1 ruling above.

**Rework ruling:** 2 rounds / 90 minutes at signature, per "same parameters as Feature E." The main session records this in the feature record now (it appears in neither BRIEF, plan, nor feature.json — goal-check departure 5). Expectation: 1 round; the delta is closed-form and grading was de-risked at §8.

## Conditions

- **C1 — Checker stays fail-closed.** split-equivalence.py applies the map only to the locator field's path span of full-line formats R1–R6; it never gains cross-line substitution, line-number masking or wildcards, or traceback rewriting. A sampled run that prints a line-numbered locator in the three split files, raises an uncaught exception, or reorders, FAILs; the remedy is adjusting the sample, never widening the map.
- **C2 — MAP discipline.** The relocation map is derived from moved top-level names (never the inventory); `notes/equivalence-final.txt`'s MAP block is equal, line for line and in order, to the T-04 verify's own live run, every line matching the same-NAME regex into exactly the two modules.
- **C3 — The COUPLED pointer.** The comment added above `main`'s audit dispatch names `canonical_reader_audit._run_canonical_reader_audit` as the summary producer, so the frozen tests.yml:236 pointer remains true at the entry. tests.yml stays byte-identical (`projection_confined` enforces it).
- **C4 — Complete-install scope holds as disclosed.** Case 19b's copy list carries both modules; no new partial-install promise is added, and the BRIEF's Verification-gaps disclosure of the import-failure surface is retained verbatim.
- **C5 — No contract re-narrowing.** SC-02's fifth item ships with its class wording ("illustrations, not a list"; membership-by-print; the two bounded exceptions) unedited; any build-time pressure to enumerate producers instead is refused and escalated.
- **C6 — Backlog ticket filed** (Q3 ruling): record-panel readers merge-not-replace plus reason-'none' serialization; one ticket, outside this feature.
- **C7 — Distill items** (Q4 ruling): verify-or-drop the plan-merge-apply exit-7 expertise claim; log the record-panel observation in the pm feature log.
