# DESIGN — Kaya local chat

The minimal browser conversation needs an interactive prototype. This contract and the linked prototype are **pending user approval bundled with the unsigned plan signature**; neither is product implementation or proof of live provider/storage behavior. The earlier document-only prototype ruling is void.

## Substrate

- system: `@astryxdesign/core@0.6.5`, `@astryxdesign/theme-neutral@0.6.5`; no second component substrate, AI Elements or executable model UI.
- provisioned: **no verified product installation**. Designer independently read [core exact-release metadata](https://registry.npmjs.org/@astryxdesign/core/0.6.5), [neutral exact-release metadata](https://registry.npmjs.org/@astryxdesign/theme-neutral/0.6.5) and [core exact-release README](https://unpkg.com/@astryxdesign/core@0.6.5/README.md) on 2026-10-05. They report core 0.6.5, React/ReactDOM >=19, StyleX ^0.19.0, neutral's exact core peer 0.6.5 and prebuilt CSS. This verifies registry/documentation evidence, **not installed Next/runtime compatibility**. PM's broader pins remain researched proposals in `notes/research-FEAT-01-kaya-platform-draft-plan-c2.md`, heading “Exact-release research and limits”. T-01 owns installed verification.
- Product convention: ordered `core/reset.css`, `core/astryx.css`, `theme-neutral/theme.css`; `Theme` with `neutralTheme` from `theme-neutral/built`, mode `system`. Add only this contract's scoped typography, accessible control border/target and page layout overrides. No StyleX build plugin is needed per the published README, not an exercised product claim.
- Components: Astryx `Theme`, `Button` (primary Send; secondary recovery), `TextArea` (visible Message label). Use semantic HTML header, ordered transcript list/articles, form, status and alert wrappers. Exact Button/TextArea/Theme published declarations were read; do not guess component props. Prototype follows the documented no-build import-map/React.createElement convention with updated exact pins, not README's old 0.4.1 example.

## Palette

Local semantic tokens use the following **opaque** colors in both themes. Unlisted Astryx component internals retain neutral 0.6.5; they must still pass acceptance. Color never replaces role labels, status wording or error text.

| Token | Light | Dark | Used for |
|---|---|---|---|
| bg | #f1f1f1 | #1b1b1b | document background |
| surface | #ffffff | #262626 | conversation and composer |
| text | #000000 | #ffffff | transcript, labels, headings |
| text-muted | #474747 | #9e9e9e | helper, UUID, incomplete notes |
| accent | #1b1b1b | #f1f1f1 | primary action; user message rail |
| on-accent | #ffffff | #111111 | primary action label |
| border | #d4d4d4 | #525252 | decorative dividers/assistant rail, not sole control identification |
| control-border | #767676 | #9e9e9e | textarea and secondary control outlines |
| danger | #76000c | #ffc4be | error text and outline |
| danger-surface | #fff0ee | #5b2b28 | error panel |
| success | #00490b | #a4d6a3 | confirmed saved/restored status |
| focus/link | #00458c | #a1caff | focus outline and underlined links |

- Normative contrast: WCAG AA >=4.5:1 normal text, >=3:1 large text and identifying control/focus graphics. Disabled controls are visually disabled but never the only way a user can discover a failure reason. Decorative divider contrast is not control identification.
- Measured on the composed prototype: transcript 21.00:1 light / 15.13:1 dark; muted-on-surface 9.29:1 / 5.65:1; textarea border 4.54:1 / 5.65:1. Captured dark error text/background is 7.63:1. Sources: `notes/prototypes/FEAT-01-kaya-platform/contrast-evidence.json` and corresponding DOM/screenshot files. These measurements cover those rendered pairs, not a blanket accessibility certificate or product pass. Light error state and screen-reader delivery remain implementation-review obligations.

## Type

- family: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for body, controls and headings; `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` only if code is displayed later (no code renderer in this scope). Override neutral font-family tokens consistently; no webfont requirement or silent Figtree dependency.
- complete UI scale at a 16px root: 14 / 16 / 20 / 24px, expressed as .875 / 1 / 1.25 / 1.5rem. No 12px essential text.
- 14px: UUID, supporting copy, progress, incomplete notes, limits; 16px: transcript, Message label, controls, error body; 20px: empty-state h2; 24px: h1.
- weights: 400 body/supporting, 500 controls, 600 headings/role labels. Line heights: body/supporting/controls 1.5; h2 1.4; h1 1.25. h1 letter spacing -.025em; eyebrow .04em; no all-caps message content.
- All text enlarges with browser text settings. Contract uses rem, not a fixed font-size lock on the document. Captured 200% fixture sets root 32px; it is text-resize evidence, not a claim that every browser zoom mode was exercised.

## Spacing and layout

- unit: 4px. Space ramp: 4 / 8 / 12 / 16 / 20 / 24 / 32px. Borders 1px, role rail/focus outline 3px, status dot 8px are geometry exceptions.
- radius: 8px controls/errors, 12px conversation container/empty mark, 9999px local-operator badge. No modal, shadow stack or floating chrome.
- container: max-width 768px; at >=600px 24px document gutters, 32px top/bottom margin; below 600px 16px gutters, 24px margin. Header gap 16px and bottom separation 24px.
- transcript: 24px padding at >=600px, 20px vertical/16px horizontal below; min-height 240px desktop / 200px narrow (never fixed height); message gap 24px, role-to-body 8px, rail-to-copy 16px. Content expands in normal document flow; no nested scrolling transcript.
- composer: 20px top, 24px horizontal/bottom; narrow horizontal/bottom 16px/20px. Textarea three rows, min-height 96px, 12px inner padding, vertical resize allowed. No fixed-height text clipping.
- buttons: >=44px target height and >=44px width, 10px vertical/16px horizontal padding, labels wrap if necessary. Visible focus 3px outline with 3px offset; never clipped by container overflow.
- breakpoints: 600px only. Header stacks below it; composer footer flex-wraps, helper uses flexible width and Send stays in reading order. The UUID and every message use overflow-wrap:anywhere; preserve message newlines. No document horizontal scrolling at 320 CSS px or 200% enlarged text, including errors and long identifiers. All controls remain reachable by vertical page scrolling, not overlays/sticky footers.
- light/dark: follow OS through Astryx `Theme mode="system"`; no product theme preference UI required. Prototype-only controls permit reviewing both modes and 200% text.

## Component direction

### Page and transcript

One descriptive h1, “Kaya local chat”, one main landmark and one single-conversation panel. English `html lang="en"`. Header says local platform and local operator, not a logged-in account. Empty state explains a harmless message and preserving its URL. Do not insert an assistant welcome message into persisted transcript.

Above transcript show `Conversation · <full UUID>` once assigned and a native underlined “Conversation URL” link to the same URL, usable with browser copy/bookmark/open commands. Before send: “A conversation URL is created when you send.” No clipboard API or additional permission flow is necessary. UUID is selection, **not authorization**.

Transcript is a named section “Conversation transcript”, an ordered list of articles in SDK message order. Visible roles are “You” and “Kaya”; accessible article names are “Your message” and “Assistant message”. Render UIMessage text parts as escaped plain text, preserving IDs/order/newlines. Unsupported parts get a safe “Unsupported response part” label, not executable HTML, tool cards or a fake answer. No chat bubbles that depend on alignment/color alone to distinguish roles.

### Composer and keyboard

Visible Astryx TextArea label “Message”, followed by “Enter to send · Shift+Enter for a new line” and a readable 2,000-character limit/count. Accessible description associates both helper and limit. Prevent empty/whitespace-only or over-limit send; over-limit input stays editable with visible explanation and `aria-invalid`. Client length/count must match T-03's combined text validation; do not use Astryx's grapheme counter with a different server rule.

Send is a real submit button. Enter submits once; Shift+Enter inserts newline; composing IME events/keyCode229 never submit. Prevent double-submit while bootstrapping/restoring/sending/confirming save. While busy keep composer focusable/read-only and text preserved; Send is disabled and displays “Sending…” during the turn. Do not clear draft until confirmed persistence. Preserve draft on provider/storage/auth/network rejection; never trigger generation automatically after recovery.

No initial autofocus. Tab order follows document order: skip link, conversation link when present, recovery action when present, composer, Send. On an explicit send retain/return composer focus; on asynchronous completion only return it if focus is still within the composer/submit action, never steal it from a link/recovery control. Restore/reload does not autofocus. No focus trap, modal or token/account entry. Native selection/copy of transcript remains available.

Recovery keyboard continuity is required for `checkSaved`, `restore` and `renew`: on explicit activation keep the same recovery button mounted/focusable while busy, retain its label and use `aria-disabled="true"` with a guarded handler (not native disabled). Retain the error panel until the operation settles; status announces progress separately. Do not unmount the focused action at operation start. On success deliberately focus the composer before removing the action, but only if focus is still on that action; if the user moved elsewhere, preserve that prior region. On failure retain the reachable action and its focus; never drop focus onto body. Restoration on page load has no autofocus. Renew may continue DB-only restore/check; never replay generation.

### State and recovery contract

| State | Visible status/copy | Behavior |
|---|---|---|
| Session bootstrap | “Preparing local access…” | Same-origin session request; no provider request; Send unavailable |
| Empty ready | “Ready to send” | No fabricated conversation; create UUID just before first send |
| Submitted | “Waiting for reply…” | User text visible, marked “Not yet confirmed saved”; draft retained |
| Streaming | “Receiving reply…” | Safe partial assistant text, “Incomplete until saved messages are confirmed” |
| Stream finished | “Checking saved messages…” | Still busy; no saved claim based on HTTP200/stream finish |
| Readback confirmed | “Exchange saved” | SAME thread's GET contains the current user and CURRENT completed native SDK assistant IDs, in current-turn order with the completed ordered parts matching the streamed result; only then adopt persisted SDK messages and clear draft |
| Existing URL restoring | “Restoring saved conversation…” | Bootstrap then DB-only GET; no generation, no provider-key requirement |
| Restored | “Conversation restored · no model requested” | Display recalled messages/IDs/order in same interface; do not silently append/replay |
| Provider unavailable / empty response | “Reply unavailable” | Safe explanation; no assistant invented. Keep failed turn/draft distinguishable; intentional future Send only |
| DB/config/readback failure | “Save not confirmed” or “Could not restore conversation” | Visible error; partial text remains incomplete, prior saved messages remain distinct. “Check saved messages” / “Retry restoration” performs GET only |
| Interrupted stream/network | “Connection interrupted” | Partial reply incomplete; no saved/success claim; check local app then GET-only recovery |
| Expired local cookie (401) | “Local access expired” | “Renew local access” bootstrap action visible; never auto-replay failed generation; restore may continue only as readback |
| Host/Origin/access denied (403) | “Local access denied” | Explain exact approved loopback URL/local setup; never solicit a token or promise renewal bypass |
| Malformed URL / rejected input (400) | “Invalid conversation URL” / “Message rejected” | Preserve URL/draft, safe correction guidance; no new thread replacement |
| Missing/resource-mismatched thread (404) | “Conversation unavailable” | Explain original URL did not match saved conversation; no silent UUID replacement and no history manager |


Readback must bind to native SDK identity, not a custom message-state protocol: retain the current submitted user ID and the completed assistant ID/ordered parts from the SDK stream. Require both in the same recalled thread, with assistant following the corresponding user in the current turn, and matching completed persisted parts (not merely nonempty text or any earlier assistant). A prior U1/A1 followed by saved U2 but absent A2 is **incomplete**, as are stale, partial, mismatched-ID/order/parts readbacks or an unfinished stream. Keep the visible streamed A2 and submitted draft; do not replace them with stale recall, clear draft, mark saved or announce success. GET-only recovery repeats this same predicate; successful recall of an older exchange is not confirmation of the pending exchange. A normal reopen with no pending current turn may display recalled messages without claiming a new exchange saved.
Errors show a fixed safe title + cause/action paragraph inline between transcript and composer. No raw vendor exception, secrets, stack, database URL or cookie/token. Provider/database/auth configuration failures are honest setup problems, not assistant messages or successful saves. No fallback model, automatic resend, fabricated persistence or automatic new conversation.

One separate `role="status" aria-live="polite" aria-atomic="true"` announces coarse progress, saved and restored transitions; not every stream delta. Named transcript carries `aria-busy` while restoring/receiving. Error text uses `role="alert"` once per failure, outside a busy transcript, with recovery button outside the alert text. Do not make the entire transcript live or announce every streamed token. Status and error remain visible for non-screen-reader users; safe text labels accompany the dot/color. Actual screen-reader timing, focus behavior and full WCAG AA conformance must be evaluated on the implemented product, not inferred from these attributes.

### Transport, identity and local access alignment

This is a presentation contract, not a second message-state protocol. T-07 uses actual `@ai-sdk/react useChat` and `ai DefaultChatTransport` with `@mastra/ai-sdk handleChatStream` explicitly `version:'v6'`, native UI SSE (wire header v1), Mastra-only backend. See `plan.yaml`, “Build minimal Astryx browser conversation and restoration”, and PM research “End-to-end browser and transport contract”.

Root `/?thread` absent starts empty. `crypto.randomUUID()` sets `/?thread=<uuid>` via URL replacement before first send; do not mount-restore that unsaved UUID during initial send. Reopening an existing UUID bootstraps local cookie then GETs the same thread; malformed/missing/mismatched results do not create a replacement. Product transcript/credentials are **not localStorage authority**. GET uses DB-only Mastra memory recall and converted v6 UIMessage parts; no model construction/generation/title/semantic-model recall, even with provider key unavailable. Confirmed completion requires persisted readback, not stream completion alone.

D-02 local HttpOnly cookie grants trusted local-machine access only; no full account authorization. KAYA_API_STUB_TOKEN/provider/database secrets remain server-only, never public environment variables, browser storage, rendered copy or response metadata. The interface has no auth/account form.

## Prototype and approval

- needs_prototype: **true**.
- why: A person now sends, waits, handles failures and reopens a saved browser conversation; the operator must judge these interactions before implementation.
- prototype: `notes/prototypes/FEAT-01-kaya-platform/index.html`.
- disposition: **pending user approval bundled with the pending plan signature**. UI reviewer Mode A reads this contract and the current served prototype first. No agent may mark user approval, live UAT, implementation or ship-readiness from screenshots.
- Serving/open instructions, exact correction capture commands, typed designer fields and findings disposition: `notes/mockups/design-thin-chat-c2-apply.md`. Original c2 receipt/evidence remains preserved.
- Prototype has real Astryx CDN Theme/Button/TextArea, a persistent simulation disclaimer, and explicitly review-only theme/text/send/reopen state controls. It simulates bounded delays and responses with browser fixtures. Its localStorage fixture, custom simulation state and review controls are **throwaway design evidence, never production scaffolding/callsite guidance**. It does not exercise AI SDK transport, Anthropic, Mastra, hosted Postgres or application restart persistence.

## Out of scope

- Login/account UI, history sidebar, multiple-conversation management, uploads/attachments, financial tools/result renderers, Gmail/extraction, deployment/production operation.
- Stop/regenerate/edit/delete controls, retry-generation automation, nested modals, alternate design systems and model-generated executable UI.
- Product code, install/build/test/formatter execution or plan signature in this revision. Existing product acceptance SC-01/02/03/10 remains future QA/inspection and operator live UAT; prototype capture does not discharge it.
