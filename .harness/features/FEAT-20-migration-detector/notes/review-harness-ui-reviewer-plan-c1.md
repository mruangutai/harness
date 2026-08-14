# Mode A review — FEAT-20-migration-detector — plan.yaml as the contract

**Verdict: PASS, advisory only.** No `DESIGN.md` is the right call for this feature — I agree with
visual-designer's scope-out reasoning: the OUTPUT CONTRACT lives in T-01's `intent:`, only the CI step
(T-03) parses it as text via `grep`, and T-02's INV-27 wording is composed independently from the
*structured result* the module returns, not by re-parsing CLI stdout. That keeps this at two
grep-coupled places (CLI text ↔ CI greps), not three — a third, text-coupled copy is exactly what a
`DESIGN.md` would have been for a contract whose stated failure mode is grep-drift. Firing the gate
anyway was correct: it surfaced four findings below, none of which existed before this reading.

## On visual-designer's F-1 and F-2 — agree with both, and F-1 is worse than raised

**F-1 — agree, and raise severity.** Confirmed by direct read: the CANNOT_VERIFY definition
(`plan.yaml:288-289`) has three causes — reader unreadable, reader matches neither form, surface has
*no disk evidence of either shape at all*. The third cause has no reader file to name, yet:

- T-01's OUTPUT CONTRACT (`plan.yaml:304-305`) says the per-surface line names "the reader files
  responsible" for a CANNOT_VERIFY verdict — no file exists for the no-evidence cause.
- T-02's INV-27 wording (`plan.yaml:396-397`) independently repeats the same gap: "one entry per
  CANNOT_VERIFY surface, worded as a CANNOT VERIFY finding naming the file that could not be judged."

**This is the same defect specified twice, not once.** A fix that lands only in T-01's CLI format
fixes what CI greps and leaves the session-entry operator — the higher-value call site per D-02 —
reading the identical ambiguity. Any fold-in must touch both task intents.

The other half of F-1 (a reader carrying both forms vs. a reader whose single form disagrees with
evidence render identically) is the strongest single finding here: it meets the dispatch's own bar —
an implementer can satisfy the letter of "name the reader file" while leaving the operator unable to
act, because "finish migrating this reader" and "revert this reader" are opposite remedies behind one
line of text.

**F-2 — agree.** Checked against the live house style rather than assuming it: every existing
`bad.append` in `check-state.sh` ends with an action clause — `check-state.sh:1071-1073` ("start the
session from the main checkout..."), `:1077-1078` ("clear it with `git worktree prune`"),
`:1083` ("Remove it with..."), `:1199-1202` ("run `gh-sync.py open` for it"). T-02's INV-27 spec
(`plan.yaml:392-397`) has no remedy clause for either the MIXED or CANNOT_VERIFY entries. Confirmed
gap, not a style guess.

## My own findings

**F-4 — the CLEAN definition is vacuously satisfiable if a reader set is empty, and the CI hedge
that would catch it is asymmetric.** `plan.yaml:293`: CLEAN is "exactly one evidence shape, and every
reader carrying exactly that form." Over an empty reader set, "every reader carries X" is vacuously
true. If an implementation bug drops a surface's reader list to zero entries while evidence still
shows exactly one shape, the surface computes CLEAN — the exact silent-pass class this feature exists
to prevent (issue #148), reintroduced one layer down inside its own verdict logic.

T-03's CI step is the intended defence-in-depth against a broken *checker* self-reporting healthy
(the check-plan-routes.py precedent, `tests.yml:156-171`, built for exactly this reason after
FEAT-18). T-03's intent (`plan.yaml:468`) zero-checks the feature-dir count (N) and the reader-file
count (R), but not the doc-root count (M) — "if the examined feature-dir count or the reader-file
count is 0" only. N, M and R are all wiring-distrust redundancy against the same class of bug (a
count that *should* map to CANNOT_VERIFY doing so through code the hedge does not trust); nothing in
the plan gives a principled reason DOCS gets less defence than FEATURES, and D-01 gives the two
surfaces coequal status. T-03's own `verify:` (`plan.yaml:449`) only asserts `::error::` count ≥ 3
generically — it cannot see this omission, so nothing downstream catches it either.

Recommend: (a) state a nonempty-reader-set precondition for CLEAN explicitly in T-01's PER-SURFACE
VERDICT text, not left implicit; (b) make T-03's zero-check symmetric across N, M and R, or state in
the plan why M is exempt.

**F-3 — the NOT_APPLICABLE branch's exact output text is the one under-specified string in a plan
that otherwise pins wording to the letter.** T-01's APPLICABILITY section (`plan.yaml:157-165`) says
"report NOT APPLICABLE, print zero for all three examined counts, and exit 0 without judging a
surface" but doesn't say whether the "layout: X clean, Y mixed, Z cannot-verify" summary line
(`plan.yaml:308-309`) still prints under this branch, or what X/Y/Z read when no surface was judged.
"NOT APPLICABLE" itself is not pinned as an exact string the way every other format string in this
plan is (the OUTPUT CONTRACT block, the three `::error::` messages, T-04's five verbatim phrases).
Ranked last because the blast radius is small: CI can never reach this branch (the harness's own tree
always carries the marker file), and INV-27 consumes the structured result, not this text — only
case 14's own assertion and a future manual CLI run depend on it.

## Accessibility and theme parity

Not applicable, and I'm stating that rather than manufacturing a finding: this is batch CLI output
and CI log text. Verdicts are carried by words (surface name, verdict word, exit code) and structured
data, never by colour alone. No contrast or dark/light dimension exists for this surface.

## Ranking

F-1 > F-4 > F-2 > F-3. F-1 is the one that lets an implementer satisfy the letter of the contract
while leaving the operator (and now CI) unable to distinguish opposite remedies. F-4 is a latent gap
in the verdict logic itself, not just the message text, and its hedge is asymmetric. F-2 and F-3 are
wording completeness, lower cost either way.

## Recommendation on folding in before signature

Agree with folding all four in before approval, for the reason already in the brief: T-01's cases pin
literal assertions ("that reader file named") and T-04's verify greps for verbatim phrases, so a
post-build reword is exactly the multi-place change this feature exists to avoid. This is the
operator's approval-gated call, not mine to make — recorded as an open question, non-blocking.
