# UAT draft — FEAT-01 Kaya minimal browser chat
status: draft
branch: FEAT-01-kaya-platform
review_sha: not assigned — implementation is not present

Not ready: SC-05 through SC-10 have no shipped inspection/QA evidence. This is a planning review artifact, not a request to run nonexistent code. PM may later declare ready only after pinned QA/reviewer green; only the operator records passed/failed. Canonical exit UAT publication is a later lead operation. Budget approximately ten minutes of browser observation, excluding fresh-clone install and hosted setup.

## Setup after implementation prerequisites pass

Use the exact supported Node 24.21.0 and pnpm 11.2.2 sequence in shipped README at review_sha. In that Kaya clone run `pnpm install --frozen-lockfile`, `pnpm exec playwright install chromium`; privately create ignored root `.env.local` from `.env.example`. Supply the five approved settings from the intended Kaya project/account without recording values. Follow README's project-confirmed `pnpm schema:apply` prompt. Run `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`, then `pnpm dev`. Open **http://127.0.0.1:3000** (not an alternate host). Record only safe command exits, thread UUID/URL and observations. Do not paste keys, cookies, DB URLs or full SDK errors.

## Steps — one outcome per result

- U-01 (SC-01): Execute the documented fresh-clone setup above.
  expect: every prescribed setup command exits successfully.
  result:
- U-02 (SC-01): Open the URL and inspect the real browser page.
  expect: the visible Kaya local chat surface has labeled message input, Send control and transcript.
  result:
- U-03 (SC-01): Tab through the controls without a mouse; inspect the accessibility tree.
  expect: the page has English language, one main/descriptive h1 and usable labeled controls with visible retained focus.
  result:
- U-04 (SC-01): Inspect both OS/browser light and dark schemes with contrast tooling.
  expect: text contrast meets 4.5:1 normal or 3:1 large text in each scheme.
  result:
- U-05 (SC-01): In BOTH light and dark schemes inspect the actual product at 320 CSS pixels and 200 percent enlarged text, individually and combined. Include visible provider/configuration, database/readback, expired-access, network and restoration errors with recovery actions before/busy/failure/success; use the shipped failure instructions and QA-reviewed safe failure setup, never change production code or count prototype captures.
  expect: document width does not exceed viewport width and error text/actions remain reachable through vertical scrolling.
  result:
- U-06 (SC-02): Send `Kaya browser persistence check <your unique harmless nonce>`; watch until saved completion. Send a second unique nonce in the same conversation and inspect its current exchange, not the earlier reply.
  expect: Exchange saved appears only for the corresponding current user and CURRENT completed native SDK assistant IDs in current-turn order with matching completed ordered persisted parts; earlier assistant/new-user-only or missing/partial/mismatched/order readback leaves the visible streamed reply and submitted draft incomplete.
  result:
- U-07 (SC-03): Copy the resulting `/?thread=<uuid>` URL; stop pnpm dev. Temporarily remove the Anthropic key from private local settings, restart pnpm dev and reopen exactly that URL.
  expect: the same nonce and assistant exchange visibly restores without a new generation request (browser Network has session/GET only, no POST /api/platform).
  result:
- U-08 (SC-03): Open a different unused valid UUID thread URL.
  expect: the browser reports a missing conversation rather than silently replacing it with a new thread.
  result:
- U-09 (SC-02): With the provider key still absent, attempt a new send in the prior restored conversation; restore the private key afterwards.
  expect: the UI shows a safe configuration error, not a fabricated reply or saved-success state.
  result:
- U-10 (SC-04): Run `pnpm smoke:supabase` after the documented schema setup.
  expect: named server-connectivity/catalog-grant checks pass with a successful public metadata control followed by the specific mastra HTTP406/PGRST106 rejection.
  result:
- U-11 (SC-01): In the error states above, Tab to Check saved messages, Retry restoration or Renew local access and activate with Enter; observe while busy and after failed recovery.
  expect: the same recovery action remains mounted/focusable while busy and reachable/focused on failure, never dropping focus to body.
  result:
- U-12 (SC-01): Activate a recovery that can succeed, first keeping focus on its action and then repeating with focus moved to a different link/region before completion.
  expect: successful recovery moves focus to composer before action removal only in the first case, preserving the chosen other region in the second.
  result:
- U-13 (SC-02/SC-03): Observe browser Network while checking saved messages/retrying restoration and renewing local access.
  expect: recovery makes GET-only thread requests (plus the explicit session bootstrap for renewal), with zero POST generation replay.
  result:


Extra steps are retained because the accepted fresh-clone/visual/live-restart/security obligations cannot honestly be collapsed into a single “works” verdict. CLI `smoke:live` and `smoke:readback <uuid>` may aid diagnosis but never replace U-06/U-07 in the browser. Provider, persistence or access failures are failures to capture verbatim, not reasons to accept a mocked reply. Operator result remains blank until ready and executed; no shipping/merge authorization here.

Evidence gap: DESIGN.md and notes/mockups/design-thin-chat-c2-apply.md now supply corrected prototype current-turn/focus/error evidence in both themes at enlarged narrow widths. They simulate storage/replies and enlarge text, not product SDK/Mastra/Postgres, actual browser zoom, screen-reader delivery, hosted restart or product keyboard UAT. T-02 future rendered browser assertions and implemented-product review must precede this script becoming ready. Planning has exercised none of these product checks; results above remain blank.
