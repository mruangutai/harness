# DOES THIS PLAN DELIVER THE OPERATOR'S STATED INTENT? — FAIL

FAIL — in substance yes (every clause of #1308's Requirement maps to a REQ, every regression case to a
behavioural SC, scope stays inside the grilling note's allowed set), but three defects block it as
written: T-02 case17 mandates an assertion D-10 makes unsatisfiable; REQ-07's *concurrent* clause has
no criterion; T-02 omits REQ-01/REQ-02 from `traces:`. Read-only grading of the drafted BRIEF.md and
plan.yaml against `issue://1308` and `.harness/notes/grilling-six-residual-bugs-2026-09-05.md`.

## 1 — Issue Requirement clauses → REQ (no unmapped clause)

| Clause | REQ | Note |
|---|---|---|
| replace atomically | REQ-01 | ok |
| drop when contract permits removal | REQ-02 | ok; the *permission* half is contract-side only (D-12), not mechanised — acceptable, stated |
| preserve section caps | REQ-03 | ok (D-07 caps once on final state) |
| reject missing targets | REQ-04 | ok |
| reject ambiguous targets | REQ-05 | ok (D-03 enumerates three conditions) |
| fail closed, no partial rewrite | REQ-06 | ok (D-08) |
| compatible with concurrent union-merge behaviour | REQ-07 | mapped, **not criterion-covered** — see check 4/gap G3 |
| focused regression coverage (5 cases) | REQ-09 | ok |
Added beyond the issue: REQ-08 (contract/mechanism agreement) — derives from the issue's Alternative
paragraph, justified by D-11. Not scope creep.

## 2 — Regression cases → criteria that exercise BEHAVIOUR

replacement at capacity SC-01/T-02 case11 · removal SC-02/case12 · missing target SC-03/case13 ·
ambiguous target SC-04/case14 (a,b,c) · atomic failure SC-05/case15. All five assert exit code +
stdout token + post-state (entry count, `- G-03:` absence, sha256) — none is a "the code contains X"
assertion. **No content-only criterion among the five.** SC-07 additionally pins a permanent red case
(u10 against `compute_union`), which is the strongest item in the draft. Content-shaped criteria do
exist outside the five: SC-10 (`DECISIONS-INDEX.md` carries a DEC-216 row) and half of SC-09 — flagged
below, not part of the issue's regression sentence.

## 3 — Traceability, both directions

- Every T traces ≥1 REQ: T-01, T-02 (7 REQs), T-03 (REQ-08), T-04 (REQ-08). **No orphan tasks.**
- Every SC reachable from a task: SC-01..05 → T-02 cases 11–15; SC-06 → case16; SC-07 → T-01
  `tests/unit/test-expertise-ops.py`; SC-08 → cases 11/12 `check-expertise.sh`; SC-09 → case17;
  SC-10 → T-04. **No orphan SCs.**
- **GAP G1:** T-02 `traces: [REQ-03..REQ-09]` omits REQ-01 and REQ-02, yet its case11/case12 are the
  only *integration* proof of replace and drop. REQ-01/02 are traced solely by T-01 (unit).

## 4 — Determinism

Observable in all of SC-01..SC-08 (exit codes, `REPLACED P-07`/`DROPPED G-03`, sha256 identity,
ordinal position 7, section counts).
- **GAP G2:** SC-09 "the case fails if either side changes alone" is gradeable two ways — read the
  assertion and call it met, or demand a demonstrated mutation. No mutation is required anywhere.
- **GAP G5 (minor):** SC-10 "whose hand-written ruling names the replace/drop operation" is a
  judgement; T-04's operational form is `grep -q '^- DEC-216 .* :: .*ops'`, which the substring `ops`
  satisfies incidentally (e.g. the word "ops" anywhere on the row). Weak discriminator.
- **GAP G3:** no SC exercises REQ-07's concurrency half. SC-06 covers add-only exit codes/tokens only;
  D-09's claim that `ops` takes the same lock file is asserted, never checked.

## 5 — Verifiability (paths checked, nothing project-wide run)

`tests/integration/test-expertise-merge.py`, `tests/integration/test-gen-decisions-index.py`,
`.claude/skills/harness/bin/check-expertise.sh`, `.claude/skills/harness-distill/SKILL.md`,
`.harness/harness/docs/SPEC.md` all EXIST in the worktree; `tests/unit/test-expertise-ops.py` is
created by T-01. `check-expertise.sh` does accept a file argument (its `for arg in "$@"` loop), so
SC-08 is invocable. Every verify is a targeted single-file invocation — no suite. Anchors re-derived
and both hold: SKILL.md carries "Updates are **ops**, each naming its target:" and SPEC.md §5.3
carries "The apply is a union merge, not a whole-file write". **Nothing found wrong here.**

## 6 — Scope against Allowed / Out of scope

T-01 implementation + focused unit test; T-02 focused tests; T-03 contract text; T-04 governing
docs/decision. All four inside "implementation, focused tests, governing decisions/docs, lifecycle
artifacts". No compatibility shim (D-09 leaves the `apply` path *unmodified*, which is the opposite of
a shim), no redesign, no unrelated cleanup. **Nothing found wrong here.**

## 7 — Stop conditions and the 8-cycle cap

Four tasks, chain T-01 → T-03 → {T-02, T-04}; nothing presumes a risk acceptance, a scope reduction or
a gate waiver. Advisory, not a gap: T-02 and T-04 `depends_on` T-03, which is `main-session-direct`, so
a build cycle must yield to the main session mid-flight — declared, and orchestrator-schedulable, but
it is the one place cycles can be burned waiting.

## 8 — Primary path vs the issue's Alternative

The plan takes the **primary path** (build the operation) and applies the **Alternative narrowly to one
verb**: D-10 leaves `merge` unimplemented and rewrites the contract to express it as replace + drop.
It does both, partially, and that is consistent with #1308 — the Requirement paragraph names only
replace and drop, and the Alternative's remedy is exactly "change the contract where the mechanism
cannot remove". Stated plainly so the panel does not read it as hedging.

## Gap list (repair is a separate dispatch)

- **G4 — blocking, internal contradiction.** plan.yaml T-02 case17 intent: "assert set equality, not
  containment." The contract verb set after T-03 is {add, replace, merge, drop}; the tool accepts
  {add, replace, drop} by D-10. Raw set equality is therefore *false by construction* and case17 must
  fail. SC-09's own wording is the disjunction ("accepted **or** stated by that same file to be
  rewritten"). The task instruction and the criterion disagree; the doer receives `intent:` alone.
- **G1** — plan.yaml T-02 `traces:` missing REQ-01, REQ-02 (see check 3).
- **G3** — BRIEF.md REQ-07's "concurrent" clause has no SC; D-09's shared-lock claim is unverified.
- **G2** — BRIEF.md SC-09 gradeable two ways; no mutation demonstration required.
- **G5 (minor)** — plan.yaml T-04 verify `.*ops` is a weak discriminator for SC-10's ruling text.

Checks that found nothing: 5 (verifiability), 6 (scope), 8 (path choice) — and within check 2, no
content-instead-of-behaviour criterion among the issue's five regression cases.
