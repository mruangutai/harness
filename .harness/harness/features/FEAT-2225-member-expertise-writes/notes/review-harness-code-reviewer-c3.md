# FEAT-2225 — code review c3

**FAIL — F2 remains high/substance, owning tasks T-01/T-04; F1/F3 remain CLOSED.** Reviewed `594af2a8123771da1a5290942400f4f8a064656f..6d9e6053a6367c78f1e5848a6801e7ca09d82dd1`, including c2→c3 executable changes at `219690d0`. Stage 1 completed with the mismatch below; qualitative Stage 2 is not cleared. Counterexample is **[INFERENCE] from pinned source, not an executed exploit**.

## F2 rejudgment — SC-02/SC-03

The normal feature-branch case is repaired: `expertise-merge.py:1564-1596` resolves default branch in the claimed order, computes its merge-base with HEAD, and requires that blob on the complete-file chain, including every active caller batch. `validate-digest.py:2263-2287` supplies no digest-controlled base and propagates nonzero verification as refusal. Missing all three refs and unrelated history refuse with 15; invalid explicit commits refuse with 15 through `resolve_base:990-997`.

**Remaining concrete counterexample (same F2, not a new finding):** local-only feature checkout, no origin/HEAD or origin/main; local main initially A contains G-01. On `feat/x`, delete G-01 without an op and commit B. Move the *local* main ref to B (`git branch -f main B`), while staying on `feat/x`; legitimately apply receipted P-01. The resolver selects local main B, `merge-base(B, HEAD=B)` is B, and the chain is current → B. Every active batch is consumed, P-01 agrees, and the G-01 deletion passes live/durable verification without a receipt. The same failure holds if the preferred remote-tracking ref points at B. The unit control `test-expertise-ops.py:780-794` actually expects acceptance of the feature commit when origin/HEAD resolves to it.

This does **not** require running distillation in the main checkout. Branch names differ while commit identities coincide. Neither host placement/authority (`harness-hooks.ts:1159-1200`) nor registered close context (`validate-digest.py:2017-2029`) establishes independent default-ref provenance or excludes this topology. Therefore the receipt's claim that self-anchoring occurs only in the main checkout is false. SC-03 and SPEC §5.3 (`SPEC.md:941-946`), DEC-253 (`DECISIONS.md:8195-8202`) promise close-time refusal; later exact-main replay containment does not satisfy it. Preserve **high**, owners **T-01/T-04**: complete-file close integrity still depends on a mutable feature-local ref.

## Explicit-base design and regressions

- `merge-base(--base, HEAD)` is acceptable for a **trusted main base**, including nonancestor main that advanced after the fork: the close chain starts at the common fork, whereas replay reconstructs onto exact current main. Requiring the raw advanced-main blob would incorrectly reject the retained supersession control (`test-expertise-merge.py:2261-2268`). Unrelated history refuses. An arbitrary explicit SHA is not independently authorized merely because it resolves; `--base HEAD` still self-anchors, but live/durable callers pass no such argument, so this is not a separate live bypass finding.
- New committed-tamper regressions bind actual member/lead verification and live/durable close (`test-expertise-merge.py:1937-2006`; `test-validate-digest.py:6211-6253`). Their fixed-main fixtures do not discriminate moved-ref self-authorization.
- QA c2 unchained-batch advisory is CLOSED by inspection: `_check_unchained_active_batch` asserts both positive on-chain acceptance and named off-chain refusal; supplied `red-first-fix-c2-core.md` records N2 mutant failure. No mutation execution claimed here.
- F1 CLOSED: registered authority remains required before member-ops (`harness-hooks.ts:1177-1200`, `validate-digest.py:1957-2029`). F3 CLOSED: five real-host/default-policyRunner representatives still exercise both tiers/all verbs and actual file/receipt verification (`omp-hooks.test.ts:3376-3544`). Those paths are unchanged in c3.

## Inspection and measured evidence

SC-06 inspection: pinned `SPEC.md:904-978`, `DECISIONS.md:8178-8234`, and changed distill/expertise/curate/procedure/persona guidance retain member application, feature-tree destinations, lead verification and replay/refusal routing. Documentation/guidance is unchanged from c2; no new scope departure identified.

Independent git status: only feature.json bookkeeping modified; no source dirt. Full commit census and human-marker log read; no `[harness:human]` commits. Merge-base with origin/main equals supplied base. Independent pinned Python grading: exit 0, **459 passing**, no failing/grade-2 records; `code_grade: pass` is mechanical, not behavioral clearance. No tests/build/lint/formatters or probes executed. Prior validator digest was read from disk because it is absent at the pin. QA owns executable verification; supplied red/green notes are author-reported evidence.

Open questions: none. No source, tests, guidance or Expertise edited.
