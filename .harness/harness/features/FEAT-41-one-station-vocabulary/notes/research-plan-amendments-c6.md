# Cycle 6 plan amendments — FEAT-41

Four scoped amendments applied to `plan.yaml` and `BRIEF.md`. Plan re-parses, `check-plan-routes.py`
exits 0, counts unchanged at 13 tasks / 12 decisions / 12 main-session-direct, both approvals still
`pending`. Nothing committed.

## 1. Ruling 2 — the recording form becomes an open dependency (D-09, T-12)

Scope unchanged: DEC-203 §6, DEC-191 and DEC-182 each still carry one contradicted clause, and the
three "STRUCK: … What holds instead: …" paragraphs keep their content verbatim. Only the FORM moved
from decided to pending, naming both candidates — (a) in-place strike under DEC-188, live twice at
`DECISIONS.md:3228` and `:4436`; (b) subsuming the correction into the entry in one voice — with
T-12 instructed to read what the separate decisions-authority triage landed at execution time, and
to STOP and return the question if it has not landed.

Form-(a) mechanics are now under an explicit `IF THE FORM IS (a), AND ONLY THEN` header: the
do-not-rewrite rule, the reproduce-the-live-form paragraph, and the two-part shape (renumbered
`(a1)`/`(a2)` so the labels no longer collide with the form letters), including amendment numbering.
A short `IF THE FORM IS (b)` paragraph says the strike sentence, amendment section and numbering do
not apply.

Two phrases inside the clause paragraphs were neutralised because they presumed form (a) —
"say that in the amendment" → "say that in whatever you write", "Note in the amendment that" →
"Note in what you write that". No recorded content changed.

D-09's `because:` keeps the falsified-record argument as an ARGUMENT for form (a), adds the
operator's reading behind form (b) (STRUCK does not today mean deleted; eight entries sit in
DECISIONS.md marked STRUCK), and states why the form is pending rather than chosen here.

**YAML trap hit and fixed:** `": "` inside a plain scalar terminates it. Four colons I introduced in
D-09's `because:` broke `safe_load` at line 83 col 411; all four became `" - "`. Plain scalars in
`plan.yaml` cannot carry `": "` at all.

## 2. F-1 (HIGH, gating) — T-09's plan.yaml denial

The message now states the reason first (one writer, `plan-write.py`, because every station value is
validated before it lands) and then the four verbs and tool path. A new bullet forbids `deny()`,
citing `check-domain.sh:1063-1066` (its last line appends the ROUTING constant at `:879`, which
speaks about STATE.md/digests/notes) and the existing comment at `:1161-1167`, and names
`out.append(...)` as the route to use. Two test assertions added: the denial contains the reason
clause, and does NOT contain ROUTING text. SC-05 amended to require both clauses; method and
evidence unchanged.

## 3. F-2 (med) — T-08's sign-approval refusal

Refusal text must name `sign-approval` literally rather than "the verb". Test list gains the
substring assertion (exit code alone is no longer the assertion). SC-07 amended to require both the
refused verb and the sanctioned route.

## 4. Ruling 6 — T-10's board pass adds nothing

The add-the-missing-card bullet inverted: skip, add nothing, print one line per skip. The exemption
and its reasoning (a migration moves cards, it does not create them) are stated in the task text.
Three consequences carried through: the cost sentence now reads zero stations / zero cards / one
skip; the expected-red sentence says the gap does NOT close here and is carried as PB-03; the
`verify:` splits projected names into `compared` and `skipped`, asserts non-empty on both `placed`
and `compared` so it cannot pass by having read nothing, and prints the skipped list.

Open, honestly unverified: whether `check-state.sh` INV-26 flags issue 223 after T-06 routes the
compare through `project`. 223 is a parent card, not a task sub-issue, and INV-26's per-task compare
walks recorded sub-issues — so it should be outside the set. T-10's text now says STOP and report if
a run reports it, rather than adding the card to buy the gate green.

## 5. Ruling 7 — PB-02, plus PB-03

PB-02 records FEAT-28's abandoned-but-Done card. PB-03 records the absent parent card for FEAT-12
(my call under ruling 6's "a backlog row is the instrument"). No task planned for either.
