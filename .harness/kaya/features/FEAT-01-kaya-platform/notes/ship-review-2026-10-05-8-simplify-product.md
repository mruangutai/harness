# FEAT-01-kaya-platform — plan revision c2 (thin browser chat), ready for operator review — UNSIGNED

BLUF: the plan now promises a minimal browser chat loop (send → real Anthropic reply via Mastra → restart → reopen the same conversation in the same UI) on the accepted Astryx + AI SDK UI (@mastra/ai-sdk) stack, with DESIGN.md and an interactive prototype for approval. 10 tasks, 57 anchors, `plan-merge.py check … --code-root` exit 0 at 0b0b141a. Nothing is signed, mirrored, built or implemented.

## Done when — by perspective (verbatim, BRIEF.md)

**operator** — I can start from a fresh clone, follow one documented setup sequence, send a message in the browser, and see my message and a real Anthropic-backed answer in the conversation. After restarting the local application, I can reopen that same conversation in the same browser interface and see the saved exchange without asking the model again; pending, restoration and failures are visible and honest.

**code maintainer** — I can reproduce the supported runtime, dependencies and checks, identify the protected server boundary and operational data ownership, and extend the small chat surface without a competing message-state protocol. The setup documents distinguish researched compatibility from exercised evidence and do not claim account authorization, financial functionality or production operation.

## Success criteria by perspective (full text in BRIEF.md `## Success criteria`)

operator — all `verify: uat` (browser UAT script: notes/uat-browser-c2.md, U-01..U-13, draft):
- SC-01 fresh-clone sequence; http://127.0.0.1:3000 shows labeled input, Send, transcript; English lang, one main, one h1; WCAG AA both themes; visible focus; usable at 320px and 200% text.
- SC-02 send a nonce → user message, pending state, real Anthropic-backed Mastra reply via the UI stream; "saved" only after same-thread DB readback of the CURRENT user+assistant identities with matching ordered parts; failures shown honestly, never as a fake assistant message.
- SC-03 restart `pnpm dev`, reopen the recorded conversation URL → prior nonce and reply restored from hosted Postgres with no model request (even with provider key absent); missing/mismatched threads are errors.
- SC-04 `pnpm smoke:supabase` proves privileged connectivity, `mastra` schema ownership, PUBLIC/anon/authenticated denial and the specific unexposed-schema Data API rejection.

code maintainer — all `verify: inspection` at review_sha with mandatory QA red-first/green receipts:
- SC-05 server-only guards; no key/token/connection string in client bundle, parts, errors, logs; D-02 cookie boundary, Host/Origin/fetch-metadata checks, no permissive CORS; KAYA_API_STUB_TOKEN server/CLI-only.
- SC-06 ARCHITECTURE.md Source organization (apps/web, globs, one lockfile, strict tsconfig.base, feature-owned UI, server-only entries, colocated tests, __tests__, root tests/e2e browser scenarios).
- SC-07 PostgresStore schemaName mastra, one HMR-safe pool/store owner, TLS, bounded pooling; GET restoration never constructs/calls the model; recall/title/working-memory model calls disabled.
- SC-08 unit/functional/integration/component/ui/typecheck runners executable, each test selected once in its kind, red/zero-selection demonstrations; `pnpm verify:platform` runs offline suites incl. real browser acceptance after predecessors exist.
- SC-09 README/docs/PLATFORM.md/docs/platform-compatibility.md: fresh-clone browser loop, five setting names, cookie vs bearer limits, researched vs exercised pins separated.
- SC-10 chat UI/routes/tests: Astryx presentation, AI SDK UI message state via @mastra/ai-sdk, explicit v6 transport, parts rendering, URL thread recovery, keyboard submit (IME/Shift+Enter safe), labels, focus retention, pending/restore announcements, both themes at 320px/200%.

## Tasks (10, unchanged count; every task re-intented)

T-01 workspace + browser verification tooling (main-session-direct) → T-02 browser+server red tests (qa) → T-03 settings/local session/request contracts (backend) · T-04 mastra schema grants (data) → T-05 Mastra streaming memory + model-free readback (backend) → T-06 protected v6 stream + readback routes (backend) · T-07 Astryx browser conversation + restoration (frontend, depends T-02) → T-08 unmocked browser denial + live probes (backend) → T-09 six-runner cutover + terminal gate (main-session-direct) → T-10 docs (documentor).
Main-session seams: T-01 and T-09 (root/shared config, apps/web package/next/tsconfig, .env.example, root Playwright config, .harness/harness.json) — `lanes:` in plan.yaml.

## Local access proposal (D-02, revised)

Loopback-only same-origin routes; a server-bootstrapped HMAC-signed (keyed by server-only KAYA_API_STUB_TOKEN) HttpOnly SameSite=Strict cookie with exact Host/Origin/Fetch-Metadata guards; the raw token stays server/CLI-only and never reaches browser JS; fixed resource identity; no account auth (Kaya #2). Renewal never replays generation.

## Transport / compatibility research (not exercised)

AI SDK UI `useChat`/`DefaultChatTransport` ⇄ @mastra/ai-sdk `handleChatStream` v6 ⇄ Mastra agent. Researched pins: Node 24.21.0, pnpm 11.2.2, Next 16.3.8, React 19.3.0, @mastra/core 1.74.0, @mastra/memory 1.35.0, @mastra/pg 1.29.0, @mastra/ai-sdk 1.10.6, ai 6.0.116, @ai-sdk/react 3.0.118, @ai-sdk/anthropic 3.0.103, Astryx 0.6.5, @playwright/test 1.63.0, claude-sonnet-5-5 — notes/research-FEAT-01-kaya-platform-draft-plan-c2.md. Install/typecheck/tests/UAT establish compatibility later; T-01 stops on incompatibility.

## Design and prototype

DESIGN.md (120 lines): Astryx substrate, both-theme palette, type, spacing, component direction for composer/transcript/pending/error/restore, keyboard and focus continuity, 320px/200%. `needs_prototype: true` (user-operated send/save/recover interactions). Prototype: notes/prototypes/FEAT-01-kaya-platform/index.html — serve `python3 -m http.server 4179` from that directory, open http://127.0.0.1:4179/ (exact commands in notes/mockups/design-thin-chat-c2-apply.md); screenshots + rendered DOM 01–21 (light/dark, 320px, 200%, error and recovery states) in the same directory. Simulation only: fixtures/localStorage, not SDK/Anthropic/Postgres/restart proof.

## Evidence

- Panel cycle 2: scope (code-reviewer) FAIL high, design (ui-reviewer) FAIL high/med/low, should-not-exist SKIPPED (fable-advisor unavailable), goalcheck ran — all 5 PF resolved in-run (plan.yaml `panel:`; runs/2026-10-05-6-plan-product/digest.md).
- Goalcheck: operator pass, code maintainer pass vs intake + answers file; all ten SCs not_met until build/UAT (notes/research-FEAT-01-kaya-platform-goalcheck-plan.md).
- Simplify c2: 12 mechanisms — F01/F02/F04/F05/F08/F12 applied; F03/F09/F10 backlog rows; F06/F07/F11 left (runs/2026-10-05-7-simplify-eng/digest.md, notes/research-FEAT-01-kaya-platform-simplify-apply-c2.md).
- Final check: `CHECK …/plan.yaml against …/kaya/FEAT-01-kaya-platform: 10 task(s), 57 anchor(s) resolved, 0 failure(s)` — orchestrator re-run, exit 0.

## Source ticket (Kaya #14) changes for Main

Replace the static landing page / API-command loop summary with the browser loop above; replace the SC list with SC-01..SC-10 as grouped here; add DESIGN.md + prototype review as part of the approval; state D-02 as revised; keep exclusions (financial renderers, Gmail, extraction, uploads, login/account auth, multi-conversation, production). Status remains plan / pending approval.

## Bookkeeping limitations (disclosed, not repaired)

- cycles_used 1/10 covers run 2026-10-05-6 (designer send-back). Historical run 2026-10-05-2-plan-product FAIL carries no attributed cycle (pre-existing); INV reports "1 cycle for 2 FAIL runs". Not inflated.
- runs/2026-10-05-3-simplify-eng/digest.md is a refused-return prose digest (pre-existing).
- No github.build_entry (INV-37) — expected before signature; `gh-sync.py open` is the signed successor's act.
- check-state.py run from the worktree resolves the main-checkout feature dir (no plan.yaml there → INV-34); the feature-record `--changed` hook over the worktree is the per-feature read used here.
