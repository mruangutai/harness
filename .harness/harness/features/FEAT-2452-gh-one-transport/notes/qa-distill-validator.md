# QA distillation — FEAT-2452-gh-one-transport (distill-validator)

**BLUF:** 7 ops were applied in 2 batches. No suite was run and no diff was reviewed (distill mission).

## Batches
- craft: batch `cadafccaaa69e11862137e89a703fd6eff1b656bc03bcff5ed17efec260912df` → `.harness/expertise/harness-qa.md`
  - P 15→15, G 15→15, O 10→10, Open 1→1. The ops were replaced P-05, P-07, P-12 and G-02.
- repository (harness): batch `e5c6abcaf37a3c867b0f2e7eb5cdb38afa562711a7d67a795f848726f89276a8` → `.harness/harness/expertise/harness-qa.md`
  - P 0→0, G 11→13, O 0→0, Open 0→0. The ops were replaced G-06 and added G-12 and G-13.
- Receipt: `.harness/harness/features/FEAT-2452-gh-one-transport/notes/expertise-receipt-700924d91fe41a8d3cb6cb0670bb99e0843b06f71e31df6e3fd9f0cbc2e33e48.json`

## Lead candidates
- LC-1: applied as craft G-02, displacing an earlier ship-freshness gotcha that sits outside QA's seat.
- LC-2: applied as craft P-05, merged with LC-3. The displaced entry was a dev design rule about deriving a prohibited site from the canonical authority.
- LC-3: applied as craft P-05, merged with LC-2 into one rule covering field values and identity.

## Observations
- Old-blob red reproduction became craft P-07. It displaced the narrow lock-release fixture rule.
- The unasserted recorder seam became craft P-12, which was sharpened and kept at the same length.
- The pin lacking node_modules became repository G-12.
- The bash-write-guard variable-target redirect became repository G-13.
- check-domain refusing source edits inside the pin, plus routing markers to sys.__stderr__, became repository G-06. It replaces the older advice to copy into a worktree.
- The fix-c2 red counts were not distilled. They are a one-run instance, so they are a story, not a rule.
