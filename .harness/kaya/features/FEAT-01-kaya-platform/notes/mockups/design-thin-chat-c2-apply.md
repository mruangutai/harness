# Thin browser chat — c2 owner correction

**Current-turn confirmation and recovery focus corrected; namespaced browser design evidence captured. User approval remains pending, bundled with the unsigned plan.** Original c2 receipt, capture.mjs, 01–11 screenshots/DOM and original rendered/contrast JSON are unchanged. No plan/BRIEF, product code, install/build/test, reader rerun, signature or gh-sync was performed. This actual designer send-back consumes lead cycles_used=1; subsequent PM normal apply consumes zero.

## Designer fields

- contract: updated
- needs_prototype: true
- why: Sending, save uncertainty and keyboard recovery are user-operated interactions requiring bundled prototype approval.
- mockups: [notes/prototypes/FEAT-01-kaya-platform/13-light-stale-apply.png, notes/prototypes/FEAT-01-kaya-platform/16-light-320-200-database-apply.png, notes/prototypes/FEAT-01-kaya-platform/17-dark-320-200-auth-busy-apply.png]
- prototype: notes/prototypes/FEAT-01-kaya-platform/index.html
- direction_choices: Current native SDK assistant identity + completed ordered parts selected; latest user + any assistant rejected as stale-turn false success. Mounted focusable recovery action while busy selected; removing/disabling the focused button rejected. Explicit success focus to composer selected only while focus remains on recovery; stealing focus from another region rejected. Normal-flow errors/recovery retained; no new production controls or scope.

## Findings disposition

All original kinds/severities remain unchanged; evidence below is relative to `../prototypes/FEAT-01-kaya-platform/`.

- **ui-reviewer med / code-reviewer high, substance, scope none — current-turn confirmation: applied.** DESIGN “Readback confirmed” and “State and recovery contract” now require the corresponding current user and completed native SDK assistant IDs, current-turn order and completed ordered persisted parts. Prototype `confirmed` rejects missing/stale/partial/mismatched identity/order and preserves the visible reply/draft on both initial and recovery readback. `13-light-stale-apply` explicitly records U1/A1/U2 persisted without A2, while visible A2/draft remain incomplete; `13-light-partial-apply`, `13-light-mismatch-apply`, `13-light-order-apply` show other rejection fixtures. `14-light-*-check-*-apply` retain incompleteness on unchanged readback; `15-light-*-check-success-apply` confirms only a now-complete GET fixture. Prototype shape/identity is simulated, **not native SDK execution**; frontend must use SDK identities, never copy this fixture protocol.
- **ui-reviewer high, substance, scope none — recovery focus: applied.** DESIGN “Composer and keyboard” specifies stable busy action, guarded activation, success destination and retained failure action for checkSaved/restore/renew. Prototype keeps the same Astryx button/error mounted while busy and moves focus before removal on success only if still on recovery. Astryx 0.6.5 overwrites forwarded aria-disabled; its DOM ref sets the attribute while the handler independently prevents activation. `17/18-{light,dark}-320-200-{database,auth}-{before,busy,failure|success}-apply` and `20/21-{light,dark}-320-200-restore-*-apply` capture Enter activation: BUTTON before/busy/failure, TEXTAREA success. JSON `recovery.sameNode=true` evidences node continuity. Page-load BODY focus in the restore error captures is intentional no-autofocus, not action-triggered focus loss.
- **ui-reviewer low, advisory, substance, scope none — error evidence: expanded.** `16-{light,dark}-320-200-{database,provider,auth,network}-apply` and `19-{light,dark}-320-200-restore-apply` contain screenshots + rendered DOM. The light desktop rejection/recovery series also captures error panels. Every capture reports document width equal viewport (1200 or 320); enlarged narrow states report root 32px. Inspected light narrow DB and dark narrow renewal-busy full-page screenshots; errors/actions remain in normal flow with no horizontal overflow. This is 200% text enlargement, **not actual browser-zoom certification**. PM still owns explicit T-02 and future UAT coverage; this artifact does not apply those plan changes.

`rendered-evidence-apply.json` is the correction manifest: exact capture names, Chrome/154.0.8037.93, URL, theme/width/root size, visible messages, actual saved browser fixture, draft, focus and busy/same-node state. Each name has matching `.png` and `.dom.html`. Exceptions array is empty in the completed capture. No new blanket contrast/WCAG or screen-reader delivery claim is made.

## Exact run / capture instructions

Server was started successfully and remains session-hosted. Open **http://127.0.0.1:4179/**; if stopped, rerun:

```bash
python3 -m http.server 4179 --bind 127.0.0.1 --directory /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform
```

Capture used the already-installed Chrome and Node; no installation. Start Chrome, then run the second command in another terminal (successful script closes Chrome):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-first-run --no-default-browser-check --user-data-dir=/tmp/kaya-design-c2-apply-chrome --remote-debugging-port=9229 about:blank
node /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform/capture-apply.mjs
```

**Capture warning:** script clears this prototype origin's localStorage/sessionStorage to obtain a known browser-only fixture; use the dedicated port/profile. It writes only `*-apply.png`, `*-apply.dom.html`, `rendered-evidence-apply.json`; reruns replace correction evidence, not baseline proof. Internet access to pinned CDN assets is required. First two capture attempts timed out waiting for recovery busy: the vendor overrides forwarded aria-disabled, and the original CDP Enter omitted its carriage-return text needed for native button activation. Both were corrected; the third capture completed (exit 0). These failures are preserved here, not relabeled as successes.

Manual review: send one successful turn; choose missing-current-assistant/partial/mismatched-ID/order for next send and observe incomplete reply/draft. Unchanged recovery must not save; review-only “Read now-complete current exchange” simulates a later GET of the already-streamed reply, never generation. Review theme/text and next-reopen selectors exercise errors. Product has none of these review controls; all replies/storage/access are explicitly simulated. No Anthropic/Mastra/Postgres, product restart or product UAT was exercised.

Open questions: none. Bundled user approval remains pending. PM applies plan findings next; no reviewer verdict is superseded or rerun by this owner receipt.
