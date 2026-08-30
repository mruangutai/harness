# Review — FEAT-44 build — code-reviewer, cycle 1

reviewed: 7ebfc9eb9cb77939b325f559d64e6b0cbb22d907..21e97ed88c8d56226b391fc37fb0049e8ead5fff (32 files, +2706/-3243)
No `[harness:human]` commits in range (`git log` shows 6 `T-0N:` commits + 6 plan/board commits, all agent-authored).

## Stage 1 verdict: spec compliance — PASS

### REQ traceability (all 8, all discharged, each verified at source)

| REQ | Discharged by | Verified how |
|---|---|---|
| REQ-01 (no extra turn/token, wake-derived figure) | T-02 `readContextAnchor` (stateless), T-03 injection into existing `tool_result` | Ran the real suite: SC-01/02/10 tests pass; read `readContextAnchor`/handler source directly |
| REQ-02 (orchestrator tier only) | `currentAgent === "harness-orchestrator"` gate at `harness-hooks.ts:791` | Confirmed marker string exact match at `.claude/agents/harness-orchestrator.md:21`; ran SC-04 tests (lead/main/wrong-tool all return `undefined`) |
| REQ-03 (no figure beats wrong figure) | Every branch in `readContextAnchor`/`resolveSessionFile` returns `none`/`inert`/`failed`, never a guessed number | Read every branch at source; traced the widening ladder's conservative first-fragment discard (see Stage 2) |
| REQ-04 (drift announces itself, told apart from no-session) | `SessionFileResolution` 3-way kind (`path`/`absent`/`failed`) + `ContextAnchor` 3-way kind (`tokens`/`inert`/`none`) | Read both functions; ran the accessor-failure and inert-notice tests live |
| REQ-05 (computed ratio) | `contextAdvisoryText`'s `(tokens/threshold).toFixed(2)` | Ran `contextAdvisoryText` tests (1.12x / 1.49x, two thresholds) |
| REQ-06 (playbook step 5 rewritten, DEC-198/199/201 cited) | `SKILL.md:50-58` | Read the rewritten step 5 at source — all three cites present, no numeral, no retired file named |
| REQ-07 (one mechanism, suites green) | T-04 deletion + registry moves | Ran `--check-kinds` (0), full bun suite (42/42), `test-run-unit-tests-kinds.py` (23/23), repo-wide grep for all 7 retired names |
| REQ-08 (decision record states new default's home + DEC-201's replacement) | T-06 DEC-198/DEC-201 amendments | Read both amendments in full at pinned SHA |

No scope creep found: every touched surface maps to a REQ/D. No omission found against BRIEF or #923 §6's five work items.

### Q1 — Does it actually fire in production? **Yes, verified at source, not inferred.**

- `.claude/agents/harness-orchestrator.md:21` reads `HARNESS_AGENT_ID: harness-orchestrator` — byte-exact
  match to the gate's `currentAgent === "harness-orchestrator"` string comparison at `harness-hooks.ts:791`.
- `currentAgent` is set in `before_agent_start` (`:625-629`) via `detectHarnessAgent(event.systemPrompt)`
  (`:423`), whose regex `/^HARNESS_AGENT_ID: (harness-[a-z0-9-]+)$/gm` matches that exact literal.
- The `tool_result` handler at `:751` fires on every tool result including `task` (the existing,
  pre-FEAT-44 `pendingTaskCalls`/claim-release logic in the same handler already depends on `toolName
  === "task"` firing correctly for lead→orchestrator wakes — this is live, tested machinery, not new).
- No other route reaches the gate: leads carry different `HARNESS_AGENT_ID` values (verified against
  all 15 `.claude/agents/*.md` files — each has its own distinct marker), and the main session carries
  none, so both dead-end at the pre-existing `if (!currentAgent) return;` (`:752`) before the FEAT-44
  block is ever reached.

The gate is not one character off. It fires.

### Q2 — SC-05 substitution: unreachability claim verified, substitute equivalent in force for reachable states

`postDomain` (`harness-hooks.ts:244-272`) returns `[]` for every `toolName` other than `write`/`edit`/`bash`
— read at source, confirmed the tail `return [];` is unconditional for any other name including `task`.
So a block reason and the `task` wake are provably mutually exclusive; the plan's original SC-05
("both a block reason and the advisory on one result") describes a state the code cannot produce.

The substitute (`omp-hooks.test.ts:612-625`, "a blocked non-wake result keeps isError and gains no
advisory") plus the existing positive case (`:575-583`, "isError absent" on the unblocked wake) together
pin the invariant BRIEF states — "the advisory must neither clobber nor invent isError" — over every
state the code can reach: unblocked+advisory → no `isError` key; blocked+no-advisory (bash) → `isError:
true`, no advisory line. What they cannot test, because the code cannot reach it, is
blocked+advisory-simultaneously; that state's non-existence is itself established by the `postDomain`
source read above, not merely asserted. SC-05 as amended is both satisfiable and satisfied.

### Q3 — SC-11 replacement: REQ-04's loud-on-drift guarantee is discharged, and by the gate that actually runs

Reproduced the three-copy disagreement independently: running `omp` on PATH reports `18.0.5`
(`omp --version`), the bun install cache holds five versions including `18.0.10`
(`~/.bun/install/cache/@oh-my-pi/pi-coding-agent@18.0.10@@@1`), and the bun *global* node_modules copy
— the one `Bun.resolveSync` would actually walk to — is `17.3.8`
(`~/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/package.json`). All three figures match
the docstring in `test-omp-session-accessor.py` exactly.

`test-omp-session-accessor.py` **is wired into the gate that runs**: it's the last entry in
`run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` array, and its literal path is present in
`.harness/harness.json`'s `test_kinds.integration.detect` pipe list (checked with `python3 -c` against
the parsed JSON, not a truncated grep). `run-unit-tests.sh --check-kinds` passes (ran it: "the script
arrays and test_kinds.integration.detect agree"). So this is not a self-test that never executes —
it is a required step, `--auto-approve`d against the real `omp` binary, and it fails (never skips) if
`shutil.which("omp")` is absent, if the probe produces nothing, or if `getSessionFile` stops resolving.

If a future OMP renames/drops `getSessionFile`: `resolveSessionFile`'s unit-level branches (throw /
not-a-function / missing manager) all collapse to `SessionFileResolution.failed`, and separately
`test-omp-session-accessor.py`'s case 4 (`getSessionFile resolves inside that subagent session`) goes
red the next time `run-unit-tests.sh --kind integration` runs — which is the required CI step, not a
manual invocation. REQ-04's guarantee is watched by the gate that runs, not merely by something a human
must remember to invoke.

### Q4 — Retirement sweep: clean, and the 7th artifact (`verify-context-watch-live.py`) is confirmed gone

`git ls-files` for all context-watch/context-check globs at review_sha: empty (0 files). Repo-wide grep
(`git grep -In`, all 6 retired-name variants) found matches only in: (a) `DECISIONS.md`'s own historical
prose describing what the *retired* entries used to say (correctly left as-is — DEC-158 precedent,
verified this reasoning explicitly in DEC-158's own untouched Applied list), (b) `test-orchestrator-
playbook.py`'s deliberate absence-check literal, and (c) FEAT-31's own closed-feature `notes/`/`plan.yaml`
archive (a different, already-shipped feature's historical record — correctly untouched). Zero live
references in `.claude/settings.json`, `.harness/harness.json`, `run-unit-tests.sh`, or `SKILL.md`
(directly grepped all four, confirmed exit 1/no-match). `.claude/settings.json`'s `PostToolUse` block
now carries only the `check-domain.sh --post` hook — the second object (the `context-watch-hook.py`
entry) is gone, valid JSON, no trailing comma.

### Q5 — DEC amendments: amend-not-strike is right for all three, and the specific SC-09 sub-clauses hold

- **DEC-198** (`:6806`): its amendment (`:6867` on) explicitly states the key **is present** at
  `.harness/harness.json:169` (value `200000`) and calls the equal figures "coincidence, not
  derivation" — confirmed both the amendment text and the harness.json line directly. It does **not**
  claim absence. This is a corrected recurrence of the cycle-0 panel's F1 finding (which flagged the
  plan's D-05 draft asserting the key was absent) — the build's actual text is the corrected version,
  and the amendment itself says so ("an earlier draft ... asserted the key was absent, which would have
  contradicted this entry's own un-amended paragraph").
- **DEC-201** (`:7030`): ruling survives verbatim; superseded text is only the self-identification
  paragraph. Verified DEC-204's supersession sentence ("supersedes DEC-201's host-specific mechanics for
  OMP while preserving its no-wait conduct and evidence standard") **pre-exists this diff** — it sits at
  line 7412 in the pinned tree and at the identical line 7412 in `git show <base>:DECISIONS.md`, i.e.
  this feature did not touch it, it only builds on it. The DEC-201 amendment explicitly says "this adds
  NO new supersession" and states the accessor behaviour as "one build's observed behaviour, not a
  timeless property of the OMP API" — matches SC-09's wording requirement exactly, confirmed by reading
  the amendment text in full, not by grep.
- **DEC-159** (`:4045`): its amendment corrects the present-tense claim that
  `context-watch-hook.py` is a registered PostToolUse hook, states the OMP `tool_result` injection now
  delivers the same capability, and explicitly says "No Claude hook is registered for this any more."
  Matches SC-09's third sub-clause.
- `gen-decisions-index.py --stdout` diffed clean against the committed `DECISIONS-INDEX.md` (ran it:
  exit 0, empty diff). `test-gen-decisions-index.py` also passes (10/10).
- DEC-188's strike test (tree flatly contradicts the *ruling*) does not fire on any of the three: all
  three rulings survive; only implementation-vehicle sentences went stale. Amend is correct, matching the
  same reasoning the cycle-0 panel already applied to this exact question for DEC-159 ("Considered and
  NOT flagged" in that digest) — re-derived independently here, same conclusion.

## Stage 2 — code quality

**No must_fix. No high-severity findings.** Hunted fail-open specifically, per this feature's own
purpose, across every `catch`, `undefined` return and early return in the new code.

### Checked and dismissed (recorded so it isn't re-raised)

- **Widening ladder's first-fragment discard, checked for an off-by-one that returns a WRONG number.**
  `readContextAnchor` unconditionally discards the first `\n`-split fragment on every non-whole window
  read (`:493`), even in the rare case where the window's start byte happens to land exactly on a record
  boundary (making that "torn" fragment actually complete). Traced the consequence: because the loop
  scans from EOF backward and returns on the **first** (= newest) match, discarding the *oldest* fragment
  in a partial window can only cause an extra widen-and-retry when that discarded record was the sole
  anchor in that window — never a wrong figure, because a wider window (and eventually the whole-file
  pass, which never discards) will re-include the same record and find it correctly. Confirmed this is
  the design's deliberate bias (skip/retry over guess), not a defect. REQ-03 holds.
- **Once-per-session cap's actual scope, checked against BRIEF's claim that it short-circuits the read.**
  `contextNoticeEmitted` gates the entire `if (currentAgent === ... && toolName === "task" && !contextNoticeEmitted)`
  block (`:791`), so `resolveSessionFile`/`readContextAnchor` are not called at all on a later wake once
  the flag is set — confirmed by reading the guard's placement, not just the flag's existence. It is set
  only on the two notice classes (`failed`, `inert`); a healthy under-threshold or over-threshold `tokens`
  result never sets it, so the cheap path stays uncapped and each wake re-evaluates, matching eng-lead's
  cycle-0 A4 dismissal ("does not suppress healthy advisories").
- **Field-identifier symmetry (eng-lead's cycle-0 A1), checked for duplication.** `grep -n
  "message.contextSnapshot.promptTokens" harness-hooks.ts` returns exactly one hit — the `const
  CONTEXT_TOKENS_FIELD = ...` declaration. `contextInertText` takes `field` as a parameter and never
  restates the literal; the inert notice cannot disagree with the parse. A1 landed as specified.
- **`test-orchestrator-playbook.py` case4, named plainly per the dispatch.** It is a wording assertion
  by construction: it checks two prose phrases are present in `SKILL.md` and that `"context-watch.py"`
  and `"200000"` are absent. It protects that the **prose** describes the mechanism and never restates a
  threshold numeral that would go stale — it does **not** protect that the mechanism **works**; that is
  carried entirely by the bun behavioural suite (T-01/T-02/T-03's `readContextAnchor`/injection tests).
  This is exactly what BRIEF.md's SC-08 discloses ("grades prose accuracy only ... no SC rests on wording
  alone"), not a gap discovered here.
- **`resolveContextWarnTokens`'s ratio text at a degenerate threshold (0).** `resolveContextWarnTokens`
  accepts any finite number including `0` as a configured `orchestrator_context_warn_tokens`; if an
  operator set it to `0`, `contextAdvisoryText`'s `(tokens/threshold).toFixed(2)` would render
  `"Infinityx"` rather than crashing. Low severity, no concrete cost stated (DEC-198 calibration is
  explicitly out of scope per BRIEF's Constraints, and this is a calibration-adjacent misconfiguration,
  not a code defect) — noted, not filed as a finding.

### The fifth inert check — hunted, none found

Went through every new assertion in `omp-hooks.test.ts` and the changed Python tests and asked what
each binds and what would have to break for it to fail:

- `readContextAnchor`'s four cases bind the real function against a real captured fixture (host-produced,
  not hand-authored) — fails on a wrong number, a window regression, or a wrong `kind`. Not inert.
- `resolveSessionFile`'s cases bind against fake `ctx` objects but assert on the real exported function
  with the real branch logic (throw/not-a-function/missing manager/empty/undefined) — these are
  legitimately unit-level; the live host surface is explicitly NOT claimed here (the comment says so),
  and is instead the job of `test-omp-session-accessor.py`, which does bind the real accessor. The split
  is disclosed, not hidden.
- `contextAdvisoryText`'s two cases assert exact numeric substrings (`1.12x`, `1.49x`) computed from two
  different thresholds — a hardcoded string cannot pass both. Not inert.
- The five injection cases + inert-notice + accessor-failure + under-threshold cases all drive the real
  `registerHarnessHooks` and assert on its real return value/content array — not inert.
- `test-omp-session-accessor.py`'s six cases each name a subject (omp on PATH, probe file, a subagent
  session with `usageDefined:false`, `getSessionFile` resolving inside it, the nested-path shape, the
  main session's flat-path shape) and each is gated `if not X: return finish()` rather than silently
  passing — so a missing precondition FAILS the run rather than skipping silently. Not inert.
- `test-orchestrator-playbook.py` case4 — the one genuinely wording-bound assertion, already named
  above, with its scope explicitly disclosed in BRIEF.md rather than hidden.
- T-06's DECISIONS.md checks (`git grep -q resolveContextWarnTokens`/`getSessionFile`) are bare presence
  greps, but I independently read the full amendment prose at source (not just grepped) and confirmed the
  substance the grep can't verify — so the combination is sound even though the grep alone would be weak.

No fifth instance of "a document changed" or "a stub changed" masquerading as a capability check.

## Not re-litigated (per dispatch's SETTLED list)

Claude-path retirement, one-file design, DEC-174 main-session-direct routing, full FEAT-44 scope/board
state — none reopened.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Spec-compliant across all 8 REQs with source-level traceability; both cycle-0 must_fix findings (false absent-key claim, untested accessor-drift path) are correctly discharged; no fail-open branches found in the new code; no must_fix."
  severity_max: low
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "7ebfc9eb9cb77939b325f559d64e6b0cbb22d907..21e97ed88c8d56226b391fc37fb0049e8ead5fff"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-code-reviewer-c1.md
```
