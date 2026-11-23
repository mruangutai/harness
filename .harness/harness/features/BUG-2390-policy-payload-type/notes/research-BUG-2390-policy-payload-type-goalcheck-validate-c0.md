# BUG-2390 goalcheck — validate c0

FAIL — the delivered payload typing and fixture are honest, but SC-02's specifically promised runner-mismatch red and immutable test-only pin are not evidenced. The shared discrimination clause therefore remains incomplete for SC-03. This is an evidence failure, not a demonstrated runtime regression.

## Authority and pin

Review SHA: `79db636b50aa6547edb2b16591f7c26c721f0b47`. BRIEF and plan were read with `git show` at this pin. Authored code is `9eb07b4f..369096a4` in `.omp/extensions/harness-hooks.ts` and `tests/unit/omp-hooks.test.ts`; neither file changes between `369096a4` and the review pin. Later merges and feature records are not attributed to the repair. Product guidance: AGENTS.md map; SPEC §§4.2 and 5.3; settled grilling artifact supplied in the dispatch.

## Perspective outcomes

- **code maintainer — partial:** the delivered contract/narrowing outcome passes SC-01, but its SC-02 verification promise is incomplete. Authority: pinned `BRIEF.md:9,15–18`; coverage: pinned `plan.yaml:24` traces both to T-01.
- **operator — partial:** object/array regression outcomes and baseline equality are supported; the required shared static discrimination proof is incomplete. Authority: pinned `BRIEF.md:11,19–24`; coverage: pinned `plan.yaml:24` traces SC-03 to T-01.

## Criterion outcomes

- **SC-01 — met / inspection.** At the review pin, production `PolicyPayload = Dict | unknown[]` feeds PolicyRunner, classifyPolicyRun and runPolicy (`harness-hooks.ts:49–57,410,525`). The classifier guards arrays before object access (`:431–432`); serialization and forwarding remain unchanged (`:527–528,542–547`). `opsList` returns the checked array itself (`:971–975,1686`). Test helper `objectPayload` throws on arrays before returning the narrowed object (`omp-hooks.test.ts:38–44`); runner, calls and general gate callback retain the union (`:179–189,224–231,3590,3615`). Object-only callbacks are checked at their invocation, not falsely typed at the seam. The member-ops assertion retains `[[ADD], [ADD]]` and its comment is truthful (`:2161–2163`). No relocated array-as-object lie appears in the authored diff. Corroboration: `notes/review-harness-security-reviewer-c0.md:6–8` cites the same pinned subjects.
- **SC-02 — partial / automated.** Pinned `notes/receipts/T-01-red.txt:1–6` records compiler exit 1, but its sole diagnostic is TS2614, missing exported PolicyPayload, not the required union-versus-object runner-contract mismatch. Its subject is base SHA plus uncommitted fixture edits, not an immutable test-only pin. Missing-export failure does not discriminate runner widening: adding only an exported object-only alias could remove that diagnostic while leaving the old runner contract. No such mutant was executed here. `T-01-verify.txt:1–9` records green typecheck plus suite, but likewise describes a working tree, not the completed immutable pin. QA confirmed no separate historical red evidence. A fresh green cannot establish the missing historical event.
- **SC-03 — partial / automated.** Regression portion passes: pinned baseline receipt has 214 pass / 0 fail / 1553 assertions, matching `T-01-verify.txt:5–9` and `research-patch-intake.md`'s Main baseline record. The inspected authored diff removes no test, skip-control or assertion strength; checked narrowing strengthens object reads. Specific carrying tests are member-ops forwarding (`omp-hooks.test.ts:2149–2172`), malformed-ops refusal (`:2070–2079`), and object-gate classification (`:2529–2592`). The baseline-to-feature base comparison changes neither owned file. However BRIEF explicitly reuses SC-02's required static proof, whose specificity/provenance remains incomplete. No runtime red is required or claimed.

## Deviations and decision dispositions

- The verify diagnostic-message repair is recorded in pinned `feature.json:33–38`; it does not weaken a criterion. No syntax check was rerun by this reader.
- Checked `opsList` plus existing `refuseApply: never` and shared `OPS_NOT_A_LIST` preserves the original refusal text and array identity; it serves SC-01 without replacing the removed double cast with a single cast.
- The six pre-existing payload `as any` reads remain unchanged, as settled by the advisor; no new payload assertion is introduced there.
- Pinned `plan.yaml:19–20` declares `decisions: []` and `decisions_affected: []`. Explicitly no amend/strike rows exist, so no DEC landing verdicts are applicable (DEC-254); no decision-text change is required by this bounded type repair.

## Remediation and limits

T-01/Main and QA own the missing evidence; do not re-label TS2614 as a runner mismatch or invent an earlier runtime failure. No replanning or source changes were made. This reader ran only source/history inspection, not tests, builds, linters or formatters; current-pin QA gates remain QA's evidence. Open questions: none.
