# Receipt — harness-ai-dev — FEAT-01 simplify c2 — ALTITUDE angle

Angle file followed (only one read): `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-altitude.md`.
Surface: plan.yaml T-01..T-10, D-01/D-02, lanes, c2 panel; BRIEF.md; DESIGN.md (grep only for the state/recovery contract). Flag-only; nothing edited, nothing run.

## BLUF

Scope is at the right altitude: the complete browser loop (native useChat/DefaultChatTransport -> handleChatStream -> Mastra Memory -> model-free GET restore) is planned as required, excluded work stays excluded, and no capability is bolted onto a caller. Three findings, all plan-text depth, none changing scope or settled constraints: the saved-exchange rule has six restatements with no single authority (A-1), interaction/recovery prose is restated in tasks although DESIGN.md already carries it (A-2), and two tasks carry revision-history narration (A-3). Two residuals checked and left.

## Findings (file, line, summary, concrete cost, alternative, disposition)

### A-1 — Saved-exchange rule has no single authoritative statement
- File/line: plan.yaml:314,316 (T-02), 464 (T-06), 505 (T-07), 542 (T-08), 608 (T-10); BRIEF.md SC-02 (line 17), SC-10 (line 33); DESIGN.md:82 (state table).
- Summary: "saved = same-thread GET holds the current user ID + CURRENT completed native assistant ID following it, with completed ordered parts matching the stream; stale/new-user-only/partial/mismatched stays incomplete" is re-spelled with different wording in about eight places.
- Cost: [INFERENCE] the three implementers (T-06 server tests, T-07 browser check, T-08 CLI compare) and T-02 assertions can each read a slightly different predicate (e.g. "following that user", "matching parts", "ordered"). That already happened once: panel PF-9934… / PF-2595… resolved it per surface, not once. Any later rule change needs edits in about eight places.
- Alternative: DESIGN.md:82 (or one sentence in T-06, the contract owner) is the authority. T-02/T-07/T-08/T-10 and SC-10 say "per the saved-exchange rule in DESIGN.md state table" and keep only their own assertion lists. Browser and CLI performing the check separately is accepted (different lanes and runtimes); no shared file is added.
- Disposition: **fold-in** (pm applies in plan.yaml/BRIEF; keep SC-02 full text, since it is the acceptance statement). DESIGN-touching: **yes, but only to confirm DESIGN.md:82 is the designated authority; no DESIGN edit needed if pm keeps wording equivalent**. Apply owner for the pointer: pm (plan/BRIEF); visual-designer only if the rule text moves.

### A-2 — Recovery-action/focus/theme-matrix prose restated in task intents beyond the design authority
- File/line: plan.yaml:318,320 (T-02), 507,509 (T-07); BRIEF.md SC-10 (line 33), Verification gaps (line 39); DESIGN.md:71 and 73-91 (state and recovery contract) already hold the same behaviors.
- Summary: keyboard recovery (same mounted button, aria-disabled, no native disabled, conditional focus transfer, no autofocus on load, GET-only renewal) and the light/dark x 320px x 200% matrix appear in T-02 and T-07 in near-identical form, plus DESIGN.md.
- Cost: [INFERENCE] two task intents plus DESIGN can drift; T-07 already says "read approved DESIGN.md and correction receipt" so it carries the rule twice for the same implementer. About 3-4 long paragraphs of intent that the dispatched specialist must reconcile.
- Alternative: T-07 intent keeps only "implement the recovery/focus contract in DESIGN.md state-and-recovery section" plus the Astryx-DOM-propagation verification and red-sequencing (the genuinely task-specific parts). T-02 keeps the assertion matrix (what to assert, themes x sizes) since it is the test spec. SC-10 stays as the acceptance statement.
- Disposition: **fold-in** (pm, plan T-07 only) with DESIGN confirmed complete. DESIGN-touching: **yes (read-only confirmation)**; if DESIGN.md:71 lacks the busy-failure-success focus sequence stated in T-07:507, visual-designer adds it, then pm trims T-07. Not a scope change.

### A-3 — Revision-history narration inside executable intents
- File/line: plan.yaml:426-427 (T-05: "1024 replaces old256 ..."); plan.yaml:509 (T-07: "Earlier document-only prototype exemption is superseded"); also BRIEF.md line 49 ("prior document-only prototype ruling is superseded").
- Summary: task text tells the implementer what the previous plan said. Redesign From First Principles test: a reader can tell which requirement arrived last.
- Cost: low; implementers carry a stale value ("256") and a dead exemption in context, and the "adaptive-thinking" rationale for 1024 is a model claim not exercised ("actual model support remains unexercised"). No behavior risk.
- Alternative: T-05 states "maximum output 1024 tokens; model support unexercised, incompatibility stops execution". T-07 deletes the superseded-exemption sentence; BRIEF keeps one line stating interactive prototype review is bundled with this plan.
- Disposition: **fold-in** (pm). DESIGN-touching: no.

## Checked and left (no finding)

- **L-1 Residual: saved confirmation is a GET after stream finish, not a server write guarantee.** Compensating control is named: T-05 waits on installed memory settled semantics and never infers writes from stream completion; UI stays incomplete otherwise; SC-03 live restart evidence stays operator UAT. A deeper fix (server holds the stream until saved, or a custom data part) would introduce the competing message-state protocol settled out. **leave.**
- **L-2 Probe breadth (CLI live/readback/supabase/schema-apply under tests/e2e/platform-live.ts, T-08).** Already adjudicated (F-1, run 4); CLI is supplementary and the bootstrap-vs-#8 clarification is already in plan/BRIEF (line 43). Revision did not reintroduce a new mechanism. **leave.**
- Also left, not re-raised: D-02 text across D-02/T-02/T-03/T-10 (decision vs test vs implementation vs docs are different roles); T-02 mega-QA task and red-first sequencing (settled); lane table (settled); E-1 combined Vitest (unchanged idea).

## Scope verdict

Browser send -> Mastra-streamed reply -> restart -> same-conversation restore is carried by T-05/T-06/T-07 as required behavior, tied to SC-02/03/10 (UAT-gated, not claimed by offline tests). Excluded work (financial renderers, Gmail, uploads, login, multi-conversation, deploy) appears only as exclusions (BRIEF Out of scope; T-03/T-05 "no financial"). No excluded capability leaks into a task's files.

## Principles applied

- Redesign From First Principles (`/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-craft/references/redesign-from-first-principles.md`): its "which requirement arrived last" test produced A-3 (history narration in T-05/T-07) and its propagate-through-every-reference rule produced A-1/A-2 (one authority instead of per-task retellings).
