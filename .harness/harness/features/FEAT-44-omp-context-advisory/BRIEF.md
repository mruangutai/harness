# BRIEF — FEAT-44 OMP-native orchestrator context advisory

## Problem

The orchestrator's context advisory is inert on the canonical host. PR #922 rewrote step 5 of the
orchestrator playbook to depend on "OMP's own context signal"; measured, `ctx.getContextUsage()`
returns `undefined` in exactly the session type the orchestrator runs in, because
`ExtensionRunner.initialize()` drops the callback the subagent supplies (issue #923 §1, filed
upstream as can1357/oh-my-pi#10097). The same hunk deleted the DEC-201 weighting clause and the
DEC-199/DEC-201 citations — measured `grep -c` on `.claude/skills/harness/SKILL.md`, base
`66e9a9d~1` → HEAD `7ebfc9e`: DEC-201 `1 → 0`, DEC-199 `1 → 0`. What it cost is on record: on PR
#922's own validator panel the code-reviewer reached 223,029 context tokens, past DEC-198's 200,000
advisory line, and nothing surfaced it. The predecessor mechanism (`context-watch.py`, a Claude
sidecar reader) cannot be restored — it cannot run under OMP at all, since `.omp/config.yml:1-3`
disables the Claude provider.

## Goal

The orchestrator, under OMP, is handed its own real context size at its wake — the host's own
recorded number, read off disk by the hook that already runs there — so it can weigh a handoff at a
seam as DEC-201 and DEC-198 always intended. One mechanism, in one place, with a test that reddens
loudly if the host's record shape moves. The Claude-only path is retired by an explicit decision
rather than left to rot beside its replacement.

## Requirements

- REQ-01: The orchestrator receives its current context size at its wake, derived from the host's
  own recorded figure, with no extra turn, no extra token, and no change to the dispatch contract.
- REQ-02: The advisory reaches the orchestrator tier only. The main session and the three domain
  leads are never handed an advisory addressed to a tier they are not.
- REQ-03: Every failure to measure yields no figure rather than a wrong figure.
- REQ-04: If the host's record shape moves so no figure can be read, that fact announces itself
  instead of the advisory silently going inert a second time.
- REQ-05: The advisory states how far past the threshold the orchestrator is, as a computed ratio,
  not as prose for the agent to apply by eye.
- REQ-06: The orchestrator playbook's step 5 describes the mechanism that actually exists, and
  carries the DEC-201 weighting clause and the DEC-199/DEC-201 citations again.
- REQ-07: Exactly one context-advisory mechanism exists in the tree. No registration, test
  registry, detect glob, or decision record still asserts the retired one is live, and the unit and
  integration suites are green.
- REQ-08: The decision record states where the 200000 default now lives and what mechanism
  DEC-201's surviving ruling runs on.

## Two design questions, answered

### Fixture provenance — a captured record, plus a live inert-detector rather than a live assertion

**Decided: the frozen fixture is a real captured OMP transcript excerpt, and the drift detector is
not a second test but the reader's own inert path.**

A hand-built minimal fixture encodes the reader author's *belief* about the record shape. If that
belief is wrong, fixture and reader are wrong together and the test is green — which is the failure
the grilling rejected for the old verifier ("sharing that code would compare a function to
itself"). A captured record is host-produced evidence and does not share an author with the reader.
So: capture, truncated to a handful of records and scrubbed of content, committed under the feature's
own fixtures path.

But the grilling is right that either fixture freezes at commit time, and REQ-04 is the whole point
of #923 item 5. A second *live-schema* CI assertion cannot discharge it honestly: it would depend on
a real `~/.omp/agent/sessions/**` file existing on the runner, and its only available fallback is a
soft skip — a gate that looks real and does nothing, the exact shape DEC-163 forbids. Note this is
not the same question the grilling settled: it ruled out a second *implementation* (there is no
arithmetic to second-guess), and a live assertion is not a second implementation. It is ruled out
here on determinism, separately.

The mechanism that does observe live data every wake is the reader itself. So the reader
distinguishes three states, not two: a figure; **no session file** (silence, nothing to say); and
**a session file that scans to exhaustion with no anchor** — which is drift, and emits one line into
the orchestrator's own context naming the field it looked for, once per session. Zero extra tokens on
the healthy path, no flake, and it is unit-testable against a second committed fixture containing
records but no `contextSnapshot`. Drift then announces itself in the place a human is already
reading, which a frozen fixture can never do.

The "once per session" cap on that notice is measured, not stylistic. The largest live transcript on
this machine at planning time is 34.9 MB carrying 2,418 anchors (newest `promptTokens` 38195), so the
full scan the ladder degrades to is the one genuinely expensive read in this design. Capping the
inert path at one notice per session pays it once instead of once per wake, and the healthy path
never reaches it.

### Injection scoping — three conjuncts on the closure persona, composed with the existing block path

**Decided: gate inside the existing `tool_result` handler on `currentAgent === "harness-orchestrator"`
AND `toolName === "task"` AND over threshold.**

The persona is already in scope at the injection point: `currentAgent` is declared at
`.omp/extensions/harness-hooks.ts:410` and assigned from the system prompt at `:452`, and the
handler at `:575` already returns at `:576` when it is unset — which excludes the main session for
free. The three leads carry different `HARNESS_AGENT_ID` values, so an equality test on the
orchestrator's id excludes them without a second mechanism. `toolName === "task"` is what makes this
the orchestrator's *wake* rather than any tool result (#923 §4), and it bounds frequency to order
7–15 reads per feature.

Composition matters more than the gate. The handler today computes `postDomain` and returns early at
`:613` when there is no block reason; when it does return content it sets `isError: true` (`:617`).
The advisory must therefore be computed **before** that early return, appended to the same `content`
array, and must not touch `isError`: a blocked post-write check keeps `isError: true` and gains the
advisory line, an unblocked wake returns content with no `isError` at all. Dropping the advisory when
a write is blocked would lose exactly the wake it was addressed to.

## Success Criteria

- SC-01: Driven against the committed captured fixture, the reader returns the newest
  `message.contextSnapshot.promptTokens` as a number equal to that record's value — and the
  assertion is demonstrated failing before the reader exists.
  verify: automated      evidence: unit
- SC-02: On a fixture whose newest anchor sits beyond the initial 64 KiB window, the reader returns
  the same figure a full scan returns. Pinning the window to a fixed size reddens this case.
  verify: automated      evidence: unit
- SC-03: Given a session file with records but no `contextSnapshot`, the reader yields no figure and
  the orchestrator receives the inert notice naming the field; given no resolvable session file, it
  yields no figure and no notice. Both asserted separately.
  verify: automated      evidence: unit
- SC-04: `registerHarnessHooks` driven over threshold injects for `harness-orchestrator` on a `task`
  result, and injects nothing for `harness-product-lead`, for an absent persona, or for a non-`task`
  tool name. Each of the four asserted on its own.
  verify: automated      evidence: unit
- SC-05: With a block reason present the returned result keeps `isError: true` and carries both the
  post-write check line and the advisory line; with no block reason it carries the advisory line and
  no `isError` key.
  verify: automated      evidence: unit
- SC-06: The injected line states the ratio of measured tokens to the resolved threshold, asserted
  numerically for two different thresholds so a hardcoded string cannot pass; and the threshold is
  read from `budgets.orchestrator_context_warn_tokens` when present, falling back to 200000 when the
  key is absent, asserted with a value that differs from 200000.
  verify: automated      evidence: unit
- SC-07: All seven retired artifacts are absent from `git ls-files` at `review_sha`, no
  `context-watch` reference survives in `.claude/settings.json`, `.harness/harness.json`,
  `run-unit-tests.sh` or the playbook, `run-unit-tests.sh --check-kinds` exits 0, and the unit and
  integration suites are green.
  verify: automated      evidence: integration
- SC-08: Read at `git show <review_sha>:.claude/skills/harness/SKILL.md`, step 5 describes the disk
  read and the injection as the live mechanism, names no retired file, and cites DEC-198, DEC-199 and
  DEC-201. This criterion grades prose accuracy only; the capability it describes is carried by
  SC-01 through SC-06, so no SC rests on wording alone.
  verify: inspection
- SC-09: Read at `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, DEC-198 and DEC-201 each
  carry an amendment and neither is struck; DEC-198's 200000 default is sourced to the new reader,
  DEC-201's amendment names the concrete replacement for the mechanics DEC-204 `:7411-7412` already
  retired for OMP and adds no new supersession language, and DEC-159's present-tense claim that the
  PostToolUse hook is registered is corrected. `gen-decisions-index.py --stdout` diffs clean against
  the committed index.
  verify: inspection

## Verification gaps

- `test_kinds.typecheck` has `cmd: null`: the whole implementation is TypeScript and `bun test`
  strips types rather than checking them, so no gate proves the new code typechecks. What carries it
  is behavioural — SC-01 through SC-06 execute the real module through its real exports. A
  `typecheck` runner is a standing dev-ops gap, not this feature's to close.
- `component`, `ui` and `eval` are null runners; this feature touches none of those surfaces.
- **Claude hosts lose the advisory outright, by decision.** After this change no Claude-hosted
  session gets a context advisory, and nothing verifies one, because nothing remains to verify. That
  is the settled retirement, disclosed here so it is signed rather than discovered.

## Constraints

- **DEC-174 BLOCKS the route.** Every build task is `execution_mode: main-session-direct`: the
  implementation lives entirely inside `.omp/extensions/harness-hooks.ts`, an enforcement-layer file,
  so there is no library for a squad to build. Independently confirmed at source —
  `.harness/team-config.yaml` grants no lane over `.omp/extensions/**`,
  `.harness/harness/docs/DECISIONS.md` or `.claude/settings.json`, so main-session-direct is the only
  legal route, not a preference. DEC-174's cost warning also binds the plan's size: the task count is
  deliberately six.
- **DEC-198 SUPPLIES the threshold** (`budgets.orchestrator_context_warn_tokens`, 200000 by default).
  Its *calibration* — whether an absolute token figure is the right shape across models whose windows
  vary about fivefold — is explicitly out of scope (#923 §7).
- **DEC-201 SUPPLIES the ruling** the advisory serves: the orchestrator weighs its own context and
  hands off at a seam (`DECISIONS.md:6992-6994`). **DEC-204 SUPPLIES the supersession that is already
  signed** (`:7411-7412`): it retired DEC-201's host-specific mechanics for OMP. This feature names
  the concrete replacement inside that existing frame; it does not supersede further.
- **DEC-202 SUPPLIES the limit of the Claude parity promise**: parity is scoped to agent roles,
  skills discovery and `CLAUDE.md` import (`DECISIONS.md:7113-7119`), and says nothing about
  `settings.json` hook contents, so unregistering the hook does not breach it.
- **DEC-163 BLOCKS resting any criterion on a null test kind** — see Verification gaps.
- Out of scope, closed by the grilling: provider accounting quirks, an external watchdog, DEC-198
  threshold calibration, and fixing the wording-assertion test class beyond
  `test-orchestrator-playbook.py` case 4.
- Not to be rebuilt (#923 §5): the handoff note contract, `check-domain.sh`'s `RE_HANDOFF` shape
  gate, `check-state.sh` INV-17 seam enforcement, and the successor protocol all already exist and
  are host-neutral. Only the measurement source changes. And no independent verifier is to be
  written: the new reader performs no arithmetic, so there is nothing to second-guess.

## Approval

status: pending
approved_by: <name>
date: <YYYY-MM-DD>
