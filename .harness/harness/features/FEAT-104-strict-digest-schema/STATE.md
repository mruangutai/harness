# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: `2026-09-10-17-panel-validator` (**PASS**, `harness-validator-lead`) — the final independent
  reviewer panel, cycle 11, all four reviewers over the pin `984bd26b`
- status: validate — **the panel is CLEAN and the validate gate is closed.** `must_fix: []`, four
  PASS verdicts, `severity_max: med` (advisory, not blocking, under
  `gates.review: advisory_unless_high`), zero send-backs, so `cycles_used` stays **10 of 10**. No
  goal-check, UAT, briefing or merge this cycle. Owed before ship: the SC-13 UAT and the CEO
  briefing — both to be run with the budget exhausted, so **no fix cycle remains**.

**PF-C10-01 is CLOSED, and closed by the reviewer that raised it.** `harness-ui-reviewer` rated it
`high` at c10 — the rating that would have blocked the ship — MEASURED its closure live at this pin
and WITHDREW its own rating; qa measured the same stderr independently; code confirmed the mechanism
at source. The dissenting lens retracted on its own evidence rather than being talked down.

**The one regression the fix could have introduced is REFUTED four ways plus my own measurement.**
Both messages being conditional means a schema error filling NEITHER `_missing_required` NOR
`_offending` would append nothing to `out` and ACCEPT a write the old code refused — fail-OPEN. All
four reviewers re-derived independently (I forbade adopting the previous cycle's enumeration) and
agree: only `type`, `additionalProperties` and `required` sit at the step object's own level, and the
first two are caught **outside** the `if _schema_errors:` block. **I censused the schema myself**:
`properties.steps.items` at `984bd26b` declares exactly `type: object`, `required`,
`additionalProperties: false` at its own level — no `minProperties`, `dependentRequired`,
`dependencies`, or step-level `if`/`allOf`/`anyOf`/`not`; the `propertyNames`/`oneOf` pair sits one
level down under `properties.evidence` and therefore reports with a path.

**Verified at my own tier, not on the panel's word.** The pin resolves to
`984bd26b4dc339ea984d2532221477d465a2b05c`; HEAD `cd1c6cb4` is bookkeeping-only —
`git diff --stat 984bd26b..HEAD -- . ':!.harness'` is **EMPTY**, all 11 changed paths inside the
feature dir — so working-tree reads were code-identical to the pin and the pin needed no move. I
re-ran the focused file: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py`
→ **exit 0, 13 `ok` lines**, including `schema_version 2 names a missing required step key`. The lead
digest validates **exit 0** under `validate-digest.py lead`; all four c11 notes are on disk; the run
`state.yaml` reads `status: complete` with four `complete`/`PASS` steps. **DEC-174 held absolutely**:
after the panel `git status --porcelain` carries exactly the four untracked reviewer notes and **zero
tracked modifications** — no source or test file touched, not even reverted.

**Matrix provenance as the panel stated it.** `matrix_ok: true`. Focused `test-check-domain.py`
**13/13 exit 0 MEASURED** by qa (and by me), the PF-C10-01 case reproduced standalone at case level.
Suite figures — unit **36 files**, integration **70 files**, exact baseline parity — are **ADOPTED**
from run 15 at the same pin and labelled as adopted, because this dispatch barred project-wide runs.
`change_type: bugfix` → unit + integration. `code_grade: pass` (42 functions, 0 SEVERITY lines).

**SC-08 stays MET on both seams, with one honest weakening recorded.** The step seam's discriminating
clause is pinned by the **invocation path**, not string uniqueness: `undeclared step key` has TWO
producers (`check-domain.sh:1671`, `check-state.sh:1526`). Safe today because the test fires a Write
hook, but thinner than c10 implied. The digest seam (`test-validate-digest.py:3130-3146`) is
untouched; `validate-digest.py` byte-identical, measured by two reviewers.

**Three items are the lead's own, not any reviewer's, and are recorded as such:** (1) `CF-4` fell
between all four lenses and was disposed by nobody — the lead disposed it carried-unchanged and
reported the near-miss rather than smoothing it; (2) `Q14` was resolved UPWARD on a mechanism, not
averaged; (3) the SC-08 two-producer finding, visible only across two lenses at once.

**Q14 and Q15 were graded at present tense, as dispatched, and neither expanded scope.** Q14 is
reachable today and CONTESTED (ui `med`, qa `low`, code `low`, lead `med`). Q15 is present-tense
UNREACHABLE at `info`: the emitter was deliberately NOT hardened against keywords the schema does not
declare.

## Open Questions

- Q14 (not blocking, main session, DEC-174 — **CONTESTED, re-rated**): a type/range failure on a
  **declared** step key (`cycles: not-an-int`) routes via `_path[0]` into `_offending` and prints
  under `undeclared step key or evidence shape.`, whose remedy tells the author to move the key under
  `evidence`. ui `med`, qa `low`, code `low`, **lead `med` adopted on mechanism**: an author who
  FOLLOWS the remedy produces `evidence: {cycles: "3"}`, ACCEPTED at exit 0 while the step-level field
  the retry accounting reads goes silently absent — a different class than misleading prose.
  Reachable today, untested, remedy is one branch inside the carve-out. Fix at the next main-session
  touch of `check-domain.sh`, or backlog?
- Q15 (not blocking, main session — `info`, present-tense unreachable): the branch keys on the
  validator NAME (`required`) not the structural cause (empty `error.path`). A future step-level
  `minProperties`/`dependentRequired` would fill neither bucket and emit no denial. Schema census (me
  plus all four reviewers) confirms no such keyword at the pin; no test can redden until one exists.
- Q18 (not blocking, **new**, raised only by `harness-security-reviewer`, info/latent — the lead
  labelled it Q16, renumbered to avoid collision): `_missing_required` keys on
  `_error.validator == "required"` with **no path check**, so a NESTED required violation (a future
  `evidence` sub-object) would be reported as a missing STEP key. Fail-closed but mislabelled;
  unreachable today; distinct from Q15. Gate on `error.path == []` when nested `required` arrives?
- Q19 (not blocking, **new** — lead labelled it Q17): SC-08's step seam is pinned by the INVOCATION
  path, not string uniqueness. Hold a future test asserting that phrase against combined or at-rest
  output to a producer-unique string?
- Q11 (**RECURRED, now a persona-level pattern**, harness defect): `harness-code-reviewer`'s
  `mktemp -d` probe was refused by `bash-write-guard` for the SECOND consecutive cycle (writing only
  `/tmp`) while qa and ui executed live probes. It reported the refusal rather than working around it
  — guard working, reviewer correct. Guarantee read-only panels a scratch-write route, so "reasoned,
  not mutation-executed" stops being that one lens's permanent ceiling?
- Q16 (harness defect, verified by me): a `^FAIL ` census over `run-unit-tests.sh` is defeated by
  `test-factory-claim-mutation.py` reprinting 4 `FAIL  BUG-1290 …` lines as success at exit 0.
- Q17 (harness defect): "the tree must be clean" is unsatisfiable for an agent writing its own
  artifact — only `runs/**` is gitignored. Scope such clauses to tracked modifications.
- Q12 (harness defect): terminal `yield` exiting 1 with "yield called with null data" on a complete
  fenced block. Seen on qa, the eng lead, two `dev-ops`. Did NOT recur this cycle.
- Q13 (main session): SC-08's step seam closes under `plan.yaml:460-462`'s route text, a narrower
  reading of "symbol" than the digest seam's. Hold a future feature to it? See Q19.
- Q6 (**NARROWED**, harness defect): the append-only digest channel CAN repair a REMOVABLE key (the
  validator slices from the LAST `VERDICT:`), never a MISSING required field or a verdict
  CONTRADICTION.
- Q-B3 / Q4 (harness defect): the digest contract has no home for per-kind suite exits and file
  counts, and the `lead` schema declares no `code_grade`. Avoided again by naming the declared field
  set and carrying `code_grade` inside the headline; validated first time.
- Q9: REQ-08's generic-lead archive exemption (`validate-digest.py:1407`) has no test able to redden.
  Does not falsify REQ-08.
- Q1 (DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526` interpolates `run_id` and the
  step id as bare strings; the DEC-85 route can spoof the INV-16 audit line. Carried unchanged at c11.
- Q2: **CF-3** (`low`) — `abff2a84`, a FEAT-56 station flip, is this branch's root commit, untracked
  by any REQ or D. Accept and record in the ship note.
- Q3: **CF-2** severity CONTESTED — qa `med`, code `info`, c9 lead `low`.
- Q5 (DEC-174): **CF-4** (`low`) — the downgrade branch renders a raw `None` in the omitted-on-update
  edge; **disposed by the lead, not by any reviewer**, carried unchanged on `validate-digest.py` being
  byte-identical. Q7: the 3 complete + 2 partial version-predicate spellings want one home.
- F-QA-1: `T-05` declares `change_type: logic` against DEC-212's `touches_config_shape`. Untouched by
  this delta, derived `bugfix`. F-104C10-01/02 (info) stay dismissed non-gating, as at c10.
- Residual non-gating risks, in the c9/c10/c11 panel digests: the DEC-85 Bash-write bypass; F2's
  runtime residual (DECLINED stands, `check-state.sh` topology unchanged); the `_no_parser` bootstrap
  early return; schema guards argued fail-closed rather than mutation-proven; the stale comment at
  `check-domain.sh:1646-1647`, now describing half the loop (ui `low`). Standing: the INV-26
  card/plan mismatch and the per-persona worktree-claim guard.
