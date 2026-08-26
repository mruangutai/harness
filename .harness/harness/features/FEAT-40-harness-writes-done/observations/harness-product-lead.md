# Observations — harness-product-lead — FEAT-40

- 2026-08-25 (run 07): the "sweep the class" instruction failed the same way twice in this feature.
  Run 06's dispatch named three sites and missed D-07; run 07's dispatch named three and I found
  two more at my own tier before dispatching (`gh-sync.py:219-220`, `gh-sync.py:851`), then a
  fifth after pm returned (`test-gh-sync.py:1615-1617`). The fifth is the interesting one: pm ran
  three greps — `item.?closed`, `native|lands? it in Done|...`, `clos(e|es|ing|ed).{0,80}(Done|...)`
  — and all three correctly returned nothing, because the site is a PARAPHRASE ("Done is GitHub's
  own workflow") carrying neither `Item` nor `closed` nor `native`. A phrase-shaped sweep cannot
  find a paraphrase of the claim. Distillation candidate, craft tier.
- 2026-08-25 (run 07): my own dispatch instruction was wrong on one of the two extra sites I found.
  I told pm to fold `gh-sync.py:851` into T-04; pm refused with evidence — T-11 deletes
  `cmd_close_task` "including its comments" and `depends_on: [T-04, T-06]`, so correcting it in
  T-04 is work T-11 then deletes. Lesson for me: before folding a comment fix into a task, check
  whether another task in the same plan DELETES the enclosing function. I had read the Q8 ruling
  (`answers-2026-08-25-02.md:54`) only after dispatching.
- 2026-08-25 (run 07): I spent a subagent spawn trying to correct pm mid-flight. There is no
  `SendMessage` at lead tier and `handoff-plan.md:50-51` already recorded that as a known dead end
  — it had killed run `2026-08-25-03-product`. I should have read the handoff's Dead Ends section
  before reaching for the tool. Wasted spawn, my error.
- 2026-08-25 (run 07): DEC-188's strike convention bounds this class usefully. ~15 live citations of
  DEC-192 exist across `.claude/skills/harness/bin/`, and they do NOT all need repointing when T-03
  strikes it, because a struck entry keeps its row and its record so citations still resolve. Only
  `gh-sync.py:898` needed the swap, and only because its surrounding premise was being rewritten
  anyway. Useful guard against a scope explosion the word "sweep" invites.
- 2026-08-25 (run 07): `DECISIONS.md:6614` states the same falsified causality but sits inside
  DEC-196, which T-03 strikes. Correcting it would falsify the record (PRINCIPLES rule 15, `:269`).
  Struck-and-retained is the right treatment, not corrected — worth checking before adding any
  decision-document occurrence to a comment-correction class.
