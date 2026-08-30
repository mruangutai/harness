# BRIEF — FEAT-38 DECISIONS.md states current knowledge

> **AMENDMENT — 2026-08-29 — NOT YET SIGNED.**
>
> **This is an amendment to an already-approved brief.** The operator has ruled that the
> executable-claims mechanism is **DELETED, not redesigned**: a non-executing declarative
> replacement was put to them in full and **rejected**. Every requirement and criterion that
> asserted that mechanism is retired below and replaced.
>
> **The signature in `## Approval` at the foot of this file is STALE.** It was given before the
> ruling and covers the pre-ruling scope only — it does not cover one word of this amendment. Only
> the main session may reset it, and only the operator may sign it again.
>
> Read **"The executable-claims mechanism is DELETED, not redesigned — read this before signing"**
> below before you sign. It states what is removed and, in its own subsection, what removal costs.

## Problem

`.harness/harness/docs/DECISIONS.md` no longer says what is true; it says what was true, in layers.
An agent that opens it to settle a question meets 38 amendment blocks — a decision's body, then a
dated sub-section correcting it, sometimes a third correcting the second — plus 8 entries the index
marks `SUPERSEDED BY` and 8 more marked `STRUCK`. Every reader has to date-sort the file in their head
before they can act on it, and the layering is not merely slow: it is wrong in ways nobody notices.
Four DEC-138 amendments sit physically inside DEC-168's span. Two blocks are both titled
`DEC-189 amendment 1`. `DEC-145 am.3` is annotated MOOTED and still there. DEC-181 asserts a code
location that at `7ebfc9e` is an unrelated comment block, and a budget the code does not have. The
file's own front matter mandates the layering — *APPEND-ONLY. Never rewrite or renumber an existing
entry* — so every reader's cost compounds, and the one prior attempt to simply delete an entry
(DEC-161) left a broken reference the index generator recreates on every single run.

## Goal

`DECISIONS.md` holds only live decisions, each stating current truth in its own voice. No amendment
sub-sections, no `am.N`, no superseded entries, no `SUPERSEDED BY` markers, no struck entries that
have somewhere else to point, and no code left in the tree that can produce any of them. A claim that
was measured false does not vanish — it survives as one clause of current truth, in the document's
own voice, so nobody re-proposes something already disproved. Git holds the history. **One**
mechanical check is installed while the entries are open, because it will never again be this cheap:
it catches a `file:line` anchor that no longer resolves. There is deliberately no second check. The
mechanism that re-ran an entry's claims as commands is deleted, and with it goes the only thing that
could ever have caught a cited line which still exists and no longer says what the entry claims
about it. That rot is now caught by a human reading a diff, or not at all — the operator chose that
price over letting document text reach a subprocess argv, and the trade is stated in full below.

**Size is not a goal.** The file getting shorter is a consequence of stating current truth. Nothing
is cut to hit a number.

## Scope was widened after the grilling — read this before signing

The 2026-08-24 operator interview settled *"do strike records go too? → NO."* On that ruling this
feature deleted nothing and only folded amendments.

**A later operator ruling, dated 2026-08-26, reverses it** — recorded in
`.harness/notes/triage-decisions-authority-2026-08-26.md`, section 9. It rules that **seven of the
eight struck entries are deleted**: DEC-103, DEC-104, DEC-137, DEC-140, DEC-186, DEC-192, DEC-196,
each because a named successor exists for a reader to land on. **DEC-90 is the one recorded
exception** and stays with its strike record: its successor is a SPEC section rather than a decision,
so a citation would degrade to a pointer of a different kind, and its 18 historical citations sit in
signed artifacts that cannot be edited.

In plain words, this is what you are signing that you were not signing on 2026-08-24:

- **15 entries are deleted, not 0** — the 7 struck above, plus the 8 superseded ones (DEC-19, 20, 37,
  67, 82, 88, 92, 102) that #78 always covered.
- **DEC-188's retention clause is struck.** It reads *"Struck decisions keep their heading and a
  strike record. They are not deleted from the file."* That sentence forbids the ruling, and it is
  load-bearing: any agent following decision discipline will open DEC-188 and correctly refuse the
  deletion. It is struck by DEC-188's own procedure and replaced with a narrower rule — *a struck
  decision is deleted only when a named successor exists to repoint its citations to* — which permits
  the seven, forbids DEC-90, and is derived from the measurement rather than asserted beside it.
- **54 more citation sites** must be repointed than the fold alone required: 30 to the struck seven,
  24 to the superseded eight, outside frozen records.
- **Amendment dates are deliberately dropped from the prose.** #615's read-back asks that three
  things survive each fold — the prior belief, what falsified it, and the date. The first two survive
  in the folded text as current truth. The **date does not**, by the 2026-08-24 ruling that the
  entry carries no dates and no attribution; it stays recoverable only by
  `git log --follow -- .harness/harness/docs/DECISIONS.md`, which is the command to use because the
  file was renamed in FEAT-22 and the plain `git log` reaches only 8 of the amendments.

Nothing else was widened. `.harness/logs/**` and `.harness/harness/features/**` are dated records of
what was true on a day and are **not rewritten** — that is what keeps the sweep at 54 sites rather
than several hundred.

## The executable-claims mechanism is DELETED, not redesigned — read this before signing

**A third operator ruling, dated 2026-08-29** — recorded in this feature's `STATE.md` as ruling 3 and
settled in `.harness/notes/grilling-remove-executable-claims-2026-08-29.md`. The operator accepts no
document-driven subprocess risk, and **chose removal over a non-executing redesign** after the
redesign was explained in full. Claim-checking was machinery layered above this feature's goal —
removing redundant, self-reversing decisions — rather than the goal itself.

In plain words, this is what you are signing that you were not signing when you signed below:

- **The mechanism goes entirely, not into a safer form.** `check-decision-claims.py`, its test file,
  its registration in `run-unit-tests.sh` and in `.harness/harness.json`, all 11 live claim markers in
  `DECISIONS.md`, and DEC-205's rule mandating them. Blast radius outside this feature's folder is
  exactly those five tracked files, measured at `48bbe7e`; `DECISIONS.md`, `.harness/harness.json` and
  `.claude/skills/harness/bin/**` are byte-identical at `99bb52c`, so that measurement still holds.
- **The 11 markers are deleted, not translated.** They sit in 6 entries — DEC-145, DEC-157, DEC-181
  (3), DEC-183 (3), DEC-193, DEC-205 (2). DEC-205's own two are **self-referential**: one asserts the
  allowlist constant inside the checker being deleted, the other that checker's registration in the
  runner. Once it is gone there is nothing for either to say.
- **DEC-205 becomes a lying document the moment that rule is removed, and repairing it is part of the
  edit, not a follow-up.** Its heading ends *"and two mechanical checks guard it"*, and its
  enumeration is introduced by *"Two mechanical checks guard this file, and only two."* Both are false
  with one check left. Rule 1, anchor rot, stays exactly as written.
- **`check-decision-anchors.py` is RETAINED, unchanged, and is not in the risk class.** Its argv is
  the fixed literal `["git", "ls-files"]` (`check-decision-anchors.py:111`); no document text reaches
  a subprocess anywhere in it. Nothing in this amendment touches it or its test, and over-deletion of
  it must be visible — it is adjacent to everything being removed and shares a filename prefix with
  it, which is why SC-18 exists.
- **The audit of the whole class comes IN scope.** Every other script under
  `.claude/skills/harness/bin/` is swept for the same shape — any argv built from document or
  configuration text. The ruling is about a class of risk, not about one file. 72 files there mention
  `subprocess`, `shlex`, `shell=`, `Popen`, `os.system` or `eval(`; most are tests invoking a fixed
  argv, so this is a filtering job over a real surface rather than a one-command answer.
  `check-decision-claims.py` is the only instance known today.
- **Nothing is implemented and then deleted.** Three ship-review backlog rows die here rather than
  being worked: B-8 (harden the executing checker) and B-11 (annotate `ALLOWED_GIT_SUBCOMMANDS`) are
  MOOT, both describing a path being removed, and B-10 is SUPERSEDED because that prose is deleted
  rather than patched.

### What removal costs, and the operator accepted it with the cost named

Removal is a **two-sided trade, and the second side is real.** What it buys: no document text ever
reaches a subprocess argv, so there is no allowlist that must stay ahead of every future `git`
release, and a documentation file cannot become an execution surface inside the test suite. That is a
different *kind* of assurance, not a stronger version of the same one.

What it sells: **after this lands, nothing detects semantic citation rot** — a line an entry cites
that still exists, still resolves, and no longer says what the entry claims about it. The retained
anchor check sees existence and range only, and DEC-205 rule 1 already admits exactly this in its own
words. No gate, no suite, no reviewer prompt and no convention replaces it; the detector for it is a
human reading a diff.

**The operator accepted that cost by choosing removal, with the alternative on the table.** It is
recorded here rather than in a footnote because a reader who signs this brief is signing the absence.
Whether anything should replace it later is deliberately left unsharp and is not in scope here.

## Two backlog tickets, ruled on rather than left open

**#686 — the DECISIONS-INDEX generation contract — comes IN, scoped to one clause.** Not on anybody's
recommendation; on a defect this feature manufactures. `DECISIONS-INDEX.md:206` is DEC-188's row and
reads `refs: DEC-103 DEC-104 DEC-161 DEC-165 DEC-181`. **DEC-188 survives this feature and DEC-103 and
DEC-104 are deleted by it**, so after the deletion that row cites two decisions that do not exist —
and because the index is generated, it cannot be hand-edited out. The standing proof of the shape is
already in the tree: zero `## DEC-161` headings exist at `7ebfc9e`, yet `DECISIONS-INDEX.md:123` and
`:206` both carry `DEC-161` in `refs:`, regenerated on every run. The generator's orphan detection
catches a *row* whose entry is gone; it never looks at a `refs:` graph. So one clause of #686 — what
the generator does with a `refs:` id that has no live heading — is a precondition for any deletion
here, and it is in scope. The rest of #686 is not.

**#448 stays OUT and closes on ship.** It proposes a checker for amendment spans — the exact construct
#615 deletes. The two are mutually exclusive on the same surface, and only one ordering is cheap.
It is closed as superseded once this lands.

## Requirements

- REQ-01: A reader of `DECISIONS.md` sees only live decisions, each stating current truth directly —
  no amendment block, no `am.N`, no superseded entry, no `SUPERSEDED BY` marker.
- REQ-02: A claim that was measured false survives as one clause of current truth in the entry that
  replaced it, so it cannot be re-proposed as new.
- REQ-03: The seven struck entries with named successors are gone; DEC-90 remains with its strike
  record.
- REQ-04: No live document, script or generated index row cites a decision id that has no entry.
- REQ-05: The conventions this feature establishes are written down where a decision is written down,
  and the surfaces that taught the old convention no longer teach it.
- REQ-06: The tree cannot silently regain an amendment block or a supersession marker — neither by a
  hand-written one nor by code that could emit one.
- REQ-07: A `file:line` anchor in `DECISIONS.md` that no longer resolves is caught mechanically.
- REQ-08: **RETIRED 2026-08-29 — the id is kept, not renumbered and not reused.** It required that an
  entry recording something a command can check carry that command and its expected result, re-run
  mechanically. The removal ruling withdraws it and nothing replaces it. The tombstone stands so that
  the artifacts citing REQ-08 — `plan.yaml` task `traces:` lists, `notes/ship-review-2026-08-29-18.md`
  and the run digests — land on the withdrawal instead of on text that reads as live. Nothing traces
  to it any more; a task still tracing to it is a plan defect.
- REQ-09: Before the change is accepted, a human has read each folded entry against its pre-fold form
  and confirmed the prior belief and its falsification survive.
- REQ-10: `check-decision-claims.py` — the one script known today to build a command line from
  document text — is gone with both its registrations, `DECISIONS.md` neither carries such a claim
  nor instructs an author to write one, and **the same question is answered on the record for every
  other script under `.claude/skills/harness/bin/`**: the sweep's command, the set it returned, a
  per-file verdict, and the disposition of anything it finds.
  **CONDITIONED DELIBERATELY, AND THIS CONDITIONING IS PART OF WHAT IS BEING SIGNED.** An earlier
  draft read as an unconditional claim about the whole class — *no script builds a command line from
  document or configuration text*. The audit this feature itself commissions can falsify that, and
  one candidate is already named: a whole command string stored in configuration, such as
  `.harness/harness.json`'s `test_kinds.<kind>.cmd`, executed by whatever reads it. So the
  requirement is met by the class being **swept and its members named with a recommendation**, not
  by the text-derived set being empty. **Remediating any site beyond `check-decision-claims.py` is
  explicitly OUT of scope here** and becomes a backlog row filed at ship, citing the audit note. A
  non-empty result is a finding this feature delivers, not a failure of it.

## Constraints

**Decisions that SUPPLY the mechanism** — these are how the work is done, not obstacles:

- **DEC-188** supplies the strike procedure this feature uses on DEC-188's own retention clause. Its
  retention clause is the one thing struck; the procedure stands.
- **DEC-182** supplies the plan format. `verify:` is a literal block; `files:` are plain strings.
- **DEC-174** supplies the carve-out shape used for every `main-session-direct` task below.
- **DEC-191** renamed `feature.yaml` to `feature.json`, which is why three anchors in `DECISIONS.md`
  resolve to nothing and why REQ-07 has an existence proof today.

**Decisions and facts that BLOCK or bound:**

- **DEC-188's retention clause blocks REQ-03** until struck. Nothing may delete a struck entry first.
- **`DECISIONS.md` contains zero literal "SUPERSEDED" text.** The marker is derived by the generator
  from entry titles and body prose. This is the single most important fact before touching the file.
- **`.harness/harness/features/**` and `.harness/logs/**` are frozen.** They are dated records; a
  dangling citation inside one is correct for the day it records.
- **Decision numbers are never reused.** Reuse makes every historical citation actively wrong rather
  than merely dangling.
- **`.agents/skills` is a tracked symlink** to `.claude/skills`. Every path is written against
  `.claude/skills/...`; a path spelling `.agents/skills` will not match a `git ls-files` check.
- **Thirteen surfaces this feature must edit are in NOBODY's domain** — measured with
  `check-domain.sh --resolve` per path at `7ebfc9e`. They include `.claude/skills/harness/SKILL.md`,
  `harness-team/SKILL.md`, both orchestrator agent files (`.claude/agents/` and `.omp/agents/`, the
  second a citation surface no intake artifact saw), `.gitignore` and `.harness/factory/fleet.yaml`.
  They cannot be dispatched to a squad — a NOBODY path is a violation in `check-plan-routes.py` under
  `execution_mode: team` — so they are one `main-session-direct` task, with the carve-out declared
  once in the plan's `lanes:` block rather than re-argued per task.
- **`run-unit-tests.sh` and `.harness/harness.json` are in different lanes** and must agree: the
  runner rejects any `INTEGRATION_SCRIPTS` name absent from the config's `integration` detect. A
  checker registers on both sides or the runner exits 2 — **and deregisters from both sides, for the
  same reason.** A removal that clears one side only is a live defect, not a cosmetic leftover.

## Success Criteria

Every criterion below is graded against the pinned `review_sha`, using `git show <review_sha>:<path>`
rather than a working-tree read, so a deliverable that never entered the reviewed tree cannot pass one.

- SC-01: `DECISIONS.md` at `review_sha` contains zero lines matching
  `^###\s+DEC-[0-9]+\s+amendment` and zero matching `^\*\*Amendment`. Asserted by exit status of the
  search, not by a counted-to-zero comparison. It rejects the tree today, where the two patterns
  match 25 and 13 lines.
  verify: automated        evidence: integration
- SC-02: For each of the 15 deleted ids individually — 19, 20, 37, 67, 82, 88, 92, 102, 103, 104,
  137, 140, 186, 192, 196 — `DECISIONS.md` at `review_sha` has no `## DEC-<id>` heading, and
  `DECISIONS-INDEX.md` names it in neither a row id nor a `refs:` graph. Per-id, because a
  file-global count is satisfied by the fourteen that were done.
  verify: automated        evidence: integration
- SC-03: `DECISIONS.md` at `review_sha` still carries `## DEC-90 — STRUCK` and its strike record. It
  is the one recorded exception and over-deletion must be visible.
  verify: automated        evidence: integration
- SC-04: No file outside `.harness/harness/features/`, `.harness/notes/` and `.harness/logs/`
  contains `am.N`, `DEC-<n> amendment`, or a citation to any of the 15 deleted ids at `review_sha`.
  It rejects the tree today, where those patterns match 37, 30 and 24 occurrences.
  verify: automated        evidence: integration
- SC-05: `DECISIONS-INDEX.md` at `review_sha` contains no `SUPERSEDED BY` row, no `am.` span token
  and no `am-span` header paragraph, and `gen-decisions-index.py --stdout` diffs clean against it.
  verify: automated        evidence: integration
- SC-06: `gen-decisions-index.py` at `review_sha` contains no `AMEND_HEADING_RE`, `AMEND_BOLD_RE`,
  `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE`, `compute_amendments`, `format_amendment_span` or
  `compute_supersession_target`, and its orphan detection still reports an index row whose entry is
  gone. Dead code left in is how the next `**Amendment 1` silently revives a live `am.1`.
  verify: automated        evidence: integration
- SC-07: A new case in `test-gen-decisions-index.py` fails when a single amendment heading is planted
  in `DECISIONS.md` and passes when it is removed, and the transcript of both runs is recorded. The
  new case's own `ok -` line is named, so it cannot be deleted with the suite still green.
  verify: automated        evidence: integration
- SC-08: The anchor checker reports exactly the three unresolvable `feature.yaml` anchors when run
  against `git show <base_sha>:.harness/harness/docs/DECISIONS.md`, exits 0 against the file at
  `review_sha`, and reddens when one fabricated anchor is planted. Three separate observations, because
  an exit-0 alone is what an empty or errored search also produces.
  verify: automated        evidence: integration
- SC-09: **RETIRED 2026-08-29 — the id is kept, not renumbered and not reused.** It graded the claim
  checker's run and its 80→81 mutation. The mechanism it graded is deleted, so the criterion is now
  unmeetable by construction rather than unmet; SC-14 through SC-17 grade the removal in its place.
  The tombstone stands because `notes/review-harness-qa-c0.md`,
  `notes/review-harness-code-reviewer-c0.md` and both ship reviews cite SC-09, and those records are
  frozen and correct for the day they were written. **Not graded, by anybody.**
- SC-10: `run-unit-tests.sh` exits 0 and prints zero lines beginning `FAIL`, with the output captured
  and searched rather than piped to `tail`. Both are asserted: the runner has a path where a detail
  string is empty, and a truncating pipe reports the pipe's status.
  verify: automated        evidence: integration
- SC-11: For each of the 15 rewritten entries — the 14 amendment-owning decisions DEC-11, 138, 142,
  145, 149, 152, 157, 158, 171, 174, 183, 189, 193, 194, plus DEC-181 — a reviewer cites the pre-fold
  text from `git show <base_sha>:` beside its folded form at `review_sha` and confirms two things
  survive: what was believed before, and what falsified it. Per entry, with a file pointer each. An
  entry whose falsified claim was deleted rather than restated fails this and leaves every automated
  assertion green.
  verify: inspection
- SC-12: The front-matter APPEND-ONLY mandate and the documentor's repository-tier expertise entry
  P-01 no longer instruct a reader or an agent to add an amendment, and the new decision entry states
  where the convention now lives. Cited by `file:line` at `review_sha`.
  verify: inspection
- SC-13: Reading the folded DEC-138, DEC-174 and DEC-181 entries, the operator judges that each reads
  as a decision stating current truth rather than as merged history — and that no claim they now
  consider settled has silently disappeared.
  verify: uat
- SC-14: At `review_sha`, `.claude/skills/harness/bin/check-decision-claims.py` and
  `.claude/skills/harness/bin/test-check-decision-claims.py` are absent from `git ls-tree -r`,
  `DECISIONS.md` matches zero lines containing `<!-- claim:`, and no tracked file outside
  `.harness/harness/features/`, `.harness/notes/` and `.harness/logs/` matches
  `check-decision-claims`. Three separate assertions, each by the search's exit status rather than by
  a count compared to zero. It rejects the tree at `99bb52c`, where the marker search matches 11 lines
  across 6 entries and the reference search matches 5 tracked files.
  verify: automated        evidence: integration
- SC-15: At `review_sha`, neither `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` nor
  `.harness/harness.json`'s `integration` detect names the removed checker or its test, and
  `run-unit-tests.sh` at `review_sha` exits 0 while printing zero lines beginning `FAIL`, with its
  output captured and searched rather than piped. Both halves are asserted: the runner exits 2 when
  the two registration sides disagree, so a one-sided deregistration is invisible to an absence
  search that only looks at one file.
  verify: automated        evidence: integration
- SC-16: At `review_sha`, **each of the three sentences in DEC-205 that counts the mechanical checks
  positively states the number that actually exists** — its heading, the sentence introducing its
  enumeration, and the closing sentence of the considered-and-refused paragraph (*"...that openness
  is exactly why the two that are in are the mechanical ones"*) — no numbered item in that entry
  describes a claim that is re-run or a command grammar, and rule 1 (anchor rot) reads unchanged.
  **`DECISIONS-INDEX.md`'s DEC-205 row states the same corrected count**: its ruling — the
  hand-written half, right of ` :: `, which regeneration preserves verbatim — names one check and no
  marker mechanism. Graded by citing each of the four by `file:line` from
  `git show <review_sha>:` of each path beside its pre-change form from `git show 99bb52c:` of the
  same path. Two specific failures this catches, both of which leave every automated criterion above
  green: removing the item while a sentence still says *"two mechanical checks guard it"*, and
  **DELETING a count sentence instead of restating it** — a negative-only check is satisfied by
  deletion, and the count is content.
  verify: inspection
- SC-17: A note under this feature's `notes/` records the sweep of `.claude/skills/harness/bin/` for
  any script that builds a command line from an input it does not control — a document, a
  configuration file, or stdin: the command used, the set of files it returned, and a per-file
  verdict of `FIXED-LITERAL-ARGV`, `TEXT-DERIVED-ARGV` or `NO-EXECUTION`, each with a non-empty
  rationale citing the call site, and the text-derived set either stated empty or listed as
  remaining work with a recommendation. **The three verdicts are deliberate**: the enumeration
  pattern matches `literal_eval(` and matches `subprocess` in a docstring, so a candidate file that
  executes nothing must have a verdict that is true of it. The note must also show the sweep reached
  the case most likely to produce a text-derived site — a whole command string stored in
  configuration, `.harness/harness.json`'s `test_kinds.<kind>.cmd`. A bare "swept, found nothing"
  does not meet this — the filter is a judgement over 72 candidate files, and a later reader must be
  able to re-run the command and land on the same set.
  verify: inspection
- SC-18: `.claude/skills/harness/bin/check-decision-anchors.py` and its test
  `test-check-decision-anchors.py` at `review_sha` are byte-identical to `git show 99bb52c:` of the
  same paths, and the test is still named by both `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` and
  `.harness/harness.json`'s `integration` detect. The retained check sits beside everything being
  removed and shares a filename prefix with it, so over-deletion is the likely error and must be
  visible rather than inferred from a green suite.
  verify: automated        evidence: integration

## Verification gaps

Read from `test_kinds` in `.harness/harness.json` at `7ebfc9e`. `unit` and `integration` both have
runners and both match `.claude/skills/harness/bin/test-*.py`, which is where every automated
criterion above is evidenced. No criterion rests on a null-runner kind.

- **`functional`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null`.** None of their
  detect globs matches a file this feature touches, so nothing here is routed around a dead runner.
- **The real gap is not a missing runner — it is that no runner can exist.** A green suite proves the
  index regenerated and the patterns are absent. It proves nothing about whether a fold preserved
  meaning. Deleting a struck census sentence instead of restating it, folding a reversal to state only
  its final ruling and dropping the intermediate state, or missing one citation site — every one of
  these leaves all assertions green. There is no propagation checker; DEC-188 deleted it and states
  that the enforcement is a human reading a diff. **SC-11 (inspection, per entry) and SC-13 (uat)
  carry that weight, and they are the criteria most likely to be skipped under time pressure.** If
  they are not executed, the meaning half of this feature is unverified regardless of the suite.
- **Amendment dates are not recoverable from the tree after this lands**, only from
  `git log --follow`. One block, `DEC-145 am.3`, has reasoning that exists nowhere but the file — its
  authoring commit message is an unrelated write-up. The operator was shown this on 2026-08-20 and
  accepted it as a fair price for one block in thirty; it is restated here because the block count
  has since grown to 38.
- **Semantic citation rot has no detector at all after this lands, by decision.** A cited line that
  still exists and no longer says what the entry claims about it passes the anchor check, passes the
  suite, and passes review unless a human happens to open it. The mechanism that could have caught it
  is deleted; the operator accepted that cost with the alternative on the table, and the trade is
  stated under *What removal costs* above. **What therefore is NOT proven by any gate here: that the
  claims `DECISIONS.md` makes about the code are still true on any day after `review_sha`.** What
  carries it instead is SC-11 and SC-13, both human, and neither is a standing check — they cover this
  change only.
- **The `bin/` class audit (SC-17) rests on inspection because no runner can decide it.** Whether a
  given `subprocess` call site builds its argv from document text is a reading of the code, over 72
  candidate files. A grep for `subprocess` proves presence, never class membership, so a green suite
  says nothing about REQ-10.

## Approval

status: approved
approved-by: operator
date: 2026-08-29
