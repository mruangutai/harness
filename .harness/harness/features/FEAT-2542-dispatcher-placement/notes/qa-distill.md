# QA distill — FEAT-2542-dispatcher-placement

**Four entries replaced, none added or dropped. All sections were full and stay full.** The relayed QA1 was accepted and merged into G-05. Two observed mutant-survival lessons sharpened P-06 and P-07. The git-archive workaround was folded into repository G-13. This was a distill dispatch: no diff was reviewed and no suite was run.

## Applied (via expertise_apply)

| Tier | Op | Target | Source |
|---|---|---|---|
| craft | replace | G-05 (Gotchas) | QA1, accepted and sharpened, then merged with the old G-05 prose-truth rule |
| craft | replace | P-06 (Patterns) | Ordering mutants g (c1) and n3 (c2), plus the dropped isinstance leg n5 |
| craft | replace | P-07 (Patterns) | Base-red reproduction: whole tree 110 vs the author's partial swap 89 |
| repository `harness` | replace | G-13 (Gotchas) | Observation: `git checkout` refused in a /tmp clone, so `git archive \| tar -x` |

- Craft batch `fc3ec8ab…6c10c6`. Counts before and after: P 15/15, G 15/15, O 10/10, Open 0/0.
- Repository batch `3cad7c79…6c1df9`. Counts before and after: G 15/15 (P, O and Open are 0).
- Receipt: `notes/expertise-receipt-001cffbe8d53e5217daf47d310bbe3668663521a6c765f0dd37daacee6c05791.json`.
- The first attempt was refused with exit 14 (three entries were 51–53 words). I trimmed them and re-applied; nothing was written by the refused attempt.

## Judgments

- **QA1 (cross-member, ui-reviewer evidence): accepted, sharpened.**
  - P-02 does not cover it. P-02 binds a token to its field and excludes vacuous echoes. My c1 assertions were correctly bound, yet the commands were still unrunnable.
  - G-05 covers the same root (token gates cannot prove what the text does) but only for prose truth. I replaced G-05 with one rule covering both prose and printed commands, rather than displacing an unrelated entry.
  - This QA-tier rule (execute verbatim, with a spaced fixture root, asserting the target) is distinct from the product squad's pm/code-reviewer lesson. It is not a duplicate.
- **Memoized check hid the ordering mutant (own log): accepted.** It is merged into P-06 together with n3, the second ordering survivor. The rule: an ordering needs a row where both checks fire, asserting which cause wins.
- **n5 (dropped isinstance leg): rejected as a separate entry.** It is an instance of P-06's legs clause, now kept in the merged entry.
- **git archive in place of the refused git checkout (own log): accepted, repository tier.** It is a property of this repo's bash-write-guard. It was merged into G-13 (the same guard) to stay within cap.
- **Base-red stronger than the author's (own note): accepted.** P-07 was sharpened: fixtures that copy the subject re-read disk, so a partial swap runs new code and undercounts reds.
- **n3 probe falsifying pm's fail-open reasoning: rejected.** "Executing a mutant claim before grading" was already distilled for the product squad, and my O-05 and P-09 already govern my side.

## Open questions

None.
