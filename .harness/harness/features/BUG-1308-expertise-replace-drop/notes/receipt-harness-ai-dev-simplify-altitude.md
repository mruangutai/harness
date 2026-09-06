# SIMPLIFY — ALTITUDE angle — BUG-1308

BLUF: the replace/drop capability sits at the right home and its core resolution logic is not
bolted on anywhere I could find. Two real gaps exist — one drift-detector blind spot (SPEC.md is
untested against code, unlike the distill skill) and one message-shape asymmetry at the merge
refusal — both are conservative `briefing-row`s, nothing rises to `apply-now`. Three sites I
checked are correctly placed and are recorded below as considered `leave`s per the acceptance
contract.

## Findings

**F1 — home of `ops` subcommand — `leave`**
File/line: `.claude/skills/harness/bin/expertise-merge.py:484-533` (`cmd_ops`) vs.
`harness_merge.py:1-26` (module docstring: "NO identity source", generic RMW library used by
other write routes outside this feature).
Summary: replace/drop lives as a sibling subcommand to `apply` in `expertise-merge.py`.
Cost of the alternatives: moving section/id/cap resolution into `harness_merge.py` couples a
domain-agnostic lock/RMW core (shared by other FEAT-32 write routes) to Expertise-only
vocabulary; folding it into `apply` is REQ-07-forbidden and settled (D-01/D-02). Neither
alternative is cheaper or cleaner than the sibling-subcommand home already chosen.
Alternative: none — current placement is correct.

**F2 — op-verb contract has an untested third spelling — `briefing-row`**
File/line: authoritative — `expertise-merge.py:146-167` (`_OP_KEYS`, `_validate_verb`).
Checked, mechanically drift-proofed against — `.agents/skills/harness-distill/SKILL.md`
(`tests/integration/test-expertise-merge.py` case17, `contract_drift`, lines 696-808: harvests
the SKILL.md vocabulary line, probes the real tool, and mutation-demonstrates the detector on
three drifted copies). Checked by nothing — `.harness/harness/docs/SPEC.md:932-971` §5.3 (verb
list, exit-code table, message shapes) has no equivalent probe; case17 never reads this file.
Cost: if `_validate_verb`'s accepted verbs or refusal shapes change, SPEC.md's table can go
stale with nothing to catch it, unlike the distill skill which is actively guarded.
Alternative: SPEC.md is a prose deliverable and not to be restructured (settled) — the fix is a
future case17-style probe added against SPEC.md's table, not a doc rewrite now. Rating: backlog.

**F3 — merge-refusal message shape breaks the uniform MALFORMED-OPS format — `briefing-row`**
File/line: `expertise-merge.py:158-164` (the `op == "merge"` branch in `_validate_verb`), vs.
`:153-154` (`_malformed`, the shared helper every other shape violation routes through).
Summary: every other MALFORMED OPS line is built by `_malformed(index, message)` as
`"MALFORMED OPS op index=<i>: <reason>"` (documented at `SPEC.md:968`); the merge branch raises
`MergeRefusal(12, [...])` directly with a hand-built string that omits `op index=<i>` entirely.
Cost: a consumer parsing every exit-12 line for `index=` to attribute the failing op position
gets nothing for this one path — SPEC.md's documented shape is inexact for exactly this case.
Alternative: route the merge branch through `_malformed(index, "op=merge is not a mechanism
op; express it as a replace on the surviving id plus a drop of the absorbed id.")`. I traced
this against the two tests that touch this text — unit `u7` (asserts the substring "replace on
the surviving id plus a drop of the absorbed id" in `lines[0]`) and integration case17's probe
(regex `unknown op verb|op=merge`) — both substrings would survive the rewrite. I am not
certifying it safe: this exact site is named in the shared context as assertion-strong but not
mutation-proven, so I am not moving it past `briefing-row`.

**F4 — cross-op ambiguity check (`_check_proposal_ambiguity`, :240-251, raised at :246) — `leave`**
Summary: this lives inside `_resolve_all`'s Step C, the one place every op's cross-proposal
ambiguity is checked, on every `ops` invocation — it is core resolution logic, not a special
case bolted onto a call site. The "not mutation-proven" note in the shared context is a
test-coverage gap, not a placement problem; there is nothing for this angle to fold in or move.

**F5 — exit-11 wording contract SPOF (`section=`/`id=`/`reason=` tokens) — `leave`**
File/line: asserted only at `tests/integration/test-expertise-merge.py:542-545` and `:563-566`;
unit tests (`test-expertise-ops.py`) pin only `e.code == 11`. This is a real single point of
failure for the wording contract, but it is correctly *named*, has exactly one authoritative
source (the f-strings in `_resolve_replace_or_drop`/`_check_proposal_ambiguity`) and exactly one
compensating control, and the settled list explicitly forbids touching or collapsing those two
integration ranges. Duplicating the wording assertion into the unit suite would be a defensible
hardening, but that is a QA/efficiency-angle backlog item, not an altitude fold-in — the rule
already lives in one place.

**F6 — distill SKILL.md states, then immediately narrows, its own vocabulary line — `briefing-row`**
File/line: `.agents/skills/harness-distill/SKILL.md:112` ("The vocabulary is exactly `add |
replace | merge | drop`") and the repeated comment at `:118`, versus `:125-126` three lines
later ("`op: merge` is refused by the tool"). Cost: purely reader confusion (case17 proves the
tool itself correctly refuses `merge`, so no behavioural risk) — an author skimming only the
vocabulary line or the YAML comment could expect `op: merge` to run. Docs are a prose
deliverable and not to be restructured now (settled); a later documentor pass could tighten the
phrase to distinguish "authoring vocabulary" from "mechanism-accepted verbs." Rating: backlog.

## Not found
No methodology found living only in a session's prompts rather than a durable home — the
op-verb contract, the exit codes, and the resolution algorithm are all recorded in SPEC.md,
the distill skill, or the code's own docstrings.

## Scope note
Per shared-context settled list: did not propose touching `apply`'s behaviour, did not propose
implementing `op: merge`, did not propose restructuring any of the four prose docs, and did not
propose collapsing the two integration exit-11 wording assertions.
