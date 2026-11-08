# FEAT-01 — consolidated thin-chat revision c2

**Unsigned revision complete and PENDING operator review; both perspectives pass planned coverage.** Ten tasks, 55 resolved/disjoint anchors, two decisions, actual DESIGN and interactive prototype. Final required plan check and panel recording exit 0. All four c2 findings were substance-applied by owners; original reader FAILs remain immutable. **Lead VERDICT is conservatively FAIL under DEC-123's computed worst-wins, not a surviving defect or a request for another review cycle.** No pending must-fix; do not relabel reader returns PASS. Seven actual member executions; one actual designer-owner send-back (`cycles_used: 1`); PM normal apply and exit goalcheck consume zero cycles. Fable status skipped (unavailable, no substitute). No product code, installs/builds/tests/formatters/gh-sync/signatures; BRIEF and plan approval still pending.

Paths below are relative to FD `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform` unless absolute.

## Done when — by perspective

**operator** — I can start from a fresh clone, follow one documented setup sequence, send a message in the browser, and see my message and a real Anthropic-backed answer in the conversation. After restarting the local application, I can reopen that same conversation in the same browser interface and see the saved exchange without asking the model again; pending, restoration and failures are visible and honest.

**code maintainer** — I can reproduce the supported runtime, dependencies and checks, identify the protected server boundary and operational data ownership, and extend the small chat surface without a competing message-state protocol. The setup documents distinguish researched compatibility from exercised evidence and do not claim account authorization, financial functionality or production operation.

## Perspective SCs / verification

- Operator: SC-01 fresh clone/browser/AA/reflow — uat; SC-02 real current-turn send/reply/confirmed-save/honest-error — uat; SC-03 same stored conversation after application restart, reopened in same UI without model — uat; SC-04 hosted schema grants/Data API isolation control — uat.
- Code maintainer: SC-05 private secrets/local boundary — inspection; SC-06 workspace/module shape — inspection; SC-07 process/HMR store reuse and model-free recall — inspection; SC-08 six genuine runners/red-first — inspection; SC-09 reproducible docs and evidence limits — inspection; SC-10 Astryx/native SDK state/current-turn/error/recovery/a11y — inspection. These require future pinned shipped inspection plus assertion-level QA receipts. **Every shipped SC is not_met**. `notes/uat-browser-c2.md` is draft, not ready/passed.
- Once-at-exit `notes/research-FEAT-01-kaya-platform-goalcheck-plan.md`: question “does this plan deliver the operator's stated intent?”; operator pass and code maintainer pass against BOTH original intake and trusted answers, planned coverage only. It was not a repeated reader check.

## Task mapping and serialized seams

All original IDs retained (10→10): T-01 tooling→tooling plus Chromium/SDK pins; T-02 API/static red→server/component/browser assertion-red; T-03 bearer settings→private settings/signed local session/native message; T-04 schema unchanged; T-05 generate→shared streaming/model-free storage; T-06 JSON→v6 stream/session/GET; T-07 static→minimal Astryx chat/thread URL; T-08 CLI→real browser failure/denial plus supplementary CLI; T-09 five/ui-null→six runners; T-10 API docs→browser-first docs. Exact task ownership, unchanged verify strings and topology are in `notes/research-FEAT-01-kaya-platform-apply-plan-c2.md`.

T-01 and T-09 main-session-direct SERIALIZED: shared root manifest/lock/runtime/base TS/lint/runner/Playwright, apps/web package/Next/TS, .env.example and product .harness/harness.json. `set-lanes` receipt records 30 rows; final check prints no OVERLAP. Production gates use predecessor/owned assertions; T-07 real minimal framework shell permits behavioral browser red, never startup/import/collection failure. T-09 alone is cumulative.

## Local access / identity / transport

D-01 unchanged (same-project direct/session5432, verified TLS). D-02 amended: HTTP127.0.0.1-only listener, exact Host/Origin/Fetch-Metadata, private HMAC-signed eight-hour HttpOnly SameSite=Strict host-only cookie scoped /api/platform; no Domain, Secure=false ONLY loopback HTTP. CLI metadata-free bearer remains separate. Server KAYA_API_STUB_TOKEN is never public JS/env/body. Token survives app restart, rotation invalidates cookies, explicit renewal never replays generation. Bounded trusted local-machine access, not account auth (#2) or production security. Sources: Next cookies, MDN Set-Cookie and Sec-Fetch-Site cited/read in draft research. No genuine operator tradeoff/open product question remains.

`/?thread=<uuid>` recovers same single conversation after restart. `useChat/DefaultChatTransport → @mastra/ai-sdk handleChatStream(version:'v6') → Mastra → createUIMessageStreamResponse`, SSE wire header v1 distinct from SDK major v6. DB-only ownership-checked Memory recall/perPage:false → convertMessages(...).to('AIV6.UI'); no model construction/key requirement. One HMR-safe bounded verified-TLS pool/store/init owner. Completion requires corresponding CURRENT native user/assistant IDs, current-turn order and completed ordered matching persisted parts; stale/missing/partial/mismatched readback stays incomplete and preserves visible reply/draft. Recovery/restore GET and explicit session renewal never regenerate/replay.

Exact release proposals researched, NOT exercised: Node24.21.0/pnpm11.2.2, Next16.3.8/React19.3.0, Astryx core/neutral0.6.5, ai6.0.116/react adapter3.0.118/Mastra SDK1.10.6, core1.74.0/memory1.35.0/pg1.29.0, Anthropic adapter3.0.103, Playwright1.63.0. Registry engine/peer metadata, exact published declarations, Mastra Next/handleChatStream/message-history and AI SDK protocol docs are linked in `notes/research-FEAT-01-kaya-platform-draft-plan-c2.md`. claude-sonnet-5-5 is an unexercised model candidate; install/typecheck/offline/provider/account compatibility remains later acceptance, not certified here.

## Designer return / bundled prototype gate

- contract: updated (`DESIGN.md`), concrete both-theme palette/type/spacing/Astryx0.6.5/control/state/keyboard/AA/reflow contract.
- needs_prototype: true.
- why: Sending, save uncertainty and keyboard recovery are user-operated interactions requiring user judgement before implementation. Old static-only ruling void; operator may override prototype gate either way.
- prototype: `notes/prototypes/FEAT-01-kaya-platform/index.html`.
- mockups: `13-light-stale-apply.png`, `16-light-320-200-database-apply.png`, `17-dark-320-200-auth-busy-apply.png` in that prototype directory; screenshot+DOM manifest `rendered-evidence-apply.json`, original 01–11 and contrast proof preserved.
- direction_choices: one normal-flow transcript/composer; no sidebar/history/floating obscuring composer/account/token forms; native current-turn confirmation rather than any prior assistant; same mounted focusable recovery button busy/failure, conditional composer success; no focus theft; corrected evidence namespaced `-apply`.

Open **http://127.0.0.1:4179/**. Successfully served using (restart if session host stopped):

```bash
python3 -m http.server 4179 --bind 127.0.0.1 --directory /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform
```

Already-installed Chrome+Node captured PNG/rendered DOM; exact commands and failed/corrected attempts in `notes/mockups/design-thin-chat-c2-apply.md`. BOTH-theme320px/200% error/recovery, stale/partial/mismatch/order rejection and busy/failure/success focus captured. Browser-only simulated fixture/localStorage is explicitly not proposed product state, native SDK, Anthropic, DB or restart acceptance. 200% text enlargement is not actual zoom/screen-reader certification. Prototype approval remains pending **bundled with the unsigned plan signature**; no frontend work permitted before it.

## Reader fan-in / application

`runs/2026-10-05-6-plan-product/panel-c2.md` preserves all original reader identity/kind/severity. Scope FAIL high stale-assistant confirmation; design FAIL med same stale confirmation, high recovery-focus, low advisory both-theme enlarged-error evidence. Designer corrected DESIGN/prototype; PM applied T-02/T-06/T-07/T-08/T-10/BRIEF/UAT/research, recorded panel cycle2 and supported set-panel dispositions. All four generated items resolved, historical PF-86e4a4c3 retained. This is substance-applied, **not a reader PASS on final text**. No proportionality finding or rerun. Close-out roster includes goalcheck; orchestrator may re-record from closing digest as standard plan-team close-out, retaining resolved dispositions. Full receipts/disposition pointers: `notes/research-FEAT-01-kaya-platform-apply-plan-c2.md`.

## Required final plan check (exit 0; full stdout)

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform --code-root /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform
OK T-01 15 anchor(s) resolved
OK T-02 16 anchor(s) resolved
OK T-03 5 anchor(s) resolved
OK T-04 1 anchor(s) resolved
OK T-05 4 anchor(s) resolved
OK T-06 2 anchor(s) resolved
OK T-07 6 anchor(s) resolved
OK T-08 2 anchor(s) resolved
OK T-09 1 anchor(s) resolved
OK T-10 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml against /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform: 10 task(s), 55 anchor(s) resolved, 0 failure(s)
```

Member exercised this final planning gate after all plan mutations; goalcheck read unchanged final text, no redundant run. record-panel --cycle2 also exit0; full stdout in apply note. All task-changing stdout retained in draft/apply sibling receipts. **APPROVAL-RESET: none emitted** (already pending); no mirror invoked. Final specialized contradiction grep assessed matches as historical resolved item, superseded exemption or affirmative interactive/prototype requirements; no active static-only/API-only/UI-null exclusion.

## Limits / routing

No live product criteria met; six runner and installed-interface evidence, pinned shipped inspection, true browser zoom/keyboard/screen-reader/contrast, hosted grants and real send/restart/reopen await implementation/QA/UAT. Eval null/BLOCKED belongs to #7/#9, not waived. Automatic merge diagnostics retain unrelated historical malformed digest, cycle-ledger mismatch, missing github.build_entry and expected unsigned BRIEF; none was suppressed or patched. Designer reported nonblocking proc:// mode/kill permission mismatch to xd://report_issue; exact prototype restart command is supplied, escalate only control-plane ownership, not product scope. Open product questions: none. Main alone mirrors updated pending plan to Kaya issue14 after orchestrator return.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Thin-chat revision complete, unsigned and PENDING; all findings substance-applied,
    with original reader FAILs retained under worst-wins.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/DESIGN.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/uat-browser-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2-apply-stdout.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2-set-lanes-stdout.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2-apply-red-sequencing-stdout.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2-check-stdout.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-draft-plan-c2-check-final-stdout.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-apply-plan-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-apply-proposal-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-panel-disposition-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-apply-stdout-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/research-FEAT-01-kaya-platform-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/mockups/design-thin-chat-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/mockups/design-thin-chat-c2-apply.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/notes/prototypes/FEAT-01-kaya-platform/
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-6-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-6-plan-product/dispatch-contract.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-6-plan-product/panel-c2.md
  expertise_update: []
  team: plan
  steps_run: 7
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Unsigned minimal-browser-chat revision applied; required plan check
      resolves 10 tasks and 55 anchors with zero failures.
    files_touched:
    - BRIEF.md
    - plan.yaml
    - notes/uat-browser-c2.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2-apply-stdout.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2-set-lanes-stdout.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2-apply-red-sequencing-stdout.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2-check-stdout.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2-check-final-stdout.md
  - step: design-contract
    persona: harness-visual-designer
    verdict: PASS
    headline: Thin-chat contract and interactive Astryx prototype complete; bundled
      user approval remains pending.
    files_touched:
    - DESIGN.md
    - notes/mockups/design-thin-chat-c2.md
    - notes/prototypes/FEAT-01-kaya-platform/
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Thin-chat scope and architecture align; current-turn persistence confirmation
      needs one substantive correction.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: 'Skipped: unavailable per orchestrator dispatch; no substitute or performed
      review.'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: Thin-chat direction matches intent; current-turn save confirmation and
      recovery-focus contracts need correction before build.
    files_touched: []
  - step: design-contract-apply
    persona: harness-visual-designer
    verdict: PASS
    headline: Current-turn confirmation and recovery focus corrected; both-theme error
      evidence captured; bundled user approval remains pending.
    files_touched:
    - DESIGN.md
    - notes/prototypes/FEAT-01-kaya-platform/index.html
    - notes/prototypes/FEAT-01-kaya-platform/capture-apply.mjs
    - notes/prototypes/FEAT-01-kaya-platform/rendered-evidence-apply.json
    - notes/prototypes/FEAT-01-kaya-platform/
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Current-turn and keyboard-recovery findings applied; cycle2 panel and
      final plan check exit 0; approval remains pending.
    files_touched:
    - plan.yaml
    - BRIEF.md
    - notes/uat-browser-c2.md
    - notes/research-FEAT-01-kaya-platform-draft-plan-c2.md
    - notes/research-FEAT-01-kaya-platform-apply-proposal-c2.md
    - notes/research-FEAT-01-kaya-platform-panel-disposition-c2.md
    - notes/research-FEAT-01-kaya-platform-apply-stdout-c2.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass planned coverage against original intake and
      browser amendment; all ten shipped SCs remain not_met.
    files_touched: []
  must_fix: []
  branch: none
  escalations:
  - id: DES-CP-01
    raised_by: harness-visual-designer
    question: Can governed prototype hosts use documented proc:// mode/kill lifecycle
      operations? Designer reports permission refusals.
    domain: Harness tool lifecycle permissions
    routed_to: harness-orchestrator
    resolution: Nonblocking control-plane report sent to xd://report_issue; served
      URL and exact restart instructions delivered. No product scope change requested.
    decided_by: harness-product-lead
    recorded_as: notes/mockups/design-thin-chat-c2.md and runs/2026-10-05-6-plan-product/digest.md
  adequacy_notes:
  - Revision deliverable complete and unsigned/PENDING. FAIL is DEC-123 computed worst-wins
    from original reader FAILs; all four findings resolved via owner substance application,
    not independent re-review. No surviving must_fix or additional reader cycle requested.
  - Both perspectives pass planned coverage against original intake AND trusted operator
    answers; all shipped SCs not_met. Full verbatim Done when, grouped SC methods,
    task mapping and final check stdout are in the lead artifact.
  - 'Seven actual member executions including one designer-owner send-back: cycles_used=1.
    PM normal apply and once-at-exit goalcheck each consume zero cycles.'
  - Ten tasks retained T-01 through T-10; 55 disjoint anchors; final required plan
    check exit0/no OVERLAP. T-01/T-09 serialize root/shared/app configuration and
    product harness runner cutover as main-session-direct.
  - 'D-02: localhost-only privately signed HttpOnly SameSite=Strict cookie, exact
    Host/Origin/fetch metadata, separate CLI bearer; token never browser-public. UUID
    URL recovers same conversation through DB-only GET with no model. Renewal never
    replays generation.'
  - 'Transport research: native useChat/DefaultChatTransport, explicit @mastra/ai-sdk
    v6 handleChatStream/createUIMessageStreamResponse; SDK majorv6 distinct from SSE
    wire headerv1. Registry/declaration/vendor research is not exercised compatibility;
    install/typecheck/tests/live UAT remain future.'
  - Designer contract updated; needs_prototype=true because send/save/recovery are
    user-operated interactions. Prototype notes/prototypes/FEAT-01-kaya-platform/index.html
    served http://127.0.0.1:4179/. Exact commands, screenshots/DOM/focus proof and
    direction_choices in notes/mockups/design-thin-chat-c2-apply.md. Approval bundled
    with pending plan, operator-overridable.
  - Mockups:13-light-stale-apply.png,16-light-320-200-database-apply.png,17-dark-320-200-auth-busy-apply.png.
    Prototype directory groups generated proof files; original baseline proof preserved.
    Browser fixtures/localStorage are explicitly simulated, not native SDK/Anthropic/Postgres/restart
    proof.
  - Panel cycle2 recorded/all4 c2 items resolved; historical PF-86e4a4c3 retained.
    Closing readers add goalcheck for standard orchestrator re-recording from this
    digest; retain resolved dispositions.
  - APPROVAL-RESET:none emitted. All task-changing stdout preserved. No gh-sync/mirror/approval
    edit/signature/product code/install/build/test/formatter; main alone updates Kaya
    issue14 after orchestrator returns.
  - Automatic merge diagnostics preserve expected unsigned status and preexisting
    cycle-ledger/malformed historical digest/missing github.build_entry issues; not
    waived or fixed.
  - Fable was unavailable and DID NOT RUN. Reader roster and checkpoint record status
    skipped; this member entry must be represented by the skipped union, not a performed
    PASS.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: uat
    evidence: Draft fresh-clone/browser/accessibility UAT; product execution absent.
  - id: SC-02
    verdict: not_met
    method: uat
    evidence: Real browser send/reply/current-turn save and honest failures await
      operator execution.
  - id: SC-03
    verdict: not_met
    method: uat
    evidence: Same-URL application restart/reopen in same UI with no model request
      awaits live UAT.
  - id: SC-04
    verdict: not_met
    method: uat
    evidence: Hosted grants/Data API control and rejection unexercised.
  - id: SC-05
    verdict: not_met
    method: inspection
    evidence: Security boundary specified; shipped inspection/QA receipts absent.
  - id: SC-06
    verdict: not_met
    method: inspection
    evidence: Workspace/module shape specified; no shipped review_sha inspection.
  - id: SC-07
    verdict: not_met
    method: inspection
    evidence: Storage lifetime/identity/no-model recall specified; shipped QA evidence
      absent.
  - id: SC-08
    verdict: not_met
    method: inspection
    evidence: Runner/red-first/terminal gate future work; plan check is not product
      verification.
  - id: SC-09
    verdict: not_met
    method: inspection
    evidence: Browser-first docs specified; shipped documentation inspection absent.
  - id: SC-10
    verdict: not_met
    method: inspection
    evidence: SDK/current-turn/recovery acceptance specified; simulation is not shipped
      UI/QA.
  needs_approval: true
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Installed release/model-account/runtime compatibility unexercised.
  - Six real runner cutovers, red/green and shipped inspection await implementation.
  - Hosted grants and browser send/reply/restart/reopen await live operator UAT; draft
    not ready/passed.
  - Product contrast/keyboard/screen-reader/error reflow and actual zoom future acceptance;
    prototype 200% text enlargement only.
  - 'Eval remains disclosed null/BLOCKED #7/#9 quality gap, not waived.'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-06/T-07 saved confirmation can accept an older assistant reply.
    why: With persisted U1/A1/U2 but missing current A2, checking latest user ID plus
      any nonempty assistant accepts U2 and stale A1, falsely announces saved completion
      and can discard streamed A2. BRIEF SC-02 requires confirmation of that exchange.
      T-02 must test stale second-turn readback; T-06/T-07 must bind confirmation
      to the native SDK current assistant identity and completed ordered persisted
      parts; align T-08 confirmation and T-10/research wording. Reasoned plan counterexample,
      not an exercised product defect.
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: Saved confirmation can accept a prior assistant instead of the current
      turn.
    why: DESIGN Readback confirmed and plan T-06/T-07 require latest user ID plus
      nonempty assistant, without current-turn association; BRIEF SC-02 requires the
      exchange confirmed. A persisted new user with only a previous assistant satisfies
      the literal predicate [INFERENCE].
  - kind: substance
    scope: none
    severity: high
    reader: ui-reviewer
    summary: Recovery-action focus transitions are unspecified; prototype unmounts
      the triggering button.
    why: DESIGN specifies composer/send focus only. Prototype checkSaved/restore/renew
      clear error and remove the error-dependent recovery action without a focus destination.
      Keyboard continuity must be explicitly preserved; source-derived, not independently
      browser-exercised.
  - kind: substance
    scope: none
    severity: low
    reader: ui-reviewer
    summary: Captured error evidence lacks light-theme and 320px/200% error recovery
      states.
    why: "Rendered entries 05\u201308 are dark desktop errors; 09\u201311 are restored\
      \ without errors. Contract requires all states usable; make future T-02 browser\
      \ coverage explicit. Advisory evidence gap, not observed contrast/reflow failure."
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'status skipped: fable-advisor unavailable per orchestrator dispatch;
      no substitute reader.'
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-6-plan-product/digest.md
```
