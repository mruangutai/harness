# Expertise — harness-documentor

## Patterns (max 15)
- P-01: WHEN a dispatch or plan hands down a `file:line` anchor or a count of things DO grep it
  yourself and write the named list rather than the count — handed-down anchors and counts are the
  least trustworthy input you receive.
- P-02: WHEN appending an amendment to a decision in `.harness/harness/docs/DECISIONS.md` DO grep the new
  amendment number for a collision and append at the file's last amendment, not beside its parent
  decision — amendments are not contiguous with the decision they amend.
- P-03: WHEN you edit on a dirty working tree DO read `git diff -U0` hunk headers to bound your own
  change — `--stat` totals silently include edits already present at spawn, and reporting them as
  yours misstates the diff.
- P-04: WHEN a record you write must stay true after you file it DO anchor it on quoted content
  strings, not `file:line` — your own later edits shift anchors before you ship, and other agents'
  commits rot them afterwards while the content they point at survives.
- P-05: WHEN describing behaviour you diagnosed at an earlier commit DO name that commit and write
  the past tense — present-tense wording turns a fixed diagnosis into an authority claim that one
  grep of the current file contradicts.
- P-06: WHEN a task's stated intent mandates prose containing a token that same task's `verify:`
  clause counts or forbids DO write around the token — name the mechanism, not the filename or ID —
  and raise the conflict; the grep clause is the tie-breaker, not the prose.
- P-07: WHEN an approved plan mandates wording DO follow it for names and attributions — those are
  signed decisions, not yours to revise — but verify any factual claim in it against the code
  before transcribing; approval covers the choice, not the truth.
- P-08: WHEN a bound says neighbouring text "stays verbatim" DO make the hunk list from
  `git diff -U1` your receipt — absence and count clauses cannot see collateral damage to text that
  never contained the token they watch.
- P-09: WHEN you report that a structural or parse check passed DO first run it against a
  deliberately broken copy of the same input — lenient parsers accept malformed input, so "it
  parsed" is evidence of nothing until the checker is shown rejecting something.
- P-10: WHEN adding an entry to `.harness/harness/docs/DECISIONS.md` DO append at end-of-file and regenerate
  the index rather than hand-writing the new row — appending keeps every existing `@line` anchor
  stable, and the generator emits a sentinel telling you the one place to write.
- P-11: WHEN a `verify:` clause is your evidence that a criterion about a section's body is met DO
  print the matching line for every assertion and show it sits in that section — a clause green
  before your edit and after matched unrelated text, and all-PASS then means nothing.
- P-12: WHEN you delete a block of documentation DO inventory what durable content it carried and
  name, for each item, a live in-tree site that still holds it — some survive only in history, and
  those need a `git show <sha>:<path>` in your receipt or they are lost.
- P-13: WHEN you narrow a claim in one file after disproving its broad form DO grep every file you
  touched for the stronger phrasing too — verify coverage is per-file, so the same claim restated
  in an uncovered file exits 0 and ships false.
- P-14: WHEN you strike or shrink a section of `.harness/harness/docs/DECISIONS.md` DO expect the
  regenerated index row to lose `refs:` and `[tags]` — the generator recomputes both from the
  section's body text — and report that as an effect of your edit, never as a generator defect.

## Gotchas (max 15)
- G-01: WHEN you intend to claim a checker's output is unchanged DO run that checker before your
  edit — the values a plan or brief records were true when written and drift silently afterwards.
- G-02: WHEN handed-down prose says "always" or "unconditionally" DO grep for the early return or
  skip clause before repeating it, and write the narrower claim the guards actually support.
- G-03: WHEN a decision the tree flatly contradicts turns up DO strike it, never mark it — DEC-188
  removed the superseded-pattern marker and its checker entirely. A struck decision keeps its
  heading and a strike record so old citations still land somewhere.
- G-04: WHEN you strike a decision DO sweep every live surface by hand — no propagation checker
  exists (DEC-188), so a falsified sentence standing is caught only by a human reading the diff.
  Live: CLAUDE.md, docs/, .claude/{skills,commands,agents}, .harness/expertise; .harness/features
  is historical record, leave them.
- G-05: WHEN you edit a ruling in `.harness/harness/docs/DECISIONS-INDEX.md` DO run the unit-test runner, not
  just the generator diff — the index's length budgets are asserted only in
  `test-gen-decisions-index.py` and stated nowhere in the index itself.
- G-06: WHEN a `grep -c` detector must go from 0 to >=1 in a hard-wrapped file DO re-flow so the
  counted tokens share one physical line — grep counts physical lines, so a prose-correct fix still
  reads 0 and looks unwritten.
- G-07: WHEN wording a decision title or a bold run in `DECISIONS.md` DO check which marker tokens
  `gen-decisions-index.py` scans for — a title opening with one makes the generator stamp a live
  decision's row as superseded.
- G-08: WHEN a criterion's sweep greps a compound token or a phrase DO also sweep the bare anchor
  word, across every file type in scope — backticks and inline markup break word adjacency
  mid-phrase, and habit scopes sweeps to Markdown while hand-maintained `.html` describes live
  behaviour too.
- G-09: WHEN a verify clause is a `grep -v` allow-list sweep DO read stdout, not the exit code — an
  empty result exits 1, so a wrapper treating non-zero as failure reports a green clause as red.
- G-10: WHEN deleting a clause that begins mid-sentence DO fold the deletion and the
  recapitalisation into one edit spanning the sentence boundary — no absence or count check can see
  the orphaned lowercase word left behind.
- G-11: WHEN a heading or sentence counts the blocks beneath it DO grep that claim before deleting
  any block it governs; retitle-and-trim keeps it true. Count the opening tag, never a bare class
  name — inline CSS selectors inflate the count.
- G-12: WHEN prose describes a check whose polarity the code has since inverted DO delete the
  clause, not annotate it as removed — a removal marker preserves a false statement and reads as
  deliberate history.
- G-13: WHEN a sweep's figure must be reproducible DO state the tool's ignore semantics — `git grep`
  and `rg` skip git-ignored paths that plain `grep -r` walks, so a SHA-pinned count and a
  working-tree count can differ by an order of magnitude with neither being wrong.
- G-14: WHEN a criterion is shaped "file X leaves the sweep" DO enumerate every hit in X with the
  criterion's own full pattern and show each sits in text your edit removes — grepping one token of
  a five-token pattern verifies one fifth of the claim, and file-level arithmetic verifies none.
- G-15: WHEN a sweep needs a word boundary DO use `-P` or spell it as a character class — `git grep
  -E` treats `\b` as matching nothing and exits 1, indistinguishable from a clean sweep; dropping
  `-E` breaks alternation, and `/usr/bin/grep -E` honours `\b`, so the trap is git grep's.

## Outcomes (max 10)

## Open (max 5)
