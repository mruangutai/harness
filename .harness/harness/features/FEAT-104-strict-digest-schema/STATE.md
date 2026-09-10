# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- phase: **ship — the CEO briefing is written and the feature is with the operator.**
- status: **awaiting_user (ship decision).** The goal is MET IN FULL at the pin `984bd26b`: 9/9 REQs
  and **15/15 live criteria**, SC-14 struck. **SC-13 is CLOSED — the operator returned `passed`**
  (`notes/uat.md`, U-01 against `review_sha: 984bd26b`), so the goal-check's one `pending-operator`
  row is now met. `cycles_used` stays **10 of 10**; no lead ran this cycle, so `feature.json` needed
  no write and `runs:` stays at 28.
- briefing: `notes/ship-review-ship-c11.md` (+ `.html`, rendered by `bin/render-brief.py`, never
  hand-authored). Assembled from disk with **no report round spawned** (DEC-69); every one of the
  29 digest files across all 28 runs was opened, none unreadable, and the digest paths read in full
  are named in the briefing's own disclosure section.
- **29 proposed backlog rows, B-1..B-29**, one per surviving non-gating residual — every item in
  the Open Questions list below has a row, so nothing dies silently on ship acceptance. Two items
  need the operator's name: **CF-3** (`abff2a84`, the FEAT-56 station flip that is this branch's
  root commit — recommendation ACCEPT and record) and the strike list itself.
- Gates at the pin: `qa_gate` **PASS** (blocking; unit 36 / integration 70, both exit 0, focused
  13/13), panel **PASS** `must_fix: []` `severity_max: med` (advisory under
  `gates.review: advisory_unless_high`), `code_grade: pass` 42 functions, SIMPLIFY applied none,
  goal-check **PASS**, `uat` **PASS**. `merge` is user-gated and untouched.

**Measured myself this cycle, not adopted.** `git diff --stat 984bd26b..HEAD -- . ':!.harness'` is
EMPTY — the two commits past the pin (`4907a81b`, `6d28b350`) touch only this feature's records, so
the pin still reviews the shipping code; `git status --porcelain` clean; 47 commits on
`origin/main..HEAD`, code delta 18 files +3203/-19. `validate-digest.py lead` over all 29 digest
files: **28 valid, 1 invalid** — and that **corrects Q6's record**: the unrepairable digest is
`runs/2026-09-09-08-simplify-eng/digest.md` ("VERDICT is PASS but a member returned FAIL"),
superseded by `-09`. Run `-06`, which the c9-era digests named, **validates today.**

**Budget disclosure, in the briefing where a human sees it.** `cycles_used` 10/10 is EXHAUSTED but
was never crossed (the last three runs returned zero send-backs), and **no fix cycle remains or is
needed** — every surviving item routes to the operator or the backlog, none to a squad, because
DEC-174 makes all four surfaces operator-owned. `len(runs)` **28 of an informational 20 — CROSSED**
(INV-22 notices, never stops). My read: three qa/panel/goal-check cycles at three pins each closed a
specific contested defect with measured evidence and earned their place; **six runs were tooling
overhead** (`od5-c3`/`od5b-c3`, `paneltranscribe-c1`/`c1b`, `-08`/`-09-simplify`) whose causes are
rows B-21, B-26 and B-28.

**Nothing was merged, pushed, PR'd, synced or removed.** `pr: null`, the mirror still reads `review`
(parent 1584, sub-issues 1585-1593, milestone 65), `plan.yaml status: review`, the worktree stands.
Those are main-session acts and the ship instruction comes back down before any of them.

## Open Questions

Every entry below is now also a briefing backlog row; the `B-N` id is what the operator strikes by.

- Q20 (**B-5**, not blocking, pm's R1 — recommendation, not an unmet criterion):
  `test-check-state.py:51-54` asserts run/step/key but no declaration route, though
  `check-state.sh:1526-1528` emits one. Outside SC-08's subject. One-line hardening inside the
  DEC-174 carve-out at the next main-session touch, or backlog?
- Q14 (**B-2**, not blocking, main session, DEC-174 — **CONTESTED**): a type/range failure on a
  **declared** step key (`cycles: not-an-int`) routes via `_path[0]` into `_offending` and prints
  under `undeclared step key or evidence shape.`, whose remedy tells the author to move the key under
  `evidence`. ui `med`, qa `low`, code `low`, **lead `med` on mechanism**: an author who FOLLOWS the
  remedy produces `evidence: {cycles: "3"}`, ACCEPTED at exit 0 while the step-level field the retry
  accounting reads goes silently absent. Reachable today, untested, one branch inside the carve-out.
- Q15 (**B-7**, not blocking, main session — `info`, present-tense unreachable): the branch keys on
  the validator NAME (`required`), not the structural cause (empty `error.path`). A future step-level
  `minProperties`/`dependentRequired` would fill neither bucket and emit no denial. Schema census
  (me plus four reviewers) confirms no such keyword at the pin; no test can redden until one exists.
- Q18 (**B-8**, not blocking, security-reviewer, info/latent): `_missing_required` keys on
  `_error.validator == "required"` with **no path check**, so a NESTED required violation (a future
  `evidence` sub-object) would report as a missing STEP key. Fail-closed but mislabelled;
  unreachable today; distinct from Q15. Gate on `error.path == []` when nested `required` arrives?
- Q19 (**B-9**, not blocking; pm's R2 restates it): SC-08's step seam is pinned by the INVOCATION
  path, not string uniqueness — `undeclared step key` has two producers (`check-domain.sh:1671`,
  `check-state.sh:1526`). Safe today because the test fires a Write hook. Hold a future test
  asserting that phrase against combined or at-rest output to a producer-unique string?
- Q11 (**B-25**, RECURRED, persona-level pattern, harness defect): `harness-code-reviewer`'s
  `mktemp -d` probe was refused by `bash-write-guard` for the SECOND consecutive cycle (writing only
  `/tmp`) while qa and ui executed live probes. It reported the refusal rather than working around
  it — guard working, reviewer correct. Guarantee read-only panels a scratch-write route?
- Q16 (**B-22**, harness defect, verified by me): a `^FAIL ` census over `run-unit-tests.sh` is
  defeated by `test-factory-claim-mutation.py` reprinting 4 `FAIL  BUG-1290 …` lines at exit 0.
- Q17 (**B-23**, harness defect): "the tree must be clean" is unsatisfiable for an agent writing its
  own artifact — only `runs/**` is gitignored. Scope such clauses to tracked modifications.
- Q12 (**B-24**, harness defect): terminal `yield` exiting 1 with "yield called with null data" on a
  complete fenced block. Seen on qa, the eng lead, two `dev-ops`. Did NOT recur in the last two.
- Q13 (**B-14**, main session): SC-08's step seam closes under `plan.yaml:460-462`'s route text, a
  narrower reading of "symbol" than the digest seam's. Hold a future feature to it? See Q19.
- Q6 (**B-21**, NARROWED and **corrected by measurement this cycle**, harness defect): the
  append-only digest channel CAN repair a REMOVABLE key (the validator slices from the LAST
  `VERDICT:`), never a MISSING required field or a contradiction. The one digest that remains invalid
  is `-08`'s, not `-06`'s; `-09` supersedes it.
- Q-B3 / Q4 (**B-26**, harness defect): the digest contract has no home for per-kind suite exits and
  file counts, and the `lead` schema declares no `code_grade`. Avoided again by naming the declared
  field set and carrying `code_grade` in the headline; validated first time all three cycles.
- Q9 (**B-6**, pm's R4 restates it): REQ-08's generic-lead archive exemption
  (`validate-digest.py:1407`) has no test able to redden. Does not falsify REQ-08 — present at the
  pin, behaviour demonstrated — but it is the standing regression risk on that requirement.
- Q1 (**B-1**, DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526` interpolates
  `run_id` and the step id as bare strings; the DEC-85 route can spoof the INV-16 audit line. Carried
  unchanged at c11; one of the two items the operator's UAT read, and it passed with it disclosed.
- Q2 (**operator decision at ship, plus B-29**): **CF-3** (`low`) — `abff2a84`, a FEAT-56 station
  flip, is this branch's root commit, untracked by any REQ or D and invisible to `code-grade.py`'s
  merge-base range. Recommendation in the briefing: ACCEPT and record.
- Q3 (**B-4**): **CF-2** severity CONTESTED — qa `med`, code `info`, c9 lead `low`.
- Q5 (**B-3**, DEC-174): **CF-4** (`low`) — the downgrade branch renders a raw `None` in the
  omitted-on-update edge; disposed by the lead, not by any reviewer, on `validate-digest.py` being
  byte-identical. Q7 (**B-11**): the 3 complete + 2 partial version-predicate spellings want one home.
- F-QA-1 (**B-19**): `T-05` declares `change_type: logic` against DEC-212's `touches_config_shape`.
  Untouched by this delta, derived `bugfix`. F-104C10-01 (**B-13**) / F-104C10-02 (**B-14**) stay
  dismissed non-gating, as at c10.
- Residual non-gating risks, in the c9/c10/c11 panel digests, all now rows: the DEC-85 Bash-write
  bypass (**B-18**); F2's runtime residual (**B-15**, DECLINED stands); the `_no_parser` bootstrap
  early return (**B-17**); schema guards argued fail-closed rather than mutation-proven (**B-16**);
  T-06's missing omitted-`schema_version` case (**B-20**); the stale comment at
  `check-domain.sh:1646-1647` (**B-12**); SIMPLIFY-SC08-01 (**B-10**). Standing: the INV-26
  card/plan mismatch (**B-27**) and the per-persona worktree-claim guard (**B-28**).
