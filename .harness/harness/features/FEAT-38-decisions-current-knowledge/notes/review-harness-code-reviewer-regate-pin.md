# Regate-pin targeted delta review — panel-code

**PASS, all four files.** No must_fix. One reported arithmetic figure in the dispatch contract is
FALSE (details below); one pre-existing, non-blocking gate gap in `--check-kinds` is worth a backlog
line; the DECISIONS.md fold introduces no new ruling.

## Per-file verdicts

1. **`.harness/harness.json` `test_kinds.integration` — PASS.** Branch(`4c192ab`) had 29 detect
   entries (glob-inclusive), main(`6d6d1cea`) had 26, and `main - branch = ∅` (main is a strict
   subset). Union = 29. Final(`37676244`) = 27 = union minus exactly `test-context-watch-cli.py` and
   `test-context-watch-hook.py` (the two files FEAT-44 deleted). `test-check-decision-anchors.py`
   (FEAT-38's own addition, absent from main) correctly survived. No registration that should have
   survived was dropped; no phantom entry was resurrected. **Only `unit`/`integration`/etc. `detect`
   arrays were touched — every other `test_kinds` key is byte-identical branch vs final.**
2. **`.claude/skills/harness/bin/run-unit-tests.sh` — PASS.** `UNIT_SCRIPTS`: branch=27, dropped
   `test-context-watch.py` correctly → final=26. `INTEGRATION_SCRIPTS`: branch=28, main=25 (⊆
   branch), union=28, minus the same two deleted files → final=26. At the final pin, `harness.json`'s
   declared integration set is set-equal to `INTEGRATION_SCRIPTS` in **both** directions (verified in
   Python) — no phantom entries either way today.
3. **`.harness/harness/docs/DECISIONS-INDEX.md` — PASS, strongly.** I ran
   `gen-decisions-index.py --stdout` against the committed `DECISIONS.md` at the pin and it produced
   output **byte-identical** to the committed index. This proves regeneration, not hand-merge, and —
   because the generator copies hand-written ruling text verbatim — proves no ruling text was lost
   *anywhere in the file*, a stronger result than checking the three folded rows alone.
   `git diff 6d6d1cea..79e2639 -- DECISIONS-INDEX.md` is empty, confirming FEAT-44's own tail commits
   touched nothing here; the wider `b0ea27d..6d6d1cea` window only shifts anchor line numbers and adds
   `am.1` tags to the three later-amended rows — zero ruling-clause (right of `::`) changes.
4. **`.harness/harness/docs/DECISIONS.md` fold (DEC-159/198/201) — PASS.** `git diff 141eca6..37676244`
   touches only two hunks clusters, at DEC-159 (~3716–3746) and DEC-198/DEC-201 (~5600–5943) — the
   fold is exactly these three entries, nothing else.

## Grading the prior read-back's judgement (not re-measuring it)

The read-back (`notes/review-harness-code-reviewer-readback-fold.md`,
`notes/readback-fold-merge.md`) checked **old-content survival** exhaustively and well; I did not
repeat that. I instead mined the **added** text for anything with no antecedent anywhere in
`141eca6`'s `DECISIONS.md` (whitespace-normalized substring search) — the question the read-back's
method structurally cannot answer: did the fold *decide* something new. Two forward-looking clauses
are genuinely new text: DEC-159's "and none is to be proposed again" and DEC-201's "recorded here so
it cannot be re-proposed as new." Both are direct applications of DEC-205's own stated convention
("A claim the tree has falsified survives as one clause of that current truth, so it cannot be
re-proposed as new") — not novel policy. DEC-201's closing sentence, "A claim that was right and
became inapplicable is not a claim that was refuted," is also new prose, but it is exactly the
nuance-preservation SC-11 required (the read-back itself calls this "the single most likely thing to
have been lost") — synthesis in service of a stated acceptance criterion, not a new operational rule.
**The read-back's PASS holds, corroborated by a different method.**

## The reported "28 -> 27" figure is FALSE

The dispatch's contract states the `test_kinds.integration` resolution was "Reported 28 -> 27." No
single consistent counting method produces that pair. Glob-inclusive (as the field is actually
written): 29 → 27 (drop of 2, matching the two deleted files exactly). Script-only, excluding the
`tests/integration/**` glob entry (as `run-unit-tests.sh`'s array is naturally counted): 28 → 26. The
reported figure mixes a script-only "before" (28) with a glob-inclusive "after" (27), understating the
real drop (2 files, not 1). The *final state* is correct either way — I verified it three independent
ways above — but the number as reported would mislead anyone auditing "did exactly the intended files
drop."

## Advisory, non-blocking: `--check-kinds` is one-directional

Read `run-unit-tests.sh`'s KINDCHECK block directly (not run): it asserts every `INTEGRATION_SCRIPTS`
name is declared in `harness.json`, and no `UNIT_SCRIPTS` name is declared there — array → declared,
one direction only. It never asserts the reverse (declared ⊆ union of the two arrays). A future merge
that resurrects a `harness.json` entry for a deleted test file, without also adding it to either bash
array, would sail through `--check-kinds` clean; the drift detector only flags files-on-disk missing
from the arrays, not array-absent-but-declared entries. This is pre-existing script logic, untouched
by this diff, and today's state has no such phantom entry (verified above) — so it does not gate this
review, but it is exactly the failure class this fold was designed to avoid, and the safety net for it
is thinner than the contract implies. Recommend a backlog line, not a re-open of this fold.

## Non-goals honored

Did not re-grade the other 15 rewritten `DECISIONS.md` entries, the plan, the brief, SC-11's read-back
measurement (only its judgement), or any file outside the four in scope.
