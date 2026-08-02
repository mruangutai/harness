# Observations — harness-pm — FEAT-04-decisions-index

- 2026-08-01: the grilling note and the dispatch both said "170 top-level DECs". `grep -c '^## DEC-'`
  = 170, `sort -u` = 169, `uniq -d` = `## DEC-83`. My first read was "the authority has a duplicated
  heading" and I wrote a decision around keying past it. Wrong: the second occurrence (line 1583) is
  **inside a code fence** — an illustration of the heading format. The live count is 169 and the
  duplicate does not exist once a fence guard runs. Two lessons: (i) `grep -c` on a markdown
  structural pattern over-counts by exactly the number of fenced illustrations, and the harness's own
  `check-docs.sh` carries a fence toggle for precisely this reason; (ii) I built a design decision on
  a grep artifact and only a "verify this before review" prompt caught it. The discriminating command
  was `grep -n '^## DEC-83'` plus a fence-aware parse — one line, and I should have run it before
  writing D-04, not after.
- 2026-08-01: the dispatch offered two resolutions for the index-inside-the-scanner problem
  (blanket exclusion vs blanket per-row marker) and both were dominated by a third it did not list:
  targeted markers only on rows the checker actually flags, with zero change to `check-docs.sh`.
  Choosing "neither of your two" was the right read of a dispatch that said "two candidate
  resolutions" rather than "choose one of these two".
- 2026-08-01: the generator must preserve the *whole* hand-written segment, not just ruling prose —
  an inline `<!-- ok-stale -->` living in that segment is stripped by a naive
  regenerate-rulings-only merge, and the failure surfaces as a red gate two commits later with no
  test having caught it. Named its own test rather than folded into the preservation test.
- 2026-08-01: declaring a `<!-- stale: ... -->` marker for wording a feature removes is the
  disciplined instinct, but each marker moves `check-docs.sh`'s emitted pattern count, which is
  exactly what a pinned-baseline SC asserts. The two disciplines collide; the collision belongs to
  whoever owns the pinned baseline, not to pm. Raised as a non-blocking question, not decided
  silently.
- 2026-08-01: batching a large-file read across spawns should be balanced by **lines**, not by item
  count. DEC-01..DEC-88 is 1,099 lines and DEC-116..DEC-138 is 1,104 — 88 items versus 23 for the
  same cost. Count-balanced batches would have been 4x skewed.
- 2026-08-01 (fix cycle 1): I specified an extraction regex (`DEC-NN am.N`) from the *shape I expected*
  the authority to use, and it matched zero lines. Two real forms existed — `### DEC-NNN amendment[ N]`
  headings (9) and `**Amendment …**` bold paragraphs (2) — and my D-02, T-02 and T-06 all rested on the
  invented one. One `grep -c` of my own pattern before writing the decision would have caught it. The
  general shape: a *pattern* asserted in a plan is a claim about a file and gets the same
  verify-before-writing treatment as a count.
- 2026-08-01 (fix cycle 1): a skip-on-not-ready predicate is where mechanical teeth go to die. Test 5
  skipped when "absent OR sentinel present", and the sentinel state was exactly what the requirement
  existed to catch — so the check passed forever post-ship. The honest fix costs a deliberately red
  gate window mid-feature, which must be written where the orchestrator reads it, not only in the test.
- 2026-08-01 (fix cycle 1): when a generator recomputes part of a line a human also edits, "preserved
  byte-identical" is not specifiable without naming the canonical emission order — and the strip rule
  must be plural (DEC-19 is targeted twice, so one row carries two clauses; strip-one-append-two grows
  the row every run and the idempotency gate fails for a reason that looks unrelated).
- 2026-08-01 (fix cycle 1): batch boundaries drawn on line numbers can cut a *logical* entity in half.
  DEC-138's amendments sit at :3264..:3308 and :4244..:4299 — two different batches — so the batch
  writing its ruling "as currently amended" could not see three of seven. The fix is a bounded extra
  read named in the task, not a moved boundary.
- 2026-08-01 (fix cycle 1): closing a bare-absence hole with a *length floor* can relocate the hole
  rather than close it. My first floor ("≥20 chars after the delimiter") was clearable by
  generator-written text alone — DEC-19's row carries two `— SUPERSEDED BY` clauses, ~44 characters, with
  no human prose. A floor only means "written" if it is measured on the segment the human owns, after
  the generated part is stripped.
- 2026-08-01 (fix cycle 1): a drafting constraint expressed over *sentences* is unenforceable when the
  checking tool is `grep`. Hard-wrapped prose splits sentences across lines, so a rule like "the
  sentence must also contain the negation" can be satisfied while the matching line is not. Write
  grep-facing constraints in lines.
- 2026-08-01 (fix cycle 2): pinning a plant phrase by quoting it *literally* in the plan made the plan
  itself fail the gate it was specifying — two real STALE hits in the feature's own brief and plan,
  before any deliverable existed. The scanned set is `docs/harness/`, `.harness/`, `.claude/skills/`,
  `.claude/commands/` minus basename `DECISIONS.md` and any `/runs/` path, so planning artifacts and
  this very log are targets while run digests are exempt. Two durable bits: a plan that quotes retired
  wording must carry `<!-- ok-stale -->` **on the phrase's own physical line** (`:133` is a per-line
  substring test, so a reflow silently re-reds the gate), and the alternative — anchoring by
  `DECISIONS.md:LINE` instead of quoting — is unsafe when the owning DEC declares near-homograph
  siblings on adjacent lines (`:2479` vs `:2480` differ by one word), because a one-off read yields a
  different, equally-stale phrase and the doer cannot tell.
- 2026-08-01 (fix cycle 3): a rationale clause naming a decision by id and judging its estimate
  lived at **two** sites — inside D-01's own trigger bullet and in the task step that fires it. The
  dispatch named only the second. `grep -n` on the distinctive word before editing found both; aligning
  one would have built the contradiction inside the decision itself. Rule shape: before rewriting any
  clause that references a decision by id, grep its distinctive word across the artifact — plan prose
  duplicates rationale far more than it duplicates numbers.
- 2026-08-01 (fix cycle 3): a bounded extra read specified as several narrow windows can truncate the
  very rule it exists to deliver — am.6's operative text is a blockquote well below its heading, outside
  a heading-sized window. Contiguous-and-larger beat several-and-narrow: 132 lines against a 1,104-line
  main range is still bounded, and the size figure belongs in the artifact so its boundedness is visible
  without arithmetic.
- 2026-08-01 (fix cycle 3): a batch range can be correct while a *single row inside it* is unwritable
  from that range — DEC-168's body region is 155 lines of which 132 belong to another decision's
  amendments. Line-bounded batching needs per-row body-end anchors wherever a foreign entity nests
  inside a region, and that is human misattribution, a strictly worse failure than the generator
  artifact of tags absorbing adjacent words.
- 2026-08-01: cost discipline held — no whole read of `DECISIONS.md`, no `check-docs.sh` run, SPEC
  and BUILD never opened. Every fact in both artifacts came from a targeted grep or the pinned
  `feature.yaml baseline:`.
