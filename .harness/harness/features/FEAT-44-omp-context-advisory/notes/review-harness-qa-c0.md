# QA plan review — FEAT-44 — verifiability of the 9 SCs

No implementation exists; this reviews the plan's verification design only. All findings are
reasoned, not measured against a diff (O-03).

## 1. Per-SC verifiability

| SC | Claimed | Verdict | Note |
|---|---|---|---|
| SC-01 | automated | sound | fixture-driven numeric equality, red-before-green required |
| SC-02 | automated | sound | widening case genuinely reddens a fixed-window impl |
| SC-03 | automated | sound | two branches (inert vs none) asserted separately |
| SC-04 | automated | sound | four scope conditions each asserted on their own |
| SC-05 | automated | sound | `"isError" in result` form named explicitly, avoids truthiness trap |
| SC-06 | automated | sound | two thresholds defeat a hardcoded ratio/string; math checks out: 223029/200000→1.12, 223029/150000→1.49 |
| SC-07 | automated | sound but coarse | five conjuncts in one criterion — a single FAIL cannot say which of the five broke. Not a mislabel (every conjunct is machine-decidable), but a diagnosability nit. Alternative: split into SC-07a (artifact/reference removal, T-04's own grep) and SC-07b (suites green, gate-time), no cost since T-04's verify already computes both halves separately |
| SC-08 | inspection | sound | presence of DEC-198/199/201 citations and absence of "context-watch" is already grepped by T-05's own guard test; SC-08 correctly scopes itself to the semantic-accuracy residue (does the prose actually describe the live mechanism) that grep cannot judge |
| SC-09 | inspection | sound | structural claims (resolveContextWarnTokens/getSessionFile named, index regenerated) are grepped/diffed in T-06's verify; SC-09 correctly scopes itself to the prose-judgment residue ("adds no new supersession language", "corrected") |

SC-08's own disclaimer holds: no capability is covered ONLY by SC-08/SC-09 — both are prose-accuracy
checks over documents, and the runtime capability they describe is independently proven by SC-01–07.

## 2. REQ → SC → task matrix

| REQ | SC | Producing task(s) | Gap |
|---|---|---|---|
| REQ-01 | SC-01,02,03,05,06 | T-01,T-02,T-03 | **partial** — see §3 coverage gap below |
| REQ-02 | SC-04 | T-01,T-03 | none |
| REQ-03 | SC-03 | T-01,T-02 | none |
| REQ-04 | SC-03 (inert half) | T-01,T-02,T-03 | **see §4 — partial discharge** |
| REQ-05 | SC-06 | T-01,T-02,T-03 | none |
| REQ-06 | SC-08 | T-05 | none |
| REQ-07 | SC-07 | T-04,T-06 | none |
| REQ-08 | SC-09 | T-06 | none |

No orphan REQ, no SC with zero producing task, no task tracing to a REQ it does not advance.

## 3. Coverage gap found in Phase 1 (before reading task detail)

REQ-01 promises "no extra token" on the healthy path. T-03's intent states the tokens-at-or-under-
threshold branch returns nothing. **No enumerated test in T-01's intent exercises that branch** — the
five injection tests and the inert-notice test all use fixtures/conditions constructed to be *over*
threshold, wrong-persona, wrong-tool, or anchorless. There is no test asserting "orchestrator, task
result, tokens ≤ threshold → no advisory, content unchanged." This is the single most common runtime
state (below-threshold is the default) and it is the one path with zero test pressure. Concrete,
cheap fix: add one case to the `describe("context advisory injection")` block in T-01 using a fixture
or synthetic anchor under threshold, asserting the returned content is unchanged from the no-advisory
baseline.

## 4. `bun test` on a missing named import — empirical result

Command and output, run in `/tmp/bun-import-probe` (outside the repo, throwaway):
```
$ bun test ./probe2.test.ts
SyntaxError: Export named 'readContextAnchor' not found in module '.../lib/real.ts'.
 0 pass
 1 fail
 1 error
Ran 1 test across 1 file. [5.00ms]
```
Four real `test()` cases were defined across two `describe` blocks (`readContextAnchor` ×2,
`resolveContextWarnTokens` ×1, plus one for an already-existing export); **none ran**. Bun aborts the
whole file at module-evaluation time and reports a single synthetic `1 fail`, not a per-test failure.

Applying this to T-01's verify:
```
grep -q readContextAnchor   →  MATCHES (the SyntaxError text names the missing export)
grep -qE "[1-9][0-9]* fail" →  MATCHES ("1 fail")
```
Both conjuncts pass **before a single one of the 14 enumerated behavioural tests is ever collected**,
because only the *first* missing named import is reported, and it happens to be `readContextAnchor`
by construction (T-01's intent lists it first in the import extension). This is not the DEC-98
scenario in its literal form (bun *does* emit "N fail" here, so the verify is not permanently stuck) —
it is the milder, real converse: the verify's two greps are satisfiable by a load error alone, so
they do not actually confirm any of the 14 tests were written correctly, or written at all beyond the
bare `readContextAnchor` name appearing somewhere reachable by the import list. A malformed or
incomplete T-01 (e.g., only 2 of the 14 tests present, or a typo'd describe title) passes this verify
identically to a complete one, as long as production code is still absent and the first missing name
resolves to `readContextAnchor`. Medium-severity design gap in the verify, not a hard blocker — the
task's `intent:` is explicit enough that a competent author will still write all 14, but the verify
itself cannot detect a shortfall. Cheapest fix: add a static count check independent of runtime
output, e.g. `grep -c '^\s*test(' omp-hooks.test.ts` ≥ (24 baseline + 14 new) = 38, alongside the
existing checks.

## 5. Existing test count at base and T-03 arithmetic

`git show 7ebfc9e:.claude/skills/harness/bin/omp-hooks.test.ts` — 24 `test(` occurrences; running it
live: `24 pass / 0 fail / 39 expect() calls`. T-01's intent enumerates 4 + 2 + 2 + 5 + 1 = 14 new
tests. 24 + 14 = **38**, which matches T-03's `grep -qE "[3-9][0-9] pass"` (two digits, leading digit
3–9). The arithmetic is sound as written — contrary to the risk named in the assignment, this
threshold is achievable, provided T-02/T-03 add zero further test cases (they don't; they're
implementation-only tasks). No defect here.

Also verified: `run-unit-tests.sh`'s `UNIT_SCRIPTS` includes `test-omp-hooks.py`, a thin Python
wrapper that shells out to `bun test omp-hooks.test.ts` (`.claude/skills/harness/bin/test-omp-hooks.py`).
So the standing `unit` test_kind's `cmd` genuinely exercises the bun suite T-01–T-03 write, not merely
a detect-glob false positive (P-14 checked and satisfied, not violated).

## 6. REQ-04 — verdict: **partially discharged**

(a) A frozen fixture cannot detect live drift — agreed and correctly not attempted. The runtime inert
notice is a real substitute for the *record-shape* class of drift (the `contextSnapshot` field moving
or vanishing from the JSONL), at a real, disclosed, bounded cost (one full-file scan, then capped at
one notice per session).

(b) The once-per-session cap does mean drift arriving mid-feature reaches exactly one `tool_result`.
That is genuinely weaker than a hard gate — the orchestrator can read past a single advisory line
among other content and take no action, and nothing escalates it further within the session. This is
the accepted cost of a "loud" runtime notice as opposed to a CI-time hard fail, and is a reasonable
trade given DEC-163/DEC-36 rule out the CI alternative (see below).

(c) **The load-bearing gap.** `readContextAnchor` distinguishes `"none"` (no session file — silence,
by design) from `"inert"` (session file present, scanned to exhaustion, no anchor — loud). But T-03's
own intent instructs resolving the session file as
`ctx.sessionManager?.getSessionFile?.()` inside try/catch **returning undefined on throw**,
"mirroring the `getSessionId` helper" — and that helper (`.omp/extensions/harness-hooks.ts:323-330`)
already collapses "API absent", "API throws", and "API present but genuinely has nothing to report"
into one indistinguishable `undefined`. A host change to the *session-resolution mechanism itself*
(the API renamed, its shape changed, or it starts throwing) — which is **exactly the failure class
that caused #923 in the first place**, `ctx.getContextUsage()` returning `undefined` — lands in
`readContextAnchor(undefined)` → `{ kind: "none" }`, the silent branch, not `{ kind: "inert" }`, the
loud one. REQ-04's "that fact announces itself" guarantee covers *record-content* schema drift only;
it does not cover *session-resolution API* drift, and the reasoning in D-02/D-03 never distinguishes
these two drift classes.

(d) **Verdict: partially discharged.** The mechanism closes the failure mode for the JSONL content
shape but reopens, one layer down, the identical silent-`undefined` shape that is the entire reason
issue #923 exists. Concrete cheapest addition: have the `getSessionFile` resolution wrapper
distinguish "threw / not a function / `ctx.sessionManager` missing" from "called cleanly and returned
no path", and route the former into a notice (reusing `contextInertText`'s once-per-session shape,
naming the accessor rather than the field) rather than into silent `none`. This is a runtime behavior
change fully unit-testable with a fake `ctx` whose `sessionManager.getSessionFile` throws — the same
technique T-01 already uses for its five injection tests — so it does **not** trip DEC-163: DEC-163
and its DEC-36 antecedent govern *test-time* soft skips against live, possibly-absent CI data (a
live-schema assertion needing a real `~/.omp/agent/sessions/**` file on the runner). This addition
needs no live data and no CI environment dependency; it is a pure function of a mocked `ctx`, so the
BRIEF's DEC-163 argument, while sound for the question it actually answers (rejecting a live CI
assertion), does not extend to cover this narrower addition, and nothing in the plan's own reasoning
claims it does — it simply never considers this drift class.

## 7. Test matrix per change_type (plan-level, no diff to gate)

- `bugfix` (T-01,T-02,T-03): floor is `unit` always, `__bug_class__` when `match_bug_class` (no
  bug-class table entry applies here — not firing). Satisfied: `omp-hooks.test.ts` is a registered
  `UNIT_SCRIPTS` member via `test-omp-hooks.py`.
- `cross_module` (T-04): floor is `unit` **and** `integration`, both always. T-04's own verify covers
  only the mechanical guards (`--check-kinds`, `test-run-unit-tests-kinds.py`, grep/ls-files); the
  full green-suite claim (both kinds) is explicitly deferred to a manual post-task run and to the qa
  gate — disclosed in the intent, not silently dropped. Floor is satisfiable provided the gate agent
  actually runs `run-unit-tests.sh` with no `--kind` at review time.
- `docs` (T-05,T-06): floor is empty (`always: []`). Both tasks carry guard tests exceeding the floor
  (`test-orchestrator-playbook.py`, `test-gen-decisions-index.py` + index diff). No gap.
- The known `typecheck: cmd: null` gap is disclosed in the BRIEF and is not re-reported here.

`matrix_ok: true` — reasoned against the plan's design, not measured against a diff (none exists yet).

## Nits

- SC-07's five-conjunct bundling reduces diagnostic precision on failure (§1).
- T-01's verify can pass on a load-error string match rather than confirmation of 14 real test bodies
  (§4) — medium severity, cheap static-count fix available, not blocking on its own.

## Files authored

Only this note. No test, fixture, or source touched; probe files live outside the repo at
`/tmp/bun-import-probe/` (throwaway, not part of any deliverable).

```yaml
VERDICT: FAIL
DIGEST:
  headline: REQ-04's runtime drift detector silently swallows exactly the failure class (session-resolution API drift) that #923 exists to fix, collapsing it into the same undefined-on-throw path as "no session yet"
  suite: n/a
  matrix_ok: true
  kinds: []
  coverage_gaps:
    - "REQ-01 healthy-path (tokens at/under threshold) has zero test pressure in T-01's enumerated injection tests"
    - "REQ-04: session-resolution API drift (getSessionFile throwing/renamed/missing) is indistinguishable from 'no session yet' — lands in silent kind:none, not loud kind:inert"
  sc_evidence:
    - { id: SC-01, test: "T-01 intent, describe(readContextAnchor) case 1 (not yet written)" }
    - { id: SC-02, test: "T-01 intent, describe(readContextAnchor) case 2, widening (not yet written)" }
    - { id: SC-03, test: "T-01 intent, describe(readContextAnchor) cases 3-4 (not yet written)" }
    - { id: SC-04, test: "T-01 intent, describe(context advisory injection) cases 1-4 (not yet written)" }
    - { id: SC-05, test: "T-01 intent, describe(context advisory injection) cases 1 and 5 (not yet written)" }
    - { id: SC-06, test: "T-01 intent, describe(contextAdvisoryText) + describe(resolveContextWarnTokens) (not yet written)" }
    - { id: SC-07, test: "T-04 verify block + manual run-unit-tests.sh at gate time" }
    - { id: SC-08, test: "inspection at git show <review_sha>:.claude/skills/harness/SKILL.md" }
    - { id: SC-09, test: "inspection at git show <review_sha>:.harness/harness/docs/DECISIONS.md" }
  open_questions:
    - { id: Q1, question: "Should T-02/T-03's intent add the session-resolution-vs-no-session distinction described in §6(d) before build, or is the once-per-session record-shape notice judged sufficient by the user knowingly (a la DEC-163's accepted-gap pattern)?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-qa-c0.md
```
