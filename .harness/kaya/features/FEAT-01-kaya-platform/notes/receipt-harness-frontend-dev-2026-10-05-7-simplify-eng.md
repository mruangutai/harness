# Receipt: harness-frontend-dev: FEAT-01 c2 simplify, REUSE angle (run 2026-10-05-7-simplify-eng)

**Angle file followed:** `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-reuse.md` (the only angle read).

**BLUF: PASS, 3 advisory flag-only findings (all low or low-med), 5 checked and left. Nothing applied. Nothing touches DESIGN.md.** The UI transport reuses the native stack. T-07 names `useChat` and `DefaultChatTransport` (plan.yaml:503), and T-06 names `handleChatStream` v6 with `createUIMessageStreamResponse` (plan.yaml:462). T-05 names `convertMessages(...).to('AIV6.UI')` (plan.yaml:432), and T-08 names `readUIMessageStream` (plan.yaml:542). There is no custom reducer, parallel agent or second protocol. All findings are `[INFERENCE]`: nothing was installed, run or measured.

Surface read: plan.yaml T-01..T-10, D-01, D-02, lanes, c2 panel; BRIEF.md SC-10 and constraints; DESIGN.md transport lines 7, 94, 101, 103; Kaya docs/ARCHITECTURE.md:22 and DECISIONS.md DEC-012 (docs/DECISIONS.md:99–105). Prior run-4 digest (R-1, R-2/F-2, S-1, E-1, F-1 and the 8 skips) was honoured: none re-raised.

## Findings (file, line, summary, cost, alternative, disposition)

### U-1 (low-med): the "saved exchange" predicate is specified as prose in six places and implemented in two code homes with no named owner
- **File/line:** plan.yaml:464 (T-06 contract), :505 (T-07 browser predicate, "this exact predicate"), :542 (T-08 CLI live predicate), :314 (T-02 server tests), :312–318 (T-02 browser), :608 (T-10 docs); DESIGN.md:94.
- **Summary:** The same checks are re-spelled for the browser and the CLI. They are: current user ID, current assistant ID following that user, and completed ordered parts equal to the streamed parts. The CLI reconstructs them from `readUIMessageStream` output and the browser from `useChat` completion. T-07's file list (plan.yaml:483–494) holds no predicate home, and T-08 is told only to implement its own.
- **Cost:** Two code spellings of an ordering/identity rule must change in lockstep. This rule was already the subject of two high or med plan findings (PF-9934…, PF-2595…, plan.yaml:36–49). The copy nobody remembers goes stale silently, and the CLI could then accept a stale-assistant case the browser rejects, or the reverse.
- **Alternative:** T-07 names one small pure function (inputs: the retained current user message, the retained completed assistant message, the readback messages; output: ok or a rejection reason). It is an added file in `apps/web/src/features/chat/` and sits in the frontend lane that T-07 already holds. T-08 imports it, since T-08 already depends on T-07 (plan.yaml:527). It is a pure comparison of native UIMessages, not a protocol or a seam. It has two real consumers, so it passes the "two adapters = real" test (harness-codebase-design). T-02 expected literals stay independent of the implementation.
- **Disposition:** **apply** (pm, plan.yaml T-07 files and intent, T-08 intent). If pm judges CLI-supplementary status too weak to justify the import, **leave** and say so. **Not DESIGN-touching.**

### U-2 (low): the "newest message only plus threadId, credentials same-origin" shaping names no native transport option
- **File/line:** plan.yaml:503 (T-07), :252 (T-01 records the `DefaultChatTransport` and `useChat` API surface), :369–370 (T-03 allowlist requiring exactly the newest user message).
- **Summary:** `DefaultChatTransport` is pinned at ai 6.0.116, but the plan never says how the "newest message only" body is produced.
- **Cost:** An implementer with no named hook may hand-roll a fetch wrapper or a custom `ChatTransport`, which is the parallel client transport this plan forbids. A full-history POST would also be rejected by T-03 as unknown input. Nothing in the plan pins the option to the exact installed types, so the cost is a probable red and rework at T-07.
- **Alternative:** T-07 names the transport's own request-preparation and credentials options (I expect `prepareSendMessagesRequest` and `credentials`; **unverified against installed types**). T-01's exact-API receipt (plan.yaml:252) also records them, so T-07 uses a verified spelling and does not guess.
- **Disposition:** **apply** (pm, one clause in T-01 and T-07 intent). **Not DESIGN-touching.**

### U-3 (low): the local-session cookie MAC check and the CLI bearer check each need their own timing-safe compare
- **File/line:** plan.yaml:353–366 (T-03, `local-session.ts`), :338–341 (`platform-token.ts`); T-02 tests :310 ("timing-safe comparisons").
- **Summary:** Neither file names a sole owner of the constant-time comparison. `local-session.ts` verifies the HMAC. `platform-token.ts` verifies the bearer. Both read `KAYA_API_STUB_TOKEN` through `env.ts`.
- **Cost:** Two independent compare spellings are probable. One could be omitted or use `===`, and T-02 asserts both only by observable behaviour, which constant-time properties cannot show. The cost is a drifting security-sensitive pair.
- **Alternative:** T-03 names `platform-token.ts` as the only comparison authority and has `local-session.ts` verify its MAC through it. If pm judges it too fine-grained for a plan row, record it as a briefing-row backlog item.
- **Disposition:** **briefing-row backlog** (low; implementation-level, backend lane). **Not DESIGN-touching.**

## Checked and left (no finding)
1. Client UUID check in T-07 `thread-url.ts` (plan.yaml:493, 503) versus T-03 `request.ts` (:369): leave. The client and server are separate guard boundaries, `request.ts` is `server-only` (:352) so no import is possible, and T-02 pins each side independently.
2. Four-name empty-env list in T-01 (:242–243), T-08 (:540) and `.env.example` (:224): leave. T-08 already reuses the T-03 env authority (:540) and prior R-1 covers it. `playwright.config.ts` is T-01-owned and precedes T-03, so it cannot import from it.
3. Focus, recovery and theme matrix restated across T-02, T-07, T-08 and T-10: leave, per prior S-3, because tests and implementation are separately dispatched.
4. Bootstrap and renew via `fetch` in T-07 (:501): leave. D-02 is settled and no native AI SDK equivalent exists for the cookie bootstrap.
5. Readback via `convertMessages(...).to('AIV6.UI')`, `handleChatStream`, `readUIMessageStream`, Astryx `Button`/`TextArea`/`Theme` (DESIGN.md:10): the reuse is already complete. There is no AI Elements and no parallel backend (plan.yaml:234, DEC-012).

## Flag-only, DESIGN-touching summary
None. Every finding applies to plan.yaml only (U-1 and U-2 pm apply, U-3 briefing-row).

## Principles applied
- **Redesign From First Principles** (`references/redesign-from-first-principles.md`, read this run): I treated the "saved exchange" requirement as foundational to the browser chat. That changed U-1 from "add a CLI comment" to "name one owner that both consumers import", and U-2 from "describe the body" to "use the native transport's own option". It did not change U-3, which is a lockstep-drift point.
- `harness-codebase-design` (preloaded skill, cited by skill name, not a craft principle): the "one adapter hypothetical, two real" test is why a shared predicate (two consumers) is justified here but a UUID helper (guards at separate boundaries) is not.

No source, plan, BRIEF, DESIGN, approval or verification action was taken. No T-NN verify command was run.
