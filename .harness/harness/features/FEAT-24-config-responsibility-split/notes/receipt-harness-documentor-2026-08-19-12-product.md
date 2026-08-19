# Receipt — harness-documentor — distillation, cold

**Five entries added, all to the empty Outcomes section; nothing displaced, nothing dropped.**
`git diff --stat` on the Expertise file is `17 insertions(+), 0 deletions(-)` — a pure insertion via
one `Edit` on the `## Outcomes (max 10)` heading. No op names any `P-` or `G-` entry, so every
pre-existing Patterns and Gotchas entry is byte-identical.

Counts — before: Patterns 15/15, Gotchas 15/15, Outcomes 0/10, Open 0/5, 98 lines.
After: Patterns 15/15, Gotchas 15/15, **Outcomes 5/10**, Open 0/5, **115 lines** (budget 150).

## Accepted

| ID | Source | Entry, in short | Why it earns a slot |
|---|---|---|---|
| O-01 | **my own prior artifact** (receipt `...-3-product.md`, opening section) | correcting a self-scoping record → append a separate record, never extend | Extending am.1 would have falsified its own closing sentence *"This amendment touches the stations paragraph alone."* — creating a fourth false statement while removing one. The form choice is the durable move; it generalises to any record whose text scopes itself. |
| O-02 | **my own prior artifact** (receipt `...-2-product.md`, Q1) | "never hand-edit this generated file" → check which regions the generator preserves, report the narrower constraint | The blanket ban left the hand-written ruling right of ` :: ` — which regeneration cannot reach — with no owner, so a falsified ruling would have survived every regeneration. The rule sends me to *go check* something I would otherwise skip. |
| O-03 | **lead's digest skim, C1** (rewritten) | verify checks only literals/placement/counts → say so in the return, and name what only your reading covered | Accepted as distinct from P-11: P-11 is about *proving a clause matched the right place*; O-03 is about the *coverage gap between the clause set and the intent*, and the duty to report that the only check on substance was my own reading. |
| O-04 | **my own observations log** (2026-08-18, second bullet) | quoting a heading/identifier inside text a parser uses as a boundary → strip the delimiter prefix | A literal `## DEC-196` inside the amendment's quotation would have made the section scan (`src.find("## DEC-", i+1)`) truncate the section under check. Craft half of the observation; the parser specifics are repository-layer (see Open). |
| O-05 | **lead's digest skim, C2** (rewritten) | strike/retitle → two sweeps: the struck wording, and the decision's own identifier | Accepted as distinct from G-04, which sweeps the struck **wording** across live surfaces. O-05 sweeps the **identifier** — a different query catching a different harm: a citation still pointing at the retired title, invisible to a wording sweep. Not folded into G-04 as a `replace` because G-04 is already near the 50-word cap carrying its live-surface list, and folding would cost that list. |

## Rejected, with reasons — not to be re-litigated

- **C3** (amendment 1's *"the record is appended to, never rewritten"* reads general but is scoped by
  its subject; am.2 reconciled the tension explicitly). **Rejected.** Its action is downstream of the
  observation — once the tension is noticed, "mention it" is self-executing, and the noticing is the
  part a rule cannot help with. It also comes from the same incident as O-01, and one incident
  yielding two entries is over-harvest. The durable move from that incident is O-01's form choice.
- **Observations log, first bullet** (regeneration preserves the ruling right of ` :: `; only
  `test-gen-decisions-index.py`'s 30-word cap catches an over-long replacement). Craft half accepted
  as O-02; the cap half is already G-05. Residue is repository-layer — see Open.
- **Receipt `...-2-product.md` Q2** (retitling a signed `##` heading is a plan-level call — flag, do
  not act). **Considered and ruled already covered** by P-15 (*write the true shape into your own
  record, raise the signed prose for re-signature, neither transcribe nor silently edit*). No slot
  spent.

## Open — repository-layer candidates, written nowhere

The repository tier (`.harness/<repo>/expertise/<agent>.md`) is granted to nobody;
`.harness/team-config.yaml:127` grants me only the craft path. Two residues are genuinely
repository-layer and are reported here rather than written:

1. `gen-decisions-index.py` preserves the hand-written ruling right of ` :: ` by DEC number across
   every regeneration; only the generated columns left of it are rebuilt.
2. `AMEND_BOLD_RE` counts any line opening `**Amendment` as an amendment, and a
   `### DEC-NNN amendment` heading contains the substring `## DEC-`, so the last entry in
   `DECISIONS.md` must take the bold inline form.

## Gates

```
$ bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-documentor.md
exit=0
```
Directory-wide run: 15 files, all `OK`, exit 0 (verbatim output in the return).
