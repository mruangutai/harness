# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- runs: `2026-09-10-15-qa-gate-validator` (**PASS**, `harness-validator-lead`) and
  `2026-09-10-16-simplify-eng` (**PASS**, `harness-eng-lead`), dispatched concurrently, both
  strictly read-only, both over the re-pinned `review_sha` `984bd26b`
- status: validate — **Q10 is CLOSED: PF-C10-01 is fixed and both build-side gates are green over
  the fix.** The main session applied the remedy at `984bd26b` (DEC-174 holds — no agent edited it);
  this cycle re-gated and read it. No panel, goal-check, UAT, briefing or merge this cycle. Owed
  before ship: the SC-13 UAT and the CEO briefing. **`cycles_used` is 10 of 10 — the budget is
  EXHAUSTED; no further rework cycle is available.**

**The fix.** `check-domain.sh` `shape_problems`, three hunks inside lines 1647-1685: `required`
errors on a dict instance divert into a new `_missing_required` set (`validator_value` minus the keys
present), and the one unconditional message becomes two conditional ones — `missing required step
key.` naming `missing key(s)`, and the unchanged `undeclared step key or evidence shape.` naming
`offending key(s)`. Plus one integration case (+6/-0). `git diff 790023f0 984bd26b --stat -- .
':!.harness'` lists no third code file.

**I re-ran the suites MYSELF** rather than accepting the gate's report: `--kind unit` **exit 0, 36
files**, `--kind integration` **exit 0, 70 files** — exactly the `790023f0`/`168f875f` baseline, so
discovery did not collapse — and focused `tests/integration/test-check-domain.py` **13/13 exit 0**,
up from the 12/13 RED witness at the old pin. The unit suite's 4 `^FAIL ` lines are
`test-factory-claim-mutation.py` reprinting its own mutant output between `MUTANT ACTIVE` and
`MUTATION PROOF` at exit 0 (lines 989-999): a defect in the census heuristic, not the suite (Q16).

**The one regression the fix could have introduced is CLOSED by enumeration, not by the happy path.**
Before `984bd26b` a non-empty `_schema_errors` always denied even with an empty key list; after it
both messages are conditional, so an error populating NEITHER set would ACCEPT a write the old code
refused. Both segments answered independently and agree: only `type`, `additionalProperties` and
`required` sit at the step object's own level and can report an empty `error.path`, since every error
beneath a named property carries that property as `path[0]`. Whole-step `type` is caught by
`_offending.add("<step>")` and `additionalProperties` by `set(_step) - _declared`, **both outside the
`if _schema_errors:` block**, so conditionalising the messages cannot suppress them; `required` is the
fix itself and cannot come back empty. eng enumerated 15 rows with 0 fall-throughs; qa exercised
`required`, `additionalProperties`, `propertyNames`, `oneOf` and both `type` shapes live. **No
version-2 step shape reaches a jsonschema error and emits no message.**

**Mixed violations fire BOTH diagnostics** — qa's probe under a disposable fixture root: `status`
omitted AND `rogue_step_key` present → exit 2, stderr carrying `missing key(s): 'status'` AND
`offending key(s): 'rogue_step_key'`. A non-mapping step is still refused. Red capability of the new
case stays REASONED (DEC-174 forbids the mutation): no other branch satisfies the assertion
conjunction — the `except Exception` route emits a different head — and the 12/13 witness is the
empirical half.

**Simplify found nothing gating and I did not let it invent one.** Four angles PASS across five
readers: reuse says leave the two message blocks (the sentences differ materially); simplification
says the structure is right, with one stale comment at 1646-1647 now describing half the loop;
efficiency is at the noise floor; altitude says the fix removes one INSTANCE of the empty-path class,
not the class. **The apply step was cancelled by my dispatch** under DEC-174 — every recommendation is
described, none applied. `must_fix` empty on both sides.

**Tree verified at my own tier.** `git diff --stat HEAD` over the three carve-out paths is EMPTY —
byte-identical to HEAD. `git status --porcelain` carries only untracked feature-tree notes and
receipts, each attributed to a named member of these two runs; zero tracked modifications. Both
digests validate at exit 0 under their own persona.

**Cycle accounting, stated rather than rounded** (DEC-157): 9 → **10**, from the ONE send-back the
validator lead reported inside its run (a member misread `--stat`'s graph column as `+34/-8`;
`--numstat` confirmed `+26/-8`). The eng lead reported zero. The main session's fix is a
main-session-direct act, not a run, and adds no cycle. `len(runs)` is 26 of 20, informational only
(#79); these two earned their place — they moved the pin onto the fix and closed the accept-shape
question by enumeration. **The pin MOVED and that was the point**: a run at `790023f0` would have
reviewed a tree the fix is absent from. The plan's `status:` stays `review` and its
`approval.status` stays `approved`; I wrote neither.

## Open Questions

- Q14 (not blocking, main session, DEC-174 — **new; PF-C10-01's own sibling**): the false head
  SURVIVES on the route `984bd26b` did not touch. A type/range failure on a **declared** step key
  (`cycles: not-an-int`, `id: 123`) routes via `_path[0]` into `_offending` and prints under
  `undeclared step key or evidence shape.`, whose remedy tells the author to move the key under
  `evidence` — wrong advice for a declared key. Reachable today; denial still correct and the key
  named truthfully, which is why both segments declined to gate. Found independently by qa and eng.
- Q15 (not blocking, main session — new): the branch keys on the validator NAME (`required`) rather
  than the structural cause (empty `error.path`). Adding `minProperties`/`dependentRequired` to
  `run-state-schema.json` later would emit NO denial line. Latent — no test can redden until then.
- Q16 (not blocking, harness defect — new, verified by me): a `^FAIL ` census over
  `run-unit-tests.sh` output is defeated by `test-factory-claim-mutation.py`, which reprints 4
  `FAIL  BUG-1290 …` lines as success output at exit 0. A gate reading it literally calls green red.
- Q17 (not blocking, harness defect — new): "the tree must be clean" is unsatisfiable for an agent
  writing its own artifact — only `runs/**` is gitignored, `notes/` is tracked. Scope such clauses to
  tracked modifications.
- Q12 (not blocking, harness defect — **RECURRED and widened**): terminal `yield` exiting 1 with
  "yield called with null data" while the fenced block and on-disk artifact are complete. First seen
  on `harness-qa`; this cycle it hit the **eng lead** and two `dev-ops` members. I accepted the eng
  lead's return on its digest validating at exit 0 on disk rather than re-dispatching.
- Q11 (not blocking, harness defect): panel falsification capability is ASYMMETRIC — a write guard
  refused one reviewer's /tmp copy while another ran a live repro. Both segments probed under
  disposable fixture roots this cycle without incident.
- Q13 (not blocking, main session): SC-08's STEP seam closes under `plan.yaml:460-462`'s route text,
  a narrower reading of "symbol" than the digest seam's. Hold a future feature to it?
- Q6 (**NARROWED**, harness defect): the append-only digest channel CAN repair a REMOVABLE key — used
  again this cycle by the eng lead to add a missing `adequacy_notes`, since the validator slices from
  the LAST `VERDICT:` anchor. It cannot repair a MISSING required field or a verdict CONTRADICTION.
- Q-B3 / Q4 (not blocking, harness defect): the digest contract still has no home for per-kind suite
  exits and file counts, and the `lead` schema declares no `code_grade`. Avoided again by naming the
  declared field set in both dispatches; both validated first time.
- Q9 (not blocking): REQ-08's generic-lead archive exemption (`validate-digest.py:1407`) has no test
  able to redden. Does not falsify REQ-08.
- Q1 (not blocking, DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526` interpolates
  `run_id` and the step id as bare strings; the DEC-85 route can spoof the INV-16 audit line.
- Q2 (not blocking): **CF-3** (`low`) — `abff2a84`, a FEAT-56 station flip, is this branch's root
  commit and merges with this PR, untracked by any REQ or D. Accept and record in the ship note.
- Q3 (not blocking): **CF-2** severity CONTESTED — qa `med`, code `info`, lead `low`.
- Q5 (not blocking, DEC-174): **CF-4** (`low`) — the downgrade branch renders a raw `None` in the
  omitted-on-update edge. Q7: the 3 complete + 2 partial version-predicate spellings want one home.
- F-QA-1 (not blocking): `T-05` declares `change_type: logic` against DEC-212's
  `touches_config_shape`. Untouched by this delta, which qa derived as `bugfix` → unit + integration.
- Residual non-gating risks, in the c9/c10 panel digests: the DEC-85 Bash-write bypass; F2's runtime
  residual; the `_no_parser` bootstrap early return; the schema guards argued fail-closed rather than
  mutation-proven; the stale comment at `check-domain.sh:1646-1647`. Standing: the INV-26 card/plan
  mismatch and the per-persona worktree-claim guard.
