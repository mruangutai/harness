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

## 2026-08-05 — T-10 REOPENED under A-3 · receipt for the two added dispositions (rows 10 and 11)

**Verdict: PASS.** Both A-3 rows landed in `docs/harness/SPEC.md`. All five `verify:` clauses re-run
with output pasted below. Working root `/Users/molchairuangutai/GitHub/harness`, branch
`feat/FEAT-08-remove-cost-tracking`, pre-edit tip `00f3e03`.

### The two edits — identified by content, not line number

- **Site A** (§10.3 worked briefing example): removed the two-line `Cost` row and the single blank
  line following it. Now exactly one blank line between the `Goal check` block and `UAT`. Every
  other row verbatim.
- **Site B** (cycle-counter ownership prose): deleted `Same shape as cost (DEC-116) — ` and
  recapitalised, giving `that. The tier that can see across runs is the tier that bounds them.`
  The line was NOT re-wrapped — reflowing a ~140-char line in cycle territory would be diff noise
  beyond the ruled edit.

### Unchanged-count clause — baseline, captured BEFORE any edit (A-3 ruling: own baseline, current tree)

    $ grep -c -e max_total_cycles -e 'DEC-157' docs/harness/SPEC.md
    8            # PRE-EDIT
    8            # POST-EDIT

Equal, as A-3 predicted — neither disposition touches `max_total_cycles` or `DEC-157`. Matches the
independent cross-check of 8 at `00f3e03`.

### A-3 plain-word sweep — MID-FLIGHT, before the edits. Exactly two lines:

    1448:Cost        $12.83 of the $50 budget (26%), across 9 spawns and 2 fix cycles.
    1574:that. Same shape as cost (DEC-116) — the tier that can see across runs is the tier that bounds them. Exhausting either terminates the loop, and the sequence is:

Not two-plus, not fewer. This pair can never be recaptured and is the only evidence the clause is
discriminating in the failing direction. (The `Most of it — $7.40 —` continuation line carries no
`cost` token, so a two-line defect surfaces as one grep hit.)

### A-3 plain-word sweep — POST-EDIT. Empty:

    $ grep -n -i 'cost' docs/harness/SPEC.md | grep -v -F -e '| Cost |' ... (15 survivors)
    (no output)   exit 1

**Exit 1 with empty stdout IS the pass** — `grep -v` returns 1 when it prints nothing. No hit
surfaced off the allow-list, so the SC-12 / ESCALATE branch stayed dormant; the allow-list was not
touched and no SPEC survivor was deleted.

### Compound-token clause — one hit, and it carries the D-07 marker:

    2126:monitoring: `bin/cost-report.py` (removed — DEC-178) computed per-agent spend, ...

### Whole unit suite:  `SUITE_EXIT=0`, 12 `PASS` lines, zero `FAIL`.
### `check-docs.sh`:  `DOCS_EXIT=0`, "checked 45 superseded pattern(s) across 203 file(s). no stale statements found."

Both were run by me, after the edits and after this receipt was written (the receipt is itself in
`check-docs.sh`'s scan glob — G-04).

### Diff scope — the bound no clause covers

`git diff -U1 docs/harness/SPEC.md` shows **exactly two hunks**, at `@@ -1447,5 +1447,2 @@` and
`@@ -1573,3 +1570,3 @@`. Nothing else moved. This is the only receipt line discharging A-3's
"counter-ownership table and domain-hook paragraph stay verbatim" bound — the absence clauses cannot
see collateral damage and the count clause survives most of it. The table's `cycles_used` /
`max_total_cycles` row was `:1569` pre-edit and is `:1566` now; Site A's three deleted lines shifted
everything below it up by 3 (Site B likewise moved `:1574` → `:1571`), so any anchor quoted from
A-3 or from the mid-flight capture below is one revision behind the current file.

### Observations

- 2026-08-05 (T-10/A-3): the three verify clauses that guard SPEC are all absence-or-count checks.
  None of them can see collateral damage to text that never contained the banned token. On a task
  whose bounds say "these neighbouring lines stay verbatim", the hunk-count diff is the receipt, not
  the greps.
- 2026-08-05 (T-10/A-3): a `grep -v` allow-list sweep passes with exit **1**. A run that treats
  non-zero exit as failure would report a green clause as red.
- 2026-08-05 (T-10/A-3): deleting a mid-sentence clause after a period is a delete PLUS a
  recapitalisation. No absence check catches the orphaned lowercase word — fold both into a single
  `Edit` whose `old_string` spans the sentence boundary.
- 2026-08-05 (T-10/A-3): `BUILD.md:545` ("## Build the org; monitor cost in practice") is ruled by
  A-3 as deliberately preserved — dated historical heading under D-07, plus the target of SPEC's
  cross-file anchor. It answers the Q17 note above; not re-opened, not a finding.
