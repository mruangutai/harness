# Review — FEAT-44 plan (BRIEF.md + plan.yaml) — code-reviewer, primary seat

review_sha: b0ea27d8eb9740f2d8e6f2fceeb82fa16bdead56 (plan artifacts only; base for source anchors 7ebfc9e)
Scope: plan review. No implementation exists. Nothing under `.omp/extensions/harness-hooks.ts` etc. is
reviewed for quality — those anchors are cited only to check the plan's *claims about them*.

## Stage 1 verdict: spec compliance — PASS on coverage, with two defects that must be fixed before build

Every #923 item and every grilling `## Settled` item traces to a REQ, a task and an SC (table below).
**Nothing falls through.** The plan, if executed literally, *would* deliver the primary fix — the
orchestrator stops seeing `undefined` and gets a real number, reached exactly where step 5 reads it,
gated correctly to the orchestrator tier only. But two concrete defects, both traced to specific plan
text, must be corrected first: **(1)** a false factual claim the plan instructs be written into
`DECISIONS.md`, and **(2)** a gap in REQ-04's loud-on-drift coverage that reproduces #923's own root-cause
class through an untested seam. Both detailed under Stage 2 below (they are quality-of-the-decision
findings, not compliance omissions, but both gate the FAIL).

### #923 §6 traceability (§6 enumerates FIVE items, not six — minor correction to the dispatch)

| #923 §6 item | REQ | Task(s) | SC | Gap? |
|---|---|---|---|---|
| 1. Transcript reader, adaptive scan, no regex, no persisted state | REQ-01, REQ-03 | T-02 | SC-01, SC-02, SC-03 | none |
| 2. Wire into `tool_result`, inject only over threshold, computed ratio | REQ-01, REQ-02, REQ-05 | T-03 | SC-04, SC-05, SC-06 | none |
| 3. Restore SKILL.md step 5 + DEC-201 weighting clause + DEC-199/201 citations | REQ-06 | T-05 | SC-08 | none |
| 4. Retire Claude-only path (§923 text names 6 artifacts; grilling caught the 7th, `verify-context-watch-live.py`, and the plan carries the correction) | REQ-07 | T-04 | SC-07 | none — deviation from #923's literal list is a documented, correct fix, not an omission |
| 5. Test against behaviour not wording (the `case4` wording assertion + a loud drift signal) | REQ-04 | T-01, T-02, T-05 | SC-03, SC-08 | **narrow gap — see Stage 2 finding F2** |

Grilling `## Settled` list — all nine items map to a plan element (retire path→T-04; full-FEAT-44+board→
`source_issues:[923]` in plan.yaml header; amend-not-strike DEC-198/201→D-05/D-06→T-06; closure
mechanism→`source_issues`; DEC-174 forces main-session-direct→D-07, all six tasks are
`main-session-direct`; task count kept to six as promised→T-01..T-06 confirmed = 6; one TypeScript
impl→D-01, no Python CLI added anywhere in the task files; no independent verifier→confirmed, T-04
deletes `verify-context-watch-live.py` and nothing replaces it; test lives in existing bun suite→T-01
extends `omp-hooks.test.ts`). Nothing unaccounted for.

### Reachability — verified at source, not inferred

- `HARNESS_AGENT_ID: harness-orchestrator` is the literal in `.claude/agents/harness-orchestrator.md:21`
  — exact match to the gate's `currentAgent === "harness-orchestrator"` string.
- `currentAgent` is declared at `harness-hooks.ts:410` and assigned from `detectHarnessAgent(event.systemPrompt)`
  at `:452` inside `before_agent_start` — VERIFIED, matches D-04's citation.
- `tool_result` handler at `:575`, early return at `:576` (`if (!currentAgent) return;`), task-claim
  bookkeeping `:579-611`, post-domain check `:612`, early return `:613`, block-return `:615-618` —
  every line VERIFIED byte-for-byte against the plan's citations (table below). This is the strongest
  part of the plan: the composition T-03 specifies (advisory computed *before* `:613`, appended to
  `content` without an `isError` key on the no-block path, appended alongside the check line when
  blocked) is coherent with the code as it exists today, and correctly satisfies REQ-02 (leads and main
  excluded by the same equality test / existing early return, no second mechanism needed) — consistent
  with Expertise P-09 (enumerated every other route: leads carry different `HARNESS_AGENT_ID`, main
  carries none, both dead-end at `:576` or the equality test, no third route exists).
- `.omp/config.yml:1-3` confirms the Claude provider is disabled, closing off the "restore the old
  hook" alternative the BRIEF cites.

## Anchor table — every cited anchor, VERIFIED at source (worktree == 7ebfc9e for all non-plan files; confirmed via `git diff --stat 7ebfc9e b0ea27d` touching only the 5 planning files)

**Zero stale anchors found.** This is worth stating plainly since the plan itself flags "two of the
three line numbers handed to pm were already stale" during planning — those were caught and fixed
before this pin; my independent re-verification of the full cited set (34 anchors) found none still
stale.

| File:lines | Claim | Status |
|---|---|---|
| `harness-hooks.ts:409` | `registerHarnessHooks` function start | VERIFIED |
| `harness-hooks.ts:410-417` | closure state vars (`currentAgent` etc.) | VERIFIED |
| `harness-hooks.ts:452` | `currentAgent` assigned from system prompt | VERIFIED |
| `harness-hooks.ts:575` | `tool_result` handler registered | VERIFIED |
| `harness-hooks.ts:576` | early return when `currentAgent` unset | VERIFIED |
| `harness-hooks.ts:579-611` | task claim bookkeeping block | VERIFIED |
| `harness-hooks.ts:612` | `postDomain` check computed | VERIFIED |
| `harness-hooks.ts:613` | early return, no block reason | VERIFIED |
| `harness-hooks.ts:615-618` | block-reason return shape, `isError: true` | VERIFIED |
| `harness-hooks.ts:324-328` | `sessionId(ctx)` try/catch pattern to mirror (fn is named `sessionId`, not "getSessionId" — cosmetic naming looseness in the intent prose, not a line-number error) | VERIFIED (substance) |
| `harness-hooks.ts:1-3` | current imports (`node:child_process`, `node:path`, `node:url`) | VERIFIED |
| `omp-hooks.test.ts:12` | import block closes, sources `harness-hooks.ts` | VERIFIED |
| `omp-hooks.test.ts:3` | `tmpdir` import | VERIFIED |
| `.claude/settings.json:54-68` | `PostToolUse` block, two hook objects | VERIFIED |
| `.claude/settings.json:58-61` | `check-domain.sh --post` entry (kept) | VERIFIED |
| `.claude/settings.json:62-65` | `context-watch-hook.py` entry (removed) | VERIFIED |
| `.claude/settings.json:64` | the command line itself | VERIFIED |
| `run-unit-tests.sh:30` | `UNIT_SCRIPTS` contains `test-context-watch.py` | VERIFIED |
| `run-unit-tests.sh:31` | `INTEGRATION_SCRIPTS` contains the two cli/hook test names | VERIFIED |
| `.harness/harness.json:119` | `integration.detect` contains both context-watch test paths | VERIFIED |
| `test-orchestrator-playbook.py:62-67` | `case4` function body | VERIFIED |
| `test-orchestrator-playbook.py:63-65` | presence assertion (wording regex) | VERIFIED |
| `test-orchestrator-playbook.py:66-67` | absence assertion (`context-watch.py` literal) | VERIFIED — and matches the grilling's CORRECTED reading, not the original inverted one |
| `SKILL.md:50-56` | current (broken) step 5 text | VERIFIED |
| `SKILL.md:52` | DEC-198 citation survives untouched | VERIFIED |
| `DECISIONS.md:6786` | DEC-198 heading | VERIFIED |
| `DECISIONS.md:6790-6792` | stated source = `context-watch.py`'s `DEFAULT_CONTEXT_WARN_TOKENS` | VERIFIED |
| `DECISIONS.md:6985` | DEC-201 heading | VERIFIED |
| `DECISIONS.md:6992-6994` | DEC-201 ruling clause (survives verbatim) | VERIFIED |
| `DECISIONS.md:7041-7048` | DEC-201 self-identification / nonce-probe paragraph (superseded) | VERIFIED |
| `DECISIONS.md:7411-7412` | DEC-204 already supersedes DEC-201's host mechanics for OMP | VERIFIED — the plan's edit-size claim is sound |
| `DECISIONS.md:4091-4102` | DEC-159 in-flight-warning paragraph, present-tense hook-registration claim | VERIFIED |
| `DECISIONS.md:3954` | DEC-158 amendment-1 header style to match | VERIFIED |
| `DECISIONS.md:3971-3974` | DEC-158 Applied list citing `context-check.md` (left untouched, correctly — historical record) | VERIFIED |
| `verify-context-watch-live.py:75-79` | sibling-path derivation | VERIFIED |
| `verify-context-watch-live.py:220-224` | `subprocess.run` invocation | VERIFIED |
| `verify-context-watch-live.py:233-238` | unreachable missing-sibling diagnostic | VERIFIED |
| `.omp/config.yml:1-3` | Claude provider disabled | VERIFIED |

## Stage 2 — plan quality

### F1 [MUST_FIX, high] — D-05's justification and T-06's DEC-198 amendment instruct a false claim into DECISIONS.md

`plan.yaml` D-05 `because:` reads: *"the stated source is being deleted while
`budgets.orchestrator_context_warn_tokens` is absent from `.harness/harness.json`, so the default path
is the live path."* T-06's intent repeats it more strongly: *"budgets in `.harness/harness.json` holds
`max_total_cycles` and `max_total_runs` only, so the key is absent today and the default IS the live
value."*

**This is false, checked at source.** `.harness/harness.json:169` reads
`"orchestrator_context_warn_tokens": 200000` — present since `ac6c113` (2026-08-25), predating this
feature by days. It directly contradicts the **un-amended** text of the very entry T-06 is amending:
`DECISIONS.md:6788-6790` already states *"The leaf sits in `.harness/harness.json` (this repo's live
config)"* and cites this repo's own measured distribution behind the figure. If T-06 executes as
written, DEC-198 will contain an amendment that flatly contradicts its own parent paragraph a few lines
above — a self-contradicting, falsified statement landing in the permanent decision record (rule 15).

**Concrete cost beyond record hygiene:** the false framing tells a future reader that *"the default IS
the live value"* — i.e., that editing `DEFAULT_CONTEXT_WARN_TOKENS` in `harness-hooks.ts` is how you
change this repo's threshold. It is not: the explicit `harness.json` key wins, and a code edit to the
constant would be silently ineffective here. BRIEF's own "Verification gaps" section flags DEC-198
threshold calibration as anticipated future work — exactly the task a future implementer, trusting this
false decision-record text, would misdirect.

**Alternative:** T-06's DEC-198 amendment should state the key IS present in this repo (200000,
currently equal to the constant by coincidence, not because the key is unset) and in the template, and
that `DEFAULT_CONTEXT_WARN_TOKENS`/`resolveContextWarnTokens` governs only a config that genuinely lacks
the key (a fresh `/harness-init` before propagation, or an operator who has removed it). SC-09's
"sourced to the new reader" requirement is satisfiable either way — nothing forces the false framing.

### F2 [MUST_FIX, high] — REQ-04's loud-on-drift design covers JSONL schema drift, not session-resolution API drift — the same failure class #923 exists to close

T-02's `readContextAnchor` yields `{kind:"none"}` on three collapsed paths: falsy `sessionFile`
argument, `stat` throwing, or `open` throwing. T-03 wires `ctx.sessionManager?.getSessionFile?.()`
inside try/catch, folding a throw into `undefined` — indistinguishable from "no session file," which
T-03 correctly treats as legitimate silence. But **within the already-gated context** (`currentAgent
=== "harness-orchestrator" && toolName === "task"`), a session file always exists — this is a call
scoped to an orchestrator mid-run, never the case where "no session yet" is legitimate. In that
specific scope, `getSessionFile()` throwing or returning non-string can only mean one thing: the OMP
API surface moved.

That is **exactly** #923's own root cause — `ctx.getContextUsage()` silently returning `undefined` due
to an internal OMP wiring change, undetected until deliberate probing (#923 §1: "ruled out: our omp
predates the wiring — No"). REQ-04 exists precisely so this class of regression "announces itself
instead of the advisory silently going inert a second time." The plan's "inert" notice covers drift in
the `contextSnapshot` JSONL *field shape*; it does not cover drift in the `getSessionFile` *resolution
API* — the identical shape of failure that produced #923, reachable through the one new seam this
feature depends on and does not itself measure. T-01's test list has no case for a
`getSessionFile`-throws scenario (`describe("context advisory injection")`'s five cases plus the
anchorless-once case cover toolName/persona/threshold/block combinations, never a resolution failure),
so this gap is also untested, not merely undocumented.

**Alternative:** inside the gated block, treat a `getSessionFile()` throw or non-string return as a
loud, once-per-session notice (same shape and cap as the existing `contextInertText` path) rather than
silently folding it into `readContextAnchor(undefined)`'s "none," and add one T-01 test asserting it.

### Nits

- T-02's intent calls `harness-hooks.ts:324-328`'s helper "the `getSessionId` helper"; the function is
  actually named `sessionId`. The pattern it points at (try/catch around
  `ctx.sessionManager?.getSessionId?.()`, undefined on throw) is correctly described — cosmetic only.
- The dispatch states "#923 enumerates six work items"; §6 "Proposed work" enumerates five
  (numbered 1-5). Traceability table above uses the actual five.
- T-02's own verify (`-t readContextAnchor`) filters to one `describe` block, leaving
  `resolveContextWarnTokens`/`contextAdvisoryText`/`contextInertText` unverified until T-03's full-suite
  run. Not a defect — T-03's verify covers the aggregate — just looser than it needed to be as an
  incremental gate.

### Considered and NOT flagged (recorded per Expertise O-15, so it isn't re-raised)

- **DEC-159 amend-vs-strike under DEC-188.** T-06's own intent text calls the tree's contradiction of
  DEC-159's in-flight-warning paragraph "flatly false" — language that echoes DEC-188's strike trigger.
  Read DEC-188 at source (`DECISIONS.md:5919-5949`): the strike test is whether the tree contradicts
  the *ruling*, not whether one descriptive sentence inside the entry has gone stale. DEC-159's ruling —
  that an in-flight warning capability exists — survives; only its *implementation-vehicle* sentence
  (PostToolUse hook, `.claude/settings.json`) is now wrong. That is DEC-188's own "partly overtaken →
  amend" branch, matching how DEC-198 and DEC-201 are handled. Correct call, not a violation.
- **Sweep for other present-tense DECISIONS.md claims about context-watch/PostToolUse/nonce/context-check** —
  full-file grep found only DEC-198 (`:6790`), DEC-201 (`:7043,:7045`), DEC-159 (`:4092`) — the three
  T-06 already amends — plus DEC-158's historical Applied list (`:3972`, past-tense, correctly left
  alone) and several unrelated `PostToolUse` mentions (`check-domain.sh`'s own hook, `:5288, :5302,
  :5307, :5379, :6726`, all describing a *different* registered hook that survives this change). Three
  amendments are sufficient.
- **Seven-artifact delete list** — repo-wide sweep (basenames + `context-watch`, `context-check`,
  `CONTEXT_WARN`, `DEFAULT_CONTEXT_WARN_TOKENS`, `context_check`, `orchestrator_context_warn_tokens`)
  found no consumer outside: the seven files' own cross-references (deleted together), `DECISIONS.md`
  (covered by T-06), and FEAT-31's own historical `notes/` (a closed feature's record, correctly left
  alone — same DEC-158 precedent). The list is exactly right in both directions: nothing missing,
  nothing over-included.
- **Three mechanical guards** — read at source: `run-unit-tests.sh`'s drift check (`:95-140`) really
  cannot see a `test_kinds.integration.detect` entry with no matching array member (confirmed by reading
  its two one-directional loops), which is exactly why T-04's verify carries the separate `git grep`;
  `test-run-unit-tests-kinds.py` (confirmed by reading `case_2`/`case_3`) tests only the two directions
  the code implements, matching T-04's claim precisely; `test-orchestrator-playbook.py`'s `case4` reads
  as the grilling's CORRECTED version, not the original inverted one. None of the three guard
  descriptions is backwards.
- **Test-first ordering, empirically checked, not just read.** Ran a probe (`bun test` against a file
  importing a not-yet-exported name from the real `harness-hooks.ts`): Bun's static ESM check throws a
  `SyntaxError` that (a) contains the missing export's name — satisfying T-01 verify's `grep -q
  readContextAnchor` — and (b) reports `"1 fail"` — satisfying `grep -qE "[1-9][0-9]* fail"`. T-01's RED
  gate is real, not vacuous. T-03's `[3-9][0-9] pass` range is also real: current suite is 24 (ran it),
  T-01 adds 14 (4+2+2+6, counted from the intent's own enumeration), landing at 38 — inside the
  asserted range with room either side.

## Direct answers

1. **Would this fix #923, or leave it inert somewhere?** Fixes the reported bug — the orchestrator
   stops reading `undefined` and gets the host's own recorded figure, reached at the correct wake, gated
   to the correct tier, with the composition around the existing `isError` early-return sound. It does
   **not** yet close REQ-04 completely: F2 is a narrow, untested seam that reproduces #923's own failure
   class through a different API surface. Not inert today, but not fully guarded against recurring the
   way #923 itself arose.
2. **Is the seven-artifact delete list wrong in either direction?** No — verified correct both ways.
3. **Do the three guards break as described, and is any backwards?** All three break exactly as
   described; none is backwards. The previously-inverted `case4` reading was already corrected before
   this pin and the correction is what the plan carries.
4. **Are the T-06 amendments sufficient under DEC-188?** The *set* of three entries is sufficient — no
   fourth entry needs correcting. But amendment F1 (DEC-198) as currently specified writes a false claim
   into the very entry it corrects, which must be fixed before this lands.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Plan traces cleanly to #923 and the grilling with zero stale anchors, but must_fix on two concrete defects — a false absent-key claim T-06 would write into DEC-198, and a REQ-04 drift-detection blind spot on session-file resolution that reproduces #923's own root-cause class."
  severity_max: high
  findings: 2
  must_fix:
    - "D-05/T-06: budgets.orchestrator_context_warn_tokens is present (200000) in .harness/harness.json today, not absent — fix the amendment text before it lands in DECISIONS.md self-contradicting DEC-198's own un-amended paragraph"
    - "T-02/T-03: getSessionFile() resolution failure inside the gated orchestrator+task context is folded into silent 'none' with no notice and no test — REQ-04 requires this class of drift to announce itself, matching #923's own root cause"
  spec_violations: []
  reviewed: "base 7ebfc9e (source anchors) :: b0ea27d8eb9740f2d8e6f2fceeb82fa16bdead56 (plan artifacts, pinned)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should T-01 gain an explicit getSessionFile-throws test case and should T-03's intent specify the loud notice for it (F2), before this plan is approved?", blocking: true }
    - { id: Q2, question: "Should T-06's DEC-198 amendment be rewritten now (F1) so pm doesn't hand a false claim to whoever executes T-06 main-session-direct?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-code-reviewer-c0.md
```
