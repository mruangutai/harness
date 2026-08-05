# pm Expertise distillation — record of judgment

## BLUF

**5 entries admitted, 2 candidates rejected, 0 displacements.** All three lead-relayed candidates
survived judgment and were rephrased as rules; two of my own three observations were admitted, the
third rejected as already covered by the rule layer. No section was at cap, so nothing was displaced.
`check-expertise.sh` exits 0 — run from the worktree AND from main (the two copies are byte-identical,
`diff` exit 0), so the green is not a stale-validator artifact.

Counts: Patterns 10 → 14 · Gotchas 7 → 8 · Outcomes 0 → 0 · Open 0 → 0. File 64 → 78 lines of 150.

## Admitted, and why each earns a permanent slot

| New | Source | The action it changes |
|---|---|---|
| P-11 | C-1 | State a criterion's observable outcome, not the mechanism behind it |
| P-12 | C-2 | Enumerate the data for an unshadowed instance before asserting "only via X" |
| P-13 | C-3 | Count verification *techniques*, not clauses; force one behavioural leg |
| P-14 | my observation log | Probe the input condition the brief did NOT name |
| G-08 | my observation log | Register a new test file in the same task that adds it |

**P-11 is not the swap test restated.** The brief and spec-driven rules apply the swap test to
requirements only. The durable content here is the consequence on the *criterion* side: a criterion
that is false only in its mechanism is graded approved-but-unmet, which routes as a fix cycle against
code that already behaves correctly — never as a re-signature of the wording. That consequence clause
is what makes the entry non-redundant, and it is why I did not trim it for the word cap.

**P-11 is distinct from P-08**, the nearest neighbour. P-08 is a task's `verify:` contradicting its
own intent prose — both halves authored by me, self-inconsistent. P-11 is a self-consistent criterion
disagreeing with the implementation. Different detector, different fix.

**P-12 is distinct from P-07.** P-07 reads a presupposition against *sibling criteria*. P-12 reads it
against the *manifest data*, which no amount of cross-reading criteria will surface — only enumerating
the data does. The stronger empirical result the lead supplied (every mid-pattern grant in the manifest
is shadowed by a prefix-shaped one; a live resolve returns two agents where a prefix implementation
would grant six) is what promotes this from "check your premises" to a rule with a concrete probe.

**P-13 survives P-04 by construction.** P-04 counts clauses against fixtures; here those counts balance
(four and four) and the hole is still open, because three of the four fixtures read source and a source
read is respellable. Per the skill I kept the rule and dropped both incident cases — an entry citing
more than one incident is a distillation smell.

**P-14 is phrased around the probe, not around distrust.** "Brief framing is untrustworthy" is already
the illustrative entry in the preloaded skill text and would earn nothing. The action is specific:
probe the opposite input condition, because the named half is the half someone already noticed and the
unnamed half is the one that fails open.

**G-08 is new and unrelated to the "G-08" named in my dispatch.** The dispatch's near-neighbour
citation for C-1 was "your G-08"; my file has no G-08 — the entry it describes is **P-08**. G-08 is
the next free Gotcha id and carries the registration-list rule. Anyone reconciling the dispatch against
this record should read the dispatch's "G-08" as P-08.

## Rejected, with the reason on the record

**REJECT — the `execution_mode` synonym observation** (three spellings in the tree before this plan
pinned two). The rule it would produce is "define your vocabulary before a checker reads it," which the
spec-driven rule layer already owns in its glossary section — challenge drift, sharpen fuzz, code wins.
It also fires only when a plan invents a new declared field, which is rare enough to fail the
six-spawns test. It stays in the observations log, where it is free.

**REJECT — sharpening P-10 with the propagation consequence** (the lead disclosed this as filtered at
its tier and offered me the overrule; I decline). The stale anchor is P-10 violated, not P-10
insufficient. Adding "and a wrong anchor is copied verbatim into shipped source" raises the stakes in
the rationale but leaves the *action* identical: anchor on content strings, never line numbers. An op
that does not change what I do next time spends budget on a story. P-10 stands unchanged.

## What I did not do

No re-run of the goal-check. No source, BRIEF, PLAN or `feature.yaml` change. No amendment drafted for
the unmet criterion — its three remedies are the user's choice and are not yet made. The filed issue
from the validation panel was not reopened. `cycles_used: 0`.

## Open questions

None. Nothing here needs a ruling; the two rejections are mine to make and are recorded above.
