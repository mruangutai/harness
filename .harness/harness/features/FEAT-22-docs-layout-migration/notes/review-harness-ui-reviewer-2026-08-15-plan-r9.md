# ui-reviewer r9 — FEAT-22 plan.yaml delta re-fire (T-08 four-clause verify)

**Superseded by the send-back addendum below (2026-08-15): verdict revised to FAIL.** The
cycle-1 body immediately following is kept as-written, unedited, per rule 15 — the addendum
records what changed and why, it does not rewrite this section.

**VERDICT: PASS.** The remedy discharges the r8 Q3 coverage gap. It also introduces a narrower,
non-blocking message-accuracy defect in clause 4's failure string, found by the false-FAIL probe the
dispatch asked for.

## Re-measured vs. attested ledger

| Claim | Status |
|---|---|
| `wc -l` = 1306 | **re-measured**, matches |
| `:961-971` byte content (the hunk) | **re-measured** (Read) |
| T-08 id/title/depends_on unmoved (`:951-960`) | **re-measured** |
| T-08 `intent:` `:972-1032` (mandate text) | **re-measured** in full |
| T-09 id `:1034`, T-10 id `:1155`, T-11 id `:1257`, EOF `:1306` | **re-measured**, matches attested ledger exactly |
| `:1065-1071`, `:1073-1076` (r8-cited anchors that moved) | **re-measured**, content consistent with r8's characterization |
| Corrected-figure literal now at `:1015` (was `:1013`) | **re-measured**, confirmed: "the correct figure is ONE of the four" |
| DEC-189 pin content, `docs/harness/DECISIONS.md:5549-5946` at `0f12f14` | **re-measured** via `git show 0f12f14:docs/harness/DECISIONS.md` |
| T-08 is the only task whose `files:` block includes DECISIONS.md content edits | **re-measured** — grepped every task's `files:` block; T-02 only `git mv`s it (rename, no content diff), T-03/T-04/T-06 reference its path as a string literal inside *other* files, none list it under `files:` |
| Everything else (Q1, Q2, A5, DESIGN.md absence) | **attested only** — not re-opened, per instruction |

## Does the remedy discharge r8 Q3?

Yes, for its stated purpose. Synthetic probe (three amendment texts, run against **all four clauses**
of the real awk pipeline, in scratchpad — never against `DECISIONS.md`):

| Probe | clause1 FOUND | clause2 SPELL | clause3 ARITH | clause4 FIGURE |
|---|---|---|---|---|
| (a) intent-faithful — quotes "two of the four", states "the correct figure is ONE of the four" per `:1015` | PASS | PASS | PASS | PASS |
| (b) quotes old figure, states no correction anywhere — the r8 Q3 gap | PASS | PASS | PASS | **FAIL** — "amendment does not correct the two-of-the-four arithmetic" |
| (c) corrects the arithmetic, phrased differently — "Only a single path of the four... The corrected count is 1, not 2." | PASS | PASS | PASS | **FAIL** — same message as (b) |

**(b) failing clause 4 is the proof the remedy works** — r8's Q3 gap (nothing checked for the
corrected figure's presence) is closed. No amendment lacking any stated correction can pass T-08 now.
**(c) is the false-FAIL probe** — see finding below.

## Finding — clause 4's failure message overclaims what the check proves (med, non-blocking)

Clause 4 (`:969-970`) is a literal, case-insensitive substring match for `one of the four`. It is not
a semantic check that the arithmetic was corrected. Probe (c) demonstrates the gap directly: an
amendment that correctly states the count moved from two to one, in different words, fails clause 4
and receives the message "amendment does not correct the two-of-the-four arithmetic" — false in case
(c). The actual defect the check catches is narrower: absence of one specific literal phrase. A
maintainer meeting this message at failure time is told the wrong thing — that the arithmetic itself
is wrong — when the real issue is a phrasing mismatch against an unstated literal requirement.

This matters because T-08's own `intent:` (`:1004-1026`) never mandates a literal phrase for the
corrected figure — the only `USE THE LITERAL PHRASE` instruction (`:1024`) is for the OLD figure,
"two of the four", "quoting what is being corrected." Nothing in the intent tells a future amender
they must reproduce "ONE of the four" verbatim; `:1015`'s caps are, per pm's own stated ground for
judgement 1, "emphatic register, not a requirement." Clause 4 enforces a literal the intent does not
require, and the failure message asserts a semantic defect the check cannot actually detect.

**Why this does not gate:** the compliant path is the likely one. `:1015` hands the executor the
exact phrase to reproduce, so an intent-faithful T-08 execution will almost certainly contain it
verbatim or in a trivial case variant, keeping probe-(c)-shaped failures rare in practice. This is the
same class of low-probability-but-real precision gap as r8's own Q3 was ranked against — advisory,
not must_fix, and DECISIONS.md is not signed. Recommend (not required): reword `:970`'s message to
name the syntactic requirement — e.g. "amendment does not contain the phrase 'one of the four'" —
rather than the semantic claim it currently makes.

## Finding — T-08 self-description gap (med, non-blocking, same standard as Q2/T-06-title)

`:972-1032`'s intent explains clause 3 (why the old-figure literal is grepped, `:1024-1026`) but says
nothing about clause 4 or why a literal "one of the four" check exists. Per G-04 and the operator's
own precedent on Q2 (T-06's title — med, non-blocking, accepted): a gap in a contract's
self-description differs from a shipped-defect risk, because the operator-facing outcome (a
correction is now enforced to be present) is independently checked by clause 4 itself, imprecise
message aside.

## Judgements — wording only, verdicts are eng-lead's

**1. Bracket class `[Oo][Nn][Ee]` vs. `IGNORECASE=1`.** pm's stated ground — "the plan mandates a
literal only for the old figure and never for the corrected one, so the caps at `:1015` are emphatic
register, not a requirement" — is accurate as a reading of `:1004-1026`; I independently confirmed
the only literal mandate in the intent targets "two of the four" (`:1024`). Note the tension this
creates with clause 4's own design (not pm's portability rationale, which is a separate, structural
question for eng-lead): if the corrected figure genuinely carries no literal-phrase requirement, then
clause 4 requiring any specific literal — case-flexible or not — already enforces something stricter
than the intent it verifies. That tension is the mechanism behind the finding above.

**2. No `f`-clearing, "no false pass possible at the pin."** I independently grepped
`docs/harness/DECISIONS.md` at `0f12f14` case-insensitively for both phrases: exactly one hit, "two
of the four" at `:5585`, inside DEC-189's *original* ruling text — which precedes where "### DEC-189
amendment 1" would be appended, so awk's flag would not yet be set when it reaches that line. No
other occurrence of either phrase exists anywhere else in the 5946-line file at the pin. This measured
claim carries to execution time, not just the pin: T-08 is the only task in the cluster whose `files:`
block lists DECISIONS.md content for editing (re-measured above); T-02's `git mv` is a rename with no
content diff, and T-03/T-04/T-06 edit other files' string-literal references to the path, not the
document's own text. Nothing between the pin and T-08's run can introduce a stray occurrence of either
phrase into the file. pm's claim is confirmed, not merely consistent.

## Standing, not re-opened

Q1, Q2, A5, DESIGN.md-absence: unchanged, per instruction.

## Accessibility / theme / rendered-layout

Not applicable — this surface is a CLI verify script and a decisions-document amendment, no
colour-only state encoding, no rendered layout. (P-06/G-02.)

---

## Send-back addendum — the false-PASS direction (probes d, e)

**Verdict revised: FAIL.** The prior PASS covered the false-FAIL direction only. The false-PASS
direction — the one r8's Q3 was actually ranked on — fails at the pipeline's own construction, and
does so on text a compliant executor is naturally invited to write, not on a contrived adversarial
string.

### Probe (d): phrase present only in a non-corrective, intent-mandated sentence

Constructed a synthetic amendment (scratchpad, never `DECISIONS.md`) satisfying clauses 1–3
verbatim as (a)/(c) do, but writing the arithmetic correction in probe-(c)'s own non-literal wording
("the true count is 1, not 2" — deliberately reusing (c)'s already-validated false-FAIL shape) and
placing the literal phrase "one of the four" nowhere except inside the sentence `:1016-1023`
mandates every compliant amendment contain: the enumeration clause recording that "docs/PRINCIPLES.md
, one of the four named paths, still has nothing to match against." Ran against the real awk
pipeline (`:963-970`), file, not narration:

| Probe | clause1 FOUND | clause2 SPELL | clause3 ARITH | clause4 FIGURE |
|---|---|---|---|---|
| (d) correct arithmetic, non-literal wording + incidental phrase from the mandated enumeration | PASS | PASS | PASS | **PASS** |

Clause 4 passes. The corrective sentence itself is never matched by clause 4 at all — the check is
satisfied entirely by a different sentence that has nothing to do with arithmetic correction.

### Probe (e): same incidental phrase, arithmetic stated wrongly

Did not collapse into (d) — ran it, because the shape is materially worse and the mechanism needed
confirming under an actually-incorrect payload, not just a differently-worded-but-correct one.
Identical text to (d) except the corrective sentence now reads "the true count is 3, not 2" — wrong
on its face. Same four-clause run:

| Probe | clause1 FOUND | clause2 SPELL | clause3 ARITH | clause4 FIGURE |
|---|---|---|---|---|
| (e) arithmetic stated wrongly + incidental phrase from the mandated enumeration | PASS | PASS | PASS | **PASS** |

Clause 4 does not distinguish right, wrong, or absent-in-matching-form arithmetic. It only checks
whether the literal substring occurs anywhere after the amendment heading, and the mandated
enumeration clause supplies that substring regardless of what the corrective sentence says.

### Judgement 1 — does clause 4 fully discharge r8 Q3, or only partially?

Only partially, and the prior "Yes, for its stated purpose" is too broad. Clause 4 closes exactly
one shape of Q3: total silence (probe b, phrase absent everywhere) still fails correctly — that part
of the original finding stands unchanged. It does **not** close the shape probes (d) and (e)
demonstrate: an amendment where the corrective sentence itself is phrased outside clause 4's literal
match (differently-but-rightly per (d), or outright wrongly per (e)), while a *different*, mandated
sentence elsewhere supplies the substring incidentally. That second shape is a false-PASS: `awk`
prints nothing, the shell prints `OK`, and the task proceeds to append the amendment to
`DECISIONS.md` with either a non-standard-but-correct correction (d) or a wrong one (e) — with no
propagation checker anywhere in the tree to catch it afterward, per this project's own stated
constraint (`CLAUDE.md`, DEC-188 note: "there is no propagation checker — nothing detects a falsified
statement left standing"). Probe (e) in particular is closer to what Q3 was actually worried about
than probe (b) was: a *wrong number reaching the record unopposed*, not merely a *missing* one.

### Judgement 2 — is the plausibility real or contrived?

Real. `:1004-1026` is not optional colour — it opens "ONE MORE CLAUSE... Amend it as follows, and no
further" and then mandates, as content the author must write, that the amendment (i) enumerate all
four named paths, (ii) state that README.md and `.github/**` "never made the argument," and (iii)
"record that the argument for target-keying still holds, on docs/PRINCIPLES.md" (`:1021-1023`). A
compliant author discharging clause (iii) has to identify docs/PRINCIPLES.md relative to the set of
four named paths — my probe sentence is a direct paraphrase of what that clause asks for, not a
reach for the trigger phrase. Meanwhile `:1015`'s corrective sentence carries no literal-phrase
mandate at all (judgement 1 above, unchanged, independently confirmed both in the original r9 and
again here) — an executor following `:1015`'s content freely, in their own words, has no reason to
route through "one of the four" specifically. The two clauses landing in the same amendment section,
one supplying the phrase incidentally and the other never needing to, is the natural consequence of
what `:1004-1026` actually mandates an author to produce — not a contrived adversarial construction.

### Judgement 3 — severity: revised, and a third finding

This changes severity, not just detail. The original clause-4 finding (message overclaims, med,
non-blocking) is a false-FAIL: loud, blocks the task at `exit 1`, and is corrected by the executor
before anything lands — self-limiting in consequence, which was the explicit ground for rating it
non-blocking. Probes (d)/(e) are the opposite polarity: a false-PASS. The check prints `OK`, the task
proceeds, and — per probe (e) specifically — an amendment carrying a **wrong** corrected figure can
land inside `### DEC-189 amendment 1` in `docs/harness/DECISIONS.md`, which this project's own
`CLAUDE.md` names as "the authority" — read there as ground truth, per the harness's own stated
principle against falsifying the record — with no propagation checker anywhere in the tree to catch
it afterward (same `CLAUDE.md`, DEC-188 note). That is not a message-wording defect; it is a
checkability failure of the contract clause 4 exists to provide — clause 4 was added specifically to
close r8's Q3, and it does not close the shape of Q3 that matters most (a wrong figure reaching the
authority document unopposed, silently). I am not hedging this: **third finding, `must_fix`, severity
`high`** — VERDICT for T-08's clause 4 as currently constructed is **FAIL**. This is a judgement about
the check's coverage, not the structural regex-portability question (bracket class vs. `IGNORECASE`)
reserved for eng-lead in parallel — clause 4 in *either* form still only substring-matches, so this
finding holds regardless of which way that separate question resolves.

**Finding — clause 4 is satisfiable by an unrelated, intent-mandated sentence, independent of what
the corrective sentence itself says (high, must_fix).** Clause 4 cannot be repaired by widening the
pattern — the phrase it greps for is also the phrase a compliant author is independently instructed
to write for an unrelated reason (`:1021-1023`'s enumeration clause). Any literal-substring check
against this specific phrase, in this section, inherits the same false-PASS. A check that actually
discharges Q3 needs to anchor to the corrective sentence itself (e.g., proximity to "two of the four"
within the same sentence or a bounded span, not "anywhere after the amendment heading"), or the
enumeration clause's mandated phrasing needs to change so it no longer collides with the corrective
literal. Recommend (not deciding the fix — eng-lead's call, alongside the two standing structural
questions): re-scope clause 4 to match within N lines of the clause-3 hit, or require the phrase
adjacent to "not two" / "corrects to," so an incidental occurrence elsewhere in the amendment cannot
satisfy it.
