# Simplification angle — BUG-1290 B-27 diff (fb9a4ac4)

**BLUF: no applyable findings.** The three anchors this diff fights for (`_emit_5b` indirection,
the narrative comments, the compound conjuncts) all earn their place. One backlog-only row is
noted per the dispatch's own rule (conjunct redundancy may never be an apply post-qa-PASS). Both
suites re-run green/expected: `test-factory-claim.py` 125/125; mutation suite prints `MUTATION
PROOF: 3/3 cases reddened` and `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`.

## Q1 — `_emit_5b(record)` (test-factory-claim.py:1226)

**Leave it.** Judgement: earns itself. Inlining at both call sites (:1237 `_emit_5b(check)`,
:1338 `_emit_5b(_capture)`) would duplicate the pairing of `_run_5b_scenario()` +
`_5b_property_holds(...)` + the fixed `name_5b` key across two try-blocks — exactly the
lockstep-drift risk this pass' own REUSE angle exists to flag, just self-inflicted instead of
against an external helper. More importantly it is the mechanism that makes the diff's central
claim true: 5g reruns case 5b's *own* verdict-producing path, not a parallel rebuild of it. A
second, textually-similar-but-drifted copy at :1338 would silently undermine exactly the property
the commit message states as its purpose. No cost found — it is two lines wrapping a stable pair
of calls, called from two sites, with a name that states what it returns nothing and reports
through `record`.

## Q2 — new docstrings/comments: present-fact vs. narration

Mixed, and correctly so:
- `_emit_5b` docstring (test-factory-claim.py:1227-1230): present fact. States what the function
  does and why `record` is polymorphic. No cycle history. Fine as-is.
- 5g's block comment (test-factory-claim.py:1307-1318): mostly present fact — describes the
  *current* mutant, the *current* required observable (952 present, "unresolvable blocker",
  not "no plan could be read"). It does carry one clause of rationale ("must carry the SPECIFIC
  observable... not merely any falsy shape a differently-broken mutant... could also produce")
  that reads like it is arguing against a past-wrong version. **Judgement: load-bearing, not
  narration-that-dates.** The comment is defending the compound conjunct in the assertion that
  follows it (Q3) — without that sentence, a future reader has no way to know the 4-conjunct
  check isn't accidental over-specification; it's the rationale for exactly the assertion sitting
  three lines below it. It doesn't reference "B-27" or "this cycle" — it survives past this
  feature closing.
- `test-factory-claim-mutation.py` module docstring addition (lines 20-23) and
  `_KeyCollapsingBlockerCache` docstring (lines 159-162) both **do** narrate cycle history
  explicitly: "B-27's lesson was that an unreached mutant 'proving' a red case is fail-open in
  disguise" and "B-27's fail-open lesson is why `_reached` below is asserted, not assumed." These
  name the incident by id. **Judgement: still leave, not an applyable trim.** This is the single
  documented instance of the reached-marker anchor (settled constraint #3) explaining *why* it
  exists at this exact call site — deleting the B-27 reference would leave `_reached` looking like
  incidental instrumentation instead of an anchor. A future reader who strips it and later
  "simplifies away" the guard has no textual signal it's load-bearing. Cost of leaving it: the
  literal string "B-27" ages once the incident id stops meaning anything to new readers — real
  but minor, and the alternative (state the rule with no incident id: "an unreached mutant
  'proving' a red case is fail-open") loses no information the guard needs. **Backlog-only,
  not applyable**: could reword to drop the incident id and keep the rule, but the pass may not
  touch narrative-only prose changes that don't affect assertions, and skill scope here is code
  surface complexity, not prose polish of settled anchors. Noting it, not proposing an apply.
- `_mutate_and_run_key_collapse` / `_key_collapse_proof` docstrings (mutation.py:151-155,
  186-188): present fact, describe current mechanism and current guard. Fine.

## Q3 — redundant conjuncts

- `_key_collapse_proof` (mutation.py:194-200): single conjunct-free check (`line is None` /
  else print+pass). No redundancy.
- 5g's compound `check` condition (test-factory-claim.py:1343-1349): five conjuncts —
  `not mutant_cond`, `mutant_code == 1`, `mutant_out == ""`, `"952" in mutant_err`,
  `"unresolvable blocker" in mutant_err`, `"no plan could be read" not in mutant_err`. **Not
  redundant with each other** — each pins a distinct observable dimension (verdict boolean, exit
  code, stdout emptiness, which issue number, which refusal reason, and explicitly which refusal
  reason it must NOT be, ruling out the sibling `no_plan` path from case 5c). None restates a fact
  another conjunct already establishes; `"952" in mutant_err` and `"no plan could be read" not in
  mutant_err` look adjacent but assert independent facts (identity of the blocked issue vs.
  identity of the refusal reason). **BACKLOG ROW per dispatch instruction, not a finding of
  actual redundancy:** the dispatch requires flagging this class as backlog-only regardless — I
  looked for an actual duplicate conjunct and found none; recording that explicitly so the lead
  doesn't read silence as "didn't check."

## Anchors confirmed, not flagged

`sys.__stdout__` (mutation.py:173), the `finally`-restore of `_BlockerCache` (both files), the
`_reached`/reached-marker guards (both mutant classes) — all present, all load-bearing, none
touched by this angle.

## Suite runs (grounding only, no edits made)

- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` → `125/125 checks passed.`
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py` → `MUTATION PROOF:
  3/3 cases reddened`, `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`, exit 0.

No proposal in this angle would weaken either suite's ability to report RED — none is being made.
