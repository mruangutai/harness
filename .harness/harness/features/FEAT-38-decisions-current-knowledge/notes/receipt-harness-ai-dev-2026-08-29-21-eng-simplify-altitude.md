# Receipt — harness-ai-dev — FEAT-38 simplify pass, ALTITUDE angle — 2026-08-29-21

Read-only review of `plan.yaml:1733-2091` (T-24..T-29) and the amended `BRIEF.md`. No writes made.
Verdict: PASS (advisory findings only; nothing here must change before signature).

## Q1/Q2 — per task (HOW-vs-WHAT pins, and invented-content risk)

**T-24** (deregister runner side). Pins: "remove the single string ... from INTEGRATION_SCRIPTS"
(WHAT/target, load-bearing), "leave anchors checker in place" (WHAT/safety, load-bearing), "do NOT
delete the checker here" (WHAT/scope boundary, load-bearing). The long ordering-rationale block
(1758–1770) explains WHY, not HOW to edit — not a HOW pin. No invented content required (Q2: clean).
**Altitude is right.**

**T-25** (deregister config side). "Remove the literal path... it's a single pipe-separated string,
not a list; don't convert to a list, don't reorder" — WHAT/format-preservation, load-bearing (a
plausible wrong move — converting to an array — is foreclosed). Ordering rationale (1821–1825)
again WHY not HOW, duplicates T-24's (see Q3 below). No invented content (Q2: clean).
**Altitude is right.**

**T-26** (delete checker+test). "Delete both files with **git rm**, not with a plain rm" (line 1856)
is a genuine HOW pin: the verify (1848–1849) only checks the *outcome* (untracked + absent from
disk), which `rm` + `git add -u` would satisfy equally. Decoration, not load-bearing — harmless,
but is the one clear instance in this batch of over-specifying implementation where the acceptance
already fully covers it (**ALT-2**, `leave`). Everything else in T-26's intent (anchors-checker
do-not-touch, dependency ordering, the unscoped sweep) is WHAT/scope, load-bearing. No invented
content (Q2: clean) — it authors nothing.

**T-27** (delete 11 markers). "delete the blank line ... only where that would otherwise produce two
consecutive blank lines" is a WHAT-level output constraint (unverified by the verify block, but
low-risk cosmetic). "Find them with grep -n rather than by line number" is a HOW pin, but explicitly
load-bearing (other tasks move this file). No invented content — pure deletion, nothing authored.
**Altitude is right.**

**T-28** (repair DEC-205 + regenerate). The four "literal wording" edits are the crux the dispatch
flagged. Verdict: **right to pin exact wording here — this is not decoration.** DECISIONS.md prose
is the signed deliverable itself; letting a builder free-paraphrase the heading/enumeration sentence
would be authoring uncleared decision-document content (exactly the Q2 risk), which "ADD NO POSITIVE
GUIDANCE" (1996–2000) is the explicit compensating control against. So specifying the exact resulting
text is WHAT (what the document must say), not HOW-to-edit, given the domain. One real asymmetry
found: edits 2 and 3 (heading, enumeration sentence) give the full literal replacement sentence;
edit 4 (closing paragraph, 1989–1994) only says "rewrite it to speak of the one check above and the
one that is in" — a paraphrase instruction, not a literal sentence, unlike its siblings. Low risk in
practice since the original sentence is quoted in full and the fix is a mechanical two→one
substitution, so no real invention is required — but it is an inconsistency in how tightly the four
edits are specified (**ALT-3**, `leave`).

**T-29** (bin/ argv audit). The enumeration command, the two-question filter rubric, and the table
shape are all WHAT/reproducibility pins, load-bearing (explicitly: "so two readers reach the same
verdict", "so verify can match it"). The prescribed *order* of the note's sections (2072: "in this
order: command, count, table...") is not checked by verify and is a mild, harmless format pin
(decoration). Q2: the note's content is empirical audit judgment, not policy — no operator-approval
gap. **Altitude is right.**

## Q3 — restated rules that can drift

**check-decision-anchors.py retained / not-in-risk-class claim** appears independently in BRIEF
(107–111), T-24 (1754), T-25 (1814), T-26 (1866–1871) — four authorings of one fact (fixed literal
argv, `check-decision-anchors.py:111`). All four are consistent today. Real but low-severity drift
risk: if that checker is ever touched by later work, all four citations need synchronized updates
and nothing forces that (**ALT-1**, `briefing-row`).

**Drift-check ordering rule** (asymmetry of `run-unit-tests.sh`'s KIND-DRIFT check) is independently
re-derived in T-24 (1758–1770, ~12 lines) and T-25 (1821–1825, ~5 lines) rather than stated once and
referenced. Bounded risk: these are one-time migration task intents that become historical the
moment T-24/T-25 land, unlike a living document rule — so drift exposure is short-lived. Not folded
in as a blocking finding, noted for completeness only (`leave`).

## Q4 — residuals and their compensating controls

Semantic-citation-rot loss: **not a finding** per the dispatch's own carve-out — and BRIEF does name
its (deliberately weak) control explicitly: "the detector for it is a human reading a diff" (Goal,
and again in "What removal costs", 130–134). Satisfied.

One residual the BRIEF does **not** name a control for: **T-29's audit may surface a non-empty
TEXT-DERIVED-ARGV set**, and its own intent (2079–2081) explicitly permits that set to be "listed as
remaining work with a recommendation" rather than closed. But REQ-10 is worded as an unconditional
class claim ("No script under `.claude/skills/harness/bin/` builds a command line from text..."),
with only a soft hedge ("it holds only once the rest of `bin/` has been swept and the sweep's result
is on the record"). Neither REQ-10 nor T-29 states what happens if the sweep is not clean — no
follow-up ticket number, no restated scope, no explicit statement that REQ-10 is satisfied by
recording the sweep rather than by a zero count. Today's expected residual is empty (BRIEF line 117:
"the only instance known today"), but the plan does not commit to what closes the gap if it is not
(**ALT-4**, `briefing-row`).

## Q5 — capability in the caller vs. the module

T-26's verify carries an unscoped whole-tree `git grep` blast-radius sweep (1852–1853), and its
intent (1877–1894) already argues at length for keeping it unscoped rather than task-scoped — a
deliberate, already-litigated call, not an oversight. But the plan does not close the loop: that
exact assertion — "no tracked file outside the three frozen pathspecs matches
`check-decision-claims`" — **is already SC-14** (BRIEF 282–289), and T-26's own intent even
name-drops SC-14 by id (line 1863: "SC-14 grades..."). Yet T-26's `traces:` is `[REQ-10]` only —
SC-14 is not listed. The plan already has the right convention for exactly this case: T-29 traces
`[REQ-10, SC-17]` specifically "because this note IS that criterion's entire evidence, and the
grader looks for the id here" (2090). T-26 is in the identical position for SC-14 and does not
follow its own precedent. The same gap recurs for T-28/SC-16: SC-16 (`verify: inspection`, like
SC-17) grades exactly the four edits T-28 performs (T-28's own intent even cites it: line 1978,
"SC-16 grades rule 1 as unchanged"), but T-28's `traces:` is `[REQ-05, REQ-10]` — SC-16 absent.
Both are cheap, mechanical additions, not redesigns (**ALT-5** and **ALT-6**, `fold-in`).

## Findings summary

| id | task/lines | severity | recommendation |
|---|---|---|---|
| ALT-1 | check-decision-anchors claim x4 (BRIEF:107-111, plan.yaml:1754,1814,1866-1871) | low | briefing-row |
| ALT-2 | T-26, plan.yaml:1856 ("git rm, not plain rm") | low | leave |
| ALT-3 | T-28, plan.yaml:1989-1994 (edit 4 under-pinned vs. edits 2-3) | low | leave |
| ALT-4 | REQ-10 / T-29, BRIEF:179-182, plan.yaml:2079-2081 (residual audit outcome, no named control) | medium | briefing-row |
| ALT-5 | T-26 traces, plan.yaml:1835 vs. 1863 (SC-14 self-cited, not traced) | medium | fold-in |
| ALT-6 | T-28 traces, plan.yaml:1952 vs. 1978 (SC-16 self-cited, not traced) | medium | fold-in |
