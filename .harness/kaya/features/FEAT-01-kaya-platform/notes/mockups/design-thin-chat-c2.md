# Thin browser chat — design c2

**Contract and clickable Astryx prototype complete; user approval remains pending with the unsigned plan signature.** The old document-only prototype ruling is void. Product CODE was untouched; no product install/build/test/formatter, provider/database call, signature or gh-sync was run.

## Designer fields

- contract: written
- needs_prototype: true
- why: A person sends, waits, handles failures and reopens a saved browser conversation; the operator must judge these interactions before implementation.
- mockups: [notes/prototypes/FEAT-01-kaya-platform/03-light-saved.png, notes/prototypes/FEAT-01-kaya-platform/05-dark-database-error.png, notes/prototypes/FEAT-01-kaya-platform/11-dark-320-200percent.png]
- prototype: notes/prototypes/FEAT-01-kaya-platform/index.html
- direction_choices: Single normal-flow transcript + multiline composer selected; sidebar/history manager rejected as excluded scope; floating/sticky composer rejected because narrow/enlarged text can be obscured; stream-finished success rejected because DB readback must confirm save; token/account form rejected because local HttpOnly session is server-bootstrapped; static-only mockup rejected because interaction approval is required.

## Open and operate

This exact command was run and port 4178 became ready:

```bash
python3 -m http.server 4178 --bind 127.0.0.1 --directory /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform
```

Open **http://127.0.0.1:4178/** in a browser. If the session-hosted service has stopped, rerun the command; no dependency installation is required. Internet access to pinned esm.sh and jsDelivr assets is required; failed loading is visibly reported, never replaced with fake controls. Actual Astryx Theme/Button/TextArea are used through the vendor-documented no-build CDN convention. Core/neutral 0.6.5 registry peers and exact README were independently read; **no verified product installation or Next/runtime compatibility claim**. See `../../DESIGN.md`, “Substrate”.

Type a harmless message and press Enter or Send. Watch pending, simulated streamed text, confirmation, then use the Conversation URL to reopen the same fixture. Expand **Prototype controls · simulated states** for next-send provider/database/auth/interrupted-stream results, reopen database/auth/missing results, light/dark/system and 200% text. “Reopen same URL” reloads the fixture. Recovery buttons renew local access or read saved messages without simulated generation. Reset is explicitly demo-only. No multiple-conversation/history feature is proposed.

The always-visible disclaimer and simulated reply identify browser-only fixtures. localStorage is **prototype simulation only**, not proposed product storage; product restoration uses same UUID URL + protected DB-only GET + SDK setMessages. This prototype does not exercise AI SDK wire transport, Mastra, Anthropic, hosted Postgres, actual app restart, account authorization or live acceptance.

## Current captured evidence

Installed Chrome capture command (run successfully, capture browser then closed):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-first-run --no-default-browser-check --user-data-dir=/tmp/kaya-design-c2-chrome --remote-debugging-port=9228 about:blank
```

With that browser and the prototype server running:

```bash
node /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform/capture.mjs
```

Current durable evidence is under `../prototypes/FEAT-01-kaya-platform/`: `01-light-empty`, `02-light-pending`, `03-light-saved`, `04-dark-restored`, `05-dark-database-error`, `06-dark-provider-error`, `07-dark-auth-error`, `08-dark-restore-error`, `09-light-320`, `10-light-320-200percent`, `11-dark-320-200percent`, each with **.png screenshot and .dom.html rendered DOM**. `rendered-evidence.json` contains Chrome identity, current URLs, messages/status/errors, focus and computed styles; `contrast-evidence.json` calculates contrast from those composed rendered pairs. No screenshot fallback was needed.

Observed Chrome/154.0.8037.93: real Enter-key send reached pending/user text, simulated saved result retained textarea focus, same-URL reload displayed the same fixture with restored status; provider/database/auth/restore alerts rendered; all eleven captures had one main/h1 and document width equal viewport (1200 or 320px). Both 320px/200% captures used root font 32px and no horizontal document overflow. Transcript contrast 21.00:1 light / 15.13:1 dark; muted-on-surface 9.29:1 / 5.65:1; control border 4.54:1 / 5.65:1; captured dark error 7.63:1. Browser exception collection was empty. These are **design artifact observations**, not product tests, full accessibility/screen-reader certification or SC/UAT completion. Light error rendering, IME/Shift+Enter, full keyboard traversal, screen-reader announcements, live provider and restart restoration remain future product review/QA/operator obligations.

## Reviewer and approval gate

UI reviewer Mode A must read `../../DESIGN.md` and the interactive source/current evidence; new chat interaction cannot scope out. The operator reviews the actual clickable flow and both themes together with the pending plan. No approval has been written; frontend must wait for that bundled approval and implement with actual AI SDK UI/Mastra, not copy simulation state or review-only controls. Required future acceptance remains BRIEF SC-01/02/03/10.

Open questions: no product/design scope uncertainty. Nonblocking control-plane issue DES-CP-01: advertised proc:// mode/kill writes were refused for this governed persona; reported to xd://report_issue. Capture browser was closed with `kill -TERM 45884` (exit 0); prototype service remains session-hosted, with exact restart instructions above. Host should resolve documented prototype-service lifecycle access without changing this product plan.
