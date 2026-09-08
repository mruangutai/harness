# SIMPLIFICATION angle — BUG-1290 B-3 fixture diff (test-factory-claim.py)

**BLUF: no findings. The diff adds no unnecessary complexity — declined after inspection, nothing to backlog either.**

## Commands run

```
git -C <worktree> diff -- tests/unit/test-factory-claim.py
git -C <worktree> diff --unified=0 -- tests/unit/test-factory-claim.py | grep -nE "^\+\+\+|^@@|^\+"
sed -n '335,340p;1179,1183p' tests/unit/test-factory-claim.py | grep -nE "now|no longer| was |previously|used to"
python3 tests/unit/test-factory-claim.py
```

## Lines read

- `:324-398` — `build_features_root()` full body, including the rewritten docstring (335-340)
  and both fixture blocks (kaya_seg 375-378, harness_seg 380-383).
- `:1163-1233` — cases 5a, 5b, 5c in full, including the rewritten 5b comment (1179-1183) and
  the `check(name_5b, ...)` expression (1202-1206).
- `git diff --unified=0` — confirms exactly which lines this diff touches, to separate
  in-scope additions from pre-existing, untouched code.

## Findings (five-part, each labeled)

None reach the bar for a finding. Three specific things were checked and declined; recorded so
the next reader doesn't re-check them cold.

1. **Redundant conjuncts in case 5b's `check()` — declined, out of scope.** `git diff
   --unified=0` shows the `check(name_5b, code == 0 and json.loads(out).get("issue") == 952
   and "951" in err and "unresolvable blocker" in err and "no plan could be read" not in err,
   ...)` expression (test-factory-claim.py:1202-1206) is byte-identical before and after this
   diff — the only change inside the 5b try-block is the added `rec.issue_data[954] = ...`
   line (1200). The dispatch scope is this diff; a conjunct never touched by it isn't
   "added complexity" this diff introduces. Read on its own merits anyway: each conjunct
   checks a distinct fact — verdict code, which issue won, which issue got named as the
   blocker, which reason string fired, and which reason string did *not* fire — none restates
   another. No apply, no backlog.

2. **Comments narrating the change vs. stating the present fact — declined, both pass.**
   Checked the rewritten `build_features_root()` docstring (:335-340) and the case 5b comment
   (:1179-1183) against changelog language (`now`, `no longer`, `was`, `previously`, `used to`)
   with a literal grep over just those spans — zero matches. Both read as present-tense
   statements of what the fixture *is* ("kaya-ai's T-77 depends on an unresolvable T-88... harness's
   T-77 depends on T-99 which its OWN map resolves to a closed issue"), not as a record of what
   changed. No apply, no backlog.

3. **A construct with a simpler equivalent (collapsing the two `write_json`/`write_yaml` pairs
   for kaya_seg and harness_seg into one parameterized helper) — declined, per the batch
   context's own trap.** The two blocks (:375-378, :380-383) look near-identical in shape but
   differ in exactly the two places that make case 5b discriminate: the dep id (`T-88` vs.
   `T-99`) and the issue map contents (`{"T-77": 850}` vs. `{"T-99": 954}`). Collapsing them
   into one parameterized call would not preserve that anchoring without carrying both
   differences as explicit parameters — at which point it is not simpler, just indirected. This
   was not attempted (I did not write the helper or run the mutant probes it would require);
   it is recorded here as a construct considered and rejected on inspection, not as a backlog
   row, since no version of it clears the bar of "simpler while anchoring-preserving."

## Verification

`python3 tests/unit/test-factory-claim.py` from the worktree: `124/124 checks passed` (matches
the batch's measured baseline; I made no edits, so this is a repeat of the already-established
fact, not new evidence of anything).

## Scope discipline

Did not touch `tests/unit/test-factory-claim.py` or any other file. Did not run mutant probes
(not needed — no candidate finding depended on one). Stayed inside the diff plus the immediate
surrounding context needed to judge each of the three items above.
