# Observations — harness-documentor — FEAT-08-remove-cost-tracking

- 2026-08-05 (T-09): `compute_refs` harvests every DEC number in a new entry's BODY into the new
  row's generated `refs:` field. So a verify clause shaped `grep -n 'DEC-NNN' INDEX | grep -c
  <forbidden-token>` also covers the ROW OF THE NEW DECISION, not just the target's row — the new
  decision's hand-written ruling must avoid the forbidden token too. Nearly missed: the instinct is
  to name the deleted script in the ruling of the decision that deletes it.
- 2026-08-05 (T-09): PLAN intent (T-09, B(ii), `PLAN.md:528`) says the DEC-148 ruling must state the
  watchdog was dropped "with `cost-report.py`", while the same task's verify clause 2
  (`PLAN.md:539-540`) requires zero occurrences of the literal `cost-report.py` on any DEC-148 line.
  Resolved by naming "the meter" instead of the filename — the gate is the tie-breaker. Raised as Q10.
- 2026-08-05 (T-09): the safe write order for a new decision is: append the entry at EOF of
  `DECISIONS.md` (keeps every existing `@line` anchor stable), edit the target's hand-written ruling
  in the index, run `gen-decisions-index.py` with NO flag to rewrite the file in place, then replace
  the single `⚠ RULING PENDING` sentinel it emitted. Hand-constructing the generated left side of a
  new row is never necessary.
- 2026-08-05 (T-09): `check-state.sh:331-335` already carried a forward reference to DEC-178 (written
  by T-02) before the entry existed. Appending the entry closed the dangling reference; nothing in
  the toolchain would have flagged it if the entry had never been written.
- 2026-08-05 (T-09): rule of thumb that kept `BODY_SUPERSESSION_RE` quiet — open every bold run in a
  decision body with a NOUN. `**DEC-148 is only PARTIALLY superseded here.**` is safe (the regex
  needs the verb immediately after `**`); `**Supersedes DEC-148**` or `**Corrects DEC-134**` would
  have stamped a false `— SUPERSEDED BY` clause on another decision's row.
- 2026-08-05 (T-10): third instance of the PLAN defect shape "intent mandates prose containing a
  token the same task's `verify:` counts" (after T-01 intent 2 and T-02 intent h,
  `feature.yaml:99-102`). Here intent said retitle to "**The cycle budget has teeth (DEC-157)**"
  while verify required `grep -c -e max_total_cycles -e 'DEC-157'` unchanged. Resolved by keeping
  the existing `(DEC-134)` attribution in the title: DEC-134 is not marked superseded
  (`DECISIONS-INDEX.md:154`), DEC-178 already `refs: DEC-134`, and the DEC-157 attribution survives
  verbatim in the kept body half. Count stayed 8. Raised as Q14.
- 2026-08-05 (T-10): a "keep half a paragraph verbatim" instruction is also a WRAPPING instruction
  when a `grep -c` clause guards it. Preserving the original line breaks of lines 1715-1718 kept the
  two token-bearing physical lines intact; a re-flow of identical prose would have moved the count.
- 2026-08-05 (T-10): `check-docs.sh` was run PRE-edit and was already green with `bin/cost-report.py`
  live in SPEC — so DEC-178 declares no superseded pattern matching the deleted meter's name. That
  is what makes D-07's mandated `(removed — DEC-178)` marker safe to keep (cf. G-03).
- 2026-08-05 (T-10): a plain-word sweep (`grep -in -e cost -e spend -e usd -e '\$[0-9]'`) found TWO
  live cost sites in SPEC that the disposition table's nine rows do not cover, because every verify
  clause in this feature counts COMPOUND tokens (`cost_usd`, `cost-report`, `max_cost`, `INV-11`) and
  none of them can see prose that just says "cost". Left unedited — out of mandate — and raised as
  Q15/Q16:
  - `SPEC.md:1448-1449`, the §10.3 worked CEO-briefing example, still renders a `Cost $12.83 of the
    $50 budget…` row. Site `:1422` (mandated) deleted the cost line from the briefing STEP prose 25
    lines above it, so the doc's own example now shows a section the doc no longer says to produce.
  - `SPEC.md:1574`, "Same shape as cost (DEC-116)" — an analogy to a mechanism this feature deleted.
- 2026-08-05 (T-10): §11.5 was read in full (`:1744-1768`); no property there names cost, so the
  disposition's closing "change no §11.5 property that does not name cost" required no edit at all.
- 2026-08-05 (T-10): §15.5's `See BUILD.md § "Build the org; monitor cost in practice."` is a
  cross-file anchor T-11 may invalidate. Left untouched — out of T-10's domain.
- 2026-08-05 (T-11): fourth instance of the PLAN defect shape "intent's site model conflicts with the
  same task's grep-counted verify". Intent said `:578` gets "one appended sentence"; verify required
  every `cost-report` PHYSICAL line to carry `DEC-178`, and `:578` is mid-paragraph, so a sentence
  appended at the paragraph's end (`:582`) would have left `:578` failing. Resolved with an inline
  `(removed — DEC-178)` ON `:578` plus the reason sentence appended. Raised as Q18.
- 2026-08-05 (T-11): the appended sentence had to avoid BOTH `DEC-114` (a `grep -c` unchanged clause,
  counted lines) and `cost-report` (a new wrapped line would itself need `DEC-178`). Wrote "the
  meter" — the same evasion T-09 used. Two independent token traps on one appended sentence.
- 2026-08-05 (T-11): SC-01's five tokens are not all present in BUILD.md. Only `cost-report` (5 lines)
  and `INV-11` (2 lines, `:191` and `:333`) hit; `cost_usd`, `max_cost`, `per_feature_usd` are absent
  from the file entirely. Both `INV-11` hits survive by D-07 mandate and now also carry `DEC-178`.
- 2026-08-05 (T-12): my T-10 reasoning on the `(DEC-134)` title was wrong in a way the gate could not
  show me. I argued the attribution was mine to keep because `grep -c` held at 8 either way. A silent
  gate does not license departing from an attribution an approved PLAN mandated — that is a decision,
  and decisions are approval-gated. The substantive tell I never checked: DEC-134's ruling
  (`DECISIONS-INDEX.md:154`) opens "The cost budget is informational…", so its first clause describes
  the mechanism this feature deletes; DEC-157 (`:177`) is the actual authority for a claim about
  `max_total_cycles`. Corrected to `(DEC-157)` in T-12; count held at 8, as predicted, because grep
  counts physical lines and `:1711` already bore `max_total_cycles`.
- 2026-08-05 (T-12): "not marked superseded" is too weak a test for whether a DEC is the right
  attribution. A decision can be live while the HALF of it a title leans on is dead. Read the ruling's
  clauses, not just its supersession status.
- 2026-08-05 (T-12): `.harness/README.md:86` was genuinely stale, not merely cost-flavoured — it said
  `check-state.sh` flags "runs completed without a cost block", but `check-state.sh:329-335` now keeps
  `"cost"` only as a HISTORICAL-ONLY tolerated key ("nothing produces it any more", DEC-178). The doc
  described a check with inverted polarity to the code. Deleting the clause was right; a removal
  marker would have preserved a false statement.
- 2026-08-05 (T-12): the sole `max_total_cycles` bearer in `.harness/README.md` was line `:26` — one
  of the four lines the task edits, and the row whose `, cost` item was being deleted. When an
  "unchanged count" clause guards a file, check whether the bearing line IS an edit site and re-count
  immediately after that specific edit rather than at the end.
- 2026-08-05 (T-11): answers T-10's Q17 — `BUILD.md:545` "## Build the org; monitor cost in practice"
  (the `SPEC.md:2130` cross-file anchor) is outside T-11's five sites and is unchanged. But it is a
  plain-word `cost` site invisible to every compound-token sweep in this feature, same shape as
  Q15/Q16. Reported, not renamed.
