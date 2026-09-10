# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: `2026-09-10-18-goalcheck-product` (**PASS**, `harness-product-lead`) — the final goal-check of
  the DELIVERED feature against the signed BRIEF at the pin `984bd26b`
- status: validate — **the goal is MET. 9/9 REQs and 14 of 15 live criteria are met at the pin;
  SC-13 (`verify: uat`) is the sole remaining item and only the operator can close it.** `must_fix`
  empty, no send-backs, so `cycles_used` stays **10 of 10**. No UAT, briefing, merge or ship this
  cycle. Owed before ship: the SC-13 UAT, then the CEO briefing — both with the budget exhausted, so
  **no fix cycle remains and none is needed**.

**SC-08, the only gap c9 found, is CLOSED at both seams — verified at source by me, not on pm's
word.** The fix landed at `790023f0` and is RETAINED at `984bd26b`:
`git show 984bd26b:tests/integration/test-check-domain.py` case *"schema_version 2 refuses an
undeclared step key, names it and gives its route"* (`:87-91`) requires `undeclared step key`,
`rogue_step_key`, **`run-state-schema.json`** and **`` `evidence` ``** in stderr — the route by file
and symbol, asserted as substrings, which is exactly what c9 found absent. The digest seam
(`test-validate-digest.py:3138-3146`) requires `validate-digest.py`, `PASSTHROUGH`,
`DOCUMENTED_OPTIONAL`, `SCHEMAS` in the one message. pm's ruling that the AT-REST seam
(`test-check-state.py:51-54`) is outside SC-08's subject is accepted on its mechanism: SC-08 grades
*rejection* text, INV-16 is a report over already-written artifacts, and the route is emitted there
anyway (`check-state.sh:1526-1528`). The unasserted route is Q20, a recommendation.

**SC-12 was EXECUTED this cycle, both halves, and I re-executed both at my own tier — nothing
adopted.** T-10's `verify:` from `plan.yaml:649-673`, byte-for-byte from the OWNER ROOT: positive
**`manifested 728 changed 0 vanished 0`, exit 0**; discrimination against a `/tmp` copy with one
hexdigest character altered **exit 1**, naming the altered path. pm's run named
`FEAT-10-software-factory/runs/goalcheck2-product/digest.md` (line 201), mine
`FEAT-14-feature-json-schema/runs/2026-08-10-01-plan-product/digest.md` (line 301) — two different
lines, so it discriminates per path, not by luck. Two cycles of run artifacts were written since the
c9 execution at `168f875f`, so a fresh grade was the only honest one. No real artifact was mutated;
the `/tmp` copy is deleted.

**Automated criteria rest on two legs, both recorded.** The discriminating assertion in the test
source at the pin — every c9 anchor re-derived by content string with `git show 984bd26b:<path>`,
because `790023f0` shifted all of them and pm re-located each — plus execution, **ADOPTED** from qa
run `2026-09-10-15-qa-gate-validator` at this same pin (unit exit 0 / 36, integration exit 0 / 70)
and labelled adopted; focused `test-check-domain.py` re-run read-only, **MEASURED** 13/13 exit 0.
SC-14 is `struck` — deleted during planning, absent from the signed BRIEF.

**The c11 panel's standing is unchanged and was not re-adjudicated:** PASS at this pin,
`must_fix: []`, four PASS reviewers, `severity_max: med` (advisory under
`gates.review: advisory_unless_high`), `code_grade: pass` (42 functions), `matrix_ok: true`.
PF-C10-01 stays closed by the reviewer that raised it.

**DEC-174 held absolutely.** `git status --porcelain` after the run carried exactly two entries,
both feature-tree artifacts the run legitimately writes — the goal-check note and pm's observations
log. **Zero tracked modifications to any source or test file.** The pin resolves to
`984bd26b4dc339ea984d2532221477d465a2b05c`; `git diff --stat 984bd26b..HEAD -- . ':!.harness'` is
EMPTY, so the pin needed no move.

**Readiness: the UAT may now be generated.** SC-13 is the one thing a human can settle and nothing
it depends on is outstanding. The operator reads the diff of the four DEC-174 carve-out files and
confirms it changes nothing beyond the declared contract; the concrete items are CF-1
(`check-state.sh:1525-1526`), CF-4 (`check-domain.sh` downgrade branch near `:1608`) and panel Q14
(`med`).

## Open Questions

- Q20 (not blocking, **new**, pm's R1 — recommendation, not an unmet criterion):
  `test-check-state.py:51-54` asserts run/step/key but no declaration route, though
  `check-state.sh:1526-1528` emits one. Outside SC-08's subject. One-line hardening inside the
  DEC-174 carve-out at the next main-session touch, or backlog?
- Q14 (not blocking, main session, DEC-174 — **CONTESTED**): a type/range failure on a **declared**
  step key (`cycles: not-an-int`) routes via `_path[0]` into `_offending` and prints under
  `undeclared step key or evidence shape.`, whose remedy tells the author to move the key under
  `evidence`. ui `med`, qa `low`, code `low`, **lead `med` on mechanism**: an author who FOLLOWS the
  remedy produces `evidence: {cycles: "3"}`, ACCEPTED at exit 0 while the step-level field the retry
  accounting reads goes silently absent. Reachable today, untested, one branch inside the carve-out.
- Q15 (not blocking, main session — `info`, present-tense unreachable): the branch keys on the
  validator NAME (`required`), not the structural cause (empty `error.path`). A future step-level
  `minProperties`/`dependentRequired` would fill neither bucket and emit no denial. Schema census
  (me plus four reviewers) confirms no such keyword at the pin; no test can redden until one exists.
- Q18 (not blocking, security-reviewer, info/latent): `_missing_required` keys on
  `_error.validator == "required"` with **no path check**, so a NESTED required violation (a future
  `evidence` sub-object) would report as a missing STEP key. Fail-closed but mislabelled;
  unreachable today; distinct from Q15. Gate on `error.path == []` when nested `required` arrives?
- Q19 (not blocking; pm's R2 restates it): SC-08's step seam is pinned by the INVOCATION path, not
  string uniqueness — `undeclared step key` has two producers (`check-domain.sh:1671`,
  `check-state.sh:1526`). Safe today because the test fires a Write hook. Hold a future test
  asserting that phrase against combined or at-rest output to a producer-unique string?
- Q11 (**RECURRED, persona-level pattern**, harness defect): `harness-code-reviewer`'s `mktemp -d`
  probe was refused by `bash-write-guard` for the SECOND consecutive cycle (writing only `/tmp`)
  while qa and ui executed live probes. It reported the refusal rather than working around it —
  guard working, reviewer correct. Guarantee read-only panels a scratch-write route?
- Q16 (harness defect, verified by me): a `^FAIL ` census over `run-unit-tests.sh` is defeated by
  `test-factory-claim-mutation.py` reprinting 4 `FAIL  BUG-1290 …` lines as success at exit 0.
- Q17 (harness defect): "the tree must be clean" is unsatisfiable for an agent writing its own
  artifact — only `runs/**` is gitignored. Scope such clauses to tracked modifications.
- Q12 (harness defect): terminal `yield` exiting 1 with "yield called with null data" on a complete
  fenced block. Seen on qa, the eng lead, two `dev-ops`. Did NOT recur this cycle or the last.
- Q13 (main session): SC-08's step seam closes under `plan.yaml:460-462`'s route text, a narrower
  reading of "symbol" than the digest seam's. Hold a future feature to it? See Q19.
- Q6 (**NARROWED**, harness defect): the append-only digest channel CAN repair a REMOVABLE key (the
  validator slices from the LAST `VERDICT:`), never a MISSING required field or a contradiction.
- Q-B3 / Q4 (harness defect): the digest contract has no home for per-kind suite exits and file
  counts, and the `lead` schema declares no `code_grade`. Avoided again by naming the declared field
  set and carrying `code_grade` in the headline; validated first time both cycles.
- Q9 (pm's R4 restates it): REQ-08's generic-lead archive exemption (`validate-digest.py:1407`) has
  no test able to redden. Does not falsify REQ-08 — present at the pin, behaviour demonstrated — but
  it is the standing regression risk on that requirement.
- Q1 (DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526` interpolates `run_id` and the
  step id as bare strings; the DEC-85 route can spoof the INV-16 audit line. Carried unchanged at
  c11; one of the two items SC-13 asks the operator to read.
- Q2: **CF-3** (`low`) — `abff2a84`, a FEAT-56 station flip, is this branch's root commit, untracked
  by any REQ or D. Accept and record in the ship note.
- Q3: **CF-2** severity CONTESTED — qa `med`, code `info`, c9 lead `low`.
- Q5 (DEC-174): **CF-4** (`low`) — the downgrade branch renders a raw `None` in the omitted-on-update
  edge; disposed by the lead, not by any reviewer, on `validate-digest.py` being byte-identical. The
  second item SC-13 asks the operator to read. Q7: the 3 complete + 2 partial version-predicate
  spellings want one home.
- F-QA-1: `T-05` declares `change_type: logic` against DEC-212's `touches_config_shape`. Untouched by
  this delta, derived `bugfix`. F-104C10-01/02 (info) stay dismissed non-gating, as at c10.
- Residual non-gating risks, in the c9/c10/c11 panel digests: the DEC-85 Bash-write bypass; F2's
  runtime residual (DECLINED stands, `check-state.sh` topology unchanged); the `_no_parser` bootstrap
  early return; schema guards argued fail-closed rather than mutation-proven; the stale comment at
  `check-domain.sh:1646-1647`, now describing half the loop (ui `low`). Standing: the INV-26
  card/plan mismatch and the per-persona worktree-claim guard.
