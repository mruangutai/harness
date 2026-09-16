# Parity amend — eight of nine DIFFERENT rows closed, one recorded known-open

**BLUF.** The plan now closes **8 of the 9 DIFFERENT rows** in
`notes/research-BUG-285-parity-survey.md`; the 9th (wrong-typed members) is recorded in BRIEF Risk
as known-open with its reason and is a separate ticket. Four rows closed by amending **T-02 only** —
one guard pair, one function, no new task. The ABSENT path is unchanged and now pinned by two named
checks (SC-16). Every cascade the closure contradicted is reconciled: D-08 superseded by **D-14**,
D-06 rewritten, SC-06/SC-11/SC-14/SC-15 amended, SC-16 and REQ-12 added, T-03/T-04/T-05 intents
amended. **No mandated docstring anywhere claims convergence.** Operator's section A held on every
claim; nothing overturned.

## Every DIFFERENT row, with its disposition

|row|verdict|incident|disposition|
|---|---|---|---|
|file empty (0 bytes)|DIFFERENT|YES|**CLOSED** by T-02's JSON parse (`json.loads("")` raises). Pinned SC-07, SC-14|
|non-UTF-8 bytes|DIFFERENT|no|**CLOSED** by T-04 (read guard gains `UnicodeDecodeError`). REQ-09, SC-12, SC-13|
|top-level list|DIFFERENT|YES|**CLOSED** by amended T-02 item 5a. REQ-12, SC-06, T-03 check 5, T-05 input 8|
|top-level scalar string|DIFFERENT|YES|**CLOSED**, same guard. T-03 check 6|
|top-level scalar int|DIFFERENT|YES|**CLOSED**, same guard. T-03 check 7|
|block key present, not a mapping|DIFFERENT|YES|**CLOSED** by amended T-02 item 5b (the SPLIT). T-03 check 8, T-05 input 9|
|duplicate block keys|DIFFERENT|no|**CLOSED** by T-02's JSON parse — both now accept, last wins. Pinned as T-05 input 10, the only row in the other direction|
|YAML-only block mapping|DIFFERENT|no|**CLOSED** by T-02. SC-07, SC-14 input 6|
|block mapping, wrong-typed members|DIFFERENT|YES|**KNOWN-OPEN.** BRIEF Risk, D-14, T-05 comment. Separate ticket|

Post-T-02 verdicts for the three rows the operator asked me to state: **empty file → SAME (both
refuse)**, **duplicate keys → SAME (both accept, last wins)**, **YAML-only → SAME (both refuse)**.
All three verified by running the mandated guard shape against a patched COPY (below).

## Section A — the operator's reading, checked at source

- **non-UTF-8 / survey Q1: the operator is right, the survey is wrong.** `BRIEF REQ-09` names this
  exact defect ("refused by `load_recorded` … never raised as a traceback"), SC-12 asserts the
  `refuse` verdict with no class name leak, SC-13 pins the read guard, T-04 edit 1 makes it so.
  **Q1 is retired**, not carried up.
- **Q2 (duplicate keys) is also retired**: it is no longer merely disclosed — T-05 input 10 pins it,
  in the one direction the earlier six-input set did not cover.
- **empty file needs no further amendment.** Confirmed.
- **The four rows close with one guard pair in one function.** Confirmed, and the shape is not
  invented: `load_recorded` already carries it — `"github" not in doc` returns the default
  (`gh-sync.py:583-586`), present-non-mapping refuses (`:588-594`), non-mapping document refuses
  (`:578`). T-02 converges `load_factory` onto it.
- **The split is load-bearing, measured:** all **80** `feature.json` files under
  `.harness/*/features/*/` in this worktree have the `factory` key **ABSENT**. Collapsing the split
  into a single refusal would refuse every live feature.
- **Caller survey, confirmed as read:** one call site, `factory_decompose.py:515` in `_main()`; a
  refusal there exits before `ensure_labels` (`:538`, the declared point of no return) with zero
  remote writes; no test depends on tolerance. Stop condition did not fire.
- **Nothing overturned.**

## The ABSENT path — how it is provably unchanged

- `factory_decompose.py:114-115`, the `os.path.exists` early return, is the line that still hands
  back the empty record for an absent file. **No amended instruction touches it** — T-02's edits are
  confined to the `try` at `:120-123` and the two guards at `:124-128`.
- The new risk is not that line but the *second* absent case: a present mapping with no `factory`
  key. That is why item 5b is a membership test (`"factory" not in doc`) rather than a
  `.get()`-plus-isinstance — `.get()` cannot distinguish a recorded `null` from an absent key.
- **What reddens if a future edit breaks it:** SC-16, via two named checks in T-03 (empty directory,
  and a mapping whose `factory` key is absent), each asserting the return is EQUAL to
  `_empty_factory()`; plus T-05 inputs 2 and 3 with SC-14's clause D; plus the last two cases of
  T-02's own `verify:` block, which exit 1 if either turns into a refusal.

## Satisfiability — the mandated code was run, not just written

Throwaway probe on a **COPY** in a tempdir (`/tmp/bug285-amend/prove_t02.py`, deleted tree-side
nothing): the exact guard pair T-02 now mandates, applied to a copy of `factory_decompose.py`, run
over 12 inputs → **ALL GREEN, exit 0**. Five refusals for the newly-closed rows, two empty records
for the absent rows, duplicate key accepted last-wins (`repo: c/d`), and every refusal's stderr
names the path while containing no `unexpected failure`, `Traceback` or exception class name.
Pre-change baseline of T-02's own verify block on the real tree: **5 FAIL, 2 ok, exit 1** (yaml-only
→ populated; the four others → empty), so the task's red-then-green is measured, not asserted.

## What was amended

- **Plan (via `plan-merge.py` only).** New: **D-14** (closure + supersession of D-08), **D-15**
  (where the new assertions land). Amended: D-08 `choice`/`because` (marked superseded, history
  preserved), D-06 `because` (enumeration replaces the two-surviving-classes claim), T-02
  `title`/`traces`/`intent`/`verify`, T-03 `title`/`traces`/`intent` (checks 5–10), T-04 `intent`
  (docstring item 3 now mandates an ENUMERATION and forbids any convergence claim), T-05
  `traces`/`intent` (input set 6 → 10, one excluded row).
- **BRIEF.** Problem now cites the 13-class table; **REQ-12** added; Risk rewritten as the
  disposition of all nine rows; SC-06 extended to both new refusals and the membership test; SC-11
  bent to T-03's two named checks; SC-14 spans the table at ten inputs in both directions; SC-15
  mandates an enumerated statement citing the survey note; **SC-16** added for the absent path; two
  Verification-gaps entries corrected/added.
- **Untouched:** `approval:` (sha256 `6f59dc09…` identical), `lanes:` (identical), `panel:`
  (identical), `feature.json`, `tests/`, `bin/`, skills.

## Verification as measured

1. `harness_yaml.load_plan(plan.yaml)` → **LOADED**, 5 tasks, 15 decisions.
2. Every `files:` entry: T-01/T-02/T-04 exist on disk; `tests/unit/test-factory-decompose-loader.py`
   (T-03) and `tests/unit/test-feature-json-readers.py` (T-05) are absent and are created by their
   own task.
3. `check-plan-routes.py <plan>` from `/Users/molchairuangutai/GitHub/harness` → **exit 0, "0
   violation(s) across 1 plan(s)"**, all five tasks OK. The team-config-skew MANIFEST deviation the
   dispatch warned about **did not reproduce** today at this invocation.
4. All 12 `plan-merge.py` invocations returned `ADDED`/`AMENDED` + `APPLIED`. **No exit 7.**

## Open questions

- **Q4 (non-blocking, for the operator):** the wrong-typed-members row needs a ticket, and the
  policy question it carries is *refuse or silently drop a wrongly-typed member in a POPULATED
  record*. Not decidable inside this feature's constraints.
- **Q5 (non-blocking):** BRIEF's earlier "77 `feature.json` in this worktree" was stale — the same
  glob measures **80** today (owner root still 79). Corrected in Risk with both invocations named.
