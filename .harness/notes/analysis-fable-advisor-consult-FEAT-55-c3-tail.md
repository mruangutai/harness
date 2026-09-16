# Advisor consult (tail) — FEAT-55 — N3, N4, N6 and the cross-cutting ruling-order question

**Persona: `fable-advisor` — the same external reader that served as the cycle-3 plan panel's
`should-not-exist` step and answered the first consult. It RESOLVED. It was not skipped, preflight
did not refuse it, and no substitute answered.** Read-only, no write grant; this note is the
validator lead's transcription of its return
(`agent://FinalizeIssueTypesPlan.AdvisorConsultTail.AdvisorC3Tail`, transcript
`history://FinalizeIssueTypesPlan.AdvisorConsultTail.AdvisorC3Tail`).

**Nothing in this note resolves, accepts or waives anything, and no severity is reassigned.** Every
item is a recommendation to the operator, who alone rules (DEC-176). No plan edit was made.
This note does not supersede `analysis-fable-advisor-consult-FEAT-55-c3.md`; it is additive.

**Advisor headline.** *All three premises HOLD. N4 is the one worth acting on before signature — a
config schema is a one-way door and its remedy SHRINKS the spec; N3 is a free rider on any edit
batch; N6 needs no ruling at all, only reading before F1 is ruled.*

---

## Anchor drift — read this before checking any citation

After the panel ran, pm transcribed the panel record into `plan.yaml`'s `panel:` key, inserting
~77 lines at `:159`. **Every anchor in the panel findings text pointing past `:159` is stale by
exactly +77.** Re-measured by the lead and used throughout below:

| what | stale | current |
|---|---|---|
| D-12 | `:91-93` | `:91-94` — unchanged, precedes the insertion |
| T-01 assertion 5 | `:322-326` | `:398-403` |
| T-02 `overrides_from_config` | `:415-417` | `:492-495` |
| T-03 verify loop / case F | `:470` / `:532-539` | `:547-549` / `:609-616` |
| T-05 case G | `:785-796` | `:862-873` |
| T-07 `traces:` / case I | `:869` / `:969-984` | **`:946-952`** / `:1046-1057` |
| T-08 `traces:` | `:988` | `:1065` |

The advisor corrected one of the lead's own re-measurements: T-07's `traces:` list spans
`:946-952`, not `:946-949`. Verified — six entries at `:947-952`.

---

## N3 — `PF-3626edafbb21d2afb151ff470a450714` (scope, `low` — that reader's value, verbatim)

**Premise verdict: HOLDS, and sharper than the panel text.** Independently re-derived twice — by
the advisor and by the lead before dispatch:

- T-07 `traces:` (`:946-952`) and T-08 `traces:` (`:1065`) omit `REQ-10`; T-03 (`:535`) and T-04
  (`:653`) carry it.
- T-07 case F (`:1020-1028`) **cites REQ-10 by name in its own prose**; case H (`:1035-1045`) and
  T-08 §8 (`:1147-1159`) implement the adopted/absent-provenance exemption. This is an omission,
  not a deliberate scoping judgement.
- BRIEF SC-12 (`BRIEF.md:166-175`) calls itself "REQ-10's only falsifiable grading" and runs it on
  both routes.

**Advisor's addition, verified by the lead: `traces:` is not inert metadata.** No mechanical gate
consumes it (`check-plan-routes.py:350` is a line budget), and the panel's own orphan-REQ hunt does
**not** go red because REQ-10 stays traced by T-03/T-04 — so nothing will ever catch this. But
`gh-sync.py:359-367` joins `traces` and publishes it **verbatim into the GitHub issue body**
(`factory_decompose.py` likewise). The gap therefore reaches a human-visible surface.

**Recommendation — fix now, but conditionally.** Append `REQ-10` at `:946-952` and `:1065`. Cost is
two tokens, and the advisor recommends it *solely because* F1's remedy already reopens `plan.yaml`.
**Absent any other edit, `accept` is defensible at scope's `low`.** Honest caveat the advisor
volunteered: nothing mechanical goes red — this binds the audit record and the published issue
bodies, not a gate.

**Consequence of accepting instead.** The next REQ-10 audit that walks `traces:` — a future panel
cycle, a goal-check assessor, or a human reading the mirrored factory issues — concludes the factory
route is ungraded, and spends a cycle re-deriving what SC-12 already names, or orders redundant
cases. No runtime effect. Reversible. Discovered at the next audit.

---

## N4 — `PF-595ce69d5574361d12a048900fcf3e0f` (should-not-exist — the advisor's OWN finding, `low`)

**The advisor KEPT its own `low`** and upgraded only the recommendation, on one-way-door grounds.
It was told plainly that withdrawing its own claim was a first-class answer; it declined, and said
why.

**Premise verdict: HOLDS, both halves.**
- REQ-03 (`BRIEF.md:34-37`) enumerates four roles and a four-key role map discharges every word of
  it; D-12 (`:91-94`) ships sixteen keys.
- The silent split is real: resolution falls through (D-12 `:92`, T-02 `:482-485`) and refusal fires
  only via `missing_types` over resolved **names** (T-02 `:525-526`, T-04 §4 `:612-614`, T-08 §6
  `:1055-1056`). Renaming Task coherently needs twelve keys; miss one while the repository declares
  both names and there is no refusal and no diagnostic — one role split across two native types.

**On the expressiveness fact the lead handed it as a fact, not a judgement:** the advisor re-derived
it (T-01 assertion 5 `:400-401` pins `feature`→`Story` alone, which a role-keyed map cannot express)
and **judged it incidental** — not something REQ-03 asks for, and anti-aligned with D-18's own
`because` (`:118`, splitting "destroys exactly that dimension"). It found the only defence to be
D-02 `:52` inertia.

**Verified sharpening the panel did not record.** D-12's phrase "the **EXISTING** key
`github.issue_types`" is inaccurate. Lead-verified: `.harness/harness.json` has a `github` block
(`:357`) but **no `issue_types` key at all**, and D-16 (`:107-110`) keeps it out of the shipped
template. There is **no installed base until ship** — which is precisely what makes the remedy cheap
now and a breaking config migration later.

**Recommendation — fix now.** Re-key D-12 to four role keys (`bug`, `feature`, `task`, `parent`).
The remedy *shrinks* spec text. Mechanical edits named: D-12 `:91-94` (and correct "EXISTING key");
D-02 `:52` final clause deletes; T-01 assertions 5–6 `:398-408` rewritten; T-02 `:479-497` resolvers
read the role key; T-03 case E fixture `:605-608` → `{"bug":"Defect","parent":"Epic"}`; T-07 case D
fixture `:1006-1012` → `{"bug":"Story","parent":"Story"}` (assertions unchanged in both).
**Zero required-string-loop edits** — lead spot-checked: `IT_defect`/`IT_epic` (`:547`) and
`IT_story` (`:964`) all still produced by the rewritten fixtures. What reddens: the split config
becomes unrepresentable, and the new T-01 assertion fails any per-`change_type` implementation that
today's assertion 5 *requires*.

**Lead note, not the advisor's:** this remedy edits **signed decisions D-12 and D-02**. It is an
approval-gated decision change and is the operator's alone — it is not a fix any squad may dispatch.

**Consequence of accepting instead.** The sixteen-key surface ships and T-01 pins it permanently;
`github.issue_types` becomes a published contract on first use. The failure fires in exactly the
canonical Bug/Feature/Task views this feature exists to establish: a later partial rename splits one
role silently. Discovered by a human reading a board, arbitrarily later. Repair costs completing the
config **and hand-retyping**, because the backfill never touches `typed: True` (T-04 §7, T-08 §8).
Narrowing the surface post-ship is a breaking config migration, against a two-fixture rename today.

---

## N6 — `PF-e74a2da89380cfa94f6b1693191d759d` (should-not-exist `info` — the advisor's own, kept; scope `med` — untouched, verbatim; transcribed `med`)

**Premise verdict: HOLDS — and uniformly across all three gates.** The advisor's material addition:
this is **one property of the `grep -qF` idiom, not a T-03 defect**. T-03 `:547-549` (`partial`
satisfied by the fake's spec `:567-568`, `github.issue_types` by case E `:605-606`, neither binding
case F's refusal wording `:611-612`); T-05 `:801-803`; T-07 `:964-966`.

**Recommendation — accept. There is NOTHING here for the operator to RULE; the note has already
done its job by being written down.** The advisor verified rather than asserted:
`PF-8b5853…`'s own disposition said "gate uniformity, not coverage"; scope's note says the operator
was not misled; the c3 digest kept N6 out of `fix_order`; **neither reader proposed a remedy**, and
none is worth building — a case-scoped grep is unordered machinery, and the real protection for case
F is behavioural, i.e. F1's remedy.

**Operator action: read N6 once, immediately BEFORE ruling F1. Then nothing.**

**Consequence.** None adverse. The written finding *is* the guard against a future reader mistaking
edit 2 for coverage. The only way to waste it is to rule F1 without it in view.

---

## Q-tail — conflicts and must-rule-together pairs across the full set of twelve

**Conflicts: NONE.** The advisor checked every remedy pair: no two edit the same lines, no remedy
deletes text another edits, N4 disturbs no required-string token, and even F1-per-panel and N4
rewrite different cases of the same files.

**Must rule together / read together, and ordering:**

| pair or group | relation |
|---|---|
| `PF-56a2ce7a053111a3aff62a4b97c5902e` + `PF-0c12a033f69bb6bc60b8f96134f94fd0` | **rule together** — unchanged from the first consult |
| **F1 + N6** | **read together**; N6 needs no ruling. N6 proves marker and string-loop edits buy parity, not coverage — ruling F1 toward the panel's add-cases remedy without it in view repeats cycle-5 edit 1's exact failure shape |
| **N4 before, or with, F1's edit batch** | both reopen T-03/T-07 case text; separate rulings edit and re-read the same files twice |
| batch-formers **F1, N4, N2, `PF-1286544c197d1b0eb4a9b0dc8e1234dc`** before batch-contingents **`PF-452948136bf467869d223e027191ae49`** ("fix if any batch is ordered") and **N5(b)** ("nearly free if the F1 fix is ordered") | the contingents' recommendation is a function of whether a batch exists |
| **N3** | rides any batch free |

**Otherwise clean: eleven of the twelve can be ruled in any order without producing an inconsistent
set.**

## Changes to earlier answers

**None.** Nothing here alters any first-consult recommendation. The ordering rows above only restate
conditionality already stated there.

---

**Still open, for the operator alone:** N3, N4 and N6's dispositions, alongside F1, N2, N5 and the
six carried `PF-` ids. Nothing above moves any of them.
