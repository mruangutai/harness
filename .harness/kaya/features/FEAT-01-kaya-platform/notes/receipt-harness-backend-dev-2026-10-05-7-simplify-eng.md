# Receipt — harness-backend-dev — 2026-10-05-7-simplify-eng — SIMPLIFICATION angle

**BLUF: PASS, 4 advisory findings (none blocking, none touch DESIGN.md), 5 checked-and-left. Flag-only; nothing edited, nothing executed.**

Angle file followed (only this one): `.agents/skills/harness-simplify/references/angle-simplification.md`. Scope: whole c2 `plan.yaml` (T-01..T-10, D-01/D-02, lanes, panel) + `BRIEF.md`, with route/auth/storage depth emphasis. All plan line numbers are `plan.yaml` as read (raw read for T-06/T-07 intents). Costs are `[INFERENCE]`, unmeasured.

## Findings

### S7-1 (med) — one saved-exchange predicate is stated as server work in T-06 but lives in the client and the CLI
- File/line: `plan.yaml` T-06.intent (:464 "Browser send completion is not a storage claim… Reject old assistant/new-user-only… Recovery repeats GET only with the same predicate; session renewal never replays generation"); same predicate at T-07.intent (:505), T-08.intent (:542), T-02 (:314,:316), T-10 (:608), BRIEF SC-02/SC-10. T-06.files (:455-458) are only the two route handlers.
- Summary: the "SAME-thread GET contains current user ID + CURRENT assistant ID in order with matching parts" check is a comparison of *streamed* result vs *readback*. A GET handler cannot reject anything; the comparison is implemented in `chat-panel.tsx` (T-07) and again in `platform-live.ts` (T-08). T-06 nevertheless restates it as an obligation and its verify (:460) claims to cover "second-turn missing/stale/partial/mismatched/order failures" (:466) with no T-06-owned file that holds the predicate. Dead/misplaced reference: a client rule written into the server task.
- Concrete cost: a T-06 dispatch cannot tell what it must implement versus what the integration test only observes; three independently written copies of one comparison (browser, CLI, T-06 test oracle) can drift on what "matching parts" and "order" mean. [INFERENCE] one extra send-back or a vacuous server test.
- Alternative: reduce T-06 to server-observable facts (stream carries native assistant ID/parts; GET returns saved messages with those IDs/parts in order; no model call), drop "Reject…/Recovery repeats…/renewal never replays" from T-06 and keep T-07 as the single predicate authority text, with T-08/T-10/T-02 saying "same predicate as T-07" instead of re-spelling it. No new module or seam.
- Disposition: apply (pm plan: T-06.intent, optionally T-08/T-10 wording). DESIGN: no.

### S7-2 (low-med) — readback "sanitize unsupported parts" and client "matching persisted parts" can contradict
- File/line: T-05.intent :431-433 ("sanitize metadata and unsupported parts"); T-06.intent :464 and T-07.intent :505 ("completed ordered persisted parts matching the stream/streamed parts"; "label unsupported parts safely").
- Summary: two layers decide what happens to non-text parts (server drops/sanitizes on GET; client labels). The confirmation predicate compares persisted parts to streamed parts, but never states the comparison domain. If the model (the plan itself anticipates adaptive thinking, :427) emits a part the readback sanitizes away, the exact-match predicate fails forever while the exchange is genuinely saved, and Check saved messages cannot ever pass.
- Concrete cost: [INFERENCE] a permanently "incomplete" honest-but-unconfirmable turn that only appears with a real provider, invisible to every fixture-based gate (offline fixtures use text parts only, :316).
- Alternative: state once, in T-05 (readback), which part types readback preserves vs sanitizes, and have the T-07 predicate compare exactly that preserved set (or say text parts only). One sentence replaces two spellings.
- Disposition: apply (pm plan: T-05.intent + T-07.intent clause). DESIGN: no.

### S7-3 (low-med) — route-facing authorization interface is split across two modules with no named entry point
- File/line: T-03.files :338-341 (`platform-token.ts`, `local-session.ts`); T-03.intent :358-366 (cookie, Origin/Fetch-Metadata, *and* "CLI bearer accepted only with exact loopback Host and no browser Origin/Fetch-Metadata… 401/403/503" all specified under `local-session.ts`; `platform-token.ts` is given no behaviour in its own intent); T-06.intent :462 ("GET/POST authorize before parsing").
- Summary: the one decision "which credential applies and what status results" is described inside `local-session.ts` while bearer comparison lives in `platform-token.ts`. Neither T-03 nor T-06 names the single function both route handlers call.
- Concrete cost: two route handlers (and the session bootstrap route) can each re-assemble the order of bearer/cookie/metadata checks; a reader tracing "where does 401 vs 403 come from?" must hold two modules plus the routes (layers and state axes of `harness-codebase-design`). Wrong branch order here is the repo's fail-open failure mode.
- Alternative: name the existing interface, not a new layer: `local-session.ts` exports the one request-authorization function (browser cookie or CLI bearer, returns allow or classified denial), `platform-token.ts` only provides the timing-safe bearer verification it calls; T-06 handlers call only that export.
- Disposition: apply (pm plan: T-03.intent one sentence, T-06.intent reference). DESIGN: no.

### S7-4 (low) — `server/db/supabase.ts` is a production-tree module whose only consumer is the CLI probe
- File/line: T-03.files :344, T-03.intent :370-372; T-08.intent :540 ("Reuse T-03 env/admin operations"); routes use pg via T-05 storage, never the admin client (T-05 :417-421, T-06 :462).
- Summary: deletion test — delete `supabase.ts`: the send/readback runtime is unaffected; the complexity reappears only in `platform-live.ts`/`smoke:supabase`. It is a server-only module with its own unit test and service-role setting (`supabase.test.ts`, `SUPABASE_SERVICE_ROLE_KEY`) shipped in the app tree for a probe.
- Concrete cost: [INFERENCE] reader must learn that `server/db` mixes the app's data path (none) with a probe helper; service-role key handling sits in the app tree although the app never uses it.
- Alternative (if wanted): state in T-03 that `supabase.ts` exists solely for the T-08 probe so nobody wires it into routes. Moving it out of `apps/web/src/server/**` is *not* recommended: it reopens lane rows, SC-04's smoke contract and the five fixed setting names.
- Disposition: leave, or briefing-row at most (clarifying sentence); no apply of relocation. DESIGN: no.

## Checked and left (not findings)
- D-01 direct/session-5432 and "no transaction 6543/no fallback" restated in T-03/T-05/T-08/T-10/tests: each consumer enforces a different edge (validate, connect, apply, document); settled by prior S-6/R-3 skips, mechanism not reintroduced.
- Two-route split (`/api/platform`, `/api/platform/session`): different auth rules and methods; deleting the split moves bootstrap into the chat route, adding branching. Earns its keep.
- `index.ts` / `storage.ts` / `readback.ts` split: composition home, one pooled store, DB-only reader that must not touch the agent (SC-07); deletion would put model construction on the GET path.
- Overlapping `*.test.*` lane rows: prior S-4 skip; no new mechanism.
- Combined T-07 Vitest invocation: not re-raised (prior E-1).

## Principles applied
- Redesign From First Principles (read this run): framed S7-1/S7-2 by asking where the saved-exchange rule would live had it been foundational, and found it written in four tasks instead of one authority; applied the propagate-through-every-reference test.
- Delete First (read this run): S7-1/S7-4 judged by removal first (drop the server-side restatement; confirm the probe-only module is not a layer to add to).
- `harness-codebase-design` (skill, not a craft leaf): deletion test and layers/state reader-load axes for S7-3/S7-4.

## Constraints honored
Settled stack, D-01/D-02, main-session lanes T-01/T-09, red-first T-02, native stream/hydration/persistence, financial/Gmail/account exclusions untouched; no source, plan, BRIEF or DESIGN edit; no verification run.
