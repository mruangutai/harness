# Receipt — harness-backend-dev — BUG-1290 · simplify · altitude — 2026-09-06

**BLUF:** One real altitude finding worth an apply — the reached-marker discipline is a
methodology re-implemented from scratch per mutant class rather than factored into a shared
helper, and the two existing instances already diverge in shape. Everything else checked
(home of the two operator-directed arms, `_emit_5b` as a seam, the mutant subclass's placement)
is at its right altitude. No proposal below touches either seam's ability to report RED.

Both suites re-run clean and match the expected transcripts: `test-factory-claim.py` →
`125/125 checks passed.`; `test-factory-claim-mutation.py` → `MUTATION PROOF: 3/3 cases
reddened` then `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`.

## 1. Home of the key-collapse proof (5g vs. `_key_collapse_proof`) — leave, plus one sub-finding

Each arm sits where its sibling pattern already sits: 5g lives inside `test-factory-claim.py`
alongside 5c–5f and reuses `_emit_5b`/`_5b_property_holds` (same in-suite shape); the
printed-FAIL arm lives inside `test-factory-claim-mutation.py` alongside `_mutation_proof()`
and reuses `_run_suite`/`_case_line` (same out-of-process shape). Structural placement: **leave**.

Sub-finding — **file** `tests/unit/test-factory-claim-mutation.py:21-25` (module docstring),
`:159-162` (`_KeyCollapsingBlockerCache` docstring), and `tests/unit/test-factory-claim.py:1307-1318`
(5g's header comment). **Summary:** the same mechanism narrative ("collapsing (repo, feature) to
feature-alone routes harness's 952 through kaya's map, refusing it as an unresolvable blocker")
is restated in prose three times across two files. **Cost:** each is free-text, none enforced by
a check; if the specific observable ever changes (e.g. the refusal message), an editor must find
and update all three by hand, and the class-level one — closest to the code — is the one most
likely to get updated while the file-level and 5g-side commentary quietly goes stale. **Alternative:**
keep the full mechanism narrative only in `_KeyCollapsingBlockerCache`'s docstring (closest to
the code it describes) and have the module docstring and 5g's comment each carry one line plus a
named pointer to it, the same way the module docstring already points at 5g by name at line 24.
**Recommendation: leave.** This mirrors the file's own established narrative-heavy-docstring
convention (5g's own comment, the original `_MutantFactoryConfig` docstring) rather than
diverging from it, and the duplication is prose, not an assertion — a stale comment cannot make
either gate report GREEN on a real defect. Noting it, not spending the one apply slot here.

## 2. `_emit_5b` as a seam — leave, earns its keep

Deletion test: removing `_emit_5b` and inlining `_run_5b_scenario()` + a `record(...)` call at
both call sites (the plain `name_5b` block and 5g's mutant block) costs only ~2 duplicated lines
per site — cheap on its face. But the property `_emit_5b`'s docstring names (`tests/unit/test-factory-claim.py:1226-1230`)
is that 5g calls **the same verdict-producing path**, not a hand-copied lookalike. Inlining
creates exactly the drift risk B-27 exists to guard against one level up: an editor changing
`_5b_property_holds` or the scenario builder for the real case could edit only the `name_5b`
block and forget the second copy inside 5g, silently decoupling the mutation-test's fidelity
from the case it claims to defend. Two real call sites, one genuine invariant enforced by
sharing code rather than convention. **Recommendation: leave.**

## 3. Special case bolted onto shared infrastructure — leave

`_KeyCollapsingBlockerCache` (`tests/unit/test-factory-claim-mutation.py:158-181`) subclasses the
real `factory_claim._BlockerCache`, is monkeypatched in and restored in a `finally`, transient for
the duration of one run — same shape as the pre-existing `_MutantFactoryConfig` proxy for
`factory_config`. It lives in the test file that already owns this technique, not bolted onto
`_BlockerCache` itself or onto production. The residual accepted (the mutant might never fire)
has its compensating control named and present: the class-level `_reached` flag, asserted before
the printed line is trusted (`:189-193`). Nothing here patches a symptom the underlying mechanism
should refuse instead — the mechanism (per-repo blocker cache keying) is what's under test.
**Recommendation: leave.**

## 4. Methodology living only in docstrings — the reached-marker discipline itself — fold-in

This is the one worth spending the apply slot on. The "assert-you-were-reached, don't assume it"
discipline (B-27's lesson) is **not** only a docstring convention here — the *mechanism* is
hand-rolled twice, independently, in two different shapes:

- `_MutantFactoryConfig` (`tests/unit/test-factory-claim-mutation.py:61-79`, pre-existing):
  `_reached` is an **instance** attribute set via `object.__setattr__`, exposed through a
  `reached()` **method**, printed guarded by that instance flag.
- `_KeyCollapsingBlockerCache` (`tests/unit/test-factory-claim-mutation.py:158-181`, new this
  cycle): `_reached` is a **class** attribute, read by callers as a bare attribute
  (`_KeyCollapsingBlockerCache._reached`, `:182`), no accessor method.

Two instances, two shapes, already diverged (instance-vs-class attribute, method-call-vs-direct-
read) — exactly the "several statements that can drift" this angle exists to catch, except the
statement is code, not prose, so the drift is silent complexity rather than a comment going
stale. **Cost:** a third mutant (there will be one — this file's whole reason to exist is one
mutant per defect closed) copies whichever of the two shapes its author happens to read first,
with no signal which is canonical; reviewers must hold both idioms in mind to confirm either one
correctly guards against B-27. **Alternative:** factor a tiny shared primitive — e.g. a
`_ReachedMarker` helper (`mark()` / `was_reached()`, or a one-line class both mutants hold an
instance of) — used by both `_MutantFactoryConfig` and `_KeyCollapsingBlockerCache`, so the third
mutant has exactly one idiom to copy. This only touches the *proving* scaffolding, never an
assertion: it cannot weaken either gate's ability to report RED, and it stays entirely inside
`test-factory-claim-mutation.py` (no cross-file edit, no touch to the operator-directed seams'
content). **Recommendation: fold-in.**

## Ranking for the one-fix ceiling

1. **#4 — fold-in the reached-marker primitive.** Concrete, test-file-local, zero risk to either
   gate's RED path, and the divergence is measured (not hypothetical) after only two instances.
2. #1's sub-finding (prose triplication) — recommended `leave`, offered only as a note.
3. #2, #3 — `leave`, both pass their deletion tests / placement checks as designed.

No proposal here reduces either suite's ability to report RED; #4 touches only the
scaffolding that *proves* redness, not the assertions themselves.
