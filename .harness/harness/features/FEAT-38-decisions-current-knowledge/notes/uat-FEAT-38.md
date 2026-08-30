# UAT — FEAT-38 decisions as current knowledge
status: ready              # draft | ready | passed | failed — only you set passed/failed
criterion: SC-13 (the only `verify: uat` criterion in BRIEF.md)
tree: graded at `review_sha` **635cd3ba**; pre-fold baseline is `7ebfc9e`. `DECISIONS.md` is byte-identical between `635cd3ba` and this worktree (`git diff 635cd3ba -- .harness/harness/docs/DECISIONS.md` is empty), so every command below reads the reviewed tree. Against the earlier pin `48bbe7e`, the measured delta in this criterion's three entries is: DEC-138 and DEC-174 byte-identical; DEC-181 lost exactly 3 `<!-- claim: -->` markers and 2 blank lines, with zero prose lines changed or removed and zero lines added.

**SC-13, verbatim:** *"Reading the folded DEC-138, DEC-174 and DEC-181 entries, the operator judges
that each reads as a decision stating current truth rather than as merged history — and that no claim
they now consider settled has silently disappeared."*

Ungraded here by design — the judgement is yours. ~15 minutes.

## Setup — paste once

```bash
export WT=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge
export D=.harness/harness/docs/DECISIONS.md
span() { awk -v d="^## DEC-$1 " '$0~d{f=1} f&&/^## DEC-/&&$0!~d{exit} f'; }
amds() { awk '/^### DEC-138 amendment/{f=1;print "----- "$0;next} f&&/^#{2,3} /{f=0} f'; }
cd "$WT"
```

Every extraction is anchored on the `## DEC-NNN` heading, never a line number: line numbers differ
between the two revisions. For any entry, `diff <(git show 7ebfc9e:"$D" | span NNN) <(span NNN < "$D")`
gives the two forms against each other.

## Steps

- **U-01 (SC-13) — DEC-138, eight amendments folded.**
  ```bash
  span 138 < "$D"                        # folded, now  (128 lines)
  git show 7ebfc9e:"$D" | span 138       # pre-fold     (107 lines)
  git show 7ebfc9e:"$D" | amds           # the 8 amendment blocks as they were
  ```
  The third command is required: at `7ebfc9e`, amendments **5–8 sat physically inside DEC-168's span**
  and were folded into DEC-138 by the id their own heading declares, so they are absent from the
  pre-fold DEC-138 span (`notes/receipt-harness-documentor-2026-08-29-06-product-T-08.md`
  §"The five misfiled blocks").
  What to look at:
  - Four claims the tree measured false are meant to survive as present-tense rule text, not as
    dated history: no third category between doing the work and not (`absorbs:` struck); origin does
    not decide a parent's closure (`parent_origin` read null on FEAT-34/35); a closed issue's card
    does not move on its own (#818–#830 closed, all at `Review`); the comment ban's line is
    PROVENANCE, not which skill asks. Source: `runs/2026-08-29-06-product/digest.md` (falsified-claims
    table, four DEC-138 rows).
  - **Two things were dropped, not folded** — the likeliest "a claim disappeared": DEC-138's SC-13
    pre-ship prose note (the two `.claude/skills/harness/SKILL.md` sites and the staleness-marker
    reasoning) and its "codebase map" entry in the not-mirrored list. Both in T-08's receipt
    §"Deleted rather than folded, with justification". Do you consider either settled and now missing?
  - A `### DEC-137 amendment 2` block sat inside DEC-138's span and was cut there — a collision
    between the two entries' spans. It belonged to DEC-137, which was itself deleted as a struck
    entry, so that content is gone from the file rather than relocated: `grep 'map.html'` and
    `grep '^## DEC-137 '` both return nothing now
    (`notes/receipt-harness-documentor-2026-08-29-05-product-T05.md`, row 2 and the six-deletions
    table). Intended, but worth your eye.
  - Index row: `notes/receipt-harness-documentor-2026-08-29-08-product-T11.md` (DEC-138, 23 → 26).
  **PASS/FAIL:** does DEC-138 read as one live rule set, and is every DEC-138 claim you consider
  settled still stated somewhere? If FAIL, name the claim and where you expected it.
  result:

- **U-02 (SC-13) — DEC-174, a reversal where the intermediate position had to survive.**
  ```bash
  span 174 < "$D"                        # folded, now  (122 lines)
  git show 7ebfc9e:"$D" | span 174       # pre-fold     (214 lines)
  ```
  Amendments 2 and 3 were a reversal; the requirement was that the fold state the intermediate
  position **was tried and reversed**, not just the endpoint
  (`runs/2026-08-29-06-product/send-back-criteria.md` item 9). Two surviving clauses to find
  (`notes/receipt-harness-documentor-2026-08-29-06-product-T-08.md:26-27`):
  - the factory-workspace route was reachable but never sanctioned; a harness path there now resolves
    to no declared repository and `check-domain.sh --resolve` exits **2**, not NOBODY;
  - declaring the station board in `fleet.yaml` was tried **twice** (top level, then per `repos[]`
    entry) and reversed; the loader now REJECTS both.
  am.4's fold is recorded in `notes/receipt-harness-documentor-2026-08-29-08-product-T11.md`
  (DEC-174, am.4: category governs, enumeration only records).
  **PASS/FAIL:** can a reader still tell that the reversed position was tried, and why it failed —
  or does the entry keep only the endpoint? If FAIL, quote the sentence that lost the reason.
  result:

- **U-03 (SC-13) — DEC-181, a partial strike folded, two false code citations corrected.**
  ```bash
  span 181 < "$D"                        # folded, now  (46 lines)
  git show 7ebfc9e:"$D" | span 181       # pre-fold     (47 lines)
  ```
  Landed (`notes/receipt-harness-documentor-2026-08-29-06-product-T-09.md`): the
  `**STRUCK IN PART, 2026-08-10.**` paragraph removed; enforcement re-anchored from
  `check-domain.sh:779-780` to the message at `:1335`; peer budget `feature.yaml` 200/20 corrected to
  `feature.json` 300. Consequentially, DEC-188's body no longer asserts DEC-181 is struck in part
  (`notes/receipt-harness-documentor-2026-08-29-08-product-S2.md`) — check `span 188 < "$D"` too.
  - Since the previously graded revision this entry lost three `<!-- claim: -->` HTML-comment markers
    and nothing else: no prose line was changed, removed or added. Any earlier reading of DEC-181
    therefore still holds.
  **Two items you are being pointed at deliberately, because they are the likeliest FAIL:**
  - **(a) Three sentences of drafting history remain** in the folded entry: "80 was re-derived at
    `a5edb13`, not inherited from issue #139"; "an earlier draft of this entry began the table after
    the cleanup"; "An earlier draft called 80 'the only number with evidence' — that overstated it,
    and a reviewer said so." Recorded as the pm's own reservation in
    `runs/2026-08-29-06-product/digest.md`. Whether that is current truth or merged history is exactly
    SC-13's question, and it is yours to answer — the first two are argued there to be load-bearing
    for the 75-83 band, the third is change-narration.
  - **(b) `CLAUDE.md` is now 12 lines** (an `@AGENTS.md` pointer) while DEC-181's prose discusses the
    file at 74–84 lines. Flagged and deliberately not edited:
    `notes/receipt-harness-documentor-2026-08-29-08-product-T21.md` §"Caveat".
  **PASS/FAIL:** does DEC-181 read as one live budget rule stating current truth? If FAIL, say
  whether it is (a), (b), or a claim from the pre-fold form you consider settled and now missing.
  result:

- **U-04 (SC-13, overall) — the criterion itself.**
  Taking the three entries together: does each read as a decision stating current truth rather than as
  merged history, and has no claim you now consider settled silently disappeared?
  **A FAIL must name the entry (138 / 174 / 181) and the specific claim or sentence** — that is what
  the next fix cycle acts on.
  result:

## Recording the result

Set `status:` above to `passed` or `failed` and leave your `result:` text verbatim. A `failed` result
is a fix cycle, not a discussion. `gates.uat` in `.harness/harness.json` is
`blocking_when_uat_criteria_exist`, so the ship decision waits on this file.
